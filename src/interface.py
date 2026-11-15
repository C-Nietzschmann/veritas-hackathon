"""The interface (card #35): what a user sees for one company.

- draw_graph (#98): a picture that shows on GitHub. Register facts are solid lines,
  our guesses dashed, and a guess says how sure we are in words (likely, possible,
  unlikely), because a decimal like 0.73 looks more exact than the model is.
- evidence_table (#100): every line of the picture as a table row, with its source.
- show (#99): a company number in; the decision, the reason, the picture and the table out.

Labels come only from the masked display columns. Like every box, it imports nothing
from src/ but the shared schema (ADR-005), so show() takes the decisions the decision
layer already made instead of running it.
"""

import io

import pandas as pd
from matplotlib.figure import Figure
from sklearn.metrics import precision_recall_curve

from src import evidence as ev

# How sure we are, in words. A guess at or above a line gets that word.
WORDS = [(0.8, "likely"), (0.4, "possible"), (0.0, "unlikely")]

# Left to right: the query company, its directors, the matched earlier people, their companies.
COLUMN_X = {"query": 0.0, "director": 1.0, "other": 2.2, "earlier": 3.2}


def in_words(p):
    """0.9 -> "likely", 0.5 -> "possible", 0.1 -> "unlikely"."""
    for line, word in WORDS:
        if p >= line:
            return word
    return "unlikely"


def label(mentions, mention_id):
    """A mention's name for the picture, from the display column only.

    An empty display name never falls back to the real name: a company shows its number,
    a person "director (name hidden)".
    """
    row = mentions.set_index("mention_id").loc[mention_id]
    shown = row["display_name"]
    if isinstance(shown, str) and shown.strip():
        return shown
    if row["kind"] == "company":
        return str(row["company_number"])
    return "director (name hidden)"


def spread(n):
    """n heights evenly spaced around 0, top to bottom: spread(3) -> [1.0, 0.0, -1.0]."""
    return [(n - 1) / 2 - i for i in range(n)]


def evidence(query, mentions, claims, links):
    """What the picture and the table show for one query company.

    Returns (query_id, facts, guesses):
    - facts: the register's director_of edges behind the picture, as rows of the observed graph
    - guesses: one dict per link, with director, other, earlier (mention ids), p and depends_on
    links: what decide.candidate_matches gave for this query (None or empty: no matches).
    """
    companies = mentions[mentions["kind"] == "company"].set_index("company_number")
    query_id = companies.loc[query, "mention_id"]

    # The register's facts as they stood when the company was formed (the as-of rule, ADR-001).
    edges = ev.observed_graph(claims, as_of=companies.loc[query, "incorporated_on"])
    facts = [edges[edges["object"] == query_id]]
    directors = set(facts[0]["subject"])

    # Each link rests on a pair (a, b): one is the query's director, the other ran the earlier company.
    guesses = []
    if links is not None:
        for _, link in links.iterrows():
            a, b = link["via"]
            director, other = (a, b) if a in directors else (b, a)
            earlier = companies.loc[link["predecessor"], "mention_id"]
            guesses.append(dict(director=director, other=other, earlier=earlier,
                                p=link["p"], depends_on=link["depends_on"],
                                via=tuple(sorted(link["via"]))))
            # the earlier company's fact: the claim this link depends on, other -> earlier
            facts.append(edges[edges["claim_id"].isin(link["depends_on"]) & (edges["object"] == earlier)])

    facts = pd.concat(facts).drop_duplicates(["subject", "object"]).reset_index(drop=True)
    return query_id, facts, guesses


def is_flip(guess, flip):
    """Is this guess the match the decision layer says to check first (decide.flip, #102)?"""
    return flip is not None and guess["via"] == tuple(sorted(flip["via"]))


def draw_graph(query, mentions, claims, links, decision, flip=None):
    """Draw one query company's evidence: its directors, our guessed matches and the
    earlier insolvent companies behind them. Returns a matplotlib Figure.

    decision: the decision word, for example "FLAG". flip: the decision's flip (or None);
    that match is drawn red and thicker, labelled "check this first" (#102).
    """
    query_id, facts, guesses = evidence(query, mentions, claims, links)
    directors = list(dict.fromkeys(facts.loc[facts["object"] == query_id, "subject"]))
    others = list(dict.fromkeys(g["other"] for g in guesses))
    earlier = list(dict.fromkeys(g["earlier"] for g in guesses))

    # Where each box goes.
    place = {query_id: (COLUMN_X["query"], 0.0)}
    for column, ids in (("director", directors), ("other", others), ("earlier", earlier)):
        for mention_id, y in zip(ids, spread(len(ids))):
            place[mention_id] = (COLUMN_X[column], y)

    # A Figure made directly, not through pyplot: it needs no window, and it leaves the
    # notebook's own plotting alone.
    fig = Figure(figsize=(10, 2 + 1.2 * max(len(directors), len(others), 1)))
    ax = fig.subplots()

    def line(a, b, style, text=None, color="black", width=1.5):
        (x1, y1), (x2, y2) = place[a], place[b]
        ax.plot([x1, x2], [y1, y2], linestyle=style, color=color, linewidth=width, zorder=1)
        if text:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.12, text, ha="center", fontsize=9, style="italic",
                    zorder=3, bbox=dict(facecolor="white", edgecolor="none", pad=1))

    for _, fact in facts.iterrows():                                   # facts: solid
        line(fact["subject"], fact["object"], "-")
    for g in guesses:                                                  # guesses: dashed
        if is_flip(g, flip):
            line(g["director"], g["other"], "--", in_words(g["p"]) + " same person: check this first",
                 color="red", width=2.5)
        else:
            line(g["director"], g["other"], "--", in_words(g["p"]) + " same person")

    for mention_id, (x, y) in place.items():
        is_company = mention_id == query_id or mention_id in earlier
        ax.text(x, y, label(mentions, mention_id), ha="center", va="center", fontsize=9, zorder=2,
                bbox=dict(boxstyle="square" if is_company else "round", facecolor="white",
                          edgecolor="black"))

    ax.set_title(f"{query}: {decision}", fontsize=13, fontweight="bold")
    fig.text(0.5, 0.02, "solid line: on the register    dashed line: our guess that two records are one person",
             ha="center", fontsize=9)
    ax.set_xlim(-0.6, 3.8)
    ax.set_ylim(min(y for _, y in place.values()) - 0.8, max(y for _, y in place.values()) + 0.8)
    ax.axis("off")
    return fig


def evidence_table(query, mentions, claims, links, flip=None):
    """Every line of the picture as one row (#100): masked labels only.

    A fact row names its source and record_ref (the raw file, row and hash it came from).
    A guess row gives how sure we are, in words and as p, and the claims it depends on,
    so no guess appears without its uncertainty. "check first" marks the decision's flip (#102).
    """
    query_id, facts, guesses = evidence(query, mentions, claims, links)
    rows = []
    for _, fact in facts.iterrows():
        rows.append({"line": "solid (fact)", "from": label(mentions, fact["subject"]),
                     "to": label(mentions, fact["object"]), "says": "director of",
                     "how sure": "on the register", "p": None,
                     "source": fact["source"], "record or depends on": fact["record_ref"],
                     "check first": ""})
    for g in guesses:
        rows.append({"line": "dashed (guess)", "from": label(mentions, g["director"]),
                     "to": label(mentions, g["other"]), "says": "same person?",
                     "how sure": in_words(g["p"]), "p": round(float(g["p"]), 2),
                     "source": "our matcher", "record or depends on": ", ".join(g["depends_on"]),
                     "check first": "yes" if is_flip(g, flip) else ""})
    return pd.DataFrame(rows, columns=["line", "from", "to", "says", "how sure", "p",
                                       "source", "record or depends on", "check first"])


def flip_sentence(links, flip):
    """One sentence on what to check first, with the match number what_if takes (#102), or None.

    Masked: it names the earlier company by number and the match by its number, never a person.
    """
    if flip is None or links is None:
        return None
    vias = [tuple(sorted(via)) for via in links["via"]]
    number = vias.index(tuple(sorted(flip["via"])))
    turns_out = "is" if flip["if_same_person"] else "is not"
    action = "confirm" if flip["if_same_person"] else "reject"
    return (f"Check first: match {number} (with {flip['predecessor']}). The decision becomes "
            f"{flip['becomes']} if it {turns_out} the same person: try what_if(..., {action}=[{number}]).")


def what_if(links, confirm=(), reject=()):
    """The company's matches after a person checked some of them by hand (#103).

    confirm and reject hold match numbers: the row numbers of `links`, in the order the
    evidence table lists the guesses. A confirmed match gets p = 1, a rejected one p = 0.
    Every other match keeps its p exactly (R7), so only the links that rest on a checked
    match change. Returns a copy; `links` itself is left alone.
    Run the decision layer again on the result to see the new decision.
    """
    confirm, reject = set(confirm), set(reject)
    if confirm & reject:
        raise ValueError(f"Match {sorted(confirm & reject)} can't be both confirmed and rejected.")
    for number in confirm | reject:
        if number not in range(len(links)):
            raise ValueError(f"There is no match {number}: this company has {len(links)} (0 to {len(links) - 1}).")
    checked = links.copy().reset_index(drop=True)
    checked.loc[sorted(confirm), "p"] = 1.0
    checked.loc[sorted(reject), "p"] = 0.0
    return checked


def cost_summary(query, links, line, costs, decide, thresholds):
    """One line of text: the costs, the thresholds they give and the decision they lead to (#104).

    decide and thresholds are the decision layer's own functions, passed in by the notebook,
    because the interface imports nothing but the schema (ADR-005).
    """
    clear_below, flag_above = thresholds(*costs)
    decision = decide(query, links, line, costs)["decision"]
    miss, wrong_flag, ask = costs
    return (f"Costs: missed case {miss:g}, wrong flag {wrong_flag:g}, asking {ask:g}. "
            f"Clear at or below {clear_below:.0%}, flag at or above {flag_above:.0%}. "
            f"{query}: {decision}")


def cost_sliders(query, links, line, agreed_costs, decide, thresholds):
    """Three sliders for the costs, the thresholds and decision next to them, and a Reset
    button that returns to the agreed costs (#104). Returns the widget box to display.

    The saved notebook on GitHub can't show sliders, so it also prints the line for the
    agreed costs once.
    """
    import ipywidgets as widgets   # here, so the rest of the interface works without it

    miss, wrong_flag, ask = agreed_costs
    sliders = [
        widgets.FloatSlider(value=miss, min=1, max=50, step=1, description="Missed case"),
        widgets.FloatSlider(value=wrong_flag, min=0.5, max=20, step=0.5, description="Wrong flag"),
        widgets.FloatSlider(value=ask, min=0.5, max=10, step=0.5, description="Asking"),
    ]
    summary = widgets.Label()
    reset = widgets.Button(description="Reset to agreed costs")

    def update(_change=None):
        costs = tuple(slider.value for slider in sliders)
        summary.value = cost_summary(query, links, line, costs, decide, thresholds)

    def back_to_agreed(_button):
        for slider, value in zip(sliders, agreed_costs):
            slider.value = value      # each change runs update() again

    for slider in sliders:
        slider.observe(update, names="value")
    reset.on_click(back_to_agreed)
    update()
    print(summary.value)
    return widgets.VBox(sliders + [summary, reset])


def show(query, mentions, claims, matches, decisions):
    """A company number in; the decision, the reason, the picture and the evidence table out (#99).

    matches: {company number: what decide.candidate_matches gave}; decisions: the decisions
    table. Both come from the decision layer, which the notebook runs first.
    Returns (decision row, figure, table), or None for a company we have no decision for.
    """
    query = str(query).strip().upper()
    decided = decisions[decisions["query"] == query]
    if decided.empty:
        print(f"Sorry, {query} isn't one of the companies we have data for, so we can't judge it. "
              "Check the number: we cover construction companies (SIC 41-43) formed in 2021 and 2022.")
        return None

    row = decided.iloc[0]
    print(f"{query}: {row['decision']}")
    print(row["reason"])
    links = matches.get(query)
    if links is None:   # nothing to draw: no director records on file (R8)
        return row, None, None
    flip = row.get("flip")
    sentence = flip_sentence(links, flip)
    if sentence:
        print(sentence)
    fig = draw_graph(query, mentions, claims, links, row["decision"], flip)
    table = evidence_table(query, mentions, claims, links, flip)
    display_png(fig)
    try:                # in a notebook, show the table too; elsewhere just return it
        from IPython.display import display
        display(table)
    except ImportError:
        pass
    return row, fig, table


def display_png(fig):
    """Show a figure in the notebook as a PNG, so it is saved as a picture GitHub can show.
    Outside a notebook it does nothing."""
    try:
        from IPython.display import Image, display
    except ImportError:
        return
    png = io.BytesIO()
    fig.savefig(png, format="png", dpi=100, bbox_inches="tight")
    display(Image(png.getvalue()))


# --- 42 The static figures for the notebook (cards #107, #108) -------------------------

# One colour per method, the same in every figure.
METHOD_COLORS = {"formula": "#2a78d6", "same_name": "#d6542a", "officer_links": "#52514e", "flag_nothing": "#a8a7a2"}
GRID = "#e5e4e0"


def tidy(ax):
    """The same light look for every figure: a faint grid, no box on top and right."""
    ax.grid(color=GRID, linewidth=0.5)
    ax.set_axisbelow(True)
    ax.spines[["top", "right"]].set_visible(False)


def pr_figure(decisions, labels, scores):
    """#107: precision against recall, ours against the baselines.

    A method that gives p_fail (ours) gets a curve: precision and recall at every threshold.
    Every method's actual decisions are one point, from scores = evaluate.score_methods(...).
    A method that flags nothing has no precision, so it has no point: the caption names it.
    The dashed line is the share of companies that failed: what flagging at random gives.
    """
    fig = Figure(figsize=(6, 4.5))
    ax = fig.subplots()
    both = decisions.merge(labels[["company_id", "failed"]], left_on="query", right_on="company_id")
    for method, part in both.groupby("method", sort=False):
        part = part[part["p_fail"].notna()]
        failed = part["failed"].astype(bool)
        if failed.nunique() < 2:   # a curve needs failed and not failed companies with a p_fail
            continue
        precision, recall, _ = precision_recall_curve(failed, part["p_fail"].astype(float))
        ax.plot(recall, precision, color=METHOD_COLORS.get(method, "#000000"), linewidth=1.5,
                label=f"{method}: every threshold")
    no_point = []
    for _, row in scores.iterrows():
        if pd.isna(row["precision"]):
            no_point.append(row["method"])
            continue
        ax.scatter(row["recall"], row["precision"], s=60, zorder=3, color=METHOD_COLORS.get(row["method"], "#000000"),
                   label=f"{row['method']}: its decisions ({row['flags']} flags)")
    share = labels.loc[labels["company_id"].isin(both["query"]), "failed"].astype(bool).mean()
    ax.axhline(share, linestyle="--", linewidth=1, color=METHOD_COLORS["flag_nothing"])
    ax.text(1.0, share, f"random: {share:.0%}", ha="right", va="bottom", fontsize=9, color="#52514e")
    ax.set(xlim=(-0.02, 1.02), ylim=(-0.02, 1.05), xlabel="recall: share of failed companies flagged",
           ylabel="precision: share of flags that failed", title="Who gets flagged, and how often rightly")
    ax.legend(fontsize=8, loc="upper right", frameon=False)
    tidy(ax)
    if no_point:
        fig.text(0.01, -0.02, "No point (flags nothing, so no precision): " + ", ".join(no_point),
                 fontsize=8, color="#52514e")
    return fig


def false_flag_figure(table):
    """#108: the false-flag rate per name-commonness band, one bar per method.

    table = evaluate.false_flags_by_band(...). Each bar carries its count, false flags out of
    companies that didn't fail, so a rate built on a few companies shows as such. A band with
    no honest company has no rate: its bar is left out and marked "no companies".
    """
    fig = Figure(figsize=(7, 4))
    ax = fig.subplots()
    bands = list(dict.fromkeys(table["band"]))
    methods = list(dict.fromkeys(table["method"]))
    width = 0.8 / len(methods)
    labelled = set()   # each method in the legend once, at its first bar
    empty = set()      # bands already marked as having no rate
    for i, method in enumerate(methods):
        part = table[table["method"] == method].set_index("band").reindex(bands)
        for j, band in enumerate(bands):
            x = j - 0.4 + width * (i + 0.5)
            rate, n = part.loc[band, "false_flag_rate"], part.loc[band, "not_failed"]
            if pd.isna(rate):
                if band not in empty:   # one note per band, in its middle
                    ax.text(j, 2, "no companies that didn't fail", ha="center", va="bottom", fontsize=8, color="#52514e")
                    empty.add(band)
                continue
            ax.bar(x, rate * 100, width, color=METHOD_COLORS.get(method, "#000000"),
                   label=None if method in labelled else method)
            labelled.add(method)
            ax.text(x, rate * 100, f"{int(part.loc[band, 'false_flags'])}/{int(n)}", ha="center", va="bottom", fontsize=7)
    ax.set_xticks(range(len(bands)), [f"{band} surname" for band in bands])
    ax.set_xlim(-0.5, len(bands) - 0.5)   # room for every band, even one with no bars
    ax.set(ylabel="false flags, % of companies that didn't fail", title="False flags by how common the surname is")
    ax.legend(fontsize=8, frameon=False)
    tidy(ax)
    return fig


def reliability_figure(p, same, bins=(0, 0.2, 0.4, 0.6, 0.8, 1.0)):
    """#108: is the matcher's p a probability? One dot per bin of p: its mean p against the share of
    pairs that really are the same person (same officer id). On the dashed line, p means what it says.

    p: the matcher's p for held-out pairs; same: 1 or 0 for the same pairs, in the same order.
    Each dot is labelled with its number of pairs. Empty bins have no dot.
    """
    points = pd.DataFrame({"p": list(p), "same": list(same)})
    points["bin"] = pd.cut(points["p"], list(bins), include_lowest=True)
    table = points.groupby("bin", observed=True).agg(pairs=("p", "size"), mean_p=("p", "mean"), share=("same", "mean"))
    fig = Figure(figsize=(5, 5))
    ax = fig.subplots()
    ax.plot([0, 1], [0, 1], linestyle="--", linewidth=1, color="#52514e")
    ax.scatter(table["mean_p"], table["share"], s=60, zorder=3, color=METHOD_COLORS["formula"])
    for x, y, n in zip(table["mean_p"], table["share"], table["pairs"]):
        ax.annotate(f"{n} pair" + ("s" if n != 1 else ""), (x, y), textcoords="offset points",
                    xytext=(8, 4), fontsize=9, color="#52514e")
    ax.set(xlim=(-0.02, 1.02), ylim=(-0.02, 1.05), xlabel="mean p in the bin",
           ylabel="share of pairs that are the same person", title="Matcher calibration")
    tidy(ax)
    return fig

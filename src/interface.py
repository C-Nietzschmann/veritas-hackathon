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
                                p=link["p"], depends_on=link["depends_on"]))
            # the earlier company's fact: the claim this link depends on, other -> earlier
            facts.append(edges[edges["claim_id"].isin(link["depends_on"]) & (edges["object"] == earlier)])

    facts = pd.concat(facts).drop_duplicates(["subject", "object"]).reset_index(drop=True)
    return query_id, facts, guesses


def draw_graph(query, mentions, claims, links, decision):
    """Draw one query company's evidence: its directors, our guessed matches and the
    earlier insolvent companies behind them. Returns a matplotlib Figure.

    decision: the decision word, for example "FLAG".
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

    def line(a, b, style, text=None):
        (x1, y1), (x2, y2) = place[a], place[b]
        ax.plot([x1, x2], [y1, y2], linestyle=style, color="black", linewidth=1.5, zorder=1)
        if text:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.12, text, ha="center", fontsize=9, style="italic",
                    zorder=3, bbox=dict(facecolor="white", edgecolor="none", pad=1))

    for _, fact in facts.iterrows():                                   # facts: solid
        line(fact["subject"], fact["object"], "-")
    for g in guesses:                                                  # guesses: dashed
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


def evidence_table(query, mentions, claims, links):
    """Every line of the picture as one row (#100): masked labels only.

    A fact row names its source and record_ref (the raw file, row and hash it came from).
    A guess row gives how sure we are, in words and as p, and the claims it depends on,
    so no guess appears without its uncertainty.
    """
    query_id, facts, guesses = evidence(query, mentions, claims, links)
    rows = []
    for _, fact in facts.iterrows():
        rows.append({"line": "solid (fact)", "from": label(mentions, fact["subject"]),
                     "to": label(mentions, fact["object"]), "says": "director of",
                     "how sure": "on the register", "p": None,
                     "source": fact["source"], "record or depends on": fact["record_ref"]})
    for g in guesses:
        rows.append({"line": "dashed (guess)", "from": label(mentions, g["director"]),
                     "to": label(mentions, g["other"]), "says": "same person?",
                     "how sure": in_words(g["p"]), "p": round(float(g["p"]), 2),
                     "source": "our matcher", "record or depends on": ", ".join(g["depends_on"])})
    return pd.DataFrame(rows, columns=["line", "from", "to", "says", "how sure", "p",
                                       "source", "record or depends on"])


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
    fig = draw_graph(query, mentions, claims, links, row["decision"])
    table = evidence_table(query, mentions, claims, links)
    try:                # in a notebook, show both; elsewhere just return them
        from IPython.display import Image, display
        png = io.BytesIO()
        fig.savefig(png, format="png", dpi=100, bbox_inches="tight")   # a picture GitHub can show
        display(Image(png.getvalue()))
        display(table)
    except ImportError:
        pass
    return row, fig, table

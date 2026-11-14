"""The interface (card #35). For now one picture, draw_graph (#98), that shows on GitHub.

Facts from the register are solid lines; our guesses are dashed. A guess says how sure
we are in words (likely, possible, unlikely), because a decimal like 0.73 looks more
exact than the model is. Labels come only from the masked display columns.

Like every box, it imports nothing from src/ but the shared schema (ADR-005).
"""

import matplotlib
import matplotlib.pyplot as plt

from src import evidence as ev

matplotlib.use("Agg")   # draw without a window, so it also runs in tests and on GitHub

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


def draw_graph(query, mentions, claims, links, decision):
    """Draw one query company's evidence: its directors, our guessed matches and the
    earlier insolvent companies behind them. Returns a matplotlib Figure.

    links: what decide.candidate_matches gave for this query (None or empty: no matches).
    decision: the decision word, for example "FLAG".
    """
    companies = mentions[mentions["kind"] == "company"].set_index("company_number")
    query_id = companies.loc[query, "mention_id"]

    # The register's facts as they stood when the company was formed (the as-of rule, ADR-001).
    formed = companies.loc[query, "incorporated_on"]
    edges = ev.observed_graph(claims, as_of=formed)
    directors = list(dict.fromkeys(edges.loc[edges["object"] == query_id, "subject"]))

    # Each link rests on a pair (a, b): one is the query's director, the other ran the earlier company.
    guesses = []   # (director, other, earlier company, p)
    if links is not None:
        for _, link in links.iterrows():
            a, b = link["via"]
            director, other = (a, b) if a in directors else (b, a)
            guesses.append((director, other, companies.loc[link["predecessor"], "mention_id"], link["p"]))
    others = list(dict.fromkeys(g[1] for g in guesses))
    earlier = list(dict.fromkeys(g[2] for g in guesses))

    # Where each box goes.
    place = {query_id: (COLUMN_X["query"], 0.0)}
    for column, ids in (("director", directors), ("other", others), ("earlier", earlier)):
        for mention_id, y in zip(ids, spread(len(ids))):
            place[mention_id] = (COLUMN_X[column], y)

    fig, ax = plt.subplots(figsize=(10, 2 + 1.2 * max(len(directors), len(others), 1)))

    def line(a, b, style, text=None):
        (x1, y1), (x2, y2) = place[a], place[b]
        ax.plot([x1, x2], [y1, y2], linestyle=style, color="black", linewidth=1.5, zorder=1)
        if text:
            ax.text((x1 + x2) / 2, (y1 + y2) / 2 + 0.12, text, ha="center", fontsize=9, style="italic",
                    zorder=3, bbox=dict(facecolor="white", edgecolor="none", pad=1))

    for director in directors:                                   # facts: solid
        line(director, query_id, "-")
    for director, other, company, p in guesses:
        line(other, company, "-")                                # fact: solid
        line(director, other, "--", in_words(p) + " same person")  # guess: dashed

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

"""Tests for draw_graph (card #98), on the tiny world."""
import pandas as pd

from src import decide, interface
from src import evidence as ev
from tests.tiny_world import tiny_world

mentions, claims, truth = tiny_world()

# The same stand-in pairs main.ipynb uses until the matcher runs on real data.
pairs = pd.DataFrame(
    [(a, b, 0.9, None, "stand-in", None) for a, b in truth["same_person"]]
    + [(a, b, 0.05, None, "stand-in", None) for a, b in truth["look_alikes"]],
    columns=ev.PAIR_COLS)


def texts(fig):
    """Every piece of text in the figure."""
    return [t.get_text() for t in fig.findobj(match=lambda o: hasattr(o, "get_text"))]


def test_draws_the_tiny_world_without_error():
    for query in truth["queries"]:
        links = decide.candidate_matches(query, mentions, claims, pairs)
        fig = interface.draw_graph(query, mentions, claims, links, truth["decision"][query])
        assert query in fig.axes[0].get_title()


def test_the_phoenix_shows_a_dashed_guess_in_words():
    links = decide.candidate_matches("TW000002", mentions, claims, pairs)
    fig = interface.draw_graph("TW000002", mentions, claims, links, "FLAG")
    assert "likely same person" in texts(fig)
    assert "--" in [l.get_linestyle() for l in fig.axes[0].get_lines()]


def test_no_decimals_in_the_picture():
    links = decide.candidate_matches("TW000002", mentions, claims, pairs)
    fig = interface.draw_graph("TW000002", mentions, claims, links, "FLAG")
    assert not any("0." in t for t in texts(fig))


def test_an_empty_display_name_never_shows_the_real_name():
    hidden = mentions.copy()
    hidden.loc[hidden["kind"] == "person", "display_name"] = ""
    links = decide.candidate_matches("TW000002", hidden, claims, pairs)
    fig = interface.draw_graph("TW000002", hidden, claims, links, "FLAG")
    shown = " ".join(texts(fig))
    assert "Daniel" not in shown   # "Harrow" itself is in the company names, which may be shown
    assert "director (name hidden)" in shown


def test_in_words():
    assert interface.in_words(0.9) == "likely"
    assert interface.in_words(0.5) == "possible"
    assert interface.in_words(0.05) == "unlikely"

"""Tests for draw_graph (card #98), on the tiny world."""
import pandas as pd
import pytest

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


# --- #100 evidence table and #99 show() ----------------------------------------------

LINE, COSTS = (0.05, 0.6), (10, 2, 1)   # a made-up failure line for the tests, and the team's costs
matches = {q: decide.candidate_matches(q, mentions, claims, pairs) for q in truth["queries"]}
decisions = pd.DataFrame([decide.decide(q, matches[q], LINE, COSTS) for q in truth["queries"]],
                         columns=ev.DECISION_COLS)


def test_the_table_has_one_row_per_line_and_every_guess_has_its_uncertainty():
    table = interface.evidence_table("TW000002", mentions, claims, matches["TW000002"])
    guesses = table[table["line"] == "dashed (guess)"]
    assert len(guesses) == 1
    assert guesses["p"].notna().all() and (guesses["how sure"] != "").all()
    assert guesses["record or depends on"].str.len().gt(0).all()
    facts = table[table["line"] == "solid (fact)"]
    assert facts["source"].notna().all() and facts["record or depends on"].notna().all()


def test_the_table_shows_masked_values_only():
    hidden = mentions.copy()
    hidden.loc[hidden["kind"] == "person", "display_name"] = ""
    links = decide.candidate_matches("TW000002", hidden, claims, pairs)
    table = interface.evidence_table("TW000002", hidden, claims, links)
    assert "Daniel" not in table.to_string()


def test_show_gives_the_decision_the_picture_and_the_table(capsys):
    row, fig, table = interface.show("tw000002", mentions, claims, matches, decisions)
    assert row["decision"] == decisions.set_index("query").loc["TW000002", "decision"]
    assert fig is not None and len(table) > 0
    assert "TW000002" in capsys.readouterr().out


def test_show_is_polite_about_a_company_outside_the_slice(capsys):
    assert interface.show("00000006", mentions, claims, matches, decisions) is None
    assert "Sorry, 00000006 isn't one of the companies" in capsys.readouterr().out


def test_show_without_director_records_gives_only_the_decision():
    quiet = [q for q in truth["queries"] if matches[q] is None][0]
    row, fig, table = interface.show(quiet, mentions, claims, matches, decisions)
    assert row["decision"] == "NOT ENOUGH EVIDENCE" and fig is None and table is None


# --- #103 confirm and reject a match --------------------------------------------------

def two_matches():
    """TW000002's match plus a made-up second one, to check the other match is left alone."""
    links = matches["TW000002"]
    second = links.iloc[[0]].assign(p=0.3, predecessor="TW999999")
    return pd.concat([links, second], ignore_index=True)


def test_reject_sets_p_to_0_and_leaves_the_other_match_alone():
    links = two_matches()
    checked = interface.what_if(links, reject=[0])
    assert checked.loc[0, "p"] == 0.0
    pd.testing.assert_series_equal(checked.loc[1], links.loc[1])   # R7: untouched
    assert links.loc[0, "p"] == 0.9                                # the original is left alone


def test_confirm_sets_p_to_1():
    assert interface.what_if(two_matches(), confirm=[1]).loc[1, "p"] == 1.0


def test_rejecting_the_phoenix_match_changes_the_decision():
    before = decide.decide("TW000002", matches["TW000002"], LINE, COSTS)["decision"]
    after = decide.decide("TW000002", interface.what_if(matches["TW000002"], reject=[0]), LINE, COSTS)["decision"]
    assert (before, after) == ("FLAG", "CLEAR")


def test_a_wrong_match_number_or_both_at_once_gives_a_readable_error():
    with pytest.raises(ValueError, match="There is no match 5"):
        interface.what_if(matches["TW000002"], reject=[5])
    with pytest.raises(ValueError, match="both confirmed and rejected"):
        interface.what_if(matches["TW000002"], confirm=[0], reject=[0])


# --- #104 cost sliders -------------------------------------------------------------

def test_cost_summary_names_the_thresholds_and_the_decision():
    text = interface.cost_summary("TW000002", matches["TW000002"], LINE, COSTS, decide.decide, decide.thresholds)
    assert "Clear at or below 10%, flag at or above 50%" in text and text.endswith("TW000002: FLAG")


def test_moving_a_slider_moves_the_decision_and_reset_brings_it_back():
    box = interface.cost_sliders("TW000002", matches["TW000002"], LINE, COSTS, decide.decide, decide.thresholds)
    miss, wrong_flag, ask = box.children[:3]
    summary, reset = box.children[3], box.children[4]
    assert summary.value.endswith("FLAG")
    wrong_flag.value = 20            # a wrong flag now costs a lot, so flagging needs much more certainty
    ask.value = 0.5
    assert "flag at or above 98%" in summary.value and not summary.value.endswith("FLAG")
    reset.click()
    assert summary.value == interface.cost_summary("TW000002", matches["TW000002"], LINE, COSTS,
                                                   decide.decide, decide.thresholds)

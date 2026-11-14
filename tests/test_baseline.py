"""Tests for src/baseline.py, the three baselines (card #27), on the tiny world.

What each baseline should get right and wrong is written into the tiny world (#21):
same name flags the phoenix but also both innocent look-alikes, and officer links miss
the phoenix, whose director came back under a new officer id.
"""

import pandas as pd

from src import baseline as bl
from src import evidence as ev
from tests.tiny_world import APPOINTMENTS, tiny_world


def verdicts(table):
    """{query company: decision} from a decisions table."""
    return dict(zip(table["query"], table["decision"]))


def flagged(table):
    return {query for query, verdict in verdicts(table).items() if verdict == "FLAG"}


# --- 27.1 Flag nothing ------------------------------------------------------------------

def test_flag_nothing_clears_every_company():
    _, _, truth = tiny_world()
    table = bl.flag_nothing(truth["queries"])
    assert list(table.columns) == ev.DECISION_COLS
    assert list(table["query"]) == list(truth["queries"])
    assert set(table["decision"]) == {"CLEAR"}


# --- 27.2 Same name means same person --------------------------------------------------

def test_normalise_name_handles_case_punctuation_titles_and_order():
    assert bl.normalise_name("HARROW, Daniel James") == "daniel harrow"
    assert bl.normalise_name("Mr Daniel Harrow") == "daniel harrow"
    assert bl.normalise_name("daniel   harrow.") == "daniel harrow"
    assert bl.normalise_name(None) == ""


def test_same_name_flags_the_phoenix_and_both_look_alikes():
    mentions, claims, truth = tiny_world()
    table = bl.same_name_flags(truth["queries"], mentions, claims)
    assert flagged(table) == {"TW000002", "TW000003", "TW000005"}   # 1 right, 2 innocent look-alikes
    assert verdicts(table)["TW000007"] == "CLEAR"   # Lambert Electrical was dissolved, not insolvent


def test_only_insolvencies_in_the_window_count():
    mentions, claims, truth = tiny_world()
    joinery = mentions["mention_id"] == truth["mention"]["TW000004"]
    mentions.loc[joinery, "insolvency_on"] = "2017-01-01"   # 4 years before Elm Street Plumbing formed
    assert verdicts(bl.same_name_flags(truth["queries"], mentions, claims))["TW000005"] == "CLEAR"
    assert verdicts(bl.same_name_flags(truth["queries"], mentions, claims, window_years=5))["TW000005"] == "FLAG"


def test_same_name_pairs_are_in_the_shared_format():
    mentions, _, truth = tiny_world()
    pairs = bl.same_name_pairs(mentions)
    ev.check_columns(pairs, "pairs")
    assert (pairs["p"] == 1.0).all()
    phoenix = tuple(sorted((truth["mention"]["p1"], truth["mention"]["p2"])))
    assert phoenix in set(zip(pairs["a"], pairs["b"]))


# --- 27.3 Companies House officer links only -------------------------------------------

def test_officer_links_miss_the_phoenix_with_a_new_officer_id():
    mentions, claims, truth = tiny_world()
    table = bl.officer_link_flags(truth["queries"], mentions, claims)
    # Nothing is flagged. James Smith's own officer id does lead to Smith Brothers Builders,
    # but that company is formed in 2023 and fails in 2024: the future, as seen from Elm Street
    # Plumbing's formation in 2021, so it can't count (as-of rule).
    assert flagged(table) == set()


def test_officer_links_flag_when_the_register_links_the_director():
    mentions, claims, truth = tiny_world()
    phoenix = mentions["mention_id"] == truth["mention"]["p2"]
    mentions.loc[phoenix, "officer_id"] = "tw-officer-01"   # as if he had kept his old officer id
    assert flagged(bl.officer_link_flags(truth["queries"], mentions, claims)) == {"TW000002"}


# --- All three ----------------------------------------------------------------------------

def test_run_all_gives_one_decision_per_company_and_baseline():
    mentions, claims, truth = tiny_world()
    table = bl.run_all(truth["queries"], mentions, claims)
    assert len(table) == 3 * len(truth["queries"])
    assert set(table["method"]) == {"flag_nothing", "same_name", "officer_links"}
    assert set(table["decision"]) <= {"FLAG", "CLEAR"}   # baselines never abstain


def test_reasons_name_no_person():
    mentions, claims, truth = tiny_world()
    names = {appointment[1] for appointment in APPOINTMENTS}
    for reason in bl.run_all(truth["queries"], mentions, claims)["reason"]:
        assert not any(name in reason for name in names)

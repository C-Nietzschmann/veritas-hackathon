"""Tests for src/decide.py, the decision layer (card #34, sub-tasks 34.1 to 34.3).

Entity resolution (#30, #31) isn't built yet, so the pairs are made by hand from the
tiny world's true answers: same-person pairs get p = 0.9, look-alikes p = 0.05.
"""

import pandas as pd
import pytest

from src import evidence as ev
from src.decide import candidate_matches, decide, p_predecessor, thresholds
from tests.tiny_world import tiny_world

LINE = (0.05, 0.6)    # hand-made: 5% fail without an insolvent predecessor, 60% with one
COSTS = (10, 2, 1)    # a missed case, a wrong flag, asking (Idea)


def hand_made_pairs(truth, same_person=0.9, look_alike=0.05):
    """A stand-in for entity resolution: the true answers, each with a probability."""
    rows = [(a, b, same_person, None, "hand_made", True) for a, b in truth["same_person"]]
    rows += [(a, b, look_alike, None, "hand_made", False) for a, b in truth["look_alikes"]]
    return pd.DataFrame(rows, columns=ev.PAIR_COLS)


def decide_all(mentions, claims, pairs):
    return {query: decide(query, candidate_matches(query, mentions, claims, pairs), LINE, COSTS)
            for query in ["TW000002", "TW000003", "TW000005", "TW000006", "TW000007"]}


# --- 34.1 P(predecessor) -------------------------------------------------------

def test_p_predecessor():
    assert p_predecessor([]) == 0
    assert p_predecessor([0.3]) == pytest.approx(0.3)
    assert p_predecessor([0.5, 0.5]) == pytest.approx(0.75)


def test_one_match_counts_once_even_when_it_leads_to_two_insolvent_companies():
    mentions, claims, truth = tiny_world()
    # Say the phoenix's earlier Daniel Harrow also ran Smith and Sons Joinery (insolvent 2020).
    extra = claims[claims["subject"] == truth["mention"]["p1"]].assign(
        claim_id="extra", object=truth["mention"]["TW000004"], valid_from="2016-01-01")
    claims = pd.concat([claims, extra], ignore_index=True)
    matches = candidate_matches("TW000002", mentions, claims, hand_made_pairs(truth))
    assert set(matches["predecessor"]) == {"TW000001", "TW000004"}
    assert decide("TW000002", matches, LINE, COSTS)["p_predecessor"] == pytest.approx(0.9)


def test_a_pair_listed_both_ways_round_counts_once():
    mentions, claims, truth = tiny_world()
    pairs = hand_made_pairs(truth)
    both = pd.concat([pairs, pairs.rename(columns={"a": "b", "b": "a"})], ignore_index=True)
    matches = candidate_matches("TW000002", mentions, claims, both)
    assert decide("TW000002", matches, LINE, COSTS)["p_predecessor"] == pytest.approx(0.9)


def test_a_copied_claim_is_still_one_link():
    mentions, claims, truth = tiny_world()
    # Brightwater's director is on record twice (the copied source, R5). Say her earlier company went insolvent.
    mentions.loc[mentions["company_number"] == "TW000008", "insolvency_on"] = "2020-12-01"
    matches = candidate_matches("TW000007", mentions, claims, hand_made_pairs(truth))
    assert len(matches) == 1


# --- 34.2 Thresholds -------------------------------------------------------------

def test_thresholds_from_the_proposed_costs():
    assert thresholds(*COSTS) == pytest.approx((0.1, 0.5))


def test_when_asking_never_pays_the_thresholds_meet():
    # Asking costs 5: clearing beats it below 0.5, flagging above -1.5, so the two overlap.
    clear_below, flag_above = thresholds(10, 2, 5)
    assert clear_below == flag_above == pytest.approx(2 / 12)


def test_exactly_on_a_threshold_acts():
    # ADR-004: clear if P(fail) ≤ 0.1, flag if P(fail) ≥ 0.5. This line starts and ends exactly there.
    line = (0.1, 0.5)
    no_match = ev.empty_table("links")
    sure_match = pd.DataFrame([["Q", "E", ("a", "b"), 1.0, "hand_made", []]], columns=ev.LINK_COLS)
    assert decide("Q", no_match, line, COSTS)["decision"] == "CLEAR"
    assert decide("Q", sure_match, line, COSTS)["decision"] == "FLAG"


# --- 34.3 decide() ---------------------------------------------------------------

def test_the_tiny_world_decisions_match():
    mentions, claims, truth = tiny_world()
    rows = decide_all(mentions, claims, hand_made_pairs(truth))
    assert {query: row["decision"] for query, row in rows.items()} == truth["decision"]
    for row in rows.values():
        assert list(row) == ev.DECISION_COLS


def test_r8_no_evidence_gives_not_enough_evidence():
    mentions, claims, truth = tiny_world()
    pairs = hand_made_pairs(truth)
    for query in ["TW000006", "TW999999"]:   # no director records; not in our data at all
        row = decide(query, candidate_matches(query, mentions, claims, pairs), LINE, COSTS)
        assert row["decision"] == "NOT ENOUGH EVIDENCE"
        assert row["p_fail"] is None


def test_no_predecessor_found_is_not_the_same_as_no_evidence():
    mentions, claims, truth = tiny_world()
    matches = candidate_matches("TW000007", mentions, claims, hand_made_pairs(truth))
    assert matches is not None and matches.empty   # it has a director, who matches nobody insolvent
    row = decide("TW000007", matches, LINE, COSTS)
    assert row["p_predecessor"] == 0
    assert row["decision"] == "CLEAR"


def test_the_future_does_not_count():
    mentions, claims, truth = tiny_world()
    # TW000005's director is truly (p = 0.9) the James Smith whose company fails in 2024.
    matches = candidate_matches("TW000005", mentions, claims, hand_made_pairs(truth))
    assert set(matches["predecessor"]) == {"TW000004"}   # only the 2020 look-alike, at 5%
    assert decide("TW000005", matches, LINE, COSTS)["decision"] == "CLEAR"


def test_insolvency_counts_up_to_the_formation_day():
    mentions, claims, truth = tiny_world()
    pairs = hand_made_pairs(truth)
    harrow_build = mentions["company_number"] == "TW000001"
    for insolvent_on, links in [("2021-04-20", 1), ("2021-04-21", 0)]:   # the day TW000002 was formed; the day after
        mentions.loc[harrow_build, "insolvency_on"] = insolvent_on
        assert len(candidate_matches("TW000002", mentions, claims, pairs)) == links


def test_a_company_with_no_formation_date_is_not_judged():
    mentions, claims, truth = tiny_world()
    mentions.loc[mentions["company_number"] == "TW000002", "incorporated_on"] = None
    assert candidate_matches("TW000002", mentions, claims, hand_made_pairs(truth)) is None


def test_a_director_who_joins_later_does_not_count():
    mentions, claims, truth = tiny_world()
    # The phoenix director also joins Brightwater (formed 2021-05-15), but only in 2023.
    later = claims[claims["subject"] == truth["mention"]["p2"]].assign(
        claim_id="later", object=truth["mention"]["TW000007"], valid_from="2023-01-01")
    claims = pd.concat([claims, later], ignore_index=True)
    matches = candidate_matches("TW000007", mentions, claims, hand_made_pairs(truth))
    assert matches.empty


def test_in_between_says_check_by_hand_not_no_records():
    mentions, claims, truth = tiny_world()
    rows = decide_all(mentions, claims, hand_made_pairs(truth, same_person=0.5))
    middle, no_records = rows["TW000002"], rows["TW000006"]
    assert middle["decision"] == no_records["decision"] == "NOT ENOUGH EVIDENCE"
    assert middle["p_fail"] == pytest.approx(0.05 + 0.5 * (0.6 - 0.05))
    assert middle["reason"] != no_records["reason"]


def test_reasons_never_show_a_person():
    mentions, claims, truth = tiny_world()
    people = mentions[mentions["kind"] == "person"]
    for row in decide_all(mentions, claims, hand_made_pairs(truth)).values():
        for private in list(people["name"]) + list(people["postcode"]):
            assert private not in row["reason"]


# --- 33.1 The failure line -------------------------------------------------------------

def test_the_line_recovers_the_two_failure_rates():
    from src.decide import fit_failure_line
    # 10 companies without a predecessor, 1 failed (10%); 10 with one, 6 failed (60%).
    p = [0.0] * 10 + [1.0] * 10
    failed = [True] + [False] * 9 + [True] * 6 + [False] * 4
    assert fit_failure_line(p, failed) == pytest.approx((0.1, 0.6))


def test_the_line_leaves_out_companies_with_no_p_predecessor():
    from src.decide import fit_failure_line
    p = [0.0] * 10 + [1.0] * 10 + [None, None]
    failed = [True] + [False] * 9 + [True] * 6 + [False] * 4 + [True, True]
    assert fit_failure_line(p, failed) == pytest.approx((0.1, 0.6))


def test_the_ends_of_the_line_stay_between_0_and_1():
    from src.decide import fit_failure_line
    # The closest straight line through these points ends below 0 and above 1.
    rate_without, rate_with = fit_failure_line([0.0, 0.05, 0.05, 0.9], [False, False, False, True])
    assert (rate_without, rate_with) == (0.0, 1.0)


def test_one_value_of_p_predecessor_is_no_line():
    from src.decide import fit_failure_line
    with pytest.raises(ValueError, match="two different values"):
        fit_failure_line([0.0, 0.0, 0.0], [True, False, False])


def test_company_p_predecessor_is_none_when_there_is_nothing_to_judge():
    from src.decide import company_p_predecessor
    assert company_p_predecessor(None) is None


def test_the_line_stops_when_the_two_lists_are_not_the_same_length():
    from src.decide import fit_failure_line
    with pytest.raises(ValueError, match="same companies"):
        fit_failure_line([0.0, 1.0, 1.0], [False, True])

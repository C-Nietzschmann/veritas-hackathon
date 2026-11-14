"""Tests for src/baseline.py, the three baselines (card #27), on the tiny world.

What each baseline should get right and wrong is written into the tiny world (#21):
same name flags the phoenix but also both innocent look-alikes, and officer links miss
the phoenix, whose director came back under a new officer id. The regression tests after
the review on #127 change the tiny world a little, each next to a control case, so a test
can't pass just because nothing ever gets flagged.
"""

import pandas as pd
import pytest

from src import baseline as bl
from src import evidence as ev
from tests.tiny_world import APPOINTMENTS, tiny_world


def verdicts(table):
    """{query company: decision} from a decisions table."""
    return dict(zip(table["query"], table["decision"]))


def flagged(table):
    return {query for query, verdict in verdicts(table).items() if verdict == "FLAG"}


def with_claim(claims, key, subject, relation, company, start):
    """The claims plus one more, stated by the same source as the first claim."""
    claim = claims.iloc[0].copy()
    claim[["claim_id", "subject", "relation", "object", "valid_from", "valid_to"]] = [
        f"test-claim-{key}", subject, relation, company, start, None]
    return pd.concat([claims, claim.to_frame().T], ignore_index=True)


def with_appointment(mentions, claims, key, copy_of, company, start):
    """The tiny world plus one new director record: a copy of person `copy_of` (same name,
    birth date and officer id) appointed to `company` from `start`."""
    person = mentions[mentions["mention_id"] == copy_of].iloc[0].copy()
    person["mention_id"] = f"test-person-{key}"
    mentions = pd.concat([mentions, person.to_frame().T], ignore_index=True)
    return mentions, with_claim(claims, key, person["mention_id"], "director_of", company, start)


def set_insolvency(mentions, truth, number, date):
    """Change one company's insolvency date (None: it never failed)."""
    mentions = mentions.copy()
    mentions.loc[mentions["mention_id"] == truth["mention"][number], "insolvency_on"] = date
    return mentions


# --- 27.1 Flag nothing ------------------------------------------------------------------

def test_flag_nothing_clears_every_company():
    _, _, truth = tiny_world()
    table = bl.flag_nothing(truth["queries"])
    assert list(table.columns) == ev.DECISION_COLS
    assert list(table["query"]) == list(truth["queries"])
    assert set(table["decision"]) == {"CLEAR"}


# --- 27.2 Same name means same person --------------------------------------------------

def test_normalise_name_ignores_case_punctuation_titles_and_order():
    expected = "daniel harrow"
    for written in ["HARROW, Daniel", "Daniel Harrow", "Mr Daniel Harrow", "harrow daniel."]:
        assert bl.normalise_name(written) == expected
    assert bl.normalise_name(None) == ""
    assert bl.normalise_name("") == ""


def test_normalise_name_keeps_every_name_word():
    # Regression: hyphens, apostrophes and middle names used to be cut away, which made
    # different names "the same" and gave this baseline false flags it shouldn't have.
    different = [
        ("SMITH-JONES, Anna", "JONES, Anna"),
        ("O'BRIEN, Sean", "BRIEN, Sean"),
        ("HARROW, Daniel James", "HARROW, Daniel"),
        ("José Pérez", "Jose Perez"),
    ]
    for one, other in different:
        assert bl.normalise_name(one) != bl.normalise_name(other)
    # The documented assumption: punctuation separates words.
    assert bl.normalise_name("SMITH-JONES, Anna") == bl.normalise_name("Anna Smith Jones")


def test_same_name_flags_the_phoenix_and_both_look_alikes():
    mentions, claims, truth = tiny_world()
    table = bl.same_name_flags(truth["queries"], mentions, claims)
    assert flagged(table) == {"TW000002", "TW000003", "TW000005"}   # 1 right, 2 innocent look-alikes
    assert verdicts(table)["TW000007"] == "CLEAR"   # Lambert Electrical was dissolved, not insolvent


def test_only_insolvencies_in_the_window_count():
    mentions, claims, truth = tiny_world()
    mentions = set_insolvency(mentions, truth, "TW000004", "2017-01-01")   # 4 years before Elm Street Plumbing
    assert verdicts(bl.same_name_flags(truth["queries"], mentions, claims))["TW000005"] == "CLEAR"
    assert verdicts(bl.same_name_flags(truth["queries"], mentions, claims, window_years=5))["TW000005"] == "FLAG"


def test_window_counts_whole_years_with_both_ends_included():
    mentions, claims, truth = tiny_world()   # Elm Street Plumbing (TW000005) is formed on 2021-02-10
    exactly = set_insolvency(mentions, truth, "TW000004", "2018-02-10")
    a_day_more = set_insolvency(mentions, truth, "TW000004", "2018-02-09")
    assert verdicts(bl.same_name_flags(["TW000005"], exactly, claims))["TW000005"] == "FLAG"
    assert verdicts(bl.same_name_flags(["TW000005"], a_day_more, claims))["TW000005"] == "CLEAR"
    with pytest.raises(ValueError, match="whole number of years"):
        bl.same_name_flags(["TW000005"], mentions, claims, window_years=2.5)


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


def test_officer_link_pairs_are_in_the_shared_format():
    mentions, _, truth = tiny_world()
    pairs = bl.officer_link_pairs(mentions)
    ev.check_columns(pairs, "pairs")
    assert (pairs["p"] == 1.0).all()
    person = truth["mention"]
    expected = {tuple(sorted((person["p5"], person["p9"]))), tuple(sorted((person["p6"], person["p7"])))}
    assert set(zip(pairs["a"], pairs["b"])) == expected


# --- Both linking baselines: what counts as evidence ------------------------------------

def test_only_director_claims_count():
    # Regression: a "controls" claim (a person with significant control) used to count as a
    # directorship, on the earlier company's side and on the query company's side.
    mentions, claims, truth = tiny_world()
    person, company = truth["mention"], truth["mention"]
    both = [bl.same_name_flags, bl.officer_link_flags]

    # Priya Lambert (same officer id as Brightwater's director) controls Harrow Build Ltd,
    # which went insolvent in 2021, but was never its director.
    for relation, expected in [("controls", "CLEAR"), ("director_of", "FLAG")]:
        extra = with_claim(claims, "earlier", person["p6"], relation, company["TW000001"], "2017-02-01")
        for baseline in both:
            assert verdicts(baseline(["TW000007"], mentions, extra))["TW000007"] == expected

    # The phoenix Daniel Harrow controls Brightwater from its first day, but isn't its director.
    for relation, expected in [("controls", "CLEAR"), ("director_of", "FLAG")]:
        extra = with_claim(claims, "query", person["p2"], relation, company["TW000007"], "2021-05-15")
        assert verdicts(bl.same_name_flags(["TW000007"], mentions, extra))["TW000007"] == expected


def test_missing_records_clear_with_their_own_reason():
    # Regression: a company we have no data on used to get "no director matches" as its reason.
    mentions, claims, _ = tiny_world()
    for baseline in [bl.same_name_flags, bl.officer_link_flags]:
        table = baseline(["TW999999", "TW000006"], mentions, claims)   # not in our data; no directors
        assert set(table["decision"]) == {"CLEAR"}
        assert all(reason.startswith("No director records for") for reason in table["reason"])


# --- The as-of rule (ADR-001): nothing from after the formation date --------------------

def test_a_director_appointed_after_formation_does_not_count():
    mentions, claims, truth = tiny_world()   # Brightwater (TW000007) is formed on 2021-05-15
    for start, expected in [("2021-08-01", "CLEAR"), ("2021-05-15", "FLAG")]:
        # A second Daniel Harrow joins Brightwater; a namesake ran Harrow Build Ltd (insolvent 2021).
        m, c = with_appointment(mentions, claims, "late", truth["mention"]["p3"], truth["mention"]["TW000007"], start)
        assert verdicts(bl.same_name_flags(["TW000007"], m, c))["TW000007"] == expected


def test_a_namesake_appointed_after_formation_does_not_count():
    mentions, claims, truth = tiny_world()
    for start, expected in [("2021-07-01", "CLEAR"), ("2019-01-01", "FLAG")]:
        # Another Priya Lambert record (same officer id) at the insolvent Smith and Sons Joinery.
        m, c = with_appointment(mentions, claims, "joinery", truth["mention"]["p6"], truth["mention"]["TW000004"], start)
        for baseline in [bl.same_name_flags, bl.officer_link_flags]:
            assert verdicts(baseline(["TW000007"], m, c))["TW000007"] == expected


def test_a_later_insolvency_of_an_existing_company_does_not_count():
    mentions, claims, truth = tiny_world()   # Northgate Roofing (TW000003) is formed on 2021-06-01
    # Only one Daniel Harrow company ever fails: Harrow Build Services, which exists by then
    # but fails in 2022, after Northgate's formation.
    no_old_failure = set_insolvency(mentions, truth, "TW000001", None)
    assert verdicts(bl.same_name_flags(["TW000003"], no_old_failure, claims))["TW000003"] == "CLEAR"
    failed_before = set_insolvency(no_old_failure, truth, "TW000002", "2021-05-01")
    assert verdicts(bl.same_name_flags(["TW000003"], failed_before, claims))["TW000003"] == "FLAG"


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

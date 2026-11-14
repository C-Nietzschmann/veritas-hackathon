"""Tests for src/infer.py, one identity per director (card #32)."""

import itertools
import math

import pandas as pd
import pytest

from src import evidence as ev
from src.infer import one_identity, person_pairs, sample_worlds


def by_listing_every_case(ps):
    """The same answer the slow way: list every yes/no combination of the matches, keep the
    ones where at most one is yes, and see how much of their chance each candidate has."""
    kept, share = 0.0, [0.0] * len(ps)
    for case in itertools.product([False, True], repeat=len(ps)):
        if sum(case) > 1:
            continue   # the director can't be two people
        chance = math.prod(p if yes else 1 - p for p, yes in zip(ps, case))
        kept += chance
        for k, yes in enumerate(case):
            if yes:
                share[k] += chance
    return [one / kept for one in share]


def test_one_candidate_gives_back_its_p():
    assert one_identity([0.3]) == pytest.approx([0.3])
    assert one_identity([0.9]) == pytest.approx([0.9])


def test_two_even_candidates_get_a_third_each_and_nobody_gets_the_rest():
    shares = one_identity([0.5, 0.5])
    assert shares == pytest.approx([1 / 3, 1 / 3])
    assert 1 - sum(shares) == pytest.approx(1 / 3)   # nobody we know


@pytest.mark.parametrize("ps", [[0.5, 0.5], [0.9, 0.9, 0.9], [0.05] * 20, [0.99, 0.01], [0.2, 0.7, 0.4, 0.6]])
def test_the_shares_never_add_up_to_more_than_1(ps):
    shares = one_identity(ps)
    assert sum(shares) <= 1
    assert all(0 <= share <= p for share, p in zip(shares, ps))   # a rival never raises a share


@pytest.mark.parametrize("ps", [[0.3], [0.5, 0.5], [0.9, 0.2], [0.2, 0.7, 0.4, 0.6], [0.05] * 6])
def test_the_closed_form_agrees_with_listing_every_case(ps):
    assert one_identity(ps) == pytest.approx(by_listing_every_case(ps))


def test_more_look_alikes_make_each_candidate_less_likely():
    alone = one_identity([0.6])[0]
    with_two_look_alikes = one_identity([0.6, 0.3, 0.3])[0]
    assert with_two_look_alikes < alone


def test_no_candidates_gives_no_shares():
    assert one_identity([]) == []


def test_a_certain_candidate_takes_everything_and_two_share():
    assert one_identity([1.0, 0.6]) == [1.0, 0.0]
    assert one_identity([1.0, 1.0, 0.6]) == [0.5, 0.5, 0.0]


@pytest.mark.parametrize("bad", [-0.1, 1.2, float("nan")])
def test_a_p_outside_0_to_1_is_refused(bad):
    with pytest.raises(ValueError, match="between 0 and 1"):
        one_identity([0.5, bad])


def test_a_candidate_with_p_0_gets_nothing_and_takes_nothing():
    assert one_identity([0.0, 0.5]) == pytest.approx([0.0, 0.5])
    assert one_identity([0.0]) == [0.0]


# --- 32.2 Possible worlds --------------------------------------------------------------

def pairs_of(*rows):
    """A hand-made pairs table: (a, b, p) each."""
    return pd.DataFrame([(a, b, p, None, "hand_made", None) for a, b, p in rows], columns=ev.PAIR_COLS)


def p_of(sampled):
    return {(a, b): p for a, b, p in zip(sampled["a"], sampled["b"], sampled["p"])}


def matchings_listed(rows):
    """The exact answer the slow way, for any pairs: list every yes/no combination, keep the
    ones where no record has two "yes" pairs, and see how much of their chance each pair has."""
    kept, share = 0.0, [0.0] * len(rows)
    for case in itertools.product([False, True], repeat=len(rows)):
        records = [record for (a, b, p), yes in zip(rows, case) if yes for record in (a, b)]
        if len(records) != len(set(records)):
            continue
        chance = math.prod(p if yes else 1 - p for (a, b, p), yes in zip(rows, case))
        kept += chance
        for k, yes in enumerate(case):
            if yes:
                share[k] += chance
    return [one / kept for one in share]


def test_where_nothing_interacts_the_worlds_reproduce_the_closed_form():
    # One director, three candidates who have no other pairs.
    ps = [0.5, 0.5, 0.2]
    sampled = sample_worlds(pairs_of(("d", "x", ps[0]), ("d", "y", ps[1]), ("d", "z", ps[2])), n=4000, seed=42)
    assert list(sampled["p"]) == pytest.approx(one_identity(ps), abs=0.03)
    assert set(sampled["method"]) == {"possible_worlds"}


def test_a_pair_on_its_own_keeps_its_p():
    sampled = sample_worlds(pairs_of(("d", "x", 0.3)), n=4000, seed=42)
    assert sampled["p"].iloc[0] == pytest.approx(0.3, abs=0.03)
    assert sampled["worlds_kept"].iloc[0] == 4000   # nothing to break the rule with


def test_two_directors_pointing_at_one_earlier_person_agree_with_listing_every_case():
    # d1 and d2 both look like x, and d1 also looks like y: the closed form can't do this.
    rows = [("d1", "x", 0.6), ("d2", "x", 0.6), ("d1", "y", 0.5)]
    sampled = sample_worlds(pairs_of(*rows), n=4000, seed=42)
    assert list(sampled["p"]) == pytest.approx(matchings_listed(rows), abs=0.03)
    by_pair = p_of(sampled)
    assert by_pair[("d1", "x")] + by_pair[("d2", "x")] <= 1   # x is at most one of the two directors


def test_the_same_seed_gives_the_same_worlds_and_another_seed_others():
    pairs = pairs_of(("d", "x", 0.5), ("d", "y", 0.5))
    assert list(sample_worlds(pairs, seed=1)["p"]) == list(sample_worlds(pairs, seed=1)["p"])
    assert list(sample_worlds(pairs, seed=1)["p"]) != list(sample_worlds(pairs, seed=2)["p"])


def test_the_order_of_the_rows_changes_nothing():
    pairs = pairs_of(("d", "x", 0.5), ("d", "y", 0.4), ("e", "z", 0.7))
    backwards = pairs.iloc[::-1].reset_index(drop=True)
    assert p_of(sample_worlds(pairs, seed=3)) == p_of(sample_worlds(backwards, seed=3))


def test_each_pair_lists_the_pairs_of_its_group_and_only_those():
    sampled = sample_worlds(pairs_of(("d", "x", 0.5), ("d", "y", 0.4), ("e", "z", 0.7)), seed=3)
    depends = dict(zip(zip(sampled["a"], sampled["b"]), sampled["depends_on"]))
    assert depends[("d", "x")] == depends[("d", "y")] == [("d", "x"), ("d", "y")]
    assert depends[("e", "z")] == [("e", "z")]


def test_matches_that_always_contradict_leave_no_world_and_say_so():
    with pytest.warns(UserWarning, match="no world left"):
        sampled = sample_worlds(pairs_of(("d", "x", 1.0), ("d", "y", 1.0)), seed=3)
    assert sampled["p"].isna().all() and (sampled["worlds_kept"] == 0).all()


def test_the_same_pair_twice_is_refused():
    with pytest.raises(ValueError, match="listed twice"):
        sample_worlds(pairs_of(("d", "x", 0.5), ("x", "d", 0.5)))


def test_person_pairs_makes_one_candidate_of_two_records_of_one_person():
    # The director d, and two records x1, x2 of one earlier person under officer id "old".
    person_of = {"d": "new", "x1": "old", "x2": "old"}
    people = person_pairs(pairs_of(("d", "x1", 0.9), ("d", "x2", 0.6), ("x1", "x2", 0.99)), person_of)
    assert [(a, b, p) for a, b, p in zip(people["a"], people["b"], people["p"])] == [("new", "old", 0.9)]
    ev.check_columns(people, "pairs")


def test_person_pairs_lets_a_record_without_an_officer_id_stand_for_itself():
    people = person_pairs(pairs_of(("d", "x", 0.4)), {"d": "new", "x": None})
    assert list(zip(people["a"], people["b"])) == [("new", "x")]

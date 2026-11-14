"""Tests for src/infer.py, one identity per director (card #32)."""

import itertools
import math

import pytest

from src.infer import one_identity


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

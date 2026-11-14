"""Tests for src/resolve.py, entity resolution (card #30), on the tiny world."""

from src import evidence as ev
from src import resolve as rs
from tests.tiny_world import tiny_world


def pair_set(pairs):
    return set(zip(pairs["a"], pairs["b"]))


def pair(truth, key_a, key_b):
    return tuple(sorted((truth["mention"][key_a], truth["mention"][key_b])))


def renamed(mentions, truth, key, **changes):
    """The mentions with one person's columns changed."""
    mentions = mentions.copy()
    row = mentions["mention_id"] == truth["mention"][key]
    for col, value in changes.items():
        mentions.loc[row, col] = value
    return mentions


# --- 30.1 Blocking ---------------------------------------------------------------------

def test_name_parts_reads_both_ways_a_name_is_written():
    assert rs.name_parts("HARROW, Daniel James") == ("harrow", "d")
    assert rs.name_parts("Mr Daniel Harrow") == ("harrow", "d")
    assert rs.name_parts("SMITH-JONES, Anna, Dr") == ("smith jones", "a")
    assert rs.name_parts("Harrow") == ("harrow", "")
    assert rs.name_parts(None) == ("", "")


def test_every_true_same_person_pair_survives_blocking():
    mentions, _, truth = tiny_world()
    assert set(truth["same_person"]) <= pair_set(rs.candidate_pairs(mentions))


def test_pairs_are_people_once_each_and_in_the_shared_shape():
    mentions, _, _ = tiny_world()
    pairs = rs.candidate_pairs(mentions)
    ev.check_columns(pairs, "pairs")
    people = set(mentions.loc[mentions["kind"] == "person", "mention_id"])
    assert set(pairs["a"]) | set(pairs["b"]) <= people
    assert (pairs["a"] < pairs["b"]).all()
    assert not pairs.duplicated(["a", "b"]).any()


def test_register_and_plain_spelling_of_one_name_are_paired():
    mentions, _, truth = tiny_world()
    mentions = renamed(mentions, truth, "p2", name="HARROW, Daniel")
    assert pair(truth, "p1", "p2") in pair_set(rs.candidate_pairs(mentions))


def test_same_birth_month_pairs_a_misspelt_surname_but_not_a_different_one():
    mentions, _, truth = tiny_world()
    # p2 is p1 with a typo; Ruth Okafor (p8) is given p1's birth month as the control.
    mentions = renamed(mentions, truth, "p2", name="Daniel Harow")
    mentions = renamed(mentions, truth, "p8", birth_year=1979, birth_month=4)
    found = pair_set(rs.candidate_pairs(mentions))
    assert pair(truth, "p1", "p2") in found
    assert pair(truth, "p1", "p8") not in found


def test_a_person_with_no_name_is_in_no_pair():
    mentions, _, truth = tiny_world()
    mentions = renamed(mentions, truth, "p1", name=None)
    mentions = renamed(mentions, truth, "p2", name=None)   # same birth month as p1
    pairs = rs.candidate_pairs(mentions)
    nameless = {truth["mention"]["p1"], truth["mention"]["p2"]}
    assert not (set(pairs["a"]) | set(pairs["b"])) & nameless

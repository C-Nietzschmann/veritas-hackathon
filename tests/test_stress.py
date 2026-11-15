"""Tests for src/stress.py: the name-and-birth baseline and the stress test (card #191)."""
import random

import pandas as pd

from src import resolve, stress
from tests.tiny_world import tiny_world


def test_split_and_join_read_both_ways_a_name_is_written():
    assert stress.split_name("HARROW, Daniel James") == ("HARROW", ["Daniel", "James"])
    assert stress.split_name("Daniel James Harrow") == ("Harrow", ["Daniel", "James"])
    assert stress.join_name("HARROW", ["Daniel"]) == "HARROW, Daniel"


def test_a_typo_keeps_the_letters_and_the_first_letter_but_changes_the_word():
    word = stress.typo("harrow", random.Random(1))
    assert word != "harrow" and sorted(word) == sorted("harrow") and word[0] == "h"
    assert stress.typo("lee", random.Random(1)) == "leee"   # too short to swap inside


def test_name_and_birth_needs_the_name_and_the_birth_date_and_a_missing_date_never_counts():
    mentions = pd.DataFrame({"mention_id": ["d", "same", "other", "none"],
                             "birth_year": [1979, "1979", 1979, None], "birth_month": [3, 3, 4, None]})
    links = pd.DataFrame({"director": ["d", "d", "d", "d"], "record": ["same", "other", "none", "same"],
                          "same name": [True, True, True, False]})
    assert list(stress.name_and_birth(links, mentions)) == [True, False, False, False]


def test_compare_counts_confirmed_and_unconfirmed_links_per_method():
    links = pd.DataFrame({"company_id": ["A", "A", "B"], "register": ["same officer id", "different ids", "different ids"],
                          "rule": [True, True, True], "careful": [True, False, False]})
    table = stress.compare(links, ["rule", "careful"])
    assert table.loc["rule"].to_dict() == {"links": 3, "confirmed": 1, "not confirmed": 2,
                                           "recall vs the register": 1.0, "companies linked": 2}
    assert table.loc["careful", "not confirmed"] == 0 and table.loc["careful", "companies linked"] == 1


def test_stress_test_gives_one_row_per_change_and_a_new_surname_is_never_linked():
    mentions, _, _ = tiny_world()
    labelled = resolve.labelled_pairs(mentions)
    model = resolve.train_matcher(resolve.pair_features(labelled, mentions), labelled["label"], 42)
    same_person = labelled[labelled["label"] == 1]
    table = stress.stress_test(model, mentions, same_person, seed=42)
    assert len(table) == 8 and (table["pairs"] == len(same_person)).all()
    assert table.loc["new surname", "matcher still links it %"] == 0
    assert table.loc["new surname", "same-name rule still links it %"] == 0
    assert table.loc["nothing changed", "same-name rule still links it %"] == 100
    # the same seed gives the same typos, so the same table
    pd.testing.assert_frame_equal(table, stress.stress_test(model, mentions, same_person, seed=42))


def test_stress_test_with_no_pairs_gives_an_empty_table():
    mentions, _, _ = tiny_world()
    assert stress.stress_test(None, mentions, pd.DataFrame({"a": [], "b": []}), seed=42).empty

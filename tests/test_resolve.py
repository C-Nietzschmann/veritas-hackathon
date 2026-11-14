"""Tests for src/resolve.py, entity resolution (card #30), on the tiny world."""

import pandas as pd

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
    assert rs.name_parts("SMITH, Mr John") == rs.name_parts("SMITH, John") == ("smith", "j")
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


# --- 30.2 Pair features ----------------------------------------------------------------

def features_of(mentions, truth, key_a, key_b):
    """The feature row of one pair, as a dict."""
    a, b = pair(truth, key_a, key_b)
    pairs = pd.DataFrame([(a, b, None, None, "by hand", None)], columns=ev.PAIR_COLS)
    return rs.pair_features(pairs, mentions).iloc[0].to_dict()


def test_officer_id_is_never_a_feature():
    mentions, _, _ = tiny_world()
    pairs = rs.candidate_pairs(mentions)
    assert "officer_id" not in rs.FEATURE_COLS
    assert list(rs.pair_features(pairs, mentions).columns) == rs.FEATURE_COLS
    # And it isn't read on the quiet: without any officer id the features are the same.
    without = mentions.assign(officer_id=None)
    assert rs.pair_features(pairs, without).equals(rs.pair_features(pairs, mentions))


def test_one_feature_row_per_pair_and_no_empty_cells():
    mentions, _, _ = tiny_world()
    pairs = rs.candidate_pairs(mentions)
    features = rs.pair_features(pairs, mentions)
    assert len(features) == len(pairs)
    assert features.notna().all().all()


def test_the_phoenix_agrees_on_name_and_birth_the_look_alike_only_on_name():
    mentions, _, truth = tiny_world()
    phoenix = features_of(mentions, truth, "p1", "p2")       # the same Daniel Harrow, new postcode
    look_alike = features_of(mentions, truth, "p1", "p3")    # another Daniel Harrow
    assert phoenix["name_similarity"] == 1 and phoenix["birth_same"] == 1
    assert phoenix["postcode_same"] == 1                      # ZZ1 1AA and ZZ1 1AB: the same district
    assert look_alike["name_similarity"] == 1
    assert look_alike["birth_same"] == 0 and look_alike["postcode_same"] == 0


def test_name_order_and_titles_do_not_lower_the_similarity():
    mentions, _, truth = tiny_world()
    mentions = renamed(mentions, truth, "p2", name="HARROW, Daniel")
    mentions = renamed(mentions, truth, "p1", name="Mr Daniel Harrow")
    assert features_of(mentions, truth, "p1", "p2")["name_similarity"] == 1


def test_a_missing_value_is_marked_missing_not_different():
    mentions, _, truth = tiny_world()
    mentions = renamed(mentions, truth, "p2", birth_month=None, nationality=None)
    row = features_of(mentions, truth, "p1", "p2")
    assert row["birth_missing"] == 1 and row["birth_same"] == 0
    assert row["nationality_missing"] == 1 and row["nationality_same"] == 0
    assert row["postcode_missing"] == 0                      # the control: still known


def test_district_reads_a_postcode_with_or_without_its_space():
    assert rs.district("ZZ1 1AA") == rs.district("zz11aa") == "ZZ1"
    assert rs.district("ZZ1") == "ZZ1"                        # only the district was written
    assert rs.district(None) == rs.district("  ") == ""


# --- 30.3 Blocking recall --------------------------------------------------------------

def test_blocking_keeps_every_pair_the_tiny_register_links():
    mentions, _, _ = tiny_world()
    result = rs.blocking_recall(rs.candidate_pairs(mentions), mentions)
    assert result == dict(true_pairs=2, kept=2, recall=1.0)   # p5-p9 and p6-p7 share an officer id
    swapped = rs.candidate_pairs(mentions).rename(columns={"a": "b", "b": "a"})
    assert rs.blocking_recall(swapped, mentions)["recall"] == 1.0   # (b, a) is the same pair


def test_recall_drops_when_blocking_loses_a_linked_pair():
    mentions, _, truth = tiny_world()
    # p9 is p5 under another name and with no birth date: neither blocking route proposes it.
    mentions = renamed(mentions, truth, "p9", name="Jim Smythe", birth_year=None)
    result = rs.blocking_recall(rs.candidate_pairs(mentions), mentions)
    assert result == dict(true_pairs=2, kept=1, recall=0.5)


def test_recall_is_none_when_the_register_links_nobody():
    mentions, _, _ = tiny_world()
    mentions = mentions.assign(officer_id=None)
    assert rs.blocking_recall(rs.candidate_pairs(mentions), mentions)["recall"] is None


# --- 31.1 Labelled pairs ---------------------------------------------------------------

def labels_of(mentions):
    pairs = rs.labelled_pairs(mentions)
    return dict(zip(zip(pairs["a"], pairs["b"]), pairs["label"]))


def test_same_officer_id_is_label_1_and_a_different_id_is_label_0():
    mentions, _, truth = tiny_world()
    labels = labels_of(mentions)
    assert labels[pair(truth, "p5", "p9")] == 1 and labels[pair(truth, "p6", "p7")] == 1
    assert labels[pair(truth, "p1", "p3")] == 0             # a look-alike: other officer id
    assert sorted(labels.values()) == [0, 0, 0, 0, 0, 1, 1]


def test_the_phoenix_gets_label_0_which_is_the_labels_known_mistake():
    # The same Daniel Harrow under a new officer id: the register says "different people".
    mentions, _, truth = tiny_world()
    assert pair(truth, "p1", "p2") in truth["same_person"]
    assert labels_of(mentions)[pair(truth, "p1", "p2")] == 0


def test_a_linked_pair_that_blocking_missed_is_still_label_1():
    mentions, _, truth = tiny_world()
    mentions = renamed(mentions, truth, "p9", name="Jim Smythe", birth_year=None)
    assert labels_of(mentions)[pair(truth, "p5", "p9")] == 1


def test_a_pair_with_a_missing_officer_id_has_no_label():
    mentions, _, truth = tiny_world()
    mentions = renamed(mentions, truth, "p3", officer_id=None)
    labels = labels_of(mentions)
    assert pair(truth, "p1", "p3") not in labels and pair(truth, "p2", "p3") not in labels


# --- 31.2 The matcher ------------------------------------------------------------------

def trained(mentions, seed=42):
    """A matcher trained on the mentions' own labelled pairs, and those pairs scored."""
    labelled = rs.labelled_pairs(mentions)
    model = rs.train_matcher(rs.pair_features(labelled, mentions), labelled["label"], seed)
    return model, rs.scored_pairs(model, labelled, mentions)


def test_every_pair_gets_a_p_strictly_between_0_and_1_and_none_is_dropped():
    mentions, _, _ = tiny_world()
    _, scored = trained(mentions)
    ev.check_columns(scored, "pairs")
    assert len(scored) == len(rs.labelled_pairs(mentions))    # R6: nothing merged, nothing dropped
    assert ((scored["p"] > 0) & (scored["p"] < 1)).all()
    assert set(scored["method"]) == {"matcher"}


def test_the_same_seed_gives_the_same_p():
    mentions, _, _ = tiny_world()
    assert list(trained(mentions, seed=42)[1]["p"]) == list(trained(mentions, seed=42)[1]["p"])


def test_pairs_that_agree_on_birth_and_postcode_score_higher_than_look_alikes():
    mentions, _, truth = tiny_world()
    _, scored = trained(mentions)
    p = dict(zip(zip(scored["a"], scored["b"]), scored["p"]))
    for look_alike in truth["look_alikes"]:
        assert p[pair(truth, "p6", "p7")] > p[look_alike]


def test_each_scored_pair_carries_its_features_and_never_the_officer_id():
    mentions, _, _ = tiny_world()
    model, scored = trained(mentions)
    assert all(list(row) == rs.FEATURE_COLS for row in scored["features"])
    assert list(rs.matcher_weights(model).index) == rs.FEATURE_COLS + ["intercept"]

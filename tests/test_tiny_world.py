"""Tests for the tiny world (sub-tasks 21.1 and 21.2): it is valid, stable, and its stories hold."""

import pandas as pd

from src import evidence as ev
from tests.tiny_world import APPOINTMENTS, tiny_world


def test_passes_the_schema_checks():
    mentions, claims, _ = tiny_world()
    ev.check_rows(mentions, claims)


def test_same_tables_every_call():
    first, second = tiny_world(), tiny_world()
    pd.testing.assert_frame_equal(first[0], second[0])
    pd.testing.assert_frame_equal(first[1], second[1])
    assert first[2] == second[2]


def test_about_thirty_rows():
    mentions, claims, _ = tiny_world()
    assert 25 <= len(mentions) + len(claims) <= 35


def test_every_query_has_an_expected_decision():
    _, _, truth = tiny_world()
    for query in truth["queries"]:
        assert truth["decision"][query] in ev.DECISIONS
        assert query in truth["predecessor"] and query in truth["failed"]


def test_look_alikes_are_not_the_same_person():
    _, _, truth = tiny_world()
    assert not set(truth["look_alikes"]) & set(truth["same_person"])


def test_same_person_pairs_share_a_birth_date_and_look_alikes_do_not():
    born = {key: when for key, _, when, *_ in APPOINTMENTS}
    _, _, truth = tiny_world()
    key_of = {mention_id: key for key, mention_id in truth["mention"].items()}
    for a, b in truth["same_person"]:
        assert born[key_of[a]] == born[key_of[b]]
    for a, b in truth["look_alikes"]:
        assert born[key_of[a]] != born[key_of[b]]


def test_phoenix_director_got_a_new_officer_id():
    mentions, _, truth = tiny_world()
    officer = mentions.set_index("mention_id")["officer_id"]
    assert officer[truth["mention"]["p1"]] != officer[truth["mention"]["p2"]]


def test_no_evidence_company_has_no_claims():
    _, claims, truth = tiny_world()
    assert truth["mention"]["TW000006"] not in set(claims["object"])


def test_the_future_insolvency_comes_after_the_query():
    mentions, claims, truth = tiny_world()
    formed = mentions.set_index("company_number")["incorporated_on"]
    edges = ev.observed_graph(claims, as_of=formed["TW000005"])
    assert truth["mention"]["p9"] not in set(edges["subject"])


def test_copied_claim_has_the_same_origin():
    _, claims, truth = tiny_world()
    brightwater = claims[claims["object"] == truth["mention"]["TW000007"]]
    assert len(brightwater) == 2
    assert brightwater["origin"].nunique() == 1
    assert brightwater["source"].nunique() == 2

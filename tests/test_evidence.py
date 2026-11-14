"""Tests for src/evidence.py, the shared schema (sub-tasks 22.1 to 22.4).

They run on a small hand-made example with invented names. Once the shared
tiny world (#21) exists, they can switch to it.
"""

import hashlib

import pandas as pd
import pytest

from src import evidence as ev

RAW = b'{"company_number": "00000001", "officers": ["Alex Example"]}'


def mini_world():
    """Two companies, two people with the same name, three claims."""
    ref = ev.record_ref("data/raw/example.json", 0, RAW)
    provenance = dict(source="test", record_ref=ref, origin="test", adapter="test")

    def mention(key, kind, name, **attributes):
        row = dict.fromkeys(ev.MENTION_COLS)
        row.update(mention_id=ev.make_id("test", key), kind=kind, name=name, **provenance)
        row.update(attributes)
        return row

    mentions = pd.DataFrame([
        mention("company/1", "company", "Example Builders Ltd", company_number="00000001"),
        mention("company/2", "company", "Example Builders 2021 Ltd", company_number="00000002"),
        mention("person/1", "person", "Alex Example", birth_month=4, birth_year=1980),
        mention("person/2", "person", "Alex Example", birth_month=9, birth_year=1975),
    ], columns=ev.MENTION_COLS)
    company_1, company_2, alex_1, alex_2 = mentions["mention_id"]

    def claim(key, subject, relation, obj, start, end=None):
        return dict(claim_id=ev.make_id("test", key), subject=subject, relation=relation,
                    object=obj, valid_from=start, valid_to=end, **provenance)

    claims = pd.DataFrame([
        claim("appointment/1", alex_1, "director_of", company_1, "2019-03-01", "2021-04-30"),
        claim("appointment/2", alex_1, "director_of", company_2, "2021-05-01"),
        claim("control/1", alex_2, "controls", company_2, "2022-02-01"),
    ], columns=ev.CLAIM_COLS)
    return mentions, claims


def assert_rejected(mentions, claims, *fragments):
    """check_rows must raise, and its message must contain every fragment."""
    with pytest.raises(ev.SchemaError) as error:
        ev.check_rows(mentions, claims)
    for fragment in fragments:
        assert fragment in str(error.value)


# --- 22.1 The columns ----------------------------------------------------------

def test_empty_tables_have_the_schema_columns():
    assert list(ev.empty_mentions().columns) == ev.MENTION_COLS
    assert list(ev.empty_claims().columns) == ev.CLAIM_COLS
    for name, columns in ev.TABLES.items():
        assert list(ev.empty_table(name).columns) == columns


def test_display_columns_sit_next_to_what_they_mask():
    columns = ev.MENTION_COLS
    assert columns.index("display_name") == columns.index("name") + 1
    assert columns.index("display_postcode") == columns.index("postcode") + 1


# --- 22.2 Stable ids and record_ref --------------------------------------------

def test_ids_are_stable_across_runs():
    assert ev.make_id("ch", "company/00000001") == ev.make_id("ch", "company/00000001")
    assert ev.make_id("ch", "company/00000001") != ev.make_id("ch", "company/00000002")
    first, _ = mini_world()
    second, _ = mini_world()
    assert first["mention_id"].tolist() == second["mention_id"].tolist()


def test_record_ref_rehash_matches_the_raw_response():
    ref = ev.record_ref("data/raw/example.json", 3, RAW)
    path, row, sha = ev.parse_record_ref(ref)
    assert (path, row) == ("data/raw/example.json", 3)
    assert sha == hashlib.sha256(RAW).hexdigest()
    assert ev.raw_unchanged(ref, RAW)
    assert not ev.raw_unchanged(ref, RAW + b" ")


# --- 22.3 Row checks -------------------------------------------------------------

def test_good_rows_pass():
    mentions, claims = mini_world()
    ev.check_rows(mentions, claims)


def test_empty_source_is_rejected():
    mentions, claims = mini_world()
    claims.loc[0, "source"] = " "
    assert_rejected(mentions, claims, f"claims row {claims.loc[0, 'claim_id']}: empty source", "R2")


def test_missing_record_ref_is_rejected():
    mentions, claims = mini_world()
    mentions.loc[1, "record_ref"] = None
    assert_rejected(mentions, claims, f"mentions row {mentions.loc[1, 'mention_id']}: empty record_ref", "R2")


def test_duplicate_id_is_rejected():
    mentions, claims = mini_world()
    claims.loc[2, "claim_id"] = claims.loc[1, "claim_id"]
    assert_rejected(mentions, claims, f"claims row {claims.loc[1, 'claim_id']}: duplicate claim_id")


def test_unknown_kind_is_rejected():
    mentions, claims = mini_world()
    mentions.loc[0, "kind"] = "trust"
    assert_rejected(mentions, claims, f"mentions row {mentions.loc[0, 'mention_id']}: unknown kind 'trust'")


def test_unknown_relation_is_rejected():
    mentions, claims = mini_world()
    claims.loc[0, "relation"] = "knows"
    assert_rejected(mentions, claims, f"claims row {claims.loc[0, 'claim_id']}: unknown relation 'knows'")


def test_claim_pointing_at_no_mention_is_rejected():
    mentions, claims = mini_world()
    claims.loc[2, "object"] = "nobody"
    assert_rejected(mentions, claims, f"claims row {claims.loc[2, 'claim_id']}: object 'nobody' is not a mention")


def test_end_before_start_is_rejected():
    mentions, claims = mini_world()
    claims.loc[0, "valid_to"] = "2018-01-01"
    assert_rejected(mentions, claims, f"claims row {claims.loc[0, 'claim_id']}: valid_to is before valid_from")


def test_empty_id_is_rejected():
    mentions, claims = mini_world()
    mentions.loc[0, "mention_id"] = None
    claims.loc[0, "object"] = None       # would otherwise "match" the mention with no id
    assert_rejected(mentions, claims, "mentions: 1 row(s) with an empty mention_id")


def test_claim_written_the_wrong_way_round_is_rejected():
    mentions, claims = mini_world()
    person, company = claims.loc[0, ["subject", "object"]]
    claims.loc[0, ["subject", "object"]] = [company, person]
    assert_rejected(mentions, claims, f"claims row {claims.loc[0, 'claim_id']}: the object of director_of must be a company")


def test_unreadable_date_is_rejected():
    mentions, claims = mini_world()
    claims.loc[1, "valid_from"] = "01/05/2021"
    assert_rejected(mentions, claims, f"claims row {claims.loc[1, 'claim_id']}: valid_from '01/05/2021' is not a date")


def test_unreadable_company_date_is_rejected():
    mentions, claims = mini_world()
    mentions.loc[0, "incorporated_on"] = "15/03/2021"   # row 0 is a company
    assert_rejected(mentions, claims, f"mentions row {mentions.loc[0, 'mention_id']}: incorporated_on '15/03/2021' is not a date")


def test_record_ref_in_the_wrong_shape_is_rejected():
    mentions, claims = mini_world()
    mentions.loc[0, "record_ref"] = "data/raw/example.json"
    assert_rejected(mentions, claims, f"mentions row {mentions.loc[0, 'mention_id']}: record_ref is not file#row@sha256")


# --- 22.4 The observed graph -------------------------------------------------------

def test_one_edge_per_claim():
    _, claims = mini_world()
    edges = ev.observed_graph(claims)
    assert len(edges) == len(claims)
    assert set(edges["claim_id"]) == set(claims["claim_id"])


def test_as_of_drops_later_claims():
    _, claims = mini_world()
    edges = ev.observed_graph(claims, as_of="2021-12-31")
    assert set(edges["claim_id"]) == set(claims.loc[[0, 1], "claim_id"])


def test_as_of_keeps_a_claim_that_starts_that_day():
    # Directors are usually appointed on the day their company is formed, so that day counts.
    _, claims = mini_world()
    edges = ev.observed_graph(claims, as_of="2021-05-01")
    assert claims.loc[1, "claim_id"] in set(edges["claim_id"])


def test_as_of_hides_end_dates_from_the_future():
    _, claims = mini_world()                       # claim 0 runs 2019-03-01 to 2021-04-30
    edges = ev.observed_graph(claims, as_of="2020-01-01")
    assert len(edges) == 1 and pd.isna(edges.loc[0, "valid_to"])
    edges = ev.observed_graph(claims, as_of="2021-12-31")
    assert "2021-04-30" in set(edges["valid_to"])   # an end date in the past stays


def test_as_of_drops_undated_claims():
    _, claims = mini_world()
    claims.loc[0, "valid_from"] = None
    edges = ev.observed_graph(claims, as_of="2030-01-01")
    assert claims.loc[0, "claim_id"] not in set(edges["claim_id"])
    assert len(edges) == 2

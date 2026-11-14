"""Tests for src/ingest_companies_house.py on the invented raw sample in tests/raw_sample/.

The sample holds four invented companies in the shapes the Companies House API answers with
("TW" numbers and "ZZ" postcodes don't exist in the real register):
- TW000001 Harrow Build: in creditors' voluntary liquidation since 2021-03-15, after an
  earlier voluntary arrangement that must not count.
- TW000002 Harrow Build Services: the query company, formed 2021-04-20, active.
- TW000003 Northgate Roofing: dissolved in 2020.
- TW000004 Elm Street Joinery: in members' voluntary liquidation, a solvent wind-down,
  so it must get no insolvency date.
"""

import json

from src import evidence as ev
from src import ingest_companies_house as ch

SAMPLE = "tests/raw_sample"   # pytest runs from the repo folder (pytest.ini)


def company_rows():
    """The company mentions, one row per company number."""
    return ch.companies_to_mentions(ch.load_raw(SAMPLE)).set_index("company_number")


# --- 25.1 Company profiles become company mentions (#74) ----------------------------

def test_one_mention_per_company():
    raw = ch.load_raw(SAMPLE)
    profiles = [path for path in raw if "/company/" in path]
    mentions = ch.companies_to_mentions(raw)
    assert len(mentions) == len(profiles) == 4
    assert set(mentions["kind"]) == {"company"}
    assert list(mentions.columns) == ev.MENTION_COLS


def test_company_attributes_as_written():
    query = company_rows().loc["TW000002"]
    assert query["name"] == "HARROW BUILD SERVICES LTD"
    assert query["status"] == "active"
    assert query["incorporated_on"] == "2021-04-20"
    assert query["postcode"] == "ZZ1 1AB"
    assert query["sic_code"] == "41202"   # the construction code, not the first one (68100)
    assert ev.is_blank(company_rows()["display_name"]).all()   # masking is card #111


def test_dissolved_company_keeps_its_end_date():
    assert company_rows().loc["TW000003", "dissolved_on"] == "2020-12-01"


def test_insolvency_date_counts_only_liquidation_and_administration():
    rows = company_rows()
    assert rows.loc["TW000001", "insolvency_on"] == "2021-03-15"   # not the 2020 voluntary arrangement
    assert ev.is_blank(rows.loc[["TW000002", "TW000003", "TW000004"], "insolvency_on"]).all()   # TW000004: members' liquidation


def test_company_provenance_points_at_its_raw_file():
    raw = ch.load_raw(SAMPLE)
    row = company_rows().loc["TW000001"]
    path, position, _ = ev.parse_record_ref(row["record_ref"])
    assert (path, position) == ("tests/raw_sample/company/TW000001.json", 0)
    assert ev.raw_unchanged(row["record_ref"], raw[path])   # R1
    assert (row["source"], row["origin"], row["adapter"]) == ("companies_house", "companies_house", "ingest_companies_house")
    assert json.loads(raw[path])["company_name"] == row["name"]


def test_ids_do_not_depend_on_file_order():
    raw = ch.load_raw(SAMPLE)
    backwards = dict(reversed(list(raw.items())))
    assert ch.companies_to_mentions(raw).equals(ch.companies_to_mentions(backwards))   # R7

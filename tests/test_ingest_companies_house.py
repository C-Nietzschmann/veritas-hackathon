"""Tests for src/ingest_companies_house.py on the invented raw sample in tests/raw_sample/.

The sample holds four invented companies in the shapes the Companies House API answers with
("TW" numbers and "ZZ" postcodes don't exist in the real register):
- TW000001 Harrow Build: in creditors' voluntary liquidation since 2021-03-15, after an
  earlier voluntary arrangement that must not count.
- TW000002 Harrow Build Services: the query company, formed 2021-04-20, active.
- TW000003 Northgate Roofing: dissolved in 2020.
- TW000004 Elm Street Joinery: in members' voluntary liquidation, a solvent wind-down,
  so it must get no insolvency date.

And their officers:
- Daniel Harrow (officer id tw-officer-01) directs TW000001 and then TW000002: one person,
  two records, which must stay two mentions (R6).
- A look-alike Daniel Harrow (tw-officer-03, other birth date and postcode) directed
  TW000003 until he resigned in 2019.
- A secretary at TW000001 and a corporate director at TW000002, both skipped.
"""

import json

import pandas as pd

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


def test_insolvency_date_is_the_earliest_start():
    # A company that went into administration and from there into liquidation: two cases.
    # The earlier start counts, whatever order the cases come in. End dates never count.
    administration = {"type": "in-administration", "dates": [
        {"type": "administration-started-on", "date": "2020-02-01"},
        {"type": "administration-ended-on", "date": "2021-03-01"},
    ]}
    liquidation = {"type": "creditors-voluntary-liquidation", "dates": [
        {"type": "wound-up-on", "date": "2021-03-01"},
    ]}
    assert ch.insolvency_start({"cases": [liquidation, administration]}) == "2020-02-01"


def test_insolvency_date_is_a_start_not_a_petition_or_an_end():
    # Compulsory liquidation: the petition comes before the court's order, the conclusion after.
    # Only the order is the start.
    court_case = {"type": "compulsory-liquidation", "dates": [
        {"type": "petitioned-on", "date": "2019-01-05"},
        {"type": "ordered-to-wind-up-on", "date": "2019-03-01"},
        {"type": "concluded-winding-up-on", "date": "2022-06-30"},
    ]}
    assert ch.insolvency_start({"cases": [court_case]}) == "2019-03-01"


def test_insolvency_start_date_left_empty_is_skipped():
    empty = {"type": "compulsory-liquidation", "dates": [{"type": "wound-up-on", "date": None}, {"type": "wound-up-on"}]}
    assert ch.insolvency_start({"cases": [empty]}) is None
    dated = {"type": "in-administration", "dates": [{"type": "administration-started-on", "date": "2020-02-01"}]}
    assert ch.insolvency_start({"cases": [empty, dated]}) == "2020-02-01"


def test_company_with_only_a_name_and_a_number():
    # Every other field of a profile is optional in the API. Missing ones stay empty.
    profile = {"company_name": "BARE BONES LTD", "company_number": "TW000009"}
    mentions = ch.companies_to_mentions({"data/raw/company/TW000009.json": json.dumps(profile).encode()})
    assert len(mentions) == 1
    assert ev.is_blank(mentions.loc[0, ["status", "incorporated_on", "dissolved_on", "insolvency_on", "sic_code", "postcode"]]).all()
    ev.check_rows(mentions, ev.empty_claims())


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
    for ours, theirs in zip(ch.officers_to_evidence(raw), ch.officers_to_evidence(backwards)):
        assert ours.equals(theirs)


def look_alike_ids(raw):
    """The mention id and the claim id of the look-alike Daniel Harrow (tw-officer-03)."""
    people, claims = ch.officers_to_evidence(raw)
    mention_id = people.loc[people["officer_id"] == "tw-officer-03", "mention_id"].iloc[0]
    claim_id = claims.loc[claims["subject"] == mention_id, "claim_id"].iloc[0]
    return mention_id, claim_id


def test_ids_do_not_depend_on_an_officers_place_in_the_list():
    # A later crawl can list the same officers in another order.
    # The ids come from the appointment link, so they must stay the same (R7).
    raw = ch.load_raw(SAMPLE)
    path = "tests/raw_sample/officers/TW000003.json"
    officers = json.loads(raw[path])
    officers["items"].reverse()
    crawled_again = dict(raw)
    crawled_again[path] = json.dumps(officers).encode()
    assert look_alike_ids(crawled_again) == look_alike_ids(raw)


# --- 25.2 Officer records become person mentions and claims (#75) -------------------

def director_appointments(raw):
    """Count the director appointments in the raw officer files, straight from the JSON."""
    count = 0
    for path, raw_bytes in raw.items():
        if "/officers/" in path:
            for officer in json.loads(raw_bytes)["items"]:
                if officer["officer_role"] == "director":
                    count += 1
    return count


def test_one_claim_per_director_appointment():
    raw = ch.load_raw(SAMPLE)
    people, claims = ch.officers_to_evidence(raw)
    assert len(claims) == len(people) == director_appointments(raw) == 5
    assert set(people["kind"]) == {"person"}
    assert set(claims["relation"]) == {"director_of"}


def test_secretaries_and_corporate_directors_are_skipped():
    people, _ = ch.officers_to_evidence(ch.load_raw(SAMPLE))
    assert "OKAFOR, Ruth" not in set(people["name"])              # secretary
    assert "HARROW HOLDINGS LIMITED" not in set(people["name"])   # corporate director


def bare_officer(role, appointment):
    """An invented officer with only the fields the API always sends. Everything else is optional."""
    return {
        "name": "TESTER, Sam",
        "officer_role": role,
        "links": {
            "self": f"/company/TW000009/appointments/{appointment}",
            "officer": {"appointments": "/officers/tw-officer-09/appointments"},
        },
    }


def officers_file(officers):
    """A raw dict holding one officers file, for company TW000009."""
    return {"data/raw/officers/TW000009.json": json.dumps({"items": officers}).encode()}


def test_nominee_directors_count_but_corporate_nominees_do_not():
    raw = officers_file([
        bare_officer("nominee-director", "tw-appointment-0901"),             # a person
        bare_officer("corporate-nominee-director", "tw-appointment-0902"),   # a company
    ])
    people, claims = ch.officers_to_evidence(raw)
    assert len(people) == len(claims) == 1
    assert ev.parse_record_ref(people.loc[0, "record_ref"])[1] == 0   # the first record: the person


def test_director_with_only_the_required_fields():
    # Old records have no birth date, nationality, address or appointment date. They still count.
    people, claims = ch.officers_to_evidence(officers_file([bare_officer("director", "tw-appointment-0901")]))
    assert len(people) == len(claims) == 1
    assert ev.is_blank(people.loc[0, ["birth_month", "birth_year", "nationality", "postcode"]]).all()
    assert pd.isna(claims.loc[0, "valid_from"]) and pd.isna(claims.loc[0, "valid_to"])


def test_same_person_at_two_companies_stays_two_mentions():
    people, claims = ch.officers_to_evidence(ch.load_raw(SAMPLE))
    daniel = people.loc[people["officer_id"] == "tw-officer-01"]
    assert len(daniel) == 2 and daniel["mention_id"].nunique() == 2   # R6: nothing merged
    companies = claims.loc[claims["subject"].isin(daniel["mention_id"]), "object"]
    assert set(companies) == {ch.company_mention_id("TW000001"), ch.company_mention_id("TW000002")}


def test_look_alike_keeps_its_own_record():
    people, _ = ch.officers_to_evidence(ch.load_raw(SAMPLE))
    harrows = people.loc[people["name"] == "HARROW, Daniel"].set_index("officer_id")
    assert len(harrows) == 3
    look_alike = harrows.loc["tw-officer-03"]
    assert (look_alike["birth_month"], look_alike["birth_year"]) == (11, 1990)
    assert (look_alike["nationality"], look_alike["postcode"]) == ("Irish", "ZZ7 2CD")


def test_claim_dates_follow_the_appointment():
    people, claims = ch.officers_to_evidence(ch.load_raw(SAMPLE))
    by_officer = claims.merge(people[["mention_id", "officer_id"]], left_on="subject", right_on="mention_id")
    resigned = by_officer.loc[by_officer["officer_id"] == "tw-officer-03"].iloc[0]
    assert (resigned["valid_from"], resigned["valid_to"]) == ("2016-03-01", "2019-08-31")
    serving = by_officer.loc[by_officer["officer_id"] == "tw-officer-04"].iloc[0]
    assert serving["valid_from"] == "2015-05-01" and pd.isna(serving["valid_to"])


def test_officer_provenance_points_at_the_officer_record():
    raw = ch.load_raw(SAMPLE)
    people, claims = ch.officers_to_evidence(raw)
    look_alike = people.loc[people["officer_id"] == "tw-officer-03"].iloc[0]
    path, position, _ = ev.parse_record_ref(look_alike["record_ref"])
    assert (path, position) == ("tests/raw_sample/officers/TW000003.json", 1)
    assert json.loads(raw[path])["items"][position]["name"] == look_alike["name"]
    assert ev.raw_unchanged(look_alike["record_ref"], raw[path])   # R1
    his_claim = claims.loc[claims["subject"] == look_alike["mention_id"]].iloc[0]
    assert his_claim["record_ref"] == look_alike["record_ref"]   # the claim comes from the same record


def test_companies_and_officers_pass_the_schema_checks():
    raw = ch.load_raw(SAMPLE)
    people, claims = ch.officers_to_evidence(raw)
    mentions = pd.concat([ch.companies_to_mentions(raw), people], ignore_index=True)
    ev.check_rows(mentions, claims)   # raises SchemaError if any row is bad

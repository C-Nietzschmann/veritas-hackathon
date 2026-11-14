"""Tests for src/real_slice.py on the invented raw sample (tests/raw_sample) and the tiny world.

The raw sample (see tests/test_ingest_companies_house.py): TW000002 is a query company formed
2021-04-20. Its director has the officer id of a director of TW000001, which went into
liquidation on 2021-03-15. TW000001's profile says has_insolvency_history.
"""

import json
import math
import warnings

import pandas as pd
import pytest

from src import evaluate
from src import evidence as ev
from src import ingest_companies_house as adapter
from src import real_slice
from tests.tiny_world import tiny_world

SAMPLE = "tests/raw_sample"


def done_file(tmp_path, numbers):
    """A query_companies.csv like the crawl writes, listing these numbers."""
    path = tmp_path / "query_companies.csv"
    path.write_text("year,company_number\n" + "".join(f"2021,{n}\n" for n in numbers), encoding="utf-8")
    return path


# --- The slice --------------------------------------------------------------------------

def test_query_companies_keeps_numbers_as_text_and_each_company_once(tmp_path):
    queries = real_slice.query_companies(done_file(tmp_path, ["01234567", "TW000002", "01234567"]))
    assert list(queries["company_number"]) == ["01234567", "TW000002"]   # the leading 0 stays
    assert list(queries.columns) == ["year", "company_number"]


def test_load_slice_labels_and_splits_the_query_companies(tmp_path):
    mentions, claims, labels, left_out = real_slice.load_slice(SAMPLE, done_file(tmp_path, ["TW000002"]))
    assert list(labels.columns) == ev.LABEL_COLS
    row = labels.set_index("company_id").loc["TW000002"]
    assert row["formed_on"] == "2021-04-20"
    assert not row["failed"]          # active, never insolvent
    assert row["split"] == "train"    # formed Jan-Sep 2021
    assert left_out == {}
    # the evidence covers every raw file, not only the query companies
    assert set(mentions.loc[mentions["kind"] == "company", "company_number"]) == {
        "TW000001", "TW000002", "TW000003", "TW000004"}


def test_a_number_without_a_profile_is_left_out():
    raw = adapter.load_raw(SAMPLE)
    _, _, labels, left_out = real_slice.slice_from_raw(raw, ["TW000002", "TW999999"])
    assert list(labels["company_id"]) == ["TW000002"]
    assert left_out == {"TW999999": "no profile"}


def test_a_flagged_company_without_its_insolvency_file_is_left_out():
    raw = adapter.load_raw(SAMPLE)
    del raw["tests/raw_sample/insolvency/TW000001.json"]   # its profile says has_insolvency_history
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")    # the adapter warns about it too
        _, _, labels, left_out = real_slice.slice_from_raw(raw, ["TW000001", "TW000002"])
    assert list(labels["company_id"]) == ["TW000002"]
    assert left_out == {"TW000001": "insolvency file missing"}


def test_make_labels_gives_the_tiny_worlds_known_answers():
    mentions, _, truth = tiny_world()
    labels = real_slice.make_labels(mentions, truth["queries"])
    assert dict(zip(labels["company_id"], labels["failed"])) == truth["failed"]
    assert set(labels["split"]) == {"train"}   # all five were formed Jan-Sep 2021


def test_make_labels_uses_the_teams_label_which_counts_dissolution():
    mentions, _, truth = tiny_world()
    northgate = mentions["company_number"] == "TW000003"   # formed 2021-06-01, never insolvent
    mentions.loc[northgate, "dissolved_on"] = "2022-06-01"  # dissolved 12 months later
    labels = real_slice.make_labels(mentions, ["TW000003"])
    assert labels.loc[0, "failed"]


# --- Which split a pair belongs to ----------------------------------------------------------

def tiny_splits():
    """The tiny world with TW000003 moved to validation and TW000005 to test, and its people by friendly key."""
    mentions, claims, truth = tiny_world()
    labels = real_slice.make_labels(mentions, truth["queries"])
    labels.loc[labels["company_id"] == "TW000003", "split"] = "validation"
    labels.loc[labels["company_id"] == "TW000005", "split"] = "test"
    return real_slice.person_split(mentions, claims, labels), truth["mention"]


def test_a_person_gets_the_split_of_the_query_company_they_direct():
    splits, m = tiny_splits()
    assert splits[m["p2"]] == "train"         # director of TW000002
    assert splits[m["p3"]] == "validation"    # director of TW000003
    assert pd.isna(splits[m["p1"]])           # director of TW000001, an earlier company


def test_a_pair_is_held_out_as_soon_as_one_person_is():
    splits, m = tiny_splits()
    pairs = pd.DataFrame({"a": [m["p1"], m["p1"], m["p2"], m["p1"], m["p3"]],
                          "b": [m["p3"], m["p2"], m["p3"], m["p4"], m["p5"]]})
    # p3 directs a validation company, p5 a test one: test is held out first
    assert list(real_slice.pair_split(pairs, splits)) == ["validation", "train", "validation", "train", "test"]


# --- The key table ----------------------------------------------------------------------------

def as_keys(pairs, truth):
    """A pairs table as a set of (friendly key, friendly key), for readable asserts."""
    key = {mention_id: name for name, mention_id in truth["mention"].items()}
    return {tuple(sorted((key[a], key[b]))) for a, b in zip(pairs["a"], pairs["b"])}


def test_link_pairs_sorts_pairs_into_the_three_links():
    mentions, _, truth = tiny_world()
    links = real_slice.link_pairs(mentions)
    assert as_keys(links["same officer id"], truth) == {("p5", "p9"), ("p6", "p7")}
    assert as_keys(links["same name and birth month and year"], truth) == {("p1", "p2")}   # the phoenix
    assert as_keys(links["same name only"], truth) == {("p1", "p3"), ("p2", "p3"), ("p4", "p5"), ("p4", "p9")}


def test_strongest_link_on_the_tiny_world():
    mentions, claims, truth = tiny_world()
    found = real_slice.strongest_link(truth["queries"], mentions, claims, real_slice.link_pairs(mentions))
    assert found.to_dict() == {
        "TW000002": "same name and birth month and year",   # the phoenix, under a new officer id
        "TW000003": "same name only",                       # the look-alike of the phoenix's director
        "TW000005": "same name only",                       # the common name; the 2024 insolvency is the future
        "TW000006": "no director records",
        "TW000007": "no predecessor",                       # her earlier company closed without insolvency
    }


def test_a_company_counts_under_its_strongest_link_only():
    mentions, claims, truth = tiny_world()
    phoenix = real_slice.link_pairs(mentions)["same name and birth month and year"]   # the pair p1-p2
    every_link = {link: phoenix for link in real_slice.LINKS}   # the same pair found by all three links
    found = real_slice.strongest_link(["TW000002"], mentions, claims, every_link)
    assert found["TW000002"] == "same officer id"   # the first link in LINKS wins, the others don't count


def test_the_officer_id_is_the_strongest_link():
    mentions, claims = real_slice.build_evidence(adapter.load_raw(SAMPLE))
    found = real_slice.strongest_link(["TW000002"], mentions, claims, real_slice.link_pairs(mentions))
    assert found["TW000002"] == "same officer id"   # the register's own link: one officer id at both companies


def test_wilson_interval():
    assert real_slice.wilson(5, 10) == pytest.approx((0.2366, 0.7634), abs=1e-4)
    low, high = real_slice.wilson(0, 10)
    assert low == 0 and high == pytest.approx(0.2775, abs=1e-4)   # 0 out of 10 is not "surely 0%"
    assert real_slice.wilson(10, 10) == pytest.approx((0.7225, 1.0), abs=1e-4)
    assert all(math.isnan(end) for end in real_slice.wilson(0, 0))


def test_rate_table_counts_each_company_under_its_link():
    link = pd.Series({"A": "no predecessor", "B": "same officer id", "C": "no predecessor"})
    failed = pd.Series({"A": True, "B": True, "C": False})
    insolvent = pd.Series({"A": False, "B": True, "C": False})
    table = real_slice.rate_table(link, failed, insolvent).set_index("strongest link")
    assert list(table.index) == ["no predecessor"] + real_slice.LINKS   # no "no director records" row when there are none
    assert table.loc["no predecessor", "companies"] == 2
    assert table.loc["no predecessor", "failed (team label)"] == "1 of 2: 50% (9-91%)"
    assert table.loc["no predecessor", "failed through insolvency only"] == "0 of 2: 0% (0-66%)"   # A failed, but not by insolvency
    assert table.loc["same officer id", "failed through insolvency only"] == "1 of 1: 100% (21-100%)"
    assert table.loc["same name only", "failed (team label)"] == "no companies"
    assert real_slice.rate(3, 10) == "3 of 10: 30% (11-60%)"


# --- The second key table: predecessors that failed the way our label defines it -----------

def appointments_from(mentions, claims):
    """The appointment lists the crawl would have saved for the tiny world: one row per directorship."""
    people = mentions.set_index("mention_id")
    numbers = mentions.set_index("mention_id")["company_number"]
    return pd.DataFrame({
        "officer_id": claims["subject"].map(people["officer_id"]).to_numpy(),
        "name": claims["subject"].map(people["name"]).to_numpy(),
        "birth_month": claims["subject"].map(people["birth_month"]).to_numpy(),
        "birth_year": claims["subject"].map(people["birth_year"]).to_numpy(),
        "company_number": claims["object"].map(numbers).to_numpy(),
        "appointed_on": claims["valid_from"].to_numpy(),
    }, columns=real_slice.APPOINTMENT_COLS)


def test_failure_dates_follow_the_teams_label():
    mentions, _, _ = tiny_world()
    failed_on = real_slice.failure_dates(mentions)
    assert (failed_on.notna() == evaluate.label_failures(mentions)).all()   # failed exactly when the label says so
    assert failed_on["TW000002"] == pd.Timestamp("2022-09-01")   # liquidation 16 months after it was formed
    assert pd.isna(failed_on["TW000001"])   # insolvent, but 4 years after it was formed: not a failure by our label
    assert pd.isna(failed_on["TW000008"])   # dissolved after nearly 5 years: not a failure either


def test_the_failure_date_is_the_earlier_event_inside_the_window():
    mentions, _, _ = tiny_world()
    elm = mentions["company_number"] == "TW000005"            # formed 2021-02-10
    mentions.loc[elm, ["insolvency_on", "dissolved_on"]] = ["2022-01-10", "2022-06-01"]
    assert real_slice.failure_dates(mentions)["TW000005"] == pd.Timestamp("2022-01-10")


def test_appointment_rows_keeps_directorships_with_their_start():
    listing = {"name": "Daniel HARROW", "date_of_birth": {"month": 4, "year": 1979}, "items": [
        {"name": "Daniel HARROW", "officer_role": "director", "appointed_on": "2017-02-01",
         "appointed_to": {"company_number": "TW000001", "company_status": "liquidation"}},
        {"name": "Daniel HARROW", "officer_role": "secretary", "appointed_on": "2018-01-01",
         "appointed_to": {"company_number": "TW000005", "company_status": "active"}},
        {"name": "Daniel HARROW", "officer_role": "director", "appointed_before": "1991-10-01",
         "appointed_to": {"company_number": "TW000004", "company_status": "dissolved"}},
    ]}
    raw = {"data/raw/appointments/tw-officer-01.json": json.dumps(listing).encode("utf-8")}
    rows = real_slice.appointment_rows(raw)
    assert list(rows.columns) == real_slice.APPOINTMENT_COLS
    assert list(rows["company_number"]) == ["TW000001", "TW000004"]   # the secretary role is skipped
    assert list(rows["appointed_on"]) == ["2017-02-01", "1991-10-01"]  # appointed_before when there is no appointed_on
    assert set(rows["officer_id"]) == {"tw-officer-01"}                # the file name
    assert list(rows["birth_year"]) == [1979, 1979]


def test_the_appointment_route_with_the_first_tables_rule_gives_the_first_table():
    mentions, claims, truth = tiny_world()
    companies = mentions[mentions["kind"] == "company"].set_index("company_number")
    insolvent_on = evaluate.read_dates(companies["insolvency_on"])   # the first table's rule: insolvent, any age
    first = real_slice.strongest_link(truth["queries"], mentions, claims, real_slice.link_pairs(mentions))
    again = real_slice.strongest_failed_link(truth["queries"], mentions, claims,
                                             appointments_from(mentions, claims), insolvent_on)
    assert again.to_dict() == first.to_dict()


def failed_tiny_world():
    """The tiny world with two earlier companies that failed within 24 months of being formed."""
    mentions, claims, truth = tiny_world()
    harrow_build = mentions["company_number"] == "TW000001"
    mentions.loc[harrow_build, "incorporated_on"] = "2020-01-01"   # liquidation 2021-03-15: 14 months later
    lambert = mentions["company_number"] == "TW000008"
    mentions.loc[lambert, "dissolved_on"] = "2017-06-01"           # dissolved 15 months after 2016-03-01
    return mentions, claims, truth


def test_strongest_failed_link_counts_only_failures_under_our_label_before_the_formation():
    mentions, claims, truth = failed_tiny_world()
    found = real_slice.strongest_failed_link(truth["queries"], mentions, claims, appointments_from(mentions, claims),
                                             real_slice.failure_dates(mentions))
    assert found.to_dict() == {
        "TW000002": "same name and birth month and year",   # Harrow Build failed 2021-03-15, before 2021-04-20
        "TW000003": "same name only",                       # the look-alike, other birth date
        "TW000005": "no predecessor",   # Smith and Sons went insolvent 5 years after it was formed: not a failure by our label
        "TW000006": "no director records",
        "TW000007": "same officer id",  # her own earlier company was dissolved within 24 months
    }


def test_a_failure_after_the_formation_does_not_count():
    mentions, claims, truth = failed_tiny_world()
    failed_on = real_slice.failure_dates(mentions)
    failed_on["TW000008"] = pd.Timestamp("2021-05-16")   # the day after TW000007 was formed
    found = real_slice.strongest_failed_link(["TW000007"], mentions, claims, appointments_from(mentions, claims), failed_on)
    assert found["TW000007"] == "no predecessor"
    failed_on["TW000008"] = pd.Timestamp("2021-05-15")   # the formation day itself counts, as in the first table
    found = real_slice.strongest_failed_link(["TW000007"], mentions, claims, appointments_from(mentions, claims), failed_on)
    assert found["TW000007"] == "same officer id"


def test_an_appointment_that_starts_after_the_formation_does_not_count():
    mentions, claims, truth = failed_tiny_world()
    appointments = appointments_from(mentions, claims)
    appointments.loc[appointments["company_number"] == "TW000008", "appointed_on"] = "2021-06-01"   # after 2021-05-15
    found = real_slice.strongest_failed_link(["TW000007"], mentions, claims, appointments, real_slice.failure_dates(mentions))
    assert found["TW000007"] == "no predecessor"


def test_the_officer_id_beats_a_name_link_in_the_second_table_too():
    mentions, claims, truth = failed_tiny_world()
    appointments = appointments_from(mentions, claims)
    extra = pd.DataFrame([["tw-officer-02", "Daniel Harrow", 4, 1979, "TW000008", "2016-03-01"]],
                         columns=real_slice.APPOINTMENT_COLS)   # the phoenix's director also ran Lambert Electrical
    found = real_slice.strongest_failed_link(["TW000002"], mentions, claims, pd.concat([appointments, extra]),
                                             real_slice.failure_dates(mentions))
    assert found["TW000002"] == "same officer id"   # and the name and birth link to Harrow Build doesn't count on top

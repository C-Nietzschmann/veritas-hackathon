"""Tests for src/evaluate.py (card #28): the failure label, the split and the as-of rule.

All companies and people are invented: "TW" company numbers don't exist in the
real register.
"""

import pandas as pd
import pytest

from src import evaluate
from src import evidence as ev


def company(number, formed, insolvent=None, dissolved=None, status="active"):
    """One company mention with only the columns these tests need filled in."""
    row = dict.fromkeys(ev.MENTION_COLS)
    row.update(mention_id=ev.make_id("test", f"company/{number}"), kind="company",
               name=f"Company {number} Ltd", company_number=number, status=status,
               incorporated_on=formed, insolvency_on=insolvent, dissolved_on=dissolved)
    return row


def person(key, name):
    row = dict.fromkeys(ev.MENTION_COLS)
    row.update(mention_id=ev.make_id("test", f"person/{key}"), kind="person", name=name)
    return row


def table(rows):
    return pd.DataFrame(rows, columns=ev.MENTION_COLS)


# --- 28.1 The failure label ------------------------------------------------------

def test_label_counts_only_failures_within_24_months():
    mentions = table([
        company("TW100001", "2021-01-15", insolvent="2021-11-15"),   # month 10: failed
        company("TW100002", "2021-01-15", insolvent="2023-07-15"),   # month 30: too late
        company("TW100003", "2021-01-15"),                           # never insolvent
        company("TW100004", "2021-01-15", insolvent="2023-01-15"),   # exactly 24 months: counts
        company("TW100005", "2021-01-15", insolvent="2023-01-16"),   # one day past 24 months: too late
        person("p1", "Alex Example"),                                # people get no label
    ])
    failed = evaluate.label_failures(mentions)
    assert failed.name == "failed"
    assert failed.to_dict() == {"TW100001": True, "TW100002": False, "TW100003": False,
                                "TW100004": True, "TW100005": False}
    # A 12-month window keeps only the month-10 failure.
    assert evaluate.label_failures(mentions, window_months=12).sum() == 1


def test_a_date_not_written_as_iso_stops_instead_of_being_guessed():
    # 01/10/2021 is 1 October in the UK. Guessed month-first it is 10 January:
    # a validation company would land in train, and a month-25 failure would count.
    with pytest.raises(ValueError):
        evaluate.split(table([company("TW100006", "01/10/2021")]))
    with pytest.raises(ValueError):
        evaluate.label_failures(table([company("TW100007", "2021-02-01", insolvent="01/03/2023")]))
    with pytest.raises(ValueError):
        evaluate.mentions_as_of(table([company("TW100008", "2014-03-01")]), "01/05/2021")
    # A claim that starts on 1 June must not count as "started by 1 May" because it reads as 6 January.
    with pytest.raises(ValueError):
        evaluate.history_as_of(claims_table([claim("june", "p", "c", "01/06/2021")]), "2021-05-01")


# --- 28.2 The time split and the as-of rule ------------------------------------

def claim(key, subject, obj, start, end=None):
    """One director_of claim, with provenance so the observed graph keeps it."""
    ref = ev.record_ref("tests/test_evaluate.py", 0, key.encode("utf-8"))
    return dict(claim_id=ev.make_id("test", key), subject=subject, relation="director_of",
                object=obj, valid_from=start, valid_to=end,
                source="test", record_ref=ref, origin="test", adapter="test")


def claims_table(rows):
    return pd.DataFrame(rows, columns=ev.CLAIM_COLS)


def test_split_puts_every_company_in_at_most_one_set():
    companies = table([
        company("TW200001", "2020-12-31"),   # before the slice: none
        company("TW200002", "2021-01-01"),   # train
        company("TW200003", "2021-09-30"),   # train
        company("TW200004", "2021-10-01"),   # validation
        company("TW200005", "2021-12-31"),   # validation
        company("TW200006", "2022-01-01"),   # test
        company("TW200007", "2022-12-31"),   # test
        company("TW200008", "2023-01-01"),   # after the slice: none
        company("TW200009", None),           # no date: none
    ])
    train, validation, test = evaluate.split(companies)
    train, validation, test = (set(part["company_number"]) for part in (train, validation, test))
    assert train == {"TW200002", "TW200003"}
    assert validation == {"TW200004", "TW200005"}
    assert test == {"TW200006", "TW200007"}
    assert not (train & validation or train & test or validation & test)


def test_history_drops_claims_that_start_after_the_date():
    date = "2021-05-01"
    claims = claims_table([
        claim("before", "p", "c", "2019-03-01"),
        claim("same day", "p", "c", "2021-05-01"),   # appointed the day the company forms: kept
        claim("after", "p", "c", "2021-05-02"),
        claim("undated", "p", "c", None),
    ])
    history = evaluate.history_as_of(claims, date)
    assert set(history["claim_id"]) == {ev.make_id("test", "before"), ev.make_id("test", "same day")}
    assert (pd.to_datetime(history["valid_from"]) <= pd.Timestamp(date)).all()


def test_history_hides_end_dates_after_the_date():
    claims = claims_table([
        claim("ended before", "p", "c", "2015-01-01", "2019-06-30"),
        claim("ends that day", "p", "c", "2015-01-01", "2021-05-01"),   # already known on the date: stays
        claim("ends after", "p", "c", "2015-01-01", "2023-02-01"),
    ])
    history = evaluate.history_as_of(claims, "2021-05-01").set_index("claim_id")
    assert history.loc[ev.make_id("test", "ended before"), "valid_to"] == "2019-06-30"
    assert history.loc[ev.make_id("test", "ends that day"), "valid_to"] == "2021-05-01"
    assert pd.isna(history.loc[ev.make_id("test", "ends after"), "valid_to"])
    assert not (pd.to_datetime(history["valid_to"]) > pd.Timestamp("2021-05-01")).any()


def test_insolvency_from_the_future_does_not_leak():
    # A director joined TW300001 in 2015, and it went into liquidation in 2022.
    # Judged on 2021-05-01, the day the director's new company TW300003 forms, that hadn't happened.
    mentions = table([
        company("TW300001", "2014-03-01", insolvent="2022-03-01", status="liquidation"),
        company("TW300002", "2016-01-01", insolvent="2020-06-01", dissolved="2021-09-01", status="dissolved"),
        company("TW300003", "2021-05-01"),
        person("p1", "Alex Example"),
    ])
    old, older, new, alex = mentions["mention_id"]
    claims = claims_table([
        claim("alex/old", alex, old, "2015-01-01"),
        claim("alex/older", alex, older, "2016-01-01", "2020-06-01"),
        claim("alex/new", alex, new, "2021-05-01"),
    ])
    date = "2021-05-01"
    history = evaluate.history_as_of(claims, date)
    seen = evaluate.mentions_as_of(mentions, date).set_index("mention_id")

    assert old in set(history["object"])                      # the 2015 claim survives ...
    assert pd.isna(seen.loc[old, "insolvency_on"])            # ... but shows no insolvency in 2021
    assert seen.loc[older, "insolvency_on"] == "2020-06-01"   # an insolvency in the past stays
    assert pd.isna(seen.loc[older, "dissolved_on"])           # dissolved after the date: hidden
    assert seen["status"].isna().all()                        # download-day status: always hidden
    assert mentions.loc[0, "insolvency_on"] == "2022-03-01"   # the table passed in is unchanged


def test_insolvency_on_the_date_itself_stays():
    # "After the date" is the future. The date itself has happened, like a claim that starts that day.
    mentions = table([company("TW300004", "2014-03-01", insolvent="2021-05-01", dissolved="2021-05-01")])
    seen = evaluate.mentions_as_of(mentions, "2021-05-01")
    assert seen.loc[0, "insolvency_on"] == "2021-05-01"
    assert seen.loc[0, "dissolved_on"] == "2021-05-01"


def test_as_of_without_a_date_stops_instead_of_showing_the_future():
    # A company with no formation date has nothing to cut at, so nothing would be hidden.
    mentions = table([company("TW300005", "2014-03-01", insolvent="2022-03-01")])
    claims = claims_table([claim("later", "p", "c", "2024-01-01")])
    for no_date in (None, float("nan"), ""):   # the ways an empty cell can arrive
        with pytest.raises(ValueError):
            evaluate.history_as_of(claims, no_date)
        with pytest.raises(ValueError):
            evaluate.mentions_as_of(mentions, no_date)

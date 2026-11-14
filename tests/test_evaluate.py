"""Tests for src/evaluate.py (card #28): the failure label, the split and the as-of rule.

All companies and people are invented: "TW" company numbers don't exist in the
real register.
"""

import pandas as pd

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
        person("p1", "Alex Example"),                                # people get no label
    ])
    failed = evaluate.label_failures(mentions)
    assert failed.name == "failed"
    assert failed.to_dict() == {"TW100001": True, "TW100002": False, "TW100003": False, "TW100004": True}

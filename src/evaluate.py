"""The evaluation box: the failure label, the time split and the as-of rule (card #28),
and one scoring function for every method (card #80).

Like every box, it imports nothing from src/ except evidence.py (ADR-005).
Dates are read with read_dates, which stops with an error on a date that is not
written as YYYY-MM-DD, so a bad date can't quietly change a label or a set.
"""

import pandas as pd
from sklearn.metrics import average_precision_score

from src import evidence as ev


def read_dates(dates):
    """Read dates written as YYYY-MM-DD: a whole column, or one date.

    An empty cell becomes NaT ("not a time"). Any other way of writing a date
    stops with an error. Without the fixed format pandas guesses: it reads
    01/10/2021 (1 October in the UK) as 10 January and says nothing.
    """
    return pd.to_datetime(dates, format="%Y-%m-%d")


def as_of_date(date):
    """Read the one date an as-of function is given, and stop if it is empty.

    With no date, nothing counts as "after it", so the whole future would stay in.
    """
    date = read_dates(date)
    if pd.isna(date):
        raise ValueError("the as-of rule needs a date like 2021-05-01, and got an empty one")
    return date


# --- 28.1 The failure label ------------------------------------------------------

def label_failures(mentions, window_months=24):
    """Did each company fail within `window_months` months of incorporation?

    Failed means insolvency_on is on or before incorporated_on + window_months.
    The adapter (#74) fills insolvency_on with the earliest start date of a
    liquidation or administration case, leaving out members' voluntary
    liquidation (a solvent wind-down), so the label only reads that column.
    No insolvency date, or a later one, means not failed.

    Give it the mentions as downloaded, never the output of mentions_as_of: the
    label looks into the future on purpose, and the as-of view hides that future,
    so every company would come out "not failed" without any error.

    Returns a True/False Series named "failed", one row per company, indexed by
    company_number. People in mentions are skipped.
    """
    companies = mentions.loc[mentions["kind"] == "company"]
    formed = read_dates(companies["incorporated_on"])
    insolvent = read_dates(companies["insolvency_on"])
    deadline = formed + pd.DateOffset(months=window_months)
    # An empty insolvency date is NaT ("not a time"), and NaT <= anything is False.
    failed = insolvent <= deadline
    return pd.Series(failed.to_numpy(), index=companies["company_number"], name="failed")


# --- 28.2 The time split and the as-of rule ------------------------------------

def split(companies):
    """Split companies by formation date: train on earlier, test on later.

    Train: formed Jan-Sep 2021. Validation: Oct-Dec 2021. Test: formed in 2022.
    A company formed outside those dates, or with no date, is in none of the
    three. The split is by date only, so no random seed changes it.

    Returns three tables (train, validation, test) with the same columns as
    `companies`, which only needs an incorporated_on column.
    """
    formed = read_dates(companies["incorporated_on"])
    # between() includes both ends, and an empty date (NaT) is never between.
    train = companies.loc[formed.between("2021-01-01", "2021-09-30")]
    validation = companies.loc[formed.between("2021-10-01", "2021-12-31")]
    test = companies.loc[formed.between("2022-01-01", "2022-12-31")]
    return train, validation, test


def history_as_of(claims, date):
    """Directors' history as it stood on `date`, the query company's formation date.

    Keeps claims that started on or before `date`, as ADR-001 says. "On" counts
    on purpose: directors are normally appointed on the day the company forms.
    A claim with no start date is dropped: we can't show it existed by then.
    An end date after `date` is emptied: on that date the appointment was still
    running, and when it would end was still the future.
    Stops with an error if `date` is empty, or if a claim's date is not written
    as YYYY-MM-DD.

    Returns the observed graph's edges: evidence.observed_graph does the filtering.
    The companies' own dates follow the same rule in evidence.mentions_as_of.
    """
    date = as_of_date(date)
    # observed_graph drops a claim whose start date it can't read, and leaves an end date
    # it can't read as it is, even one in the future. Reading both here first stops instead.
    read_dates(claims["valid_from"])
    read_dates(claims["valid_to"])
    return ev.observed_graph(claims, as_of=date)


# --- 27.4 Score any method the same way ----------------------------------------------

def score(decisions, labels):
    """How one method's decisions compare with what really happened (card #80).

    `decisions` is the decisions table of one method; `labels` is the labels table
    (company_id, failed, ...). Only companies in both count. Our method and every
    baseline go through this one function, so they're scored the same way (ADR-005).
    - FLAG on a company that failed is a right flag; FLAG on one that didn't is a false flag.
    - A company that failed and wasn't flagged is a miss, whether it was cleared or left
      to check by hand.

    Returns a dict:
    - companies, failed: how many companies were scored, and how many of them failed
    - flags, false_flags, misses: counts
    - precision: right flags / flags. None when nothing was flagged: 0 out of 0 is no number
    - recall: right flags / failed companies. None when none failed
    - not_enough_evidence: the share of companies left to check by hand
    - pr_auc: the average precision of p_fail over the companies that have one. None when
      the method gives no probabilities, or they don't cover both a failure and a non-failure
    """
    ev.check_columns(decisions, "decisions")
    ev.check_columns(labels, "labels")
    methods = list(decisions["method"].unique())
    if len(methods) != 1:
        raise ValueError(f"score() scores one method at a time, got {methods}: use score_methods()")

    both = decisions.merge(labels[["company_id", "failed"]], left_on="query", right_on="company_id")
    failed = both["failed"].astype(bool)
    flagged = both["decision"] == "FLAG"
    right_flags = int((flagged & failed).sum())

    has_p = both["p_fail"].notna()
    pr_auc = None
    if has_p.any() and failed[has_p].nunique() == 2:
        pr_auc = float(average_precision_score(failed[has_p], both.loc[has_p, "p_fail"].astype(float)))

    return dict(
        method=methods[0],
        companies=len(both),
        failed=int(failed.sum()),
        flags=int(flagged.sum()),
        false_flags=int((flagged & ~failed).sum()),
        misses=int((failed & ~flagged).sum()),
        precision=right_flags / int(flagged.sum()) if flagged.any() else None,
        recall=right_flags / int(failed.sum()) if failed.any() else None,
        not_enough_evidence=float((both["decision"] == "NOT ENOUGH EVIDENCE").mean()) if len(both) else None,
        pr_auc=pr_auc,
    )


def score_methods(decisions, labels):
    """score() for every method in a decisions table, one row each: our method next to the baselines."""
    rows = [score(decisions[decisions["method"] == method], labels) for method in decisions["method"].unique()]
    return pd.DataFrame(rows)

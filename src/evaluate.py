"""The evaluation box (card #28): the failure label, the time split and the as-of rule.

Like every box, it imports nothing from src/ except evidence.py (ADR-005).
Dates are read with pd.to_datetime, which stops with an error on a date it
can't read, so a bad date can't quietly change a label or a set.
"""

import pandas as pd


# --- 28.1 The failure label ------------------------------------------------------

def label_failures(mentions, window_months=24):
    """Did each company fail within `window_months` months of incorporation?

    Failed means insolvency_on is on or before incorporated_on + window_months.
    The adapter (#74) fills insolvency_on with the earliest start date of a
    liquidation or administration case, leaving out members' voluntary
    liquidation (a solvent wind-down), so the label only reads that column.
    No insolvency date, or a later one, means not failed.

    Returns a True/False Series named "failed", one row per company, indexed by
    company_number. People in mentions are skipped.
    """
    companies = mentions.loc[mentions["kind"] == "company"]
    formed = pd.to_datetime(companies["incorporated_on"])
    insolvent = pd.to_datetime(companies["insolvency_on"])
    deadline = formed + pd.DateOffset(months=window_months)
    # An empty insolvency date is NaT ("not a time"), and NaT <= anything is False.
    failed = insolvent <= deadline
    return pd.Series(failed.to_numpy(), index=companies["company_number"], name="failed")

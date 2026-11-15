"""Tests for company_bands() and false_flags_by_band() (card #106). Every number is worked out on paper."""
import pandas as pd
import pytest

from src import evaluate
from src import evidence as ev
from tests.test_score import decisions, labels


def mentions_table(companies, people):
    """Mentions from {company number: formed on} and a list of person mention ids."""
    rows = [dict(mention_id=f"c{number}", kind="company", company_number=number, incorporated_on=formed)
            for number, formed in companies.items()]
    rows += [dict(mention_id=person, kind="person", name=person) for person in people]
    return pd.DataFrame(rows, columns=ev.MENTION_COLS)


def claims_table(rows):
    """director_of claims from (person, company number, appointed on) rows."""
    return pd.DataFrame([dict(claim_id=f"k{i}", subject=person, relation="director_of", object=f"c{number}",
                              valid_from=start, valid_to=None, source="test", record_ref=f"r{i}",
                              origin="test", adapter="test")
                         for i, (person, number, start) in enumerate(rows)], columns=ev.CLAIM_COLS)


def test_a_company_takes_the_most_common_band_of_its_directors():
    mentions = mentions_table({"A": "2021-03-01", "B": "2021-03-01", "C": "2021-03-01"},
                              ["rare1", "common1", "medium1", "late1"])
    claims = claims_table([
        ("rare1", "A", "2021-03-01"), ("common1", "A", "2021-03-01"),   # A: rare and common -> common
        ("medium1", "B", "2020-01-01"),                                 # B: medium
        ("late1", "B", "2021-06-01"),                                   # appointed after B formed: ignored
        ("late1", "C", "2021-04-01"),                                   # C's only director came later: no band
    ])
    bands = pd.Series({"rare1": "rare", "common1": "common", "medium1": "medium", "late1": "common"})
    result = evaluate.company_bands(mentions, claims, bands)
    assert result.to_dict() == {"A": "common", "B": "medium"}


def test_hand_made_decisions_give_the_rates_worked_out_on_paper():
    bands = pd.Series({"A": "common", "B": "common", "C": "common", "D": "rare", "E": "rare", "F": "medium"})
    failed = labels({"A": False, "B": False, "C": True, "D": False, "E": True, "F": False})
    table = pd.concat([
        decisions([("A", "FLAG", None), ("B", "CLEAR", None), ("C", "FLAG", None),
                   ("D", "CLEAR", None), ("E", "FLAG", None), ("F", "NOT ENOUGH EVIDENCE", None)], "ours"),
        decisions([("A", "FLAG", None), ("B", "FLAG", None), ("C", "FLAG", None),
                   ("D", "FLAG", None), ("E", "CLEAR", None), ("F", "CLEAR", None)], "same_name"),
    ], ignore_index=True)
    result = evaluate.false_flags_by_band(table, failed, bands).set_index(["method", "band"])

    # common: A and B didn't fail. ours flags A only -> 1 of 2; same_name flags both -> 2 of 2.
    assert result.loc[("ours", "common"), ["companies", "not_failed", "flags", "false_flags"]].tolist() == [3, 2, 2, 1]
    assert result.loc[("ours", "common"), "false_flag_rate"] == pytest.approx(0.5)
    assert result.loc[("same_name", "common"), "false_flag_rate"] == pytest.approx(1.0)
    # rare: only D didn't fail. ours clears it -> 0 of 1; same_name flags it -> 1 of 1.
    assert result.loc[("ours", "rare"), "false_flag_rate"] == 0
    assert result.loc[("same_name", "rare"), "false_flag_rate"] == 1
    # medium: F didn't fail, nobody flags it. NOT ENOUGH EVIDENCE is not a flag.
    assert result.loc[("ours", "medium"), "false_flags"] == 0


def test_a_band_with_no_honest_company_has_no_rate():
    table = decisions([("C", "FLAG", None)], "ours")
    result = evaluate.false_flags_by_band(table, labels({"C": True}), pd.Series({"C": "common"}))
    row = result.set_index("band").loc["common"]
    assert row["not_failed"] == 0 and row["false_flag_rate"] is None
    assert result.set_index("band").loc["rare", "companies"] == 0   # every band is listed, even when empty


def test_companies_without_a_band_or_label_are_left_out():
    table = decisions([("A", "FLAG", None), ("X", "FLAG", None), ("Y", "FLAG", None)], "ours")
    result = evaluate.false_flags_by_band(table, labels({"A": False, "X": False}), pd.Series({"A": "rare", "Y": "rare"}))
    assert result["companies"].sum() == 1          # X has no band, Y has no label

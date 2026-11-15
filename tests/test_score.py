"""Tests for score() and score_methods() in src/evaluate.py (card #80).

The hand-made cases can be checked on paper. The last test runs the three baselines
on the tiny world: its numbers are the ones written in Evaluation.
"""

import pandas as pd
import pytest

from src import baseline as bl
from src import evaluate
from src import evidence as ev
from tests.tiny_world import tiny_world


def decisions(rows, method="by hand"):
    """A decisions table from (query, decision, p_fail) rows."""
    return pd.DataFrame([dict(query=query, method=method, decision=decision, p_predecessor=None,
                              p_fail=p_fail, reason="", flip=None) for query, decision, p_fail in rows],
                        columns=ev.DECISION_COLS)


def labels(failed):
    """A labels table from {company: failed}."""
    return pd.DataFrame([dict(company_id=company, formed_on=None, failed=value, split=None)
                         for company, value in failed.items()], columns=ev.LABEL_COLS)


def test_four_hand_made_decisions_give_the_numbers_worked_out_on_paper():
    table = decisions([
        ("A", "FLAG", None),                  # failed: a right flag
        ("B", "FLAG", None),                  # didn't fail: a false flag
        ("C", "CLEAR", None),                 # failed: a miss
        ("D", "NOT ENOUGH EVIDENCE", None),   # didn't fail
    ])
    result = evaluate.score(table, labels({"A": True, "B": False, "C": True, "D": False}))
    assert result["companies"] == 4 and result["failed"] == 2
    assert result["flags"] == 2 and result["false_flags"] == 1 and result["misses"] == 1
    assert result["precision"] == 0.5     # 1 right flag out of 2 flags
    assert result["recall"] == 0.5        # 1 of the 2 failed companies was flagged
    assert result["not_enough_evidence"] == 0.25
    assert result["pr_auc"] is None       # no probabilities given


def test_precision_is_none_when_nothing_is_flagged():
    result = evaluate.score(decisions([("A", "CLEAR", None), ("B", "CLEAR", None)]),
                            labels({"A": True, "B": False}))
    assert result["precision"] is None
    assert result["recall"] == 0.0 and result["misses"] == 1


def test_pr_auc_from_p_fail():
    table = decisions([("A", "FLAG", 0.9), ("B", "FLAG", 0.8), ("C", "CLEAR", 0.2), ("D", "CLEAR", 0.1)])
    result = evaluate.score(table, labels({"A": True, "B": False, "C": True, "D": False}))
    # Ranked by p_fail: A right (precision 1/1), B wrong, C right (precision 2/3), D wrong.
    # Average precision = 1/2 × 1 + 1/2 × 2/3 = 5/6.
    assert result["pr_auc"] == pytest.approx(5 / 6)


def test_only_companies_in_both_tables_count():
    table = decisions([("A", "FLAG", None), ("Z", "FLAG", None)])   # no label for Z
    result = evaluate.score(table, labels({"A": True}))
    assert result["companies"] == 1 and result["false_flags"] == 0


def test_score_takes_one_method_and_score_methods_takes_them_all():
    both = pd.concat([decisions([("A", "FLAG", None)], "one"), decisions([("A", "CLEAR", None)], "two")])
    with pytest.raises(ValueError, match="one method at a time"):
        evaluate.score(both, labels({"A": True}))
    table = evaluate.score_methods(both, labels({"A": True}))
    assert list(table["method"]) == ["one", "two"]
    assert list(table["recall"]) == [1.0, 0.0]


def test_the_baselines_on_the_tiny_world():
    """The numbers written in Evaluation, section "Tiny world check"."""
    mentions, claims, truth = tiny_world()
    failed = evaluate.label_failures(mentions)
    tiny_labels = labels(dict(zip(failed.index, failed)))
    table = evaluate.score_methods(bl.run_all(truth["queries"], mentions, claims), tiny_labels).set_index("method")

    assert set(table["companies"]) == {5} and set(table["failed"]) == {1}   # only TW000002 fails in 24 months
    nothing, name, officer = (table.loc[m] for m in ["flag_nothing", "same_name", "officer_links"])
    # In a table, "no precision" (nothing flagged) shows as a missing value.
    assert (nothing["flags"], nothing["misses"], nothing["recall"]) == (0, 1, 0.0) and pd.isna(nothing["precision"])
    assert (name["flags"], name["false_flags"], name["misses"]) == (3, 2, 0)
    assert name["precision"] == pytest.approx(1 / 3) and name["recall"] == 1.0
    assert (officer["flags"], officer["misses"], officer["recall"]) == (0, 1, 0.0) and pd.isna(officer["precision"])

"""Tests for the static figures (cards #107, #108): they draw what the tables say."""
import pandas as pd

from src import evaluate, interface
from tests.test_score import decisions, labels


def bar_heights(fig):
    return sorted(round(patch.get_height(), 1) for patch in fig.axes[0].patches)


def texts(fig):
    return [text.get_text() for text in fig.axes[0].texts] + [text.get_text() for text in fig.texts]


def test_pr_figure_has_a_curve_for_ours_and_a_point_per_flagging_method():
    failed = labels({"A": True, "B": False, "C": True, "D": False})
    table = pd.concat([
        decisions([("A", "FLAG", 0.9), ("B", "FLAG", 0.8), ("C", "CLEAR", 0.2), ("D", "CLEAR", 0.1)], "formula"),
        decisions([("A", "FLAG", None), ("B", "CLEAR", None), ("C", "CLEAR", None), ("D", "CLEAR", None)], "same_name"),
        decisions([(q, "CLEAR", None) for q in "ABCD"], "flag_nothing"),
    ], ignore_index=True)
    fig = interface.pr_figure(table, failed, evaluate.score_methods(table, failed))
    ax = fig.axes[0]
    curves = [line for line in ax.lines if line.get_label().startswith("formula")]
    assert len(curves) == 1                                   # only ours gives p_fail
    points = {tuple(offsets) for c in ax.collections for offsets in c.get_offsets().tolist()}
    assert (0.5, 0.5) in points                               # formula: 1 right of 2 flags, 1 of 2 failures
    assert (0.5, 1.0) in points                               # same_name: 1 right of 1 flag
    assert any("flag_nothing" in t for t in texts(fig))       # no precision, so named in the caption
    assert "random: 50%" in texts(fig)                        # 2 of 4 failed


def test_false_flag_figure_draws_each_rate_with_its_count():
    table = pd.DataFrame([
        dict(method="same_name", band="rare", companies=3, not_failed=2, flags=0, false_flags=0, false_flag_rate=0.0),
        dict(method="same_name", band="common", companies=4, not_failed=4, flags=1, false_flags=1, false_flag_rate=0.25),
        dict(method="formula", band="rare", companies=3, not_failed=2, flags=0, false_flags=0, false_flag_rate=0.0),
        dict(method="formula", band="common", companies=4, not_failed=0, flags=0, false_flags=0, false_flag_rate=None),
    ])
    fig = interface.false_flag_figure(table)
    assert bar_heights(fig) == [0.0, 0.0, 25.0]               # the band with no rate has no bar
    assert "1/4" in texts(fig) and "no companies that didn't fail" in texts(fig)


def test_reliability_figure_puts_one_dot_per_filled_bin():
    p = [0.1, 0.1, 0.9, 0.9, 0.9, 0.9]
    same = [0, 0, 1, 1, 1, 0]
    fig = interface.reliability_figure(p, same)
    dots = fig.axes[0].collections[0].get_offsets().tolist()
    assert [[round(x, 2), round(y, 2)] for x, y in dots] == [[0.1, 0.0], [0.9, 0.75]]   # 3 of 4 at p 0.9
    assert {"2 pairs", "4 pairs"} <= set(texts(fig))

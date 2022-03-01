import numpy as np
import pandas as pd

from ruleskit import HyperrectangleCondition, RegressionRule, ClassificationRule
from ruleskit import Rule
from ruleskit import RuleSet
import pytest


@pytest.mark.parametrize(
    "rule1, rule2, rs",
    [
        (
            Rule(HyperrectangleCondition([0], bmins=[1], bmaxs=[2])),
            Rule(HyperrectangleCondition([1], bmins=[4], bmaxs=[5])),
            RuleSet(
                [
                    Rule(HyperrectangleCondition([0], bmins=[1], bmaxs=[2])),
                    Rule(HyperrectangleCondition([1], bmins=[4], bmaxs=[5])),
                ]
            ),
        ),
    ],
)
def test_add(rule1, rule2, rs):
    res = RuleSet([rule1])
    res += RuleSet([rule2])
    np.testing.assert_equal(res, rs)


@pytest.mark.parametrize(
    "xs, y, rule_list, coverage, exp_act, exp_covs, exp_preds, exp_crits",
    [
        (
            np.array([[5, 3], [3, 4], [2, np.nan], [2, 4]]),
            np.array([1, 3, 2, 1]),
            [
                RegressionRule(HyperrectangleCondition([0], bmins=[1], bmaxs=[2])),
                RegressionRule(HyperrectangleCondition([1], bmins=[4], bmaxs=[5])),
            ],
            0.75,
            np.array([0, 1, 1, 1]),
            pd.Series([0.5, 0.5], index=["X_0 in [1, 2]", "X_1 in [4, 5]"]),
            pd.Series([1.5, 2], index=["X_0 in [1, 2]", "X_1 in [4, 5]"]),
            pd.Series([0.25, 1], index=["X_0 in [1, 2]", "X_1 in [4, 5]"]),
        ),
        (
            np.array([[5, 4], [3, 3], [2, np.nan], [2, 4]]),
            np.array([1, 3, 2, 1]),
            [
                ClassificationRule(HyperrectangleCondition([0], bmins=[1], bmaxs=[2])),
                ClassificationRule(HyperrectangleCondition([1], bmins=[4], bmaxs=[5])),
            ],
            0.75,
            np.array([1, 0, 1, 1]),
            pd.Series([0.5, 0.5], index=["X_0 in [1, 2]", "X_1 in [4, 5]"]),
            pd.Series([1, 1], index=["X_0 in [1, 2]", "X_1 in [4, 5]"]),
            pd.Series([0.5, 1], index=["X_0 in [1, 2]", "X_1 in [4, 5]"]),
        ),
    ],
)
def test_fit(clean, xs, y, rule_list, coverage, exp_act, exp_covs, exp_preds, exp_crits):
    res = RuleSet(rule_list, remember_activation=True, stack_activation=False)
    res.fit(y, xs)
    np.testing.assert_equal(res.ruleset_coverage, coverage)
    np.testing.assert_equal(res.activation, exp_act)
    for r in res:
        assert r.coverage == exp_covs[str(r.condition)]
        assert r.prediction == exp_preds[str(r.condition)]
        assert r.criterion == exp_crits[str(r.condition)]


@pytest.mark.parametrize(
    "xs, y, rule_list, weights, exp_coverage, exp_act, exp_stacked_act, exp_covs, exp_preds, exp_crits, exp_pred",
    [
        (
            np.array([[5, 3], [3, 4], [2, np.nan], [2, 4]]),
            np.array([1, 3, 2, 1]),
            [
                RegressionRule(HyperrectangleCondition([0], bmins=[1], bmaxs=[2])),
                RegressionRule(HyperrectangleCondition([1], bmins=[4], bmaxs=[5])),
            ],
            None,
            0.75,
            np.array([0, 1, 1, 1]),
            pd.DataFrame([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=np.uint8, columns=["X_0 in [1, 2]", "X_1 in [4, 5]"]),
            pd.Series([0.5, 0.5], index=["X_0 in [1, 2]", "X_1 in [4, 5]"]),
            pd.Series([1.5, 2], index=["X_0 in [1, 2]", "X_1 in [4, 5]"]),
            pd.Series([0.25, 1], index=["X_0 in [1, 2]", "X_1 in [4, 5]"]),
            pd.Series([np.nan, 2, 1.5, 1.75]),
        ),
        (
            np.array([[5, 3], [3, 4], [2, np.nan], [2, 4]]),
            np.array([1, 3, 2, 1]),
            [
                RegressionRule(HyperrectangleCondition([0], bmins=[1], bmaxs=[2])),
                RegressionRule(HyperrectangleCondition([1], bmins=[4], bmaxs=[5])),
            ],
            pd.Series([1, 0],  index=["X_0 in [1, 2]", "X_1 in [4, 5]"]),
            0.75,
            np.array([0, 1, 1, 1]),
            pd.DataFrame([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=np.uint8, columns=["X_0 in [1, 2]", "X_1 in [4, 5]"]),
            pd.Series([0.5, 0.5], index=["X_0 in [1, 2]", "X_1 in [4, 5]"]),
            pd.Series([1.5, 2], index=["X_0 in [1, 2]", "X_1 in [4, 5]"]),
            pd.Series([0.25, 1], index=["X_0 in [1, 2]", "X_1 in [4, 5]"]),
            pd.Series([np.nan, np.nan, 1.5, 1.5]),
        ),
        (
            np.array([[5, 3], [3, 4], [2, np.nan], [2, 4]]),
            np.array([1, 3, 2, 1]),
            [
                RegressionRule(HyperrectangleCondition([0], bmins=[1], bmaxs=[2])),
                RegressionRule(HyperrectangleCondition([1], bmins=[4], bmaxs=[5])),
            ],
            pd.Series([1],  index=["X_0 in [1, 2]"]),
            0.75,
            np.array([0, 1, 1, 1]),
            pd.DataFrame([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=np.uint8, columns=["X_0 in [1, 2]", "X_1 in [4, 5]"]),
            pd.Series([0.5, 0.5], index=["X_0 in [1, 2]", "X_1 in [4, 5]"]),
            pd.Series([1.5, 2], index=["X_0 in [1, 2]", "X_1 in [4, 5]"]),
            pd.Series([0.25, 1], index=["X_0 in [1, 2]", "X_1 in [4, 5]"]),
            pd.Series([np.nan, np.nan, 1.5, 1.5]),
        ),
        (
            np.array([[5, 3], [3, 4], [2, np.nan], [2, 4]]),
            np.array([1, 3, 2, 1]),
            [
                RegressionRule(HyperrectangleCondition([0], bmins=[1], bmaxs=[2])),
                RegressionRule(HyperrectangleCondition([1], bmins=[4], bmaxs=[5])),
            ],
            pd.Series([0.75, 1],  index=["X_0 in [1, 2]", "X_1 in [4, 5]"]),
            0.75,
            np.array([0, 1, 1, 1]),
            pd.DataFrame([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=np.uint8, columns=["X_0 in [1, 2]", "X_1 in [4, 5]"]),
            pd.Series([0.5, 0.5], index=["X_0 in [1, 2]", "X_1 in [4, 5]"]),
            pd.Series([1.5, 2], index=["X_0 in [1, 2]", "X_1 in [4, 5]"]),
            pd.Series([0.25, 1], index=["X_0 in [1, 2]", "X_1 in [4, 5]"]),
            pd.Series([np.nan, 2, 1.5, 1.785714286]),
        ),
        (
            np.array([[5, 3], [3, 4], [2, np.nan], [2, 4]]),
            np.array([1, 3, 2, 1]),
            [
                RegressionRule(HyperrectangleCondition([0], bmins=[1], bmaxs=[2])),
                RegressionRule(HyperrectangleCondition([1], bmins=[4], bmaxs=[5])),
            ],
            "criterion",
            0.75,
            np.array([0, 1, 1, 1]),
            pd.DataFrame([[0, 0], [0, 1], [1, 0], [1, 1]], dtype=np.uint8, columns=["X_0 in [1, 2]", "X_1 in [4, 5]"]),
            pd.Series([0.5, 0.5], index=["X_0 in [1, 2]", "X_1 in [4, 5]"]),
            pd.Series([1.5, 2], index=["X_0 in [1, 2]", "X_1 in [4, 5]"]),
            pd.Series([0.25, 1], index=["X_0 in [1, 2]", "X_1 in [4, 5]"]),
            pd.Series([np.nan, 2, 1.5, 1.9]),
        ),
        (
            np.array([[5, 3], [5, 4], [2, np.nan], [2, 4], [2, 6]]),
            np.array([1, 3, 2, 2, 3]),
            [
                ClassificationRule(HyperrectangleCondition([0], bmins=[1], bmaxs=[2])),
                ClassificationRule(HyperrectangleCondition([1], bmins=[4], bmaxs=[6])),
                ClassificationRule(HyperrectangleCondition([0, 1], bmins=[2, 4], bmaxs=[3, 5])),
            ],
            None,
            0.8,
            np.array([0, 1, 1, 1, 1]),
            pd.DataFrame(
                [[0, 0, 0], [0, 1, 0], [1, 0, 0], [1, 1, 1], [1, 1, 0]],
                dtype=np.uint8,
                columns=["X_0 in [1, 2]", "X_1 in [4, 6]", "X_0 in [2, 3] AND X_1 in [4, 5]"],
            ),
            pd.Series([0.6, 0.6, 0.2], index=["X_0 in [1, 2]", "X_1 in [4, 6]", "X_0 in [2, 3] AND X_1 in [4, 5]"]),
            pd.Series([2, 3, 2], index=["X_0 in [1, 2]", "X_1 in [4, 6]", "X_0 in [2, 3] AND X_1 in [4, 5]"]),
            pd.Series([2 / 3, 2 / 3, 1], index=["X_0 in [1, 2]", "X_1 in [4, 6]", "X_0 in [2, 3] AND X_1 in [4, 5]"]),
            pd.Series([np.nan, 3, 2, 2, np.nan]),
        ),
        (
            np.array([[5, 3], [5, 4], [2, np.nan], [2, 4], [2, 6]]),
            np.array([1, 3, 2, 2, 3]),
            [
                ClassificationRule(HyperrectangleCondition([0], bmins=[1], bmaxs=[2])),
                ClassificationRule(HyperrectangleCondition([1], bmins=[4], bmaxs=[6])),
                ClassificationRule(HyperrectangleCondition([0, 1], bmins=[2, 4], bmaxs=[3, 5])),
            ],
            pd.Series([1, 0, 1],  index=["X_0 in [1, 2]", "X_1 in [4, 6]", "X_0 in [2, 3] AND X_1 in [4, 5]"]),
            0.8,
            np.array([0, 1, 1, 1, 1]),
            pd.DataFrame(
                [[0, 0, 0],
                 [0, 1, 0],
                 [1, 0, 0],
                 [1, 1, 1],
                 [1, 1, 0]],
                dtype=np.uint8,
                columns=["X_0 in [1, 2]", "X_1 in [4, 6]", "X_0 in [2, 3] AND X_1 in [4, 5]"],
            ),
            pd.Series([0.6, 0.6, 0.2], index=["X_0 in [1, 2]", "X_1 in [4, 6]", "X_0 in [2, 3] AND X_1 in [4, 5]"]),
            pd.Series([2, 3, 2], index=["X_0 in [1, 2]", "X_1 in [4, 6]", "X_0 in [2, 3] AND X_1 in [4, 5]"]),
            pd.Series([2 / 3, 2 / 3, 1], index=["X_0 in [1, 2]", "X_1 in [4, 6]", "X_0 in [2, 3] AND X_1 in [4, 5]"]),
            pd.Series([np.nan, np.nan, 2, 2, 2]),
        ),
        (
            np.array([[5, 3], [5, 4], [2, np.nan], [2, 4], [2, 6]]),
            np.array([1, 3, 2, 2, 3]),
            [
                ClassificationRule(HyperrectangleCondition([0], bmins=[1], bmaxs=[2])),
                ClassificationRule(HyperrectangleCondition([1], bmins=[4], bmaxs=[6])),
                ClassificationRule(HyperrectangleCondition([0, 1], bmins=[2, 4], bmaxs=[3, 5])),
            ],
            pd.Series([0.5, 1],  index=["X_1 in [4, 6]", "X_0 in [2, 3] AND X_1 in [4, 5]"]),
            0.8,
            np.array([0, 1, 1, 1, 1]),
            pd.DataFrame(
                [[0, 0, 0],
                 [0, 1, 0],
                 [1, 0, 0],
                 [1, 1, 1],
                 [1, 1, 0]],
                dtype=np.uint8,
                columns=["X_0 in [1, 2]", "X_1 in [4, 6]", "X_0 in [2, 3] AND X_1 in [4, 5]"],
            ),
            pd.Series([0.6, 0.6, 0.2], index=["X_0 in [1, 2]", "X_1 in [4, 6]", "X_0 in [2, 3] AND X_1 in [4, 5]"]),
            pd.Series([2, 3, 2], index=["X_0 in [1, 2]", "X_1 in [4, 6]", "X_0 in [2, 3] AND X_1 in [4, 5]"]),
            pd.Series([2 / 3, 2 / 3, 1], index=["X_0 in [1, 2]", "X_1 in [4, 6]", "X_0 in [2, 3] AND X_1 in [4, 5]"]),
            pd.Series([np.nan, 3, np.nan, 2, 3]),
        ),
        (
            np.array([[5, 3], [5, 4], [2, np.nan], [2, 4], [2, 6]]),
            np.array([1, 3, 2, 2, 3]),
            [
                ClassificationRule(HyperrectangleCondition([0], bmins=[1], bmaxs=[2])),
                ClassificationRule(HyperrectangleCondition([1], bmins=[4], bmaxs=[6])),
                ClassificationRule(HyperrectangleCondition([0, 1], bmins=[2, 4], bmaxs=[3, 5])),
            ],
            "criterion",
            0.8,
            np.array([0, 1, 1, 1, 1]),
            pd.DataFrame(
                [[0, 0, 0],
                 [0, 1, 0],
                 [1, 0, 0],
                 [1, 1, 1],
                 [1, 1, 0]],
                dtype=np.uint8,
                columns=["X_0 in [1, 2]", "X_1 in [4, 6]", "X_0 in [2, 3] AND X_1 in [4, 5]"],
            ),
            pd.Series([0.6, 0.6, 0.2], index=["X_0 in [1, 2]", "X_1 in [4, 6]", "X_0 in [2, 3] AND X_1 in [4, 5]"]),
            pd.Series([2, 3, 2], index=["X_0 in [1, 2]", "X_1 in [4, 6]", "X_0 in [2, 3] AND X_1 in [4, 5]"]),
            pd.Series([2 / 3, 2 / 3, 1], index=["X_0 in [1, 2]", "X_1 in [4, 6]", "X_0 in [2, 3] AND X_1 in [4, 5]"]),
            pd.Series([np.nan, 3, 2, 2, np.nan]),
        ),
    ],
)
def test_stacked_fit(
    clean_for_stacked_fit,
    xs,
    y,
    rule_list,
    weights,
    exp_coverage,
    exp_act,
    exp_stacked_act,
    exp_covs,
    exp_preds,
    exp_crits,
    exp_pred,
):
    res = RuleSet(rule_list, remember_activation=True, stack_activation=True)
    res.fit(y, xs)
    assert res.ruleset_coverage == exp_coverage
    np.testing.assert_equal(res.activation, exp_act)
    pd.testing.assert_frame_equal(res.stacked_activations, exp_stacked_act)
    for r in res:
        assert r.coverage == exp_covs[str(r.condition)]
        assert r.prediction == exp_preds[str(r.condition)]
        assert r.criterion == exp_crits[str(r.condition)]
    pd.testing.assert_series_equal(res.calc_prediction(y, weights), exp_pred)


@pytest.mark.parametrize(
    "rs",
    [
        RuleSet(
            [
                Rule(HyperrectangleCondition([0], bmins=[1], bmaxs=[2])),
                Rule(HyperrectangleCondition([1], bmins=[4], bmaxs=[5])),
            ]
        ),
    ],
)
def test_save(rs):
    rs.save("tests/unit/data/ruleset.csv")


@pytest.mark.parametrize(
    "rs",
    [
        RuleSet(
            [
                Rule(HyperrectangleCondition([0, 1], bmins=[1, 1], bmaxs=[2, 3])),
                Rule(HyperrectangleCondition([1, 2], bmins=[4, 4], bmaxs=[5, 4])),
            ]
        ),
    ],
)
def test_save(rs):
    rs.save("tests/unit/data/ruleset.csv")


def test_load():
    rs = RuleSet()
    rs.load("tests/unit/data/ruleset_test.csv")
    for rule in rs:
        print(rule)

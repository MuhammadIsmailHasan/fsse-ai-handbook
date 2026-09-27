"""Checks for evaluate_alarms.py. Don't edit this file."""

from evaluate_alarms import evaluate_alarms


def test_only_the_crossed_threshold_fires():
    readings = {"error_rate": 0.08, "cpu": 55}
    rules = [
        {"name": "high-errors", "metric": "error_rate", "op": ">", "threshold": 0.02},
        {"name": "high-cpu", "metric": "cpu", "op": ">", "threshold": 80},
    ]
    assert evaluate_alarms(readings, rules) == ["high-errors"]


def test_missing_metric_is_skipped():
    readings = {"cpu": 90}
    rules = [
        {"name": "no-data", "metric": "error_rate", "op": ">", "threshold": 0.02},
        {"name": "high-cpu", "metric": "cpu", "op": ">=", "threshold": 90},
    ]
    assert evaluate_alarms(readings, rules) == ["high-cpu"]


def test_all_operators():
    readings = {"a": 10}
    rules = [
        {"name": "gt", "metric": "a", "op": ">", "threshold": 5},
        {"name": "lt", "metric": "a", "op": "<", "threshold": 5},
        {"name": "ge", "metric": "a", "op": ">=", "threshold": 10},
        {"name": "le", "metric": "a", "op": "<=", "threshold": 10},
    ]
    assert evaluate_alarms(readings, rules) == ["ge", "gt", "le"]


def test_nothing_fires():
    readings = {"error_rate": 0.0}
    rules = [{"name": "high-errors", "metric": "error_rate", "op": ">", "threshold": 0.02}]
    assert evaluate_alarms(readings, rules) == []


def test_result_is_sorted():
    readings = {"a": 1, "b": 1}
    rules = [
        {"name": "zebra", "metric": "a", "op": ">", "threshold": 0},
        {"name": "alpha", "metric": "b", "op": ">", "threshold": 0},
    ]
    assert evaluate_alarms(readings, rules) == ["alpha", "zebra"]

"""Reference solution. See README.md."""

import operator

_OPS = {
    ">": operator.gt,
    "<": operator.lt,
    ">=": operator.ge,
    "<=": operator.le,
}


def evaluate_alarms(readings: dict, rules: list[dict]) -> list[str]:
    firing: list[str] = []
    for rule in rules:
        metric = rule["metric"]
        if metric not in readings:
            continue  # can't evaluate a metric we don't have
        compare = _OPS[rule["op"]]
        if compare(readings[metric], rule["threshold"]):
            firing.append(rule["name"])
    return sorted(firing)

"""Decide which alarms fire from metric readings. See README.md."""


def evaluate_alarms(readings: dict, rules: list[dict]) -> list[str]:
    raise NotImplementedError

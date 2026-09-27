"""Canary rollout control logic. See README.md."""


def canary_decision(error_rate: float, threshold: float, percent: int) -> str:
    raise NotImplementedError

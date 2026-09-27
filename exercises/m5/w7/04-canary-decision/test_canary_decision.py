"""Checks for canary_decision.py. Don't edit this file."""

from canary_decision import canary_decision


def test_healthy_small_canary_promotes():
    assert canary_decision(0.01, 0.05, 5) == "promote"


def test_unhealthy_rolls_back():
    assert canary_decision(0.09, 0.05, 5) == "rollback"


def test_healthy_at_full_is_done():
    assert canary_decision(0.01, 0.05, 100) == "done"


def test_unhealthy_at_full_still_rolls_back():
    assert canary_decision(0.2, 0.05, 100) == "rollback"


def test_exactly_at_threshold_is_still_healthy():
    # error_rate must be strictly greater than threshold to roll back.
    assert canary_decision(0.05, 0.05, 50) == "promote"


def test_healthy_mid_rollout_promotes():
    assert canary_decision(0.0, 0.05, 50) == "promote"

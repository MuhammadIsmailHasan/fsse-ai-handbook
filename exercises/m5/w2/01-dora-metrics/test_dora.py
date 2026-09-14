"""Checks for dora.py. Don't edit this file."""

from datetime import datetime, timedelta, timezone

import pytest

from dora import Deployment, Incident, change_failure_rate, classify, deployment_frequency, lead_time_hours, recovery_time_hours

T0 = datetime(2026, 9, 1, 9, 0, tzinfo=timezone.utc)


def h(hours: float) -> datetime:
    return T0 + timedelta(hours=hours)


DEPLOYS = [
    Deployment("d1", "production", h(10), [h(0), h(4)], "success"),
    Deployment("d2", "staging", h(20), [h(12)], "success"),
    Deployment("d3", "production", h(30), [h(20), h(26), h(28)], "success"),
    Deployment("d4", "production", h(50), [h(40)], "rolled_back"),
    Deployment("d5", "production", h(80), [h(70)], "failed"),
    Deployment("d6", "production", h(24 * 10), [h(24 * 9)], "success"),
]
INCIDENTS = [
    Incident("i1", "d3", h(31), h(33.5)),
    Incident("i2", "d2", h(21), h(22)),
    Incident("i3", "d6", h(241), None),
    Incident("i4", "d4", h(51), h(51.5)),
]


def test_deployment_frequency():
    assert deployment_frequency(DEPLOYS, T0, T0 + timedelta(days=14)) == 1.5
    assert deployment_frequency(DEPLOYS, T0, T0 + timedelta(days=7)) == 2.0
    assert deployment_frequency(DEPLOYS, h(30), h(240)) == 0.8  # d3 counts (start inclusive), d6 does not (end exclusive): 1 per 1.25 weeks
    assert deployment_frequency([], T0, T0 + timedelta(days=7)) == 0.0


def test_lead_time_median_over_commits_of_successful_production_deploys():
    # d1: 10, 6 · d3: 10, 4, 2 · d6: 24 → sorted [2, 4, 6, 10, 10, 24] → median 8.0
    assert lead_time_hours(DEPLOYS) == 8.0
    assert lead_time_hours([DEPLOYS[1], DEPLOYS[3]]) is None


def test_change_failure_rate_counts_outcomes_and_incidents():
    # production: d1 ok, d3 incident, d4 rolled back (+incident, counted once), d5 failed, d6 incident → 4 / 5
    assert change_failure_rate(DEPLOYS, INCIDENTS) == 0.8
    assert change_failure_rate(DEPLOYS, []) == 0.4
    assert change_failure_rate([DEPLOYS[1]], INCIDENTS) is None


def test_recovery_time_median_of_resolved_production_incidents():
    # i1 2.5 h, i4 0.5 h (i2 staging, i3 unresolved) → median 1.5
    assert recovery_time_hours(INCIDENTS, DEPLOYS) == 1.5
    assert recovery_time_hours([INCIDENTS[2]], DEPLOYS) is None


@pytest.mark.parametrize(
    ("metrics", "expected"),
    [
        ((10, 3, 0.02, 0.5), "elite"),
        ((10, 3, 0.02, 1.0), "high"),
        ((2, 30, 0.08, 5), "high"),
        ((0.5, 200, 0.12, 30), "medium"),
        ((20, 2, 0.20, 0.2), "low"),
        ((0.1, 10, 0.01, 0.1), "low"),
        ((7, 23.9, 0.05, 0.99), "elite"),
        ((None, 5, None, None), "elite"),
        ((1, None, 0.15, 167.9), "medium"),
    ],
)
def test_classify(metrics, expected):
    assert classify(*metrics) == expected

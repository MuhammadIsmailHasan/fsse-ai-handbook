"""Checks for cost_review.py. Don't edit this file."""

from cost_review import Resource, idle_resources, monthly_cost


RES = [
    Resource("api", 0.10, True),
    Resource("old-db", 0.20, False),
    Resource("unused-lb", 0.025, False),
]


def test_monthly_cost_sums_all():
    # (0.10 + 0.20 + 0.025) * 730 = 237.25
    assert monthly_cost(RES) == 237.25


def test_monthly_cost_empty():
    assert monthly_cost([]) == 0.0


def test_idle_resources_sorted():
    assert idle_resources(RES) == ["old-db", "unused-lb"]


def test_idle_resources_none_idle():
    res = [Resource("api", 0.1, True)]
    assert idle_resources(res) == []


def test_single_in_use_cost():
    assert monthly_cost([Resource("api", 0.10, True)]) == 73.0

"""Checks for trace_bottleneck.py. Don't edit this file."""

from trace_bottleneck import Span, slowest_step, time_by_service

TRACE = [
    Span("s1", "gateway", 10),
    Span("s2", "orders", 40),
    Span("s3", "catalog", 30),
    Span("s4", "payments", 4200),
    Span("s5", "payments", 30),
]


def test_slowest_step():
    assert slowest_step(TRACE) == "s4"


def test_slowest_step_empty():
    assert slowest_step([]) is None


def test_slowest_step_tie_keeps_first():
    spans = [Span("a", "x", 100), Span("b", "y", 100)]
    assert slowest_step(spans) == "a"


def test_time_by_service_sums_per_service():
    assert time_by_service(TRACE) == {
        "gateway": 10,
        "orders": 40,
        "catalog": 30,
        "payments": 4230,
    }


def test_time_by_service_empty():
    assert time_by_service([]) == {}


def test_single_span():
    spans = [Span("only", "gateway", 5)]
    assert slowest_step(spans) == "only"
    assert time_by_service(spans) == {"gateway": 5}

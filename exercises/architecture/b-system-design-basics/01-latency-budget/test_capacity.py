import pytest

from capacity import average_rps, max_throughput, parallel_latency, peak_rps, percentile, sequential_latency

SAMPLES = [30, 10, 20, 40, 50, 60, 70, 80, 90, 100]


@pytest.mark.parametrize(("p", "expected"), [(50, 50), (90, 90), (95, 100), (99, 100), (10, 10), (100, 100)])
def test_percentile_nearest_rank(p, expected):
    assert percentile(SAMPLES, p) == expected


def test_percentile_needs_samples():
    with pytest.raises(ValueError):
        percentile([], 50)


def test_sequential_and_parallel():
    assert sequential_latency([80, 400, 60]) == 540
    assert parallel_latency([80, 400, 60]) == 400
    assert sequential_latency([]) == 0
    assert parallel_latency([]) == 0


def test_rps_estimates():
    assert average_rps(100_000, 20) == pytest.approx(23.148, rel=1e-3)
    assert peak_rps(100_000, 20, 10) == pytest.approx(231.48, rel=1e-3)


def test_max_throughput():
    assert max_throughput(10, 50) == pytest.approx(200.0)
    assert max_throughput(1, 250) == pytest.approx(4.0)

"""Checks for the load test and the results analyzer. Don't edit this file."""

import csv
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest

from analyze import EndpointStats, load_stats, slo_violations, slowest

HERE = Path(__file__).parent
EXPECTED_NAMES = {"POST /api/v1/login", "GET /api/v1/jobs", "GET /api/v1/jobs/[id]", "POST /api/v1/jobs/[id]/save"}


# ---------- Part 1: analyze.py ----------

def test_load_stats_skips_aggregated_and_unused_rows():
    stats = load_stats(HERE / "sample_stats.csv")
    assert [s.name for s in stats] == [
        "GET /api/v1/jobs",
        "GET /api/v1/jobs/[id]",
        "GET /api/v1/jobs/search",
        "POST /api/v1/jobs/[id]/save",
        "POST /api/v1/login",
    ]
    search = stats[2]
    assert search == EndpointStats("GET", "GET /api/v1/jobs/search", 830, 12, 640.0, 1480.0, 13.8)
    assert stats[0].failure_rate == pytest.approx(0.1)
    assert EndpointStats("GET", "x", 0, 0, 0, 0, 0).failure_rate == 0.0


def test_slo_violations():
    stats = load_stats(HERE / "sample_stats.csv")
    assert slo_violations(stats, max_p95_ms=500, max_failure_rate=0.01) == [
        "GET /api/v1/jobs: failure rate 10.0% > 1.0%",
        "GET /api/v1/jobs/search: p95 1480ms > 500ms",
        "GET /api/v1/jobs/search: failure rate 1.4% > 1.0%",
    ]
    assert slo_violations(stats, max_p95_ms=250, max_failure_rate=0.2) == [
        "GET /api/v1/jobs/search: p95 1480ms > 250ms",
        "POST /api/v1/login: p95 280ms > 250ms",
    ]
    assert slo_violations(stats, max_p95_ms=5000, max_failure_rate=0.5) == []


def test_slowest():
    stats = load_stats(HERE / "sample_stats.csv")
    assert slowest(stats) == ["GET /api/v1/jobs/search", "POST /api/v1/login", "GET /api/v1/jobs"]
    assert slowest(stats, n=1) == ["GET /api/v1/jobs/search"]


# ---------- Part 2: locustfile.py against a real server ----------

def free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def locust_run(tmp_path_factory):
    tmp = tmp_path_factory.mktemp("locust")
    port = free_port()
    server = subprocess.Popen([sys.executable, str(HERE / "target_app.py"), "--port", str(port)], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:
        for _ in range(50):
            try:
                urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1)
                break
            except OSError:
                time.sleep(0.1)
        # Use YOUR JobSeeker, but with almost no think time so a 3-second test produces enough traffic.
        wrapper = tmp / "fast_locustfile.py"
        wrapper.write_text(
            f"import sys\nsys.path.insert(0, {str(HERE)!r})\n"
            "from locust import constant\nfrom locustfile import JobSeeker\nJobSeeker.wait_time = constant(0.01)\n"
        )
        result = subprocess.run(
            [sys.executable, "-m", "locust", "-f", str(wrapper), "--headless", "-u", "5", "-r", "5", "-t", "3s",
             "--host", f"http://127.0.0.1:{port}", "--csv", str(tmp / "run"), "--only-summary", "--exit-code-on-error", "0"],
            capture_output=True, text=True, timeout=60,
        )
        assert result.returncode == 0, result.stderr[-2000:]
        with open(tmp / "run_stats.csv", newline="") as file:
            yield {row["Name"]: row for row in csv.DictReader(file) if row["Name"] != "Aggregated"}
    finally:
        server.terminate()
        server.wait(timeout=10)


def count(rows, name, column="Request Count"):
    return int(rows[name][column]) if name in rows else 0


def test_requests_are_grouped_by_name(locust_run):
    assert set(locust_run) == EXPECTED_NAMES, "Use name= so URLs with ids are grouped into one row each"


def test_logs_in_once_per_user(locust_run):
    assert count(locust_run, "POST /api/v1/login") == 5


def test_degraded_responses_are_failures(locust_run):
    assert count(locust_run, "GET /api/v1/jobs", "Failure Count") > 0, "A 200 with an error body must be marked as failure"
    for name in EXPECTED_NAMES - {"GET /api/v1/jobs"}:
        assert count(locust_run, name, "Failure Count") == 0, f"{name} should not fail (token sent? ids 1..50?)"


def test_task_weights_are_5_3_1(locust_run):
    browse, view, save = (count(locust_run, n) for n in ("GET /api/v1/jobs", "GET /api/v1/jobs/[id]", "POST /api/v1/jobs/[id]/save"))
    assert save > 0
    assert 1.2 < browse / view < 2.3
    assert 1.8 < view / save < 4.5

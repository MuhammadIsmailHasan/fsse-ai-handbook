"""Architecture · B — Latency and capacity calculators."""

SECONDS_PER_DAY = 86_400


def percentile(samples_ms: list[float], p: float) -> float:
    # YOUR CODE HERE
    return -1


def sequential_latency(calls_ms: list[float]) -> float:
    # YOUR CODE HERE
    return -1


def parallel_latency(calls_ms: list[float]) -> float:
    # YOUR CODE HERE
    return -1


def average_rps(daily_users: int, requests_per_user: int) -> float:
    # YOUR CODE HERE
    return -1


def peak_rps(daily_users: int, requests_per_user: int, peak_factor: float) -> float:
    # YOUR CODE HERE
    return -1


def max_throughput(concurrency: int, latency_ms: float) -> float:
    """Requests per second one server can handle."""
    # YOUR CODE HERE
    return -1

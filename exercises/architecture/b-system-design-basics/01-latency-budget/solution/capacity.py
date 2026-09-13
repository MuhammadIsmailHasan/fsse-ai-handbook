"""Reference solution."""

import math

SECONDS_PER_DAY = 86_400


def percentile(samples_ms: list[float], p: float) -> float:
    if not samples_ms:
        raise ValueError("need at least one sample")
    ordered = sorted(samples_ms)
    rank = max(1, math.ceil(p / 100 * len(ordered)))
    return ordered[rank - 1]


def sequential_latency(calls_ms: list[float]) -> float:
    return sum(calls_ms)


def parallel_latency(calls_ms: list[float]) -> float:
    return max(calls_ms, default=0)


def average_rps(daily_users: int, requests_per_user: int) -> float:
    return daily_users * requests_per_user / SECONDS_PER_DAY


def peak_rps(daily_users: int, requests_per_user: int, peak_factor: float) -> float:
    return average_rps(daily_users, requests_per_user) * peak_factor


def max_throughput(concurrency: int, latency_ms: float) -> float:
    return concurrency / (latency_ms / 1000)

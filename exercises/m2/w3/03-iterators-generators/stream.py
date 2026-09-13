"""M2 · W3 · 03 — Streaming log analytics with generators."""

from collections.abc import Iterable, Iterator
from itertools import islice  # noqa: F401


def read_lines(path: str) -> Iterator[str]:
    # YOUR CODE HERE
    return iter([])


def parse_records(lines: Iterable[str], stats: dict) -> Iterator[dict]:
    # YOUR CODE HERE
    return iter([])


def slow(records: Iterable[dict], threshold_ms: int) -> Iterator[dict]:
    # YOUR CODE HERE
    return iter([])


def take(iterable: Iterable, n: int) -> Iterator:
    # YOUR CODE HERE
    return iter([])


def batched_items(iterable: Iterable, size: int) -> Iterator[list]:
    # YOUR CODE HERE
    return iter([])


def total_ms_by_path(records: Iterable[dict]) -> dict[str, int]:
    # YOUR CODE HERE
    return {}

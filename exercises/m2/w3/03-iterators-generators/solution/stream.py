"""Reference solution."""

from collections.abc import Iterable, Iterator
from itertools import islice


def read_lines(path: str) -> Iterator[str]:
    with open(path, encoding="utf-8") as file:
        for line in file:
            yield line.rstrip("\n")


def parse_records(lines: Iterable[str], stats: dict) -> Iterator[dict]:
    stats.setdefault("invalid", 0)
    for line in lines:
        try:
            _timestamp, level, method, path, status, duration = line.split()
            record = {
                "level": level,
                "method": method,
                "path": path,
                "status": int(status),
                "ms": int(duration.removesuffix("ms")),
            }
        except ValueError:  # wrong number of fields, or non-numeric status/duration
            stats["invalid"] += 1
            continue
        yield record


def slow(records: Iterable[dict], threshold_ms: int) -> Iterator[dict]:
    return (record for record in records if record["ms"] > threshold_ms)


def take(iterable: Iterable, n: int) -> Iterator:
    return islice(iterable, n)


def batched_items(iterable: Iterable, size: int) -> Iterator[list]:
    if size < 1:
        raise ValueError("size must be at least 1")
    iterator = iter(iterable)
    while batch := list(islice(iterator, size)):
        yield batch


def total_ms_by_path(records: Iterable[dict]) -> dict[str, int]:
    totals: dict[str, int] = {}
    for record in records:
        totals[record["path"]] = totals.get(record["path"], 0) + record["ms"]
    return totals

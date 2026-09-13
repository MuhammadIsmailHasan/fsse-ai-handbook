"""Tests for stream.py. Don't edit this file."""

import inspect
import types

import pytest

from stream import batched_items, parse_records, read_lines, slow, take, total_ms_by_path

LINES = [
    "2026-09-13T10:02:11 INFO GET /api/jobs 200 34ms",
    "2026-09-13T10:02:12 ERROR POST /api/applications 500 820ms",
    "garbage line",
    "2026-09-13T10:03:40 WARN GET /api/jobs 429 610ms",
    "2026-09-13T10:04:01 INFO GET /api/jobs 200 abcms",
    "2026-09-13T10:05:22 INFO POST /api/applications 201 90ms",
]


def test_read_lines_is_lazy_and_strips_newlines(tmp_path):
    path = tmp_path / "app.log"
    path.write_text("first ☕\nsecond\n", encoding="utf-8")
    lines = read_lines(str(path))
    assert isinstance(lines, types.GeneratorType)
    assert list(lines) == ["first ☕", "second"]


def test_parse_records_skips_and_counts_invalid():
    stats = {}
    records = parse_records(LINES, stats)
    assert isinstance(records, types.GeneratorType)
    parsed = list(records)
    assert parsed[1] == {"level": "ERROR", "method": "POST", "path": "/api/applications", "status": 500, "ms": 820}
    assert len(parsed) == 4
    assert stats["invalid"] == 2


def test_slow_and_total():
    records = list(parse_records(LINES, {}))
    assert [r["ms"] for r in slow(records, 600)] == [820, 610]
    assert total_ms_by_path(records) == {"/api/jobs": 644, "/api/applications": 910}


def test_take():
    assert list(take(range(100), 3)) == [0, 1, 2]
    assert list(take([1], 5)) == [1]


def test_batched_items():
    assert list(batched_items(range(7), 3)) == [[0, 1, 2], [3, 4, 5], [6]]
    assert list(batched_items([], 3)) == []
    with pytest.raises(ValueError):
        list(batched_items([1], 0))
    assert inspect.isgeneratorfunction(batched_items)


def test_pipeline_is_truly_lazy():
    """10 million virtual lines: only a lazy pipeline can take the first 3 slow requests instantly."""

    def huge():
        for i in range(10_000_000):
            yield f"2026-09-13T10:00:00 INFO GET /api/jobs/{i} 200 {i % 1000}ms"

    stats = {}
    first_slow = list(take(slow(parse_records(huge(), stats), 997), 3))
    assert [r["path"] for r in first_slow] == ["/api/jobs/998", "/api/jobs/999", "/api/jobs/1998"]

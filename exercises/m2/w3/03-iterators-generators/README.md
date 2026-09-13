# M2 · W3 · 03 — Streaming Log Analytics

> 🚫🤖 **No-AI** · ⏱️ ~50 min

Log lines look like: `2026-09-13T10:02:12 ERROR POST /api/applications 500 120ms`

Implement in `stream.py` — **all lazy** (generators), except the final aggregations:

| Function | Returns |
|---|---|
| `read_lines(path)` | generator of lines without the trailing newline (UTF-8) |
| `parse_records(lines, stats)` | generator of dicts `{"level", "method", "path", "status": int, "ms": int}`; malformed lines are skipped and `stats["invalid"]` is incremented (start it at 0 if missing) |
| `slow(records, threshold_ms)` | generator of records with `ms` **greater than** threshold |
| `take(iterable, n)` | generator of at most `n` items (use `itertools.islice`) |
| `batched_items(iterable, size)` | generator of **lists** of up to `size` items (don't use `itertools.batched`); `size < 1` raises `ValueError` |
| `total_ms_by_path(records)` | dict path → total ms (this one consumes the iterator) |

```bash
cd exercises
uv run pytest m2/w3/03-iterators-generators
```

# M5 · W5 · 05 — Find the bottleneck in a trace

> 🚫🤖 **No-AI** · ⏱️ ~25 min

A trace is a list of spans. The two questions you ask it most are "what was the slowest step?" and "where did the time go?". Answer both in `trace_bottleneck.py`.

## Data

```python
@dataclass(frozen=True)
class Span:
    span_id: str
    service: str
    duration_ms: int
```

## Functions

```python
slowest_step(spans: list[Span]) -> str | None
```

Return the `span_id` of the span with the largest `duration_ms`. On a tie, return the **first** such span in the list. Return `None` for an empty list.

```python
time_by_service(spans: list[Span]) -> dict[str, int]
```

Return a dict mapping each `service` to the **total** `duration_ms` of its spans.

Example:

```python
spans = [Span("s1", "gateway", 10), Span("s2", "payments", 4200), Span("s3", "payments", 30)]
slowest_step(spans)     # -> "s2"
time_by_service(spans)  # -> {"gateway": 10, "payments": 4230}
```

```bash
cd exercises
uv run pytest m5/w5/05-trace-bottleneck
```

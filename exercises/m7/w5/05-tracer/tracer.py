"""Module 7 · W5 — A tiny tracer: traces and spans (no API key needed).

Observability tools (Langfuse, OpenTelemetry, ...) all record the same shape:
  TRACE = one request from start to finish
  SPAN  = one step inside it (retrieve, rerank, llm call, tool call), nested like a call tree
Each span has a start, an end, attributes (tokens, cost, ids) and a status.
"""

import time  # noqa: F401
from contextlib import contextmanager  # noqa: F401


class Span:
    """The live handle you get inside `with tracer.span(...) as s:`. Methods/attributes:
        s.id       the span id
        s.set(**attrs)   add attributes (later calls add to / overwrite earlier ones)"""

    def __init__(self, span_id: str) -> None:
        raise NotImplementedError

    def set(self, **attrs) -> None:
        raise NotImplementedError


class Tracer:
    """Tracer(clock=time.perf_counter, ids=None)
        clock() -> float seconds.   ids() -> a new unique string each call (default: "1", "2", "3", ... as strings).

    with tracer.span(name, **attrs) as s:      # a context manager
      - if no span is open, this starts a NEW TRACE (trace_id = ids()); otherwise it is a child of the innermost open span
      - the span id is ids(); take ids in this order: the trace id FIRST (only for a new trace), then the span id
      - start = clock() when entering, end = clock() when leaving
      - if the body raises: status "error", error "<ExceptionClass>: <message>", the exception is re-raised
        (outer spans the exception passes through also become "error")
    When the OUTERMOST span closes, the finished trace is appended to tracer.traces as
        {"trace_id": ..., "spans": [span dicts in the order the spans STARTED]}
    A span dict: {"id", "trace_id", "parent_id" (None for the root), "name", "start", "end", "duration" (end - start),
                  "attrs": {...}, "status": "ok" | "error", "error": None | "Type: message"}
    """

    def __init__(self, clock=time.perf_counter, ids=None) -> None:
        raise NotImplementedError

    def span(self, name: str, **attrs):
        raise NotImplementedError


def slowest_span(trace: dict, include_root: bool = False) -> dict | None:
    """The span with the largest duration (the first one in start order on a tie).
    The root span (parent_id None) is skipped unless include_root. No candidates: None."""
    raise NotImplementedError


def total(trace: dict, key: str) -> float:
    """Sum of the numeric attribute `key` over all spans that have it (bool and non-numbers are ignored). None found: 0."""
    raise NotImplementedError


def render_tree(trace: dict) -> list[str]:
    """One line per span, children indented by two spaces per level, in start order:
        "<indent><name> (<ms> ms)"          ms = round(duration * 1000)
    with " ERROR" appended for spans whose status is "error".   Example:
        rag (120 ms)
          retrieve (30 ms)
          llm (80 ms) ERROR"""
    raise NotImplementedError

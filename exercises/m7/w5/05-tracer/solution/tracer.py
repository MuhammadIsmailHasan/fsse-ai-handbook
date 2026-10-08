import itertools
import time
from contextlib import contextmanager


class Span:
    def __init__(self, span_id):
        self.id = span_id
        self.attrs = {}

    def set(self, **attrs):
        self.attrs.update(attrs)


class Tracer:
    def __init__(self, clock=time.perf_counter, ids=None):
        self.clock = clock
        if ids is None:
            counter = itertools.count(1)
            ids = lambda: str(next(counter))
        self.ids = ids
        self.traces = []
        self._stack = []          # open span dicts
        self._current = None      # the trace being built

    @contextmanager
    def span(self, name, **attrs):
        if not self._stack:
            self._current = {"trace_id": self.ids(), "spans": []}
        parent = self._stack[-1] if self._stack else None
        handle = Span(self.ids())
        handle.attrs.update(attrs)
        record = {
            "id": handle.id,
            "trace_id": self._current["trace_id"],
            "parent_id": parent["id"] if parent else None,
            "name": name,
            "start": self.clock(),
            "end": None,
            "duration": None,
            "attrs": handle.attrs,
            "status": "ok",
            "error": None,
        }
        self._current["spans"].append(record)
        self._stack.append(record)
        try:
            yield handle
        except BaseException as exc:
            record["status"] = "error"
            record["error"] = f"{type(exc).__name__}: {exc}"
            raise
        finally:
            record["end"] = self.clock()
            record["duration"] = record["end"] - record["start"]
            self._stack.pop()
            if not self._stack:
                self.traces.append(self._current)
                self._current = None


def slowest_span(trace, include_root=False):
    best = None
    for span in trace["spans"]:
        if span["parent_id"] is None and not include_root:
            continue
        if best is None or span["duration"] > best["duration"]:
            best = span
    return best


def total(trace, key):
    value = 0
    for span in trace["spans"]:
        v = span["attrs"].get(key)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            value += v
    return value


def render_tree(trace):
    depth = {}
    lines = []
    for span in trace["spans"]:
        level = 0 if span["parent_id"] is None else depth[span["parent_id"]] + 1
        depth[span["id"]] = level
        suffix = " ERROR" if span["status"] == "error" else ""
        lines.append(f"{'  ' * level}{span['name']} ({round(span['duration'] * 1000)} ms){suffix}")
    return lines

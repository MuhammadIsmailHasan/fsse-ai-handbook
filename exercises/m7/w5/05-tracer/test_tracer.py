import pytest

from tracer import Tracer, render_tree, slowest_span, total


class Clock:
    """Returns the given times in order, one per call."""

    def __init__(self, *times):
        self.times = list(times)

    def __call__(self):
        return self.times.pop(0)


def test_one_trace_with_nested_spans():
    clock = Clock(0.0, 0.01, 0.04, 0.05, 0.13, 0.15)       # rag start, retrieve start/end, llm start/end, rag end
    tracer = Tracer(clock)
    with tracer.span("rag", user="u1") as root:
        root.set(question_chars=21)
        with tracer.span("retrieve") as s:
            s.set(chunks=5)
        with tracer.span("llm", model="m") as s:
            s.set(input_tokens=1200, output_tokens=150)
    assert len(tracer.traces) == 1
    trace = tracer.traces[0]
    assert trace["trace_id"] == "1"
    names = [s["name"] for s in trace["spans"]]
    assert names == ["rag", "retrieve", "llm"]
    rag, retrieve, llm = trace["spans"]
    assert (rag["id"], retrieve["id"], llm["id"]) == ("2", "3", "4")           # trace id took "1"
    assert rag["parent_id"] is None and retrieve["parent_id"] == "2" and llm["parent_id"] == "2"
    assert rag["attrs"] == {"user": "u1", "question_chars": 21}
    assert retrieve["attrs"] == {"chunks": 5} and llm["attrs"] == {"model": "m", "input_tokens": 1200, "output_tokens": 150}
    assert rag["start"] == 0.0 and rag["end"] == 0.15 and rag["duration"] == pytest.approx(0.15)
    assert retrieve["duration"] == pytest.approx(0.03) and llm["duration"] == pytest.approx(0.08)
    assert all(s["trace_id"] == "1" and s["status"] == "ok" and s["error"] is None for s in trace["spans"])


def test_a_trace_is_stored_only_when_the_outermost_span_closes():
    tracer = Tracer(Clock(*range(10)))
    with tracer.span("outer"):
        with tracer.span("inner"):
            pass
        assert tracer.traces == []
    assert len(tracer.traces) == 1


def test_two_requests_make_two_traces_with_their_own_ids():
    ids = iter(["t1", "s1", "t2", "s2"])
    tracer = Tracer(Clock(*range(10)), ids=lambda: next(ids))
    with tracer.span("a"):
        pass
    with tracer.span("b"):
        pass
    assert [t["trace_id"] for t in tracer.traces] == ["t1", "t2"]
    assert [t["spans"][0]["id"] for t in tracer.traces] == ["s1", "s2"]


def test_siblings_and_deeper_nesting_get_the_right_parents():
    tracer = Tracer(Clock(*range(20)))
    with tracer.span("root"):
        with tracer.span("a"):
            with tracer.span("a1"):
                pass
        with tracer.span("b"):
            pass
    spans = {s["name"]: s for s in tracer.traces[0]["spans"]}
    assert spans["a1"]["parent_id"] == spans["a"]["id"]
    assert spans["a"]["parent_id"] == spans["root"]["id"] and spans["b"]["parent_id"] == spans["root"]["id"]


def test_errors_are_recorded_and_re_raised_through_every_open_span():
    tracer = Tracer(Clock(*range(10)))
    with pytest.raises(TimeoutError, match="model timed out"):
        with tracer.span("rag"):
            with tracer.span("llm"):
                raise TimeoutError("model timed out")
    rag, llm = tracer.traces[0]["spans"]
    assert llm["status"] == "error" and llm["error"] == "TimeoutError: model timed out"
    assert rag["status"] == "error" and rag["error"] == "TimeoutError: model timed out"
    assert rag["end"] is not None and llm["duration"] is not None


def test_an_error_caught_inside_does_not_fail_the_outer_span():
    tracer = Tracer(Clock(*range(10)))
    with tracer.span("rag"):
        try:
            with tracer.span("rerank"):
                raise ValueError("bad score")
        except ValueError:
            pass
    rag, rerank = tracer.traces[0]["spans"]
    assert rag["status"] == "ok" and rerank["status"] == "error"


def test_the_tracer_is_usable_after_an_error():
    tracer = Tracer(Clock(*range(10)))
    with pytest.raises(RuntimeError):
        with tracer.span("first"):
            raise RuntimeError("x")
    with tracer.span("second"):
        pass
    assert [t["spans"][0]["name"] for t in tracer.traces] == ["first", "second"]
    assert tracer.traces[1]["spans"][0]["parent_id"] is None


def make_trace():
    tracer = Tracer(Clock(0.0, 0.0, 0.03, 0.03, 0.11, 0.12))
    with tracer.span("rag"):
        with tracer.span("retrieve") as s:
            s.set(cost=0.0001)
        with tracer.span("llm") as s:
            s.set(input_tokens=1000, output_tokens=200, cost=0.004, cached=True, note="x")
    return tracer.traces[0]


def test_slowest_span_skips_the_root_by_default():
    trace = make_trace()
    assert slowest_span(trace)["name"] == "llm"
    assert slowest_span(trace, include_root=True)["name"] == "rag"
    assert slowest_span({"spans": []}) is None
    only_root = Tracer(Clock(0.0, 1.0))
    with only_root.span("solo"):
        pass
    assert slowest_span(only_root.traces[0]) is None


def test_slowest_span_tie_goes_to_the_first_started():
    tracer = Tracer(Clock(0, 0, 1, 1, 2, 3))
    with tracer.span("root"):
        with tracer.span("first"):
            pass
        with tracer.span("second"):
            pass
    assert slowest_span(tracer.traces[0])["name"] == "first"


def test_total_sums_numbers_only():
    trace = make_trace()
    assert total(trace, "cost") == pytest.approx(0.0041)
    assert total(trace, "input_tokens") == 1000
    assert total(trace, "cached") == 0            # a bool is not a number
    assert total(trace, "note") == 0 and total(trace, "missing") == 0


def test_render_tree():
    assert render_tree(make_trace()) == ["rag (120 ms)", "  retrieve (30 ms)", "  llm (80 ms)"]


def test_render_tree_marks_errors_and_indents_deeper_levels():
    tracer = Tracer(Clock(0.0, 0.0, 0.0, 0.01, 0.02, 0.05))
    with pytest.raises(ValueError):
        with tracer.span("rag"):
            with tracer.span("llm"):
                with tracer.span("parse"):
                    raise ValueError("bad json")
    assert render_tree(tracer.traces[0]) == ["rag (50 ms) ERROR", "  llm (20 ms) ERROR", "    parse (10 ms) ERROR"]

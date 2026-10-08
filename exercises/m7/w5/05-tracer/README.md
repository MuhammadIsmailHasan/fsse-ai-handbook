# Module 7 · W5 · Traces and Spans

> 🚫🤖 **No-AI** · ⏱️ ~55 min · no API key needed

When an AI request is slow, expensive or wrong, a log line is not enough. You need to see **every step** of that one request: what was retrieved, how long the model took, how many tokens it used, which step failed. Tools like **Langfuse** and **OpenTelemetry** record this as:

- a **trace** = one request from start to finish,
- **spans** = the steps inside it, nested like a call tree. Each has a start, an end, attributes (tokens, cost, ids) and a status.

```text
rag (120 ms)                       ← the trace's root span
  retrieve (30 ms)   chunks=5
  rerank   (10 ms)
  llm      (80 ms)   input_tokens=1200  output_tokens=150  cost=0.004
```

| Piece | Does |
|---|---|
| `Tracer.span(name, **attrs)` | a context manager: opens a span, closes it, records the duration; a span with no open parent **starts a new trace**; an exception marks the span (and the spans it passes through) as `error` and is **re-raised** |
| `slowest_span(trace)` | where did the time go? |
| `total(trace, "cost")` | sum tokens or cost over the steps |
| `render_tree(trace)` | a readable outline of the request |

The clock and the id generator are passed in, so tests can use fake time. Real tracers do exactly this with real time, plus sending the data to a server.

```bash
cd exercises
uv run pytest m7/w5/05-tracer
```

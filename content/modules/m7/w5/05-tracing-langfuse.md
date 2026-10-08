---
title: "Tracing with Langfuse"
summary: "See inside every AI request — traces and spans, what to record (prompts, tokens, cost, latency, errors), scores and feedback, sessions, privacy and sampling, and how a tool such as Langfuse turns traces into debugging and evals."
type: lesson
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: core, ops: optional }
durationMinutes: 180
tags: [observability, tracing, langfuse, spans, cost, monitoring]
lastReviewed: 2026-10
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What **observability** means for AI features
- **Traces** and **spans**: the shape of one request
- What to **record** on each span (and what not to)
- **Scores and feedback** attached to traces
- How **Langfuse** (and tools like it) uses these ideas
- **Privacy, sampling and cost** of tracing itself
- How traces feed **debugging, evals and monitoring**

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Observability** | Being able to see what your system did, from the outside | Keteramatan |
| **Trace** | The full record of one request, from start to finish | Jejak |
| **Span** | One step inside a trace, with a start, an end and details | Rentang / langkah |
| **Generation** | A span for one model call (prompt, output, tokens, cost) | Panggilan model |
| **Session** | Several traces from the same conversation or user visit | Sesi |
| **Score** | A number attached to a trace or span: thumbs, eval result | Skor |
| **Langfuse** | An open-source platform for tracing, scoring and managing LLM apps | Platform observabilitas LLM |
| **Sampling** | Recording only a share of requests | Pengambilan sampel |

## 🧠 The big idea

When a parcel goes wrong, a delivery company shows you the **tracking page**: picked up 09:02, sorted 11:40, left the warehouse 14:10, delivered 16:55. Each line is a step with a time. You can see where it got stuck.

An AI request is a parcel with many steps: rewrite the question, search, re-rank, build the prompt, call the model, check the citations, send the answer. A **trace** is its tracking page, and each **span** is one line on it. Without it, "the bot was slow and wrong yesterday" is a mystery. With it, you open the trace, see that the search took 1.8 seconds and returned nothing useful, and you know where to work.

## ❓ Why it matters

AI systems fail in new ways: a slow model, a retry loop, a surprise token bill, a retrieval miss, a prompt that grew too long. Normal logs ("200 OK in 3.2 s") cannot tell you which step caused the problem or what the model actually saw.

Tracing gives you:

- **Debugging:** the exact prompt, context, output and timing of the failed request.
- **Cost control:** tokens and cost per request, per feature, per user.
- **Latency work:** which step is the slow one.
- **Quality loop:** scores and user feedback attached to the very request they are about, ready to become eval cases.
- **Accountability:** which prompt version and model produced an answer.

## 📖 Step by step

### 1. Traces and spans

```text
trace "rag-answer"  (one request)                          120 ms
 ├─ span "rewrite"                                          15 ms
 ├─ span "retrieve"     chunks=20                           30 ms
 ├─ span "rerank"       top_n=5                             10 ms
 ├─ generation "llm"    model=…  input_tokens=1200           80 ms ← model call
 │                      output_tokens=150  cost=0.004
 └─ span "validate-citations"   ok=true                      2 ms
```

A **trace** is the whole request. A **span** is one step. Spans **nest**: a step may contain smaller steps (a tool call inside an agent step). A span that is a model call is often called a **generation** and carries the prompt, the output and the token usage.

### 2. A tiny tracer, to understand the mechanics

Real tools do this with real clocks and send the data to a server. The core is small:

```python
import itertools, time
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
        counter = itertools.count(1)
        self.ids = ids or (lambda: str(next(counter)))
        self.traces, self._stack, self._current = [], [], None

    @contextmanager
    def span(self, name, **attrs):
        if not self._stack:                                         # no open span → a NEW trace starts
            self._current = {"trace_id": self.ids(), "spans": []}
        parent = self._stack[-1] if self._stack else None
        handle = Span(self.ids())
        handle.attrs.update(attrs)
        record = {"id": handle.id, "trace_id": self._current["trace_id"],
                  "parent_id": parent["id"] if parent else None, "name": name,
                  "start": self.clock(), "end": None, "duration": None,
                  "attrs": handle.attrs, "status": "ok", "error": None}
        self._current["spans"].append(record)
        self._stack.append(record)
        try:
            yield handle
        except BaseException as exc:
            record["status"] = "error"
            record["error"] = f"{type(exc).__name__}: {exc}"
            raise                                                   # recording an error must not hide it
        finally:
            record["end"] = self.clock()
            record["duration"] = record["end"] - record["start"]
            self._stack.pop()
            if not self._stack:
                self.traces.append(self._current)
                self._current = None
```

Using it looks like this:

```python
with tracer.span("rag", user="u1"):
    with tracer.span("retrieve") as s:
        s.set(chunks=5)
    with tracer.span("llm", model="m") as s:
        s.set(input_tokens=1200, output_tokens=150, cost=0.004)
```

Three details worth noticing: a span without an open parent **starts a new trace**; an exception **marks the span as error and is re-raised** (the tracer observes, it does not swallow); and the clock and id generator are injectable, so tests use fake time.

### 3. Reading a trace

With the data in hand, three questions answer most problems:

```python
def slowest_span(trace, include_root=False):
    best = None
    for span in trace["spans"]:
        if span["parent_id"] is None and not include_root:
            continue
        if best is None or span["duration"] > best["duration"]:
            best = span
    return best

def total(trace, key):                    # sum tokens or cost over the steps
    value = 0
    for span in trace["spans"]:
        v = span["attrs"].get(key)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            value += v
    return value

def render_tree(trace):
    depth, lines = {}, []
    for span in trace["spans"]:
        level = 0 if span["parent_id"] is None else depth[span["parent_id"]] + 1
        depth[span["id"]] = level
        suffix = " ERROR" if span["status"] == "error" else ""
        lines.append(f"{'  ' * level}{span['name']} ({round(span['duration'] * 1000)} ms){suffix}")
    return lines
```

- *Where did the time go?* `slowest_span`.
- *What did it cost?* `total(trace, "cost")`.
- *What happened, in order?* `render_tree`.

### 4. What to record

| On every model call | Why |
|---|---|
| model name and version, key parameters | to compare models and reproduce |
| the prompt (or its **name, version and fingerprint**) and the messages | to see what the model saw |
| the output and the **stop reason** | cut off? refusal? |
| **input and output tokens**, cache read/write tokens | cost and cache health |
| latency, and **time to first token** for streamed answers | speed as users feel it |
| errors, retries, fallbacks used | reliability |

| On the request | Why |
|---|---|
| user id (or a hashed id), tenant, session id | per-user cost, support, privacy requests |
| the feature name and app version | slicing |
| retrieved ids and scores, filters, rewritten query | RAG debugging |
| tool calls: name, arguments (masked), result type, duration | agent debugging |
| validation results: citations valid, guardrail hits | quality and safety |

Add **attributes** (key-value) instead of putting everything in the span name. Keep names stable (`retrieve`, `llm`), so you can group them.

### 5. Scores and feedback

A **score** is a number attached to a trace (or span) after the fact:

- **User feedback:** thumbs up/down, "was this helpful?", a handoff to a human.
- **Automatic checks:** citation validity, guardrail triggers, format valid.
- **Eval results:** a judge's faithfulness score for this trace.
- **Business signals:** the ticket was resolved, the user did not ask again.

Because the score sits on the trace, one click takes you from "this answer got a thumbs-down" to the exact prompt, context and tokens. And a thumbs-down trace is the best **new test case** for next week's eval.

### 6. Sessions, users, and tags

Group traces from one conversation in a **session**, so you can read the whole chat. Tag traces with user, tenant, environment (`prod`, `staging`), release and feature, so you can filter ("show failures for tenant 7 since release 2.3"). Version your prompts and record the version on the trace: then "did prompt 1.4 make cost go up?" becomes a chart.

### 7. Langfuse and similar tools

**Langfuse** is an open-source platform for LLM observability. You can use their cloud or **self-host** it (useful for private data). It provides, roughly:

- **Tracing** with traces, spans, generations, sessions and users, plus a UI to browse, search and filter them.
- **Cost and latency** dashboards from the token usage you record.
- **Scores** (from code, users or evaluators) and annotation queues for human review.
- **Datasets and experiments** to run your eval cases and compare versions.
- **Prompt management** with versions.

You integrate by adding an SDK: usually a decorator or context manager around your functions, plus integrations for common frameworks and model SDKs. The API names change between versions, so follow the current quick-start guide. The shape is exactly the tiny tracer above:

```python
# Pseudocode: the real decorator/context-manager names differ per SDK version
@observe(name="rag-answer")
def answer(question, user_id):
    with span("retrieve") as s:
        chunks = search(question)
        s.update(metadata={"chunks": len(chunks)})
    with generation("llm", model=MODEL, input=prompt) as g:
        text = call_model(prompt)
        g.update(output=text, usage={"input": 1200, "output": 150})
    return text
```

Other tools do the same job (Arize Phoenix, LangSmith, Helicone, OpenTelemetry-based setups). **OpenTelemetry** is a vendor-neutral standard for traces and spans, and many LLM tools can send or receive it. Choose by hosting needs, privacy, cost and team habits, not by brand.

### 8. Privacy, sampling and cost of tracing

Traces contain prompts, and prompts contain user data.

- **Mask or drop** personal data before it leaves your app (emails, phones, card numbers, secrets): the same redaction you wrote for guardrails.
- **Never log secrets** (API keys, tokens, passwords) in prompts or attributes.
- **Retention:** keep traces only as long as needed (for example 30 days), and support deletion requests.
- **Access:** limit who can read production traces.
- **Self-host or choose a provider with the right data terms** for sensitive data.
- **Sampling:** at high traffic, store all errors and slow requests, and a sample (say 10%) of the rest. Always keep traces with user feedback.
- **Overhead:** send traces **asynchronously** (a background queue), never block the user's request on the tracing server, and make sure a tracing failure never breaks the app.

### 9. Traces power the quality loop

```text
production traffic ─► traces ─► scores & thumbs-down ─► review ─► new eval cases ─► eval/gate ─► better release
                         ▲                                                                       │
                         └───────────────────────── monitoring ◄─────────────────────────────────┘
```

Set up a few **alerts**: error rate, p95 latency, cost per day, share of "no answer", citation-validity rate, thumbs-down rate. Alert on changes after a release, and use the trace links in the alert to start the investigation.

### Choosing your setup

| Situation | Do this |
|---|---|
| Starting out | trace every request: retrieval, model call, validation; record tokens, cost, latency, versions |
| Private data | mask before sending; self-host or pick strict data terms |
| High traffic | sample normal requests; keep all errors, slow ones and those with feedback |
| Need to find "why slow" | spans with durations, and `slowest_span` or the UI's flame view |
| Need to find "why expensive" | tokens and cost per span, per feature, per user |
| Want a quality loop | attach scores and feedback to traces; turn failures into eval cases |
| Many services | propagate a trace id (OpenTelemetry) across services |

- ✅ Trace every model call with usage and the prompt version.
- ✅ Mask personal data before recording.
- 🚫 Blocking user requests on the tracing backend.
- 🚫 Storing secrets or raw personal data in traces.

## ⚠️ Common mistakes

- Logging only the final answer, not the steps.
- No token or cost attributes, so the bill is a surprise.
- Recording raw user data and secrets.
- Tracing code that can crash the request.
- Spans without stable names, so nothing can be grouped.
- No link from user feedback to the trace.
- Keeping every trace forever.
- Never looking at the traces until something breaks.

:::revoshop
Sketch the spans for RevoShop's "ask about my order" request: list each step, the attributes you would record on each, which fields you would mask, and one alert you would set.
:::

## 🏆 Best practices

- [ ] Wrap every request in a trace, and every step (retrieve, rerank, model, tool, validate) in a span.
- [ ] Record model, parameters, prompt version, tokens, cost, latency and stop reason on each generation.
- [ ] Attach feedback and automatic scores to traces; turn failures into eval cases.
- [ ] Mask personal data and secrets; set retention; restrict access.
- [ ] Send traces asynchronously and make tracing failures harmless.
- [ ] Sample high-volume traffic but keep errors, slow requests and feedback.
- [ ] Add dashboards and alerts for errors, latency, cost and quality signals.
- [ ] Use stable span names and consistent attributes.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain traces and spans with the parcel-tracking picture. Why must a tracing error never break the user's request?

## 📐 Design it

SupportDesk AI: some customers wait 12+ seconds for an answer, the monthly model bill is 40% above forecast, and support leads say "the bot was wrong on Tuesday" without details. Design the tracing: spans, attributes, scores, privacy rules, sampling, dashboards and alerts, and how you would use it to find each of the three problems.

:::quiz
Show a possible design

- **Spans per request:** `chat-request` (root) → `auth`, `rewrite-query`, `retrieve` (vector + keyword), `rerank`, `build-prompt`, `llm` (generation), `validate-output` (citations, guardrails), `stream-to-client`. Tool calls become child spans.
- **Attributes:** on the root — tenant, hashed user id, session id, feature, app and prompt versions, environment; on `retrieve` — filters, pool size, scores summary, retrieved ids; on `llm` — model, parameters, input/output tokens, cache read/write tokens, cost, stop reason, time to first token, retries and fallbacks; on `validate-output` — citation validity, guardrail hits.
- **Scores:** thumbs up/down and "talk to a human" clicks attached to the trace; automatic scores (citations valid, no-answer, guardrail triggered); a nightly judge score for faithfulness on a sample.
- **Privacy:** mask emails, phones and card numbers before export; never include secrets; keep prompts and outputs for 30 days; restrict production traces to the AI team; deletion by user id on request.
- **Sampling:** keep 100% of errors, slow traces (above 8 s), traces with feedback or handoff, and 10% of the rest; send asynchronously with a bounded queue.
- **Slow answers:** filter traces above 12 s and compare span durations: if `retrieve` or `rerank` dominates, fix the search; if `llm` time to first token dominates, shorten the prompt, enable caching, or choose a faster model; if retries appear, fix provider errors or timeouts.
- **Over-budget bill:** group cost by feature, tenant, prompt version and day; look for long prompts (too many chunks), missing cache hits, retry loops, or one tenant sending huge inputs; set per-tenant limits and a daily cost alert.
- **"Wrong on Tuesday":** search traces by date and thumbs-down; open the retrieved ids, the prompt version and the answer; classify with the diagnosis categories (retrieval miss, dropped, not used) and add each to the eval set.
- **Alerts:** p95 latency, error rate, cost per day, thumbs-down rate, no-answer rate and citation-invalid rate, each compared with the last release.

**Rule shown:** one well-attributed trace per request answers "what happened, how long, how much, and was it good", and feeds the eval loop.
:::

### 📝 Self-review checklist

- [ ] Every step of the request is a named span
- [ ] Tokens, cost, latency and versions are recorded
- [ ] Scores and feedback are attached to traces
- [ ] Personal data and secrets are masked; retention is set
- [ ] Tracing is asynchronous and failure-safe

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m7/w5/05-tracer" ai="no-ai" title="A tiny tracer: traces and spans"}
Write `Span`, `Tracer.span` (a context manager: a span without an open parent starts a new trace, children nest, errors are recorded and re-raised, a finished trace is stored when the outermost span closes), `slowest_span`, `total` and `render_tree`. The clock and id generator are injected so the tests use fake time. No API key needed.
:::

:::hints
- Keep a stack of open span records; the trace id is taken **first** (only for a new trace), then the span id.
- Add each record to `current["spans"]` when the span **starts**, so the order is start order.
- In `except BaseException`: set `status` and `error`, then `raise`. Put the end time in `finally`.
- When the stack becomes empty after popping, append the finished trace to `self.traces`.
- `total`: ignore bools (`isinstance(True, int)` is `True`).
- `render_tree`: remember each span's depth by id; children use `depth[parent] + 1`.
:::

## ✅ Quick check

:::quiz
Where does a trace start and end?

A trace starts when the first (outermost) span opens, with no parent, and ends when that outermost span closes. Spans opened inside it become its children. So one request normally equals one trace.
:::

:::quiz
Why record prompt version and token usage on each model call?

The version lets you tie a good or bad result to the exact prompt, compare versions and roll back. Token usage gives cost and shows long prompts or missing cache hits. Without them, you cannot explain a bill or a change in quality.
:::

:::quiz
How can tracing itself cause harm, and how do you avoid it?

It can leak personal data or secrets into logs, slow requests if it blocks on a tracing server, or crash the app if it throws. Mask data before export, set retention and access rules, send traces asynchronously, and catch tracing errors so they never affect the user.
:::

## 📚 Keep learning

- [Langfuse documentation](https://langfuse.com/docs)
- [OpenTelemetry: Traces concepts](https://opentelemetry.io/docs/concepts/signals/traces/)
- [OpenTelemetry: GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)

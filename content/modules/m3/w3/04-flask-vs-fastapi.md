---
title: "Flask vs FastAPI Decision Guide"
summary: Choose between Flask and FastAPI with reasons, not fashion — what each does well, the real cost of a rewrite, how to move one endpoint at a time, and how to explain your choice in an interview.
type: lesson
source: original
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: optional }
durationMinutes: 90
tags: [fastapi, flask, decision, architecture, migration]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What Flask and FastAPI each do well
- The questions that decide the choice
- Why "FastAPI is faster" is usually the wrong reason
- How to move from Flask to FastAPI **one endpoint at a time**
- How to explain the choice in an interview

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **WSGI** | The older Python web standard: one request, one worker at a time | Standar web Python lama |
| **ASGI** | The newer standard that supports `async` and streaming | Standar web Python baru |
| **Batteries included** | Many features come with the framework | Fitur lengkap bawaan |
| **Micro-framework** | A small core; you add the rest yourself | Kerangka kecil |
| **Migration cost** | Time, bugs and risk of moving to something new | Biaya pindah |
| **Strangler pattern** | Replace an old system piece by piece, not all at once | Mengganti sedikit demi sedikit |
| **Trade-off** | You gain one thing and give up another | Untung dan rugi |

## 🧠 The big idea

Choosing a framework is like choosing a **vehicle**. A motorbike (Flask) is light, you know it, and it gets through small streets. A delivery van (FastAPI) has a bigger load space and a built-in GPS (validation and docs). Neither is "better". The right one depends on the road and the cargo. And if your bike already works for your route, buying a van "because vans are modern" is a waste.

## ❓ Why it matters

Teams lose months on rewrites that did not need to happen, and also ship slow, painful code because they stayed with a tool that no longer fit. A good engineer can say **why** a tool fits, and what it costs. This also shows up in interviews and in real jobs: you will read Flask code at work, and you will be asked to start FastAPI services. You need to move between them without drama.

## 📖 Step by step

### 1. The same endpoint in both

Flask (you wrote this in RevoShop):

```python
@app.post("/notes")
def create_note():
    data = request.get_json()
    if not data or "text" not in data:
        return {"error": "text is required"}, 400
    note = repo.add(data["text"])
    return note, 201
```

FastAPI (what you wrote this module):

```python
class NoteIn(BaseModel):
    text: str

@app.post("/notes", status_code=201)
def create_note(body: NoteIn, repo: NoteRepo = Depends(get_repo)):
    return repo.add(body.text)
```

In FastAPI the type hints do the validation, return a clear `422` for bad input, and feed the automatic docs. In Flask you add that yourself, usually with Marshmallow or a similar library.

### 2. What each does well

| | Flask | FastAPI |
|---|---|---|
| Style | small core, add what you need | validation, docs and DI built in |
| Validation | extra library (Marshmallow, Pydantic) | Pydantic built in |
| API docs | extra library (flask-smorest, apispec) | automatic OpenAPI at `/docs` |
| `async` | possible, but not the main design | first class (ASGI) |
| Streaming (AI) | works, takes more care | simple with `StreamingResponse` |
| HTML pages (Jinja) | strong, mature | possible, not the focus |
| Ecosystem | very large, many years of extensions | newer, growing quickly |
| Age in real codebases | everywhere | common in new services, especially AI |

### 3. "FastAPI is faster" is a weak reason

Benchmarks of "hello world" show a gap. Your real app spends its time **waiting on the database and other services**, not in the framework. A slow SQL query costs a thousand times more than the framework choice. `async` helps only when you do a lot of waiting in parallel (you saw this in the async lesson). Pick FastAPI for validation, docs and async I/O, not for a benchmark number.

### 4. The questions that decide

Ask these in order:

1. **Do you render HTML pages on the server?** Flask (or Django) fits better.
2. **Is there already a working Flask app?** Then you need a real reason to move. A rewrite has a cost and gives users nothing new.
3. **Does the service wait on many slow calls, or stream AI tokens?** FastAPI helps.
4. **Do many clients need clear contracts and docs?** FastAPI's automatic OpenAPI saves work.
5. **What does the team already know?** A skilled team in Flask beats a new team fighting FastAPI.

### 5. Migrate one endpoint at a time (strangler)

Never stop the world for a rewrite. Run both side by side.

```text
            ┌───────────────┐   /api/ai/*  ──►  new FastAPI service
 client ──► │ gateway/proxy │
            └───────────────┘   everything else ─► existing Flask app
```

1. Put a gateway (nginx, API Gateway) in front.
2. Build the **new** feature in FastAPI. Send only its path to FastAPI.
3. Move old endpoints later, one by one, when they need big changes anyway.
4. Share the database carefully, or give the new service its own.
5. When Flask has nothing left, remove it.

This is how a real team keeps shipping while it modernizes.

### 6. Your choices in this handbook

- **RevoShop** stays Flask. It works, and it teaches the fundamentals.
- **CareerPilot's AI service** is FastAPI. It streams, waits on an AI model, and exposes a clear API.
- In a job, expect both. Knowing Flask *and* FastAPI is a plus for remote roles, because many companies run old Flask services next to new FastAPI ones.

### Choosing

| Situation | Choose |
|---|---|
| Server-rendered pages | Flask (or Django) |
| Existing Flask app, nothing forcing a change | keep Flask |
| New API with AI streaming or lots of I/O waiting | FastAPI |
| New API, small team that knows Flask well | Flask is fine |
| Old Flask app + one new AI feature | add a FastAPI service beside it |

## ⚠️ Common mistakes

- Rewriting a working app only because FastAPI is trendy.
- Choosing by benchmark numbers instead of the real bottleneck (the database).
- Mixing Flask and FastAPI inside one process without a plan.
- Underestimating migration cost: tests, auth, deployment and monitoring all change.
- Saying "X is better" in an interview, with no reasons and no trade-offs.

:::revoshop
Think about adding a "smart product description" feature to RevoShop that streams text from an AI model. (1) Would you rewrite RevoShop in FastAPI, or add a separate FastAPI service? Why? (2) What would the gateway route to each? (3) List two things that would have to change if you did rewrite everything (hint: auth, tests, deployment).
:::

## 🏆 Best practices

- [ ] Decide with written reasons and trade-offs, not taste.
- [ ] Do not rewrite a working app without a business reason.
- [ ] Move gradually: gateway in front, one endpoint or service at a time.
- [ ] Keep the contract (URLs, JSON shapes) the same while moving.
- [ ] Measure the real bottleneck before blaming the framework.
- [ ] Learn both; the skills transfer (routing, validation, auth, testing).

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

In two minutes, explain to a teammate why a team might keep Flask for an old service but pick FastAPI for a new AI service. Use the motorbike-and-van picture, and name one trade-off for each side.

## 📐 Design it

A company has a Flask monolith with 80 endpoints. The product team wants an AI assistant with streaming answers. Plan the approach: what you build, in which framework, how traffic reaches each part, what you leave alone, and what could go wrong.

:::quiz
Show a possible design

- **Build the assistant as a new FastAPI service.** It streams tokens (SSE) and waits on an AI model, which is what FastAPI is good at.
- **Leave the 80 Flask endpoints alone.** They work; nothing forces a rewrite.
- **Gateway in front:** route `/api/assistant/*` to FastAPI and everything else to Flask. The browser sees one domain.
- **Auth:** share the same JWT secret or an auth service, so one login works for both. Test that tokens are accepted by both.
- **Data:** the new service reads through the existing API, or gets its own tables. Avoid two services writing the same tables.
- **Observability:** one logging format and a request-id header across both, so a trace follows the request.
- **Risks:** two deployments to run, duplicated auth logic, proxy buffering that breaks streaming. Mitigate with shared libraries, a staging test and a gateway setting for streaming.
- **Later:** move a Flask endpoint only when it needs a big change anyway.

**Rule shown:** add new capabilities beside the old system; migrate old parts only when there is a reason.
:::

### 📝 Self-review checklist

- [ ] The choice comes with reasons and a stated trade-off
- [ ] The plan avoids a big-bang rewrite
- [ ] Auth and logging work across both services
- [ ] The risks are named

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m3/w3/04-decision" ai="no-ai" title="Write the decision guide as code"}
In `framework_choice.py`, implement `choose_framework(...)`. It returns `"flask"`, `"keep-flask"` or `"fastapi"` using three rules: server-rendered pages → Flask; an existing Flask app with no reason to move → keep it; otherwise a score (async I/O +2, AI streaming +2, auto docs +1, team knows FastAPI +1, minus 2 if migrating) that needs 3 to choose FastAPI.
:::

:::hints
- Check the two early-return rules first, in the order given.
- Booleans count as 0 or 1, so `2 * needs_async_io` works.
- Subtract 2 only when `existing_flask_app` is true.
- At the end: `score >= 3` → `"fastapi"`; otherwise `"keep-flask"` if there is an existing app, else `"flask"`.
:::

## ✅ Quick check

:::quiz
Why is "FastAPI is faster" usually a weak reason to rewrite a Flask app?

Real apps spend their time waiting on the database and other services, not in the framework. A slow query or a missing index costs far more than any framework difference, and a rewrite adds risk and cost. Fix the actual bottleneck first; choose FastAPI for validation, docs or async I/O when you truly need them.
:::

:::quiz
What is the strangler approach to moving from Flask to FastAPI?

Put a gateway in front of both, build new features in FastAPI and route only their paths there, and move old endpoints one by one when it makes sense. The app keeps working the whole time, and you remove Flask only when nothing is left in it.
:::

## 📚 Keep learning

- [FastAPI: Alternatives, Inspiration and Comparisons](https://fastapi.tiangolo.com/alternatives/)
- [Flask documentation](https://flask.palletsprojects.com/)
- [Martin Fowler: Strangler Fig](https://martinfowler.com/bliki/StranglerFigApplication.html)

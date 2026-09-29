---
title: "Why FastAPI Exists"
summary: Why learn FastAPI after Flask? It turns your Python type hints into automatic validation and interactive docs, and supports async out of the box — so you write less glue code and catch bad requests for free.
type: lesson
source: original
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: optional }
durationMinutes: 100
tags: [fastapi, flask, api, types, validation]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What FastAPI is and how it compares to the Flask you know
- How Python **type hints** become automatic validation and docs
- What `async` support buys you (and when it matters)
- Why "less glue code" means fewer bugs
- When FastAPI is worth it — and when Flask is perfectly fine

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **FastAPI** | A Python web framework built around type hints | Framework web berbasis tipe |
| **Type hint** | Saying a value's type in code (`item_id: int`) | Menyebut tipe nilai |
| **Validation** | Checking incoming data is the right shape | Memeriksa bentuk data |
| **OpenAPI** | A standard description of your whole API | Deskripsi standar API |
| **Swagger UI** | The interactive `/docs` page | Halaman docs interaktif |
| **async** | Doing other work while waiting on I/O | Mengerjakan lain saat menunggu |
| **Glue code** | Boilerplate you write to wire things together | Kode perekat berulang |

## 🧠 The big idea

Flask is a **plain kitchen**: it gives you a stove and lets you cook however you like — you write the order-checking and the menu card yourself. FastAPI is a **kitchen with a smart order screen**: you describe each dish once (with types), and it automatically checks orders for mistakes and prints the menu for customers. Same cooking, less paperwork.

## ❓ Why it matters

In RevoShop (Flask) you wrote validation by hand — checking that `price` is a number, returning `400` on bad input — and you kept API docs in sync manually (or with flask-smorest). That hand-written glue is where bugs hide and time drains.

FastAPI reads the **type hints** you'd write anyway and does that work for you: it validates every request against your types and generates always-correct interactive docs. Less code to write, fewer mistakes, and a live `/docs` page teammates can actually use.

## 📖 Step by step

### 1. The same endpoint, two frameworks

Flask (what you know):

```python
@app.post("/items")
def create_item():
    data = request.get_json()
    if not isinstance(data.get("price"), (int, float)):   # manual check
        return {"error": "price must be a number"}, 400
    ...
```

FastAPI:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float          # the type IS the validation

@app.post("/items")
def create_item(item: Item):
    return {"name": item.name, "price": item.price}
```

The FastAPI version has **no manual validation**: declaring `price: float` makes FastAPI reject `"price": "abc"` with a clear `422` automatically.

### 2. Type hints do double duty

The types you write for readability now also power:
- **Validation** — wrong type in → automatic `422` with a helpful message.
- **Docs** — every field shows up in the OpenAPI schema and `/docs`.
- **Editor help** — autocomplete and type-checking on `item.price`.

One declaration, three benefits. That's the core idea of FastAPI.

### 3. Automatic interactive docs

Run the app and open `/docs`: FastAPI shows an interactive **Swagger UI** listing every endpoint, its inputs and outputs, with a "Try it out" button. It's generated from your code, so it can't drift out of date. Frontend teammates use it to see exactly what to send.

### 4. Async support, built in

FastAPI lets you write `async def` handlers. When an endpoint mostly **waits** on I/O (calling another API, a database, an AI model), `async` lets the server handle other requests during the wait instead of blocking. For I/O-heavy or high-concurrency services this is a real throughput win. (You'll go deep on this in Week 2.)

```python
@app.get("/weather")
async def weather():
    data = await call_external_api()   # server serves others while waiting
    return data
```

### 5. So should you drop Flask?

No — both are excellent. Choose per project:

| Situation | Pick |
|---|---|
| Want auto validation + docs from types | **FastAPI** |
| Lots of async I/O (external APIs, AI calls) | **FastAPI** |
| Existing Flask app / team knows Flask | **Flask** is fine |
| Simple app, few endpoints | Either; use what you know |

- ✅ Reach for FastAPI when validation, docs, and async pay off.
- ✅ Keep using Flask where it already works — the concepts transfer.
- 🚫 Don't rewrite a working Flask app "just because" FastAPI is newer.

## ⚠️ Common mistakes

- Expecting FastAPI to be "Flask with faster runtime" — the real win is types → validation + docs, not raw speed.
- Writing manual validation anyway, duplicating what Pydantic already does.
- Using `async def` for CPU-heavy work (it doesn't help there; async is for I/O waits).
- Thinking you must abandon Flask — the HTTP/REST knowledge from Module 2 carries straight over.

:::revoshop
RevoShop's API is Flask + flask-smorest (which adds schema validation and docs on top of Flask). (1) Find where RevoShop validates input and generates docs — FastAPI would fold both into the type hints. (2) Pick one RevoShop endpoint and sketch its FastAPI version with a Pydantic model. (3) Which RevoShop calls are I/O-bound (Midtrans, DB) and could benefit from `async`?
:::

## 🏆 Best practices

- [ ] Let type hints + Pydantic do validation; don't hand-write checks FastAPI provides.
- [ ] Keep `/docs` as the living API contract for frontend teammates.
- [ ] Use `async def` for I/O-bound handlers; plain `def` is fine for simple/CPU work.
- [ ] Reuse your Module 2 REST knowledge — status codes, methods, and design are identical.
- [ ] Choose the framework per project need, not by novelty.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a Flask developer, using the plain-kitchen vs smart-order-screen analogy, what FastAPI automates. Then name the three things one type hint gives you in FastAPI.

## 📐 Design it

You're starting CareerPilot's new "AI service" as a fresh API that mostly calls an external LLM and the database. Decide whether FastAPI or Flask fits better and justify it (think validation, docs, and async I/O). Then sketch one endpoint `POST /suggestions` with its Pydantic request/response models.

:::quiz
Show a possible design

**Framework:** **FastAPI** fits well here — the service is I/O-bound (LLM + DB calls), so `async` improves throughput; and typed request/response models give automatic validation plus `/docs` the rest of the team can use.

**Endpoint sketch:**
```python
class SuggestionRequest(BaseModel):
    profile_id: int
    job_text: str

class SuggestionResponse(BaseModel):
    summary: str
    score: float

@app.post("/suggestions", response_model=SuggestionResponse)
async def suggest(req: SuggestionRequest):
    result = await call_llm(req.profile_id, req.job_text)
    return SuggestionResponse(summary=result.summary, score=result.score)
```

FastAPI validates the incoming JSON against `SuggestionRequest`, shapes the output with `SuggestionResponse`, and documents both in `/docs` — no manual validation or docs code.

**Rule shown:** pick FastAPI when typed validation, auto docs, and async I/O all pay off; the endpoint design (methods, status codes) is the same REST you learned in Module 2.
:::

### 📝 Self-review checklist

- [ ] Choice justified by validation/docs/async, not hype
- [ ] Request and response modeled with Pydantic
- [ ] Async used because the work is I/O-bound
- [ ] REST design consistent with Module 2

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m3/w1/01-first-fastapi" ai="no-ai" title="Your first FastAPI app"}
Build a minimal FastAPI app: a `GET /health` returning `{"status": "ok"}` and a `POST /greet` that takes a typed `{"name": str}` body and returns a greeting. The tests use FastAPI's `TestClient` and prove that a missing/invalid body is rejected with `422` automatically — no manual validation.
:::

:::hints
- `app = FastAPI()`; a Pydantic `class GreetIn(BaseModel): name: str`.
- `@app.get("/health")` returns a dict; `@app.post("/greet")` takes `body: GreetIn`.
- The test imports `app` and uses `TestClient(app)`; sending `{}` to `/greet` should give status `422` for free.
:::

## ✅ Quick check

:::quiz
In FastAPI, what three things does a single type hint like `price: float` give you?

Automatic validation (a non-number is rejected with `422`), documentation (the field appears in the OpenAPI schema and `/docs`), and editor support (autocomplete and type-checking). One declaration, three benefits — that's the point of FastAPI.
:::

:::quiz
When does `async def` actually help a FastAPI endpoint?

When the handler mostly **waits on I/O** — calling another API, a database, or an AI model — because the server can handle other requests during the wait. It doesn't help CPU-bound work, where the code is busy computing rather than waiting.
:::

## 📚 Keep learning

- [FastAPI: first steps](https://fastapi.tiangolo.com/tutorial/first-steps/)
- [FastAPI: features](https://fastapi.tiangolo.com/features/)
- [Flask vs FastAPI (official FAQ perspective)](https://fastapi.tiangolo.com/alternatives/)

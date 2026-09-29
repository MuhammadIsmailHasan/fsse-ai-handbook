---
title: "Automatic Docs & Validation"
summary: Where FastAPI's free superpowers come from — the OpenAPI schema and interactive /docs, response_model to shape and filter output, correct status codes, and HTTPException for clean errors, all from your types.
type: lesson
source: original
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: optional }
durationMinutes: 100
tags: [fastapi, openapi, docs, response-model, status-codes, errors]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- How FastAPI generates **OpenAPI** and the interactive `/docs`
- Shaping and filtering output with **`response_model`**
- Setting correct **status codes** (like `201 Created`)
- Returning clean errors with **`HTTPException`**
- Why the docs are always correct (they come from your code)

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **OpenAPI** | A standard machine description of your API | Deskripsi API standar |
| **Swagger UI** | The interactive `/docs` page | Halaman docs interaktif |
| **response_model** | The Pydantic model that shapes the output | Model bentuk output |
| **Status code** | The HTTP result number (200, 201, 404…) | Kode hasil HTTP |
| **HTTPException** | FastAPI's way to return an error response | Cara mengembalikan error |
| **Schema** | The described shape of a request/response | Bentuk yang dideskripsikan |

## 🧠 The big idea

`response_model` is a **filter at the exit door**. Your handler may hold a full user object (including a password hash), but the exit filter only lets through the fields you declared as safe to return. And `/docs` is a **live menu printed by the kitchen itself** — because it's generated from your code, it can never show a dish you no longer serve.

## ❓ Why it matters

Two real risks: **leaking data** (accidentally returning a password hash or internal field) and **stale docs** (hand-written docs that lie). FastAPI fixes both from your types: `response_model` guarantees the output shape and hides everything else, and the OpenAPI/`/docs` are generated from the code so they're always accurate. Correct status codes and clean errors make your API predictable for the frontend.

## 📖 Step by step

### 1. The docs are automatic

Every route + Pydantic model feeds an **OpenAPI** schema, served as interactive **Swagger UI** at `/docs` (and ReDoc at `/redoc`). No setup, always in sync with the code.

### 2. response_model shapes and filters output

Declare what an endpoint returns; FastAPI validates and **filters** the response to exactly those fields:

```python
class UserIn(BaseModel):
    name: str
    email: str
    password: str

class UserOut(BaseModel):      # note: no password
    id: int
    name: str
    email: str

@app.post("/users", response_model=UserOut)
def create_user(user: UserIn):
    record = save_user(user)              # record has a password hash
    return record                          # response_model strips it to id/name/email
```

Even though `record` has extra fields, the client only ever sees `UserOut`. Sensitive fields can't leak.

### 3. Correct status codes

Set the right code per action:

```python
from fastapi import status

@app.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: UserIn): ...
```

`201 Created` for creation, `200 OK` for reads/updates, `204 No Content` for a delete with no body. (Same REST codes from Module 2.)

### 4. Clean errors with HTTPException

When something is wrong, raise `HTTPException` — FastAPI turns it into a proper error response with your status and message:

```python
from fastapi import HTTPException

@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    user = find_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

Client gets `404` with `{"detail": "User not found"}` — predictable and documented.

### 5. Extra polish (optional)

- `tags=["users"]` groups endpoints in `/docs`.
- `summary`/`description` add human notes to the docs.
- `response_model_exclude_none=True` hides null fields.

### Choosing what to expose

| Concern | Do this |
|---|---|
| Hide sensitive fields | a separate `...Out` model via `response_model` |
| Signal success type | correct `status_code` (201/200/204) |
| Report a not-found / bad state | `raise HTTPException(...)` |
| Group & explain endpoints | `tags`, `summary` |

- ✅ Use a dedicated output model; never return raw DB objects.
- ✅ Set accurate status codes and raise `HTTPException` for errors.
- 🚫 Don't reuse the input model as the output (it may expose secrets).

## ⚠️ Common mistakes

- Returning the ORM/record object directly, leaking internal or sensitive fields.
- Reusing one model for input and output, so `password` slips into responses.
- Returning `200` for everything, even creation and errors.
- Returning error dicts with `200` instead of raising `HTTPException` with the right code.
- Writing separate docs by hand — they drift; let `/docs` be the source of truth.

:::revoshop
RevoShop returns JSON from Flask routes. (1) Is there any endpoint that could leak an internal field (password hash, internal flags)? A `response_model`/output schema would prevent it. (2) Which creations should return `201`, and which deletes `204`? (3) Where does RevoShop return an error — would `HTTPException` (or flask-smorest's abort) make the status code and message cleaner?
:::

## 🏆 Best practices

- [ ] Define separate input (`...In`) and output (`...Out`) models; expose only safe fields.
- [ ] Use `response_model` so responses are shaped and filtered automatically.
- [ ] Set accurate status codes (`201` create, `204` delete, etc.).
- [ ] Raise `HTTPException` for error cases with a clear `detail`.
- [ ] Treat `/docs` as the living contract; group with `tags` and add summaries.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain `response_model` with the filter-at-the-exit-door analogy, and `/docs` with the live-menu-printed-by-the-kitchen analogy. Then say why these prevent data leaks and stale docs.

## 📐 Design it

Design CareerPilot's `POST /users` (register) and `GET /users/{id}`. The stored user has `id, name, email, password_hash, is_admin`. Decide the input and output models, the status codes, and the error for a missing user — so no sensitive field ever leaks.

:::quiz
Show a possible design

```python
class UserIn(BaseModel):
    name: str
    email: str
    password: str

class UserOut(BaseModel):          # no password_hash, no is_admin
    id: int
    name: str
    email: str

@app.post("/users", response_model=UserOut, status_code=201)
def register(user: UserIn):
    record = create_user(user)     # has password_hash, is_admin
    return record                   # filtered to UserOut

@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    user = find_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

- **Input** `UserIn` includes `password`; **output** `UserOut` excludes `password_hash` and `is_admin`, so neither can leak even though the record holds them.
- **Status:** `201` on register, `200` on read.
- **Error:** missing user → `HTTPException(404)` with a clear detail.

**Rule shown:** separate In/Out models + `response_model` guarantee safe output; correct status codes and `HTTPException` make the API predictable.
:::

### 📝 Self-review checklist

- [ ] Separate input and output models; sensitive fields excluded from output
- [ ] `response_model` used on each returning endpoint
- [ ] Accurate status codes
- [ ] Errors via `HTTPException` with clear detail

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m3/w1/04-response-model" ai="no-ai" title="Shape output and handle errors"}
Build a `POST /users` that returns `201` with a `UserOut` (no password) even though the stored record contains a password, and a `GET /users/{id}` that returns the user or raises `404`. The tests prove the password never appears in responses and that a missing user gives `404`.
:::

:::hints
- Two models: `UserIn(name, email, password)` and `UserOut(id, name, email)`.
- `@app.post("/users", response_model=UserOut, status_code=201)` — return a dict/object that also has `password`; `response_model` strips it.
- Keep a module-level `dict` as a fake store; `GET` raises `HTTPException(status_code=404, detail=...)` when the id is absent.
:::

## ✅ Quick check

:::quiz
How does `response_model` prevent leaking sensitive fields?

FastAPI validates and filters the response to exactly the fields declared in the `response_model`, dropping everything else. So even if your handler returns a full record with a `password_hash`, the client only receives the safe fields you listed — leaks are impossible by construction.
:::

:::quiz
Why are FastAPI's `/docs` never out of date?

Because they're generated from your actual routes and Pydantic models (the OpenAPI schema), not written by hand. If you change an endpoint or model, the docs change with it automatically, so they can't drift from the real behavior.
:::

## 📚 Keep learning

- [FastAPI: response model](https://fastapi.tiangolo.com/tutorial/response-model/)
- [FastAPI: handling errors](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [FastAPI: metadata & docs URLs](https://fastapi.tiangolo.com/tutorial/metadata/)

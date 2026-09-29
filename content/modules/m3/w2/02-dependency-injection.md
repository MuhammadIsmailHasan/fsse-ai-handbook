---
title: "Dependency Injection"
summary: FastAPI's Depends system — declare what an endpoint needs (a DB session, the current user, settings) and FastAPI builds it, injects it, and cleans it up, removing duplicated setup and making handlers trivial to test.
type: lesson
source: original
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: optional }
durationMinutes: 110
tags: [fastapi, dependency-injection, depends, testing, auth]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What **dependency injection** means and why FastAPI leans on it
- Using `Depends(...)` to provide shared setup to endpoints
- Dependencies with **`yield`** for setup + cleanup (like a DB session)
- Building a **`get_current_user`** dependency for auth
- Why DI makes handlers small, reusable, and easy to test

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Dependency** | Something an endpoint needs to do its job | Sesuatu yang dibutuhkan endpoint |
| **Injection** | The framework supplies it for you | Framework menyediakannya |
| **Depends** | FastAPI's way to declare a dependency | Cara mendeklarasikan dependency |
| **yield dependency** | Runs setup, then cleanup after the response | Setup lalu bersih-bersih |
| **Reuse** | One dependency used by many endpoints | Satu dipakai banyak endpoint |
| **Override** | Swap a dependency in tests | Menukar dependency saat tes |

## 🧠 The big idea

Dependency injection is a **restaurant supply chain**. A chef (your endpoint) doesn't drive to the market for ingredients before every dish — they just say "I need fresh vegetables" and the supplier delivers them, and takes back the crates afterward. The chef focuses on cooking. In FastAPI you declare "I need a DB session / the current user", and the framework builds it, hands it over, and cleans up.

## ❓ Why it matters

Without DI, every handler repeats the same setup: open a DB session, read and verify the auth token, load settings — and remembers to close/clean up. That's duplicated, error-prone, and hard to test. FastAPI's `Depends` centralizes each concern in one function, injects it wherever declared, and (with `yield`) guarantees cleanup. Bonus: in tests you can **override** a dependency to inject a fake, so handlers test in isolation.

## 📖 Step by step

### 1. A simple dependency

A dependency is just a function whose return value is injected:

```python
from fastapi import Depends

def pagination(page: int = 1, limit: int = 20) -> dict:
    return {"page": page, "limit": limit}

@app.get("/items")
def list_items(pg: dict = Depends(pagination)):
    return pg     # FastAPI called pagination() and injected the result
```

Now every list endpoint reuses the same paging logic by declaring `Depends(pagination)`.

### 2. Dependencies with yield (setup + cleanup)

For resources that must be opened and closed — a database session — use `yield`:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db            # hand the session to the endpoint
    finally:
        db.close()          # always cleaned up, even on error

@app.get("/users/{id}")
def read_user(id: int, db = Depends(get_db)):
    return db.get(User, id)
```

FastAPI runs the code up to `yield` before the handler, and the code after `yield` once the response is sent — so you never leak a session.

### 3. Auth as a dependency: get_current_user

The classic use — turn a token into the current user, and reject if missing/invalid:

```python
from fastapi import Header, HTTPException

def get_current_user(authorization: str | None = Header(default=None)):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.removeprefix("Bearer ")
    user = verify_token(token)                # decode & look up
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

@app.get("/me")
def me(user = Depends(get_current_user)):
    return {"id": user.id, "name": user.name}
```

Any protected endpoint just adds `user = Depends(get_current_user)` — the auth check lives in one place.

### 4. Dependencies can depend on dependencies

`get_current_user` can itself `Depends(get_db)`. FastAPI resolves the whole chain for you, in order, and caches a dependency's result within a single request.

### 5. Overriding in tests

In tests, replace a real dependency with a fake:

```python
app.dependency_overrides[get_current_user] = lambda: FakeUser(id=1)
```

Now the endpoint runs with a fake user — no real tokens or DB needed. This is why DI makes code so testable.

### Choosing when to make a dependency

| Repeated concern | Make it a dependency? |
|---|---|
| DB session (open/close) | ✅ yes (`yield`) |
| Current authenticated user | ✅ yes |
| Pagination / common query params | ✅ yes |
| Settings / config object | ✅ yes |
| One-off logic used by a single endpoint | 🚫 keep it inline |

- ✅ Extract shared setup (DB, auth, settings, paging) into dependencies.
- ✅ Use `yield` for anything that needs cleanup.
- ✅ Override dependencies in tests to inject fakes.
- 🚫 Don't turn trivial one-endpoint logic into a dependency just for style.

## ⚠️ Common mistakes

- Opening a DB session inside each handler instead of a `yield` dependency (leaks, duplication).
- Repeating the auth check in every endpoint rather than one `get_current_user`.
- Forgetting the `finally` (or `try/finally`) so cleanup doesn't run on errors.
- Not using `dependency_overrides`, then needing real tokens/DB in every test.
- Putting heavy work in a dependency that runs on every request unnecessarily.

:::revoshop
RevoShop (Flask) uses decorators/before-request hooks for auth and a session per request. (1) Which repeated setup (DB session, current user, RBAC check) would become FastAPI dependencies? (2) Sketch `get_current_user` for RevoShop returning the logged-in user or `401`. (3) How would `dependency_overrides` let you test a protected endpoint without a real JWT?
:::

## 🏆 Best practices

- [ ] Move DB sessions, auth, settings, and paging into reusable dependencies.
- [ ] Use `yield` + `finally` for resources that must be cleaned up.
- [ ] Build one `get_current_user` and reuse it on every protected route.
- [ ] Override dependencies in tests to inject fakes instead of real services.
- [ ] Keep dependencies focused; let FastAPI resolve dependency chains.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain dependency injection with the restaurant-supply-chain analogy. Then say what a `yield` dependency guarantees that a plain one doesn't.

## 📐 Design it

Design the dependencies for CareerPilot's API: a database session, the current user from a Bearer token, and an "admin only" guard for admin endpoints. Show how a normal endpoint and an admin endpoint each declare what they need, and how you'd test the admin endpoint without a real token.

:::quiz
Show a possible design

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(db = Depends(get_db), authorization: str | None = Header(default=None)):
    user = user_from_token(db, authorization)
    if user is None:
        raise HTTPException(401, "Not authenticated")
    return user

def require_admin(user = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(403, "Admin only")
    return user

@app.get("/me")
def me(user = Depends(get_current_user)):
    return {"id": user.id}

@app.get("/admin/stats")
def stats(admin = Depends(require_admin), db = Depends(get_db)):
    return compute_stats(db)
```

- `get_db` (yield) opens/closes the session; `get_current_user` depends on it and the header; `require_admin` builds on `get_current_user` and adds the role check (`403` if not admin).
- **Testing the admin route:** `app.dependency_overrides[require_admin] = lambda: FakeAdmin()` — the endpoint runs with a fake admin, no real token or DB needed.

**Rule shown:** layer dependencies (db → current user → admin guard), declare only what each endpoint needs, and override in tests for isolation.
:::

### 📝 Self-review checklist

- [ ] DB session is a `yield` dependency with cleanup
- [ ] Auth and role checks are dependencies, not repeated code
- [ ] Endpoints declare only what they need
- [ ] Tests override dependencies to inject fakes

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m3/w2/02-depends" ai="no-ai" title="Auth and DB via Depends"}
Build a `get_current_user` dependency that reads a `Bearer` token from the `Authorization` header (rejecting missing/invalid with `401`) and a protected `GET /me` that returns the user. The tests hit `/me` with no token (`401`), a bad token (`401`), a good token (`200`), and also use `dependency_overrides` to inject a fake user.
:::

:::hints
- A tiny token→user map, e.g. `{"tok-ismail": {"id": 1, "name": "Ismail"}}`.
- `get_current_user(authorization: str | None = Header(default=None))`: require it starts with `"Bearer "`, look up the token, raise `HTTPException(401, ...)` if missing/unknown.
- `@app.get("/me")` with `user = Depends(get_current_user)` returns the user dict.
- One test sets `app.dependency_overrides[get_current_user] = lambda: {"id": 99, "name": "Fake"}` then calls `/me`.
:::

## ✅ Quick check

:::quiz
What does a `yield` dependency give you that a plain (return) dependency does not?

Guaranteed cleanup: the code before `yield` runs as setup, the value is injected, and the code after `yield` (in a `finally`) runs once the response is sent — even if the handler errored. That's how a DB session is reliably opened and always closed.
:::

:::quiz
Why does dependency injection make endpoints easy to test?

Because the endpoint doesn't build its own DB session or user — it declares them via `Depends`, so in tests you can `dependency_overrides` them with fakes. The handler runs in isolation with no real database, tokens, or network.
:::

## 📚 Keep learning

- [FastAPI: dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [FastAPI: dependencies with yield](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/)
- [FastAPI: testing with dependency overrides](https://fastapi.tiangolo.com/advanced/testing-dependencies/)

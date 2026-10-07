---
title: "Testing with pytest & TestClient"
summary: Test a FastAPI app without starting a server — call it with TestClient, swap the database for a fresh fake with dependency_overrides, share setup with fixtures, and test the error paths, not just the happy path.
type: lesson
source: original
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: optional }
durationMinutes: 120
tags: [fastapi, testing, pytest, testclient, dependency-overrides]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Call your API from a test with **`TestClient`** — no server to start
- Swap a real dependency for a fake one with **`dependency_overrides`**
- Share setup between tests with a **fixture**
- Keep tests **isolated** so one test never changes another
- Test the **error paths**, not only the happy path

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **TestClient** | A fake browser that calls your app directly | Klien uji |
| **Fixture** | Reusable setup that pytest gives to tests | Persiapan yang dipakai ulang |
| **Override** | Replace a real dependency with a fake for one test | Menimpa dependency |
| **Fake** | A simple stand-in that behaves like the real thing | Pengganti sederhana |
| **Isolation** | Each test starts from a clean state | Tiap tes mulai bersih |
| **Assertion** | A check that must be true for the test to pass | Pernyataan cek |
| **Happy path** | The case where everything goes right | Jalur sukses |

## 🧠 The big idea

Testing an API is like a **driving-school practice track**. You do not learn on the real highway with real traffic. You use a closed track (`TestClient`), with cones you can place anywhere (`dependency_overrides`), and you reset the cones before every lesson (isolation). The car is real. The road is safe.

## ❓ Why it matters

Without tests, every change is a guess. You edit one endpoint and quietly break another, and you find out from a user. With fast tests you change code with confidence. Tests that share state are worse than no tests: one test passes only because another ran first, and the suite fails at random. Good API tests are quick, isolated and cover the failures too, because that is where real bugs hide.

## 📖 Step by step

### 1. Call the app with `TestClient`

`TestClient` runs your app in the same process. No port, no `uvicorn`. It feels like `requests` or `httpx`.

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

Check the **status code** and the **body**. Both are part of your API's promise.

### 2. Test writes and errors

```python
def test_create_note():
    r = client.post("/notes", json={"text": "buy milk"})
    assert r.status_code == 201
    assert r.json()["text"] == "buy milk"

def test_missing_note_is_404():
    assert client.get("/notes/999").status_code == 404

def test_bad_body_is_422():
    assert client.post("/notes", json={}).status_code == 422
```

The last test is free: FastAPI validates the body for you, and you only confirm it. Always test at least one failure for each endpoint.

### 3. Swap the database with `dependency_overrides`

Your endpoint asks for a repository with `Depends(get_repo)`. In a test you do not want the real one. Replace it:

```python
def test_with_fake_repo():
    fake = NoteRepo()
    app.dependency_overrides[get_repo] = lambda: fake
    try:
        client = TestClient(app)
        client.post("/notes", json={"text": "a"})
        assert fake.all() == [{"id": 1, "text": "a"}]
    finally:
        app.dependency_overrides.clear()   # always clean up
```

This is the payoff of dependency injection from last week: the app never knows it is being tested. The `finally` matters. `dependency_overrides` is **global** to the app, so a leftover override leaks into the next test.

### 4. Put the setup in a fixture

Repeating that `try/finally` is noisy. A **fixture** does it once. Code before `yield` is setup, code after is cleanup, and pytest runs the cleanup even if the test fails.

```python
import pytest

@pytest.fixture
def client():
    fake = NoteRepo()                              # fresh for every test
    app.dependency_overrides[get_repo] = lambda: fake
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_create_note(client):                      # pytest injects it by name
    assert client.post("/notes", json={"text": "a"}).status_code == 201
```

Put shared fixtures in `conftest.py` and pytest finds them in every test file next to it.

### 5. Keep tests isolated

Each test must work **alone and in any order**. A fresh fake per test gives you that. The trap is the shared, process-wide object (a module-level list or repository). If test A adds a note and test B expects an empty list, B passes only when it runs first.

A quick check: run one test by itself (`pytest -k test_name`) and run the suite in a different order. If results change, you have shared state.

### 6. Test the real database too, but fewer times

A fake is fast, but it can differ from the real database. Use both:

| Kind | Database | Speed | Use for |
|---|---|---|---|
| Unit/API test | fake or in-memory SQLite | very fast | most tests, business rules, error paths |
| Integration test | a real PostgreSQL (e.g. in Docker) | slower | a few tests: queries, constraints, transactions |

Many tests on the fast layer, a few on the real one. This is the **test pyramid**.

### When to use what

| Need | Do this |
|---|---|
| Call an endpoint | `TestClient(app)` |
| Replace the DB or the logged-in user | `app.dependency_overrides[dep] = fake` |
| Reuse setup | a fixture, `yield` for cleanup |
| Same test, many inputs | `@pytest.mark.parametrize` |
| Check a real query or constraint | a few integration tests on real PostgreSQL |

## ⚠️ Common mistakes

- Forgetting to clear `dependency_overrides`, so one test changes the next.
- Testing only the happy path — no 404, 401 or 422.
- A module-level shared repository that makes tests depend on order.
- Asserting only the status code and never the body.
- Mocking so much that the test checks the mock, not your code.

:::revoshop
Open RevoShop's `tests/` folder. (1) How does it get a test client and a clean database for each test — which fixture does that? (2) Find one test for a failure case (401, 403 or 404). (3) How would you do the same in FastAPI: what replaces Flask's test client, and what replaces swapping the database config?
:::

## 🏆 Best practices

- [ ] Give every test its own fresh state (a fixture that builds a new fake or database).
- [ ] Always clean up overrides, with `yield` in a fixture or `try/finally`.
- [ ] Test the failure cases: missing item, no token, wrong role, bad input.
- [ ] Assert on both the status code and the response body.
- [ ] Keep most tests fast (fake or in-memory) and a few on a real database.
- [ ] Name tests as sentences: `test_missing_note_is_404`.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain `TestClient`, `dependency_overrides` and a fixture using the driving-school-track analogy. Then say why a leftover override is a bug.

## 📐 Design it

Plan the tests for CareerPilot's `POST /applications` endpoint (the user saves a job they applied to). List the test cases, what each one asserts, which dependencies you would override, and which one or two tests you would run against a real PostgreSQL.

:::quiz
Show a possible design

- **Happy path:** valid body → `201`, body has an `id` and the same fields; the fake repo now holds one application.
- **Validation:** missing `company` → `422`; empty `title` → `422`.
- **Auth:** no token → `401`; a token for a different user cannot read this application → `404` or `403`.
- **Duplicate:** same job saved twice → `409` (or the rule you chose).
- **Overrides:** `get_repo` → a fresh fake per test; `get_current_user` → a fixed fake user, so most tests need no real token.
- **Real PostgreSQL (integration):** one test for the unique constraint and one for a transaction that rolls back on error.
- **Isolation:** all of it in fixtures with `yield` cleanup.

**Rule shown:** many fast, isolated tests on fakes; a few on the real database; always the failure paths.
:::

### 📝 Self-review checklist

- [ ] Each test builds its own state and cleans up
- [ ] Failure cases are tested, not only success
- [ ] Both status code and body are asserted
- [ ] Only a few tests need a real database

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m3/w3/01-testclient" ai="no-ai" title="A test client with a fresh repository"}
`notes_app.py` is a finished notes API that reads notes through a shared `get_repo` dependency. Write `client_with_fresh_repo` in `notes_testing.py`: a context manager that overrides `get_repo` with a fresh `NoteRepo()` (or one you pass in), yields a `TestClient`, and **always** removes the override afterward. The tests check isolation between tests and the cleanup, even when a test body fails.
:::

:::hints
- `@contextmanager` turns a generator into a `with` block: code before `yield` is setup, after it is cleanup.
- `app.dependency_overrides[get_repo] = lambda: fake` — the lambda returns the same `fake` each call.
- Put the `yield` inside `try:` and the `app.dependency_overrides.clear()` in `finally:` so it runs even if the test raises.
- Use `repo if repo is not None else NoteRepo()`, not `repo or NoteRepo()` — an empty repo should still count as given.
:::

## ✅ Quick check

:::quiz
Why must you clear `app.dependency_overrides` after a test?

`dependency_overrides` belongs to the app object, which lives for the whole test run. If you leave an override in place, the next test silently uses the fake too, and results depend on test order. Clearing it (in a fixture's cleanup or a `finally`) keeps every test isolated.
:::

:::quiz
Why is testing only the happy path not enough?

Most real bugs live in the failure cases: missing items, bad input, no login, the wrong role. These paths are also the ones users hit by accident. A test for each failure (404, 401, 422) proves the API answers clearly instead of crashing.
:::

## 📚 Keep learning

- [FastAPI: Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [FastAPI: Testing dependencies with overrides](https://fastapi.tiangolo.com/advanced/testing-dependencies/)
- [pytest: How to use fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)

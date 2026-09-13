# M2 · W6 · 02 — Integration Tests for a Flask API

> 🚫🤖 **No-AI** · ⏱️ ~90 min · needs the exercise database (`docker compose up -d`)

`api.py` (a CareerPilot applications API) is **correct** — read its docstring for the full contract. Provided: `app.py` (`create_app(database_url, api_key)`) and `models.py`.

Write **`test_api.py`**: integration tests that call the real app with Flask's test client against PostgreSQL.

The grader runs your tests against `api.py` (must **pass**) and against 11 buggy copies in `mutants/` (each must make your tests **fail**). 🙈 Don't open `mutants/` until you've tried.

```bash
cd exercises
uv run pytest m2/w6/02-testing-flask-endpoints/test_api.py -v
uv run pytest m2/w6/02-testing-flask-endpoints/test_grader.py -v
```

Checklist of what to cover:
- status code **and** response body for success and each error
- that writes are **persisted** (read them back with a separate request)
- auth: missing key **and** wrong key
- every allowed and a few forbidden status transitions
- that a failed request **didn't change** anything

⚠️ **Fixture trap:** the starter fixture keeps one app context open while requests run. Then all requests share one SQLAlchemy session, and a change that was only flushed (never committed) still looks saved. If a "not committed" mutant survives, fix your fixture: push the app context only for setup and teardown.

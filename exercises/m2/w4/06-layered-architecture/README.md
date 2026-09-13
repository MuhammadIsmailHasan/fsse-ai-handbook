# M2 · W4 · 06 — Split a Feature into Layers

> 🚫🤖 **No-AI** · ⏱️ ~75 min · needs the exercise database (`docker compose up -d`)

Provided in `careerpilot/`: the app factory (`__init__.py`), `errors.py`, `models.py`, and `repositories.py`. You write **`services.py`** and **`routes.py`**.

## `services.py` — `ApplicationService(repository, clock)`
`repository` has `get_for_user`, `list_for_user`, `add`, `commit`. `clock()` returns the current `datetime`. **No Flask or SQLAlchemy imports.**

| Method | Behavior |
|---|---|
| `create(user_id, data)` | `data` has `company` and `role_title` (non-blank strings, stripped). Otherwise raise `ValidationFailed({field: "required"})` for **all** missing fields. Creates an `Application` with status `"applied"`, `created_at` and `updated_at` = `clock()`; calls `add` then `commit` **once**; returns it |
| `list(user_id)` | the repository's list |
| `change_status(user_id, application_id, status)` | unknown/other user's → `ApplicationNotFound`. Allowed: `applied → interview/rejected`, `interview → offer/rejected`, `offer → accepted/declined`; otherwise `InvalidTransition`. Sets `updated_at = clock()`, commits once, returns the application |

## `routes.py` — blueprint `applications` (`/api/v1/applications`)
The current user id comes from the `X-User-Id` header (real auth arrives in Week 5). Missing/invalid header → `401 {"error": {"code": "unauthorized", ...}}`.

| Route | Response |
|---|---|
| `POST ""` | `201 {"data": application}` |
| `GET ""` | `200 {"data": [applications]}` |
| `POST "/<int:application_id>/status"` with `{"status": "..."}` | `200 {"data": application}` |

An application serializes as `{"id", "company", "role_title", "status"}`. Routes build the service with `SqlApplicationRepository()` and a UTC clock. **Routes must not import `db`, `select` or `sqlalchemy`.** Domain errors are mapped to HTTP by the provided error handler — don't catch them in routes.

```bash
cd exercises
uv run pytest m2/w4/06-layered-architecture
```

# M2 · W4 · 02 — Queries and Units of Work with SQLAlchemy 2.0

> 🚫🤖 **No-AI** · ⏱️ ~60 min · needs the exercise database (`docker compose up -d`)

`models.py` and `app.py` are provided. Implement `repository.py` using **SQLAlchemy 2.0 style** (`select`, `db.session.scalars/execute/get`) — not the legacy `Model.query`.

| Function | Behavior |
|---|---|
| `get_for_user(application_id, user_id)` | the `Application` or `None` (other users' applications → `None`) |
| `list_applications(user_id, statuses=None, page=1, per_page=20)` | `(items, total)`: newest `created_at` first, then `id` desc; `statuses` optional list filter; `total` counts **all** matches |
| `count_by_status(user_id)` | `dict[str, int]` |
| `create_application_with_company(user_id, company_name, role_title)` | find company by name **case-insensitively** or create it; create the application; **one commit**; returns the application. If the user already has an application for that company + role (unique constraint), roll back and raise `DuplicateApplication` — the company created in this call must **not** be saved either |

Rules: `list_applications` must run **exactly 2** SQL statements (items + count). Don't use `Model.query`.

```bash
cd exercises
uv run pytest m2/w4/02-sqlalchemy
```

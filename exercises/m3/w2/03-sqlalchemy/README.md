# Module 3 · W2 · SQLAlchemy 2.0 CRUD

> 🚫🤖 **No-AI** · ⏱️ ~30 min

Use SQLAlchemy 2.0 against an **in-memory SQLite** database (no server needed). Implement three functions on a `User` model:

| Function | 2.0 API |
|---|---|
| `create_user(session, name, email)` | `add` + `commit` + `refresh` |
| `get_user(session, user_id)` | `session.get(User, id)` |
| `list_users_by_domain(session, domain)` | `select(User).where(...)` + `scalars` |

The tests spin up a fresh SQLite session, insert users, and check the queries.

```bash
cd exercises
uv run pytest m3/w2/03-sqlalchemy
```

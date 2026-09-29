# Module 3 · W1 · Your First FastAPI App

> 🚫🤖 **No-AI** · ⏱️ ~25 min

Build two endpoints in `app.py`:

| Endpoint | Returns |
|---|---|
| `GET /health` | `{"status": "ok"}` |
| `POST /greet` (body `{"name": str}`) | `{"message": "Hello, <name>!"}` |

Because `/greet` takes a Pydantic model, FastAPI validates the body automatically — the tests prove a missing `name` is rejected with `422` without any hand-written checks.

```bash
cd exercises
uv run pytest m3/w1/01-first-fastapi
```

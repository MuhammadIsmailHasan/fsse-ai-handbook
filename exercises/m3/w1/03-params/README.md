# Module 3 · W1 · Path, Query & Body

> 🚫🤖 **No-AI** · ⏱️ ~25 min

Build three endpoints in `app.py`, one for each kind of input:

| Endpoint | Input kind |
|---|---|
| `GET /items/{item_id}` | path param (`int`) |
| `GET /items?q=&page=` | query params with defaults |
| `POST /items` (body `{"name","price"}`) | Pydantic body |

The tests check routing, query defaults, `422` on a bad path type, and body validation — all automatic from your type hints.

```bash
cd exercises
uv run pytest m3/w1/03-params
```

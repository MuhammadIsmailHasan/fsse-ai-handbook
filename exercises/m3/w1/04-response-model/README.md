# Module 3 · W1 · Shape Output & Handle Errors

> 🚫🤖 **No-AI** · ⏱️ ~25 min

Two endpoints in `app.py`:

- `POST /users` → `201`, returns a `UserOut` (**no password**) even though the stored record keeps one — `response_model` filters the output.
- `GET /users/{id}` → the user, or `404` via `HTTPException` when missing.

The tests prove the password never appears in any response and that a missing user returns `404` with a clear detail.

```bash
cd exercises
uv run pytest m3/w1/04-response-model
```

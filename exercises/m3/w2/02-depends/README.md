# Module 3 · W2 · Auth via Depends

> 🚫🤖 **No-AI** · ⏱️ ~25 min

Build a `get_current_user` dependency that reads a `Bearer` token from the `Authorization` header, and a protected `GET /me` that returns the user.

| Case | Result |
|---|---|
| No / malformed header | `401` |
| Unknown token | `401` |
| Known token | the user dict |

The tests cover all three, plus one that uses `app.dependency_overrides` to inject a fake user — showing why DI makes protected endpoints easy to test.

```bash
cd exercises
uv run pytest m3/w2/02-depends
```

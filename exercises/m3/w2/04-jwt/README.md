# Module 3 · W2 · Sign & Verify a Token

> 🚫🤖 **No-AI** · ⏱️ ~30 min

Build a minimal JWT-style token with the standard library — no PyJWT.

| Function | Does |
|---|---|
| `sign(payload, secret)` | `base64(payload).base64(hmac_signature)` |
| `verify(token, secret, now)` | Recompute the signature, check `exp`; return payload or raise `TokenError` |

The tests prove the important guarantees: a **tampered** payload, a **wrong secret**, an **expired** token, and a **malformed** token are all rejected — while a valid, unexpired token round-trips. `now` is passed in so tests are deterministic.

```bash
cd exercises
uv run pytest m3/w2/04-jwt
```

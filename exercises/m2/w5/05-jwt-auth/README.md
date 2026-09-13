# M2 · W5 · 05 — Register, Login, Refresh and Logout

> 🚫🤖 **No-AI** · ⏱️ ~90 min · needs the exercise database (`docker compose up -d`)

Provided: `app.py` (factory; config with `JWT_SECRET_KEY`, 15-min access / 30-day refresh expiry; `ApiError` handler; calls `auth.init_auth(app)`; registers `auth.auth_bp`) and `models.py` (`User`, `RevokedToken`).

Implement `auth.py`.

## `init_auth(app)`
Create `JWTManager(app)` and register **JSON 401 responses** `{"error": {"code": ..., "message": ...}}`:

| Situation | code |
|---|---|
| no/invalid Authorization header | `token_missing` |
| expired token | `token_expired` |
| malformed/tampered token, or wrong token type | `token_invalid` |
| token's `jti` is in `RevokedToken` | `token_revoked` |
| token's user no longer exists | `user_not_found` |

## Blueprint `auth` (prefix `/api/v1/auth`)
User JSON: `{"id", "email", "full_name", "role"}` — never the password hash.

| Endpoint | Behavior |
|---|---|
| `POST /register` `{email, password, full_name}` | email stripped + lowercased, must contain `@` and a `.` after it; password ≥ 12 chars; full_name 1–100 → else `ApiError(422, "validation_failed", ..., fields)`; email already registered (any case) → `409 email_taken`; store a **hash**; `201 {"data": user}` |
| `POST /login` `{email, password}` | `200 {"access_token", "refresh_token", "token_type": "Bearer", "expires_in": 900}`; wrong password **or** unknown email → `401 invalid_credentials` with the **same** message |
| `GET /me` (access token) | `200 {"data": user}` |
| `POST /refresh` (refresh token) | `200 {"access_token", "token_type": "Bearer", "expires_in": 900}` |
| `POST /logout` (access token) | revoke this access token → `204` |
| `POST /logout-refresh` (refresh token) | revoke this refresh token → `204` |

Access tokens: `sub` = user id **as a string**, extra claim `role`.

```bash
cd exercises
uv run pytest m2/w5/05-jwt-auth
```

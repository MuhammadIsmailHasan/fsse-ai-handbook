# M2 · W5 · 02 — Correct Writes with Idempotency Keys

> 🚫🤖 **No-AI** · ⏱️ ~90 min · needs the exercise database (`docker compose up -d`)

Provided: `app.py` (factory + `ApiError` handler), `models.py` (`Note`, `IdempotencyRecord`). Implement `notes.py` — blueprint `notes`, prefix `/api/v1/notes`.

**Current user:** header `X-User-Id` (digits) → otherwise `ApiError(401, "unauthorized", …)`.
**Serialized note:** `{"id", "title", "body", "pinned"}`.

### Fields
| Field | Rules |
|---|---|
| `title` | string, stripped, 1–120 chars, **not nullable** |
| `body` | string or `null` |
| `pinned` | boolean |
| `id`, `user_id`, `created_at`, `updated_at` | read-only → field error `"read-only field"` |
| anything else | field error `"unknown field"` |

Validation problems → `ApiError(422, "validation_failed", …, fields)` with **all** field errors. Body that isn't a JSON object → `ApiError(400, "invalid_json", …)`.

### Endpoints
| Endpoint | Behavior |
|---|---|
| `POST ""` | `title` required; `body` default `null`; `pinned` default `false` → **201**, `{"data": note}`, header `Location: /api/v1/notes/<id>` |
| `GET "/<int:note_id>"` | 200; missing **or other user's** → `404 note_not_found` |
| `PUT "/<int:note_id>"` | full replacement: `title` required; missing `body` → `null`; missing `pinned` → `false` → 200 |
| `PATCH "/<int:note_id>"` | only sent fields change; `body: null` clears it; `title: null` → field error `"cannot be null"`; empty object → `422 no_fields` → 200 |
| `DELETE "/<int:note_id>"` | **204** empty body; deleting again → 404 |

### Idempotency (POST only)
Optional header `Idempotency-Key` (1–100 chars):
- first request: create the note and store `(user_id, key, request_hash, status_code, response_json)` in `IdempotencyRecord` **in the same commit**
- same user + key + **same body** → return the stored status and JSON (and the same `Location`), without creating anything
- same user + key + **different body** → `ApiError(422, "idempotency_key_reused", …)`
- the same key used by **another user** is independent

```bash
cd exercises
uv run pytest m2/w5/02-write-methods
```

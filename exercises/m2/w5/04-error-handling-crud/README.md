# M2 · W5 · 04 — A Complete CRUD Resource with Production-Grade Errors

> 🚫🤖 **No-AI** · ⏱️ ~90 min · needs the exercise database (`docker compose up -d`)

Provided: `app.py` (factory that calls `errors.register_error_handlers(app)` and registers `companies.companies_bp`) and `models.py` (`Company` with a unique index on `lower(name)`; `Job` referencing companies with `ON DELETE RESTRICT`).

## `errors.py`
- `AppError(Exception)` with class attributes `status_code`, `code`; subclasses: `NotFound` (404, `not_found`), `Conflict` (409, `conflict`), `ValidationFailed(fields)` (422, `validation_failed`)
- `register_error_handlers(app)`:
  - **request ids**: before each request set `g.request_id` from header `X-Request-ID` if it matches `^[A-Za-z0-9-]{1,64}$`, else a new `uuid4().hex`; after each request add response header `X-Request-ID`
  - `AppError` → `{"error": {"code", "message", "request_id"[, "fields"]}}` with its status
  - `HTTPException` → same shape; code = the name in snake_case (`not_found`, `method_not_allowed`)
  - any other exception → `500`, code `internal_error`, message exactly `"Something went wrong"`; log it with `app.logger.exception` and a message containing the request id

## `companies.py` — blueprint `companies`, prefix `/api/v1/companies`
Serialized company: `{"id", "name", "website"}`.

| Endpoint | Behavior |
|---|---|
| `GET ""` | `200 {"data": [...]}` sorted by name A→Z (case-insensitive); optional `q` → name contains `q` (case-insensitive) |
| `GET "/<int:id>"` | `200`; missing → `NotFound` with code `company_not_found` |
| `POST ""` | `name` required (1–200 after strip); `website` optional, `null` or a string starting with `https://`; unknown fields rejected → `ValidationFailed`; duplicate name (any case) → **409 `company_exists`**; success **201** + `Location` |
| `PATCH "/<int:id>"` | same field rules, only sent fields change; duplicate → 409 `company_exists` |
| `DELETE "/<int:id>"` | **204**; jobs still reference it → **409 `company_in_use`**; missing → 404 |

Bad JSON body → `ValidationFailed` with `fields: {"body": "must be a JSON object"}`.

```bash
cd exercises
uv run pytest m2/w5/04-error-handling-crud
```

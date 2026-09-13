# M2 · W5 · 03 — Schemas, Error Paths and Status Codes

> 🚫🤖 **No-AI** · ⏱️ ~75 min · no database needed

Implement in `schemas.py` (marshmallow 4) and `api.py` (Flask).

### `SalarySchema`
- `min`, `max`: required integers ≥ 0 · `currency`: one of `IDR`, `USD`, `SGD`, default `"IDR"`
- `max < min` → error on **`max`**: `"must be greater than or equal to min"` — reported **even if another salary field (like `currency`) is also invalid** (hint: look up `skip_on_field_errors`)

### `ApplicationCreateSchema`
| Field | Rules |
|---|---|
| `company` | required string, 1–200 after stripping |
| `role_title` | required string, 1–200 after stripping |
| `status` | one of `wishlist`, `applied`, `interview`; default `"applied"` |
| `applied_on` | optional date (`YYYY-MM-DD`) or `null`; default `None`; not in the future → `"can't be in the future"` |
| `contact_email` | optional email or `null`; default `None`; lowercased |
| `salary` | optional nested `SalarySchema` or `null`; default `None` |
| `tags` | optional list of strings (each 1–30), at most 10, unique ignoring case → `"tags must be unique"`; stored lowercase; default `[]` |

- All string values stripped **before** validation (`@pre_load`); unknown fields rejected
- `ApplicationCreateSchema(partial=True)` is used for updates

### `ApplicationResponseSchema`
Dumps `id`, `company`, `role_title`, `status`, `applied_on` (ISO string), `salary`, `tags` — and **never** `user_id` or `private_notes`.

### `flatten_errors(messages) -> dict[str, str]`
Nested marshmallow messages → dot paths with the **first** message: `{"salary": {"max": ["…"]}}` → `{"salary.max": "…"}`; list items → `"tags.1"`; `_schema` → `"body"`.

### `api.py` — `create_app()` with `POST /applications`
- body not JSON **object** → `400 {"error": {"code": "invalid_json", …}}`
- validation errors → `422 {"error": {"code": "validation_failed", "message": "Some fields are invalid", "fields": flatten_errors(...)}}`
- success → `201 {"data": ApplicationResponseSchema().dump({**data, "id": 1, "user_id": 7, "private_notes": "secret"})}`

```bash
cd exercises
uv run pytest m2/w5/03-validation
```

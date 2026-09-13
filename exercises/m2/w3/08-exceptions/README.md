# M2 · W3 · 08 — Error Hierarchy and a Safe Boundary

> 🚫🤖 **No-AI** · ⏱️ ~50 min

Implement in `errors.py`:

### Hierarchy
| Class | Parent | `status_code` | `code` |
|---|---|---|---|
| `AppError` | `Exception` | 500 | `"internal_error"` |
| `NotFound` | `AppError` | 404 | `"not_found"` |
| `Conflict` | `AppError` | 409 | `"conflict"` |
| `ValidationFailed` | `AppError` | 422 | `"validation_failed"` — has `.errors: dict[str, str]` |
| `ApplicationNotFound` | `NotFound` | 404 | `"application_not_found"` — has `.application_id`; message `"application 7 not found"` |
| `ServiceUnavailable` | `AppError` | 503 | `"service_unavailable"` |

### `parse_application(data: dict) -> dict`
Validate and return `{"company": str, "role_title": str, "salary_expectation": int | None}`. Collect **all** problems, then raise one `ValidationFailed` with field → message:
- `company`: required, non-blank string → `"required"`
- `role_title`: required, non-blank string → `"required"`
- `salary_expectation`: optional; if present must be an integer ≥ 0 (strings like `"12000000"` are accepted and converted) → `"must be a non-negative integer"`
Strip whitespace from strings.

### `load_application(fetch, application_id)`
Calls `fetch(application_id)`. If `fetch` raises `ConnectionError`, raise `ServiceUnavailable("database unavailable")` **chained** from it. If it returns `None`, raise `ApplicationNotFound(application_id)`.

### `to_response(error) -> tuple[dict, int]`
- `AppError` → `({"error": {"code": …, "message": str(error)}}, status_code)`; for `ValidationFailed` also `"fields": errors`
- anything else → `({"error": {"code": "internal_error", "message": "Something went wrong"}}, 500)` — **never** include the original message

### `timer(name, records)` — context manager
Appends `(name, elapsed_seconds)` to `records` when the block ends, **even if it raises** (and the exception still propagates).

```bash
cd exercises
uv run pytest m2/w3/08-exceptions
```

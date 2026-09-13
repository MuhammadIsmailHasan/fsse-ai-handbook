# M2 · W5 · 07 — A Self-Documenting Companies API

> 🚫🤖 **No-AI** · ⏱️ ~60 min · no database needed

Implement `api.py` with **flask-smorest**. Data lives in memory: `app.extensions["companies"]` is a list, starting empty; ids start at 1.

## `create_app()`
- Config: `API_TITLE="CareerPilot API"`, `API_VERSION="v1"`, `OPENAPI_VERSION="3.0.3"`, `OPENAPI_URL_PREFIX="/docs"`, `OPENAPI_JSON_PATH="openapi.json"`
- Security scheme **`BearerAuth`**: `{"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}`
- Blueprint **`companies`**, prefix `/api/v1/companies`, description `"Companies you apply to"`
- Custom handler for `422`: `{"error": {"code": "validation_failed", "message": "Some fields are invalid", "fields": {"json.name": "…", "query.page": "…"}}}` (first message per field)

## Schemas (marshmallow)
| Schema | Fields |
|---|---|
| `CompanyQuerySchema` | `q` (optional string), `page` (int ≥ 1, default 1) |
| `CompanyCreateSchema` | `name` (required, 1–200, **description** and **example** `"Kopi Data"`), `website` (optional URL) |
| `CompanySchema` | `id` (dump only), `name`, `website` |
| `ErrorSchema` | `error` — a nested object with `code`, `message` |

## Endpoints (MethodView, with docstrings)
| Operation | Summary (docstring 1st line) | Documented responses | Security |
|---|---|---|---|
| `GET ""` | `List companies` | 200 (list of `CompanySchema`), 422 | — |
| `POST ""` | `Create a company` | 201 `CompanySchema`, 409 `ErrorSchema`, 422 | `BearerAuth` |
| `GET "/<int:company_id>"` | `Get a company` | 200, 404 `ErrorSchema` | — |
| `DELETE "/<int:company_id>"` | `Delete a company` | 204, 404 `ErrorSchema` | `BearerAuth` |

Behavior: list filters by `q` (case-insensitive contains); POST with a duplicate name (any case) → `409 {"error": {"code": "company_exists", …}}`; unknown id → `404 {"error": {"code": "company_not_found", …}}`. (No real token check — this exercise is about documentation.)

```bash
cd exercises
uv run pytest m2/w5/07-openapi-docs
# then: cd m2/w5/07-openapi-docs && uv run flask --app "api:create_app()" run --port 5091 → http://localhost:5091/docs/openapi.json
```

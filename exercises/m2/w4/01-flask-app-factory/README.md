# M2 · W4 · 01 — A Job Board API with a Factory and Blueprints

> 🚫🤖 **No-AI** · ⏱️ ~75 min

Create a package `jobboard/` in this folder:

```text
jobboard/
├── __init__.py      # create_app(config_object=DevelopmentConfig)
├── config.py        # Config, DevelopmentConfig, TestingConfig (TESTING = True)
├── errors.py        # register_error_handlers(app)
└── routes/
    ├── __init__.py
    ├── health.py    # blueprint "health"
    └── jobs.py      # blueprint "jobs", url_prefix "/api/v1/jobs"
```

Data lives in memory: `create_app` stores a fresh copy of `SEED_JOBS` (from `seed.py`, provided) in `app.extensions["jobs_store"]` (a list of dicts). Each app gets its **own** copy.

### Endpoints
| Method & path | Behavior |
|---|---|
| `GET /health` | `200 {"status": "ok"}` |
| `GET /api/v1/jobs` | `200 {"data": [...], "meta": {"total": n}}`; optional filters `city` (case-insensitive) and `remote` (`true`/`false`; any other value → `422` with code `invalid_filter`) |
| `GET /api/v1/jobs/<int:job_id>` | `200 {"data": job}`; unknown id → `404` with code `job_not_found` |
| `POST /api/v1/jobs` | JSON `{"title", "company", "city"?, "remote"?}` → `201 {"data": job}` + `Location: /api/v1/jobs/<id>`; new id = max id + 1 |

POST validation → `422 {"error": {"code": "validation_failed", "message": "…", "fields": {...}}}`:
- `title`, `company`: required non-blank strings → `"required"`
- `remote`: if present must be a boolean → `"must be a boolean"`
- body not a JSON object → `400` with code `invalid_json`

### Errors (all JSON)
`{"error": {"code": "...", "message": "..."}}`
- unknown URL → `404`, code `not_found`
- wrong method → `405`, code `method_not_allowed`
- unexpected exception → `500`, code `internal_error`, message `"Something went wrong"`

```bash
cd exercises
uv run pytest m2/w4/01-flask-app-factory
# try it:
cd m2/w4/01-flask-app-factory && uv run flask --app "jobboard:create_app()" run --port 5091
```

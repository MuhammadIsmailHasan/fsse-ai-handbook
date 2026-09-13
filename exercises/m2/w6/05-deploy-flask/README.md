# M2 · W6 · 05 — Production-Ready Flask: Gunicorn, Health Checks, WSGI

> 🚫🤖 **No-AI** · ⏱️ ~75 min · needs the exercise database (`docker compose up -d`)

Provided: `app.py` (factory reading `DATABASE_URL`; `TRUST_PROXY=1` enables `ProxyFix`; `/api/v1/whoami`) and `extensions.py`.

## 1. `health.py` — blueprint `health_bp` (prefix `/health`)
| Endpoint | Behavior |
|---|---|
| `GET /health/live` | always `200 {"status": "ok"}` — **never** touches the database |
| `GET /health/ready` | runs `SELECT 1`; ok → `200 {"status": "ok", "checks": {"database": "ok"}}`; any error → `503 {"status": "unavailable", "checks": {"database": "fail"}}` |

- Both send `Cache-Control: no-store`.
- On failure: **log** the exception at ERROR level (server-side), roll back the session, and don't put error details in the response.

## 2. `gunicorn.conf.py` — every value from the environment
| Setting | Env var | Default |
|---|---|---|
| `bind` | `PORT` | `"0.0.0.0:5091"` |
| `workers` | `WEB_CONCURRENCY` | `min(2 × CPU + 1, 8)` |
| `threads` | `GUNICORN_THREADS` | `1`; `worker_class` = `"gthread"` if threads > 1 else `"sync"` |
| `timeout` | `GUNICORN_TIMEOUT` | `30` |
| `graceful_timeout` | — | `30` |
| `max_requests`, `max_requests_jitter` | — | positive numbers (e.g. 1000, 100) |
| `accesslog`, `errorlog` | — | `"-"` (stdout/stderr) |
| `loglevel` | `LOG_LEVEL` | `"info"` (lower-cased) |
| `forwarded_allow_ips` | `FORWARDED_ALLOW_IPS` | `"127.0.0.1"` |

## 3. `wsgi.py`
Expose `app = create_app()`.

The last test starts a **real Gunicorn** with 2 workers, calls it over HTTP, checks requests are handled by worker processes, then sends `SIGTERM` and expects a clean exit.

```bash
cd exercises
uv run pytest m2/w6/05-deploy-flask

# run it yourself
cd m2/w6/05-deploy-flask
DATABASE_URL=postgresql+psycopg://fsse:fsse@localhost:5491/fsse PORT=5091 uv run gunicorn -c gunicorn.conf.py wsgi:app
curl -i localhost:5091/health/ready
```

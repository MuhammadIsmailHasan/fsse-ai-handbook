# M2 · W6 · 06 — A Production Docker Image for Flask

> 🤖✅ **AI-allowed** (explain every line) · ⏱️ ~90 min · Docker needed only for the optional run test

`service/` contains the lesson 05 app (`app.py`, `health.py`, `wsgi.py`, `gunicorn.conf.py`) as a **uv project** (`pyproject.toml` + `uv.lock`). Its `Dockerfile`, `.dockerignore` and `compose.prod.yaml` are naive. Rewrite all three.

## `service/Dockerfile`
- **Two stages**: a named builder (`FROM python:3.14-slim AS builder`) and a slim runtime; pin every base tag (no `latest`)
- builder: copy uv from `ghcr.io/astral-sh/uv:<pinned version>`; `uv sync --locked --no-dev` (every `uv sync` uses `--locked`/`--frozen` and `--no-dev`)
- **cache-friendly order**: copy `pyproject.toml` + `uv.lock` and install dependencies **before** `COPY . .`
- runtime: `COPY --from=builder` the built app, no `uv sync` here, `ENV PYTHONUNBUFFERED=1`, put `/app/.venv/bin` on `PATH`
- a **non-root `USER`** before `CMD`, `EXPOSE 5091`
- `HEALTHCHECK` that calls `/health/live` (the slim image has no curl: use `python -c "import urllib.request; ..."`)
- `CMD` in **exec form** (JSON array) running `gunicorn ... wsgi:app` (add `--no-control-socket`)
- no secrets in `ENV`/`ARG`

## `service/.dockerignore`
Exclude at least `.git`, `.venv`, `__pycache__`, `.env` and `.env.*`.

## `service/compose.prod.yaml`
- `api` (build `.`) and `db` (pinned `postgres:17-alpine`)
- secrets & `DATABASE_URL` come from **required** variables: `${POSTGRES_PASSWORD:?set POSTGRES_PASSWORD}`, `${JWT_SECRET_KEY:?...}`
- `db` has a `pg_isready` healthcheck, a named volume for `/var/lib/postgresql/data`, and **no published ports**
- `api` waits with `depends_on: db: condition: service_healthy`, publishes `"${API_PORT:-5093}:5091"`
- both have a `restart` policy

```bash
cd exercises
uv run pytest m2/w6/06-dockerize-flask                       # static checks
RUN_DOCKER_TESTS=1 uv run pytest m2/w6/06-dockerize-flask    # + real build, run, health, non-root, graceful stop

# by hand
cd m2/w6/06-dockerize-flask/service
JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(48))") POSTGRES_PASSWORD=local-only-pass \
  docker compose -f compose.prod.yaml up -d --build --wait
curl localhost:5093/health/ready
docker compose -f compose.prod.yaml down -v
```

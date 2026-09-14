# M5 · W1 · 03 — The whole stack in Compose

> 🚫🤖 **No-AI** · ⏱️ ~2 h

Describe a RevoShop-style production stack in `stack/compose.yaml` and a developer override in `stack/compose.override.yaml`. The tests run **`docker compose config`** (Compose's own validator and normalizer) — nothing is built or started.

## `stack/compose.yaml` — production-like (project name `shop`)
| Service | Requirements |
|---|---|
| **proxy** | `caddy:2-alpine`; the **only** service with `ports`: `"${HTTP_PORT:-8080}:80"`; mounts `./Caddyfile` to `/etc/caddy/Caddyfile` **read-only**; waits for `api` to be **healthy**; network `frontend`; `restart: unless-stopped` |
| **api** | `build: { context: ./api, target: prod }`, `image: shop-api:local`; env `JWT_SECRET_KEY: ${JWT_SECRET_KEY:?set JWT_SECRET_KEY}`, `DATABASE_URL: postgresql+psycopg://shop:${POSTGRES_PASSWORD:?set POSTGRES_PASSWORD}@db:5432/shop`, `REDIS_URL: redis://redis:6379/0`; a `healthcheck` calling `/health/live` on port 5091; starts after `db` and `redis` are **healthy** and `migrate` **completed successfully**; networks `frontend` and `backend`; `read_only: true` with a `tmpfs` at `/tmp`; memory limit **512M** (`deploy.resources.limits.memory`); `restart: unless-stopped` |
| **migrate** | same `image: shop-api:local` (no build); `command: ["flask", "--app", "wsgi:app", "db", "upgrade"]`; same `DATABASE_URL`; waits for `db` healthy; network `backend`; `restart: "no"` |
| **worker** | `image: shop-api:local`; `command: ["python", "-m", "worker"]`; `DATABASE_URL` and `REDIS_URL`; waits for `db` and `redis` healthy and `migrate` completed; network `backend`; `restart: unless-stopped` |
| **db** | `postgres:17-alpine`; `POSTGRES_USER: shop`, `POSTGRES_DB: shop`, `POSTGRES_PASSWORD` required as above; named volume `pgdata` at `/var/lib/postgresql/data`; `pg_isready` healthcheck; network `backend`; **no ports** |
| **redis** | `redis:8-alpine`; `command: ["redis-server", "--appendonly", "yes"]`; named volume `redisdata` at `/data`; `redis-cli ping` healthcheck; network `backend`; **no ports** |
| **mailpit** | `axllent/mailpit` with a pinned version tag (not `latest`); profile **`tools`** only; port `"8025:8025"`; network `backend` |

Top level: `name: shop`; networks `frontend` and `backend`; volumes `pgdata` and `redisdata`.

## `stack/compose.override.yaml` — loaded automatically in development
- `api`: build target **`dev`**; bind-mount `./api` to `/app`; `FLASK_DEBUG: "1"`; publish `"5092:5091"` (the root filesystem can stay read-only: the bind mount itself is writable)
- `db`: publish `"5493:5432"` (for your SQL client) · `redis`: publish `"6392:6379"`

```bash
cd exercises
docker compose -f m5/w1/03-compose-full-stack/stack/compose.yaml config        # see what Compose understands
uv run pytest m5/w1/03-compose-full-stack
```

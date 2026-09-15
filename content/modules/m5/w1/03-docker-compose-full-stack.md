---
title: "Docker Compose: The Full Stack Locally"
summary: Run a whole system with one command — proxy, API, worker, migrations, PostgreSQL and Redis — with health-ordered startup, override files, profiles, networks, volumes, and when Compose is enough in production.
type: lesson
source: original
roles: { be: recommended, fe: recommended, fs: core, ai: recommended, ops: core }
durationMinutes: 150
tags: [docker-compose, containers, local-development, postgresql, redis]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Designing a multi-service stack: **proxy → api → worker**, **db**, **redis**, one-off **migrate**
- Startup order with **health checks** and `service_completed_successfully`
- **Environment variables** in Compose: defaults `${VAR:-x}` and required `${VAR:?message}`
- **Override files** (`compose.override.yaml`), several `-f` files and **profiles**
- Networks, named volumes, restart policies and resource limits
- Developer workflow: bind mounts, **`docker compose watch`**, running one-off commands
- Running it: logs, exec, scaling, backups — and when Compose on one server is enough

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Service** | One kind of container in Compose (api, db, redis…) | Layanan |
| **Reverse proxy** | The front door that receives all web traffic and passes it to the right service | Pintu masuk lalu lintas |
| **Worker** | A process that does background jobs (sending emails) instead of answering web requests | Pekerja latar belakang |
| **Migration** | A script that changes the database structure (add a table or column) | Migrasi database |
| **One-off service** | A container that runs a task once and exits | Layanan sekali jalan |
| **Health check** | A command Docker runs to see if a service is really ready | Cek kesehatan |
| **Interpolation** | Filling `${VAR}` in the Compose file with a real value | Penyisipan nilai variabel |
| **Override file** | A second Compose file that changes or adds settings | Berkas penimpa |
| **Profile** | A group of optional services that only start when you ask | Kelompok layanan opsional |

## 🧠 The big idea

`compose.yaml` is the **floor plan of a small building**:

- which rooms exist (services),
- which doors connect them (networks),
- which rooms have safes (volumes),
- which door faces the street (published ports),
- the order the lights come on in the morning (dependencies).

Anyone with the plan can build the same building anywhere — your laptop, a CI machine or a server.

## ❓ Why it matters

A real product is several programs: RevoShop needs the API, PostgreSQL, a way to run migrations, and — as it grows — Redis, a background worker and a reverse proxy with HTTPS. Without Compose, new developers spend a day installing things, and "works on my machine" differences hide bugs. With it: `git clone && docker compose up`.

When it's designed badly:

- `depends_on: [db]` without a health condition → the API starts before PostgreSQL accepts connections → it crashes again and again.
- Migrations run inside every API container at start → two copies run them at the same time.
- Every service publishes ports "for debugging" → Redis open to the internet on a server.
- One big `compose.yaml` with `FLASK_DEBUG=1` used on the production server.

## 📖 Step by step

### 1. The architecture

```mermaid
flowchart LR
    U[Browser / Postman] -->|":8080"| P[proxy<br/>Caddy]
    subgraph frontend
      P --> A[api<br/>gunicorn]
    end
    subgraph backend
      A --> D[(db<br/>PostgreSQL)]
      A --> R[(redis)]
      W[worker] --> R
      W --> D
      M[migrate<br/>one-off] --> D
    end
```

One image (`shop-api:local`) runs as **api**, **worker** and **migrate** with different commands — build once, run three ways. Like one employee trained for the cashier, the warehouse and the stock count: same person, different job for the shift.

### 2. Startup ordered by health

```yaml
services:
  api:
    image: shop-api:local
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy
      migrate:
        condition: service_completed_successfully
    healthcheck:
      test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5091/health/live', timeout=2)"]
      interval: 15s
      timeout: 3s
      retries: 3
      start_period: 10s

  migrate:
    image: shop-api:local
    command: ["flask", "--app", "wsgi:app", "db", "upgrade"]
    depends_on:
      db:
        condition: service_healthy
    restart: "no"

  db:
    image: postgres:17-alpine
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U shop -d shop"]
      interval: 5s
      retries: 10
```

A shop opening in the morning: the cashier (api) doesn't start until the lights are on (db **healthy**) and the shelves are stocked (migrate **completed**).

`depends_on` only orders **startup** on one machine. Your app must still retry connections — databases restart and networks have hiccups.

### 3. Configuration and secrets

```yaml
x-db-url: &database-url postgresql+psycopg://shop:${POSTGRES_PASSWORD:?set POSTGRES_PASSWORD}@db:5432/shop

services:
  api:
    environment:
      JWT_SECRET_KEY: ${JWT_SECRET_KEY:?set JWT_SECRET_KEY}   # refuse to start without it
      DATABASE_URL: *database-url                             # YAML anchor: one definition, reused
      LOG_LEVEL: ${LOG_LEVEL:-INFO}                           # default
```

- `${VAR:-x}` = "use x if it's missing". `${VAR:?message}` = "stop and show this message if it's missing" — better for secrets than a weak default.
- Values come from your shell or a `.env` file next to the Compose file (never commit it; commit `.env.example`).
- `docker compose config` prints the final result after all values are filled in — use it to debug.
- Compose also supports `secrets:` (files mounted under `/run/secrets/`), which keeps secrets out of `docker inspect` output.

### 4. Overrides and profiles

```text
compose.yaml            production-like defaults (no debug, no extra ports)
compose.override.yaml   loaded AUTOMATICALLY by `docker compose up` → dev settings
compose.prod.yaml       server-specific additions (e.g. real domain, log driver)
```

```yaml
# compose.override.yaml
services:
  api:
    build: { target: dev }
    volumes: ["./api:/app"]
    environment: { FLASK_DEBUG: "1" }
    ports: ["5092:5091"]
  db:
    ports: ["5493:5432"]   # connect your SQL client locally
```

```bash
docker compose up                                        # compose.yaml + compose.override.yaml
docker compose -f compose.yaml up -d                     # production-like only
docker compose -f compose.yaml -f compose.prod.yaml up -d
docker compose --profile tools up -d                     # + services with profiles: [tools] (mailpit, adminer)
```

The base file is the **standard house plan**; the override is a **sticky note** with changes for your home ("add a desk here"). Lists like `ports` and `volumes` are **combined**; single values are replaced. Check the result with `config`.

Profiles are like **folding chairs in the storage room**: they exist, but only come out when you ask (`--profile tools`).

### 5. Networks, volumes, restart, limits

```yaml
services:
  api:
    networks: [frontend, backend]
    restart: unless-stopped
    read_only: true
    tmpfs: [/tmp]
    deploy:
      resources:
        limits: { memory: 512M, cpus: "1.0" }
networks:
  frontend:
  backend:
volumes:
  pgdata:
  redisdata:
```

- Only the **proxy** publishes ports; the database and Redis are reachable only on `backend` — staff-only corridors.
- Avoid `container_name` — it blocks `docker compose up --scale worker=3` (two containers can't share one name).
- `docker compose down` keeps volumes; `down -v` **deletes your data**.

### 6. Developer loop

```bash
docker compose up -d --build
docker compose logs -f api worker
docker compose exec api flask --app wsgi:app shell
docker compose run --rm migrate                       # run a one-off service again
docker compose run --rm api python -m pytest          # one-off command in a fresh container
docker compose watch                                   # Compose 2.22+: sync/rebuild on file changes (develop.watch)
docker compose up -d --scale worker=3
```

### 7. Backups (yes, even locally)

```bash
docker compose exec -T db pg_dump -U shop -Fc shop > backup-$(date +%F).dump
docker compose exec -T db pg_restore -U shop -d shop --clean < backup-2026-09-15.dump
```

A backup you've never restored is like a spare key you've never tried in the lock. Test the restore.

### 8. Is Compose enough for production?

| Situation | Compose on one VM | Orchestrator (ECS, Kubernetes) |
|---|---|---|
| Portfolio app, early startup, internal tool | ✅ simple, cheap | overkill |
| Needs zero-downtime deploys across machines | ⚠️ manual (blue/green with a proxy) | ✅ built in |
| Auto-scaling on load, self-healing across hosts | ❌ | ✅ |
| Managed database with backups/failover | combine: Compose app + RDS | ✅ |

Many real products start with Compose on one VM + a managed database — you'll do exactly that with RevoShop, then learn ECS in Week 4.

### Choices to make

- **Migrations as a one-off service:** runs once, clear logs, stops a bad deploy — one more service to understand. **In the entrypoint:** "just works" for one container, but copies race each other and restarts get slow.
- ✅ Compose for local development, CI integration tests, demos, single-server deployments, and reproducing a production bug with the same images.
- 🚫 Not for high availability across several servers or autoscaling — use an orchestrator.
- 🚫 Don't keep production secrets in a `.env` file that's committed or shared in chat.

## ⚠️ Common mistakes

- `depends_on` without health conditions.
- `DATABASE_URL=...@localhost:5432` inside a container.
- `docker compose down -v` in the wrong terminal.
- Mixing old `docker-compose` (v1, retired) commands with `docker compose` (v2) docs.

## 🏆 Best practices

- [ ] One image, several roles (api, worker, migrate) with different commands.
- [ ] Health checks on every service; `service_healthy` / `service_completed_successfully` conditions.
- [ ] Required secrets with `${VAR:?message}`; `.env.example` committed, `.env` ignored.
- [ ] Production-like `compose.yaml`; developer conveniences in `compose.override.yaml`.
- [ ] Publish only the proxy; internal services on a backend network.
- [ ] Named volumes for data; backups tested with a restore.
- [ ] Limits, restart policies, read-only filesystems; no `container_name` if you may scale.
- [ ] Pin image tags (`postgres:17-alpine`, `redis:8-alpine`, `caddy:2-alpine`).
- [ ] Check the file with `docker compose config` in CI.

:::revoshop
Compare your two Compose files side by side.

1. Run `docker compose -f docker-compose.prod.yml config` **without** a `.env` file. It fails with `set POSTGRES_USER` — good, you already use `${VAR:?}` for required secrets. Which required variables does the **dev** file silently give a default instead (`JWT_SECRET_KEY: ${JWT_SECRET_KEY:-dev-secret-key-change-me}`)? Is that acceptable for development?
2. **Migrations.** Both files set `RUN_MIGRATIONS: "true"` and `docker/entrypoint.sh` runs `flask db upgrade` on every container start. Rewrite that as a one-off `migrate` service with `service_completed_successfully`, like the exercise.
3. **Exposure.** `docker-compose.prod.yml` publishes gunicorn directly on `${WEB_PORT:-8000}`. Where would Caddy go, which network would PostgreSQL move to, and which `ports:` disappear?
4. **Scaling blockers.** Both files use fixed `container_name`s. Try `docker compose -f docker-compose.prod.yml up -d --scale web=2` and read the error.
5. **Health.** The prod healthcheck calls `/api/v1/health`, which queries PostgreSQL (`app/routes/health.py`). Why is that a good *readiness* signal but a risky *liveness* signal? Which endpoint will you add?
6. Draw RevoShop's target stack as a table (service · image · command · networks · ports · depends_on) before you touch the files in lesson 05.
:::

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain the "floor plan" analogy and why only the proxy's door should face the street.

## 📐 Design it

RevoShop is adding: product image uploads to object storage, order confirmation emails sent in the background, and an admin that needs a database UI during development only. Design the Compose services (names, images, commands, networks, volumes, ports, dependencies, profiles) for development and production-like use.

:::quiz
Show a possible design

| Service | Image / command | Networks | Ports | Depends on | Notes |
|---|---|---|---|---|---|
| proxy | `caddy:2-alpine` | frontend | `80, 443` (prod) / `8080` (dev) | api healthy | Caddyfile read-only; `caddy_data` volume for certificates |
| api | `revoshop-api` prod target; gunicorn | frontend, backend | none | db, redis healthy; migrate completed | read-only rootfs, limits |
| worker | same image; `python -m app.worker` | backend | none | db, redis healthy; migrate completed | sends emails from a Redis queue |
| migrate | same image; `flask db upgrade` | backend | none | db healthy | `restart: "no"` |
| db | `postgres:17-alpine` | backend | dev only `5493:5432` (override) | — | `pgdata` volume |
| redis | `redis:8-alpine --appendonly yes` | backend | dev only `6392:6379` | — | `redisdata` volume |
| minio | `minio/minio` (pinned) — S3-compatible storage for **dev** | backend | dev `9001` console | — | profile `dev-storage`; production uses real S3 |
| mailpit | `axllent/mailpit` (pinned) | backend | `8025` | — | profile `tools`; catches emails in dev |
| adminer | `adminer` (pinned) | backend | `8081` | db | profile `tools` only |

Production: `docker compose -f compose.yaml -f compose.prod.yaml up -d` with S3 credentials from an IAM role or secrets, no tools profile, the real domain in the Caddyfile.
:::

### 📝 Self-review checklist

- [ ] Ports published only where needed
- [ ] Dev-only services behind profiles
- [ ] Startup ordered by health; migrations run once

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m5/w1/03-compose-full-stack" ai="no-ai" title="The whole stack in Compose"}
Write a production-like `compose.yaml` (proxy, api, migrate, worker, db, redis, mailpit profile) with required secrets, health-ordered startup, internal-only data services and limits, plus a development override. Graded with `docker compose config`, so nothing gets built.
:::

:::hints
- Run `docker compose -f stack/compose.yaml config` often — it shows exactly what Compose understood.
- `${VAR:?set VAR}` makes Compose stop with that message when the variable is missing.
- YAML anchors (`&name` / `*name`) avoid repeating the database URL.
:::

## ✅ Quick check

:::quiz
What's the difference between `docker compose run --rm migrate` and `docker compose up migrate`?

`run` starts a new one-off container for that service (and removes it with `--rm`) — useful for repeating a task. `up` creates/starts the service as part of the project and follows its lifecycle.
:::

:::quiz
You added `ports: ["6379:6379"]` to redis in `compose.yaml` for debugging. Why is that dangerous on a server, and where should it go instead?

It opens Redis (often without a password) on the server's public network interface. Put it in `compose.override.yaml` for local development only, or bind it to `127.0.0.1`.
:::

## 📚 Keep learning

- [Docker docs: Compose file reference](https://docs.docker.com/reference/compose-file/) · [Startup order](https://docs.docker.com/compose/how-tos/startup-order/) · [Profiles](https://docs.docker.com/compose/how-tos/profiles/) · [Compose Watch](https://docs.docker.com/compose/how-tos/file-watch/)
- [Caddy: reverse proxy quick start](https://caddyserver.com/docs/quick-starts/reverse-proxy)

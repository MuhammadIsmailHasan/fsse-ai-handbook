---
title: "Docker in Depth"
summary: Understand what a container really is — namespaces, cgroups and layers, images and digests, CPU architectures, networking, storage, limits and exit codes, debugging and hardening.
type: lesson
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: recommended, ops: core }
durationMinutes: 180
tags: [docker, containers, linux, networking, security, debugging]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What a container is under the hood: **namespaces**, **cgroups**, **overlay filesystems**
- Images, **manifests**, **digests**, tags and registries
- **CPU architectures** (`arm64` Macs vs `amd64` servers) and multi-platform images
- Container **networking**: bridge networks, DNS, published ports
- **Storage**: layers vs volumes vs bind mounts vs tmpfs
- **Resource limits**, the OOM killer and **exit codes** (137, 143, 1)
- A **debugging toolkit**: `logs`, `exec`, `inspect`, `stats`, `events`, `top`
- **Hardening**: non-root, read-only root filesystem, dropped capabilities, `no-new-privileges`

## 🧠 The big idea

A container is **not a small virtual machine**. It's a normal Linux process wearing **blinkers** (namespaces: it can only see its own files, processes and network) and a **diet plan** (cgroups: it can only use so much CPU and memory), standing on a **stack of transparent sheets** (image layers) with one writable sheet on top.

Once you see it that way, most Docker mysteries — "why did it die?", "why can't it reach the database?", "where did my data go?" — become Linux questions with Linux answers.

## ❓ Why does this matter?

In Module 2 you built a good Flask image. In production you'll also need to answer: why did the container restart at 3 a.m.? Why does the image work on my Mac but not on the server? Why is the database data gone after a redeploy? Why does the app ignore `docker stop` for 10 seconds? Those are **runtime** questions, and cloud platforms (ECS, Kubernetes) are built on exactly these primitives.

## 💥 What happens if we DON'T understand it?

- Your RevoShop container shows **`Exited (137)`** and you "fix" it by restarting, again and again.
- You store uploaded files inside the container and lose them on the next deploy.
- An image built on an M-series Mac crashes on an x86 server with `exec format error`.
- You debug networking by publishing every port to the host "to be safe" — including PostgreSQL.

## 📖 How it works, step by step

### 1. What a container is

```mermaid
flowchart TB
    subgraph Host["Linux host (or Docker Desktop's Linux VM on macOS)"]
      K[Linux kernel]
      subgraph C1["container: revoshop-web"]
        P1["gunicorn (PID 1 inside)"]
      end
      subgraph C2["container: revoshop-db"]
        P2["postgres (PID 1 inside)"]
      end
      C1 -. namespaces: pid, net, mnt, uts, ipc, user .-> K
      C1 -. cgroups: cpu, memory, pids .-> K
      C2 -.-> K
    end
```

| Mechanism | Gives the container |
|---|---|
| **PID namespace** | its own process tree (your app is PID 1) |
| **Network namespace** | its own interfaces, IP and ports |
| **Mount namespace** | its own filesystem view |
| **cgroups** | CPU, memory and process-count limits and accounting |
| **OverlayFS** | read-only image layers + a thin writable layer |
| **Capabilities / seccomp** | a reduced set of root powers and allowed system calls |

On macOS and Windows, Docker Desktop runs these containers inside a small **Linux VM** — that's why memory for all containers is limited by the VM's setting (check with `docker info`).

### 2. Images, tags and digests

```bash
docker pull python:3.13-slim
docker image inspect python:3.13-slim --format '{{index .RepoDigests 0}}'
# python@sha256:9d2e55…   ← content address: this exact image forever
```

- An **image** = config + ordered **layers**, described by a **manifest**.
- A **tag** (`3.13-slim`) is a movable label; a **digest** (`@sha256:…`) is immutable.
- A **multi-platform image** has a manifest *list* pointing to one manifest per platform (`linux/amd64`, `linux/arm64`).
- Registries: Docker Hub, **GitHub Container Registry (GHCR)**, **Amazon ECR**, Google Artifact Registry.

### 3. CPU architecture: the Apple Silicon trap

```bash
uname -m                                  # arm64 on M-series Macs
docker image inspect myapp --format '{{.Architecture}}'
docker buildx build --platform linux/amd64 -t myapp:amd64 .           # for x86 servers
docker buildx build --platform linux/amd64,linux/arm64 -t ghcr.io/you/myapp:1.0.0 --push .   # both
```

AWS offers both x86 and **Graviton (arm64)** instances — arm64 is often cheaper for the same performance, and your Mac builds it natively. Decide the target platform deliberately; CI (Week 2) usually builds on `amd64` runners.

### 4. Networking

```bash
docker network create shop
docker run -d --name db --network shop -e POSTGRES_PASSWORD=pw postgres:17-alpine
docker run -d --name api --network shop -p 127.0.0.1:8000:5000 myapp   # host → container
docker exec api getent hosts db          # Docker's embedded DNS resolves service names
```

| Concept | Meaning |
|---|---|
| user-defined bridge network | containers reach each other **by name** (`db:5432`) |
| `-p 8000:5000` | publishes container port 5000 on **all** host interfaces port 8000 |
| `-p 127.0.0.1:8000:5000` | only reachable from the host itself |
| `EXPOSE` | documentation only — doesn't publish anything |
| `localhost` inside a container | the **container itself**, not your laptop and not the database |

Publish only what users must reach (the reverse proxy). Databases stay on internal networks.

### 5. Storage

| Type | Lives | Use for |
|---|---|---|
| container writable layer | until the container is **removed** | nothing important |
| **named volume** (`pgdata:/var/lib/postgresql/data`) | managed by Docker, survives container replacement | database data |
| **bind mount** (`./src:/app`) | a host directory | development hot reload, config files |
| **tmpfs** (`--tmpfs /tmp`) | memory only | scratch files with a read-only root filesystem |

In the cloud, containers are **disposable**: files go to object storage (S3), data to managed databases (RDS), logs to stdout.

### 6. Limits, the OOM killer and exit codes

```bash
docker run --memory 256m --cpus 0.5 --pids-limit 200 myapp
docker stats                                             # live CPU/memory per container
docker inspect revoshop-web --format '{{.State.ExitCode}} OOMKilled={{.State.OOMKilled}}'
```

| Exit code | Meaning |
|---|---|
| 0 | clean exit |
| 1 (or other small numbers) | the app failed (read `docker logs`) |
| 125 / 126 / 127 | Docker couldn't run it / command not executable / command not found |
| **137** | killed with SIGKILL — **OOM killer** or `docker stop` timeout |
| **143** | stopped with SIGTERM (normal graceful stop) |

`docker stop` sends **SIGTERM**, waits 10 s, then SIGKILL. If PID 1 is a shell (`CMD gunicorn …` in shell form) the signal may never reach gunicorn → slow stops ending in 137.

### 7. The debugging toolkit

```bash
docker ps -a                              # status, exit codes, restart counts
docker logs --since 10m -f api            # what the app said
docker inspect api                        # env, mounts, networks, health, exit state
docker exec -it api sh                    # look around inside (if a shell exists)
docker top api                            # processes inside
docker events --since 30m                 # oom, die, health_status events
docker run --rm -it --network container:api nicolaka/netshoot   # network debugging tools next to a container
docker system df                          # disk used by images, volumes, build cache
```

### 8. Hardening

```bash
docker run \
  --user 10001:10001 \
  --read-only --tmpfs /tmp \
  --cap-drop ALL \
  --security-opt no-new-privileges \
  --memory 512m --pids-limit 200 \
  myapp
```

Plus: small base images, no secrets in layers, scan images (`docker scout cves`, `trivy image`), keep base images updated, and never mount `/var/run/docker.sock` into an app container (that's root on the host).

## ⚖️ Trade-offs

| Choice | ✅ | ❌ |
|---|---|---|
| Containers vs VMs | fast start, dense packing, same image everywhere | share the host kernel (weaker isolation than VMs) |
| slim vs alpine vs distroless base | slim: compatible (glibc); alpine: tiny; distroless: minimal attack surface | alpine's musl can break Python wheels; distroless has no shell for debugging |
| `amd64` vs `arm64` targets | amd64: widest compatibility; arm64: cheaper Graviton, native on Macs | building for the other platform is slower (emulation) |
| Named volumes vs managed DB | volumes: cheap, simple | backups, failover, upgrades are on you |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ Package every service as an image; run the same image in dev, CI and production.
- ✅ Use limits and health checks everywhere, even on one server.
- 🚫 Don't treat containers like pets you SSH into and patch — rebuild and redeploy.
- 🚫 Don't run stateful production databases in containers on a single VM without backups and a restore test.

## 🏆 Best practices

- [ ] Know your target **platform** and build for it (or publish multi-arch).
- [ ] Deploy by **digest** or immutable tag, never by `latest`.
- [ ] Publish only the proxy's ports; keep databases on internal networks.
- [ ] Named volumes or managed services for data; nothing important in the container layer.
- [ ] Set memory/CPU limits; watch `docker stats`; alert on restarts and OOM kills.
- [ ] Exec-form CMD so PID 1 receives SIGTERM; handle graceful shutdown.
- [ ] Non-root user, read-only root filesystem, `--cap-drop ALL`, `no-new-privileges`.
- [ ] Log to stdout/stderr; let the platform collect logs.
- [ ] Scan images in CI and rebuild regularly for base-image security fixes.

## 🏭 How it's used in industry

- ECS, Kubernetes, Cloud Run and App Runner all run **OCI images** using these same kernel features; skills transfer directly.
- Platform teams enforce hardening with policies (e.g. Kubernetes Pod Security Standards: non-root, read-only filesystems, dropped capabilities).
- Many companies run mixed x86/arm64 fleets and publish multi-arch images from CI.

## ⚠️ Common mistakes

- `localhost` in `DATABASE_URL` inside a container.
- Deleting a volume with `docker compose down -v` and losing the local database.
- Ignoring exit code 137 or restart loops (`Restarting (1)`).
- Mounting the Docker socket into an app "for convenience".
- Images that only work on the developer's CPU architecture.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain "a process with blinkers, a diet plan and transparent sheets" to a teammate who thinks containers are lightweight VMs, and use it to explain why `localhost` inside a container doesn't reach the database.

## 📐 Design it

Your RevoShop container on a 2 GB server keeps showing `Exited (137)` after traffic spikes, and each restart takes 40 seconds. Write an investigation plan (commands, what you'd look for) and a hardened `docker run` (or Compose service) with limits, health check and security options.

:::quiz
Show a possible plan

**Investigate**
1. `docker inspect revoshop-web --format '{{.State.OOMKilled}} {{.State.ExitCode}} {{.RestartCount}}'` → confirms OOM vs stop timeout.
2. `docker events --since 24h --filter container=revoshop-web` → `oom` and `die` events with timestamps; match with traffic.
3. `docker stats` during a Locust load test → memory per worker × `GUNICORN_WORKERS` (3 workers × ~150 MB + spikes).
4. `docker logs --since 1h` → slow startup: the entrypoint waits for the DB and runs **migrations on every start** (the 40 s).
5. `free -m` / `docker info` on the host → other containers (Postgres) competing for 2 GB.

**Fix**
- Right-size workers (`WEB_CONCURRENCY=2`, `--max-requests 1000 --max-requests-jitter 100` to recycle leaky workers) and set a memory limit with headroom; give Postgres its own limit/`shared_buffers`.
- Move migrations to a one-off job; exec-form CMD for graceful shutdown.

```yaml
api:
  image: ghcr.io/you/revoshop-api:sha-3f2c1ab
  restart: unless-stopped
  environment: { WEB_CONCURRENCY: "2" }
  deploy: { resources: { limits: { memory: 768M, cpus: "1.0" } } }
  read_only: true
  tmpfs: [/tmp]
  cap_drop: [ALL]
  security_opt: ["no-new-privileges:true"]
  healthcheck:
    test: ["CMD", "python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/api/v1/health', timeout=2)"]
    interval: 15s
    timeout: 3s
    retries: 3
    start_period: 20s
```
:::

### 📝 Self-review checklist

- [ ] Evidence before fixes
- [ ] Limits sized from measurements
- [ ] Graceful shutdown addressed

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m5/w1/01-dockerfile-audit" ai="no-ai" title="Build a Dockerfile auditor"}
Write a small Dockerfile linter: a parser that handles continuations and comments, eight rules (unpinned images, root user, shell-form CMD, cache-busting COPY, apt hygiene, baked secrets, ADD with URLs, missing HEALTHCHECK) and a CLI with exit codes. Then run it on your RevoShop Dockerfile.
:::

:::hints
- Split instructions into stages at every `FROM`; remember stage names so `FROM builder` isn't "unpinned".
- For ENV, distinguish `ENV A=b C=d` from the legacy `ENV A b`.
- The registry host may contain a port (`registry:5000/app`) — look for a tag only in the last path segment.
:::

## ✅ Quick check

:::quiz
Why does a named volume survive `docker compose up --build` but a file written inside the container doesn't survive `docker compose up --force-recreate`?

Recreating replaces the container and its writable layer; the named volume is a separate Docker object that's re-attached to the new container.
:::

:::quiz
What does `-p 127.0.0.1:5432:5432` change compared with `-p 5432:5432`?

The port is only published on the host's loopback interface, so other machines on the network (or the internet) can't reach the database.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Namespace | Ruang nama (isolasi pandangan proses) |
| cgroup | Grup kontrol (batas sumber daya) |
| Digest | Sidik isi image (hash tetap) |
| Volume | Penyimpanan data persisten Docker |
| OOM killer | Mekanisme kernel yang mematikan proses saat memori habis |
| Hardening | Pengerasan keamanan |

## 📚 Keep learning

- [Docker docs: Engine security](https://docs.docker.com/engine/security/) · [Networking overview](https://docs.docker.com/engine/network/) · [Volumes](https://docs.docker.com/engine/storage/volumes/)
- [Docker docs: Multi-platform builds](https://docs.docker.com/build/building/multi-platform/)
- [OWASP Docker Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Docker_Security_Cheat_Sheet.html)

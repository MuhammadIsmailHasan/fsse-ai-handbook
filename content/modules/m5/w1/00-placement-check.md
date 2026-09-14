---
title: "Week 1 Placement Check"
summary: Container internals and debugging, build targets, image tags and registries, multi-architecture images, Compose for a full stack, and Redis caching, rate limiting and queues — check what you can skip.
type: placement-check
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: recommended, ops: core }
durationMinutes: 20
tags: [placement, docker, compose, redis]
---

::::placement{id="modules/m5/w1"}
:::quiz
1 · A container shows `Exited (137)`. What happened, and how do you find out why?

137 = 128 + 9 → the process got **SIGKILL**: usually the kernel OOM killer (memory limit hit) or `docker stop` timing out after SIGTERM was ignored. Check `docker inspect --format '{{.State.OOMKilled}}' <name>`, `docker logs`, `docker stats`, and whether the app handles SIGTERM (exec-form CMD).
:::

:::quiz
2 · You build an image on an Apple Silicon Mac and run it on an x86 EC2 instance: `exec format error`. Why, and what are two fixes?

The image was built for `linux/arm64`. Build for the target platform (`docker buildx build --platform linux/amd64`) or publish a multi-arch image (`--platform linux/amd64,linux/arm64`) — or run on an arm64 (Graviton) instance.
:::

:::quiz
3 · Why tag images with the Git commit SHA instead of only `latest`?

Every running container maps to exact source code; deployments are reproducible; rollback = redeploy the previous tag. `latest` is mutable and ambiguous.
:::

:::quiz
4 · In Compose, how do you make sure database migrations run **once** before the API and worker start?

A one-off `migrate` service using the same image, and `depends_on: migrate: condition: service_completed_successfully` on the api and worker (plus `db: condition: service_healthy`).
:::

:::quiz
5 · 10,000 product-list cache keys all expire at the same second and the database falls over. Name the problem and two mitigations.

A **cache stampede** / thundering herd. Add TTL **jitter**, use a **lock** so only one request recomputes a key, serve stale while revalidating, or pre-warm popular keys.
:::

:::quiz
6 · Why is "`LPUSH` to add jobs and `RPOP` to take them" not a reliable queue, and what's the fix?

If a worker crashes after `RPOP` the job is lost. Atomically move jobs to a processing list (`BLMOVE`/`LMOVE`), acknowledge by removing them, and requeue stale ones — or use Redis Streams with consumer groups or a real queue (SQS).
:::
::::

:::tip[Scoring yourself]
Pass with **5 of 6**. Even if you pass, do lesson 05 — it applies this week to **your RevoShop**.
:::

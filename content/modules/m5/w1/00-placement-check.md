---
title: "Week 1 Placement Check"
summary: How containers work and how to debug them, build targets, image tags and registries, images for different CPU types, Compose for a full stack, and Redis caching, rate limiting and queues — check what you can skip.
type: placement-check
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: recommended, ops: core }
durationMinutes: 20
tags: [placement, docker, compose, redis]
---

::::placement{id="modules/m5/w1"}
Answer from memory. If a word is new to you, that's a sign to study the lesson.

:::quiz
1 · A container shows `Exited (137)`. What happened, and how do you find out why?

137 = 128 + 9 → the process received **SIGKILL** (a forced stop). Usually the system killed it for using too much memory (the "OOM killer"), or `docker stop` gave up waiting because the app ignored the polite SIGTERM signal. Check `docker inspect --format '{{.State.OOMKilled}}' <name>`, `docker logs`, `docker stats`, and whether the app handles SIGTERM (exec-form CMD).
:::

:::quiz
2 · You build an image on an Apple Silicon Mac and run it on an x86 EC2 server: `exec format error`. Why, and what are two fixes?

The image was built for ARM chips (`linux/arm64`), but the server has an Intel/AMD chip — like a plug that doesn't fit the socket. Build for the target (`docker buildx build --platform linux/amd64`) or publish one image for both (`--platform linux/amd64,linux/arm64`) — or run on an ARM (Graviton) server.
:::

:::quiz
3 · Why tag images with the Git commit SHA instead of only `latest`?

Every running container then points to exact source code; deployments can be repeated; rollback = deploy the previous tag again. `latest` can change at any time, so it doesn't tell you what's really running.
:::

:::quiz
4 · In Compose, how do you make sure database migrations run **once** before the API and worker start?

Add a one-off `migrate` service using the same image, and put `depends_on: migrate: condition: service_completed_successfully` on the api and worker (plus `db: condition: service_healthy`).
:::

:::quiz
5 · 10,000 product-list cache keys all expire in the same second and the database falls over. Name the problem and two fixes.

A **cache stampede** (thundering herd) — like every shop's stock running out at once and all customers rushing to one warehouse. Add random **jitter** to expiry times, use a **lock** so only one request rebuilds a key, serve the old value while refreshing, or pre-fill popular keys.
:::

:::quiz
6 · Why is "`LPUSH` to add jobs and `RPOP` to take them" not a reliable queue, and what's the fix?

If a worker crashes right after `RPOP`, the job is lost forever. Instead, move the job to a "processing" list in one step (`BLMOVE`/`LMOVE`), remove it when finished, and put stuck jobs back — or use Redis Streams with consumer groups, or a real queue (SQS).
:::
::::

:::tip[Scoring yourself]
Pass with **5 of 6**. Even if you pass, do lesson 05 — it applies this week to **your RevoShop**.
:::

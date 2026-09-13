---
title: "Week 6 Placement Check"
summary: Testing, load testing, secrets, deployment, containers, CI and logging — can you ship and operate the API you built?
type: placement-check
source: original
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: core }
durationMinutes: 25
tags: [placement, testing, deployment, ci]
---

::::placement{id="modules/m2/w6"}
These are the questions that separate "it works on my laptop" from "it runs in production".

:::quiz
1 · Your integration tests use SQLite, production uses PostgreSQL. Name two bugs that could slip through.

PostgreSQL-only behavior isn't tested: `ILIKE`, `JSONB` operators, timezone handling (`timestamptz`), enforced `CHECK`/length constraints that SQLite ignores, concurrency/locking behavior, case-sensitivity of comparisons, and `ON CONFLICT`/`FOR UPDATE` SQL. Test against the same database engine (e.g. PostgreSQL in Docker or a CI service container).
:::

:::quiz
2 · What makes a good unit test? Name three properties.

Fast, isolated/deterministic (no network, fixed time, no shared state), tests one behavior with a clear name, follows Arrange–Act–Assert, and fails for a real bug (not for harmless refactors).
:::

:::quiz
3 · In a Locust run, RPS is stable but p95 latency climbs from 120 ms to 2 s as users increase. What does it suggest and what do you check?

The system is saturated: requests queue up. Check CPU, DB connections/pool limits, slow queries (`pg_stat_statements`, `EXPLAIN`), Gunicorn workers/threads, and external calls; find the bottleneck before adding servers.
:::

:::quiz
4 · Where should `JWT_SECRET_KEY` come from in production, and what should the app do if it's missing?

From environment variables / a secret manager injected by the platform — never code or git. The app must **refuse to start** (fail fast) instead of falling back to a default.
:::

:::quiz
5 · How do you run Flask in production, and why not `flask run`?

Behind a production WSGI server like Gunicorn (workers, timeouts, graceful restarts), usually behind a reverse proxy/load balancer handling TLS. `flask run` is a single-process development server without production hardening.
:::

:::quiz
6 · What should a CI pipeline for this API do on every pull request?

Install locked dependencies, lint/format check, type check, run tests against a PostgreSQL service with migrations applied, maybe security scans (dependency audit, secret scanning) — and block merging when anything fails.
:::
::::

:::tip[Scoring yourself]
Pass with **5 of 6**. Question 1 is especially relevant to your RevoShop tests.
:::

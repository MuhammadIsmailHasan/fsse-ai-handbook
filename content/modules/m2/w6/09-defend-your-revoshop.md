---
title: "🎤 Defend Your RevoShop"
summary: A mock technical interview about your own backend project — explain every decision, find the weak spots before an interviewer does, and turn them into an improvement backlog and a confident project pitch.
type: career
source: original
roles: { be: core, fe: recommended, fs: core, ai: recommended, ops: recommended }
durationMinutes: 240
tags: [interview, portfolio, revoshop, code-review, communication]
---

## 🎯 Why this session exists

In interviews, the most common backend question isn't a LeetCode problem. It's:

> *"Walk me through a project you built. Why did you design it that way? What would break first?"*

Much of RevoShop was generated with Kiro. That's normal in 2026 — companies **expect** you to use AI tools. What they **also** expect is that you can explain, defend and improve every line with your name on it. If you can't, the project hurts you instead of helping.

This session turns RevoShop from "code I have" into "a system I understand".

Think of it like a driving test: you already drive every day, but now someone asks *why* you checked that mirror. Knowing the answer is what turns a driver into a licensed one.

:::warning[The rules]
1. 🚫🤖 **No AI** while answering. Open the code, read it, answer in your own words.
2. **Answer out loud** (or record a voice memo), then write 3–5 bullet points. Speaking reveals gaps that silent reading hides.
3. Every answer must point to **a file and line** in RevoShop.
4. When you don't know: write "I don't know yet", find out, then answer. That's the point.
5. Only after a section is done, reveal the guidance and grade yourself.
:::

## 🔤 Key words

| Word | In simple words |
|---|---|
| **Technical interview** | A conversation where you explain and defend how something works |
| **Project walkthrough** | Telling the story of your project: problem, design, result |
| **Trade-off** | What you gave up to get something else |
| **Design decision** | A choice you made on purpose, with a reason |
| **D-T-C** | Decision → Trade-off → Change: the shape of a good answer |
| **Weak spot** | A part you know isn't good enough yet |
| **Improvement backlog** | Your own list of what to fix next, in order |
| **Pitch** | A short, clear summary of the project for someone new |

## 🧭 How to answer: the D-T-C framework

For every "why" question, answer in three parts:

| Part | Question | Example |
|---|---|---|
| **D**ecision | What did we do? | "Order totals are `Numeric(14, 2)` columns." |
| **T**rade-off | Why this and not the alternative? | "Floats can't represent 0.1 exactly; money must be exact. The cost is converting carefully in JSON." |
| **C**hange | What would I improve now, knowing more? | "`to_dict()` converts to `float` — I'd serialize as a string or integer rupiah." |

Interviewers love the **C** part: it shows judgement and growth. "I'd change X because Y" beats pretending everything is perfect — nobody believes a project with no weak spots, and saying one out loud makes the rest of your answers more credible.

## 🗺️ Part 1 — The 2-minute pitch

Write and rehearse a pitch using this structure. Time yourself: **under 2 minutes**.

1. **What & who** — one sentence: what RevoShop does and for whom.
2. **Architecture** — the layers (routes → services → repositories → models), PostgreSQL, JWT auth, Midtrans payments.
3. **One hard problem** you solved (e.g. payment webhooks, stock handling, role permissions).
4. **Quality** — tests (how many, what kinds), Locust load test, Docker, logging.
5. **What you'd do next** — one honest improvement.

Then draw the architecture **from memory** on paper: client, Gunicorn, Flask app layers, PostgreSQL, Midtrans (checkout redirect + webhook). Compare with the code afterwards.

## 🔍 Part 2 — Defend it, topic by topic

For each question: answer first, then open the guidance.

### A. Project structure & architecture (W3–W4)

1. Trace `POST /api/v1/orders` from the route to the database. Name every file it passes through.
2. Why do routes call services, and services call repositories? What would a route that queries the DB directly cost you?
3. `create_app()` chooses config from `FLASK_ENV`. What is the default, and why is that risky on a server?

:::quiz
Guidance for A

1. `app/routes/orders.py` (parses & validates with a marshmallow schema, gets the JWT identity) → `app/services/order_service.py` `OrderService.create` (address resolution, product lookup, stock check, price snapshot) → `app/repositories/order_repository.py` `OrderRepository.create` (creates order + items, decrements stock, commits) → models in `app/models/orders.py`. A strong answer also mentions the error path: service exceptions → `app/errors.py` handlers → JSON error.
2. Separation of concerns (Week 4 lesson 06): HTTP details stay in routes, business rules in services (testable without HTTP), persistence in repositories (swappable, mockable). Cost of skipping: rules duplicated across endpoints, hard-to-test code, SQL scattered everywhere. Honest trade-off: more files/indirection for a small app.
3. Default is `'development'` (DEBUG on, SQL echo). A Procfile/PaaS deploy without `FLASK_ENV` runs development config in production. Better: fail fast if the environment isn't set explicitly, and don't rely on `FLASK_ENV` (Flask removed its built-in meaning in 2.3) — use your own `APP_ENV` (lesson 04).
:::

### B. Database & data integrity (W2, W4)

4. Why is `price` a `Numeric(11, 2)` and not a `Float`? Look at `to_dict()` — is the API response still exact?
5. Two buyers order the **last** item at the same moment. Walk through `OrderService.create` and `OrderRepository.create`: can stock go negative or be oversold? Prove it.
6. Why does `order_items` store `unit_price` instead of always reading `products.price`?
7. Which columns have indexes? Pick one list endpoint and explain whether its query uses an index (`EXPLAIN`).

:::quiz
Guidance for B

4. Exact decimal arithmetic for money; floats accumulate binary rounding errors. But `to_dict()` returns `float(self.price)`, so JSON clients receive floats — fine for display, risky if a client does arithmetic. Improvement: serialize as a string (`"150000.00"`) or store integer rupiah.
5. **Race condition.** The service reads `product.stock` and checks `stock < quantity` in Python; the repository then does `product.stock -= quantity`. Two transactions can both read stock = 1, both pass the check, both write 0 → **oversold** (a lost update). `products.stock` has no `CHECK (stock >= 0)` constraint, so the database won't stop it either (and a CHECK alone wouldn't prevent a lost update). Fixes (Week 2 transactions): `SELECT … FOR UPDATE` on the product rows (in a consistent order to avoid deadlocks), or an atomic conditional update `UPDATE products SET stock = stock - :q WHERE id = :id AND stock >= :q` and check the affected row count. Prove it with a concurrency test on PostgreSQL (lesson 02 design exercise) — not on SQLite.
6. **Price snapshot**: an order must keep the price the buyer agreed to, even if the seller changes the price later. It's also required for accurate receipts, refunds and reports.
7. Check the models' `index=True`, `Index(...)`, and migrations. For example, listing a buyer's orders filters by `user_id` and sorts by `id`/`created_at` — without an index on `(user_id, created_at)` it becomes a sequential scan as orders grow. Run `EXPLAIN ANALYZE` with seeded data and show the plan.
:::

### C. API design & validation (W5)

8. Pick three endpoints and justify their status codes for success and two errors each.
9. What happens if a client sends an unknown field or a negative quantity when creating an order? Show the schema that decides.
10. How does pagination work on `GET /products`? What happens at page 5,000?

:::quiz
Guidance for C

8. Look for 201 + created resource on create, 200 on read/update, 204 or 200 on delete, 400/422 for validation, 401 missing/invalid token, 403 wrong role/ownership, 404 missing, 409 conflicts (duplicate email, invalid status transition, insufficient stock). Be ready to defend 404-vs-403 for other users' orders (hiding existence vs clarity — Week 5 lesson 06).
9. Marshmallow 4 raises on unknown fields by default (`RAISE`); `validate.Range(min=1)` on quantity should reject ≤ 0. Open the schema in `app/schemas/` and verify — if a rule is missing, that's an item for your backlog.
10. `page`/`limit` → `OFFSET (page-1)*limit`. Deep pages get slower because PostgreSQL still walks the skipped rows, and results can shift when new products are inserted. Mitigations: cap `limit`, keyset (cursor) pagination for infinite scroll (Week 5 lesson 01).
:::

### D. Authentication, authorization & payments (W5)

11. How are passwords stored? Why bcrypt and not SHA-256?
12. A user clicks "logout". Can their access token still be used? For how long? What would you add?
13. How do you make sure a buyer can't read another buyer's order?
14. Midtrans calls your notification endpoint. How do you know the request is really from Midtrans? What if the same notification arrives twice?

:::quiz
Guidance for D

11. `bcrypt.hashpw` with a per-password salt (`app/auth.py`). bcrypt is **slow by design** with a work factor, so brute-forcing leaked hashes is expensive; SHA-256 is fast (billions of guesses per second on GPUs). Alternatives: Argon2id (OWASP's first recommendation).
12. There is no token blocklist/revocation in RevoShop, so an access token stays valid until it expires (`ProductionConfig`: 15 minutes; `BaseConfig`: 1 hour — note the **same** `JWT_ACCESS_TOKEN_EXPIRES` variable means *hours* in one class and *minutes* in the other, a unit bug waiting to happen), and a refresh token for days. Improvement: short-lived access tokens + a revocation list (Redis/DB by `jti`) checked with `token_in_blocklist_loader`, revoke refresh tokens on logout (Week 5 lesson 05).
13. The service receives `user_id` and `role` and filters/checks ownership (`OrderService.get_by_id(order_id, user_id, role)`). Mention the test that proves it (an integration test with two buyers), and that the check lives in the service, not only in the frontend.
14. `PaymentService.verify_signature` recomputes `SHA512(order_id + status_code + gross_amount + server_key)` and compares with `hmac.compare_digest` (constant time) ✅. For duplicates: check how `handle_notification` behaves when the status doesn't change or moves backwards — idempotency should come from the current status/transition rules or storing processed notification ids. Also: always re-verify the amount, and consider calling Midtrans's status API for critical transitions (Week 5 lesson 08).
:::

### E. Quality & operations (W6)

15. Your tests use SQLite in memory. Name one RevoShop behavior that could pass in tests and fail on PostgreSQL.
16. What did your Locust test measure, against which server, and what was the p95 of your slowest endpoint? What's the bottleneck?
17. What happens if production starts without `JWT_SECRET_KEY`?
18. Explain your Docker setup: image, user, how migrations run, what happens with 3 replicas.
19. A customer says "my checkout failed at 14:02". How do you find what happened?

:::quiz
Guidance for E

15. The stock race condition (SQLite serializes writes differently; no `FOR UPDATE`), `Numeric` precision and `CHECK` constraints, case sensitivity in searches (`LIKE` vs `ILIKE`), timezone handling, string length limits. Fix: run tests on PostgreSQL in Docker/CI (lessons 02 and 07).
16. The README points Locust at `127.0.0.1:5000` — the **dev server**. Honest answer: "those numbers aren't production-representative; I re-ran against Gunicorn and got …". Then name the bottleneck with evidence (slow query plan, worker saturation, Midtrans call latency). If you haven't re-run it, do it now.
17. `BaseConfig` falls back to `'super-secret-key-change-in-production'` — the app would start with a public secret, so anyone could forge admin tokens. `docker-compose.prod.yml` protects that path with `${JWT_SECRET_KEY:?}`, but the Procfile path doesn't. Fix: fail-fast settings (lesson 04).
18. Single-stage `python:3.12-slim`, dependencies installed before `COPY . .` ✅, non-root `appuser` ✅, exec-form CMD ✅; `entrypoint.sh` waits with netcat and runs `flask db upgrade` on **every** container start — with 3 replicas, three concurrent migrations. `GUNICORN_WORKERS` in compose is ignored because the CMD hardcodes `--workers 3`. Improvements: migrations as a release step, `gunicorn.conf.py` from env, HEALTHCHECK, logs to stdout (lessons 05–06).
19. Today: text logs in `logs/app.log` without request ids — hard. Improved answer: JSON logs to stdout with request ids, the error response shows the reference id, search logs by it and by `user_id` + time window, check the Midtrans notification logs for that order (lesson 08).
:::

### F. The AI question

20. *"Did you write this yourself?"* Prepare an honest, confident answer.

:::quiz
Guidance for F

Don't hide it, and don't apologize for it. A strong answer:

> "I built it in a bootcamp using Kiro for spec-driven development — I wrote the requirements and steering rules, and generated much of the first implementation. Afterwards I reviewed it deeply: for example I found the stock check has a race condition and fixed it with a row lock plus a concurrency test on PostgreSQL, and I moved the tests from SQLite to Postgres. I can walk you through any part."

It shows: you use modern tools, you own the result, and you can find and fix real problems. The claim is only credible if you **can** walk through any part — which is what this session is for.
:::

## 📋 Part 3 — Score yourself

For each of the 20 questions give yourself:

| Score | Meaning |
|---|---|
| **2** | Answered without looking anything up, pointed to the code, included a trade-off |
| **1** | Needed to read the code first, or answer lacked the trade-off/improvement |
| **0** | Couldn't answer yet |

| Total | Where you are |
|---|---|
| 34–40 | Interview-ready on this project. Polish the pitch and the README. |
| 22–33 | Solid. Re-study the 0/1 topics' lessons, then redo those questions in a week. |
| < 22 | Normal for AI-built projects. Work through the backlog below — each fix teaches the concept for real. |

Add every 0 or 1 question to the **review queue** (mark the related lessons done-but-review) so spaced repetition brings them back.

## 🛠️ Part 4 — Your RevoShop improvement backlog

Every weak spot you found is now a task, not a worry. A written backlog is also an interview answer in itself: it shows you know where the project stands.

Turn weak spots into GitHub issues in your RevoShop repo. Suggested backlog — pick at least **three** to implement yourself (No-AI for the first draft):

- [ ] **Fix the stock race condition** with `FOR UPDATE` or a conditional `UPDATE`, plus a concurrent checkout test *(M2 W2 L07, W6 L02)*
- [ ] **Run tests on PostgreSQL** (Docker locally + CI service) *(W6 L02, L07)*
- [ ] **Fail-fast settings**: no default JWT secret, explicit environment *(W6 L04)*
- [ ] **Token revocation on logout** *(W5 L05)*
- [ ] **Money serialization** as string or integer rupiah *(M2 W3 data types)*
- [ ] **GitHub Actions CI**: lint, audit, tests on Postgres, Docker build *(W6 L07)*
- [ ] **Migrations as a release step**, `gunicorn.conf.py`, `HEALTHCHECK` *(W6 L05, L06)*
- [ ] **JSON logs to stdout** with request ids; stop logging DB error parameters *(W6 L08)*
- [ ] **Re-run Locust against Gunicorn**, record p95 per endpoint in the README *(W6 L03)*
- [ ] **README "Design decisions" section** using D-T-C for 5 key decisions

Each fixed item becomes a real interview story: *"I found X, measured it, fixed it with Y, and proved it with test Z."*

:::tip[Portfolio signal]
A pull request titled "fix: prevent overselling with row-level locks (+ concurrent checkout test)" is more impressive to a hiring manager than ten new endpoints.
:::

## ✅ Done when

- [ ] Pitch recorded in under 2 minutes
- [ ] Architecture drawn from memory
- [ ] All 20 questions answered out loud with file references and scored
- [ ] At least 3 backlog items opened as issues, and 1 implemented and merged
- [ ] README has a "Design decisions" section

## 📣 End of Week 6 — share your progress

:::linkedin{type="weekly"}
🚢 Week 6: from "works on my laptop" to production-ready.

- Wrote tests that were graded by *mutants* — buggy copies of my code — to prove my tests actually catch bugs
- Load tested an API with Locust and learned why p95 matters more than the average
- Built a CI pipeline with GitHub Actions: lint, types, tests on real PostgreSQL, Docker build
- Shipped a multi-stage, non-root Docker image with health checks and JSON logs with request ids

Then I did a mock interview on my own e-commerce backend and found a race condition that could oversell the last item in stock. Fixing it taught me more than building the feature. [link to your PR]

#Python #Flask #DevOps #Testing #LearningInPublic
:::

:::linkedin{type="reflection"}
🎓 Module 2 (Backend Development) done.

What I built: [RevoShop — e-commerce API with X endpoints, JWT auth, Midtrans payments, Y tests].
Hardest part: [e.g. making payment webhooks idempotent / understanding transactions].
What I'd do differently: [e.g. test on PostgreSQL from day one].
The skill I'm proudest of: explaining *why* each design decision was made — not just that it works.

Next: frontend with React & TypeScript. 🚀

#BackendDevelopment #Python #PostgreSQL #LearningInPublic
:::

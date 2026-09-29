---
title: "Week 2 Placement Check"
summary: Can you explain when async/await actually helps, what FastAPI's dependency injection does, how SQLAlchemy 2.0 sessions work in FastAPI, and how JWT auth flows? If yes, skim the week.
type: placement-check
source: original
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: optional }
durationMinutes: 20
tags: [placement, fastapi, async, dependency-injection, jwt]
---

::::placement{id="modules/m3/w2"}
This week wires FastAPI to a database with auth. Can you explain these without looking?

:::quiz
1 · When does `async def` make a FastAPI endpoint faster, and when does it not help?

It helps when the handler mostly **waits on I/O** (a database, another API, an AI model), because the server can serve other requests during the wait. It does **not** help CPU-bound work (heavy computation), which keeps the event loop busy rather than waiting.
:::

:::quiz
2 · What problem does FastAPI's `Depends(...)` (dependency injection) solve?

It provides shared setup — a database session, the current authenticated user, settings — to any endpoint that declares it, instead of each handler creating those itself. FastAPI resolves the dependency, injects the result, and can clean it up afterward, which also makes handlers easy to test.
:::

:::quiz
3 · In SQLAlchemy 2.0, how do you get one user by id and how do you run a query?

`session.get(User, user_id)` fetches by primary key; for queries you build a statement and execute it: `session.scalars(select(User).where(User.email == e)).all()`. The `Session` is a unit of work that batches changes and commits them in a transaction.
:::

:::quiz
4 · Walk through JWT login: what does the server send back, and what does the client do next?

On successful login the server returns a signed **JWT access token**. The client stores it and sends it on later requests in the `Authorization: Bearer <token>` header. The server verifies the signature (no DB lookup needed) and reads the user id from the token's claims.
:::

:::quiz
5 · Why verify a JWT's signature on every request instead of looking the token up in a database?

Because the signature proves the token was issued by your server and hasn't been tampered with, using a secret key — so you trust its claims without a database round-trip. That statelessness is JWT's main benefit (the trade-off is you can't easily revoke a token before it expires).
:::
::::

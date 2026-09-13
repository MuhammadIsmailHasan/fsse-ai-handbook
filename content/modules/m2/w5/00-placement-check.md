---
title: "Week 5 Placement Check"
summary: Test your API design instincts — resources and methods, pagination, validation and status codes, JWT auth, authorization, docs and webhooks.
type: placement-check
source: original
roles: { be: core, fe: recommended, fs: core, ai: recommended, ops: optional }
durationMinutes: 25
tags: [placement, rest, api, auth]
---

::::placement{id="modules/m2/w5"}
RevoShop has JWT, roles, Swagger docs and Midtrans webhooks. Can you explain the *why* behind each?

:::quiz
1 · Design the endpoint to mark application 42 as withdrawn. Which method and path, and what if the client retries the same request after a timeout?

Either `PATCH /api/v1/applications/42` with `{"status": "withdrawn"}` or an action endpoint `POST /api/v1/applications/42/status`. The operation should be **idempotent** in effect: withdrawing an already-withdrawn application returns the same final state (200), not an error or a duplicate history row — or the client sends an `Idempotency-Key`.
:::

:::quiz
2 · Offset pagination (`?page=500`) is slow and returns duplicates when new rows arrive. What's the alternative?

Keyset (cursor) pagination: `WHERE (created_at, id) < (:last_created_at, :last_id) ORDER BY created_at DESC, id DESC LIMIT 20`, returning an opaque `next_cursor`.
:::

:::quiz
3 · `400`, `401`, `403`, `404`, `409`, `422` — give a one-line example for each.

400 malformed JSON · 401 missing/expired token · 403 logged in but not allowed (a buyer editing products) · 404 resource doesn't exist (or belongs to someone else) · 409 conflicts with current state (duplicate, invalid transition) · 422 well-formed but invalid fields.
:::

:::quiz
4 · What's inside a JWT, and why can't you put a user's password or role changes you need to revoke instantly only in it?

A header, a payload of claims (`sub`, `exp`, custom claims like `role`) and a signature — **signed, not encrypted**, so anyone can read the payload. The server trusts it until it expires, so revoking or changing a role doesn't take effect until expiry unless you add a denylist/short lifetimes + refresh tokens.
:::

:::quiz
5 · Authentication vs authorization — and where do you check "this order belongs to the current user"?

Authentication = who you are; authorization = what you may do. Ownership is authorization and belongs in the service/query (`WHERE user_id = :current_user`), not only in the frontend.
:::

:::quiz
6 · A payment provider sends webhooks. Name three things your endpoint must do.

Verify the **signature** (and reject unsigned/old requests), process **idempotently** (the same event can arrive multiple times), respond **quickly** with 2xx and do heavy work asynchronously — plus log and handle out-of-order events.
:::
::::

:::tip[Scoring yourself]
Pass with **5 of 6**. If you've built these features with AI help, study the lessons anyway — interviewers go deep on auth and webhooks.
:::

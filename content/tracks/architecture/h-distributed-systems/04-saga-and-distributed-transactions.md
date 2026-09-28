---
title: "Saga & Distributed Transactions"
summary: How to keep a multi-service operation consistent when one database transaction can't span them all — the saga pattern runs a chain of local steps, each with a compensating undo, so a late failure rolls the whole thing back cleanly.
type: lesson
source: original
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: core }
durationMinutes: 130
tags: [architecture, distributed-systems, saga, transactions, compensation, consistency]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Why a single database transaction can't span multiple services
- What a **saga** is: a chain of local steps with **compensations**
- How a **compensating action** undoes a completed step
- **Orchestration** vs **choreography** ways to run a saga
- Why sagas give **eventual** consistency, not instant atomicity
- How this applies to a checkout that touches stock, payment, and shipping

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Transaction** | A group of changes that all happen or none do | Semua berubah atau tidak |
| **Atomic** | All-or-nothing, no half-done state | Utuh, tak setengah jadi |
| **Saga** | A sequence of local steps that can each be undone | Rangkaian langkah bisa dibatalkan |
| **Local transaction** | One normal transaction inside one service | Transaksi dalam satu layanan |
| **Compensation** | An action that undoes a completed step | Aksi pembatal |
| **Orchestration** | One coordinator drives the steps | Satu pengatur menjalankan langkah |
| **Choreography** | Services react to each other's events | Layanan bereaksi ke event |

## 🧠 The big idea

Booking a trip means three separate desks: **flight**, **hotel**, **car**. There is no single "trip transaction" — each desk only controls its own booking. A **saga** is the **travel agent** who books them one by one, and if the car desk says "sold out" after the flight and hotel are booked, the agent **cancels** the hotel and the flight (the **compensations**) so you don't end up half-booked.

A compensation isn't a magic rewind — it's a real, sensible undo: cancel the reservation, refund the payment, release the stock.

## ❓ Why it matters

In Module 2 you used one transaction to make several changes atomic — but that only works **inside one database**. Once an operation crosses services (order service, payment service, shipping service), each has its *own* database, and no single transaction can wrap them all.

Without a plan, a failure halfway leaves a mess: stock reserved but no payment, or money taken but no order. The saga pattern is the standard way to keep such multi-service operations consistent — not instantly, but reliably.

## 📖 Step by step

### 1. Why not just one big transaction?

The classic answer is **two-phase commit (2PC)**: a coordinator asks every service "ready?", then "commit". It gives true atomicity, but it's slow, and it **blocks**: if the coordinator or one service stalls, everyone waits with locks held. At scale this is fragile, so most systems avoid 2PC for cross-service work.

### 2. The saga: local steps + compensations

A saga breaks the big operation into a **sequence of local transactions**, each in one service. Every step has a matching **compensation** that undoes it:

| Step (do) | Compensation (undo) |
|---|---|
| Reserve stock | Release stock |
| Charge payment | Refund payment |
| Create shipment | Cancel shipment |

Run the steps in order. If a step fails, run the **compensations for the already-completed steps, in reverse order**.

```
reserve stock ✅ → charge payment ✅ → create shipment ❌
                          ↓ fail → compensate in reverse:
                    refund payment ↩ → release stock ↩
```

The end state is consistent: either everything succeeded, or everything was undone.

### 3. Compensations must be real and idempotent

A compensation is business logic, not a database rollback. "Refund payment" means actually issuing a refund. And because steps and compensations may be retried (at-least-once messaging), each must be **idempotent** — refunding twice must not send two refunds.

Some steps can't be perfectly undone (an email already sent). For those you compensate as best you can (send a correction) — a reason to order steps so the hardest-to-undo ones come **last**.

### 4. Orchestration vs choreography

Two ways to run the chain:

- **Orchestration**: one **coordinator** (an "order saga") explicitly calls each step and triggers compensations on failure. Easy to see the whole flow in one place; the coordinator is a central piece to maintain.
- **Choreography**: no coordinator — each service emits **events** (`StockReserved`, `PaymentCharged`) and the next service reacts. Very decoupled, but the overall flow is spread across services and harder to follow.

Beginners should usually start with **orchestration**: the logic is in one readable place.

### 5. Eventual, not instant

While a saga runs, the system is briefly *inconsistent* (stock reserved, payment not yet charged). That's expected — a saga gives **eventual** consistency. So states like `order: pending` are normal, and the user is told "we're confirming your order" until the saga finishes.

### Choosing your approach

| Situation | Do this |
|---|---|
| All changes are in one database | Use a normal transaction — no saga needed |
| An operation spans several services | Saga with compensations |
| A small, readable team-owned flow | Orchestration (one coordinator) |
| Highly decoupled, event-driven services | Choreography (events), with care |

- ✅ Use a plain transaction when everything is in one database.
- ✅ For multi-service operations, define each step's compensation up front.
- ✅ Order steps so the hardest-to-undo action is last; make steps idempotent.
- 🚫 Don't reach for cross-service 2PC by default — it's slow and blocking.

## ⚠️ Common mistakes

- Assuming one transaction can span services — it can't; each has its own database.
- Forgetting to write a compensation for a step, so a late failure can't be undone.
- Non-idempotent steps/compensations → double refunds or double reservations under retries.
- Ordering an un-undoable step (send email, ship goods) early, before risky steps.
- Hiding the in-progress state, so users think the order failed while the saga is still running.

:::revoshop
RevoShop checkout today is one PostgreSQL transaction (reserve stock, create order, record payment together). (1) If payment moved to a separate service (or Midtrans), that transaction no longer covers everything — sketch the saga: steps and each step's compensation. (2) Which step is hardest to undo, and where should it sit in the order? (3) The payment webhook can fire twice — how do you keep the "charge" step and its "refund" compensation idempotent?
:::

## 🏆 Best practices

- [ ] Keep single-database work in one transaction; only use a saga across services.
- [ ] Define a compensation for every step before shipping the saga.
- [ ] Make every step and compensation idempotent (retries are guaranteed).
- [ ] Order steps so the least-reversible action runs last.
- [ ] Prefer orchestration first for a clear, central flow; add choreography only when decoupling demands it.
- [ ] Model and show in-progress states (`pending`, `confirming`) to users and monitoring.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain a saga with the travel-agent-booking-flight-hotel-car analogy, including what happens when the car is sold out. Then say, in one sentence, why a compensation is different from a database rollback.

## 📐 Design it

CareerPilot offers a paid "Priority Application": it (1) spends 1 credit, (2) calls a paid AI to tailor the CV, (3) submits the application to a partner API, and (4) emails a confirmation. These touch different services. Design the saga: the ordered steps, each compensation, which step should be last, and how you handle the fact that the email can't really be un-sent.

:::quiz
Show a possible design

**Ordered steps + compensations:**
1. **Spend 1 credit** ↔ compensate: **refund the credit**.
2. **AI tailor CV** ↔ compensate: **discard the generated draft** (cheap; nothing external changed).
3. **Submit to partner API** ↔ compensate: **withdraw/cancel the submission** (if the partner allows it).
4. **Email confirmation** — practically **un-undoable**, so it goes **last**, only after everything else succeeded.

**On failure:** if step 3 (submit) fails, compensate in reverse — discard the draft and refund the credit — leaving the user exactly as before, and never send the confirmation email.

**The email problem:** you can't un-send it, so you (a) put it last so it only fires on full success, and (b) if something must be undone after it, send a **correction** email as the compensation. Ordering the least-reversible step last minimizes this.

**Idempotency:** key each step by the application id so a retried "spend credit" or "refund" doesn't double up.

**Rule shown:** a saga is ordered local steps with real compensations; put the least-reversible step last and make everything idempotent, accepting eventual (not instant) consistency.
:::

### 📝 Self-review checklist

- [ ] Every step has a concrete compensation
- [ ] The least-reversible step is ordered last
- [ ] Steps and compensations are idempotent
- [ ] In-progress/eventual state is modeled and shown

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/architecture/h-distributed-systems/04-saga" ai="no-ai" title="A saga runner with compensations"}
Implement a saga runner: run each step's action in order; if one fails, run the compensations of the already-completed steps in reverse order, and report what committed vs. what was rolled back. The tests drive a booking saga to full success and to a mid-way failure that must undo the earlier steps.
:::

:::hints
- Each step is a dict: `{"name", "action", "compensate"}`; `action(ctx)` and `compensate(ctx)` take a shared context dict. A failing action raises an exception.
- Track completed steps; on an exception, iterate `reversed(completed)` calling each `compensate`.
- Return something like `{"status": "committed"|"aborted", "committed": [names], "compensated": [names in undo order], "failed_at": name|None}`.
:::

## ✅ Quick check

:::quiz
Why can't you use a single database transaction to make a multi-service operation atomic?

Because each service has its own database, and a transaction only spans one database. To keep the whole operation consistent across services you use a saga: a chain of local transactions, each with a compensation that undoes it if a later step fails.
:::

:::quiz
What is a compensating action, and how does it differ from a rollback?

It's a business action that undoes a completed step — release stock, refund a payment, cancel a shipment. Unlike a database rollback (which erases uncommitted changes automatically), a compensation is real work you run explicitly, because the step already committed in another service.
:::

## 📚 Keep learning

- [Microservices.io: Saga pattern](https://microservices.io/patterns/data/saga.html)
- [AWS: saga pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/saga.html)
- [Martin Kleppmann, *DDIA*, Ch. 7 (transactions)](https://dataintensive.net/)

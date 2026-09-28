---
title: "Retries, Backoff & Circuit Breaker"
summary: How to handle a flaky dependency without making things worse — retry only safe operations, wait longer each time with jitter, and trip a circuit breaker to stop hammering a service that's clearly down.
type: lesson
source: original
roles: { be: core, fe: recommended, fs: core, ai: recommended, ops: core }
durationMinutes: 120
tags: [architecture, distributed-systems, retries, backoff, circuit-breaker, resilience]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- When a **retry** helps and when it hurts
- **Exponential backoff**: waiting longer after each failed attempt
- **Jitter**: adding randomness so clients don't retry in sync
- The **thundering herd** / retry storm problem
- The **circuit breaker**: stop calling a service that's clearly down
- How these protect a real dependency (payment gateway, AI API)

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Transient error** | A brief, likely-to-pass failure | Kegagalan sesaat |
| **Retry** | Try the same call again | Coba lagi |
| **Backoff** | Wait longer before each retry | Menunggu makin lama |
| **Exponential backoff** | Double the wait each attempt | Waktu tunggu berlipat |
| **Jitter** | Random wiggle added to the wait | Acak kecil pada waktu tunggu |
| **Thundering herd** | Many clients retrying at the same instant | Semua mencoba serentak |
| **Circuit breaker** | A switch that stops calls to a failing service | Sakelar penghenti panggilan |

## 🧠 The big idea

- **Retry with backoff** is **knocking on a door**: if no answer, you don't pound continuously — you wait a bit, then a bit longer, giving them time to come.
- **Jitter** is **not everyone knocking on the same beat**: if a whole crowd knocks in perfect unison, the door never gets a quiet moment; spreading the knocks out helps.
- **Circuit breaker** is a **home fuse**: when something is badly wrong, the fuse trips and cuts the power so the house doesn't burn. After a while you flip it back to test if things are safe again.

## ❓ Why it matters

Networks and services fail briefly all the time — a blip, a timeout, a momentary overload. A naive app either gives up too easily (fails on a blip that a single retry would fix) or retries too aggressively (hammers a struggling service until it fully collapses, and takes your app down with it).

Retries, backoff, jitter, and circuit breakers are the standard toolkit for being **resilient without being a bully**: recover from blips, but back off and stop when a dependency is truly down.

## 📖 Step by step

### 1. Retry — but only what's safe

Retrying makes sense for **transient** errors (timeouts, `503 Service Unavailable`, connection resets). It's dangerous for operations that aren't **idempotent**: retrying "charge the card" might charge twice. So:

- Retry **reads** and idempotent writes freely.
- Retry non-idempotent writes (payments) **only** with an idempotency key (previous lessons).
- Don't retry a `400 Bad Request` — it'll fail the same way every time.

### 2. Exponential backoff

Don't retry instantly in a tight loop — that just piles on load. Wait **longer after each attempt**, doubling the delay:

```python
def backoff_delay(attempt, base=0.5, cap=30):
    return min(cap, base * (2 ** attempt))
# attempt 0 → 0.5s, 1 → 1s, 2 → 2s, 3 → 4s ... capped at 30s
```

This gives a struggling service breathing room instead of a constant barrage, and the **cap** stops the wait growing forever.

### 3. Jitter — break the sync

If 1,000 clients all fail at the same moment and all back off by exactly the same amounts, they retry in perfect waves — a **thundering herd** that keeps knocking the service over. Add **jitter** (randomness) so retries spread out:

```python
import random
def backoff_with_jitter(attempt, base=0.5, cap=30):
    delay = min(cap, base * (2 ** attempt))
    return random.uniform(0, delay)   # spread retries across the window
```

Now the crowd knocks at slightly different times, and the service gets quiet moments to recover.

### 4. The circuit breaker

If a service has been failing for a while, retrying at all is pointless and harmful. A **circuit breaker** watches the failures and, past a threshold, **trips open** — new calls fail fast (or use a fallback) without even trying the dead service. It has three states:

```
CLOSED  → calls flow normally; count failures
   │  too many failures
   ▼
OPEN    → calls are blocked immediately (fail fast) for a cooldown period
   │  cooldown elapsed
   ▼
HALF-OPEN → allow ONE trial call
   ├─ success → back to CLOSED (recovered)
   └─ failure → back to OPEN (still down)
```

This protects both sides: your app stops wasting time on doomed calls, and the struggling service gets a break from the traffic so it can recover.

### 5. Putting it together

A resilient call to a dependency:

1. Try the call.
2. On a transient error, **retry with exponential backoff + jitter**, a few times.
3. Feed successes/failures to a **circuit breaker**; if it's open, fail fast or use a fallback instead of retrying.

### When to use what

| Situation | Tool |
|---|---|
| A single timeout / `503` on a read | Retry with backoff + jitter |
| A payment or non-idempotent write | Retry only with an idempotency key |
| A dependency failing repeatedly for a while | Circuit breaker (fail fast) |
| A `400`/validation error | Don't retry — fix the request |

- ✅ Retry transient failures with capped exponential backoff and jitter.
- ✅ Wrap flaky dependencies in a circuit breaker with a fallback.
- 🚫 Don't retry non-idempotent writes without an idempotency key.
- 🚫 Don't retry instantly or in lockstep — that causes retry storms.

## ⚠️ Common mistakes

- Immediate, unlimited retries with no backoff → a retry storm that worsens the outage.
- Backoff with no jitter → synchronized thundering herd.
- Retrying non-idempotent operations → double charges.
- No cap on backoff → waits grow to minutes; or no circuit breaker → hammering a dead service.
- Retrying errors that will never succeed (`400`, `404`, auth failures).

:::revoshop
RevoShop calls Midtrans (payment) and may later call an AI service. (1) Which calls are safe to retry as-is, and which need an idempotency key first (creating a charge)? (2) Add exponential backoff with jitter to a flaky external call — what base and cap are reasonable? (3) If Midtrans is down for minutes, how would a circuit breaker help RevoShop fail fast and show users a clear "payments temporarily unavailable" message instead of long hangs?
:::

## 🏆 Best practices

- [ ] Retry only transient, safe (idempotent or keyed) operations; never blindly retry payments.
- [ ] Use capped exponential backoff **with jitter** to avoid synchronized retries.
- [ ] Limit the number of retries; give up and surface a clear error eventually.
- [ ] Wrap unreliable dependencies in a circuit breaker with a sensible fallback.
- [ ] Log and alert when a breaker trips — it signals a real outage.
- [ ] Distinguish retryable (5xx/timeout) from non-retryable (4xx) errors.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain retries-with-backoff with the knocking-on-a-door analogy, jitter with the not-knocking-in-unison idea, and a circuit breaker with the home-fuse analogy. Then say in one sentence why a payment call shouldn't be retried without an idempotency key.

## 📐 Design it

CareerPilot depends on a paid LLM API that occasionally times out and, rarely, goes down for several minutes. Design a resilient calling strategy: which errors you retry and how (backoff/jitter/limits), how a circuit breaker protects the app and the LLM during a longer outage, and what the user sees in each case.

:::quiz
Show a possible design

**Retries:** on a timeout or `503`, retry up to 3 times with exponential backoff + jitter (e.g. base 0.5s, cap 8s, `random.uniform(0, delay)`). The LLM "generate" call is effectively idempotent for retries if you key on the request (or accept a possibly-different completion); a `400` (bad prompt) is **not** retried.

**Circuit breaker:** wrap the LLM client. After, say, 5 failures in a row, the breaker **opens** for a 30s cooldown — calls fail fast instead of piling 3 retries × many users onto a dead service. After cooldown it goes **half-open**, lets one trial call through; success → closed, failure → open again.

**What the user sees:** a transient blip is invisible (a retry fixes it). During an open breaker, the app fails fast with a friendly fallback — "AI suggestions are temporarily unavailable, we saved your draft" — instead of long spinners, and it recovers automatically once the trial call succeeds.

**Rule shown:** retry transient errors with backoff + jitter and a limit, and use a circuit breaker to fail fast (with a fallback) during a real outage so you don't hammer the dependency.
:::

### 📝 Self-review checklist

- [ ] Retryable vs non-retryable errors are distinguished
- [ ] Backoff is capped and has jitter; retries are limited
- [ ] Non-idempotent writes are keyed before any retry
- [ ] A circuit breaker with a fallback covers longer outages

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/architecture/h-distributed-systems/03-backoff-breaker" ai="no-ai" title="Exponential backoff and a circuit breaker"}
Implement capped exponential backoff and a three-state circuit breaker (closed → open → half-open). The tests check the doubling-and-cap of the delays and drive the breaker through a failure streak, the cooldown, a half-open trial, and recovery.
:::

:::hints
- `backoff_delay(attempt, base, cap)` = `min(cap, base * (2 ** attempt))`, with `attempt` starting at 0.
- Breaker state: track `state`, `failures`, and `opened_at`. `allow(now)` returns True in CLOSED; in OPEN returns False until `now - opened_at >= cooldown`, then flips to HALF-OPEN and returns True.
- `on_success` → CLOSED, reset failures. `on_failure(now)` → count failures; at the threshold (or any failure while HALF-OPEN) go OPEN and set `opened_at = now`.
:::

## ✅ Quick check

:::quiz
Why add jitter to exponential backoff instead of using fixed doubling delays?

Without jitter, many clients that failed at the same moment retry at the exact same times, creating synchronized waves (a thundering herd) that keep overwhelming the service. Jitter randomizes each client's wait so retries spread out and the service gets quiet moments to recover.
:::

:::quiz
What does an open circuit breaker do, and how does it help both sides?

It blocks calls immediately (fail fast, or use a fallback) instead of trying a service that's clearly down. This saves your app from wasting time on doomed calls and gives the struggling dependency a break from traffic so it can recover, after which a half-open trial checks if it's healthy again.
:::

## 📚 Keep learning

- [AWS: timeouts, retries, and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
- [Martin Fowler: CircuitBreaker](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Google SRE book: addressing cascading failures](https://sre.google/sre-book/addressing-cascading-failures/)

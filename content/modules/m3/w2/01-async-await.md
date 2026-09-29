---
title: "async/await: When It Helps"
summary: The honest guide to async in FastAPI — how awaiting frees the server to handle other requests during I/O waits, why it does nothing for CPU-bound work, and how gather runs many I/O calls at once instead of one after another.
type: lesson
source: original
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: recommended }
durationMinutes: 110
tags: [fastapi, async, await, concurrency, performance]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What `async def` and `await` actually do
- Why async helps **I/O-bound** work but not **CPU-bound** work
- How the server serves other requests while one waits
- Running many I/O calls at once with `asyncio.gather`
- The traps: blocking calls inside async, and using async where it won't help

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **async / await** | Mark code that can pause while waiting | Menandai kode yang bisa jeda |
| **I/O-bound** | Work that mostly waits (network, disk, DB) | Kerja yang kebanyakan menunggu |
| **CPU-bound** | Work that mostly computes | Kerja yang kebanyakan menghitung |
| **Event loop** | The scheduler that runs async tasks | Penjadwal tugas async |
| **Concurrency** | Making progress on many things at once | Maju banyak hal sekaligus |
| **gather** | Run several awaitables at the same time | Menjalankan banyak sekaligus |
| **Blocking** | Code that stops everything while it runs | Kode yang menghentikan semua |

## 🧠 The big idea

Async is a **waiter serving many tables**. While the kitchen cooks table 1's order (an I/O wait), the waiter doesn't stand and stare — they take table 2's order and refill table 3's water. One waiter, many tables, because most of the time is spent *waiting* on the kitchen, not doing the cooking. But if the waiter had to personally chop all the vegetables (CPU work), a second body would be needed — one waiter can't speed that up.

## ❓ Why it matters

FastAPI is popular partly because it makes async easy. But async is widely misunderstood: people sprinkle `async` everywhere expecting speed, or block the event loop and make things *slower*. The honest rule — **async helps when you wait on I/O, not when you compute** — is what lets you use it correctly. For a service that calls a database, other APIs, and an AI model, async can multiply throughput; for number-crunching, it does nothing.

## 📖 Step by step

### 1. What await does

`await` marks a point where the function can **pause** while something else finishes, handing control back to the **event loop** so it can run other work:

```python
@app.get("/profile")
async def profile():
    user = await db.fetch_user()      # pause here; loop serves other requests
    posts = await api.fetch_posts()   # pause again
    return {"user": user, "posts": posts}
```

During each `await`, the server isn't stuck — it handles other incoming requests. That's the whole win.

### 2. I/O-bound vs CPU-bound

| Kind | Example | Does async help? |
|---|---|---|
| **I/O-bound** | DB query, HTTP call, reading a file, LLM call | ✅ yes — the wait is freed |
| **CPU-bound** | resizing an image, big math, parsing a huge file | 🚫 no — nothing to wait on |

Async doesn't add CPUs. If the work is *computing*, there's no idle wait to reuse, so `async` gives no speedup (and can block the loop). Heavy CPU work belongs in a background worker or a process pool.

### 3. Running calls concurrently with gather

Two independent I/O calls shouldn't run one-after-another. `asyncio.gather` runs them **at the same time**:

```python
import asyncio

# Sequential: total ≈ time(a) + time(b)
user = await fetch_user()
posts = await fetch_posts()

# Concurrent: total ≈ max(time(a), time(b))
user, posts = await asyncio.gather(fetch_user(), fetch_posts())
```

For a page that needs three independent sources, gather can turn 3× the wait into 1× the wait.

### 4. The blocking trap

Inside an `async def`, calling a **blocking** function (a synchronous DB driver, `time.sleep`, heavy CPU) freezes the whole event loop — every other request waits too. Rules:

- Use **async libraries** for I/O inside async handlers (async DB driver, `httpx.AsyncClient`).
- For unavoidable blocking/CPU work, offload it (`run_in_executor`, a worker/queue).
- If a handler has no `await` and does only quick sync work, a plain `def` handler is fine — FastAPI runs it in a threadpool.

### Choosing sync vs async

| Situation | Use |
|---|---|
| Handler awaits DB/HTTP/LLM I/O | `async def` + async libraries |
| Several independent I/O calls | `async def` + `asyncio.gather` |
| Quick sync work, no waiting | plain `def` is fine |
| Heavy CPU work | offload to a worker/executor, don't block the loop |

- ✅ Use async for I/O-bound handlers and gather independent calls.
- ✅ Keep everything inside an async handler non-blocking.
- 🚫 Don't use async for CPU work; don't call blocking libraries in async handlers.

## ⚠️ Common mistakes

- Adding `async` everywhere expecting speed, even for CPU work — no benefit, possible harm.
- Calling a **blocking** library (sync DB driver, `time.sleep`, `requests`) inside `async def`, freezing the loop.
- Awaiting independent calls sequentially when `gather` could run them at once.
- Doing heavy computation in an async handler and starving other requests.
- Mixing sync and async DB sessions without care.

:::revoshop
Look at RevoShop's I/O. (1) The Midtrans call and DB queries are I/O-bound — in FastAPI they'd be good `async` candidates; identify them. (2) Is there any CPU-heavy step (e.g. generating a report/PDF) that should NOT be async but offloaded to a worker? (3) A checkout page might load the cart, the user, and shipping options — could `gather` fetch these concurrently instead of one-by-one?
:::

## 🏆 Best practices

- [ ] Use `async def` only when the handler awaits I/O; plain `def` for quick sync work.
- [ ] Never call blocking libraries inside async handlers — use async clients/drivers.
- [ ] Run independent I/O calls with `asyncio.gather` to cut total wait.
- [ ] Offload CPU-heavy work to a worker/executor, keeping the event loop free.
- [ ] Measure before assuming async made things faster.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain async with the one-waiter-many-tables analogy, and state clearly why it helps I/O-bound work but not CPU-bound work. Then explain what `asyncio.gather` changes for two independent calls.

## 📐 Design it

CareerPilot's dashboard endpoint needs: the user's profile (DB), their applications (DB), and a "jobs you might like" list from an external partner API. Each takes ~150 ms. Design the handler: sync or async, sequential or gathered, and estimate the latency for each approach. Note any step that must not block the loop.

:::quiz
Show a possible design

**Async + gather.** All three are I/O-bound (two DB reads, one external API), so use `async def` with async DB/HTTP clients. The three calls are independent, so run them with `asyncio.gather`:

```python
@app.get("/dashboard")
async def dashboard(user_id: int):
    profile, apps, jobs = await asyncio.gather(
        fetch_profile(user_id),
        fetch_applications(user_id),
        fetch_recommended_jobs(user_id),
    )
    return {"profile": profile, "applications": apps, "jobs": jobs}
```

**Latency:** sequential awaits ≈ 150 + 150 + 150 = **~450 ms**; gathered ≈ **~150 ms** (the longest single call). Async also lets the server handle *other* users' requests during those waits.

**Must not block:** use async clients (async DB driver, `httpx.AsyncClient`) — a synchronous driver here would freeze the loop and cancel the benefit. Any CPU-heavy post-processing should be kept out of the handler.

**Rule shown:** async + gather turns independent I/O waits from additive into parallel, while keeping the server responsive to other requests.
:::

### 📝 Self-review checklist

- [ ] Async used because the work is I/O-bound
- [ ] Independent calls run with `gather`
- [ ] Only async (non-blocking) clients used inside the handler
- [ ] CPU-heavy work kept off the event loop

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m3/w2/01-async-gather" ai="no-ai" title="Sequential vs concurrent I/O"}
Implement two async functions that call a fake async `fetch` for several ids: one that awaits them one-by-one, and one that runs them all at once with `asyncio.gather`. A shared counter proves the concurrent version has all calls in flight simultaneously while the sequential one never exceeds one. The tests run them with `asyncio.run` — no timing, fully deterministic.
:::

:::hints
- The fake `fetch` increments a shared `in_flight` counter on entry, records the max seen, `await asyncio.sleep(0)` to yield, then decrements and returns the id.
- `fetch_all_sequential`: `for id in ids: results.append(await fetch(id))` → max in-flight stays 1.
- `fetch_all_concurrent`: `await asyncio.gather(*(fetch(i) for i in ids))` → max in-flight equals len(ids).
- Both must return results for every id (concurrent returns them in input order via gather).
:::

## ✅ Quick check

:::quiz
Why does `async` speed up an I/O-bound endpoint but not a CPU-bound one?

For I/O work, the handler spends most time *waiting* (on a DB, API, or file), and `await` lets the server use that idle time to serve other requests. CPU work has no idle wait — the code is busy computing — so async can't reuse anything and may even block the event loop.
:::

:::quiz
Your async handler needs data from two independent services. What do you use, and what changes?

`asyncio.gather` — it runs both awaitables at the same time, so total latency is about the *longer* of the two instead of their sum. Awaiting them one after another would add the waits together.
:::

## 📚 Keep learning

- [FastAPI: async and await](https://fastapi.tiangolo.com/async/)
- [Python docs: asyncio — gather](https://docs.python.org/3/library/asyncio-task.html#asyncio.gather)
- [Real Python: async IO in Python](https://realpython.com/async-io-python/)

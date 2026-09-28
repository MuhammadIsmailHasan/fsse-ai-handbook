---
title: "How to Approach System Design"
summary: A repeatable framework for any system design question — clarify requirements, estimate scale, sketch the API and data model, then the high-level design and bottlenecks — worked end to end on a classic URL shortener.
type: lesson
source: original
roles: { be: core, fe: recommended, fs: core, ai: recommended, ops: recommended }
durationMinutes: 140
tags: [architecture, system-design, interview, url-shortener, scalability]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- A step-by-step **framework** you can use for any design question
- How to turn a vague prompt into clear **requirements**
- Rough **back-of-the-envelope** scale estimates
- Sketching an **API** and a **data model** before drawing boxes
- A full worked example: designing a **URL shortener**
- How to talk about **bottlenecks** and trade-offs like a senior engineer

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Functional requirement** | What the system must *do* | Apa yang harus dilakukan |
| **Non-functional** | How well it must do it (fast, reliable) | Seberapa baik melakukannya |
| **Back-of-envelope** | A rough estimate to size the system | Perkiraan kasar |
| **Read-heavy** | Far more reads than writes | Jauh lebih banyak baca |
| **Bottleneck** | The part that limits the whole system | Bagian yang membatasi |
| **Base62** | Encoding numbers using 0-9, a-z, A-Z | Kode angka pakai 62 simbol |

## 🧠 The big idea

A system design question is like being asked to **design a house**. You don't start laying bricks. You first ask **who lives here and what do they need** (requirements), estimate **how big** (scale), agree on the **rooms and doors** (API and data), then sketch the **floor plan** (high-level design), and finally check **where it might crack** (bottlenecks). Same order, every time.

## ❓ Why it matters

System design comes up in senior interviews and, more importantly, in real projects when you plan a feature. Beginners freeze because the prompt ("design Twitter") feels huge. A **framework** turns that panic into a calm, ordered conversation — and interviewers are grading your *process and trade-offs*, not one magic right answer.

## 📖 Step by step

### The framework (memorize this order)

1. **Clarify requirements** — functional (what it does) and non-functional (scale, latency, reliability). Ask questions; don't assume.
2. **Estimate scale** — rough reads/writes per second and storage. This decides everything downstream.
3. **Define the API** — the handful of endpoints, their inputs and outputs.
4. **Design the data model** — the main tables/entities and keys.
5. **High-level design** — the boxes (clients, servers, database, cache) and how requests flow.
6. **Deep-dive & bottlenecks** — find the part under most pressure and address it (cache, replicas, sharding — from earlier lessons).

Now let's apply all six to a real prompt.

### Worked example: design a URL shortener (like bit.ly)

**1. Requirements**
- Functional: given a long URL, return a short one; visiting the short URL redirects to the long one.
- Non-functional: redirects must be **fast** (they're on the critical path of every click), highly available, and links shouldn't collide.
- Clarifying questions: custom aliases? link expiry? analytics? (Assume: no custom alias for v1, optional expiry, basic click counts.)

**2. Estimate scale**
- Say 100M new links/month, and it's very **read-heavy** — people click far more than they create. Assume 100:1 reads:writes.
- Writes ≈ 100M / (30 × 86,400) ≈ **~40 writes/sec**; reads ≈ **~4,000 reads/sec**.
- Storage: 100M/month × 12 × ~500 bytes ≈ tens of GB/year — small. The challenge is **fast reads**, not storage.

**3. API**
```
POST /shorten   { "url": "https://very/long/link" }  → { "short": "aB3xY" }
GET  /{code}                                          → 302 redirect to the long URL
```

**4. Data model**
```
links( id BIGSERIAL PK, code VARCHAR UNIQUE, long_url TEXT,
       created_at, expires_at NULL, clicks BIGINT DEFAULT 0 )
```
Index `code` (every redirect looks up by it).

**5. Generating the short code**
Use the row's auto-increment `id` and encode it in **base62** (0-9, a-z, A-Z). A base62 string of length 7 covers 62⁷ ≈ 3.5 trillion links — plenty — and the codes are short and collision-free because ids are unique.

```
id 125 → base62 → "cb"     (short, unique, no random collisions)
```

**6. High-level design & the bottleneck**
```
             ┌──────── cache (Redis): code → long_url ───────┐
 client ──▶ app servers ──▶                                   ──▶ PostgreSQL
   click        │  (redirect: check cache, then DB)                (source of truth)
```
- The **bottleneck is redirect reads** (4,000/sec, latency-critical). Fix with the tools you learned: **cache** hot codes in Redis (most clicks go to popular links), add **read replicas**, and put the redirect behind a CDN/edge if global.
- Writes are only ~40/sec — a single PostgreSQL primary handles them easily.

### The senior touch: trade-offs out loud

- Base62-of-id vs random codes: id-based is collision-free and simple, but leaks rough creation order/volume; a random or hashed code hides that at the cost of collision checks. State the trade-off and pick one.
- Redirect uses `302` (temporary) if you want click analytics on every hit, or `301` (permanent) for best caching but fewer analytics. Name the choice.

### Using the framework

| Step | Skip it and… |
|---|---|
| Requirements | You build the wrong thing |
| Estimate scale | You over- or under-engineer |
| API + data model | Your boxes don't connect to anything real |
| High-level design | You can't reason about flow |
| Bottlenecks | You miss the part that actually breaks |

- ✅ Always go in order; say your assumptions aloud.
- ✅ Let the scale numbers drive the design (read-heavy → cache + replicas).
- 🚫 Don't jump to "microservices and Kafka" before requirements and scale.

## ⚠️ Common mistakes

- Designing before clarifying — solving a problem the interviewer didn't ask.
- Skipping estimates, then can't justify why you need a cache or replicas.
- Jumping to complex tech (sharding, microservices) for a system that doesn't need it.
- Forgetting the read/write ratio, which usually decides the whole shape.
- Never naming a trade-off — the interview is *about* trade-offs.

:::revoshop
Apply the framework to a RevoShop feature: "design product search". (1) Requirements: what must search do (by name, category, price), how fast, how fresh? (2) Estimate: is search read-heavy? Roughly how many searches/sec at 10k daily users? (3) Sketch the API, the data/index needed, and name the likely bottleneck (a full-text index vs a `LIKE` scan) and how you'd fix it.
:::

## 🏆 Best practices

- [ ] Start every design with functional + non-functional requirements and clarifying questions.
- [ ] Do rough scale math; let the read/write ratio and storage drive the design.
- [ ] Define the API and data model before drawing the architecture.
- [ ] Identify the single biggest bottleneck and address it with known tools (cache, replicas, sharding).
- [ ] Say trade-offs out loud and make an explicit choice.
- [ ] Keep v1 as simple as the requirements allow; note what you'd add later.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain the six-step framework using the design-a-house analogy. Then, in two sentences, say why a URL shortener is "read-heavy" and what that implies for its design.

## 📐 Design it

Use the full framework to design a **pastebin** (users paste text, get a short link others can view; pastes can expire). Go through all six steps: requirements, a scale estimate, the API, the data model, the high-level design, and the main bottleneck with a fix.

:::quiz
Show a possible design

- **Requirements**: create a paste (text, optional expiry, optional syntax), view a paste by its short id; fast reads, private-by-obscurity links; no editing in v1.
- **Scale**: read-heavy like the URL shortener (more views than creates). Say 1M pastes/month → ~0.4 writes/sec, ~40 reads/sec at 100:1 — small; storage grows with text size, so cap paste size (e.g. 1 MB) and store large bodies in object storage (S3), keeping metadata in the DB.
- **API**: `POST /pastes {text, expires_at?}` → `{id}`; `GET /{id}` → the paste (or 404/410 if expired).
- **Data model**: `pastes(id, code UNIQUE, body_ref, created_at, expires_at)`. Code via base62 of the id.
- **High-level**: clients → app servers → PostgreSQL (metadata) + object storage (big bodies); Redis cache for hot pastes.
- **Bottleneck**: read latency on popular pastes and large bodies. Fix: cache hot pastes in Redis, serve big bodies from object storage/CDN, and a background job deletes expired pastes.

**Rule shown:** the same six-step framework and the same tools (cache, replicas, object storage) solve a new prompt — the skill is the process, not memorized answers.
:::

### 📝 Self-review checklist

- [ ] Requirements (functional + non-functional) stated with assumptions
- [ ] A rough scale estimate that drives the design
- [ ] API and data model defined before architecture
- [ ] One clear bottleneck named and addressed with a known tool

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/architecture/i-system-design-practice/01-url-shortener" ai="no-ai" title="Base62 short codes and a capacity estimate"}
Implement the core of a URL shortener: encode an auto-increment id to a base62 short code and decode it back, plus a couple of back-of-the-envelope helpers (writes/sec from monthly volume, and how many links a code length can address). The tests check the round-trip and the estimates.
:::

:::hints
- Base62 alphabet: `0-9` then `a-z` then `A-Z` (indexes 0–61). `encode(0)` should be `"0"`.
- `encode`: repeatedly take `n % 62`, prepend the letter, `n //= 62`. `decode`: fold digits back with `n = n*62 + value`.
- `writes_per_sec(monthly)` = `monthly / (30 * 86400)`. `capacity(code_len)` = `62 ** code_len`.
:::

## ✅ Quick check

:::quiz
What are the first two steps of the framework, and why do they come first?

Clarify requirements (functional + non-functional), then estimate scale. They come first because they define *what* you're building and *how big*, which drive every later decision — the API, data model, and especially where the bottlenecks (and the need for caches/replicas) will be.
:::

:::quiz
A URL shortener is heavily read-dominated. What does that imply for its design?

That the redirect (read) path is the critical bottleneck, not writes or storage. You optimize reads: cache hot codes in Redis, add read replicas, and possibly serve redirects from a CDN/edge, while a single primary easily handles the small write volume.
:::

## 📚 Keep learning

- [System Design Primer (GitHub)](https://github.com/donnemartin/system-design-primer)
- [ByteByteGo: how to answer a system design interview](https://bytebytego.com/)
- [Designing a URL shortener — worked example](https://www.educative.io/courses/grokking-the-system-design-interview/m2ygV4E81AR)

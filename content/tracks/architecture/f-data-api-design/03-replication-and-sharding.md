---
title: "Replication & Sharding"
summary: Two ways to grow a database past one machine — replication (copies for more reads and safety) and sharding (splitting data across machines for more writes) — plus their real costs, replication lag and hard cross-shard queries.
type: lesson
source: original
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: core }
durationMinutes: 120
tags: [architecture, database, replication, sharding, scaling, postgresql]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- **Replication**: keeping copies of a database for more reads and safety
- What **replication lag** is and the bug it causes
- **Sharding**: splitting one big table across several machines
- How a **shard key** is chosen and what a **hotspot** is
- Why cross-shard queries and transactions are hard
- The order to reach for these (and why you probably don't need sharding yet)

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Replication** | Keeping live copies of the same database | Menyalin database secara langsung |
| **Primary** | The one copy that accepts writes | Salinan yang menerima tulis |
| **Replica** | A read-only copy kept in sync with the primary | Salinan hanya-baca |
| **Replication lag** | The short delay before a write reaches replicas | Jeda sebelum tulis sampai ke replika |
| **Sharding** | Splitting rows across several databases | Membagi baris ke banyak database |
| **Shard key** | The value that decides which shard a row lives on | Kunci penentu shard |
| **Hotspot** | One shard getting far more traffic than the others | Satu shard kelebihan beban |
| **Failover** | Promoting a replica when the primary dies | Mengangkat replika saat primary mati |

## 🧠 The big idea

**Replication** is **photocopying a ledger**: one master copy (the **primary**) is where you write, and several photocopies (**replicas**) are handed out so many people can *read* at once. Copies are made fast, but for a split second a photocopy can be slightly behind the master.

**Sharding** is **splitting one huge phone book into A–M and N–Z volumes**, each kept in a different room. No single volume is too heavy — but "list everyone named Ismail" now means visiting *both* rooms.

## ❓ Why it matters

One database on one machine has a ceiling: only so many reads, writes, and so much data fit. Two very different problems hit that ceiling, and they need different tools:

- **Too many reads** (a busy shop's product pages) → **replication**.
- **Too many writes / too much data for one machine** → **sharding**.

Reaching for the wrong one — or for sharding far too early — adds huge complexity for no gain. Knowing which problem you have is the whole skill.

## 📖 Step by step

### 1. Replication: copies for reads and safety

You keep one **primary** (accepts writes) and one or more **replicas** (read-only copies). The primary streams every change to the replicas.

```
        writes                 reads
  app  ───────▶  PRIMARY  ──▶  REPLICA 1  ◀───  app
                    │      ──▶  REPLICA 2  ◀───  app
                    └──────▶ (stream of changes)
```

Two big wins:
- **Scale reads**: send read queries to replicas, so the primary is freed up. Most apps read far more than they write, so this helps a lot.
- **Safety / failover**: if the primary dies, promote a replica to be the new primary (**failover**).

### 2. The catch: replication lag

Copies are not *instant*. For a short moment a replica can be slightly behind the primary — this is **replication lag**. It causes a classic bug:

```
1. User updates their profile name    → written to PRIMARY
2. Page reloads, reads from a REPLICA → replica hasn't caught up yet
3. User sees their OLD name and thinks the save failed
```

Fix: read your **own** just-written data from the primary (or wait for the replica to catch up). This is called "read-your-writes". Reads that can tolerate being a second stale (a product listing) are fine on replicas.

### 3. Sharding: splitting the data itself

Replication copies the *whole* database many times — it does not help when the data is too big or writes are too many for one machine. **Sharding** splits the rows across machines:

```
users 1–1,000,000      → SHARD A
users 1,000,001–2,000,000 → SHARD B
users 2,000,001–3,000,000 → SHARD C
```

Each shard is a full database holding a **slice** of the rows. Writes and storage are now spread across machines.

### 4. The shard key decides everything

The **shard key** is the value used to pick a row's shard (often via a hash):

```python
shard = hash(user_id) % number_of_shards
```

Choosing it well is the hard part:
- Pick a key that **spreads load evenly**. `user_id` is usually good; `country` is bad if 90% of users are in one country (that shard becomes a **hotspot**).
- Pick a key you **already have** when you query. If you shard by `user_id` but often search by `email`, you don't know which shard to ask → you must query them all.

### 5. Why sharding is painful

| Easy on one DB | With sharding |
|---|---|
| JOIN across all data | ❌ data lives on different machines |
| `COUNT(*)` over everything | ❌ must ask every shard and add up |
| A transaction spanning two users | ❌ crosses machines — very hard |
| Adding capacity | ⚠️ resharding moves lots of data |

This is why sharding is a **last resort**. You add real, permanent complexity to every query and transaction.

### The order to reach for scaling

| Step | Do this first |
|---|---|
| 1 | Optimize: add indexes, fix slow queries, cache hot reads (Redis) |
| 2 | Scale up: a bigger machine (more CPU/RAM) — boringly effective |
| 3 | **Replication**: move reads to replicas |
| 4 | **Sharding**: only when one machine genuinely can't hold the writes/data |

- ✅ Solve read scaling with caching and replicas long before sharding.
- ✅ If you must shard, choose a shard key that spreads load and matches your queries.
- 🚫 Don't shard "to be ready" — most apps never need it, and it slows down all your development.

## ⚠️ Common mistakes

- Reading just-written data from a replica and showing users stale results (replication lag).
- Treating a replica as a backup — it copies mistakes too (a `DELETE` replicates instantly). You still need real backups.
- Sharding by a skewed key (`country`, `is_premium`) and creating a hotspot.
- Sharding early, then fighting cross-shard JOINs and counts forever.

:::revoshop
RevoShop runs on one PostgreSQL. (1) Which pages are **read-heavy** (product listings, product detail) and could safely use a replica? Which reads must be fresh (the buyer's own cart/order right after checkout)? (2) If RevoShop ever had to shard, what shard key would spread load and match its main queries — `user_id`, `order_id`, or `product_id`? What query would become painful? (3) Before sharding, what cheaper steps (indexes, Redis caching, a bigger machine, a read replica) would you try first?
:::

## 🏆 Best practices

- [ ] Exhaust indexes, caching, a bigger machine, and read replicas before sharding.
- [ ] Send tolerant reads to replicas; read-your-own-writes from the primary.
- [ ] Keep real backups — replicas are not backups (they copy deletes too).
- [ ] If sharding, pick a shard key that spreads load evenly and that you have at query time.
- [ ] Design to avoid cross-shard JOINs/transactions; keep related data on the same shard.
- [ ] Have a tested failover plan so promoting a replica isn't your first attempt during an outage.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain replication vs sharding with the photocopied-ledger and split-phone-book analogies. Then explain replication lag: why a user might update their name and briefly still see the old one.

## 📐 Design it

A social app has 50 million users. The feed (reading posts) is 95% of traffic; posting is 5%. Later, the *posts* table alone grows too big for one machine. Design the scaling path: what you do for the read-heavy feed, and what you'd do when the posts table outgrows a single machine — including the shard key and one query that gets harder.

:::quiz
Show a possible design

**Read-heavy feed first → replication + cache.** Add read replicas and route feed reads to them; cache hot feeds in Redis. This handles the 95% cheaply. Writes (posting) still go to the primary — 5% is easy for one machine.

**Posts table too big → shard the posts.** Shard key: `user_id` (the author), so all of one user's posts sit on one shard and "show this user's posts" hits a single shard. Hash `user_id` to spread load evenly.

**What gets harder:** a global feed mixing many authors, or "count all posts today", now spans every shard — you must query all shards and merge, or precompute feeds/counts. Read-your-writes (a user seeing their own new post) should read from the primary or their own shard.

**Rule shown:** replicate for reads, shard only the one table that truly outgrows a machine, and pick a shard key that keeps each user's data together.
:::

### 📝 Self-review checklist

- [ ] Read scaling solved with replicas/cache before any sharding
- [ ] Shard key spreads load and matches the main query
- [ ] A now-hard cross-shard query is named
- [ ] Freshness handled (read-your-writes from primary)

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/architecture/f-data-api-design/03-sharding" ai="no-ai" title="Shard router and the resharding cost"}
Implement a hash-based shard router, a read/write router (writes → primary, reads → replica), and a function that counts how many keys change shard when you go from N to N+1 shards. The tests show that naive `hash % n` sharding moves *most* keys on a resize — the reason real systems use consistent hashing.
:::

:::hints
- Use a stable hash (`hashlib.md5`), not Python's built-in `hash()`, so results are the same every run.
- `shard_for(key, n)` = `stable_hash(key) % n`.
- `keys_moved` : count keys whose `shard_for(key, old_n) != shard_for(key, new_n)`.
- Read/write router: writes always go to `"primary"`; reads go to `"replica"`.
:::

## ✅ Quick check

:::quiz
You have far too many read requests but writes are fine. Replication or sharding?

**Replication.** Add read replicas and send read queries to them, freeing the primary. Sharding is for when writes or data size outgrow one machine — a different problem.
:::

:::quiz
Why is choosing a good shard key so important?

Because it decides both load balance and query cost: a skewed key creates a hotspot (one overloaded shard), and a key you don't have at query time forces you to ask every shard. A good key spreads load evenly and matches how you query.
:::

## 📚 Keep learning

- [PostgreSQL: high availability & replication](https://www.postgresql.org/docs/current/high-availability.html)
- [Martin Kleppmann, *DDIA*, Ch. 5–6 (replication, partitioning)](https://dataintensive.net/)
- [Consistent hashing explained](https://www.toptal.com/big-data/consistent-hashing)

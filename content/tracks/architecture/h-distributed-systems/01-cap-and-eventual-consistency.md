---
title: "CAP & Eventual Consistency"
summary: What happens when parts of a system can't talk — the CAP idea in plain words, why a network split forces a choice between consistency and availability, and how eventual consistency lets replicas disagree briefly then converge.
type: lesson
source: original
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: core }
durationMinutes: 120
tags: [architecture, distributed-systems, cap, consistency, availability, replication]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What a **network partition** is and why it's unavoidable at scale
- The **CAP** idea, explained without the scary theory
- Why a partition forces a choice: **consistency** or **availability**
- What **eventual consistency** means and how replicas **converge**
- **Last-write-wins** as one simple way to resolve conflicts
- Which choice fits which feature (bank balance vs like count)

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Node** | One server in a group that work together | Satu server dalam kelompok |
| **Partition** | Nodes can't talk to each other for a while | Node terputus sementara |
| **Consistency (CAP)** | Everyone reads the same latest value | Semua baca nilai terbaru sama |
| **Availability** | Every request still gets an answer | Tiap request tetap dijawab |
| **Eventual consistency** | Copies disagree briefly, then match up | Sesaat beda, lalu sama |
| **Converge** | Replicas settle on the same final value | Menyatu ke nilai sama |
| **Last-write-wins** | On a clash, the newest write wins | Tulis terbaru menang |

## 🧠 The big idea

Imagine two cashiers at a **warung** who normally sync their notebooks. Suddenly the phone line between them drops (a **partition**). A customer wants to pay. Two choices:

- **Stay consistent**: "Sorry, I can't reach the other cashier to be sure — please wait." (Refuse to risk a wrong answer.)
- **Stay available**: "Sure, I'll record it and we'll sync later." (Answer now, reconcile afterward.)

You cannot have both while the line is down. That trade-off is the whole of **CAP**.

## ❓ Why it matters

Once your data lives on more than one machine, networks *will* fail sometimes — cables, switches, whole data centers. This isn't rare; at scale it's constant. CAP tells you the honest truth: **during** a partition you must pick consistency or availability. Pretending otherwise leads to systems that quietly show wrong data or freeze at the worst moment.

Knowing this lets you choose *per feature*: a bank balance should refuse rather than be wrong; a like count can happily be a little behind.

## 📖 Step by step

### 1. The three letters

CAP is about three properties of a system spread across **nodes**:

- **C — Consistency**: every read sees the most recent write (all nodes agree).
- **A — Availability**: every request gets a (non-error) response.
- **P — Partition tolerance**: the system keeps working even when nodes can't talk.

### 2. The real rule: P is not optional

At scale, partitions *happen*, so **P is a given** — you don't get to opt out of network failures. That means the real choice, **during a partition**, is between **C and A**:

- **CP** (choose consistency): refuse or block requests that can't be made consistent. The bank cashier who says "please wait".
- **AP** (choose availability): answer anyway and reconcile later. The cashier who records it and syncs afterward.

(When there is *no* partition, a good system gives you both C and A. CAP is about the failure moment.)

### 3. Eventual consistency: the AP way

An **AP** system accepts writes on whichever node it can reach, so for a short time two replicas can hold different values. Then, once they can talk again, they exchange updates until they **converge** on the same value. This is **eventual consistency**: not wrong forever, just *briefly* out of date.

```
Partition:
  Replica A:  likes = 10  (+1 here → 11)
  Replica B:  likes = 10  (+1 there → 11)   ← can't see A
Heal + merge:
  Both →      likes = 12                      ← converge
```

You see this every day: a YouTube view count that differs between refreshes, a social post that shows for you before your friend sees it.

### 4. Resolving conflicts: last-write-wins

When two replicas changed the *same* value during a partition, merging must pick a winner. The simplest rule is **last-write-wins (LWW)**: attach a timestamp to each write; on merge, keep the one with the newer timestamp.

```python
def merge(a, b):
    # a, b are (value, timestamp); keep the newer write
    return a if a.timestamp >= b.timestamp else b
```

LWW is simple but can *lose* one of two concurrent edits. Richer systems use smarter merges (e.g. counters that add up, or CRDTs) — but LWW is the one to understand first.

### Choosing consistency vs availability, per feature

| Feature | Choose | Why |
|---|---|---|
| Bank balance, stock at checkout | **CP** (consistency) | A wrong answer is worse than a slow one |
| Like counts, view counts, feeds | **AP** (availability) | Being briefly behind is fine; downtime isn't |
| Username uniqueness | **CP** | Two people must not grab the same name |
| Shopping cart contents | often **AP** | Merge items later rather than block the user |

- ✅ Decide C-vs-A per feature, based on the cost of a wrong vs. missing answer.
- ✅ For AP features, design how replicas converge and resolve conflicts.
- 🚫 Don't assume "strongly consistent everywhere" is free — it costs availability during partitions.

## ⚠️ Common mistakes

- Believing you can have C, A, and P all at once during a partition — you can't.
- Using an eventually-consistent store for money or stock, then seeing impossible totals.
- Reading from a replica right after writing and assuming it's up to date (see replication lag).
- Ignoring conflict resolution, so a merge silently loses one user's change.
- Treating rare partitions as impossible — at scale they're routine.

:::revoshop
RevoShop is one PostgreSQL today (strongly consistent). (1) Which parts *must* stay consistent even if it means an error — stock at checkout, payment status? (2) Which parts could tolerate eventual consistency if RevoShop grew — a "products viewed" count, a homepage "trending" list? (3) If two admins edited the same product during a network hiccup between replicas, what would last-write-wins do, and could that silently lose an edit?
:::

## 🏆 Best practices

- [ ] Treat partition tolerance as mandatory; decide C-vs-A per feature for the partition case.
- [ ] Keep money, stock, and uniqueness on strongly consistent (CP) paths.
- [ ] For AP features, define convergence and a conflict-resolution rule up front.
- [ ] Prefer merge rules that don't lose data (counters, sets) over plain last-write-wins where edits matter.
- [ ] Set user expectations for eventual data ("counts may take a moment to update").
- [ ] Test behavior *during* a simulated partition, not just when everything is healthy.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain CAP with the two-cashiers-and-a-dropped-phone-line analogy. Then, in one sentence, say what eventual consistency means and give one everyday example (like a view count).

## 📐 Design it

A global social app shows: (1) account balance for its paid "creator payouts", (2) post like counts, and (3) unique @handles. For each, decide CP or AP during a partition and justify it. Then, for the like counts, describe how two data centers that both received likes during a partition would converge without losing likes.

:::quiz
Show a possible design

- **(1) Creator balance → CP.** Money must be correct; during a partition, block or error rather than risk a wrong balance or double payout. Slow is acceptable; wrong is not.
- **(2) Like counts → AP.** Availability matters more than being exact for a second. Each data center accepts likes during the partition and they reconcile after.
- **(3) Unique @handles → CP.** Uniqueness requires agreement; two centers must not both hand out `@ismail`. Registration blocks during a partition rather than risk a duplicate.

**Converging like counts without loss:** don't use last-write-wins on the *number* (that would throw away one center's likes). Instead treat likes as an **increment** and sum them: each center records "+N" during the partition, and on heal the totals are added (a counter CRDT). So 10 → (+1 here, +1 there) → 12, not 11.

**Rule shown:** choose C-vs-A per feature, and for AP counters use additive merges, not last-write-wins, so no increments are lost.
:::

### 📝 Self-review checklist

- [ ] Each feature has a justified CP-or-AP choice for the partition case
- [ ] Money/uniqueness kept on consistent paths
- [ ] Convergence described for the AP feature
- [ ] Merge rule chosen so data isn't silently lost

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/architecture/h-distributed-systems/01-eventual-consistency" ai="no-ai" title="Diverge during a partition, then converge"}
Model two replicas of a key-value store that take writes independently during a partition, then merge. Implement last-write-wins for single values and an additive merge for counters. The tests show LWW converges both replicas to the same state (but can drop a concurrent edit), while the counter merge converges without losing any increments.
:::

:::hints
- Represent a value as `(value, timestamp)`; `apply` only overwrites if the new timestamp is newer.
- `merge_lww(a, b)`: for each key, keep the entry with the larger timestamp (tie-break deterministically, e.g. larger value).
- `merge_counter(a, b)`: for each key, the converged count is the sum of both sides' increments — never just one side's.
:::

## ✅ Quick check

:::quiz
During a network partition, which two CAP properties must you choose between, and why not all three?

You choose between **Consistency** and **Availability**, because partition tolerance (P) is unavoidable once data is on multiple machines — the network *will* split. While it's split, you can either refuse to answer to stay consistent, or answer and reconcile later to stay available, but not both.
:::

:::quiz
Why is last-write-wins a poor choice for merging a like count, and what works better?

LWW keeps only one side's number and throws the other away, losing likes that happened on the other replica. Treating likes as increments and **summing** them (an additive/counter merge) converges without losing any.
:::

## 📚 Keep learning

- [Martin Kleppmann, *DDIA*, Ch. 9 (consistency & consensus)](https://dataintensive.net/)
- [The CAP theorem, explained simply](https://www.ibm.com/think/topics/cap-theorem)
- [A brief introduction to CRDTs](https://crdt.tech/)

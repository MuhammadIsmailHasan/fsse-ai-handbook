---
title: "Sorting Patterns"
summary: Sorting as a problem-solving tool — custom keys and stability, merge sort vs quicksort, intervals and sweep lines, heaps for top-k, partitioning, and counting inversions.
type: lesson
source: original
roles: { be: core, fe: core, fs: core, ai: core, ops: optional }
durationMinutes: 150
tags: [dsa, sorting, intervals, heap, merge-sort, patterns]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- How sorting algorithms compare: merge sort, quicksort, Timsort, counting sort
- **Stability** and multi-key sorting with `key=`
- "Sort first" patterns: intervals, sweep lines, greedy scheduling
- Heaps for **top-k** instead of full sorts
- **Partitioning** (Dutch national flag) and **divide & conquer** (inversions)
- 🧭 How to recognize when sorting unlocks a problem

## 🧠 The big idea

Sorting is like **organizing a messy pile of receipts by date** before doing your taxes. The sorting takes some effort, but afterwards "which receipts overlap this week?", "what's the biggest gap?", "any duplicates?" become simple walks through the pile.

In interviews, the question is rarely "implement a sort" — it's "**would sorting first make this easy**, and is O(n log n) acceptable?"

## ❓ Why does this exist?

Order creates structure: neighbors become meaningful. After sorting:
- duplicates are adjacent,
- overlapping intervals are adjacent,
- two pointers and binary search become possible,
- greedy choices (earliest end time first) become provably correct.

## 💥 What happens if we DON'T use it?

Checking every pair of 50,000 meetings for overlaps is 1.25 billion comparisons. Sorting by start time first makes it one pass after an O(n log n) sort.

The opposite mistake is common too: sorting 10 million items to get the **top 3** — a heap does it in O(n log 3).

## 📖 How it works, step by step

### 1. The algorithms you should be able to explain

| Algorithm | Time (avg / worst) | Space | Stable | Idea |
|---|---|---|---|---|
| **Merge sort** | O(n log n) / O(n log n) | O(n) | ✅ | split in half, sort halves, merge (two pointers!) |
| **Quicksort** | O(n log n) / O(n²) | O(log n) | ❌ | pick a pivot, partition smaller/larger, recurse |
| **Heapsort** | O(n log n) / O(n log n) | O(1) | ❌ | build a heap, pop max repeatedly |
| **Timsort** (Python) | O(n log n) / O(n log n), O(n) on nearly sorted data | O(n) | ✅ | finds existing runs, merges them |
| **Counting sort** | O(n + k) | O(k) | ✅ | when values are small integers (0..k) |

Comparison-based sorting can't beat O(n log n) in general. Counting/radix sorts can because they don't compare.

### 2. Custom keys and stability in Python

```python
jobs.sort(key=lambda job: (-job["salary"], job["title"]))   # salary high→low, then title A→Z
```

- Tuples compare element by element — perfect for multi-key sorts.
- Can't negate strings? Use **stability**: sort by the least important key first, then by more important keys; ties keep their previous order.

```python
by_title = sorted(jobs, key=lambda j: j["title"])
by_date = sorted(by_title, key=lambda j: j["posted_on"], reverse=True)   # newest first, ties stay A→Z
```

- `None` values: sort by `(value is None, value)` to put them last.

### 3. Intervals: sort by start, then merge

```python
merged = []
for start, end in sorted(intervals):
    if merged and start <= merged[-1][1]:     # overlaps (or touches) the last one
        merged[-1][1] = max(merged[-1][1], end)
    else:
        merged.append([start, end])
```

Clarify **touching**: do `[1, 3]` and `[3, 5]` overlap? For calendar slots `[9:00, 10:00)` they don't; for inclusive day ranges they do.

### 4. Sweep line: rooms needed

Turn intervals into events and walk time in order:

```python
starts = sorted(s for s, _ in meetings)
ends = sorted(e for _, e in meetings)
# walk starts; before each start, release every room whose end <= start
```

The maximum number of simultaneous meetings = rooms needed. Same idea: peak concurrent users, max overlapping bookings, busiest hour.

### 5. Top-k with a heap

```python
import heapq
heapq.nlargest(3, scores)          # O(n log k)
# or keep a min-heap of size k and replace its smallest when you see something bigger
```

For k close to n, just sort. For "k-th largest" quickselect averages O(n) (but worst case O(n²)).

### 6. Partitioning in one pass

Three categories (high / medium / low) sorted **in place** with three pointers — the Dutch national flag. This partition step is also the heart of quicksort.

```text
[ high... | medium... | unknown... | low... ]
          low        mid          high
```

### 7. Divide and conquer: counting inversions

Merge sort's merge step knows something useful: when an item from the **right** half is placed before remaining **left** items, it's smaller than all of them — that's `len(left) - i` inversions counted at once. O(n log n) instead of O(n²). The same trick measures how similar two rankings are.

:::tip[🧭 How to spot a sorting pattern]
- **Intervals**, schedules, bookings, overlaps → sort by start (or by end for greedy selection).
- "Maximum simultaneous…", "busiest time" → sweep line over sorted events.
- "Top k", "k-th largest", "closest k" → heap (or quickselect).
- Grouping/duplicates when a hash map isn't allowed → sort, then compare neighbors.
- Ranking with several criteria → a key tuple and stable sorts.
- Only a few distinct values → counting sort / partitioning in O(n).
- Pairs counted with an order condition (`i < j` and `a[i] > a[j]`) → merge sort variant.
:::

## ⚖️ Trade-offs

| Choice | ✅ | ❌ |
|---|---|---|
| Sort first | unlocks two pointers, merging, greedy | O(n log n); loses original order (keep indices if needed) |
| Hash map instead | O(n) | no order-based questions |
| Heap for top-k | O(n log k), streaming-friendly | only the top k, not the full order |
| In-place sort | O(1)–O(log n) extra memory | mutates the caller's data |
| `sorted()` copy | safe | O(n) extra memory |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ Interval/scheduling problems, ranking, neighbors-matter problems, preparing for binary search.
- ✅ When the data is sorted once and queried many times.
- 🚫 A single membership check (O(n) scan or a set beats sorting).
- 🚫 You only need the min/max or top few items → one pass or a heap.

## 🏆 Best practices

- [ ] Use `sorted()`/`.sort()` with `key=` — don't write comparison functions unless you must (`functools.cmp_to_key`).
- [ ] Clarify tie-breaking and `None` handling before coding.
- [ ] Mention stability when sorting by multiple keys.
- [ ] Keep original indices with `sorted(range(n), key=...)` or `enumerate` when you need positions.
- [ ] Prefer `heapq.nlargest/nsmallest` for small k; state O(n log k).
- [ ] For intervals, define open/closed boundaries explicitly.
- [ ] Be able to explain merge sort and quicksort (and why quicksort's worst case happens).

## 🏭 How it's used in industry

- Databases sort for `ORDER BY`, merge joins and index builds (external merge sort when data exceeds memory).
- Calendars and booking systems (meeting rooms, doctor appointments) use interval logic and sweep lines.
- Search and recommendation ranking = multi-key sorts plus top-k heaps.
- Leaderboards: Redis sorted sets.

## ⚠️ Common mistakes

- Sorting the caller's list in place by accident.
- Mixing up `reverse=True` with negated keys and breaking the tie order.
- Merging intervals without sorting first.
- Using full sorts for top-3 of millions of items.
- Advancing `mid` after swapping with `high` in the Dutch flag algorithm (the swapped item is unchecked).

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain merge sort to a friend using two already-sorted stacks of exam papers: how do you combine them into one sorted stack quickly, and how does that idea sort a completely unsorted pile?

## 📐 Design it

CareerPilot adds **interview scheduling**: recruiters publish available slots `[start, end)` and candidates publish theirs. For one recruiter (up to 2,000 slots) and one candidate (up to 2,000 slots), find all common time ranges of at least 45 minutes. Design the algorithm and complexity; then say what changes when one recruiter must be matched against 5,000 candidates.

:::quiz
Show a possible design

**One pair**: sort both slot lists by start (O(n log n + m log m)), **merge** overlapping slots within each list first (a person's own overlapping slots), then walk both with **two pointers**:

```text
i, j = 0, 0
while i < len(A) and j < len(B):
    start = max(A[i].start, B[j].start)
    end = min(A[i].end, B[j].end)
    if end - start >= 45 min: output [start, end)
    if A[i].end < B[j].end: i += 1 else: j += 1     # advance the one that ends first
```

Total O(n log n + m log m) — the walk is O(n + m).

**5,000 candidates**: sort and merge the recruiter's slots once; for each candidate repeat the two-pointer walk → O(R + C_k) per candidate. Precompute and store normalized (sorted, merged) slots in the database so each match is just the linear walk; index by date so you only load slots in the relevant week. Time zones: store in UTC, convert only for display.
:::

### 📝 Self-review checklist

- [ ] Each list sorted and self-overlaps merged first
- [ ] Two-pointer advance rule is justified
- [ ] Minimum-duration check and half-open boundaries handled
- [ ] Scaling to many candidates avoids re-sorting the recruiter

::ai-review{task="design"}

::part[Practice Problems]{n="3"}

:::problem{id="dsa-s3-sorting-basics" title="Sorting Basics" difficulty="easy" path="exercises/dsa/stage-3/17-sorting-basics"}
Multi-key job ranking with stable sorts, merging intervals, and k-th largest with a heap.
:::

:::problem{id="dsa-s3-interview-rooms" title="Interview Rooms Needed" difficulty="medium" path="exercises/dsa/stage-3/18-meeting-rooms"}
Sweep line over sorted start and end times to find peak concurrency.
:::

:::problem{id="dsa-s3-priority-partition" title="Sort Tasks by Priority in One Pass" difficulty="medium" path="exercises/dsa/stage-3/19-three-way-partition"}
The Dutch national flag algorithm: three-way partition in place.
:::

:::problem{id="dsa-s3-count-inversions" title="How Different Are Two Rankings?" difficulty="hard" path="exercises/dsa/stage-3/20-count-inversions"}
Stretch: count inversions in O(n log n) by extending merge sort.
:::

:::hints
- `rank_jobs`: `key=lambda j: (j["salary_max"] is None, -(j["salary_max"] or 0))` handles salary; use a stable earlier sort for "newest date first" on strings.
- `merge_intervals`: `sorted(intervals)` sorts by start, then end.
- `rooms_needed`: process `ends[e] <= start` before taking a room for `start`, because a room frees **at** its end time.
- `sort_priorities`: when you swap a `"low"` to the end, don't move `mid` — check the swapped-in item next.
- `count_inversions`: a bottom-up (iterative) merge sort avoids Python's recursion limit on large inputs.
:::

## ✅ Quick check

:::quiz
What does "stable sort" mean, and why does it matter for multi-key sorting?

Items that compare equal keep their original relative order. You can sort by a secondary key first and then by the primary key, and ties in the primary key stay ordered by the secondary key.
:::

:::quiz
Why is a heap better than sorting for "top 5 of 10 million scores"?

A size-5 heap processes each score in O(log 5), so the whole pass is O(n); sorting everything is O(n log n) and needs to order items you'll never use.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Stable sort | Pengurutan stabil |
| Sort key | Kunci pengurutan |
| Interval | Rentang / selang waktu |
| Sweep line | Garis sapu (memproses peristiwa berurutan) |
| Partition | Partisi — membagi menjadi kelompok |
| Inversion | Inversi — pasangan yang urutannya terbalik |
| Divide and conquer | Bagi dan taklukkan |

## 📚 Keep learning

- [Python docs: Sorting HOW TO (keys, stability)](https://docs.python.org/3/howto/sorting.html)
- [Python docs: heapq](https://docs.python.org/3/library/heapq.html)
- [VisuAlgo — sorting visualizations](https://visualgo.net/en/sorting)

## 📣 Stage 3 done — share it

:::linkedin{type="dsa"}
🧩 DSA Stage 3 done: the patterns behind most coding interview problems.

- Two pointers → pair sums and in-place tricks in O(n)
- Sliding window → longest/shortest contiguous ranges in O(n)
- Prefix sums → any range total in O(1), even with negative numbers
- Binary search → not just arrays: "find the smallest capacity that works"
- Sorting → intervals, sweep lines and top-k with heaps

The one that surprised me: [e.g. "binary search on the answer — I used it to find how many users my API can handle before p95 breaks"].

My approach now: brute force first, spot the pattern, then optimize — out loud.

#Algorithms #CodingInterview #Python #LearningInPublic
:::

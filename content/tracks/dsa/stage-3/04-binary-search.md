---
title: "Binary Search"
summary: Halve the search space every step — exact lookups, first/last positions, rotated arrays, and the powerful "binary search on the answer" technique.
type: lesson
source: original
roles: { be: core, fe: core, fs: core, ai: core, ops: recommended }
durationMinutes: 150
tags: [dsa, binary-search, patterns, monotonic, interviews]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Why halving gives **O(log n)** — 1 billion items in ~30 steps
- A reliable template with a clear **interval invariant** (no more off-by-one panic)
- Lower bound / upper bound (first position `>= x`, first `> x`)
- Searching data that's "almost sorted" (rotated arrays)
- **Binary search on the answer** for optimization problems
- 🧭 How to recognize binary search problems — including ones without an array

## 🧠 The big idea

Guess a number between 1 and 1,000. After each guess you hear "higher" or "lower". Guessing 500 first eliminates **half** of the options no matter the answer; then 250 or 750; and so on. You'll always win within 10 guesses, because 2¹⁰ = 1,024.

Binary search works whenever a question has that **"higher / lower"** structure.

## ❓ Why does this exist?

| n | Linear scan | Binary search |
|---|---|---|
| 1,000 | 1,000 | 10 |
| 1,000,000 | 1,000,000 | 20 |
| 1,000,000,000 | 1,000,000,000 | 30 |

Databases (B-tree indexes), `git bisect`, autocomplete over sorted words, version lookups and capacity planning all rely on it.

## 💥 What happens if we DON'T use it — or get it slightly wrong?

- A linear scan over a sorted list of 10 million records on every request.
- The famous bugs: infinite loops when `low` and `high` stop moving, missing the last element, `mid` overflow in fixed-width integer languages (`(low + high) / 2` in Java — Python ints don't overflow, but the lesson is worth knowing).

## 📖 How it works, step by step

### 1. Exact search (closed interval)

```python
def find_index(nums, target):
    low, high = 0, len(nums) - 1          # search space: [low, high] inclusive
    while low <= high:                     # non-empty
        mid = (low + high) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            low = mid + 1                  # target is right of mid
        else:
            high = mid - 1                 # target is left of mid
    return -1
```

**Invariant**: if the target exists, it's inside `[low, high]`. Every branch keeps that true and shrinks the interval.

### 2. Lower bound: first index with value `>= x` (half-open interval)

```python
def first_at_least(nums, x):
    low, high = 0, len(nums)               # answer is in [low, high] — high = len means "none"
    while low < high:
        mid = (low + high) // 2
        if nums[mid] < x:
            low = mid + 1                  # mid is too small → answer is after it
        else:
            high = mid                     # mid might be the answer → keep it
    return low
```

This template answers a whole family: first `>= x`, insertion position, count of items `< x` (= the index), first `> x` (use `<=`), last `< x` (answer − 1). Python's `bisect_left` / `bisect_right` implement exactly these.

### 3. Think in terms of a predicate

Rewrite any binary search as: *find the first position where `condition(i)` becomes True*, given the sequence looks like:

```text
False False False False True True True
                        ^ answer
```

If you can prove the condition is **monotonic** (once True, stays True), binary search works — even with no array at all.

### 4. Rotated sorted arrays

`[13, 15, 18, 2, 5, 9, 11]`: at any `mid`, **one half is sorted**. If `nums[low] <= nums[mid]`, the left half is sorted: check whether the target lies within `nums[low]..nums[mid]`; if yes, go left, else go right. Otherwise the right half is sorted — mirror the logic.

### 5. Binary search on the answer

*"What's the minimum daily capacity to finish all reviews in D days?"*

- Candidate answers: from `max(sizes)` (must fit the biggest application) to `sum(sizes)` (one day).
- Predicate: `can_finish(capacity)` — a greedy O(n) simulation.
- Monotonic: if capacity c works, c + 1 also works.

```python
low, high = max(sizes), sum(sizes)
while low < high:
    mid = (low + high) // 2
    if can_finish(mid):
        high = mid        # works → maybe smaller works too
    else:
        low = mid + 1     # doesn't work → need more
return low
```

Total: O(n · log(sum)). Same shape: split tasks into k sprints minimizing the largest, minimum speed to arrive on time, smallest threshold that fits a budget, largest integer square root.

:::tip[🧭 How to spot binary search]
- Data is **sorted** (or sorted after a rotation) and you need a position, first/last occurrence, or insertion point.
- The problem asks for the **minimum/maximum value that satisfies a condition**, and a feasibility check `works(x)` is **monotonic**.
- Constraints are huge (values up to 10⁹, n up to 10⁵) and an O(n log n) or O(n log V) solution is expected.
- You catch yourself trying candidate answers one by one: "try 1, try 2, try 3…".
:::

## ⚖️ Trade-offs

| Approach | Time | Needs |
|---|---|---|
| Linear scan | O(n) | nothing |
| Binary search | O(log n) | sorted data / monotonic predicate |
| Hash lookup | O(1) average | exact matches only — no "first ≥ x", no ranges |
| Binary search on answer | O(check × log range) | monotonic feasibility |
| B-tree index (databases) | O(log n) disk-friendly | database maintenance |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ Sorted arrays, ranges, "first/last", optimization with a monotonic check.
- ✅ Debugging: `git bisect` to find which commit introduced a bug.
- 🚫 Unsorted data you'd have to sort for a **single** lookup (O(n log n) > O(n)).
- 🚫 Exact-match lookups repeated many times on changing data → a set/dict.

## 🏆 Best practices

- [ ] Pick **one** template and its invariant (closed `[low, high]` or half-open `[low, high)`) and use it consistently.
- [ ] Write the invariant as a comment; check each branch keeps it and shrinks the interval.
- [ ] Test tiny inputs: empty, one element, two elements, target smaller/larger than all.
- [ ] When the loop uses `low = mid`, compute `mid` rounding **up** (`(low + high + 1) // 2`) to avoid infinite loops.
- [ ] For "search on the answer", state the predicate, prove monotonicity, and choose tight bounds.
- [ ] In production Python, use `bisect` — implement by hand in interviews and to understand it.

## 🏭 How it's used in industry

- Database indexes (B-trees) are multi-way binary searches designed for disks.
- `git bisect` finds a bad commit among thousands in ~12 test runs.
- Load testing: binary search the maximum users before p95 breaks the SLO (lesson 03 of Week 6!).
- Feature rollout and ML: finding thresholds that meet a precision target.

## ⚠️ Common mistakes

- `while low < high` with the closed template (misses the last candidate) or `<=` with the half-open one (index error).
- `high = mid - 1` when `mid` could be the answer.
- Forgetting that rotated-array logic needs **distinct** values (duplicates break the "which half is sorted" test).
- Using binary search on the answer without a monotonic check.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain `git bisect` to a teammate who has never used it: "the bug appeared somewhere in the last 500 commits" — how many test runs does it take and why?

## 📐 Design it

After lesson 03 of Week 6, you want to find the **maximum number of concurrent users** CareerPilot's API supports while keeping p95 latency under 300 ms. Each Locust run takes 5 minutes. Design an automated search: bounds, predicate, how many runs, and what makes the result unreliable.

:::quiz
Show a possible design

- **Predicate**: `ok(users)` = run Locust headless with `users` for 5 minutes (after warm-up), return `p95 <= 300 ms and error_rate < 1%`.
- **Monotonic assumption**: more users never makes latency better → once `ok` is False, it stays False.
- **Bounds**: find an upper bound by doubling: 50 ✅, 100 ✅, 200 ✅, 400 ❌ → search `[200, 400]`.
- **Binary search** to a precision of 10 users: 400−200 = 200 → about log₂(20) ≈ 5 more runs. Total ≈ 4 + 5 = 9 runs ≈ 45 minutes (vs 20+ runs stepping by 10).
- **Reliability**: measurements are noisy — repeat borderline runs, use the same data volume and a fresh environment, warm caches, and report a safety margin (e.g. plan capacity at 70% of the found maximum). Noise can break monotonicity near the boundary, so treat the result as an estimate.
:::

### 📝 Self-review checklist

- [ ] Predicate and monotonicity stated
- [ ] Upper bound found before binary search
- [ ] Number of runs estimated
- [ ] Measurement noise addressed

::ai-review{task="design"}

::part[Practice Problems]{n="3"}

:::problem{id="dsa-s3-binary-search-basics" title="Binary Search Basics" difficulty="easy" path="exercises/dsa/stage-3/13-binary-search-basics"}
Exact search, lower bound, and integer square root by searching the answer — without `bisect` or `math`.
:::

:::problem{id="dsa-s3-search-rotated" title="Search a Rotated Schedule" difficulty="medium" path="exercises/dsa/stage-3/14-search-rotated"}
Find a value in O(log n) when a sorted list was rotated at an unknown point.
:::

:::problem{id="dsa-s3-min-daily-capacity" title="Minimum Daily Review Capacity" difficulty="medium" path="exercises/dsa/stage-3/15-min-daily-capacity"}
Binary search on the answer with a greedy feasibility check.
:::

:::problem{id="dsa-s3-fair-sprint-split" title="Fair Sprint Split" difficulty="hard" path="exercises/dsa/stage-3/16-split-largest-sum"}
Stretch: minimize the heaviest of k consecutive sprints — and explain why "at most k" is enough.
:::

:::hints
- The test counts how many list elements you read: a correct binary search reads about log₂(n) of them.
- `integer_sqrt`: predicate `mid * mid <= n` is True…True False…False; you want the **last** True, so round `mid` up.
- `search_rotated`: compare `nums[low] <= nums[mid]` to find the sorted half first, then check the target's range.
- `min_daily_capacity`: the greedy check starts a new day when adding the next application would exceed the capacity.
:::

## ✅ Quick check

:::quiz
Roughly how many steps does binary search need for 1 million sorted items?

About 20, because 2²⁰ ≈ 1,048,576.
:::

:::quiz
What property must a condition have for "binary search on the answer" to work?

Monotonicity: once the condition becomes true for some value, it stays true for all larger (or all smaller) values.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Binary search | Pencarian biner |
| Search space | Ruang pencarian |
| Lower bound | Batas bawah (posisi pertama ≥ x) |
| Monotonic | Monoton — tidak berbalik arah |
| Predicate | Predikat — kondisi benar/salah |
| Rotated array | Larik yang diputar |

## 📚 Keep learning

- [Python docs: bisect](https://docs.python.org/3/library/bisect.html)
- [Git docs: git bisect](https://git-scm.com/docs/git-bisect)

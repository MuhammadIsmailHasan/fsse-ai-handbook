---
title: "Two Pointers"
summary: Walk a sequence from both ends (or at two speeds) to replace nested loops — palindromes, pair sums on sorted data, merging, three-sum and the rainwater problem.
type: lesson
source: original
roles: { be: core, fe: core, fs: core, ai: core, ops: optional }
durationMinutes: 150
tags: [dsa, two-pointers, patterns, sorting, interviews]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- The three shapes of the two-pointer pattern: **opposite ends**, **same direction (read/write)**, **two sequences**
- Why sorted input unlocks O(n) pair searches
- How to **prove** that moving a pointer never skips the answer
- Handling duplicates without a set
- 🧭 How to recognize a two-pointer problem

## 🧠 The big idea

Two people search a sorted bookshelf for two books whose page counts add up to exactly 1,000. One starts at the thinnest book, the other at the thickest. Too many pages in total? The person at the thick end steps inward. Too few? The person at the thin end steps inward. They never need to try every pair — each step **rules out** a whole group of pairs.

That's the entire pattern: **each pointer move eliminates possibilities**, so n steps replace n² comparisons.

## ❓ Why does this exist?

Brute force over pairs is O(n²): 100,000 items → 5 billion pairs. When the data has **order** (sorted values, or positions from both ends), two pointers exploit it to solve pair/partition problems in O(n) with O(1) extra memory — better than a hash map's O(n) memory.

## 💥 What happens if we DON'T use it?

```python
def pair_with_sum(sorted_prices, budget):
    for i in range(len(sorted_prices)):
        for j in range(i + 1, len(sorted_prices)):   # O(n²)
            if sorted_prices[i] + sorted_prices[j] == budget:
                return i, j
```

It passes the 10-item example and times out on the interviewer's 10⁵-item test. And you've ignored the most important hint in the problem: **sorted**.

## 📖 How it works, step by step

### 1. Shape A — opposite ends

```python
left, right = 0, len(nums) - 1
while left < right:
    total = nums[left] + nums[right]
    if total == target:
        return left, right
    if total < target:
        left += 1          # need bigger: only moving left can increase the sum
    else:
        right -= 1         # need smaller: only moving right can decrease it
```

**Why it's safe** (say this in interviews): if `nums[left] + nums[right] > target`, then `nums[right]` plus **any** remaining left value is also too big (they're all ≥ `nums[left]`). So `right` can't be part of a solution — discard it.

Also works for: palindromes (compare ends, move inward), reversing in place, container-with-most-water.

### 2. Shape B — same direction (read/write or fast/slow)

```python
write = 0
for read in range(len(nums)):
    if keep(nums[read]):
        nums[write] = nums[read]
        write += 1
```

`read` explores, `write` marks where the next kept item goes. Used for removing duplicates from sorted arrays, moving zeros (Stage 2), compacting data in place. Linked-list fast/slow pointers are the same family.

### 3. Shape C — two sequences

```python
i = j = 0
while i < len(a) and j < len(b):
    if a[i] <= b[j]:
        merged.append(a[i]); i += 1
    else:
        merged.append(b[j]); j += 1
merged += a[i:] + b[j:]
```

Merging sorted lists (the heart of merge sort), intersecting sorted lists, comparing versions.

### 4. Sort first, then two pointers

When input isn't sorted, sorting costs O(n log n) — often still far better than O(n²):

**Three-sum**: sort, fix the first number `nums[i]`, then run opposite-end two pointers on the rest for `-nums[i]`. O(n²) instead of O(n³).

Duplicates: skip equal neighbors **after sorting** instead of storing results in a set:

```python
if i > 0 and nums[i] == nums[i - 1]:
    continue
```

### 5. Moving the "limiting" side

In problems like the biggest banner or trapped rainwater, the **shorter** side limits the result. Moving the taller side can only shrink the width without raising the limit, so always move the shorter side. Rainwater extends this: the side with the smaller running maximum already knows its water level.

:::tip[🧭 How to spot two pointers]
- The input is **sorted** (or sorting doesn't break the question) and you need a **pair/triplet** with some sum or difference.
- You compare or swap items from **both ends**: palindromes, reversing, "container" problems.
- You must modify an array **in place** with O(1) extra space: remove, compact, partition.
- You **merge or compare two sorted sequences**.
- A brute force has nested loops over `i < j` and moving one index clearly rules out options.

Not sorted and order matters (you need original indices, sorting is forbidden)? Consider a **hash map** instead.
:::

## ⚖️ Trade-offs

| Approach for "pair with sum" | Time | Extra space | Needs sorted? |
|---|---|---|---|
| Brute force | O(n²) | O(1) | no |
| Hash map (Stage 1) | O(n) | O(n) | no |
| Sort + two pointers | O(n log n) | O(1)–O(n) for sorting | sorts (loses original indices) |
| Already sorted + two pointers | **O(n)** | **O(1)** | yes |

## ✅ When to use it / 🚫 When NOT to use it

- ✅ Sorted data, pair/triplet targets, in-place compaction, symmetric checks, merges.
- 🚫 Unsorted data where you must return **original** indices → hash map.
- 🚫 Contiguous subarray with a condition over a range → usually a **sliding window** (next lesson) or **prefix sums**.

## 🏆 Best practices

- [ ] Start by asking: *is it sorted? may I sort it? do I need original indices?*
- [ ] Name pointers by role: `left/right`, `read/write`, `i/j` only for two sequences.
- [ ] Before coding, state the **invariant** and why each move can't skip a valid answer.
- [ ] Decide the loop condition deliberately: `left < right` (pairs of different items) vs `left <= right`.
- [ ] Handle duplicates by skipping equal neighbors after sorting.
- [ ] Don't modify the caller's list when sorting unless allowed — `sorted(nums)` creates a copy.
- [ ] Test: empty, one element, all equal, no answer, answer at the edges.

## 🏭 How it's used in industry

- **Merge** steps in databases (merge joins) and external sorting of huge files.
- Diff tools and version comparison walk two sequences together.
- Deduplicating sorted logs or event streams in place; compaction in storage engines.

## ⚠️ Common mistakes

- Using two pointers on **unsorted** data for a pair sum.
- Infinite loops: a branch that moves no pointer.
- Returning early in three-sum and missing other triplets, or skipping duplicates at the wrong time.
- Off-by-one: `while left <= right` letting an item pair with itself.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a non-programmer why checking a word is a palindrome by comparing the first and last letters, then moving inward, is faster than generating the reversed word — and why it uses less memory.

## 📐 Design it

CareerPilot has two lists of job ids, each **sorted** and each with up to 5 million ids: jobs a user **saved** and jobs that **closed** today. Design a way to find saved jobs that closed, without loading both lists into a set. State time and memory.

:::quiz
Show a possible design

**Two-pointer intersection** over the two sorted streams:

```text
i, j = 0, 0
while i < len(saved) and j < len(closed):
    if saved[i] == closed[j]: output saved[i]; i += 1; j += 1
    elif saved[i] < closed[j]: i += 1
    else: j += 1
```

- Time **O(n + m)** — each step advances at least one pointer.
- Memory **O(1)** extra — and if the ids come from files or database cursors ordered by id, you never need both lists in memory at all (stream them).
- A set approach is also O(n + m) time but needs memory for 5 million ids (hundreds of MB in Python).
- This is exactly how databases do a **merge join** when both inputs are sorted by the join key.
:::

### 📝 Self-review checklist

- [ ] Uses sortedness to advance the smaller side
- [ ] Every loop iteration moves a pointer
- [ ] Memory advantage over a set is explained

::ai-review{task="design"}

::part[Practice Problems]{n="3"}

:::problem{id="dsa-s3-two-pointer-basics" title="Two Pointer Basics" difficulty="easy" path="exercises/dsa/stage-3/01-two-pointer-basics"}
A palindrome check without copying the text, pair indices in a sorted list, and merging two sorted lists.
:::

:::problem{id="dsa-s3-three-sum" title="Three Budgets That Balance" difficulty="medium" path="exercises/dsa/stage-3/02-three-sum"}
All unique triplets summing to zero: sort, fix one, two pointers for the rest, skip duplicates.
:::

:::problem{id="dsa-s3-biggest-banner" title="Biggest Billboard Frame" difficulty="medium" path="exercises/dsa/stage-3/03-container-most-water"}
Maximize width × shorter height by always moving the limiting side.
:::

:::problem{id="dsa-s3-rainwater" title="Rainwater on a Skyline" difficulty="hard" path="exercises/dsa/stage-3/04-trapping-rain-water"}
Stretch: trapped water in O(n) time and O(1) space with two pointers and running maxima.
:::

:::hints
- `is_clean_palindrome`: skip non-alphanumerics on each side **before** comparing.
- `pair_indices`: when the sum is too big, move `right` — that keeps the smallest valid `left`.
- `three_sum_zero`: after recording a triplet, move both pointers and skip repeated `left` values.
- `max_banner_area`: compute the area first, then move whichever side is shorter.
- `trapped_water`: if `heights[left] <= heights[right]`, the left side's water depends only on `left_max`.
:::

## ✅ Quick check

:::quiz
In the sorted pair-sum loop, why is it safe to decrement `right` when the sum is too large?

Every remaining left value is at least `nums[left]`, so `nums[right]` plus any of them is still too large — `nums[right]` can't be in any valid pair.
:::

:::quiz
Three-sum with sorting and two pointers is O(n²). Where does each factor come from?

An outer loop fixes the first number (n choices), and for each one the two-pointer scan is O(n). Sorting's O(n log n) is smaller.
:::

## 📖 Kamus (glossary)

| Term | Bahasa Indonesia |
|---|---|
| Two pointers | Dua penunjuk |
| Invariant | Invarian — kondisi yang selalu benar selama loop |
| In place | Di tempat (tanpa salinan) |
| Merge | Menggabungkan (dua urutan terurut) |
| Duplicate | Duplikat |

## 📚 Keep learning

- [Python docs: Sorting HOW TO](https://docs.python.org/3/howto/sorting.html)
- [PostgreSQL docs: Merge join and other plan types (EXPLAIN)](https://www.postgresql.org/docs/current/using-explain.html)

---
title: "Sliding Window"
summary: Answer questions about contiguous ranges in O(n) — fixed-size windows, growing and shrinking windows with counts, and why positive numbers matter.
type: lesson
source: original
roles: { be: core, fe: core, fs: core, ai: core, ops: recommended }
durationMinutes: 150
tags: [dsa, sliding-window, patterns, hash-map, interviews]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- **Fixed-size** windows: update in O(1) instead of recomputing
- **Variable-size** windows: expand right, shrink left, with a validity condition
- Tracking window contents with counters and a "missing" count
- When sliding window **fails** (negative numbers) and what to use instead
- 🧭 How to recognize a sliding window problem

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Window** | A stretch of items next to each other that you're looking at | Rentang data berdampingan |
| **Contiguous** | Items right next to each other, no gaps | Berurutan tanpa celah |
| **Fixed-size window** | The window is always k items wide | Jendela ukuran tetap |
| **Variable-size window** | It grows and shrinks to stay valid | Jendela yang berubah ukuran |
| **Expand / shrink** | Add an item on the right / remove one on the left | Tambah kanan / buang kiri |
| **Validity condition** | The rule the window must satisfy (no repeats, sum ≤ k) | Syarat jendela sah |
| **Amortised O(n)** | Each item enters and leaves at most once | Tiap data masuk-keluar sekali |

## 🧠 The big idea

You're on a train looking at the view through a window that shows exactly 3 houses. When the train moves one house forward, you don't re-count all 3 houses — **one house enters on the right, one leaves on the left**.

A sliding window keeps a summary (sum, counts, set) of a contiguous range and **updates** it as the range moves, so each element is added once and removed once: O(n).

## ❓ Why it matters

Many real questions are about **stretches that are next to each other**:

- the highest revenue in any 7-day period,
- the longest session without a repeated page,
- requests in the last 60 seconds (rate limiting — Stage 2),
- the smallest snippet of text containing all the search terms.

Recomputing the whole stretch at every position is O(n·k). Sliding the window instead updates a running summary in O(1) per step, which turns the whole scan into O(n) — like the train passenger counting one house in and one house out instead of recounting the view.

## 📖 Step by step

### 1. Fixed-size window

```python
window = sum(nums[:k])
best = window
for right in range(k, len(nums)):
    window += nums[right] - nums[right - k]    # enters, leaves
    best = max(best, window)
```

```text
[2 1 5] 1 3 2   sum 8
2 [1 5 1] 3 2   8 + 1 - 2 = 7
2 1 [5 1 3] 2   7 + 3 - 1 = 9 ✅
2 1 5 [1 3 2]   9 + 2 - 5 = 6
```

Works for sums, counts of vowels, "any duplicate within k positions" (a set of the last k items).

### 2. Variable-size window: the template

The shape is always the same: expand to the right until the window breaks the rule, then shrink from the left until it's valid again, recording the best answer as you go.

```python
left = 0
for right, item in enumerate(items):
    add(item)                          # 1. expand
    while not valid():                 # 2. shrink until valid again
        remove(items[left])
        left += 1
    best = max(best, right - left + 1) # 3. record (for "longest" problems)
```

For **"shortest"** problems, flip it: record inside the shrinking loop **while the window is valid**.

### 3. Longest with a condition

*Longest run of days within budget* (all costs positive):

- expand: `total += cost`
- invalid when `total > budget` → shrink from the left
- record the length after shrinking

*Longest substring without repeats*: keep `last_seen[char]`; if the char was seen **inside** the window, jump `left` to `last_seen[char] + 1`.

### 4. Shortest window containing everything

Track **what's missing**, so validity is O(1):

```python
need = Counter(required)
missing = len(required)
for right, char in enumerate(text):
    if need[char] > 0:
        missing -= 1
    need[char] -= 1                     # negative = extra copies in window
    while missing == 0:                 # valid → try to shrink
        record(left, right)
        need[text[left]] += 1
        if need[text[left]] > 0:
            missing += 1
        left += 1
```

### 5. Why positive numbers matter

With negative numbers, shrinking the window can *increase* the sum, so "too big → shrink" stops being true. That's where prefix sums (next lesson) take over.

Shrinking works because removing an element **always decreases** the sum, and adding always increases it. With negative numbers, a window over budget might become valid by **adding** more items, so "shrink when invalid" can skip the answer.

- Subarray sum problems **with negatives** → **prefix sums + hash map** (next lesson).
- Maximum subarray sum (any length) → **Kadane's algorithm** (a special case of dynamic programming).

### 6. Amortized O(n)

The inner `while` looks like nesting, but `left` only moves forward and never passes `right`. Across the whole run, `left` moves at most n times → total O(n).

:::tip[🧭 How to spot a sliding window]
- The question is about a **contiguous** subarray or substring (not a subsequence, not any subset).
- Words like **longest / shortest / maximum / minimum / at most / exactly k** over a range.
- A **fixed size** k window, or a condition that becomes true/false **monotonically** as the window grows (sum of positives, distinct count, counts of required items).
- A brute force recomputes something for every range that overlaps heavily with the previous range.

Negative numbers and an exact sum? → prefix sums. Non-contiguous choices? → not a window (think DP or greedy).
:::

### Choosing your setup

Every option here is a trade-off:

| Approach | Time | Space | Works with negatives? |
|---|---|---|---|
| Brute force over all ranges | O(n²)–O(n³) | O(1) | yes |
| Fixed window | O(n) | O(1) | yes |
| Variable window (shrink when invalid) | O(n) | O(1)–O(alphabet) | only when the condition is monotonic |
| Prefix sum + hash map | O(n) | O(n) | yes (exact sums) |
| Deque for window max/min | O(n) | O(k) | yes |

- ✅ Rolling metrics, moving averages, rate limits, contiguous string/array constraints.
- 🚫 Subsequences or arbitrary subsets.
- 🚫 Conditions that aren't monotonic with window size (sum with negatives).

## ⚠️ Common mistakes

- Using a window on data with negative numbers for an "at most sum" condition.
- Moving `left` backwards in the "longest without repeats" problem (use `max` or check `last_seen >= left`).
- Recomputing the window's sum or counts inside the loop.
- Recording the answer in the wrong place (before shrinking for "longest").

## 🏆 Best practices

- [ ] Ask: *contiguous? fixed size or variable? are values non-negative?*
- [ ] Write the **window state** first (sum, counter, set, missing count) and the **valid()** condition in words.
- [ ] For "longest", record after shrinking; for "shortest", record while valid before shrinking.
- [ ] Use `right - left + 1` for length and double-check off-by-one with a 1-element example.
- [ ] Keep updates O(1): a counter or running sum, never `sum(window)` in the loop.
- [ ] Explain the amortized O(n) argument — interviewers expect it.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a product manager how a dashboard can show "the best 7-day sales period this year" instantly, without adding up every possible 7-day period — use the train window analogy.

## 📐 Design it

CareerPilot wants a fraud rule: **flag a user who submits more than 20 applications within any 10-minute period**. Applications arrive as a stream of `(user_id, timestamp)` in time order. Design the data structures and the per-event algorithm, its complexity, and memory growth for 100,000 active users.

:::quiz
Show a possible design

Per user, a **deque of timestamps** in the last 10 minutes (a time-based sliding window):

```text
on event (user, t):
    window = windows[user]           # deque
    window.append(t)
    while window[0] <= t - 600:       # evict events older than 10 min
        window.popleft()
    if len(window) > 20: flag(user)
```

- **Time**: amortized O(1) per event (each timestamp is appended and evicted once).
- **Memory**: at most 21 timestamps per user are ever needed → cap the deque (`maxlen=21` still works for counting > 20) → ~100,000 × 21 timestamps, a few tens of MB; also delete deques for users idle > 10 minutes.
- **Alternative**: if exactness isn't needed, keep a counter per 1-minute bucket (10 buckets per user) — less memory, slight inaccuracy at bucket edges.
- **Production**: several API servers → keep windows in Redis (sorted sets with `ZREMRANGEBYSCORE` + `ZCARD`) or in the stream processor.
:::

### 📝 Self-review checklist

- [ ] Window is defined by time, not by count
- [ ] Eviction happens before the check
- [ ] Memory bounded per user and idle users cleaned up
- [ ] Multi-server reality considered

::ai-review{task="design"}

::part[Practice Problems]{n="3"}

:::problem{id="dsa-s3-sliding-window-basics" title="Sliding Window Basics" difficulty="easy" path="exercises/dsa/stage-3/05-sliding-window-basics"}
Max sum of k consecutive items, repeats within k positions, and most vowels in a window — all O(n) regardless of k.
:::

:::problem{id="dsa-s3-longest-unique-run" title="Longest Run Without Repeats" difficulty="medium" path="exercises/dsa/stage-3/06-longest-unique-substring"}
Variable window with a last-seen dictionary to jump the left edge.
:::

:::problem{id="dsa-s3-longest-affordable" title="Longest Streak Under Budget" difficulty="medium" path="exercises/dsa/stage-3/07-longest-under-budget"}
Expand and shrink a window of positive costs to find the longest affordable run.
:::

:::problem{id="dsa-s3-shortest-covering" title="Shortest Snippet With All Keywords" difficulty="hard" path="exercises/dsa/stage-3/08-minimum-window"}
Stretch: the minimum window containing all required characters, with a "missing" counter for O(1) validity checks.
:::

:::hints
- `has_nearby_repeat`: keep a set of at most the last `k` items; remove `items[i - k]` once the set is too big.
- `longest_unique_run`: `if last_seen.get(char, -1) >= left: left = last_seen[char] + 1`.
- `longest_affordable`: shrink with `while total > budget`.
- `shortest_covering`: store the best `(start, length)`, not the substring, to avoid copying inside the loop; use `<` (not `<=`) to keep the leftmost.
:::

## ✅ Quick check

:::quiz
Why does the "shrink when over budget" window break if costs can be negative?

With negatives, adding more items can reduce the total, so a window that's currently over budget might become valid by expanding — shrinking can discard the optimal range. Use prefix sums instead.
:::

:::quiz
The variable window has a `while` inside a `for`. Why is it O(n)?

`left` only moves forward and at most n times in total across the entire loop, so all shrink steps together cost O(n).
:::


## 📚 Keep learning

- [Python docs: collections.Counter](https://docs.python.org/3/library/collections.html#collections.Counter)
- [Redis docs: Sorted sets (used for sliding-window counters)](https://redis.io/docs/latest/develop/data-types/sorted-sets/)

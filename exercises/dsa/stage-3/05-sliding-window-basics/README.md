# DSA · Stage 3 · Sliding Window Basics

> 🟢 Easy set · 🚫🤖 No-AI · Target: O(n) each (independent of `k`)

| Function | Example | Result |
|---|---|---|
| `max_window_sum(nums, k)` | `[2, 1, 5, 1, 3, 2], 3` | `9` — the largest sum of `k` **consecutive** items; `None` if `k > len(nums)` or `k <= 0` |
| `has_nearby_repeat(items, k)` | `["a", "b", "c", "a"], 3` | `True` — two equal items whose indices differ by **at most** `k` |
| `max_vowels(text, k)` | `"abciiidef", 3` | `3` — most vowels (`aeiou`, lowercase input) in any window of length `k` (`k <= len(text)`) |

Don't recompute each window from scratch — add what enters, subtract what leaves.

```bash
cd exercises
uv run pytest dsa/stage-3/05-sliding-window-basics
```

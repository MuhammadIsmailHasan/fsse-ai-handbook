# DSA · Stage 2 · Array & String Basics

> 🟢 Easy set · 🚫🤖 No-AI

| Function | Example | Result | Target |
|---|---|---|---|
| `rotate_right(nums, k)` | `[1, 2, 3, 4, 5], 2` | `[4, 5, 1, 2, 3]` | O(n) time; return a **new** list; `k` may be larger than `len(nums)` or 0 |
| `move_zeros(nums)` | `[0, 3, 0, 1, 2]` | list becomes `[3, 1, 2, 0, 0]`, returns `None` | **in place**, O(n) time, O(1) extra space, keep the order of non-zeros |
| `compress(text)` | `"aaabccdddd"` | `"a3bc2d4"` | O(n) — a run of length 1 has no number; build with a list + `"".join` |

```bash
cd exercises
uv run pytest dsa/stage-2/01-array-string-basics
```

Write the time and space complexity as a comment above each function.

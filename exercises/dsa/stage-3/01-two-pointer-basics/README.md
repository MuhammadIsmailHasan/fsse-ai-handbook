# DSA · Stage 3 · Two Pointer Basics

> 🟢 Easy set · 🚫🤖 No-AI · Target: O(n) time, O(1) extra space (except the merged output)

| Function | Example | Result |
|---|---|---|
| `is_clean_palindrome(text)` | `"Kasur ini rusak!"` | `True` — ignore case and anything that isn't a letter or digit (`str.isalnum`) |
| `pair_indices(sorted_nums, target)` | `[1, 3, 4, 6, 9], 10` | `(0, 4)` — indices `i < j` of a pair adding up to `target` in a **sorted** list; the pair with the **smallest `i`**; `None` if none |
| `merge_sorted_lists(a, b)` | `[1, 4, 9], [2, 4, 5]` | `[1, 2, 4, 4, 5, 9]` — a new list; don't call `sorted`/`sort` |

`is_clean_palindrome` must not build a cleaned copy of the string (a test checks memory use) — move two indices inward and skip non-alphanumerics.

```bash
cd exercises
uv run pytest dsa/stage-3/01-two-pointer-basics
```

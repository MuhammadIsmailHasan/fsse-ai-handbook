# M1 · W1 · 02 — Linear, Binary and Indexed Search

> 🚫🤖 **No-AI** · ⏱️ ~50 min · Lesson: *Searching Algorithms*

Implement the functions in `searching.py`.

| Function | Example | Result |
|---|---|---|
| `linear_search(items, target)` | `[5, 3, 9], 9` | `2` |
| `binary_search(sorted_items, target)` | `[3, 8, 15, 23, 42, 57, 91], 57` | `(5, 2)` — index, steps |
| `first_job_over(jobs, minimum_salary)` | | first matching job or `None` |
| `build_index(jobs)` | | `{id: job}` |
| `jobs_in_salary_range(jobs_sorted, low, high)` | | jobs with `low <= salary <= high` |

`linear_search` may not use `in` or `.index()` — write the loop.

```bash
cd exercises
uv run pytest m1/w1/02-searching
```

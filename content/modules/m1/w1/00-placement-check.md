---
title: "Week 1 Placement Check"
summary: Can you already count, search, sort and combine data in Python? Find out in 20 minutes.
type: placement-check
source: original
roles: { be: core, fe: core, fs: core, ai: core, ops: core }
durationMinutes: 20
tags: [placement]
---

::::placement{id="modules/m1/w1"}
Answer on paper first. Code answers don't need to be perfect Python — clear logic is what counts.

:::quiz
1 · Given `words = ["python", "react", "python", "sql", "python", "react"]`, write code that finds the most common word and how often it appears.

```python
counts = {}
for word in words:
    counts[word] = counts.get(word, 0) + 1
top = max(counts, key=counts.get)
print(top, counts[top])   # python 3
```

(`collections.Counter(words).most_common(1)` also works — but can you do it without it?)
:::

:::quiz
2 · Why can binary search find an item in 1,000,000 sorted numbers in about 20 steps, and what's its one requirement?

Each step halves the remaining range: 1,000,000 → 500,000 → … → 1 takes about log₂(1,000,000) ≈ 20 steps. The data **must be sorted**.
:::

:::quiz
3 · Sort this list of jobs by salary, highest first, and for equal salaries by title A→Z: `jobs = [("Dev", 10), ("Analyst", 12), ("Admin", 10)]`

```python
sorted(jobs, key=lambda job: (-job[1], job[0]))
# [("Analyst", 12), ("Admin", 10), ("Dev", 10)]
```
:::

:::quiz
4 · Using a list comprehension, keep only remote jobs from `jobs = [{"title": "Dev", "remote": True}, {"title": "QA", "remote": False}]` and return their titles.

`[job["title"] for job in jobs if job["remote"]]` → `["Dev"]`
:::

:::quiz
5 · Group these sales by city and total them: `[("Jakarta", 100), ("Bandung", 50), ("Jakarta", 30)]`

```python
totals = {}
for city, amount in sales:
    totals[city] = totals.get(city, 0) + amount
# {"Jakarta": 130, "Bandung": 50}
```
:::

:::quiz
6 · Before coding a new problem, what steps do you take?

Understand the problem (restate it, clarify inputs/outputs) → write examples including edge cases → plan in pseudocode → code → test with the examples → review/refactor.
:::
::::

:::tip[Scoring yourself]
Pass with **5 of 6** correct *and* explained. Question 6 counts only if you actually follow those steps — be honest!
:::

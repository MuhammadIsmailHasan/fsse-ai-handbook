# DSA · Stage 3 · Sort Tasks by Priority in One Pass

> 🟡 Medium · 🚫🤖 No-AI · Target: one pass, O(1) extra space

`sort_priorities(tasks)` sorts a list of `"high"`, `"medium"` and `"low"` **in place** into the order high → medium → low, and returns `None`.

```python
tasks = ["low", "high", "medium", "high", "low"]
sort_priorities(tasks)
tasks   # ["high", "high", "medium", "low", "low"]
```

No `sort`, `sorted`, `Counter`, `count` or building a new list (a test checks) — use the **Dutch national flag** algorithm: three regions tracked by `low`, `mid`, `high` pointers.

```bash
cd exercises
uv run pytest dsa/stage-3/19-three-way-partition
```

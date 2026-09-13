# DSA · Stage 2 · Top K Searched Skills

> 🔴 Stretch · 🚫🤖 No-AI · Target: O(n log k)

`top_k_skills(searches, k)` → the `k` most frequent search terms as `[(term, count)]`:
- higher count first; ties broken **alphabetically**
- if there are fewer than `k` distinct terms, return all of them
- `k >= 0`

```python
top_k_skills(["python", "sql", "python", "react", "sql", "python", "go"], 2)
# [("python", 3), ("sql", 2)]
```

Do it **without sorting all distinct terms** — keep a heap of size k (`heapq`). A test with many distinct terms and small k checks the complexity. Think carefully about how to order ties inside a min-heap.

```bash
cd exercises
uv run pytest dsa/stage-2/08-top-k-frequent
```

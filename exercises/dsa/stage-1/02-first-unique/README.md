# DSA · Stage 1 · First Unique Character

> 🟢 Easy · Target: O(n) time

`first_unique_index(text)` → index of the first character that appears exactly once, or `-1`. Case-sensitive.

```python
first_unique_index("pipeline")  # 4  ("l" — p, i and e all repeat)
first_unique_index("aabb")         # -1
```

```bash
cd exercises
uv run pytest dsa/stage-1/02-first-unique
```

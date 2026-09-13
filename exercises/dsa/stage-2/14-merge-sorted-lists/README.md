# DSA · Stage 2 · Merge Two Sorted Lists

> 🟡 Medium · 🚫🤖 No-AI · Target: O(n + m) time, O(1) extra space

Two sorted linked lists of job ids arrive from two job boards. Merge them into **one sorted list** by relinking the existing nodes (don't create new value nodes; a dummy head node is fine). Stable: when values are equal, nodes from `a` come first.

```python
merge_sorted(1 → 3 → 5, 2 → 3 → 6)   # 1 → 2 → 3 → 3 → 5 → 6
merge_sorted(None, 4 → 7)            # 4 → 7
```

`ListNode`, `from_list`, `to_list` are provided.

```bash
cd exercises
uv run pytest dsa/stage-2/14-merge-sorted-lists
```

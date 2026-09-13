# DSA · Stage 2 · Linked List Basics

> 🟢 Easy set · 🚫🤖 No-AI · Target: O(n) time, **O(1) extra space** for all three

`ListNode`, `from_list` and `to_list` are provided in `linked_basics.py`.

| Function | Example | Result |
|---|---|---|
| `reverse_list(head)` | `1 → 2 → 3` | `3 → 2 → 1` (relink the **same** nodes, return the new head) |
| `middle_node(head)` | `1 → 2 → 3 → 4` | node `3` — for even lengths return the **second** middle; `None` for an empty list |
| `has_cycle(head)` | a list whose last node points back to node 2 | `True` |

`has_cycle` must use O(1) extra memory: no sets or dicts (a test checks) — use a slow and a fast pointer.

```bash
cd exercises
uv run pytest dsa/stage-2/13-linked-list-basics
```

# DSA · Stage 4 · Build a Min-Heap

> 🟢 Easy · 🚫🤖 No-AI · Target: O(log n) per `push` / `pop`

A **heap** keeps the smallest item always at the front, and it is cheap to add and remove. It is a binary tree stored in a **plain list**, so it needs no node objects:

```text
index:   0  1  2  3  4  5
items: [ 1, 3, 2, 7, 4, 5 ]          1
                                    / \
parent of i = (i - 1) // 2         3   2
children    = 2i + 1, 2i + 2      / \  /
                                 7  4 5
```

The only rule: every parent is **≤ both children**. (Not sorted! Just "the parent wins".)

| Method | Does |
|---|---|
| `push(value)` | add at the end, **sift up** while smaller than the parent |
| `pop()` | take `items[0]`, move the last item to the front, **sift down** (swap with the **smaller** child) |
| `peek()` | `items[0]` |
| `heap_sort(values)` | push everything, pop everything |

Write it yourself — the `heapq` module is not allowed here (you will use it in the next exercises).

```bash
cd exercises
uv run pytest dsa/stage-4/09-heap-basics
```

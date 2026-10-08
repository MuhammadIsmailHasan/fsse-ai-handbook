# DSA · Stage 4 · BST Basics

> 🟢 Easy · 🚫🤖 No-AI · Target: O(h) per operation (h = height)

A **binary search tree** keeps one rule at every node: everything in the **left** subtree is **smaller**, everything in the **right** subtree is **larger**. That rule lets you throw away half of the tree at each step, like looking up a word in a dictionary.

| Function | Does |
|---|---|
| `search(root, val)` | go left or right until you find it or run out of tree |
| `insert(root, val)` | walk down the same way, attach a new leaf; return the root; ignore duplicates |
| `min_value(root)` | keep going left |
| `max_value(root)` | keep going right |

```text
        8
       / \
      3   10         search 6 : 8 → left → 3 → right → 6   (3 steps, not 9)
     / \    \
    1   6    14
       / \   /
      4   7 13
```

```bash
cd exercises
uv run pytest dsa/stage-4/05-bst-basics
```

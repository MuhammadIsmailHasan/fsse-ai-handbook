# DSA · Stage 4 · Sorted Array to Balanced BST

> 🟡 Medium · 🚫🤖 No-AI · Target: O(n)

Insert 1, 2, 3, 4, 5 into a BST in order and you get a **chain**, and `search` becomes O(n) again. A **balanced** tree keeps the height near log n, so every operation stays fast.

| Function | Does |
|---|---|
| `sorted_array_to_bst(nums)` | build a balanced BST from a sorted list: make the **middle** value the root, then do the same for the left half and the right half |
| `is_balanced(root)` | at **every** node the two subtrees differ in height by at most 1 |

```text
nums = [1, 2, 3, 4, 5, 6, 7]          middle = 4

            4
          /   \
         2     6          height 3 = ceil(log2(7 + 1))
        / \   / \
       1   3 5   7
```

For `is_balanced`, a tree can look fine at the root and be unbalanced deeper. Do not call a separate `height()` at every node (that is O(n²)): let one helper return the height, or a flag like `-1` for "already unbalanced".

```bash
cd exercises
uv run pytest dsa/stage-4/07-sorted-to-balanced
```

# DSA · Stage 4 · Tree Basics

> 🟢 Easy · 🚫🤖 No-AI · Target: O(n)

A file explorer shows folders inside folders. Folders are nodes; each one has at most two children, `left` and `right`.

Implement four functions on `TreeNode`:

| Function | Returns |
|---|---|
| `size(root)` | how many nodes |
| `height(root)` | nodes on the longest root-to-leaf path (empty = 0, one node = 1) |
| `count_leaves(root)` | nodes with no children |
| `sum_values(root)` | the sum of all values |

```python
tree = TreeNode(1, TreeNode(2), TreeNode(3))
size(tree), height(tree), count_leaves(tree), sum_values(tree)   # (3, 2, 2, 6)
```

All four have the same shape: handle the **empty tree**, then combine the answers of the two subtrees.

```bash
cd exercises
uv run pytest dsa/stage-4/01-tree-basics
```

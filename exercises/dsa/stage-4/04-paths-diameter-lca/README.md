# DSA · Stage 4 · Paths, Diameter and Lowest Common Ancestor

> 🔴 Hard · 🚫🤖 No-AI · Target: O(n)

Four classic interview questions on one tree. The pattern: each call **returns something to its parent** (a height, a flag, a found node) and may **also record an answer on the side**.

| Function | Does |
|---|---|
| `has_path_sum(root, target)` | is there a **root-to-leaf** path adding up to `target`? |
| `root_to_leaf_paths(root)` | every root-to-leaf path, left to right |
| `diameter(root)` | longest path between any two nodes, in **edges**; one pass |
| `lowest_common_ancestor(root, p, q)` | the lowest node with both `p` and `q` below it |

```text
        3                lowest_common_ancestor(root, 5, 1) → 3
      /   \              lowest_common_ancestor(root, 5, 4) → 5   (a node is below itself)
     5     1             lowest_common_ancestor(root, 7, 4) → 2
    / \   / \
   6   2 0   8
      / \
     7   4
```

Careful: a path sum must end on a **leaf** (a node with no children), not on any node. For `diameter`, the longest path may bend inside a subtree — at each node it is `left height + right height`. Do not call a separate `height()` at every node (that is O(n²)).

```bash
cd exercises
uv run pytest dsa/stage-4/04-paths-diameter-lca
```

# DSA · Stage 4 · BST: Delete, Floor/Ceiling and LCA

> 🔴 Hard · 🚫🤖 No-AI · Target: O(h) per operation

Three operations that every interviewer likes, all based on the BST rule.

| Function | Does |
|---|---|
| `delete(root, val)` | remove a value and keep the tree a valid BST |
| `floor_ceiling(root, x)` | the largest value ≤ x and the smallest value ≥ x |
| `lca_in_bst(root, p, q)` | lowest common ancestor, using the BST rule (no full search) |

**Delete** has three cases:

```text
leaf          → just remove it
one child     → the child takes its place
two children  → copy the INORDER SUCCESSOR (the smallest value on the right) into this node,
                then delete that successor from the right subtree

delete 5 :      5                 7
               / \               / \
              3   8     →       3   8
                 / \               \
                7   9               9
```

**Floor/ceiling:** walk down one path; each time you go right, the current value is a floor candidate; each time you go left, it is a ceiling candidate. **LCA:** if `p` and `q` are both smaller go left, both larger go right, otherwise the current node is the answer.

```bash
cd exercises
uv run pytest dsa/stage-4/08-bst-delete-floor-lca
```

# DSA · Stage 4 · Validate a BST & the k-th Smallest

> 🟡 Medium · 🚫🤖 No-AI · Target: O(n) and O(h + k)

Two questions that test whether you really understand the BST rule.

| Function | Does |
|---|---|
| `is_valid_bst(root)` | is every node larger than **everything** on its left and smaller than **everything** on its right? Equal values are invalid |
| `kth_smallest(root, k)` | the k-th smallest value (k starts at 1); `ValueError` if k is out of range |

The trap in `is_valid_bst`: comparing a node only with its **direct** children passes this broken tree.

```text
      5
     / \
    1   4          4 > 1? fine.  3 < 4? fine.  But 3 sits in the RIGHT side of 5, so it must be > 5.
       / \
      3   6
```

Pass **bounds** down: each call gets a `low` and a `high` that the node must stay between. For `kth_smallest`, inorder gives sorted order, so stop at the k-th node you pop. The test tree is a chain of 30,000 nodes, so use your own stack instead of recursion.

```bash
cd exercises
uv run pytest dsa/stage-4/06-validate-kth
```

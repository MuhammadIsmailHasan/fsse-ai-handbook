# DSA · Stage 4 · Mirror & Compare

> 🟡 Medium · 🚫🤖 No-AI · Target: O(n)

Two tree questions that look different but use the same idea: **walk two nodes at once**.

| Function | Does |
|---|---|
| `is_same_tree(a, b)` | same shape **and** same values |
| `invert(root)` | swap `left` and `right` at every node; return the new root |
| `is_symmetric(root)` | the tree is a mirror image of itself |

```text
    4              4
   / \            / \
  2   7   --->   7   2        invert
 / \ / \        / \ / \
1  3 6  9      9  6 3  1
```

For `is_same_tree` compare `a.left` with `b.left`. For `is_symmetric` compare `a.left` with `b.right` — the **outer** pair and the **inner** pair. Watch the base cases: both `None` is fine, only one `None` is not.

```bash
cd exercises
uv run pytest dsa/stage-4/03-mirror-compare
```

# DSA · Stage 4 · Tree Traversals

> 🟡 Medium · 🚫🤖 No-AI · Target: O(n)

Visiting every node of a tree can be done in four useful orders:

| Function | Order | Typical use |
|---|---|---|
| `preorder` | node → left → right | copy a tree, print a folder outline |
| `inorder` | left → node → right | read a search tree **in sorted order** |
| `postorder` | left → right → node | delete a tree, add up folder sizes |
| `level_order` | row by row, left to right | "what is on each level?" |

```text
      1
     / \
    2   3          preorder   [1, 2, 4, 5, 3, 6]
   / \   \         inorder    [4, 2, 5, 1, 3, 6]
  4   5   6        postorder  [4, 5, 2, 6, 3, 1]
                   level      [[1], [2, 3], [4, 5, 6]]
```

`preorder` and `postorder` are easy with recursion. The catch: `inorder` and `level_order` get a chain of **50,000 nodes**, which crashes a recursive Python function. Write `inorder` with your **own stack** and `level_order` with a **queue** (`collections.deque`).

```bash
cd exercises
uv run pytest dsa/stage-4/02-tree-traversals
```

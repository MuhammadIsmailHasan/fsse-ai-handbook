---
title: "Binary Trees"
summary: Understand trees as nodes with children, solve tree questions by trusting recursion (base case plus combine), visit nodes in four orders, and avoid crashes on very deep trees with your own stack or queue.
type: lesson
source: original
roles: { be: core, fe: core, fs: core, ai: core, ops: recommended }
durationMinutes: 180
tags: [dsa, trees, binary-tree, recursion, traversal, interviews]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What a **tree** and a **binary tree** are, and the words around them
- The tree recipe: **base case + combine the answers of the children**
- Four ways to visit every node: **preorder, inorder, postorder, level order**
- Returning a value to the parent **and** recording an answer on the side (diameter, LCA)
- Why very deep trees break recursion, and what to use instead
- 🧭 How to recognize a tree problem

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Tree** | Data shaped like a family tree: one top, branches going down | Pohon |
| **Node** | One item in the tree | Simpul |
| **Root** | The top node. It has no parent | Akar |
| **Leaf** | A node with no children | Daun |
| **Binary tree** | Every node has at most two children: left and right | Pohon biner |
| **Height** | How many nodes are on the longest path from the root down | Tinggi |
| **Subtree** | A node together with everything below it | Sub-pohon |
| **Traversal** | Visiting every node once, in some order | Penelusuran |

## 🧠 The big idea

A tree is a **company org chart**. The CEO (root) has managers under them, and each manager has their own team. To count everybody in the company, the CEO does not walk to every desk. The CEO asks each manager, "How many people are in your team?", adds the answers, and adds 1 for themselves. Each manager does the same with their own team. A person with no team says "1".

This is the whole trick of trees: **solve the problem for one node by asking its children the same question**, then combine. You do not need to imagine the whole tree. You only trust that the children will answer correctly.

## ❓ Why it matters

Trees are everywhere in software:

- the **file system** (folders inside folders) and the **HTML DOM** in your browser,
- **comments with replies**, menus with submenus, org charts,
- the **JSON** you send to an API (objects inside objects),
- **database indexes** and **search trees** (next lessons),
- **decision trees** and the way compilers read your code.

And trees are a favourite interview topic, because one small idea (recursion with a base case) solves a lot of questions. If you learn the recipe here, BST, heaps and graphs will feel familiar.

## 📖 Step by step

### 1. The node

A binary tree node holds a value and up to two children.

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left      # another TreeNode, or None
        self.right = right
```

```text
      1            root = 1
     / \           leaves = 4, 5, 3
    2   3          height = 3 (nodes on the longest path: 1 → 2 → 4)
   / \
  4   5
```

An **empty tree** is just `None`. Treating `None` as a valid (empty) tree is what makes the code short.

### 2. The recipe: base case + combine

Every tree function looks the same:

```python
def size(root):
    if root is None:                      # 1. base case: the empty tree
        return 0
    return 1 + size(root.left) + size(root.right)   # 2. combine the children's answers
```

```python
def height(root):
    if root is None:
        return 0
    return 1 + max(height(root.left), height(root.right))
```

To write one, ask two questions:

1. What is the answer for an **empty tree**?
2. If my two children already gave me their answers, how do I get **mine**?

Do not trace the recursion all the way down in your head. Check the base case, check the combine step, and trust the rest. This is called the *leap of faith*.

### 3. Four ways to visit every node

The only difference is **when** you handle the current node.

```python
def preorder(node):                 # node, left, right
    if node is None:
        return []
    return [node.val] + preorder(node.left) + preorder(node.right)

def inorder(node):                  # left, node, right
    if node is None:
        return []
    return inorder(node.left) + [node.val] + inorder(node.right)

def postorder(node):                # left, right, node
    if node is None:
        return []
    return postorder(node.left) + postorder(node.right) + [node.val]
```

```text
      1
     / \
    2   3          preorder   [1, 2, 4, 5, 3, 6]   "me first"
   / \   \         inorder    [4, 2, 5, 1, 3, 6]   "left, me, right"
  4   5   6        postorder  [4, 5, 2, 6, 3, 1]   "children first, me last"
```

| Order | Use it when |
|---|---|
| **Preorder** | you must handle a parent **before** its children (copy a tree, print a folder outline) |
| **Inorder** | you want a search tree's values **sorted** (next lesson) |
| **Postorder** | you need the children's results **before** the parent (folder sizes, deleting a tree) |
| **Level order** | you care about **rows**: the closest nodes first, "what is on each level?" |

### 4. Level order uses a queue

Level order is not recursion. It goes row by row, so it uses a **queue** (first in, first out).

```python
from collections import deque

def level_order(root):
    if root is None:
        return []
    levels, queue = [], deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):          # exactly the nodes on this row
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        levels.append(level)
    return levels
```

Counting `len(queue)` at the start of each round is the trick to know where a row ends. You will use the same idea for graphs in the BFS lesson.

### 5. Very deep trees: use your own stack

Python allows about 1,000 nested calls. A tree that is really a long chain (50,000 nodes) crashes a recursive function with `RecursionError`. The fix is to do the work of the call stack yourself, with a list.

```python
def inorder_iterative(root):
    out, stack, node = [], [], root
    while node or stack:
        while node:                 # go as far left as possible
            stack.append(node)
            node = node.left
        node = stack.pop()          # nothing more on the left: visit
        out.append(node.val)
        node = node.right           # then move to the right subtree
    return out
```

Recursion is clearer, so use it when the tree is balanced (height about log n). Switch to a stack or queue when the tree can be deep, or when the interviewer asks for it.

### 6. Compare two nodes at once

Some questions walk **two** trees (or two sides of one tree) at the same time.

```python
def is_same_tree(a, b):
    if a is None or b is None:
        return a is b                      # both empty → same; only one empty → different
    return a.val == b.val and is_same_tree(a.left, b.left) and is_same_tree(a.right, b.right)

def is_symmetric(root):
    def mirror(a, b):
        if a is None or b is None:
            return a is b
        return a.val == b.val and mirror(a.left, b.right) and mirror(a.right, b.left)
    return root is None or mirror(root.left, root.right)
```

For symmetry, the **outer** pair (`a.left` with `b.right`) and the **inner** pair (`a.right` with `b.left`) must match.

### 7. Return one thing, record another

Some answers are not "the value at the root". The longest path (the **diameter**) may sit deep inside one subtree. The trick: each call **returns its height to the parent**, and **updates a best answer on the side**.

```python
def diameter(root):
    best = 0

    def height(node):
        nonlocal best
        if node is None:
            return 0
        left, right = height(node.left), height(node.right)
        best = max(best, left + right)       # a path that bends at this node
        return 1 + max(left, right)          # what the parent needs

    height(root)
    return best
```

If you call a separate `height()` at every node, it costs O(n²). Doing both jobs in one pass costs O(n). The same shape solves *lowest common ancestor*, *max path sum* and *is this tree balanced?*.

### 8. Cost

| | Time | Extra space |
|---|---|---|
| Visit every node | O(n) | O(h), where h is the height (the call stack) |
| Balanced tree | O(n) | O(log n) |
| A chain | O(n) | O(n), and recursion may crash |
| Level order | O(n) | O(w), where w is the widest row |

:::tip[🧭 How to spot a tree problem]
- The data has a **parent → children** shape (folders, comments, menus, JSON, org charts).
- The words **root, leaf, depth, path, ancestor, subtree**.
- The answer for a node depends on the answers for its **children**.
- You are asked for something **per level** (level order) or **in sorted order** (inorder on a BST).

If every node can connect to any other node, and there can be loops, it is a **graph**, not a tree (BFS/DFS lessons).
:::

### Choosing your setup

| Situation | Use |
|---|---|
| Answer depends on the children's answers | recursion: base case + combine |
| Need results row by row, or the shortest distance | level order with a queue |
| Tree may be very deep | your own stack (iterative) |
| Compare two trees or two sides | recurse on both at once |
| Longest/best path that may bend inside | return height, update a best on the side |

- ✅ Hierarchies, nested data, "for each level" questions.
- 🚫 Data with loops or many parents (use a graph).
- 🚫 Recursion on a tree that may be a 100,000-node chain.

## ⚠️ Common mistakes

- Forgetting the base case for `None`, or checking `root.left` before checking `root`.
- Mixing up **height** in nodes and in edges. Pick one and say it out loud.
- Path sums that end on any node instead of on a **leaf**.
- Calling `height()` at every node (O(n²)).
- Recursing on a chain of 50,000 nodes in Python.
- Changing a list (`path.append`) and forgetting to undo it (`path.pop`) when backtracking.

## 🏆 Best practices

- [ ] Write the base case first, in one line.
- [ ] Say in words: "the answer for a node is made from …".
- [ ] Test with the **empty tree**, a **single node**, a **chain** and a **balanced tree**.
- [ ] State height in nodes or edges, and be consistent.
- [ ] Return the value the parent needs, and keep side results in a variable (`nonlocal`).
- [ ] Say the time (O(n)) and the space (O(h)) before the interviewer asks.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a teammate how to find the total size of a folder (including all folders inside it) using the org-chart idea. Where does the base case come from?

## 📐 Design it

CareerPilot's notes have **threaded replies**: a note can have replies, and each reply can have replies. The web app needs to (1) show the whole thread indented, (2) show "12 replies" on top, and (3) load only the first 3 levels at first. Design the data and the algorithm.

:::quiz
Show a possible design

- **Data:** each reply row has `id`, `parent_id` (null for the top note), `text`. In memory, build a tree: a dict `id → node`, then attach each node to its parent's `children` list. One pass, O(n).
- **Indented display:** a **preorder** walk, passing `depth` down: print `"  " * depth + text`, then walk each child with `depth + 1`. Parent first, then its replies.
- **Reply count:** a **postorder**/size calculation: `count(node) = sum(count(child) + 1 for child in children)`. Each node asks its children, then answers its parent.
- **First 3 levels:** a **level order** walk (queue) that stops at depth 3, or a recursive walk with a `max_depth` argument. Show "load more" on nodes that still have hidden children.
- **Deep threads:** a thread can be a long chain, so for safety use an iterative walk, or cap the depth in the product.
- **At scale:** fetch only the levels you need with SQL (`WITH RECURSIVE`), not the whole table.

**Rule shown:** a tree walk with the right order (parent first, children first, or row by row) answers display, counting and paging questions.
:::

### 📝 Self-review checklist

- [ ] I named the traversal order and said why
- [ ] The base case (empty tree) is handled
- [ ] Deep trees are considered (stack or depth cap)
- [ ] Time and space are stated

::ai-review{task="design"}

::part[Practice Problems]{n="3"}

:::problem{id="dsa-s4-tree-basics" title="Tree Basics" difficulty="easy" path="exercises/dsa/stage-4/01-tree-basics"}
Size, height, number of leaves and the sum of all values. Four functions, one recipe: base case plus combine.
:::

:::problem{id="dsa-s4-tree-traversals" title="Tree Traversals" difficulty="medium" path="exercises/dsa/stage-4/02-tree-traversals"}
Preorder, inorder, postorder and level order. Inorder and level order must survive a 50,000-node chain.
:::

:::problem{id="dsa-s4-mirror-compare" title="Mirror & Compare" difficulty="medium" path="exercises/dsa/stage-4/03-mirror-compare"}
Are two trees the same? Invert a tree. Is a tree symmetric? Walk two nodes at once.
:::

:::problem{id="dsa-s4-paths-diameter-lca" title="Paths, Diameter and Lowest Common Ancestor" difficulty="hard" path="exercises/dsa/stage-4/04-paths-diameter-lca"}
Stretch: root-to-leaf path sums and lists, the diameter in one pass, and the lowest common ancestor.
:::

:::hints
- Every function starts with `if root is None:`. Decide what the empty tree returns (0, `[]`, `True`, `False`).
- `height`: `1 + max(height(left), height(right))`. `count_leaves`: a node with no children counts 1.
- Iterative inorder: push the left chain, pop and visit, then go right.
- Level order: at the start of each round take `len(queue)` as the size of the row.
- `is_symmetric`: compare `left.left` with `right.right`, and `left.right` with `right.left`.
- `has_path_sum`: only check the target at a **leaf**; pass `target - root.val` down.
- `root_to_leaf_paths`: `append` when you enter a node, `pop` when you leave; store a **copy** (`list(path)`) of the full path.
- `diameter`: a helper that returns the height and updates `best = max(best, left + right)`.
- `lowest_common_ancestor`: if both sides return a node, the current node is the answer; also check that both values exist.
:::

## ✅ Quick check

:::quiz
Why is a recursive tree function usually short?

It only needs a base case for the empty tree and a way to combine the answers of the left and right subtrees. The recursion handles all the depth, so you do not trace every level yourself.
:::

:::quiz
Why does a recursive inorder crash on a chain of 50,000 nodes in Python, and what do you do?

Python limits nested calls to about 1,000, and each node adds one call. Do the call stack's job yourself: use a list as a stack (or a deque as a queue for level order), so memory is the only limit.
:::

:::quiz
Which traversal order gives the values of a binary search tree in sorted order?

Inorder (left, node, right). Everything on the left is smaller and everything on the right is larger, so visiting left, then the node, then right produces ascending order.
:::

## 📚 Keep learning

- [Python docs: collections.deque](https://docs.python.org/3/library/collections.html#collections.deque)
- [Wikipedia: Tree traversal](https://en.wikipedia.org/wiki/Tree_traversal)
- [VisuAlgo: Binary tree traversals (interactive)](https://visualgo.net/en/bst)

---
title: "Binary Search Trees"
summary: Use the BST rule (smaller on the left, larger on the right) to search, insert and delete in O(h), validate a tree with bounds instead of parent checks, and see why balance decides whether a BST is fast or a slow chain.
type: lesson
source: original
roles: { be: core, fe: core, fs: core, ai: core, ops: recommended }
durationMinutes: 180
tags: [dsa, bst, binary-search-tree, trees, balance, interviews]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- The **BST rule** and how it lets you skip half the tree at each step
- **Search, insert, min and max** by walking down one path
- **Delete** a node (three cases) and keep the tree valid
- **Validate** a BST the right way (bounds, not just the parent)
- Why a BST can degrade to a chain, and how **balance** fixes it
- 🧭 How to recognize a BST problem

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **BST** | A binary tree where left is smaller and right is larger, at every node | Pohon pencarian biner |
| **Invariant** | A rule that must stay true after every operation | Aturan yang harus selalu benar |
| **Successor** | The next larger value (the smallest on the right side) | Nilai berikutnya yang lebih besar |
| **Floor / ceiling** | The closest value below or equal / above or equal | Nilai terdekat bawah / atas |
| **Balanced** | Left and right sides have about the same height | Seimbang |
| **Degenerate** | A tree that became a chain, so it is slow | Menjadi rantai |
| **O(h)** | Cost grows with the tree's height | Biaya sebanding tinggi pohon |

## 🧠 The big idea

A BST is a **dictionary** you can open in the middle. You look for the word "mango". You open the book in the middle and see "kiwi". "Mango" comes after "kiwi", so you throw away the whole first half and look only in the second half. Each step removes half of what is left.

The BST rule is the same promise at every node: **everything on the left is smaller, everything on the right is larger**. Because that promise holds everywhere, one comparison tells you which half to ignore.

## ❓ Why it matters

Fast lookup in a **sorted, changing** collection is a common need:

- the **index** of a database (most are B-trees, a cousin of the BST),
- an in-memory **ordered map** ("give me the next larger key"),
- **autocomplete ranges**, scheduling ("what is the next free slot after 3 pm?"),
- sets and maps with a **sorted order** (`TreeMap` in Java, `SortedDict` in Python libraries).

A plain sorted list searches fast (binary search), but inserting in the middle moves many items. A hash map inserts fast, but cannot answer "the next larger key". A BST gives you all three, as long as it stays **balanced**.

## 📖 Step by step

### 1. The rule, and the clue it gives

```text
        8
       / \
      3   10         left of 8 :  3, 1, 6, 4, 7   (all smaller than 8)
     / \    \        right of 8:  10, 14, 13      (all larger than 8)
    1   6    14
       / \   /
      4   7 13
```

The same rule holds at **every** node, not only at the root. So an **inorder** walk (left, node, right) gives the values **sorted**: `1 3 4 6 7 8 10 13 14`.

### 2. Search: follow one path

```python
def search(root, val):
    node = root
    while node:
        if val == node.val:
            return True
        node = node.left if val < node.val else node.right
    return False
```

You never look at both sides. Looking for 6 in the tree above: `8 → left → 3 → right → 6`. That is 3 steps, not 9.

The cost is **O(h)**, where h is the height. In a balanced tree h is about log n, so a million values need about 20 steps.

### 3. Insert: search, then attach a leaf

```python
def insert(root, val):
    if root is None:
        return TreeNode(val)
    node = root
    while True:
        if val == node.val:
            return root                      # already there
        side = "left" if val < node.val else "right"
        nxt = getattr(node, side)
        if nxt is None:
            setattr(node, side, TreeNode(val))
            return root
        node = nxt
```

A new value always becomes a **leaf**. Nothing else moves.

### 4. Smallest and largest

Smallest: keep going left. Largest: keep going right. Both O(h).

### 5. Delete: three cases

Deleting is the tricky one, because you must keep the rule true.

```python
def delete(root, val):
    if root is None:
        return None
    if val < root.val:
        root.left = delete(root.left, val)
    elif val > root.val:
        root.right = delete(root.right, val)
    else:
        if root.left is None:                 # leaf, or only a right child
            return root.right
        if root.right is None:                # only a left child
            return root.left
        successor = root.right                # two children: take the next larger value
        while successor.left:
            successor = successor.left
        root.val = successor.val
        root.right = delete(root.right, successor.val)
    return root
```

```text
leaf          → remove it
one child     → the child takes its place
two children  → copy the INORDER SUCCESSOR (smallest on the right) into this node,
                then delete that successor from the right subtree
```

Why the successor? It is larger than everything on the left and smaller than everything else on the right, so the rule still holds.

### 6. Validate: pass bounds down

The classic mistake is to check each node only against its parent:

```text
      5
     / \
    1   4          4 > 1? fine.   3 < 4? fine.
       / \         But 3 is in the RIGHT side of 5, so it must be larger than 5. This is NOT a BST.
      3   6
```

A node must be between **all** its ancestors' limits. Carry a `low` and a `high` down:

```python
def is_valid_bst(root):
    def ok(node, low, high):
        if node is None:
            return True
        if (low is not None and node.val <= low) or (high is not None and node.val >= high):
            return False
        return ok(node.left, low, node.val) and ok(node.right, node.val, high)

    return ok(root, None, None)
```

Another way: an **inorder walk must be strictly increasing**.

### 7. Order questions: inorder helps

Because inorder is sorted, many questions become easy:

- **k-th smallest:** inorder with a stack, stop at the k-th node you pop.
- **floor / ceiling of x:** walk down one path. Going right? the current value is a floor candidate. Going left? it is a ceiling candidate.
- **range sum between a and b:** skip a whole subtree when it is out of range.
- **lowest common ancestor:** if both values are smaller go left, both larger go right, otherwise this node is the answer. This is O(h), better than the general-tree version.

### 8. Balance is everything

Insert 1, 2, 3, 4, 5 in that order:

```text
1
 \
  2             a chain: height 5, search is O(n)
   \
    3
     \
      4
       \
        5
```

The same five values in a good order give a tree of height 3. A BST is only fast when it is **balanced**.

Build a balanced tree from sorted data by making the **middle** value the root, then doing the same for each half:

```python
def sorted_array_to_bst(nums):
    def build(lo, hi):
        if lo > hi:
            return None
        mid = (lo + hi) // 2
        return TreeNode(nums[mid], build(lo, mid - 1), build(mid + 1, hi))

    return build(0, len(nums) - 1)
```

To check balance, do not call `height()` at every node (O(n²)). Let one helper return the height, or `-1` when a subtree is already unbalanced.

In real systems, trees **balance themselves**: AVL trees, red-black trees (used inside many standard libraries) and B-trees (databases). You will not write them in an interview, but you should say why they exist: to keep h near log n after inserts and deletes.

### 9. Cost

| Operation | Balanced | Worst (a chain) |
|---|---|---|
| Search / insert / delete | O(log n) | O(n) |
| Min / max | O(log n) | O(n) |
| Inorder (sorted list) | O(n) | O(n) |
| Space (recursive) | O(log n) | O(n) |

:::tip[🧭 How to spot a BST problem]
- The data is **sorted** or must be kept sorted while changing.
- Words like **successor, predecessor, floor, ceiling, k-th smallest, in a range**.
- The input says "binary search tree" and you can use the left/right rule.
- You need **ordered** operations that a hash map cannot do.

Only lookup by key, no order? A hash map is simpler and O(1). A fixed sorted array that never changes? Plain binary search is enough.
:::

### Choosing your setup

| Need | Use |
|---|---|
| Lookup only | hash map |
| Sorted data that never changes | sorted array + binary search |
| Sorted data with inserts and deletes, next/previous key | balanced BST (or a sorted container library) |
| Just the smallest or largest item, repeatedly | heap (next lesson) |
| Build a tree from sorted data | middle value as root, recursively |

- ✅ Ordered maps, range queries, "next larger", schedules.
- 🚫 Plain key lookup (use a hash map).
- 🚫 Inserting already-sorted data into a plain BST (it becomes a chain).

## ⚠️ Common mistakes

- Validating only against the parent instead of passing bounds.
- Treating equal values as valid when the problem says they are not (state your rule).
- In `delete`, forgetting to return the new subtree root, so the tree is not reconnected.
- Searching both subtrees when the BST rule tells you which one.
- Inserting sorted data into a plain BST and expecting O(log n).
- Using recursion on a very deep, degenerate tree.

## 🏆 Best practices

- [ ] Say the invariant out loud: "left smaller, right larger, at every node".
- [ ] Use the rule to walk **one** path. If you visit both sides, ask why.
- [ ] Pass `low` and `high` bounds to validate.
- [ ] Handle the three delete cases separately, and test each one.
- [ ] State the cost as O(h), then say "O(log n) if balanced".
- [ ] Mention self-balancing trees (AVL, red-black, B-tree) when asked about worst cases.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a friend why looking up a word in a dictionary is like searching a BST, and why a dictionary printed in a wrong order (a chain) would be useless.

## 📐 Design it

CareerPilot's calendar must answer: "What is the next interview after this time?", "Is this time slot free?" and "Show all interviews between two dates". Interviews are added, moved and cancelled often. Design the data structure and say what each question costs.

:::quiz
Show a possible design

- **Keep interviews in a balanced ordered structure** keyed by start time (a balanced BST, or a sorted container such as `sortedcontainers.SortedList`). Add, move (delete + insert) and cancel all cost O(log n).
- **Next interview after t:** the *ceiling* of t (smallest start ≥ t, or the successor) — one path down, O(log n).
- **Is this slot free?** find the *floor* (the previous interview) and the *ceiling* (the next one) and check that the new slot fits between them. O(log n).
- **All interviews between two dates:** find the first one ≥ start, then walk inorder until you pass the end date. O(log n + k) for k results.
- **Why not a plain list?** inserting in the middle moves items, and searching needs binary search plus re-sorting after changes.
- **Why not a hash map?** it cannot answer "next after t" or ranges.
- **In the database:** an index on `start_time` is a B-tree and gives the same operations; the application structure matters when the data is in memory.
- **Warning:** a plain BST fed sorted timestamps becomes a chain, so use a self-balancing one.

**Rule shown:** when you need data kept in order with fast updates plus next/previous/range queries, think balanced BST.
:::

### 📝 Self-review checklist

- [ ] I named which operations need order (next, previous, range)
- [ ] I compared at least a list and a hash map
- [ ] I mentioned balance
- [ ] I gave the cost of each operation

::ai-review{task="design"}

::part[Practice Problems]{n="3"}

:::problem{id="dsa-s4-bst-basics" title="BST Basics" difficulty="easy" path="exercises/dsa/stage-4/05-bst-basics"}
Search, insert, smallest and largest by following one path down the tree.
:::

:::problem{id="dsa-s4-validate-kth" title="Validate a BST & k-th Smallest" difficulty="medium" path="exercises/dsa/stage-4/06-validate-kth"}
Bounds, not just parents. Then the k-th smallest with your own stack on a 30,000-node chain.
:::

:::problem{id="dsa-s4-sorted-to-balanced" title="Sorted Array to Balanced BST" difficulty="medium" path="exercises/dsa/stage-4/07-sorted-to-balanced"}
Build a balanced BST from sorted data, and check balance in one pass.
:::

:::problem{id="dsa-s4-bst-delete-floor-lca" title="BST: Delete, Floor/Ceiling and LCA" difficulty="hard" path="exercises/dsa/stage-4/08-bst-delete-floor-lca"}
Stretch: delete with three cases, floor and ceiling in O(h), and the lowest common ancestor without a full search.
:::

:::hints
- `search`/`insert`: loop with `node = node.left if val < node.val else node.right`; no recursion needed.
- `is_valid_bst`: the helper takes `(node, low, high)`; the left child gets `high = node.val`, the right child gets `low = node.val`. Equal values are invalid.
- `kth_smallest`: iterative inorder; count down `k` each time you pop; return when it reaches 0.
- `sorted_array_to_bst`: `mid = (lo + hi) // 2`; the left half is `lo..mid-1`, the right half is `mid+1..hi`.
- `is_balanced`: return `-1` from the helper when a subtree is unbalanced; otherwise return its height.
- `delete`: always assign the result back (`root.left = delete(root.left, val)`); for two children, copy the smallest value of the right subtree, then delete it there.
- `floor_ceiling`: going right means the current value is a floor candidate; going left means it is a ceiling candidate; if equal, return `(x, x)`.
- `lca_in_bst`: both smaller → left; both larger → right; otherwise return the current value.
:::

## ✅ Quick check

:::quiz
Why is checking each node only against its parent not enough to validate a BST?

A node must respect the limits of **all** its ancestors, not just its parent. A value deep in the right subtree of 5 can be larger than its own parent and still be smaller than 5, which breaks the rule. Pass `low` and `high` bounds down, or check that an inorder walk is strictly increasing.
:::

:::quiz
Why does inserting 1, 2, 3, 4, 5 in order into a plain BST make searches slow?

Each new value is larger than everything so far, so it always goes right. The tree becomes a chain of height n, and search costs O(n) instead of O(log n). Self-balancing trees (AVL, red-black) or building from the middle of sorted data keep the height near log n.
:::

:::quiz
When deleting a node with two children, why do we use the inorder successor?

The successor is the smallest value on the right side. It is larger than everything on the left and smaller than everything else on the right, so putting it in the deleted node's place keeps the BST rule true. Then we delete the successor itself, which has at most one child.
:::

## 📚 Keep learning

- [VisuAlgo: Binary Search Tree (interactive)](https://visualgo.net/en/bst)
- [Wikipedia: Self-balancing binary search tree](https://en.wikipedia.org/wiki/Self-balancing_binary_search_tree)
- [sortedcontainers: SortedList and SortedDict](https://grantjenks.com/docs/sortedcontainers/)

import random

from tree_paths import TreeNode, diameter, has_path_sum, lowest_common_ancestor, root_to_leaf_paths

def build(values):
    """Build a tree from a level-order list; None means "no node"."""
    if not values or values[0] is None:
        return None
    nodes = [None if v is None else TreeNode(v) for v in values]
    children = iter(nodes[1:])
    for node in nodes:
        if node is None:
            continue
        node.left = next(children, None)
        node.right = next(children, None)
    return nodes[0]


def random_tree(rng, n):
    """A random binary tree with n nodes (values 1..n, all different)."""
    if n == 0:
        return None
    nodes = [TreeNode(v) for v in rng.sample(range(1, n + 1), n)]
    for i in range(1, n):
        while True:
            parent = nodes[rng.randrange(i)]
            side = "left" if rng.random() < 0.5 else "right"
            if getattr(parent, side) is None:
                setattr(parent, side, nodes[i])
                break
    return nodes[0]


EX = [5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1]


def test_has_path_sum_examples():
    root = build(EX)
    assert has_path_sum(root, 22)       # 5 -> 4 -> 11 -> 2
    assert has_path_sum(root, 26)       # 5 -> 8 -> 13
    assert not has_path_sum(root, 5)    # 5 alone is not a leaf
    assert not has_path_sum(root, 100)


def test_has_path_sum_edges():
    assert not has_path_sum(None, 0)
    assert has_path_sum(TreeNode(3), 3)
    assert not has_path_sum(build([1, 2]), 1)       # node 1 has a child, so it is not a leaf
    assert has_path_sum(build([-2, None, -3]), -5)  # negative values


def test_root_to_leaf_paths():
    assert root_to_leaf_paths(build([1, 2, 3, None, 5])) == [[1, 2, 5], [1, 3]]
    assert root_to_leaf_paths(TreeNode(1)) == [[1]]
    assert root_to_leaf_paths(None) == []


def test_paths_are_independent_lists():
    paths = root_to_leaf_paths(build([1, 2, 3]))
    paths[0].append(99)
    assert paths == [[1, 2, 99], [1, 3]]


def brute_diameter(root):
    """Longest path via parent links: BFS from every node."""
    nodes, parent = [], {}
    stack = [root] if root else []
    while stack:
        n = stack.pop()
        nodes.append(n)
        for c in (n.left, n.right):
            if c:
                parent[c] = n
                stack.append(c)
    best = 0
    for start in nodes:
        seen, frontier, dist = {start}, [start], 0
        while frontier:
            nxt = []
            for n in frontier:
                for m in (n.left, n.right, parent.get(n)):
                    if m and m not in seen:
                        seen.add(m)
                        nxt.append(m)
            if nxt:
                dist += 1
            frontier = nxt
        best = max(best, dist)
    return best


def test_diameter_examples():
    assert diameter(None) == 0
    assert diameter(TreeNode(1)) == 0
    assert diameter(build([1, 2, 3, 4, 5])) == 3          # 4 -> 2 -> 1 -> 3  (or 5 -> 2 -> 1 -> 3)
    assert diameter(build([1, 2])) == 1


def test_diameter_not_through_the_root():
    # the long path is inside the left subtree
    left = build([2, 3, 4, 5, None, None, 6, 7, None, None, 8])
    root = TreeNode(1, left)
    assert diameter(root) == brute_diameter(root)
    assert diameter(root) >= 5


def test_diameter_matches_brute_force():
    rng = random.Random(8)
    for _ in range(200):
        root = random_tree(rng, rng.randint(0, 22))
        assert diameter(root) == brute_diameter(root)


def test_diameter_of_a_caterpillar():
    # A spine of 450 nodes, each with one extra leaf: the longest path runs from the deepest
    # spine node up to the root and down to the root's extra leaf.
    root = TreeNode(0)
    node = root
    for i in range(1, 450):
        node.left = TreeNode(i)
        node.right = TreeNode(-i)
        node = node.left
    assert diameter(root) == 450


LCA = [3, 5, 1, 6, 2, 0, 8, None, None, 7, 4]


def test_lca_examples():
    root = build(LCA)
    assert lowest_common_ancestor(root, 5, 1) == 3
    assert lowest_common_ancestor(root, 5, 4) == 5      # a node is below itself
    assert lowest_common_ancestor(root, 7, 4) == 2
    assert lowest_common_ancestor(root, 6, 4) == 5
    assert lowest_common_ancestor(root, 6, 6) == 6


def test_lca_missing_value():
    root = build(LCA)
    assert lowest_common_ancestor(root, 5, 99) is None
    assert lowest_common_ancestor(root, 99, 5) is None
    assert lowest_common_ancestor(None, 1, 2) is None


def test_lca_matches_brute_force():
    rng = random.Random(9)
    for _ in range(200):
        n = rng.randint(2, 20)
        root = random_tree(rng, n)
        paths = {}
        for path in root_to_leaf_paths(root):
            for i, v in enumerate(path):
                paths.setdefault(v, path[: i + 1])
        p, q = rng.randint(1, n), rng.randint(1, n)
        common = [a for a, b in zip(paths[p], paths[q]) if a == b]
        assert lowest_common_ancestor(root, p, q) == common[-1]

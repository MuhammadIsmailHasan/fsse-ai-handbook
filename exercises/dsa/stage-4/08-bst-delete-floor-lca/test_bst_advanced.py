import random

from bst_advanced import TreeNode, delete, floor_ceiling, lca_in_bst

def bst(values):
    """Reference: build a BST by iterative insertion (duplicates ignored)."""
    root = None
    for v in values:
        if root is None:
            root = TreeNode(v)
            continue
        node = root
        while True:
            if v == node.val:
                break
            side = "left" if v < node.val else "right"
            nxt = getattr(node, side)
            if nxt is None:
                setattr(node, side, TreeNode(v))
                break
            node = nxt
    return root


def inorder_ref(root):
    out, stack, node = [], [], root
    while node or stack:
        while node:
            stack.append(node)
            node = node.left
        node = stack.pop()
        out.append(node.val)
        node = node.right
    return out


def valid(root):
    values = inorder_ref(root)
    return all(a < b for a, b in zip(values, values[1:]))


def test_delete_a_leaf():
    root = delete(bst([5, 3, 8]), 3)
    assert inorder_ref(root) == [5, 8]
    assert root.left is None


def test_delete_a_node_with_one_child():
    root = delete(bst([5, 3, 8, 7]), 8)
    assert inorder_ref(root) == [3, 5, 7]
    assert root.right.val == 7


def test_delete_a_node_with_two_children_uses_the_successor():
    root = delete(bst([5, 3, 8, 7, 9]), 5)
    assert root.val == 7                      # smallest value in the right subtree
    assert inorder_ref(root) == [3, 7, 8, 9]


def test_delete_the_root_of_a_single_node_tree():
    assert delete(TreeNode(4), 4) is None


def test_delete_missing_value_changes_nothing():
    root = bst([5, 3, 8])
    assert inorder_ref(delete(root, 99)) == [3, 5, 8]
    assert delete(None, 1) is None


def test_random_deletes_keep_a_valid_bst():
    rng = random.Random(51)
    for _ in range(200):
        values = rng.sample(range(100), rng.randint(0, 25))
        root = bst(values)
        remaining = set(values)
        for v in rng.sample(range(100), 20):
            root = delete(root, v)
            remaining.discard(v)
            assert inorder_ref(root) == sorted(remaining)
            assert valid(root)


def test_floor_and_ceiling():
    root = bst([8, 3, 10, 1, 6, 14, 4, 7, 13])
    assert floor_ceiling(root, 5) == (4, 6)
    assert floor_ceiling(root, 6) == (6, 6)
    assert floor_ceiling(root, 0) == (None, 1)
    assert floor_ceiling(root, 15) == (14, None)
    assert floor_ceiling(root, 9) == (8, 10)
    assert floor_ceiling(None, 3) == (None, None)


def test_floor_ceiling_matches_sorted_list():
    rng = random.Random(52)
    for _ in range(200):
        values = rng.sample(range(0, 60, 2), rng.randint(0, 20))
        root = bst(values)
        for x in range(-2, 64):
            below = [v for v in values if v <= x]
            above = [v for v in values if v >= x]
            expected = (max(below) if below else None, min(above) if above else None)
            assert floor_ceiling(root, x) == expected


def test_lca_in_bst():
    root = bst([6, 2, 8, 0, 4, 7, 9, 3, 5])
    assert lca_in_bst(root, 2, 8) == 6
    assert lca_in_bst(root, 2, 4) == 2
    assert lca_in_bst(root, 3, 5) == 4
    assert lca_in_bst(root, 0, 5) == 2
    assert lca_in_bst(root, 7, 9) == 8
    assert lca_in_bst(root, 4, 4) == 4


def test_lca_matches_path_comparison():
    rng = random.Random(53)
    for _ in range(200):
        values = rng.sample(range(100), rng.randint(2, 25))
        root = bst(values)

        def path(target):
            node, out = root, []
            while node:
                out.append(node.val)
                if node.val == target:
                    return out
                node = node.left if target < node.val else node.right

        p, q = rng.sample(values, 2)
        common = [a for a, b in zip(path(p), path(q)) if a == b]
        assert lca_in_bst(root, p, q) == common[-1]

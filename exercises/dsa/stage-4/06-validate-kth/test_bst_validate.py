import random
import time

import pytest

from bst_validate import TreeNode, is_valid_bst, kth_smallest

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


def build(values):
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


def strictly_increasing_inorder(root):
    values = inorder_ref(root)
    return all(a < b for a, b in zip(values, values[1:]))


def test_valid_examples():
    assert is_valid_bst(None)
    assert is_valid_bst(TreeNode(1))
    assert is_valid_bst(build([2, 1, 3]))
    assert is_valid_bst(build([5, 3, 8, 1, 4, 7, 9]))


def test_simple_violation():
    assert not is_valid_bst(build([2, 3, 1]))


def test_the_classic_trap_a_deep_node_breaks_an_upper_rule():
    # 3 is less than its parent 4, but 3 is in the RIGHT subtree of 5, so it must be > 5.
    assert not is_valid_bst(build([5, 1, 4, None, None, 3, 6]))
    # Same idea on the left side: 6 is in the left subtree of 5.
    assert not is_valid_bst(build([5, 4, 7, 1, 6]))


def test_equal_values_are_invalid():
    assert not is_valid_bst(build([2, 2, 2]))
    assert not is_valid_bst(build([2, 2]))
    assert not is_valid_bst(build([2, None, 2]))


def test_large_and_negative_values():
    assert is_valid_bst(build([0, -10**12, 10**12]))
    assert is_valid_bst(build([-1, -5, 3]))


def test_random_trees_match_the_inorder_check():
    rng = random.Random(31)
    for _ in range(400):
        n = rng.randint(0, 12)
        vals = rng.sample(range(1, 40), n)
        # random shape, random values: mostly invalid
        nodes = [TreeNode(v) for v in vals]
        for i in range(1, n):
            while True:
                parent = nodes[rng.randrange(i)]
                side = rng.choice(["left", "right"])
                if getattr(parent, side) is None:
                    setattr(parent, side, nodes[i])
                    break
        root = nodes[0] if nodes else None
        assert is_valid_bst(root) == strictly_increasing_inorder(root)
    for _ in range(100):
        root = bst(rng.sample(range(100), rng.randint(0, 15)))
        assert is_valid_bst(root)


def test_kth_smallest_examples():
    root = bst([5, 3, 6, 2, 4, 1])
    assert [kth_smallest(root, k) for k in range(1, 7)] == [1, 2, 3, 4, 5, 6]


def test_kth_smallest_out_of_range():
    root = bst([2, 1, 3])
    for k in (0, -1, 4, 100):
        with pytest.raises(ValueError):
            kth_smallest(root, k)
    with pytest.raises(ValueError):
        kth_smallest(None, 1)


def test_kth_smallest_matches_sorted_order():
    rng = random.Random(32)
    for _ in range(100):
        values = rng.sample(range(-50, 50), rng.randint(1, 20))
        root = bst(values)
        for k in range(1, len(values) + 1):
            assert kth_smallest(root, k) == sorted(values)[k - 1]


def test_kth_smallest_on_a_very_deep_tree_and_stops_early():
    root = TreeNode(0)
    node = root
    for i in range(1, 30_000):
        node.right = TreeNode(i)
        node = node.right
    started = time.perf_counter()
    assert kth_smallest(root, 1) == 0
    assert kth_smallest(root, 30_000) == 29_999
    assert time.perf_counter() - started < 2.0

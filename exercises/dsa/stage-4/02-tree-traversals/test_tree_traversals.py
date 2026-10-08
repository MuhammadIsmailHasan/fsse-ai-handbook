import random
import time

import pytest

from tree_traversals import TreeNode, inorder, level_order, postorder, preorder

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


def ref_inorder(node):
    return ref_inorder(node.left) + [node.val] + ref_inorder(node.right) if node else []


def ref_preorder(node):
    return [node.val] + ref_preorder(node.left) + ref_preorder(node.right) if node else []


def ref_postorder(node):
    return ref_postorder(node.left) + ref_postorder(node.right) + [node.val] if node else []


EXAMPLE = [1, 2, 3, 4, 5, None, 6]


def test_example_orders():
    root = build(EXAMPLE)
    assert preorder(root) == [1, 2, 4, 5, 3, 6]
    assert inorder(root) == [4, 2, 5, 1, 3, 6]
    assert postorder(root) == [4, 5, 2, 6, 3, 1]
    assert level_order(root) == [[1], [2, 3], [4, 5, 6]]


def test_empty_tree():
    assert preorder(None) == inorder(None) == postorder(None) == []
    assert level_order(None) == []


def test_single_node():
    root = TreeNode(9)
    assert preorder(root) == inorder(root) == postorder(root) == [9]
    assert level_order(root) == [[9]]


def test_inorder_of_a_bst_is_sorted():
    root = build([4, 2, 6, 1, 3, 5, 7])
    assert inorder(root) == [1, 2, 3, 4, 5, 6, 7]


def test_random_trees_match_reference():
    rng = random.Random(11)
    for _ in range(300):
        root = random_tree(rng, rng.randint(0, 20))
        assert preorder(root) == ref_preorder(root)
        assert inorder(root) == ref_inorder(root)
        assert postorder(root) == ref_postorder(root)
        flat = [v for level in level_order(root) for v in level]
        assert sorted(flat) == sorted(ref_preorder(root))


def chain(n, side):
    root = TreeNode(0)
    node = root
    for i in range(1, n):
        child = TreeNode(i)
        setattr(node, side, child)
        node = child
    return root


@pytest.mark.parametrize("side", ["left", "right"])
def test_inorder_handles_a_very_deep_tree(side):
    root = chain(50_000, side)
    started = time.perf_counter()
    result = inorder(root)
    assert len(result) == 50_000
    assert result == (list(range(50_000)) if side == "right" else list(range(49_999, -1, -1)))
    assert time.perf_counter() - started < 2.0


def test_level_order_handles_a_very_deep_tree():
    levels = level_order(chain(50_000, "left"))
    assert len(levels) == 50_000
    assert levels[0] == [0] and levels[-1] == [49_999]

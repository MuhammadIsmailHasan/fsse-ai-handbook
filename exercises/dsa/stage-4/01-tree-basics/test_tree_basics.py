import random

import pytest

from tree_basics import TreeNode, count_leaves, height, size, sum_values

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


def walk(root):
    """Reference: visit every node with an explicit stack (no recursion)."""
    stack, out = ([root] if root else []), []
    while stack:
        node = stack.pop()
        out.append(node)
        stack += [c for c in (node.left, node.right) if c]
    return out


def test_empty_tree():
    assert size(None) == 0
    assert height(None) == 0
    assert count_leaves(None) == 0
    assert sum_values(None) == 0


def test_single_node():
    root = TreeNode(7)
    assert (size(root), height(root), count_leaves(root), sum_values(root)) == (1, 1, 1, 7)


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        ([1, 2, 3], (3, 2, 2, 6)),
        ([1, 2, 3, 4, 5, None, 6], (6, 3, 3, 21)),
        ([1, 2, None, 3, None, 4], (4, 4, 1, 10)),      # a left-leaning chain
        ([1, None, 2, None, 3], (3, 3, 1, 6)),          # a right-leaning chain
        ([5, 4, 8, 11, None, 13, 4, 7, 2, None, None, None, 1], (9, 4, 4, 55)),
    ],
)
def test_examples(values, expected):
    root = build(values)
    assert (size(root), height(root), count_leaves(root), sum_values(root)) == expected


def test_negative_values():
    root = build([-1, -2, 3])
    assert sum_values(root) == 0


def test_random_trees_match_reference():
    rng = random.Random(7)
    for _ in range(300):
        root = random_tree(rng, rng.randint(0, 25))
        nodes = walk(root)
        assert size(root) == len(nodes)
        assert sum_values(root) == sum(n.val for n in nodes)
        assert count_leaves(root) == sum(1 for n in nodes if not n.left and not n.right)

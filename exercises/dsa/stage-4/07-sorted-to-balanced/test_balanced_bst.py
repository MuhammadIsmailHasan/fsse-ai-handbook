import math
import random

import pytest

from balanced_bst import TreeNode, is_balanced, sorted_array_to_bst

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


def height(node):
    return 0 if node is None else 1 + max(height(node.left), height(node.right))


def naive_balanced(node):
    if node is None:
        return True
    return abs(height(node.left) - height(node.right)) <= 1 and naive_balanced(node.left) and naive_balanced(node.right)


def test_empty_and_single():
    assert sorted_array_to_bst([]) is None
    root = sorted_array_to_bst([7])
    assert root.val == 7 and root.left is None and root.right is None


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5, 6, 7, 8, 15, 16, 100, 1000])
def test_result_is_a_balanced_bst_with_the_same_values(n):
    nums = list(range(10, 10 + 3 * n, 3))
    root = sorted_array_to_bst(nums)
    assert inorder_ref(root) == nums
    assert height(root) <= math.ceil(math.log2(n + 1))
    assert naive_balanced(root)


def test_random_sorted_inputs():
    rng = random.Random(41)
    for _ in range(100):
        nums = sorted(rng.sample(range(-500, 500), rng.randint(0, 60)))
        root = sorted_array_to_bst(nums)
        assert inorder_ref(root) == nums
        assert is_balanced(root)


def test_is_balanced_examples():
    assert is_balanced(None)
    assert is_balanced(TreeNode(1))
    assert is_balanced(bst([2, 1, 3]))
    assert is_balanced(bst([3, 1, 5, 0, 2]))


def test_a_chain_is_not_balanced():
    assert not is_balanced(bst([1, 2, 3]))
    assert not is_balanced(bst([5, 4, 3, 2, 1]))


def test_unbalanced_deep_inside_while_the_root_looks_fine():
    # The root's two subtrees have equal height, but the left child is unbalanced.
    root = TreeNode(
        10,
        TreeNode(5, TreeNode(3, TreeNode(1)), None),
        TreeNode(15, TreeNode(12), TreeNode(20, None, TreeNode(30))),
    )
    assert height(root.left) == height(root.right) == 3
    assert not is_balanced(root)


def test_random_trees_match_the_naive_check():
    rng = random.Random(42)
    for _ in range(300):
        root = bst([rng.randint(0, 40) for _ in range(rng.randint(0, 14))])
        assert is_balanced(root) == naive_balanced(root)

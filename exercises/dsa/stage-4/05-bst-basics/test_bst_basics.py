import random

from bst_basics import TreeNode, insert, max_value, min_value, search

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


def test_empty_tree():
    assert search(None, 1) is False
    assert min_value(None) is None
    assert max_value(None) is None


def test_insert_into_empty_returns_a_new_root():
    root = insert(None, 5)
    assert root.val == 5 and root.left is None and root.right is None


def test_insert_builds_the_bst_shape():
    root = None
    for v in [5, 3, 8, 1, 4, 9]:
        root = insert(root, v)
    assert root.val == 5
    assert root.left.val == 3 and root.right.val == 8
    assert root.left.left.val == 1 and root.left.right.val == 4
    assert root.right.right.val == 9


def test_insert_returns_the_same_root_object():
    root = TreeNode(5)
    assert insert(root, 3) is root
    assert insert(root, 9) is root


def test_duplicates_are_ignored():
    root = None
    for v in [5, 5, 3, 3, 5]:
        root = insert(root, v)
    assert inorder_ref(root) == [3, 5]


def test_search_finds_present_and_misses_absent():
    root = bst([8, 3, 10, 1, 6, 14, 4, 7, 13])
    for v in [8, 3, 10, 1, 6, 14, 4, 7, 13]:
        assert search(root, v) is True
    for v in [0, 2, 5, 9, 11, 12, 15]:
        assert search(root, v) is False


def test_min_and_max():
    root = bst([8, 3, 10, 1, 6, 14, 4, 7, 13])
    assert min_value(root) == 1
    assert max_value(root) == 14
    assert min_value(TreeNode(4)) == max_value(TreeNode(4)) == 4


def test_negative_values():
    root = None
    for v in [0, -5, 5, -10]:
        root = insert(root, v)
    assert inorder_ref(root) == [-10, -5, 0, 5]


def test_random_inserts_match_a_sorted_set():
    rng = random.Random(21)
    for _ in range(200):
        values = [rng.randint(-30, 30) for _ in range(rng.randint(0, 25))]
        root = None
        for v in values:
            root = insert(root, v)
        assert inorder_ref(root) == sorted(set(values))
        for probe in range(-32, 33):
            assert search(root, probe) == (probe in values)
        if values:
            assert min_value(root) == min(values)
            assert max_value(root) == max(values)

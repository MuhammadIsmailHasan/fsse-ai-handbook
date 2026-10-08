import random

from mirror_compare import TreeNode, invert, is_same_tree, is_symmetric

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


def shape(node):
    return None if node is None else (node.val, shape(node.left), shape(node.right))


def mirrored(node):
    return None if node is None else (node.val, mirrored(node.right), mirrored(node.left))


def test_same_tree():
    assert is_same_tree(build([1, 2, 3]), build([1, 2, 3]))
    assert is_same_tree(None, None)


def test_different_values_or_shapes_are_not_the_same():
    assert not is_same_tree(build([1, 2, 3]), build([1, 2, 4]))
    assert not is_same_tree(build([1, 2]), build([1, None, 2]))     # same values, different shape
    assert not is_same_tree(build([1]), None)
    assert not is_same_tree(None, build([1]))


def test_invert_example():
    root = invert(build([4, 2, 7, 1, 3, 6, 9]))
    assert shape(root) == shape(build([4, 7, 2, 9, 6, 3, 1]))


def test_invert_empty_and_single():
    assert invert(None) is None
    assert shape(invert(TreeNode(5))) == (5, None, None)


def test_invert_twice_gives_the_original():
    rng = random.Random(3)
    for _ in range(100):
        root = random_tree(rng, rng.randint(0, 20))
        expected = shape(root)
        assert shape(invert(invert(root))) == expected


def test_invert_matches_reference():
    rng = random.Random(4)
    for _ in range(100):
        root = random_tree(rng, rng.randint(0, 20))
        expected = mirrored(root)
        assert shape(invert(root)) == expected


def test_symmetric_trees():
    assert is_symmetric(None)
    assert is_symmetric(TreeNode(1))
    assert is_symmetric(build([1, 2, 2, 3, 4, 4, 3]))


def test_not_symmetric():
    assert not is_symmetric(build([1, 2, 2, None, 3, None, 3]))     # same values, wrong sides
    assert not is_symmetric(build([1, 2, 3]))                       # different values
    assert not is_symmetric(build([1, 2]))                          # only one side


def test_a_tree_is_symmetric_iff_it_equals_its_mirror():
    rng = random.Random(5)
    for _ in range(200):
        n = rng.randint(0, 7)
        root = random_tree(rng, n)
        # force many symmetric cases by comparing against a mirrored copy of the left side
        assert is_symmetric(root) == (shape(root.left) == mirrored(root.right) if root else True)

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def is_same_tree(a: TreeNode | None, b: TreeNode | None) -> bool:
    """True if both trees have the same shape AND the same values."""
    raise NotImplementedError


def invert(root: TreeNode | None) -> TreeNode | None:
    """Swap left and right at every node. Return the root of the mirrored tree."""
    raise NotImplementedError


def is_symmetric(root: TreeNode | None) -> bool:
    """True if the tree is a mirror image of itself (an empty tree is symmetric)."""
    raise NotImplementedError

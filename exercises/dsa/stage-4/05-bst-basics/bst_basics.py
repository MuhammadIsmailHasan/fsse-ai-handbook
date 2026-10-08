class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def search(root: TreeNode | None, val: int) -> bool:
    """Is val in the tree? Use the BST rule — do not visit every node."""
    raise NotImplementedError


def insert(root: TreeNode | None, val: int) -> TreeNode:
    """Insert val and return the root. A value that is already there is ignored."""
    raise NotImplementedError


def min_value(root: TreeNode | None) -> int | None:
    """Smallest value, or None for an empty tree."""
    raise NotImplementedError


def max_value(root: TreeNode | None) -> int | None:
    """Largest value, or None for an empty tree."""
    raise NotImplementedError

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def size(root: TreeNode | None) -> int:
    """Number of nodes."""
    raise NotImplementedError


def height(root: TreeNode | None) -> int:
    """Number of nodes on the longest root-to-leaf path (empty tree: 0, single node: 1)."""
    raise NotImplementedError


def count_leaves(root: TreeNode | None) -> int:
    """Number of nodes with no children."""
    raise NotImplementedError


def sum_values(root: TreeNode | None) -> int:
    """Sum of all node values."""
    raise NotImplementedError

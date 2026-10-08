class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def preorder(root: TreeNode | None) -> list[int]:
    """Node, then left subtree, then right subtree."""
    raise NotImplementedError


def inorder(root: TreeNode | None) -> list[int]:
    """Left subtree, node, right subtree.

    Must NOT use recursion: the tests give it a chain of 50,000 nodes.
    Use your own stack.
    """
    raise NotImplementedError


def postorder(root: TreeNode | None) -> list[int]:
    """Left subtree, right subtree, then the node."""
    raise NotImplementedError


def level_order(root: TreeNode | None) -> list[list[int]]:
    """Values level by level, left to right: [[root], [its children], ...].

    Also must NOT use recursion (use a queue).
    """
    raise NotImplementedError

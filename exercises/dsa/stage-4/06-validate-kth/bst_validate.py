class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def is_valid_bst(root: TreeNode | None) -> bool:
    """True if every node is larger than ALL values in its left subtree and smaller than
    ALL values in its right subtree. Equal values make it invalid. Empty tree: valid.

    Watch out: checking only a node against its direct children is not enough.
    """
    raise NotImplementedError


def kth_smallest(root: TreeNode | None, k: int) -> int:
    """The k-th smallest value (k starts at 1) of a valid BST.

    Raise ValueError if k is out of range. Must NOT use recursion: the tests give it a
    chain of 30,000 nodes. Stop as soon as you have the answer.
    """
    raise NotImplementedError

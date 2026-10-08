class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def sorted_array_to_bst(nums: list[int]) -> TreeNode | None:
    """Build a height-balanced BST from a sorted list of different numbers.

    The inorder walk of the result must equal nums, and the height must be at most
    ceil(log2(n + 1)). Empty list: None.
    """
    raise NotImplementedError


def is_balanced(root: TreeNode | None) -> bool:
    """True if, at EVERY node, the heights of the left and right subtrees differ by at most 1.

    Target: O(n) — compute heights and check balance in the same pass.
    """
    raise NotImplementedError

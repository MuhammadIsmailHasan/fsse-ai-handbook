class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def has_path_sum(root: TreeNode | None, target: int) -> bool:
    """Is there a ROOT-TO-LEAF path whose values add up to target? (empty tree: False)"""
    raise NotImplementedError


def root_to_leaf_paths(root: TreeNode | None) -> list[list[int]]:
    """Every root-to-leaf path as a list of values, left to right. Empty tree: []."""
    raise NotImplementedError


def diameter(root: TreeNode | None) -> int:
    """Length (in EDGES) of the longest path between any two nodes.

    The path does not have to pass through the root. Empty or single node: 0.
    Target: O(n) — one pass, not a height() call at every node.
    """
    raise NotImplementedError


def lowest_common_ancestor(root: TreeNode | None, p: int, q: int) -> int | None:
    """Value of the lowest node that has both p and q below it (a node counts as below itself).

    Values are unique. If p or q is missing from the tree, return None.
    """
    raise NotImplementedError

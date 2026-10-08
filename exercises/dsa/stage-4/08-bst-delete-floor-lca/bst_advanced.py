class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def delete(root: TreeNode | None, val: int) -> TreeNode | None:
    """Remove val from the BST and return the (possibly new) root. If val is not there,
    the tree stays as it is. The result must still be a valid BST.

    Three cases: a leaf (just remove it), one child (replace the node by that child),
    two children (copy the INORDER SUCCESSOR — the smallest value on the right — into
    the node, then delete that successor from the right subtree).
    """
    raise NotImplementedError


def floor_ceiling(root: TreeNode | None, x: int) -> tuple[int | None, int | None]:
    """(floor, ceiling): the largest value <= x and the smallest value >= x.
    Use None where there is none. O(h): follow one path down, no full walk."""
    raise NotImplementedError


def lca_in_bst(root: TreeNode | None, p: int, q: int) -> int | None:
    """Lowest common ancestor value of p and q, where both are in the tree.
    O(h): use the BST rule, do not search both subtrees."""
    raise NotImplementedError

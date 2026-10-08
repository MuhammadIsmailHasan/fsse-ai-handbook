class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def size(root):
    if root is None:
        return 0
    return 1 + size(root.left) + size(root.right)


def height(root):
    if root is None:
        return 0
    return 1 + max(height(root.left), height(root.right))


def count_leaves(root):
    if root is None:
        return 0
    if root.left is None and root.right is None:
        return 1
    return count_leaves(root.left) + count_leaves(root.right)


def sum_values(root):
    if root is None:
        return 0
    return root.val + sum_values(root.left) + sum_values(root.right)

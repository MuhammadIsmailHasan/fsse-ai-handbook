class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def is_same_tree(a, b):
    if a is None or b is None:
        return a is b
    return a.val == b.val and is_same_tree(a.left, b.left) and is_same_tree(a.right, b.right)


def invert(root):
    if root is None:
        return None
    root.left, root.right = invert(root.right), invert(root.left)
    return root


def is_symmetric(root):
    def mirror(a, b):
        if a is None or b is None:
            return a is b
        return a.val == b.val and mirror(a.left, b.right) and mirror(a.right, b.left)

    return root is None or mirror(root.left, root.right)

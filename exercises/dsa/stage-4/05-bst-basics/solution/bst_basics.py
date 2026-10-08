class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def search(root, val):
    node = root
    while node:
        if val == node.val:
            return True
        node = node.left if val < node.val else node.right
    return False


def insert(root, val):
    if root is None:
        return TreeNode(val)
    node = root
    while True:
        if val == node.val:
            return root
        side = "left" if val < node.val else "right"
        nxt = getattr(node, side)
        if nxt is None:
            setattr(node, side, TreeNode(val))
            return root
        node = nxt


def min_value(root):
    if root is None:
        return None
    while root.left:
        root = root.left
    return root.val


def max_value(root):
    if root is None:
        return None
    while root.right:
        root = root.right
    return root.val

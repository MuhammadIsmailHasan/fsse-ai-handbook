class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def is_valid_bst(root):
    def ok(node, low, high):
        if node is None:
            return True
        if (low is not None and node.val <= low) or (high is not None and node.val >= high):
            return False
        return ok(node.left, low, node.val) and ok(node.right, node.val, high)

    return ok(root, None, None)


def kth_smallest(root, k):
    if k < 1:
        raise ValueError("k out of range")
    stack, node = [], root
    while node or stack:
        while node:
            stack.append(node)
            node = node.left
        node = stack.pop()
        k -= 1
        if k == 0:
            return node.val
        node = node.right
    raise ValueError("k out of range")

from collections import deque


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def preorder(root):
    if root is None:
        return []
    return [root.val] + preorder(root.left) + preorder(root.right)


def inorder(root):
    out, stack, node = [], [], root
    while node or stack:
        while node:
            stack.append(node)
            node = node.left
        node = stack.pop()
        out.append(node.val)
        node = node.right
    return out


def postorder(root):
    if root is None:
        return []
    return postorder(root.left) + postorder(root.right) + [root.val]


def level_order(root):
    if root is None:
        return []
    levels, queue = [], deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        levels.append(level)
    return levels

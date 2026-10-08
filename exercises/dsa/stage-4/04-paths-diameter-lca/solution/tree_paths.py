class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def has_path_sum(root, target):
    if root is None:
        return False
    if root.left is None and root.right is None:
        return root.val == target
    rest = target - root.val
    return has_path_sum(root.left, rest) or has_path_sum(root.right, rest)


def root_to_leaf_paths(root):
    out = []

    def walk(node, path):
        if node is None:
            return
        path.append(node.val)
        if node.left is None and node.right is None:
            out.append(list(path))
        else:
            walk(node.left, path)
            walk(node.right, path)
        path.pop()

    walk(root, [])
    return out


def diameter(root):
    best = 0

    def depth(node):
        nonlocal best
        if node is None:
            return 0
        left, right = depth(node.left), depth(node.right)
        best = max(best, left + right)
        return 1 + max(left, right)

    depth(root)
    return best


def lowest_common_ancestor(root, p, q):
    found = {p: False, q: False}

    def walk(node):
        if node is None:
            return None
        left, right = walk(node.left), walk(node.right)
        if node.val in found:
            found[node.val] = True
        if left is not None and right is not None:
            return node
        if node.val in (p, q):
            return node
        return left if left is not None else right

    result = walk(root)
    if not (found[p] and found[q]):
        return None
    return result.val if result else None

from collections import deque


def build_graph(edges, directed=False):
    sets = {}
    for a, b in edges:
        sets.setdefault(a, set()).add(b)
        sets.setdefault(b, set())
        if not directed:
            sets[b].add(a)
    return {node: sorted(neighbours) for node, neighbours in sets.items()}


def bfs_order(graph, start):
    seen, order, queue = {start}, [], deque([start])
    while queue:
        node = queue.popleft()
        order.append(node)
        for nxt in graph.get(node, []):
            if nxt not in seen:
                seen.add(nxt)
                queue.append(nxt)
    return order


def dfs_order(graph, start):
    seen, order, stack = set(), [], [start]
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        order.append(node)
        for nxt in reversed(graph.get(node, [])):
            if nxt not in seen:
                stack.append(nxt)
    return order


def has_path(graph, source, target):
    if source == target:
        return True
    return target in set(bfs_order(graph, source))

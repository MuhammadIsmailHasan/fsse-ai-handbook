from collections import deque


def two_color(n, edges):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    color = [-1] * n
    for start in range(n):
        if color[start] != -1:
            continue
        color[start] = 0
        queue = deque([start])
        while queue:
            node = queue.popleft()
            for nxt in adj[node]:
                if color[nxt] == -1:
                    color[nxt] = 1 - color[node]
                    queue.append(nxt)
                elif color[nxt] == color[node]:
                    return None
    return color


def is_bipartite(n, edges):
    return two_color(n, edges) is not None


def can_split_into_two_teams(n, dislikes):
    return is_bipartite(n, [(a - 1, b - 1) for a, b in dislikes])


def has_odd_cycle(n, edges):
    return not is_bipartite(n, edges)

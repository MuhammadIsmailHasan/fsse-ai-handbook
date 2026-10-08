import heapq


def _kahn(n, edges):
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for a, b in edges:
        adj[a].append(b)
        indeg[b] += 1
    return adj, indeg


def topo_order(n, edges):
    adj, indeg = _kahn(n, edges)
    ready = [i for i in range(n) if indeg[i] == 0]
    heapq.heapify(ready)
    order = []
    while ready:
        node = heapq.heappop(ready)
        order.append(node)
        for nxt in adj[node]:
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                heapq.heappush(ready, nxt)
    return order if len(order) == n else None


def can_finish(num_courses, prerequisites):
    return topo_order(num_courses, [(needs, course) for course, needs in prerequisites]) is not None


def min_semesters(n, edges):
    adj, indeg = _kahn(n, edges)
    current = [i for i in range(n) if indeg[i] == 0]
    done = rounds = 0
    while current:
        rounds += 1
        nxt_round = []
        for node in current:
            done += 1
            for nxt in adj[node]:
                indeg[nxt] -= 1
                if indeg[nxt] == 0:
                    nxt_round.append(nxt)
        current = nxt_round
    return rounds if done == n else -1

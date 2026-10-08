import heapq


def dijkstra(graph, source):
    dist = {}
    heap = [(0, source)]
    while heap:
        cost, node = heapq.heappop(heap)
        if node in dist:
            continue
        dist[node] = cost
        for nxt, weight in graph.get(node, []):
            if nxt not in dist:
                heapq.heappush(heap, (cost + weight, nxt))
    return dist


def cheapest_route(graph, start, goal):
    best = {}
    parent = {start: None}
    heap = [(0, start, None)]
    while heap:
        cost, node, prev = heapq.heappop(heap)
        if node in best:
            continue
        best[node] = cost
        parent[node] = prev
        if node == goal:
            path = []
            while node is not None:
                path.append(node)
                node = parent[node]
            return cost, path[::-1]
        for nxt, weight in graph.get(node, []):
            if nxt not in best:
                heapq.heappush(heap, (cost + weight, nxt, node))
    return None


def network_delay_time(times, n, k):
    graph = {}
    for u, v, w in times:
        graph.setdefault(u, []).append((v, w))
    dist = dijkstra(graph, k)
    return max(dist.values()) if len(dist) == n else -1

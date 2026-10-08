import random
import time

from weighted_paths import cheapest_route, dijkstra, network_delay_time

# A=0, B=1, C=2, D=3:  A→B 4, A→C 1, C→B 2, C→D 7, B→D 1
GRAPH = {0: [(1, 4), (2, 1)], 1: [(3, 1)], 2: [(1, 2), (3, 7)], 3: []}


def bellman_ford(graph, source):
    nodes = set(graph) | {v for edges in graph.values() for v, _ in edges}
    INF = float("inf")
    dist = {v: INF for v in nodes}
    dist[source] = 0
    for _ in range(len(nodes)):
        for u, edges in graph.items():
            for v, w in edges:
                if dist[u] + w < dist[v]:
                    dist[v] = dist[u] + w
    return {v: d for v, d in dist.items() if d < INF}


def test_dijkstra_example():
    assert dijkstra(GRAPH, 0) == {0: 0, 2: 1, 1: 3, 3: 4}


def test_a_longer_path_can_be_cheaper():
    # 0 -> 1 directly costs 4, but 0 -> 2 -> 1 costs 3
    assert dijkstra(GRAPH, 0)[1] == 3


def test_unreachable_nodes_are_missing_and_direction_matters():
    assert 0 not in dijkstra(GRAPH, 3)
    assert dijkstra(GRAPH, 3) == {3: 0}


def test_zero_weight_edges():
    graph = {0: [(1, 0)], 1: [(2, 0)], 2: []}
    assert dijkstra(graph, 0) == {0: 0, 1: 0, 2: 0}


def test_random_graphs_match_bellman_ford():
    rng = random.Random(171)
    for _ in range(200):
        n = rng.randint(1, 9)
        graph = {i: [] for i in range(n)}
        for _ in range(rng.randint(0, 20)):
            graph[rng.randrange(n)].append((rng.randrange(n), rng.randint(0, 9)))
        source = rng.randrange(n)
        assert dijkstra(graph, source) == bellman_ford(graph, source)


def test_cheapest_route():
    assert cheapest_route(GRAPH, 0, 3) == (4, [0, 2, 1, 3])
    assert cheapest_route(GRAPH, 0, 0) == (0, [0])
    assert cheapest_route(GRAPH, 3, 0) is None
    assert cheapest_route(GRAPH, 0, 99) is None


def test_cheapest_route_is_a_real_route_with_the_right_cost():
    rng = random.Random(172)
    for _ in range(200):
        n = rng.randint(2, 9)
        graph = {i: [] for i in range(n)}
        for _ in range(rng.randint(1, 20)):
            graph[rng.randrange(n)].append((rng.randrange(n), rng.randint(0, 9)))
        a, b = rng.randrange(n), rng.randrange(n)
        expected = bellman_ford(graph, a).get(b)
        result = cheapest_route(graph, a, b)
        if expected is None:
            assert result is None
            continue
        cost, path = result
        assert cost == expected and path[0] == a and path[-1] == b
        total = 0
        for u, v in zip(path, path[1:]):
            total += min(w for x, w in graph[u] if x == v)
        assert total == cost


def test_network_delay_time():
    assert network_delay_time([(2, 1, 1), (2, 3, 1), (3, 4, 1)], 4, 2) == 2
    assert network_delay_time([(1, 2, 1)], 2, 1) == 1
    assert network_delay_time([(1, 2, 1)], 2, 2) == -1
    assert network_delay_time([], 1, 1) == 0


def test_a_big_graph_is_fast():
    rng = random.Random(173)
    n = 50_000
    graph = {i: [(rng.randrange(n), rng.randint(1, 20)) for _ in range(5)] + [(i + 1, 50)] for i in range(n - 1)}
    graph[n - 1] = []
    started = time.perf_counter()
    dist = dijkstra(graph, 0)
    assert len(dist) == n
    assert time.perf_counter() - started < 4.0

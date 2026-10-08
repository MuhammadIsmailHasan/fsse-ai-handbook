import random
import time

from graph_traversal import bfs_order, build_graph, dfs_order, has_path

EDGES = [(1, 2), (1, 3), (2, 4), (3, 4), (4, 5)]


def test_build_undirected_graph():
    assert build_graph(EDGES) == {1: [2, 3], 2: [1, 4], 3: [1, 4], 4: [2, 3, 5], 5: [4]}


def test_build_directed_graph_keeps_sink_nodes_as_keys():
    graph = build_graph(EDGES, directed=True)
    assert graph == {1: [2, 3], 2: [4], 3: [4], 4: [5], 5: []}


def test_duplicate_edges_count_once_and_neighbours_are_sorted():
    assert build_graph([(1, 3), (1, 2), (1, 3), (3, 1)]) == {1: [2, 3], 2: [1], 3: [1]}
    assert build_graph([]) == {}


def test_bfs_visits_nearest_first():
    graph = build_graph(EDGES)
    assert bfs_order(graph, 1) == [1, 2, 3, 4, 5]


def test_dfs_goes_deep_first():
    graph = build_graph(EDGES)
    assert dfs_order(graph, 1) == [1, 2, 4, 3, 5]


def test_cycles_do_not_loop_forever():
    graph = build_graph([(1, 2), (2, 3), (3, 1)])
    assert sorted(bfs_order(graph, 1)) == [1, 2, 3]
    assert sorted(dfs_order(graph, 1)) == [1, 2, 3]


def test_only_the_reachable_part_is_visited():
    graph = build_graph([(1, 2), (3, 4)])
    assert bfs_order(graph, 1) == [1, 2]
    assert dfs_order(graph, 3) == [3, 4]


def test_directed_edges_are_followed_one_way():
    graph = build_graph([(1, 2), (2, 3)], directed=True)
    assert bfs_order(graph, 1) == [1, 2, 3]
    assert bfs_order(graph, 3) == [3]


def test_start_node_alone():
    assert bfs_order({7: []}, 7) == [7]
    assert dfs_order({7: []}, 7) == [7]


def test_has_path():
    graph = build_graph([(1, 2), (2, 3), (4, 5)])
    assert has_path(graph, 1, 3)
    assert has_path(graph, 3, 1)
    assert not has_path(graph, 1, 5)
    assert has_path(graph, 4, 4)
    assert not has_path(graph, 1, 99)


def test_has_path_respects_direction():
    graph = build_graph([(1, 2), (2, 3)], directed=True)
    assert has_path(graph, 1, 3)
    assert not has_path(graph, 3, 1)


def test_bfs_and_dfs_reach_the_same_nodes():
    rng = random.Random(101)
    for _ in range(200):
        n = rng.randint(1, 15)
        edges = [(rng.randint(0, n), rng.randint(0, n)) for _ in range(rng.randint(0, 25))]
        graph = build_graph(edges)
        if not graph:
            continue
        start = rng.choice(list(graph))
        assert sorted(bfs_order(graph, start)) == sorted(dfs_order(graph, start))
        assert len(set(bfs_order(graph, start))) == len(bfs_order(graph, start))


def test_dfs_survives_a_very_long_path():
    n = 50_000
    graph = {i: [i + 1] if i < n - 1 else [] for i in range(n)}
    started = time.perf_counter()
    assert dfs_order(graph, 0) == list(range(n))
    assert time.perf_counter() - started < 2.0


def test_bfs_on_a_big_graph_is_fast():
    n = 100_000
    graph = {i: [j for j in (2 * i + 1, 2 * i + 2) if j < n] for i in range(n)}
    started = time.perf_counter()
    assert bfs_order(graph, 0) == list(range(n))
    assert time.perf_counter() - started < 2.0

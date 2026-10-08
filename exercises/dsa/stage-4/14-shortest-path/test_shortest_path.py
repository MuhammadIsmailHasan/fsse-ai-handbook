import itertools
import random
import time

from shortest_path import distances_from, shortest_path, shortest_path_length, word_ladder_length


def undirected(edges):
    graph = {}
    for a, b in edges:
        graph.setdefault(a, []).append(b)
        graph.setdefault(b, []).append(a)
    return graph


GRAPH = undirected([(1, 2), (2, 3), (3, 4), (1, 5), (5, 4), (6, 7)])


def test_distances_from():
    assert distances_from(GRAPH, 1) == {1: 0, 2: 1, 5: 1, 3: 2, 4: 2}


def test_distances_leave_out_unreachable_nodes():
    assert 6 not in distances_from(GRAPH, 1)
    assert distances_from({9: []}, 9) == {9: 0}


def test_shortest_path_length():
    assert shortest_path_length(GRAPH, 1, 4) == 2
    assert shortest_path_length(GRAPH, 1, 1) == 0
    assert shortest_path_length(GRAPH, 1, 7) == -1
    assert shortest_path_length(GRAPH, 1, 99) == -1


def valid_path(graph, path, start, goal):
    return path[0] == start and path[-1] == goal and all(b in graph[a] for a, b in zip(path, path[1:]))


def test_shortest_path_is_a_real_shortest_path():
    path = shortest_path(GRAPH, 1, 4)
    assert valid_path(GRAPH, path, 1, 4)
    assert len(path) - 1 == 2


def test_shortest_path_edge_cases():
    assert shortest_path(GRAPH, 1, 1) == [1]
    assert shortest_path(GRAPH, 1, 7) is None
    assert shortest_path(GRAPH, 1, 99) is None


def test_directed_graph():
    graph = {1: [2], 2: [3], 3: [], 4: [1]}
    assert shortest_path_length(graph, 1, 3) == 2
    assert shortest_path_length(graph, 3, 1) == -1
    assert shortest_path(graph, 4, 3) == [4, 1, 2, 3]


def test_random_graphs_against_brute_force():
    rng = random.Random(111)
    for _ in range(150):
        n = rng.randint(2, 9)
        edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randint(0, 14))]
        graph = undirected(edges)
        for node in range(n):
            graph.setdefault(node, [])
        a, b = rng.randrange(n), rng.randrange(n)
        best = None
        for k in range(0, n):
            for middle in itertools.permutations([x for x in range(n) if x not in (a, b)], k):
                path = (a, *middle, b) if a != b else (a,)
                if all(y in graph[x] for x, y in zip(path, path[1:])):
                    best = len(path) - 1
                    break
            if best is not None:
                break
        assert shortest_path_length(graph, a, b) == (best if best is not None else -1)
        p = shortest_path(graph, a, b)
        assert (p is None) == (best is None)
        if p:
            assert valid_path(graph, p, a, b) and len(p) - 1 == best


def test_word_ladder_examples():
    words = ["hot", "dot", "dog", "lot", "log", "cog"]
    assert word_ladder_length("hit", "cog", words) == 5
    assert word_ladder_length("hit", "cog", ["hot", "dot", "dog", "lot", "log"]) == 0
    assert word_ladder_length("a", "c", ["a", "b", "c"]) == 2
    assert word_ladder_length("hot", "hot", ["hot"]) == 1


def test_word_ladder_big_input_needs_the_neighbour_trick():
    rng = random.Random(112)
    words = ["".join(rng.choice("abcdef") for _ in range(6)) for _ in range(5_000)]
    begin, end = words[0], words[1]
    started = time.perf_counter()
    result = word_ladder_length(begin, end, words)
    assert result >= 0
    assert time.perf_counter() - started < 2.0

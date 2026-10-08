import itertools
import random
import time

from bipartite import can_split_into_two_teams, has_odd_cycle, is_bipartite, two_color


def valid_colouring(n, edges, colors):
    return colors is not None and len(colors) == n and set(colors) <= {0, 1} and all(colors[a] != colors[b] for a, b in edges)


def test_even_cycle_is_bipartite():
    edges = [(0, 1), (1, 2), (2, 3), (3, 0)]
    assert two_color(4, edges) == [0, 1, 0, 1]
    assert is_bipartite(4, edges)


def test_odd_cycle_is_not():
    edges = [(0, 1), (1, 2), (2, 0)]
    assert two_color(3, edges) is None
    assert not is_bipartite(3, edges)
    assert has_odd_cycle(3, edges)


def test_smallest_node_of_each_group_is_colour_0():
    assert two_color(5, [(1, 2), (3, 4)]) == [0, 0, 1, 0, 1]
    assert two_color(3, []) == [0, 0, 0]
    assert two_color(0, []) == []


def test_self_loop_is_impossible():
    assert two_color(2, [(1, 1)]) is None
    assert has_odd_cycle(2, [(1, 1)])


def test_a_tree_is_always_bipartite():
    edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 5)]
    colors = two_color(6, edges)
    assert valid_colouring(6, edges, colors)


def test_the_odd_cycle_can_hide_in_a_later_group():
    edges = [(0, 1), (2, 3), (3, 4), (4, 2)]
    assert two_color(5, edges) is None


def test_teams_example():
    assert can_split_into_two_teams(4, [(1, 2), (1, 3), (2, 4)])
    assert not can_split_into_two_teams(3, [(1, 2), (1, 3), (2, 3)])
    assert can_split_into_two_teams(5, [])
    assert not can_split_into_two_teams(5, [(1, 2), (2, 3), (3, 4), (4, 5), (1, 5)])   # 5-cycle


def test_random_graphs_against_brute_force():
    rng = random.Random(161)
    for _ in range(300):
        n = rng.randint(1, 8)
        edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randint(0, 10))]
        brute = any(
            all(bits[a] != bits[b] for a, b in edges) for bits in itertools.product([0, 1], repeat=n)
        )
        colors = two_color(n, edges)
        assert (colors is not None) == brute
        assert is_bipartite(n, edges) == brute
        assert has_odd_cycle(n, edges) == (not brute)
        if colors is not None:
            assert valid_colouring(n, edges, colors)


def test_big_graph_is_fast():
    n = 200_000
    edges = [(i, i + 1) for i in range(n - 1)]
    started = time.perf_counter()
    colors = two_color(n, edges)
    assert colors[:4] == [0, 1, 0, 1] and colors[-1] == (n - 1) % 2
    assert time.perf_counter() - started < 3.0
    assert two_color(n, edges + [(0, 2)]) is None      # a triangle 0-1-2 appears

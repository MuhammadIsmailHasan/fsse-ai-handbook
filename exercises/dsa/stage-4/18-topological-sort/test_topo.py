import random
import time

from topo import can_finish, min_semesters, topo_order


def is_valid_order(n, edges, order):
    if order is None or sorted(order) != list(range(n)):
        return False
    pos = {node: i for i, node in enumerate(order)}
    return all(pos[a] < pos[b] for a, b in edges)


def test_simple_order_with_smallest_first_ties():
    assert topo_order(4, [(0, 1), (0, 2), (1, 3), (2, 3)]) == [0, 1, 2, 3]
    assert topo_order(3, [(2, 1), (1, 0)]) == [2, 1, 0]
    assert topo_order(3, []) == [0, 1, 2]


def test_ties_take_the_smallest_ready_node():
    # 3 and 1 are both ready at the start; 1 goes first. After 1, node 0 is unlocked.
    assert topo_order(5, [(1, 0), (3, 4)]) == [1, 0, 2, 3, 4]


def test_cycle_means_no_order():
    assert topo_order(3, [(0, 1), (1, 2), (2, 0)]) is None
    assert topo_order(2, [(0, 0)]) is None
    assert topo_order(4, [(0, 1), (2, 3), (3, 2)]) is None


def test_empty():
    assert topo_order(0, []) == []


def test_random_dags_give_valid_orders():
    rng = random.Random(151)
    for _ in range(200):
        n = rng.randint(1, 12)
        perm = list(range(n))
        rng.shuffle(perm)
        edges = []
        for _ in range(rng.randint(0, 20)):
            i, j = sorted(rng.sample(range(n), 2)) if n > 1 else (0, 0)
            if i != j:
                edges.append((perm[i], perm[j]))
        order = topo_order(n, edges)
        assert is_valid_order(n, edges, order)


def test_can_finish():
    assert can_finish(2, [(1, 0)])
    assert not can_finish(2, [(1, 0), (0, 1)])
    assert can_finish(4, [(1, 0), (2, 0), (3, 1), (3, 2)])
    assert can_finish(3, [])
    assert not can_finish(3, [(0, 1), (1, 2), (2, 0)])


def test_min_semesters():
    assert min_semesters(0, []) == 0
    assert min_semesters(3, []) == 1
    assert min_semesters(4, [(0, 1), (0, 2), (1, 3), (2, 3)]) == 3
    assert min_semesters(4, [(0, 1), (1, 2), (2, 3)]) == 4
    assert min_semesters(3, [(0, 1), (1, 2), (2, 0)]) == -1


def test_min_semesters_equals_the_longest_chain():
    rng = random.Random(152)
    for _ in range(200):
        n = rng.randint(1, 10)
        edges = []
        for _ in range(rng.randint(0, 15)):
            a, b = rng.sample(range(n), 2) if n > 1 else (0, 0)
            if a < b:
                edges.append((a, b))
        longest = [1] * n
        for a in range(n):
            for x, y in edges:
                if x == a:
                    longest[y] = max(longest[y], longest[x] + 1)
        assert min_semesters(n, edges) == max(longest)


def test_long_chain_needs_no_recursion():
    n = 100_000
    edges = [(i, i + 1) for i in range(n - 1)]
    started = time.perf_counter()
    assert topo_order(n, edges) == list(range(n))
    assert min_semesters(n, edges) == n
    assert time.perf_counter() - started < 3.0

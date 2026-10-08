import random
import time

from components import UnionFind, count_components, has_cycle, is_valid_tree


def test_union_find_basics():
    uf = UnionFind(5)
    assert uf.count == 5
    assert uf.union(0, 1) is True
    assert uf.union(1, 2) is True
    assert uf.union(0, 2) is False          # already together
    assert uf.count == 3
    assert uf.find(0) == uf.find(2)
    assert uf.find(0) != uf.find(3)


def test_union_find_chain_of_200k_is_fast_and_iterative():
    n = 200_000
    uf = UnionFind(n)
    started = time.perf_counter()
    for i in range(n - 1):
        uf.union(i, i + 1)
    assert uf.count == 1
    assert len({uf.find(i) for i in range(0, n, 997)}) == 1
    assert time.perf_counter() - started < 3.0


def test_union_find_chain_unions_in_the_worst_order():
    n = 100_000
    uf = UnionFind(n)
    for i in range(n - 1, 0, -1):
        uf.union(i, i - 1)
    assert uf.count == 1
    assert uf.find(0) == uf.find(n - 1)


def test_count_components():
    assert count_components(5, [(0, 1), (1, 2), (3, 4)]) == 2
    assert count_components(4, []) == 4
    assert count_components(0, []) == 0
    assert count_components(3, [(0, 1), (1, 2), (2, 0)]) == 1


def brute_components(n, edges):
    adj = {i: set() for i in range(n)}
    for a, b in edges:
        adj[a].add(b)
        adj[b].add(a)
    seen, groups = set(), 0
    for i in range(n):
        if i not in seen:
            groups += 1
            stack = [i]
            seen.add(i)
            while stack:
                for m in adj[stack.pop()]:
                    if m not in seen:
                        seen.add(m)
                        stack.append(m)
    return groups


def test_components_match_brute_force():
    rng = random.Random(141)
    for _ in range(300):
        n = rng.randint(0, 12)
        edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randint(0, 12))] if n else []
        assert count_components(n, edges) == brute_components(n, edges)


def test_has_cycle():
    assert not has_cycle(4, [(0, 1), (1, 2), (2, 3)])
    assert has_cycle(3, [(0, 1), (1, 2), (2, 0)])
    assert not has_cycle(5, [])
    assert has_cycle(2, [(0, 1), (1, 0)])        # the same road twice
    assert has_cycle(3, [(1, 1)])                # a road from a place to itself


def test_has_cycle_in_a_separate_component():
    assert has_cycle(6, [(0, 1), (2, 3), (3, 4), (4, 2)])


def test_has_cycle_matches_edge_count_rule():
    rng = random.Random(142)
    for _ in range(300):
        n = rng.randint(1, 10)
        edges = [(rng.randrange(n), rng.randrange(n)) for _ in range(rng.randint(0, 10))]
        # forest  <=>  edges == n - components
        forest = len(edges) == n - brute_components(n, edges)
        assert has_cycle(n, edges) == (not forest)


def test_is_valid_tree():
    assert is_valid_tree(5, [(0, 1), (0, 2), (0, 3), (1, 4)])
    assert not is_valid_tree(5, [(0, 1), (1, 2), (2, 3), (1, 3)])    # has a cycle
    assert not is_valid_tree(4, [(0, 1), (2, 3)])                    # not connected
    assert is_valid_tree(1, [])
    assert not is_valid_tree(0, [])
    assert not is_valid_tree(2, [])
    assert not is_valid_tree(3, [(0, 1), (1, 0)])

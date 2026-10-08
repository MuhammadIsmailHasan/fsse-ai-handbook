import itertools
import random
import time

from merge_sorted import merge_k_sorted, merge_streams, smallest_pair_sums


def test_merge_k_sorted_example():
    assert merge_k_sorted([[1, 4, 5], [1, 3, 4], [2, 6]]) == [1, 1, 2, 3, 4, 4, 5, 6]


def test_merge_k_sorted_edges():
    assert merge_k_sorted([]) == []
    assert merge_k_sorted([[]]) == []
    assert merge_k_sorted([[], [1], []]) == [1]
    assert merge_k_sorted([[2, 2], [2]]) == [2, 2, 2]
    assert merge_k_sorted([[-3, 0], [-5, 5]]) == [-5, -3, 0, 5]


def test_merge_k_sorted_does_not_change_the_input():
    lists = [[1, 3], [2]]
    merge_k_sorted(lists)
    assert lists == [[1, 3], [2]]


def test_merge_k_sorted_matches_sorted():
    rng = random.Random(81)
    for _ in range(200):
        lists = [sorted(rng.randint(-20, 20) for _ in range(rng.randint(0, 8))) for _ in range(rng.randint(0, 7))]
        assert merge_k_sorted(lists) == sorted(x for lst in lists for x in lst)


def test_merge_k_sorted_many_lists_is_fast():
    rng = random.Random(82)
    lists = [sorted(rng.randint(0, 10**6) for _ in range(200)) for _ in range(1000)]
    started = time.perf_counter()
    result = merge_k_sorted(lists)
    assert result == sorted(x for lst in lists for x in lst)
    assert time.perf_counter() - started < 2.0


def test_merge_streams_works_on_finite_inputs():
    assert list(merge_streams([[1, 4], iter([2, 3]), (0, 9)])) == [0, 1, 2, 3, 4, 9]
    assert list(merge_streams([])) == []
    assert list(merge_streams([[], []])) == []


def test_merge_streams_is_lazy_and_handles_infinite_streams():
    evens = itertools.count(0, 2)
    odds = itertools.count(1, 2)
    merged = merge_streams([evens, odds])
    assert list(itertools.islice(merged, 10)) == list(range(10))


def test_merge_streams_reads_only_what_it_needs():
    pulled = []

    def stream(name, values):
        for v in values:
            pulled.append((name, v))
            yield v

    merged = merge_streams([stream("a", [1, 5, 9]), stream("b", [2, 3, 4])])
    assert next(merged) == 1
    # one read per stream to start, nothing more
    assert len(pulled) <= 2
    assert next(merged) == 2
    assert len(pulled) <= 4


def test_smallest_pair_sums_examples():
    assert smallest_pair_sums([1, 7, 11], [2, 4, 6], 3) == [3, 5, 7]
    assert smallest_pair_sums([1, 1, 2], [1, 2, 3], 4) == [2, 2, 3, 3]
    assert smallest_pair_sums([1], [1, 2, 3], 5) == [2, 3, 4]
    assert smallest_pair_sums([], [1], 3) == []
    assert smallest_pair_sums([1], [1], 0) == []


def test_smallest_pair_sums_matches_brute_force():
    rng = random.Random(83)
    for _ in range(200):
        a = sorted(rng.randint(0, 20) for _ in range(rng.randint(0, 8)))
        b = sorted(rng.randint(0, 20) for _ in range(rng.randint(0, 8)))
        k = rng.randint(0, 12)
        assert smallest_pair_sums(a, b, k) == sorted(x + y for x in a for y in b)[:k]


def test_smallest_pair_sums_on_large_lists():
    a = list(range(20_000))
    b = list(range(0, 40_000, 2))
    started = time.perf_counter()
    assert smallest_pair_sums(a, b, 5) == [0, 1, 2, 2, 3]
    assert time.perf_counter() - started < 1.0

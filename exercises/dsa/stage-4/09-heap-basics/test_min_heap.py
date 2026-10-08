import random
import time

import pytest

from min_heap import MinHeap, heap_sort


def is_heap(items):
    return all(items[(i - 1) // 2] <= items[i] for i in range(1, len(items)))


def test_empty_heap():
    heap = MinHeap()
    assert len(heap) == 0
    with pytest.raises(IndexError):
        heap.peek()
    with pytest.raises(IndexError):
        heap.pop()


def test_push_and_peek_track_the_minimum():
    heap = MinHeap()
    for v, smallest in [(5, 5), (3, 3), (8, 3), (1, 1), (4, 1)]:
        heap.push(v)
        assert heap.peek() == smallest
    assert len(heap) == 5


def test_pop_returns_ascending_order():
    heap = MinHeap()
    for v in [5, 3, 8, 1, 4, 1, 9]:
        heap.push(v)
    assert [heap.pop() for _ in range(7)] == [1, 1, 3, 4, 5, 8, 9]
    assert len(heap) == 0


def test_the_list_always_satisfies_the_heap_rule():
    rng = random.Random(61)
    heap = MinHeap()
    for _ in range(500):
        if heap.items and rng.random() < 0.4:
            heap.pop()
        else:
            heap.push(rng.randint(-50, 50))
        assert is_heap(heap.items)


def test_push_is_stored_in_a_list_the_size_of_the_heap():
    heap = MinHeap()
    for v in range(10, 0, -1):
        heap.push(v)
    assert len(heap.items) == len(heap) == 10
    assert heap.items[0] == 1


def test_pop_with_a_single_item():
    heap = MinHeap()
    heap.push(7)
    assert heap.pop() == 7
    assert len(heap) == 0
    heap.push(2)
    assert heap.peek() == 2


def test_heap_sort_matches_sorted():
    rng = random.Random(62)
    for _ in range(200):
        values = [rng.randint(-100, 100) for _ in range(rng.randint(0, 40))]
        assert heap_sort(values) == sorted(values)
    assert heap_sort([]) == []


def test_heap_sort_does_not_change_the_input():
    values = [3, 1, 2]
    heap_sort(values)
    assert values == [3, 1, 2]


def test_heap_is_fast_for_many_items():
    rng = random.Random(63)
    values = [rng.randint(0, 10**9) for _ in range(100_000)]
    started = time.perf_counter()
    assert heap_sort(values) == sorted(values)
    assert time.perf_counter() - started < 3.0


def test_does_not_use_heapq():
    import inspect

    import min_heap

    assert "heapq" not in inspect.getsource(min_heap)

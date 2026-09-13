import ast
import random
import time
import tracemalloc
from pathlib import Path

import pytest

from two_pointer_basics import is_clean_palindrome, merge_sorted_lists, pair_indices


@pytest.mark.parametrize(
    ("text", "expected"),
    [("Kasur ini rusak!", True), ("A man, a plan, a canal: Panama", True), ("race a car", False), ("", True), (".,!", True), ("0P", False), ("ab1ba", True)],
)
def test_is_clean_palindrome(text, expected):
    assert is_clean_palindrome(text) is expected


def test_palindrome_random():
    rng = random.Random(31)
    for _ in range(500):
        text = "".join(rng.choice("aAb1 ,!") for _ in range(rng.randint(0, 10)))
        cleaned = [c.lower() for c in text if c.isalnum()]
        assert is_clean_palindrome(text) is (cleaned == cleaned[::-1])


def test_palindrome_does_not_copy_the_text():
    text = "ab" * 500_000 + "!" + "ba" * 500_000
    tracemalloc.start()
    try:
        assert is_clean_palindrome(text) is True
        _, peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    assert peak < 200_000, f"peak {peak} bytes — don't build a cleaned copy or reversed string"


def brute_pair(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return i, j
    return None


@pytest.mark.parametrize(("nums", "target", "expected"), [([1, 3, 4, 6, 9], 10, (0, 4)), ([1, 3, 4, 6, 9], 7, (0, 3)), ([2, 5], 8, None), ([], 1, None), ([5], 10, None)])
def test_pair_indices_examples(nums, target, expected):
    assert pair_indices(nums, target) == expected


def test_pair_indices_smallest_left_index():
    rng = random.Random(32)
    for _ in range(500):
        nums = sorted(rng.randint(-10, 10) for _ in range(rng.randint(0, 10)))
        target = rng.randint(-15, 15)
        found = pair_indices(nums, target)
        expected = brute_pair(nums, target)
        if expected is None:
            assert found is None
        else:
            assert found is not None and nums[found[0]] + nums[found[1]] == target and found[0] < found[1]
            assert found[0] == expected[0], "return the pair with the smallest left index"


def test_pair_indices_linear():
    nums = list(range(0, 400_000, 2))
    started = time.perf_counter()
    assert pair_indices(nums, 1) is None
    assert time.perf_counter() - started < 0.5


def test_merge():
    rng = random.Random(33)
    for _ in range(300):
        a = sorted(rng.randint(0, 9) for _ in range(rng.randint(0, 8)))
        b = sorted(rng.randint(0, 9) for _ in range(rng.randint(0, 8)))
        assert merge_sorted_lists(a, b) == sorted(a + b)


def test_merge_does_not_sort():
    tree = ast.parse((Path(__file__).parent / "two_pointer_basics.py").read_text())
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "merge_sorted_lists")
    names = {n.id for n in ast.walk(function) if isinstance(n, ast.Name)} | {n.attr for n in ast.walk(function) if isinstance(n, ast.Attribute)}
    assert not names & {"sorted", "sort", "heapq", "merge"}

import ast
import bisect
import math
import random
from pathlib import Path

import pytest

import search_basics
from search_basics import find_index, first_at_least, integer_sqrt


class CountingList(list):
    reads = 0

    def __getitem__(self, index):
        CountingList.reads += 1
        return super().__getitem__(index)


def test_find_index():
    assert find_index([2, 5, 8, 12, 16], 12) == 3
    assert find_index([2, 5, 8, 12, 16], 7) == -1
    assert find_index([], 1) == -1
    rng = random.Random(61)
    for _ in range(400):
        nums = sorted(rng.randint(0, 20) for _ in range(rng.randint(0, 15)))
        target = rng.randint(-1, 21)
        found = find_index(nums, target)
        assert (found == -1) if target not in nums else nums[found] == target


def test_find_index_is_logarithmic():
    nums = CountingList(range(1_000_000))
    CountingList.reads = 0
    assert find_index(nums, 765_432) == 765_432
    assert CountingList.reads <= 3 * 21, f"{CountingList.reads} reads — binary search needs about log2(n) ≈ 20"


@pytest.mark.parametrize(("nums", "x", "expected"), [([10, 20, 20, 30], 20, 1), ([10, 20, 20, 30], 25, 3), ([10, 20], 5, 0), ([10, 20], 99, 2), ([], 3, 0)])
def test_first_at_least(nums, x, expected):
    assert first_at_least(nums, x) == expected


def test_first_at_least_matches_bisect():
    rng = random.Random(62)
    for _ in range(500):
        nums = sorted(rng.randint(0, 10) for _ in range(rng.randint(0, 12)))
        x = rng.randint(-1, 11)
        assert first_at_least(nums, x) == bisect.bisect_left(nums, x)
    big = CountingList(range(0, 2_000_000, 2))
    CountingList.reads = 0
    assert first_at_least(big, 1_000_001) == 500_001
    assert CountingList.reads <= 3 * 21


def test_integer_sqrt():
    for n in list(range(0, 2_000)) + [10**12, 10**12 - 1, 2**62 + 12345]:
        assert integer_sqrt(n) == math.isqrt(n), n


def test_no_shortcuts():
    tree = ast.parse(Path(search_basics.__file__).read_text())
    imported = {alias.name for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)) for alias in node.names}
    imported |= {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom) and node.module}
    assert not imported & {"bisect", "math", "isqrt", "sqrt", "bisect_left"}, "implement it yourself — no bisect or math"
    attributes = {node.attr for node in ast.walk(tree) if isinstance(node, ast.Attribute)}
    assert not attributes & {"isqrt", "sqrt", "bisect_left", "bisect_right"}
    for node in ast.walk(tree):
        if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Pow) and isinstance(node.right, ast.Constant) and isinstance(node.right.value, float):
            raise AssertionError("no ** 0.5 — binary search the answer")

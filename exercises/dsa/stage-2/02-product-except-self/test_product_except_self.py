import ast
import math
import random
import time
from pathlib import Path

import pytest

from product_except_self import product_except_self


@pytest.mark.parametrize(
    ("nums", "expected"),
    [([2, 3, 4, 5], [60, 40, 30, 24]), ([1, 0, 3], [0, 3, 0]), ([0, 0, 4], [0, 0, 0]), ([-1, 2], [2, -1]), ([5, 7], [7, 5])],
)
def test_examples(nums, expected):
    assert product_except_self(nums) == expected


def test_matches_brute_force():
    rng = random.Random(11)
    for _ in range(300):
        nums = [rng.randint(-4, 4) for _ in range(rng.randint(2, 9))]
        expected = [math.prod(nums[:i] + nums[i + 1 :]) for i in range(len(nums))]
        assert product_except_self(nums) == expected


def test_no_division():
    tree = ast.parse((Path(__file__).parent / "product_except_self.py").read_text())
    assert not any(isinstance(node, (ast.Div, ast.FloorDiv)) for node in ast.walk(tree)), "solve it without division"


def test_is_linear():
    nums = [1, -1] * 50_000
    started = time.perf_counter()
    product_except_self(nums)
    assert time.perf_counter() - started < 0.5, "Too slow — is this O(n²)?"

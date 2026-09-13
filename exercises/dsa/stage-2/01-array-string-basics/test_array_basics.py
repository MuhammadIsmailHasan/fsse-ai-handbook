import random
import time

import pytest

from array_basics import compress, move_zeros, rotate_right


@pytest.mark.parametrize(
    ("nums", "k", "expected"),
    [([1, 2, 3, 4, 5], 2, [4, 5, 1, 2, 3]), ([1, 2, 3], 0, [1, 2, 3]), ([1, 2, 3], 3, [1, 2, 3]), ([1, 2, 3], 7, [3, 1, 2]), ([], 4, []), ([9], 1, [9])],
)
def test_rotate_right(nums, k, expected):
    original = nums[:]
    assert rotate_right(nums, k) == expected
    assert nums == original, "return a new list — don't modify the input"


def test_rotate_right_matches_brute_force():
    rng = random.Random(7)
    for _ in range(200):
        nums = [rng.randint(-9, 9) for _ in range(rng.randint(1, 12))]
        k = rng.randint(0, 30)
        expected = nums[:]
        for _ in range(k):
            expected = [expected[-1]] + expected[:-1]
        assert rotate_right(nums, k) == expected


def test_rotate_right_huge_k_is_fast():
    nums = list(range(100_000))
    started = time.perf_counter()
    assert rotate_right(nums, 10**12 + 1)[0] == 99_999
    assert time.perf_counter() - started < 0.5, "use k % len(nums)"


@pytest.mark.parametrize(
    ("nums", "expected"),
    [([0, 3, 0, 1, 2], [3, 1, 2, 0, 0]), ([0, 0], [0, 0]), ([1, 2], [1, 2]), ([], []), ([0, -1, 0, 0, 5], [-1, 5, 0, 0, 0])],
)
def test_move_zeros_in_place(nums, expected):
    same_list = nums
    assert move_zeros(nums) is None
    assert same_list == expected and same_list is nums


def test_move_zeros_is_linear():
    nums = [0, 1] * 100_000
    started = time.perf_counter()
    move_zeros(nums)
    assert time.perf_counter() - started < 0.5, "Too slow — avoid remove()/insert() inside the loop (each is O(n))"
    assert nums[:3] == [1, 1, 1] and nums[-1] == 0


@pytest.mark.parametrize(
    ("text", "expected"),
    [("aaabccdddd", "a3bc2d4"), ("", ""), ("a", "a"), ("abc", "abc"), ("zzzzzzzzzzzz", "z12"), ("aabbaa", "a2b2a2")],
)
def test_compress(text, expected):
    assert compress(text) == expected


def test_compress_is_linear():
    text = "ab" * 200_000
    started = time.perf_counter()
    assert compress(text) == text
    assert time.perf_counter() - started < 1.0

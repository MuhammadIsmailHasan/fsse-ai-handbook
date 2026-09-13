import time

import pytest

from pair_sum import has_pair_with_sum


@pytest.mark.parametrize(
    ("nums", "target", "expected"),
    [
        ([3, 9, 4, 7], 11, True),
        ([3, 9, 4, 7], 8, False),
        ([5], 10, False),
        ([5, 5], 10, True),
        ([], 0, False),
        ([-3, 8, 1], 5, True),
        ([0, 0], 0, True),
    ],
)
def test_examples(nums, target, expected):
    assert has_pair_with_sum(nums, target) is expected


def test_is_linear_time():
    nums = list(range(0, 40_000, 2))  # 20,000 even numbers
    started = time.perf_counter()
    assert has_pair_with_sum(nums, 3) is False  # odd target: never found → worst case
    assert time.perf_counter() - started < 0.5, "Too slow — is this O(n²)?"

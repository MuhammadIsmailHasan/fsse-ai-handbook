import random

import pytest

from rotated import search_rotated


class CountingList(list):
    reads = 0

    def __getitem__(self, index):
        CountingList.reads += 1
        return super().__getitem__(index)


@pytest.mark.parametrize(("nums", "target", "expected"), [([13, 15, 18, 2, 5, 9, 11], 5, 4), ([13, 15, 18, 2, 5, 9, 11], 14, -1), ([1, 3], 3, 1), ([3, 1], 1, 1), ([], 5, -1), ([7], 7, 0)])
def test_examples(nums, target, expected):
    assert search_rotated(nums, target) == expected


def test_every_rotation_and_target():
    rng = random.Random(63)
    for _ in range(100):
        base = sorted(rng.sample(range(-50, 50), rng.randint(1, 12)))
        k = rng.randrange(len(base))
        nums = base[k:] + base[:k]
        for target in range(-51, 51):
            expected = nums.index(target) if target in nums else -1
            assert search_rotated(nums, target) == expected, (nums, target)


def test_logarithmic():
    base = list(range(1_000_000))
    nums = CountingList(base[400_000:] + base[:400_000])
    CountingList.reads = 0
    assert search_rotated(nums, 123) == 600_123
    assert CountingList.reads <= 6 * 21, f"{CountingList.reads} reads — that's not O(log n)"

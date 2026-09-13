import random

import pytest

from remove_nth import from_list, remove_nth_from_end, to_list


@pytest.mark.parametrize(
    ("values", "n", "expected"),
    [([1, 2, 3, 4, 5], 2, [1, 2, 3, 5]), ([1], 1, []), ([1, 2], 1, [1]), ([1, 2], 2, [2]), ([1, 2, 3], 3, [2, 3])],
)
def test_examples(values, n, expected):
    assert to_list(remove_nth_from_end(from_list(values), n)) == expected


def test_random():
    rng = random.Random(16)
    for _ in range(300):
        values = [rng.randint(0, 9) for _ in range(rng.randint(1, 12))]
        n = rng.randint(1, len(values))
        expected = values[: len(values) - n] + values[len(values) - n + 1 :]
        assert to_list(remove_nth_from_end(from_list(values), n)) == expected


def test_long_list():
    values = list(range(200_000))
    assert to_list(remove_nth_from_end(from_list(values), 100_000))[99_999:100_001] == [99_999, 100_001]

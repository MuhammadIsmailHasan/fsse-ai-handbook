import copy
import random

import pytest

from spiral import spiral_order


@pytest.mark.parametrize(
    ("matrix", "expected"),
    [
        ([[1, 2, 3], [4, 5, 6], [7, 8, 9]], [1, 2, 3, 6, 9, 8, 7, 4, 5]),
        ([[1, 2, 3, 4], [5, 6, 7, 8]], [1, 2, 3, 4, 8, 7, 6, 5]),
        ([[1], [2], [3]], [1, 2, 3]),
        ([[1, 2, 3]], [1, 2, 3]),
        ([], []),
        ([[]], []),
        ([[7]], [7]),
    ],
)
def test_examples(matrix, expected):
    assert spiral_order(matrix) == expected


def peel(matrix):
    """Brute force: take the top row, rotate the rest counter-clockwise, repeat."""
    result = []
    matrix = [row[:] for row in matrix]
    while matrix and matrix[0]:
        result.extend(matrix.pop(0))
        matrix = [list(row) for row in zip(*matrix)][::-1] if matrix and matrix[0] else []
    return result


def test_matches_brute_force_and_keeps_input():
    rng = random.Random(5)
    for _ in range(200):
        rows, cols = rng.randint(1, 7), rng.randint(1, 7)
        matrix = [[rng.randint(0, 99) for _ in range(cols)] for _ in range(rows)]
        before = copy.deepcopy(matrix)
        assert spiral_order(matrix) == peel(matrix)
        assert matrix == before

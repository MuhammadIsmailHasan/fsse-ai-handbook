"""Automatic checks. Don't edit — make them pass by editing loops.py."""

import ast
from pathlib import Path

import pytest

from loops import cart_total, count_expensive, first_over, highest_price, longest_streak


def test_cart_total():
    assert cart_total([45_000, 120_000, 30_000]) == 195_000
    assert cart_total([]) == 0


def test_count_expensive():
    assert count_expensive([10, 50, 60], 40) == 2
    assert count_expensive([10, 40], 40) == 0  # "greater than", not "greater or equal"
    assert count_expensive([], 1) == 0


def test_highest_price():
    assert highest_price([3, 9, 2]) == 9
    assert highest_price([-5, -2, -9]) == -2
    assert highest_price([]) is None


def test_first_over():
    assert first_over([10, 50, 60], 40) == 50
    assert first_over([1, 2], 40) is None


@pytest.mark.parametrize(
    ("steps", "expected"),
    [
        ([12_000, 11_000, 2_000, 10_000], 2),
        ([10_000, 10_000, 10_000], 3),
        ([1, 2, 3], 0),
        ([], 0),
        ([9_999, 10_000, 3, 10_001, 12_000, 15_000], 3),
    ],
)
def test_longest_streak(steps, expected):
    assert longest_streak(steps, 10_000) == expected


def test_written_with_loops_not_shortcuts():
    tree = ast.parse(Path(__file__).with_name("loops.py").read_text())
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    assert not names & {"sum", "max", "min"}, "Write the loops yourself this time!"
    assert not any(isinstance(node, ast.ListComp) for node in ast.walk(tree))

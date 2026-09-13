"""Automatic checks. Don't edit — make them pass by editing rules.py."""

import pytest

from rules import letter_grade, shipping_cost, status_category


@pytest.mark.parametrize(
    ("score", "expected"),
    [(100, "A"), (90, "A"), (89, "B"), (80, "B"), (79, "C"), (70, "C"), (69, "D"), (60, "D"), (59, "E"), (0, "E")],
)
def test_letter_grade(score, expected):
    assert letter_grade(score) == expected


@pytest.mark.parametrize("score", [-1, 101, 250])
def test_letter_grade_rejects_invalid_scores(score):
    with pytest.raises(ValueError):
        letter_grade(score)


@pytest.mark.parametrize(
    ("code", "expected"),
    [
        (100, "informational"),
        (200, "success"),
        (204, "success"),
        (301, "redirect"),
        (404, "client error"),
        (499, "client error"),
        (500, "server error"),
        (503, "server error"),
        (99, "unknown"),
        (600, "unknown"),
    ],
)
def test_status_category(code, expected):
    assert status_category(code) == expected


@pytest.mark.parametrize(
    ("weight", "express", "member", "expected"),
    [
        (0, False, False, None),
        (-2, True, True, None),
        (1.5, True, True, 15_000),
        (1.5, True, False, 25_000),
        (3, False, True, 0),
        (3, False, False, 10_000),
    ],
)
def test_shipping_cost(weight, express, member, expected):
    assert shipping_cost(weight, express, member) == expected

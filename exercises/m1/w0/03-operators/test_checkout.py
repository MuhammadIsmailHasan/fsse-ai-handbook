"""Automatic checks. Don't edit — make them pass by editing checkout.py."""

import pytest

from checkout import gets_free_shipping, is_even, page_count, split_bill


@pytest.mark.parametrize(
    ("total", "people", "expected"),
    [(100_000, 4, (25_000, 0)), (100_000, 3, (33_333, 1)), (10, 20, (0, 10))],
)
def test_split_bill(total, people, expected):
    assert split_bill(total, people) == expected


@pytest.mark.parametrize(
    ("items", "per_page", "expected"),
    [(10, 3, 4), (9, 3, 3), (1, 10, 1), (0, 10, 0), (21, 20, 2)],
)
def test_page_count(items, per_page, expected):
    assert page_count(items, per_page) == expected


@pytest.mark.parametrize(("n", "expected"), [(0, True), (7, False), (10, True), (-3, False)])
def test_is_even(n, expected):
    assert is_even(n) is expected


@pytest.mark.parametrize(
    ("cart_total", "is_member", "is_oversized", "expected"),
    [
        (500_000, True, False, True),  # exactly the minimum counts
        (499_999, True, False, False),
        (900_000, False, False, False),  # not a member
        (900_000, True, True, False),  # oversized never ships free
    ],
)
def test_gets_free_shipping(cart_total, is_member, is_oversized, expected):
    assert gets_free_shipping(cart_total, is_member, is_oversized) is expected

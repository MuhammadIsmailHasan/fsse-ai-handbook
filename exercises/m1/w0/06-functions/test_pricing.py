"""Automatic checks. Don't edit — make them pass by editing pricing.py."""

import pytest

from pricing import apply_discount, cart_total, format_rupiah, line_total, receipt


@pytest.mark.parametrize(
    ("amount", "expected"),
    [(0, "Rp 0"), (500, "Rp 500"), (15_000, "Rp 15.000"), (1_500_000, "Rp 1.500.000")],
)
def test_format_rupiah(amount, expected):
    assert format_rupiah(amount) == expected


def test_apply_discount_default_and_custom():
    assert apply_discount(200_000) == 180_000
    assert apply_discount(200_000, 25) == 150_000
    assert apply_discount(199_999) == 179_999  # rounds down
    assert apply_discount(50_000, 0) == 50_000


def test_line_and_cart_total():
    assert line_total(25_000, 3) == 75_000
    assert cart_total([(25_000, 3), (10_000, 1)]) == 85_000
    assert cart_total([]) == 0


def test_receipt_with_discount():
    expected = "\n".join(
        [
            "25.000 x 3 = Rp 75.000",
            "10.000 x 1 = Rp 10.000",
            "Subtotal: Rp 85.000",
            "Discount (10%): -Rp 8.500",
            "Total: Rp 76.500",
        ]
    )
    assert receipt([(25_000, 3), (10_000, 1)], discount_percent=10) == expected


def test_receipt_without_discount():
    expected = "\n".join(["5.000 x 2 = Rp 10.000", "Subtotal: Rp 10.000", "Total: Rp 10.000"])
    assert receipt([(5_000, 2)]) == expected

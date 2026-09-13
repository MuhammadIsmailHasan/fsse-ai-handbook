"""Reference tests for discounts.py — one behavior per test, boundaries parametrized."""

import pytest

from discounts import FREE_SHIPPING_MINIMUM, SHIPPING_FEE, apply_discount, bulk_discount_percent, cart_total, parse_rupiah


class TestApplyDiscount:
    @pytest.mark.parametrize(
        ("price", "percent", "expected"),
        [
            (100_000, 10, 90_000),
            (199_999, 10, 179_999),  # 179_999.1 → rounds DOWN
            (999, 15, 849),  # 849.15 → 849
            (50_000, 0, 50_000),
            (50_000, 100, 0),
            (0, 50, 0),
        ],
    )
    def test_discounted_price_rounds_down(self, price, percent, expected):
        assert apply_discount(price, percent) == expected

    @pytest.mark.parametrize("percent", [-1, 101])
    def test_rejects_percent_outside_0_to_100(self, percent):
        with pytest.raises(ValueError, match="percent"):
            apply_discount(10_000, percent)

    def test_rejects_negative_price(self):
        with pytest.raises(ValueError, match="price"):
            apply_discount(-1, 10)


class TestBulkDiscountPercent:
    @pytest.mark.parametrize(
        ("quantity", "expected"),
        [(1, 0), (9, 0), (10, 5), (49, 5), (50, 10), (500, 10)],
    )
    def test_tiers_and_boundaries(self, quantity, expected):
        assert bulk_discount_percent(quantity) == expected

    @pytest.mark.parametrize("quantity", [0, -5])
    def test_rejects_quantity_below_one(self, quantity):
        with pytest.raises(ValueError):
            bulk_discount_percent(quantity)


class TestCartTotal:
    def test_empty_cart_costs_nothing(self):
        assert cart_total([], coupon=None) == 0

    def test_small_cart_pays_shipping(self):
        assert cart_total([(50_000, 2)], coupon=None) == 100_000 + SHIPPING_FEE

    def test_free_shipping_exactly_at_minimum(self):
        assert cart_total([(FREE_SHIPPING_MINIMUM, 1)], coupon=None) == FREE_SHIPPING_MINIMUM

    def test_shipping_charged_one_rupiah_below_minimum(self):
        assert cart_total([(FREE_SHIPPING_MINIMUM - 1, 1)], coupon=None) == FREE_SHIPPING_MINIMUM - 1 + SHIPPING_FEE

    def test_bulk_discount_applies_per_line(self):
        # 10 × 10_000 = 100_000 − 5% = 95_000; 1 × 20_000 = 20_000 → 115_000 + shipping
        assert cart_total([(10_000, 10), (20_000, 1)], coupon=None) == 115_000 + SHIPPING_FEE

    def test_hemat10_takes_ten_percent_off_subtotal(self):
        # 300_000 − 10% = 270_000 (still ≥ minimum → free shipping)
        assert cart_total([(100_000, 3)], coupon="HEMAT10") == 270_000

    def test_hemat10_can_drop_subtotal_below_free_shipping(self):
        # 210_000 − 10% = 189_000 < 200_000 → shipping charged
        assert cart_total([(210_000, 1)], coupon="HEMAT10") == 189_000 + SHIPPING_FEE

    def test_gratisongkir_removes_shipping(self):
        assert cart_total([(50_000, 1)], coupon="GRATISONGKIR") == 50_000

    def test_unknown_coupon_is_rejected(self):
        with pytest.raises(ValueError, match="coupon"):
            cart_total([(50_000, 1)], coupon="DISKON99")


class TestParseRupiah:
    @pytest.mark.parametrize(
        ("text", "expected"),
        [("Rp 15.000", 15_000), ("15.000", 15_000), ("15000", 15_000), ("  Rp 1.250.000 ", 1_250_000)],
    )
    def test_parses_valid_amounts(self, text, expected):
        assert parse_rupiah(text) == expected

    @pytest.mark.parametrize("text", ["", "Rp", "15,5", "15,000", "abc"])
    def test_rejects_invalid_text(self, text):
        with pytest.raises(ValueError):
            parse_rupiah(text)

"""Pricing rules for a small shop. This implementation is CORRECT — write tests for it."""

SHIPPING_FEE = 15_000
FREE_SHIPPING_MINIMUM = 200_000
COUPONS = {"HEMAT10", "GRATISONGKIR"}


def apply_discount(price: int, percent: int) -> int:
    """Price after a percentage discount, rounded DOWN to whole rupiah.

    Raises ValueError if price < 0 or percent is not between 0 and 100 (inclusive).
    """
    if price < 0:
        raise ValueError("price must be >= 0")
    if not 0 <= percent <= 100:
        raise ValueError("percent must be between 0 and 100")
    return price * (100 - percent) // 100


def bulk_discount_percent(quantity: int) -> int:
    """0% below 10 items, 5% for 10-49 items, 10% for 50 or more. ValueError if quantity < 1."""
    if quantity < 1:
        raise ValueError("quantity must be >= 1")
    if quantity >= 50:
        return 10
    if quantity >= 10:
        return 5
    return 0


def cart_total(items: list[tuple[int, int]], coupon: str | None) -> int:
    """Total to pay for (unit_price, quantity) items.

    1. Each line gets its bulk discount: apply_discount(price * quantity, bulk_discount_percent(quantity)).
    2. Subtotal = sum of lines.
    3. Coupon "HEMAT10" takes 10% off the subtotal (rounded down).
    4. Shipping is SHIPPING_FEE unless the subtotal (after coupon) is >= FREE_SHIPPING_MINIMUM,
       or the coupon is "GRATISONGKIR".
    5. An empty cart costs 0 (no shipping).
    Unknown coupons raise ValueError.
    """
    if coupon is not None and coupon not in COUPONS:
        raise ValueError(f"unknown coupon {coupon!r}")
    if not items:
        return 0
    subtotal = sum(apply_discount(price * quantity, bulk_discount_percent(quantity)) for price, quantity in items)
    if coupon == "HEMAT10":
        subtotal = apply_discount(subtotal, 10)
    shipping = 0 if subtotal > FREE_SHIPPING_MINIMUM or coupon == "GRATISONGKIR" else SHIPPING_FEE
    return subtotal + shipping


def parse_rupiah(text: str) -> int:
    """"Rp 15.000" or "15.000" or "15000" -> 15000. ValueError for anything else (e.g. "", "Rp", "15,5")."""
    cleaned = text.strip().removeprefix("Rp").strip().replace(".", "")
    if not cleaned.isdigit():
        raise ValueError(f"not a rupiah amount: {text!r}")
    return int(cleaned)

"""Reference solution — compare AFTER a real attempt."""

import math

FREE_SHIPPING_MINIMUM = 500_000


def split_bill(total: int, people: int) -> tuple[int, int]:
    return (total // people, total % people)


def page_count(total_items: int, per_page: int) -> int:
    # Adding (per_page - 1) pushes any partial page over the next whole number.
    return (total_items + per_page - 1) // per_page


def is_even(n: int) -> bool:
    return n % 2 == 0


def gets_free_shipping(cart_total: int, is_member: bool, is_oversized: bool) -> bool:
    qualifies = is_member and cart_total >= FREE_SHIPPING_MINIMUM
    return qualifies and not is_oversized


def shipping_fee(weight_kg: float) -> int:
    """Stretch: Rp 10.000 first kg, Rp 5.000 per started extra kg."""
    extra_kg = max(0, math.ceil(weight_kg) - 1)
    return 10_000 + extra_kg * 5_000

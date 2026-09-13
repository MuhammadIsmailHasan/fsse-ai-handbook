"""Reference solution — compare AFTER a real attempt."""


def format_number(amount: int) -> str:
    """1500000 -> "1.500.000" (Indonesian thousands separator)."""
    return f"{amount:,}".replace(",", ".")


def format_rupiah(amount: int) -> str:
    """1500000 -> "Rp 1.500.000"."""
    return f"Rp {format_number(amount)}"


def apply_discount(price: int, percent: int = 10) -> int:
    """Discounted price, rounded down. apply_discount(200_000) -> 180_000"""
    if percent < 0 or percent > 100:
        raise ValueError("percent must be between 0 and 100")
    return price * (100 - percent) // 100


def line_total(price: int, qty: int) -> int:
    return price * qty


def cart_total(items: list[tuple[int, int]]) -> int:
    total = 0
    for price, qty in items:
        total += line_total(price, qty)
    return total


def receipt(items: list[tuple[int, int]], discount_percent: int = 0) -> str:
    lines = []
    for price, qty in items:
        lines.append(f"{format_number(price)} x {qty} = {format_rupiah(line_total(price, qty))}")

    subtotal = cart_total(items)
    lines.append(f"Subtotal: {format_rupiah(subtotal)}")

    total = apply_discount(subtotal, discount_percent)
    if discount_percent > 0:
        lines.append(f"Discount ({discount_percent}%): -{format_rupiah(subtotal - total)}")

    lines.append(f"Total: {format_rupiah(total)}")
    return "\n".join(lines)

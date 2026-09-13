"""M1 · W0 · 06 — From copy-paste to functions.

The script below "works", but logic is duplicated and the two copies disagree.
Delete it and implement the functions underneath instead.
"""

# ---- OLD SCRIPT (read it, then delete it) -----------------------------------
# cart = [(25000, 3), (10000, 1)]
# total = 0
# for price, qty in cart:
#     total = total + price * qty
# print("Checkout total: Rp " + str(total))
#
# invoice_total = 0
# for price, qty in cart:
#     invoice_total = invoice_total + price + qty      # 🐛 spot the bug
# print("Invoice total: Rp " + str(invoice_total))
# -----------------------------------------------------------------------------


def format_rupiah(amount: int) -> str:
    # YOUR CODE HERE
    return ""


def apply_discount(price: int, percent: int = 10) -> int:
    # YOUR CODE HERE
    return 0


def line_total(price: int, qty: int) -> int:
    # YOUR CODE HERE
    return 0


def cart_total(items: list[tuple[int, int]]) -> int:
    # YOUR CODE HERE
    return 0


def receipt(items: list[tuple[int, int]], discount_percent: int = 0) -> str:
    # YOUR CODE HERE
    return ""

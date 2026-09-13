"""M1 · W0 · 07 — A sales report with 5 bugs. Find and fix them one by one."""

# Each sale is a (product_name, category, quantity, unit_price) tuple.
Sale = tuple[str, str, int, int]


def total_revenue(sales: list[Sale]) -> int:
    """Sum of quantity * unit_price for all sales."""
    total = 0
    for i in range(1, len(sales)):
        _, _, quantity, unit_price = sales[i]
        total += quantity * unit_price
    return total


def average_sale_value(sales: list[Sale]) -> float:
    """Average revenue per sale. Returns 0.0 when there are no sales."""
    return total_revenue(sales) / len(sales)


def revenue_for_category(sales: list[Sale], category: str) -> int:
    """Revenue for one category. Category matching ignores capitalization."""
    total = 0
    for _, sale_category, quantity, unit_price in sales:
        if sale_category == category:
            total += quantity * unit_price
    return total


def best_seller(sales: list[Sale]) -> str | None:
    """Product name with the highest total quantity sold, or None if no sales."""
    quantities: dict[str, int] = {}
    for name, _, quantity, _ in sales:
        quantities[name] = quantities.get(name, 0) + quantity

    best_name = None
    best_quantity = 0
    for name, quantity in quantities.items():
        if quantity > best_quantity:
            best_name = name
            best_quantity = quantity


def summary_line(sales: list[Sale]) -> str:
    """'3 sales · revenue Rp 125000 · best seller: Tea'"""
    best = best_seller(sales)
    return f"{len(sales)} sales · revenue Rp {total_revenue(sales)} · best seller: {best.title()}"

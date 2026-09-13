"""Reference solution. The 5 fixes are marked with FIX comments."""

Sale = tuple[str, str, int, int]


def total_revenue(sales: list[Sale]) -> int:
    total = 0
    for i in range(len(sales)):  # FIX 1: range started at 1 and skipped the first sale
        _, _, quantity, unit_price = sales[i]
        total += quantity * unit_price
    return total


def average_sale_value(sales: list[Sale]) -> float:
    if not sales:  # FIX 2: guard against ZeroDivisionError for an empty list
        return 0.0
    return total_revenue(sales) / len(sales)


def revenue_for_category(sales: list[Sale], category: str) -> int:
    total = 0
    for _, sale_category, quantity, unit_price in sales:
        if sale_category.lower() == category.lower():  # FIX 3: compare case-insensitively
            total += quantity * unit_price
    return total


def best_seller(sales: list[Sale]) -> str | None:
    quantities: dict[str, int] = {}
    for name, _, quantity, _ in sales:
        quantities[name] = quantities.get(name, 0) + quantity

    best_name = None
    best_quantity = 0
    for name, quantity in quantities.items():
        if quantity > best_quantity:
            best_name = name
            best_quantity = quantity
    return best_name  # FIX 4: the function never returned anything


def summary_line(sales: list[Sale]) -> str:
    best = best_seller(sales)
    best_label = best.title() if best is not None else "None"  # FIX 5: None has no .title()
    return f"{len(sales)} sales · revenue Rp {total_revenue(sales)} · best seller: {best_label}"

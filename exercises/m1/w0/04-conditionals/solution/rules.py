"""Reference solution — compare AFTER a real attempt."""


def letter_grade(score: int) -> str:
    if score < 0 or score > 100:
        raise ValueError("score must be between 0 and 100")
    if score >= 90:
        return "A"
    if score >= 80:
        return "B"
    if score >= 70:
        return "C"
    if score >= 60:
        return "D"
    return "E"


def status_category(code: int) -> str:
    if 100 <= code <= 199:
        return "informational"
    elif 200 <= code <= 299:
        return "success"
    elif 300 <= code <= 399:
        return "redirect"
    elif 400 <= code <= 499:
        return "client error"
    elif 500 <= code <= 599:
        return "server error"
    return "unknown"


# Stretch goal: the same logic as data instead of branches.
CATEGORIES = {1: "informational", 2: "success", 3: "redirect", 4: "client error", 5: "server error"}


def status_category_no_if(code: int) -> str:
    return CATEGORIES.get(code // 100, "unknown")


def shipping_cost(weight_kg: float, express: bool, member: bool) -> int | None:
    if weight_kg <= 0:
        return None
    if express:
        return 15_000 if member else 25_000
    return 0 if member else 10_000

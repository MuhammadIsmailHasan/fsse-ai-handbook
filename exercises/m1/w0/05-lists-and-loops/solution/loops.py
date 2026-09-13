"""Reference solution — compare AFTER a real attempt."""


def cart_total(prices: list[int]) -> int:
    total = 0
    for price in prices:
        total += price
    return total


def count_expensive(prices: list[int], limit: int) -> int:
    count = 0
    for price in prices:
        if price > limit:
            count += 1
    return count


def highest_price(prices: list[int]) -> int | None:
    if len(prices) == 0:
        return None
    highest = prices[0]
    for price in prices:
        if price > highest:
            highest = price
    return highest


def first_over(prices: list[int], limit: int) -> int | None:
    for price in prices:
        if price > limit:
            return price  # returning also stops the loop
    return None


def longest_streak(steps: list[int], goal: int) -> int:
    current = 0
    best = 0
    for day in steps:
        if day >= goal:
            current += 1
            if current > best:
                best = current
        else:
            current = 0
    return best


def chunk(items: list, size: int) -> list[list]:
    """Stretch goal."""
    pieces = []
    for start in range(0, len(items), size):
        pieces.append(items[start : start + size])
    return pieces

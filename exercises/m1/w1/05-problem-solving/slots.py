"""M1 · W1 · 05 — Free interview slots.

Write your examples and pseudocode BEFORE coding (see the lesson).
"""

Range = tuple[int, int]


def to_minutes(text: str) -> int:
    """"09:30" -> 570"""
    # YOUR CODE HERE
    return -1


def to_text(minutes: int) -> str:
    """570 -> "09:30" """
    # YOUR CODE HERE
    return ""


def merge_ranges(ranges: list[Range]) -> list[Range]:
    """Sort and merge overlapping or touching (start, end) minute ranges."""
    # YOUR CODE HERE
    return ranges


def free_slots(
    busy: list[tuple[str, str]],
    length: int,
    day_start: str = "09:00",
    day_end: str = "17:00",
) -> list[tuple[str, str]]:
    # YOUR CODE HERE
    return []

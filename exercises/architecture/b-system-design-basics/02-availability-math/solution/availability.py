"""Reference solution."""

import math

MINUTES_PER_YEAR = 365 * 24 * 60


def downtime_minutes_per_year(availability: float) -> float:
    return (1 - availability) * MINUTES_PER_YEAR


def series(availabilities: list[float]) -> float:
    return math.prod(availabilities)  # prod([]) == 1


def parallel(availabilities: list[float]) -> float:
    if not availabilities:
        return 0.0
    all_fail = math.prod(1 - a for a in availabilities)
    return 1 - all_fail


def copies_needed(single: float, target: float) -> int:
    if not 0 < single < 1:
        raise ValueError("single availability must be between 0 and 1 (exclusive)")
    copies = 1
    while parallel([single] * copies) < target - 1e-12:  # tolerance for float rounding
        copies += 1
    return copies

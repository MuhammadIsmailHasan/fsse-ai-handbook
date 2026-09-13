# Time O(n): each number is counted upward at most once (only from a streak start). Space O(n).
def longest_streak(days: list[int]) -> int:
    present = set(days)
    best = 0
    for day in present:
        if day - 1 not in present:  # start of a streak
            length = 1
            while day + length in present:
                length += 1
            best = max(best, length)
    return best

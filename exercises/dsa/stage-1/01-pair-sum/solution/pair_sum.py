"""Reference solution.

Time complexity: O(n) — one pass, set lookups are O(1) on average.
Space complexity: O(n) — the `seen` set can hold every number.
"""


def has_pair_with_sum(nums: list[int], target: int) -> bool:
    seen: set[int] = set()
    for x in nums:
        if target - x in seen:
            return True
        seen.add(x)
    return False

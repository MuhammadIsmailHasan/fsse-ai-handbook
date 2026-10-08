import heapq  # noqa: F401  (you may use it here)


def k_largest(nums: list[int], k: int) -> list[int]:
    """The k largest values, biggest first. If k >= len(nums), return all of them (sorted desc).

    Target: O(n log k) time and O(k) extra space — keep a MIN-heap of size k.
    Do not sort the whole list (the test input is large and k is small).
    """
    raise NotImplementedError


def k_most_frequent(words: list[str], k: int) -> list[str]:
    """The k most frequent words. Most frequent first; ties broken alphabetically (a before b)."""
    raise NotImplementedError


class KthLargest:
    """Track the k-th largest value in a stream.

    KthLargest(3, [4, 5, 8, 2]) then add(3) -> 4, add(5) -> 5, add(10) -> 5, add(9) -> 8
    add() returns the current k-th largest. Keep only k values (a min-heap of size k).
    Until k values have been seen, add() returns None.
    """

    def __init__(self, k: int, nums: list[int]) -> None:
        raise NotImplementedError

    def add(self, val: int) -> int | None:
        raise NotImplementedError

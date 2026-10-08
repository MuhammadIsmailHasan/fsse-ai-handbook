import heapq  # noqa: F401  (you may use it here)


class MedianFinder:
    """Keep a growing set of numbers and report the median at any time.

    add_num(x)     O(log n)
    find_median()  O(1): the middle value, or the average of the two middle values
                   (return a float for an even count, e.g. 2.5). IndexError if empty.

    Idea: TWO heaps. A max-heap for the smaller half and a min-heap for the larger half,
    always balanced so their sizes differ by at most 1. (heapq has only a min-heap: store
    negated numbers for the max-heap.)
    """

    def __init__(self) -> None:
        raise NotImplementedError

    def add_num(self, num: int) -> None:
        raise NotImplementedError

    def find_median(self) -> float:
        raise NotImplementedError


def min_cost_to_connect(ropes: list[int]) -> int:
    """Join all ropes into one. Joining two ropes costs the sum of their lengths.
    Return the smallest total cost. 0 or 1 rope: 0.

    Greedy: always join the two SHORTEST ropes (a min-heap), and put the result back.
    """
    raise NotImplementedError

import heapq  # noqa: F401  (you may use it here)
from collections.abc import Iterable, Iterator


def merge_k_sorted(lists: list[list[int]]) -> list[int]:
    """Merge k sorted lists into one sorted list.

    Target: O(N log k) where N is the total number of items — keep a heap with the CURRENT
    front item of each list. Do not concatenate and sort.
    """
    raise NotImplementedError


def merge_streams(streams: list[Iterable[int]]) -> Iterator[int]:
    """Lazily merge k sorted iterables (they may be infinite!). Yield one value at a time.

    Must be a generator that only reads what it needs: next(merged) may read at most one
    new item per input stream beyond what it has already yielded.
    """
    raise NotImplementedError


def smallest_pair_sums(a: list[int], b: list[int], k: int) -> list[int]:
    """The k smallest sums a[i] + b[j], for two sorted lists. Ascending. Fewer if there are fewer pairs.

    Do not build all len(a) * len(b) sums (the test lists are 20,000 long and k is 5).
    Idea: start with (a[0] + b[0], 0, 0) in a heap; after popping (i, j) push (i, j + 1)
    and, only when j == 0, push (i + 1, 0).
    """
    raise NotImplementedError

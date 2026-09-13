import heapq
from functools import total_ordering


@total_ordering
class _Entry:
    """Orders entries so the heap's smallest item is the WORST candidate: lower count, or same count and later alphabetically."""

    __slots__ = ("term", "count")

    def __init__(self, term: str, count: int):
        self.term, self.count = term, count

    def __lt__(self, other: "_Entry") -> bool:
        if self.count != other.count:
            return self.count < other.count
        return self.term > other.term

    def __eq__(self, other: object) -> bool:
        return isinstance(other, _Entry) and (self.count, self.term) == (other.count, other.term)


# Time O(n + d log k) for d distinct terms, space O(d).
def top_k_skills(searches: list[str], k: int) -> list[tuple[str, int]]:
    if k <= 0:
        return []
    counts: dict[str, int] = {}
    for term in searches:
        counts[term] = counts.get(term, 0) + 1
    heap: list[_Entry] = []
    for term, count in counts.items():
        entry = _Entry(term, count)
        if len(heap) < k:
            heapq.heappush(heap, entry)
        elif heap[0] < entry:
            heapq.heapreplace(heap, entry)
    best = []
    while heap:
        worst = heapq.heappop(heap)
        best.append((worst.term, worst.count))
    return best[::-1]

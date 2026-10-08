import heapq
from collections import Counter


def k_largest(nums, k):
    if k <= 0:
        return []
    heap = []
    for n in nums:
        if len(heap) < k:
            heapq.heappush(heap, n)
        elif n > heap[0]:
            heapq.heapreplace(heap, n)
    return sorted(heap, reverse=True)


def k_most_frequent(words, k):
    counts = Counter(words)
    return [w for w, _ in heapq.nsmallest(k, counts.items(), key=lambda item: (-item[1], item[0]))]


class KthLargest:
    def __init__(self, k, nums):
        self.k = k
        self.heap = []
        for n in nums:
            self._offer(n)

    def _offer(self, val):
        if len(self.heap) < self.k:
            heapq.heappush(self.heap, val)
        elif val > self.heap[0]:
            heapq.heapreplace(self.heap, val)

    def add(self, val):
        self._offer(val)
        return self.heap[0] if len(self.heap) == self.k else None

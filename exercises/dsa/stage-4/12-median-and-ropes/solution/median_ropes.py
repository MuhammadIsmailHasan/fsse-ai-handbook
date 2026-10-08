import heapq


class MedianFinder:
    def __init__(self):
        self.low = []    # max-heap of the smaller half (negated)
        self.high = []   # min-heap of the larger half

    def add_num(self, num):
        heapq.heappush(self.low, -num)
        heapq.heappush(self.high, -heapq.heappop(self.low))
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))

    def find_median(self):
        if not self.low:
            raise IndexError("median of empty collection")
        if len(self.low) > len(self.high):
            return float(-self.low[0])
        return (-self.low[0] + self.high[0]) / 2


def min_cost_to_connect(ropes):
    heap = list(ropes)
    heapq.heapify(heap)
    total = 0
    while len(heap) > 1:
        joined = heapq.heappop(heap) + heapq.heappop(heap)
        total += joined
        heapq.heappush(heap, joined)
    return total

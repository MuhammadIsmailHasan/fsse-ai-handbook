import heapq


def merge_k_sorted(lists):
    heap = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]
    heapq.heapify(heap)
    out = []
    while heap:
        value, i, j = heapq.heappop(heap)
        out.append(value)
        if j + 1 < len(lists[i]):
            heapq.heappush(heap, (lists[i][j + 1], i, j + 1))
    return out


def merge_streams(streams):
    iterators = [iter(s) for s in streams]
    heap = []
    for i, it in enumerate(iterators):
        for first in it:
            heap.append((first, i))
            break
    heapq.heapify(heap)
    while heap:
        value, i = heap[0]
        yield value
        nxt = next(iterators[i], None)
        # Only read the next item of the stream we just used.
        if nxt is None:
            heapq.heappop(heap)
        else:
            heapq.heapreplace(heap, (nxt, i))


def smallest_pair_sums(a, b, k):
    if not a or not b or k <= 0:
        return []
    heap = [(a[0] + b[0], 0, 0)]
    out = []
    while heap and len(out) < k:
        total, i, j = heapq.heappop(heap)
        out.append(total)
        if j + 1 < len(b):
            heapq.heappush(heap, (a[i] + b[j + 1], i, j + 1))
        if j == 0 and i + 1 < len(a):
            heapq.heappush(heap, (a[i + 1] + b[0], i + 1, 0))
    return out

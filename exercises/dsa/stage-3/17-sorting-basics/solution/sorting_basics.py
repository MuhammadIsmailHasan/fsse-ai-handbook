"""Sorting basics — reference solution."""

import heapq


# Time O(n log n). Negating works for numbers; for strings "newest first" we sort in two stable passes.
def rank_jobs(jobs: list[dict]) -> list[dict]:
    by_title = sorted(jobs, key=lambda job: job["title"])  # least important key first…
    by_date = sorted(by_title, key=lambda job: job["posted_on"], reverse=True)  # …stable sorts keep earlier order on ties
    return sorted(by_date, key=lambda job: (job["salary_max"] is None, -(job["salary_max"] or 0)))


# Time O(n log n) for sorting, O(n) to merge.
def merge_intervals(intervals: list[list[int]]) -> list[list[int]]:
    merged: list[list[int]] = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged


# Time O(n log k), space O(k): a min-heap of the k largest values seen so far.
def kth_largest(nums: list[int], k: int) -> int:
    heap: list[int] = []
    for value in nums:
        if len(heap) < k:
            heapq.heappush(heap, value)
        elif value > heap[0]:
            heapq.heapreplace(heap, value)
    return heap[0]

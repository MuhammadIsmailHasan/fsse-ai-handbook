# Time O(n log(sum)), space O(1).
# If the tasks fit into at most k sprints with limit L, we can always split some sprint further (k <= n)
# without making any sprint heavier, so "at most k" is equivalent to "exactly k".
def min_heaviest_sprint(points: list[int], k: int) -> int:
    def fits(limit: int) -> bool:
        sprints, load = 1, 0
        for p in points:
            if load + p > limit:
                sprints += 1
                load = 0
            load += p
        return sprints <= k

    low, high = max(points), sum(points)
    while low < high:
        mid = (low + high) // 2
        if fits(mid):
            high = mid
        else:
            low = mid + 1
    return low

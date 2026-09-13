# Time O(n log(sum(sizes))), space O(1).
def min_daily_capacity(sizes: list[int], days: int) -> int:
    def can_finish(capacity: int) -> bool:
        used_days, load = 1, 0
        for size in sizes:
            if load + size > capacity:
                used_days += 1
                load = 0
            load += size
        return used_days <= days

    low, high = max(sizes), sum(sizes)
    while low < high:
        mid = (low + high) // 2
        if can_finish(mid):
            high = mid
        else:
            low = mid + 1
    return low

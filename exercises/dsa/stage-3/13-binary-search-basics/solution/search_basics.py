"""Binary search basics — reference solution."""


# Time O(log n), space O(1). Closed interval [low, high].
def find_index(sorted_nums: list[int], target: int) -> int:
    low, high = 0, len(sorted_nums) - 1
    while low <= high:
        mid = (low + high) // 2
        if sorted_nums[mid] == target:
            return mid
        if sorted_nums[mid] < target:
            low = mid + 1
        else:
            high = mid - 1
    return -1


# Time O(log n). Half-open interval [low, high): the answer is always inside it.
def first_at_least(sorted_nums: list[int], x: int) -> int:
    low, high = 0, len(sorted_nums)
    while low < high:
        mid = (low + high) // 2
        if sorted_nums[mid] < x:
            low = mid + 1
        else:
            high = mid
    return low


# Time O(log n): binary search on the answer — "is r*r <= n?" is True…True False…False.
def integer_sqrt(n: int) -> int:
    low, high = 0, n
    while low < high:
        mid = (low + high + 1) // 2  # round up so the loop always shrinks
        if mid * mid <= n:
            low = mid
        else:
            high = mid - 1
    return low

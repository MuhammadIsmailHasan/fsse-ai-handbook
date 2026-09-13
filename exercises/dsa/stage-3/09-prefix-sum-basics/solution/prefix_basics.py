"""Prefix sum basics — reference solution."""


# Time O(n), space O(n).
def running_totals(nums: list[int]) -> list[int]:
    totals, running = [], 0
    for value in nums:
        running += value
        totals.append(running)
    return totals


# Time O(n + q): prefix[i] = sum(nums[:i]), so sum(nums[i..j]) = prefix[j + 1] - prefix[i].
def range_sums(nums: list[int], queries: list[tuple[int, int]]) -> list[int]:
    prefix = [0]
    for value in nums:
        prefix.append(prefix[-1] + value)
    return [prefix[j + 1] - prefix[i] for i, j in queries]


# Time O(n), space O(1).
def pivot_index(nums: list[int]) -> int:
    total = sum(nums)
    left = 0
    for i, value in enumerate(nums):
        if left == total - left - value:
            return i
        left += value
    return -1

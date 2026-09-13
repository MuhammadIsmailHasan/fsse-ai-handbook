# Time O(n²): sort O(n log n), then a two-pointer scan per first element. Space O(1) extra (besides output/sort).
def three_sum_zero(nums: list[int]) -> list[list[int]]:
    nums = sorted(nums)
    result: list[list[int]] = []
    for first in range(len(nums) - 2):
        if nums[first] > 0:
            break  # all remaining numbers are positive
        if first > 0 and nums[first] == nums[first - 1]:
            continue  # same first value → same triplets
        left, right = first + 1, len(nums) - 1
        while left < right:
            total = nums[first] + nums[left] + nums[right]
            if total < 0:
                left += 1
            elif total > 0:
                right -= 1
            else:
                result.append([nums[first], nums[left], nums[right]])
                left += 1
                right -= 1
                while left < right and nums[left] == nums[left - 1]:
                    left += 1
    return result

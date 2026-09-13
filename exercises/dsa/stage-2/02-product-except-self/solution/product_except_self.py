# Time O(n), space O(1) extra besides the output list.
def product_except_self(nums: list[int]) -> list[int]:
    result = [1] * len(nums)
    left = 1
    for i in range(len(nums)):  # result[i] = product of nums[:i]
        result[i] = left
        left *= nums[i]
    right = 1
    for i in range(len(nums) - 1, -1, -1):  # multiply by product of nums[i+1:]
        result[i] *= right
        right *= nums[i]
    return result

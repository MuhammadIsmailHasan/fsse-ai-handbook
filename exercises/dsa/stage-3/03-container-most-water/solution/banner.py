# Time O(n), space O(1). Moving the taller pole can only shrink width without raising the limiting height.
def max_banner_area(heights: list[int]) -> int:
    left, right = 0, len(heights) - 1
    best = 0
    while left < right:
        best = max(best, min(heights[left], heights[right]) * (right - left))
        if heights[left] <= heights[right]:
            left += 1
        else:
            right -= 1
    return best

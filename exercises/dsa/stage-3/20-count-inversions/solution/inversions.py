# Time O(n log n), space O(n). Iterative bottom-up merge sort avoids recursion limits.
def count_inversions(nums: list[int]) -> int:
    items = list(nums)
    n = len(items)
    inversions = 0
    width = 1
    while width < n:
        merged: list[int] = []
        for start in range(0, n, 2 * width):
            left = items[start : start + width]
            right = items[start + width : start + 2 * width]
            i = j = 0
            while i < len(left) and j < len(right):
                if left[i] <= right[j]:
                    merged.append(left[i])
                    i += 1
                else:
                    merged.append(right[j])
                    inversions += len(left) - i  # every remaining left item is bigger
                    j += 1
            merged.extend(left[i:])
            merged.extend(right[j:])
        items = merged
        width *= 2
    return inversions

"""Two pointer basics — reference solution."""


# Time O(n), space O(1).
def is_clean_palindrome(text: str) -> bool:
    left, right = 0, len(text) - 1
    while left < right:
        if not text[left].isalnum():
            left += 1
        elif not text[right].isalnum():
            right -= 1
        elif text[left].lower() != text[right].lower():
            return False
        else:
            left += 1
            right -= 1
    return True


# Time O(n), space O(1). Moving `right` down first when the sum is too big keeps the smallest valid `left`.
def pair_indices(sorted_nums: list[int], target: int) -> tuple[int, int] | None:
    left, right = 0, len(sorted_nums) - 1
    while left < right:
        total = sorted_nums[left] + sorted_nums[right]
        if total == target:
            return (left, right)
        if total < target:
            left += 1
        else:
            right -= 1
    return None


# Time O(n + m), space O(n + m).
def merge_sorted_lists(a: list[int], b: list[int]) -> list[int]:
    i = j = 0
    merged: list[int] = []
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            merged.append(a[i])
            i += 1
        else:
            merged.append(b[j])
            j += 1
    merged.extend(a[i:])
    merged.extend(b[j:])
    return merged

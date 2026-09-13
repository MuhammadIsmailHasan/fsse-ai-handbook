"""Reference solution — two pointers. O(n) time, O(1) extra space."""


def reverse_in_place(items: list) -> None:
    left, right = 0, len(items) - 1
    while left < right:
        items[left], items[right] = items[right], items[left]
        left += 1
        right -= 1

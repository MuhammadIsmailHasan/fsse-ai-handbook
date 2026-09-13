"""Sliding window basics — reference solution."""

VOWELS = set("aeiou")


# Time O(n), space O(1).
def max_window_sum(nums: list[int], k: int) -> int | None:
    if k <= 0 or k > len(nums):
        return None
    window = sum(nums[:k])
    best = window
    for right in range(k, len(nums)):
        window += nums[right] - nums[right - k]
        best = max(best, window)
    return best


# Time O(n), space O(min(n, k)): a set holding only the last k items.
def has_nearby_repeat(items: list[str], k: int) -> bool:
    window: set[str] = set()
    for i, item in enumerate(items):
        if item in window:
            return True
        window.add(item)
        if len(window) > k:
            window.discard(items[i - k])
    return False


# Time O(n), space O(1).
def max_vowels(text: str, k: int) -> int:
    count = sum(1 for c in text[:k] if c in VOWELS)
    best = count
    for right in range(k, len(text)):
        count += (text[right] in VOWELS) - (text[right - k] in VOWELS)
        best = max(best, count)
    return best

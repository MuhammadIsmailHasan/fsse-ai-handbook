# Time O(n), space O(n).
def count_periods(changes: list[int], k: int) -> int:
    seen = {0: 1}  # prefix sum -> how many times it occurred (the empty prefix counts once)
    prefix = count = 0
    for change in changes:
        prefix += change
        count += seen.get(prefix - k, 0)
        seen[prefix] = seen.get(prefix, 0) + 1
    return count

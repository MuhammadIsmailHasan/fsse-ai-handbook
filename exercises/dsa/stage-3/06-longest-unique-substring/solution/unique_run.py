# Time O(n), space O(alphabet).
def longest_unique_run(text: str) -> int:
    last_seen: dict[str, int] = {}
    left = best = 0
    for right, char in enumerate(text):
        if last_seen.get(char, -1) >= left:  # repeat inside the current window
            left = last_seen[char] + 1
        last_seen[char] = right
        best = max(best, right - left + 1)
    return best

"""Reference solution.

Time complexity: O(n) — two passes over the text.
Space complexity: O(k) — one counter per distinct character (k ≤ n).
"""


def first_unique_index(text: str) -> int:
    counts: dict[str, int] = {}
    for ch in text:
        counts[ch] = counts.get(ch, 0) + 1
    for index, ch in enumerate(text):
        if counts[ch] == 1:
            return index
    return -1

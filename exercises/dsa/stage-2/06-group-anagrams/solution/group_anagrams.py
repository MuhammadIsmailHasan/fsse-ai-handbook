# Time O(n · k) with a 26-letter count key (O(n · k log k) with a sorted-string key), space O(n · k).
def group_anagrams(words: list[str]) -> list[list[str]]:
    groups: dict[tuple[tuple[str, int], ...], list[str]] = {}
    for word in words:
        counts: dict[str, int] = {}
        for char in word:
            counts[char] = counts.get(char, 0) + 1
        key = tuple(sorted(counts.items()))  # sorting ≤ distinct letters, not the whole word
        groups.setdefault(key, []).append(word)
    return list(groups.values())

# Time O(S) where S = total characters checked (stops at the first mismatch), space O(1) extra.
def longest_common_prefix(words: list[str]) -> str:
    if not words:
        return ""
    first = words[0]
    for i, char in enumerate(first):  # vertical scan: column by column
        for word in words[1:]:
            if i >= len(word) or word[i] != char:
                return first[:i]
    return first

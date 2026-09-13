# Time O(n + m), space O(alphabet).
def shortest_covering(text: str, required: str) -> str:
    if not required:
        return ""
    need: dict[str, int] = {}
    for char in required:
        need[char] = need.get(char, 0) + 1
    missing = len(required)
    left = 0
    best_start, best_len = 0, len(text) + 1
    for right, char in enumerate(text):
        if need.get(char, 0) > 0:
            missing -= 1
        need[char] = need.get(char, 0) - 1  # negative = surplus inside the window
        while missing == 0:
            if right - left + 1 < best_len:
                best_start, best_len = left, right - left + 1
            need[text[left]] += 1
            if need[text[left]] > 0:
                missing += 1
            left += 1
    return text[best_start : best_start + best_len] if best_len <= len(text) else ""

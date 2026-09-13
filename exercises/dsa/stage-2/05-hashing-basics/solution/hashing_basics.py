"""Hashing basics — reference solution."""


# Time O(n), space O(n).
def first_repeat(items: list[str]) -> str | None:
    seen: set[str] = set()
    for item in items:
        if item in seen:
            return item
        seen.add(item)
    return None


# Time O(n), space O(k) distinct characters.
def is_anagram(a: str, b: str) -> bool:
    if len(a) != len(b):
        return False
    counts: dict[str, int] = {}
    for char in a:
        counts[char] = counts.get(char, 0) + 1
    for char in b:
        if counts.get(char, 0) == 0:
            return False
        counts[char] -= 1
    return True


# Time O(n + m), space O(n + m).
def common_skills(mine: list[str], wanted: list[str]) -> list[str]:
    have = set(mine)
    added: set[str] = set()
    result = []
    for skill in wanted:
        if skill in have and skill not in added:
            result.append(skill)
            added.add(skill)
    return result

"""Reference solution — compare AFTER a real attempt."""


def count_items(items: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1
    return counts


def most_frequent(items: list[str]) -> list[str]:
    counts = count_items(items)
    if not counts:
        return []
    top = max(counts.values())
    return sorted(item for item, count in counts.items() if count == top)


def first_duplicate(items: list[str]) -> str | None:
    seen: set[str] = set()
    for item in items:
        if item in seen:
            return item
        seen.add(item)
    return None


def count_skills(skill_strings: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for line in skill_strings:
        for raw in line.split(","):
            skill = raw.strip().lower()
            if skill:
                counts[skill] = counts.get(skill, 0) + 1
    return counts


def top_skills(skill_strings: list[str], n: int) -> list[tuple[str, int]]:
    ranking = sorted(count_skills(skill_strings).items(), key=lambda pair: (-pair[1], pair[0]))
    return ranking[:n]


def are_anagrams(a: str, b: str) -> bool:
    """Stretch goal."""
    clean = lambda text: [ch for ch in text.lower() if ch != " "]  # noqa: E731
    return count_items(clean(a)) == count_items(clean(b))

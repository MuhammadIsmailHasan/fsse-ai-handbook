"""Reference solution."""


def numbered_titles(jobs: list[dict]) -> list[str]:
    matches = [job for job in jobs if job["remote"] and job["salary"] is not None]
    return [f"{number}. {job['title']}" for number, job in enumerate(matches, start=1)]


def pair_scores(names: list[str], scores: list[int]) -> dict[str, int]:
    return dict(zip(names, scores, strict=True))  # strict=True raises ValueError on length mismatch


def initials(full_name: str) -> str:
    return "".join(part[0].upper() for part in full_name.split())  # split() ignores extra spaces


def count_lines_with(path: str, word: str) -> int:
    needle = word.lower()
    with open(path, encoding="utf-8") as file:
        return sum(1 for line in file if needle in line.lower())

"""M1 · W1 · 03 — Sorting."""

Job = dict[str, object]


def insertion_sort(values: list[int]) -> list[int]:
    """Return a NEW sorted list. Don't use sorted() or .sort() here."""
    # YOUR CODE HERE
    return list(values)


def top_paying(jobs: list[Job], n: int) -> list[Job]:
    """n highest salaries; equal salaries ordered by title A-Z."""
    # YOUR CODE HERE
    return jobs[:n]


def sort_names(names: list[str]) -> list[str]:
    """Case-insensitive A-Z."""
    # YOUR CODE HERE
    return names


def newest_first(jobs: list[Job]) -> list[Job]:
    """Newest `posted` first; jobs with posted=None last, in original order."""
    # YOUR CODE HERE
    return jobs

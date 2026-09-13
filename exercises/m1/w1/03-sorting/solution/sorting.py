"""Reference solution — compare AFTER a real attempt."""

Job = dict[str, object]


def insertion_sort(values: list[int]) -> list[int]:
    result = list(values)
    for i in range(1, len(result)):
        current = result[i]
        j = i - 1
        while j >= 0 and result[j] > current:
            result[j + 1] = result[j]
            j -= 1
        result[j + 1] = current
    return result


def top_paying(jobs: list[Job], n: int) -> list[Job]:
    return sorted(jobs, key=lambda job: (-job["salary"], job["title"]))[:n]


def sort_names(names: list[str]) -> list[str]:
    return sorted(names, key=str.lower)


def newest_first(jobs: list[Job]) -> list[Job]:
    with_date = [job for job in jobs if job["posted"] is not None]
    without_date = [job for job in jobs if job["posted"] is None]
    return sorted(with_date, key=lambda job: job["posted"], reverse=True) + without_date


def merge_sorted(a: list[int], b: list[int]) -> list[int]:
    """Stretch goal: the merge step of merge sort."""
    merged, i, j = [], 0, 0
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:
            merged.append(a[i])
            i += 1
        else:
            merged.append(b[j])
            j += 1
    return merged + a[i:] + b[j:]

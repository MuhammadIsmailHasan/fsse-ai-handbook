# Time O(n log n), space O(n): sweep over sorted start and end times.
def rooms_needed(interviews: list[tuple[int, int]]) -> int:
    starts = sorted(start for start, _ in interviews)
    ends = sorted(end for _, end in interviews)
    in_use = best = 0
    e = 0
    for start in starts:
        while e < len(ends) and ends[e] <= start:  # rooms freed at or before this start
            in_use -= 1
            e += 1
        in_use += 1
        best = max(best, in_use)
    return best

"""Reference solution — compare AFTER a real attempt."""

Range = tuple[int, int]


def to_minutes(text: str) -> int:
    hours, minutes = text.split(":")
    return int(hours) * 60 + int(minutes)


def to_text(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def merge_ranges(ranges: list[Range]) -> list[Range]:
    merged: list[Range] = []
    for start, end in sorted(ranges):
        if merged and start <= merged[-1][1]:
            last_start, last_end = merged[-1]
            merged[-1] = (last_start, max(last_end, end))
        else:
            merged.append((start, end))
    return merged


def free_slots(
    busy: list[tuple[str, str]],
    length: int,
    day_start: str = "09:00",
    day_end: str = "17:00",
) -> list[tuple[str, str]]:
    start_of_day, end_of_day = to_minutes(day_start), to_minutes(day_end)

    # Convert, clip to the day window, and drop ranges fully outside it.
    clipped = []
    for start_text, end_text in busy:
        start = max(to_minutes(start_text), start_of_day)
        end = min(to_minutes(end_text), end_of_day)
        if start < end:
            clipped.append((start, end))

    gaps = []
    cursor = start_of_day
    for start, end in merge_ranges(clipped):
        if start - cursor >= length:
            gaps.append((cursor, start))
        cursor = max(cursor, end)
    if end_of_day - cursor >= length:
        gaps.append((cursor, end_of_day))

    return [(to_text(start), to_text(end)) for start, end in gaps]

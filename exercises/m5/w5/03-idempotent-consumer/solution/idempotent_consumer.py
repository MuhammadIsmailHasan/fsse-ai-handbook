"""Reference solution. See README.md."""


def apply_once(events: list[tuple[str, int]]) -> tuple[int, list[str]]:
    seen: set[str] = set()
    applied_ids: list[str] = []
    total = 0

    for message_id, amount in events:
        if message_id in seen:
            continue  # duplicate delivery — do nothing
        seen.add(message_id)
        applied_ids.append(message_id)
        total += amount

    return total, applied_ids

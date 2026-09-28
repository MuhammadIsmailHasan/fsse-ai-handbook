"""Architecture · H — Diverge during a partition, then converge (solution)."""


def apply(state: dict, key: str, value, ts: int) -> None:
    existing = state.get(key)
    if existing is None or ts > existing[1]:
        state[key] = (value, ts)


def merge_lww(a: dict, b: dict) -> dict:
    result = dict(a)
    for key, entry in b.items():
        current = result.get(key)
        if current is None:
            result[key] = entry
        elif entry[1] > current[1] or (entry[1] == current[1] and entry[0] > current[0]):
            result[key] = entry
    return result


def merge_counter(a: dict[str, int], b: dict[str, int]) -> dict[str, int]:
    result = dict(a)
    for key, inc in b.items():
        result[key] = result.get(key, 0) + inc
    return result

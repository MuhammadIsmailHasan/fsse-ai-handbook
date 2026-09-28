"""Architecture · F — Build a tiny index and count the work (solution)."""


def linear_search(rows: list[dict], field: str, value) -> tuple[list[dict], int]:
    matches = [row for row in rows if row[field] == value]
    return matches, len(rows)


def build_index(rows: list[dict], field: str) -> dict:
    index: dict = {}
    for row in rows:
        index.setdefault(row[field], []).append(row)
    return index


def indexed_search(index: dict, value) -> list[dict]:
    return index.get(value, [])


def build_composite_index(rows: list[dict], field_a: str, field_b: str) -> dict:
    index: dict = {}
    for row in rows:
        index.setdefault((row[field_a], row[field_b]), []).append(row)
    return index


def search_composite_by_first(index: dict, a_value) -> list[dict]:
    matches: list[dict] = []
    for (a, _b), rows in index.items():
        if a == a_value:
            matches.extend(rows)
    return matches

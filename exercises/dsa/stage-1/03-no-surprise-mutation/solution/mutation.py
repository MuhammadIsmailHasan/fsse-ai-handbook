"""Reference solution."""


def add_tag(tags: list[str], tag: str) -> list[str]:
    return tags + [tag]  # `+` builds a new list


def make_grid(rows: int, cols: int, fill: int = 0) -> list[list[int]]:
    return [[fill] * cols for _ in range(rows)]  # a fresh row per iteration


def apply_raise(employees: list[dict], percent: int) -> list[dict]:
    # A shallow copy of the LIST still shares the dicts, so copy each dict.
    return [{**employee, "salary": employee["salary"] * (100 + percent) // 100} for employee in employees]

"""DSA · Stage 1 — Fix the mutation bugs."""


def add_tag(tags: list[str], tag: str) -> list[str]:
    """Return a NEW list with tag at the end. Don't modify `tags`."""
    tags.append(tag)
    return tags


def make_grid(rows: int, cols: int, fill: int = 0) -> list[list[int]]:
    """rows × cols grid where every row is an independent list."""
    return [[fill] * cols] * rows


def apply_raise(employees: list[dict], percent: int) -> list[dict]:
    """Return NEW employee dicts with salary increased (rounded down). Don't modify inputs."""
    result = employees.copy()
    for employee in result:
        employee["salary"] = employee["salary"] * (100 + percent) // 100
    return result

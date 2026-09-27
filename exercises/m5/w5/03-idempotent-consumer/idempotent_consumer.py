"""Process each queue message exactly once. See README.md."""


def apply_once(events: list[tuple[str, int]]) -> tuple[int, list[str]]:
    raise NotImplementedError

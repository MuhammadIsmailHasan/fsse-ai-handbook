"""M2 · W3 · 02 — Statuses, commands and events."""


class InvalidTransition(Exception):
    pass


# YOUR TRANSITIONS TABLE HERE


def next_status(current: str, target: str) -> str:
    # YOUR CODE HERE
    return target


def allowed_next(current: str) -> list[str]:
    # YOUR CODE HERE
    return []


def parse_command(text: str) -> dict:
    # YOUR CODE HERE (use match)
    return {}


def describe_event(event: dict) -> str:
    # YOUR CODE HERE (use match with mapping patterns)
    return ""

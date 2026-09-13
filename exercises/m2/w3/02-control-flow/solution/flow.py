"""Reference solution."""


class InvalidTransition(Exception):
    pass


TRANSITIONS: dict[str, frozenset[str]] = {
    "wishlist": frozenset({"applied", "withdrawn"}),
    "applied": frozenset({"interview", "rejected", "withdrawn"}),
    "interview": frozenset({"interview", "offer", "rejected", "withdrawn"}),
    "offer": frozenset({"offer_accepted", "offer_declined"}),
    "rejected": frozenset(),
    "withdrawn": frozenset(),
    "offer_accepted": frozenset(),
    "offer_declined": frozenset(),
}


def allowed_next(current: str) -> list[str]:
    try:
        return sorted(TRANSITIONS[current])
    except KeyError:
        raise InvalidTransition(f"Unknown status {current!r}") from None


def next_status(current: str, target: str) -> str:
    if target not in allowed_next(current):
        raise InvalidTransition(f"Can't go from {current!r} to {target!r}")
    return target


def parse_command(text: str) -> dict:
    parts = text.split()
    if parts:
        parts[0] = parts[0].lower()
    match parts:
        case ["add", company, *role_words] if role_words:
            return {"action": "add", "company": company, "role": " ".join(role_words)}
        case ["move", id_text, status]:
            return {"action": "move", "id": int(id_text), "status": status}  # int() raises ValueError
        case ["list"]:
            return {"action": "list", "status": None}
        case ["list", status]:
            return {"action": "list", "status": status}
        case ["help"]:
            return {"action": "help"}
        case _:
            raise ValueError(f"Unknown command: {text!r}")


def describe_event(event: dict) -> str:
    match event:
        case {"type": "application.created", "company": str(company)}:
            return f"New application at {company}"
        case {"type": "status.changed", "to": "offer" | "offer_accepted"}:
            return "🎉 Offer!"
        case {"type": "status.changed", "to": str(status)}:
            return f"Status changed to {status}"
        case {"type": str(kind)}:
            return f"Ignored event {kind}"
        case _:
            raise ValueError("Invalid event")

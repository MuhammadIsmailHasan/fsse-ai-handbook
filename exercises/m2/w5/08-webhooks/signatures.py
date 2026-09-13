"""M2 · W5 · 08 — Webhook signature verification."""


class InvalidSignature(Exception):
    pass


def verify_signature(raw_body: bytes, header: str | None, secret: str, now: float, tolerance: int = 300) -> None:
    # YOUR CODE HERE
    raise InvalidSignature("not implemented")

"""Reference solution."""

import hashlib
import hmac


class InvalidSignature(Exception):
    pass


def verify_signature(raw_body: bytes, header: str | None, secret: str, now: float, tolerance: int = 300) -> None:
    if not header:
        raise InvalidSignature("missing signature header")
    try:
        parts = dict(item.split("=", 1) for item in header.split(","))
        timestamp = int(parts["t"])
        signature = parts["v1"]
    except (ValueError, KeyError):
        raise InvalidSignature("malformed signature header") from None

    if abs(now - timestamp) > tolerance:  # rejects replays of old requests (and clocks far in the future)
        raise InvalidSignature("timestamp outside tolerance")

    expected = hmac.new(secret.encode(), f"{timestamp}.".encode() + raw_body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):  # constant-time: no timing side channel
        raise InvalidSignature("signature mismatch")

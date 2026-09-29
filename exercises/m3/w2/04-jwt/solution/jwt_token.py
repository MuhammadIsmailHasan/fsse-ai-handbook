"""Module 3 · W2 — Sign and verify a token by hand (solution)."""

import base64
import hashlib
import hmac
import json


class TokenError(ValueError):
    pass


def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _unb64(text: str) -> bytes:
    padding = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(text + padding)


def _signature(body: str, secret: str) -> str:
    digest = hmac.new(secret.encode(), body.encode(), hashlib.sha256).digest()
    return _b64(digest)


def sign(payload: dict, secret: str) -> str:
    body = _b64(json.dumps(payload, separators=(",", ":"), sort_keys=True).encode())
    return f"{body}.{_signature(body, secret)}"


def verify(token: str, secret: str, now: int) -> dict:
    parts = token.split(".")
    if len(parts) != 2:
        raise TokenError("malformed token")
    body, sig = parts
    expected = _signature(body, secret)
    if not hmac.compare_digest(sig, expected):
        raise TokenError("bad signature")
    payload = json.loads(_unb64(body))
    if "exp" in payload and payload["exp"] <= now:
        raise TokenError("token expired")
    return payload

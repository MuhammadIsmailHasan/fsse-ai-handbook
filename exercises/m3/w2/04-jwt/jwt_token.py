"""Module 3 · W2 — Sign and verify a token by hand (stdlib only).

A minimal JWT-style token: base64(payload).base64(signature).
The signature is HMAC-SHA256 over the encoded payload, using a secret only the
server knows. Verifying recomputes the signature (catching tampering) and checks
the exp claim.

`now` is passed in so tests are deterministic.
"""

import base64
import hashlib
import hmac
import json


class TokenError(ValueError):
    """Raised for tampered, expired, or wrong-secret tokens."""


def _b64(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def _unb64(text: str) -> bytes:
    padding = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(text + padding)


def _signature(body: str, secret: str) -> str:
    digest = hmac.new(secret.encode(), body.encode(), hashlib.sha256).digest()
    return _b64(digest)


def sign(payload: dict, secret: str) -> str:
    """Return '<base64 payload>.<base64 hmac signature>'."""
    # YOUR CODE HERE
    return ""


def verify(token: str, secret: str, now: int) -> dict:
    """Return the payload if the signature is valid and the token isn't expired.

    Raise TokenError if the format is wrong, the signature doesn't match
    (tampered or wrong secret), or payload["exp"] <= now.
    """
    # YOUR CODE HERE
    return {}

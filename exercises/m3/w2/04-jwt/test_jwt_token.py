import pytest

from jwt_token import TokenError, sign, verify

SECRET = "super-secret-key"


def test_sign_verify_roundtrip():
    token = sign({"sub": 7, "exp": 100}, SECRET)
    payload = verify(token, SECRET, now=50)  # not yet expired
    assert payload["sub"] == 7


def test_expired_token_rejected():
    token = sign({"sub": 7, "exp": 100}, SECRET)
    with pytest.raises(TokenError):
        verify(token, SECRET, now=100)   # exp <= now
    with pytest.raises(TokenError):
        verify(token, SECRET, now=200)


def test_wrong_secret_rejected():
    token = sign({"sub": 7, "exp": 100}, SECRET)
    with pytest.raises(TokenError):
        verify(token, "different-secret", now=50)


def test_tampered_payload_rejected():
    token = sign({"sub": 7, "role": "user", "exp": 100}, SECRET)
    _, sig = token.split(".")
    # Forge an admin payload but keep the old signature.
    forged_body = sign({"sub": 7, "role": "admin", "exp": 100}, SECRET).split(".")[0]
    forged = f"{forged_body}.{sig}"
    with pytest.raises(TokenError):
        verify(forged, SECRET, now=50)


def test_malformed_token_rejected():
    with pytest.raises(TokenError):
        verify("not-a-valid-token", SECRET, now=50)

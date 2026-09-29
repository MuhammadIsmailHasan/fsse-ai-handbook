"""Module 3 · W2 — Auth and DB via Depends.

Build a get_current_user dependency that reads a Bearer token from the
Authorization header, and a protected GET /me that returns the user.

- No token or wrong format  → 401
- Unknown token             → 401
- Known token               → the user dict
"""

from fastapi import Depends, FastAPI, Header, HTTPException

app = FastAPI()

# Fake token store: token -> user
_TOKENS = {
    "tok-ismail": {"id": 1, "name": "Ismail"},
    "tok-sari": {"id": 2, "name": "Sari"},
}


def get_current_user(authorization: str | None = Header(default=None)) -> dict:
    """Return the user for a valid 'Bearer <token>' header, else raise 401."""
    # YOUR CODE HERE
    return {}


# YOUR CODE HERE:
# @app.get("/me") with `user = Depends(get_current_user)` returning the user dict.

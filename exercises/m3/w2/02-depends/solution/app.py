"""Module 3 · W2 — Auth and DB via Depends (solution)."""

from fastapi import Depends, FastAPI, Header, HTTPException

app = FastAPI()

_TOKENS = {
    "tok-ismail": {"id": 1, "name": "Ismail"},
    "tok-sari": {"id": 2, "name": "Sari"},
}


def get_current_user(authorization: str | None = Header(default=None)) -> dict:
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.removeprefix("Bearer ")
    user = _TOKENS.get(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user


@app.get("/me")
def me(user: dict = Depends(get_current_user)):
    return user

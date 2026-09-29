"""Module 3 · W1 — Shape output and handle errors (solution)."""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

_users: dict[int, dict] = {}
_next_id = {"value": 1}


class UserIn(BaseModel):
    name: str
    email: str
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str


@app.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: UserIn):
    user_id = _next_id["value"]
    _next_id["value"] += 1
    record = {"id": user_id, "name": user.name, "email": user.email, "password": user.password}
    _users[user_id] = record
    return record  # response_model=UserOut strips "password"


@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    record = _users.get(user_id)
    if record is None:
        raise HTTPException(status_code=404, detail="User not found")
    return record

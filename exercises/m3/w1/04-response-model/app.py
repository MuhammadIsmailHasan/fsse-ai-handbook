"""Module 3 · W1 — Shape output and handle errors.

- POST /users  → 201, returns UserOut (NO password) even though we store one.
- GET  /users/{id} → returns the user, or 404 via HTTPException if not found.

response_model filters the output to only the declared fields, so the password
can never leak.
"""

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

# Fake in-memory store: id -> full record (includes password)
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


# YOUR CODE HERE:
# 1. POST /users with response_model=UserOut, status_code=201:
#    - assign a new id, store {id, name, email, password}, return that dict.
# 2. GET /users/{user_id} with response_model=UserOut:
#    - return the stored record, or raise HTTPException(404, "User not found").

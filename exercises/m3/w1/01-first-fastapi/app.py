"""Module 3 · W1 — Your first FastAPI app.

Build two endpoints:
- GET  /health  → {"status": "ok"}
- POST /greet   → takes a typed body {"name": <str>} and returns {"message": "Hello, <name>!"}

Because the body is a Pydantic model, FastAPI validates it automatically: a
missing or wrong-typed "name" is rejected with HTTP 422 — you write no checks.
"""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class GreetIn(BaseModel):
    name: str


# YOUR CODE HERE:
# 1. @app.get("/health") returning {"status": "ok"}
# 2. @app.post("/greet") taking `body: GreetIn` and returning
#    {"message": f"Hello, {body.name}!"}

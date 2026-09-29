"""Module 3 · W1 — Validate and clean with Pydantic v2.

Build two models:
- Product: name (1..50 chars), price (> 0), stock (>= 0, default 0).
- Signup: email (must contain '@', stored lowercase), password (min 8 chars).

Let Field constraints and a field_validator do the work — no manual if-checks
outside the model.
"""

from pydantic import BaseModel, Field, field_validator


class Product(BaseModel):
    # YOUR CODE HERE:
    # name: str with min_length=1, max_length=50
    # price: float greater than 0
    # stock: int, >= 0, default 0
    pass


class Signup(BaseModel):
    # YOUR CODE HERE:
    # email: str  -> a @field_validator that requires "@" and returns v.lower()
    # password: str with min_length=8
    pass

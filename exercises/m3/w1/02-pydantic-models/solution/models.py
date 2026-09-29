"""Module 3 · W1 — Validate and clean with Pydantic v2 (solution)."""

from pydantic import BaseModel, Field, field_validator


class Product(BaseModel):
    name: str = Field(min_length=1, max_length=50)
    price: float = Field(gt=0)
    stock: int = Field(default=0, ge=0)


class Signup(BaseModel):
    email: str
    password: str = Field(min_length=8)

    @field_validator("email")
    @classmethod
    def email_has_at(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("email must contain @")
        return v.lower()

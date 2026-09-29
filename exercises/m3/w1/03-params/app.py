"""Module 3 · W1 — Path, query, and body in one API.

Build three endpoints:
- GET  /items/{item_id}   → {"item_id": <int>}          (path param)
- GET  /items             → {"q": ..., "page": ...}      (query params with defaults)
- POST /items  (body {"name": str, "price": float}) → {"name": ..., "price": ...}
"""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class ItemIn(BaseModel):
    name: str
    price: float


# YOUR CODE HERE:
# 1. GET /items/{item_id} with item_id: int → {"item_id": item_id}
# 2. GET /items with q: str | None = None, page: int = 1 → {"q": q, "page": page}
# 3. POST /items with body: ItemIn → {"name": body.name, "price": body.price}

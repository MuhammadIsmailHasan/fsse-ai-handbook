"""Module 3 · W1 — Path, query, and body in one API (solution)."""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class ItemIn(BaseModel):
    name: str
    price: float


@app.get("/items/{item_id}")
def read_item(item_id: int):
    return {"item_id": item_id}


@app.get("/items")
def list_items(q: str | None = None, page: int = 1):
    return {"q": q, "page": page}


@app.post("/items")
def create_item(body: ItemIn):
    return {"name": body.name, "price": body.price}

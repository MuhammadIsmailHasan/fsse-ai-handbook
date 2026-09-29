"""Module 3 · W1 — Your first FastAPI app (solution)."""

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class GreetIn(BaseModel):
    name: str


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/greet")
def greet(body: GreetIn):
    return {"message": f"Hello, {body.name}!"}

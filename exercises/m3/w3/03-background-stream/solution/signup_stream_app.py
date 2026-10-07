"""Module 3 · W3 — Background tasks and a streaming response (solution)."""

from collections.abc import Iterator

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI()

OUTBOX: list[str] = []


def send_welcome(email: str) -> None:
    OUTBOX.append(f"welcome:{email}")


class SignupIn(BaseModel):
    email: str


@app.post("/signup", status_code=201)
def signup(body: SignupIn, background: BackgroundTasks):
    if "@" not in body.email:
        raise HTTPException(status_code=400, detail="Invalid email")
    background.add_task(send_welcome, body.email)
    return {"email": body.email}


def word_events(text: str) -> Iterator[str]:
    for word in text.split():
        yield f"data: {word}\n\n"
    yield "data: [DONE]\n\n"


@app.get("/stream")
def stream(text: str):
    return StreamingResponse(word_events(text), media_type="text/event-stream")

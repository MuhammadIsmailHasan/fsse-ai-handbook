"""Module 3 · W3 — Background tasks and a streaming response.

1. POST /signup  body {"email": "..."}
   - email without "@"  → 400 and NOTHING is scheduled
   - otherwise          → 201 {"email": ...} right away, and the welcome email
                          is sent AFTER the response via BackgroundTasks.
2. GET /stream?text=hello big world
   - streams one Server-Sent Event per word:  "data: hello\\n\\n"
   - ends with:                               "data: [DONE]\\n\\n"
   - media type: text/event-stream
"""

from collections.abc import Iterator

from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

app = FastAPI()

OUTBOX: list[str] = []   # stands in for a real email service


def send_welcome(email: str) -> None:
    """Slow work we do NOT want the user to wait for (given — do not edit)."""
    OUTBOX.append(f"welcome:{email}")


class SignupIn(BaseModel):
    email: str


@app.post("/signup", status_code=201)
def signup(body: SignupIn, background: BackgroundTasks):
    # YOUR CODE HERE
    return {}


def word_events(text: str) -> Iterator[str]:
    """Yield 'data: <word>\\n\\n' for each word, then 'data: [DONE]\\n\\n'."""
    # YOUR CODE HERE
    yield ""


@app.get("/stream")
def stream(text: str):
    # YOUR CODE HERE: return a StreamingResponse over word_events(text)
    return {}

"""Module 3 · W3 — A small notes API (already complete — do not edit).

The app reads notes through a `get_repo` dependency. In production that is one
shared, long-lived repository. In tests we replace it with a fresh one.
"""

from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class NoteIn(BaseModel):
    text: str


class NoteRepo:
    """A tiny in-memory 'database' of notes."""

    def __init__(self) -> None:
        self._notes: dict[int, dict] = {}
        self._next_id = 1

    def add(self, text: str) -> dict:
        note = {"id": self._next_id, "text": text}
        self._notes[note["id"]] = note
        self._next_id += 1
        return note

    def get(self, note_id: int) -> dict | None:
        return self._notes.get(note_id)

    def all(self) -> list[dict]:
        return list(self._notes.values())


_SHARED_REPO = NoteRepo()  # lives as long as the process — this is the trap for tests


def get_repo() -> NoteRepo:
    return _SHARED_REPO


@app.post("/notes", status_code=201)
def create_note(body: NoteIn, repo: NoteRepo = Depends(get_repo)):
    return repo.add(body.text)


@app.get("/notes")
def list_notes(repo: NoteRepo = Depends(get_repo)):
    return repo.all()


@app.get("/notes/{note_id}")
def read_note(note_id: int, repo: NoteRepo = Depends(get_repo)):
    note = repo.get(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

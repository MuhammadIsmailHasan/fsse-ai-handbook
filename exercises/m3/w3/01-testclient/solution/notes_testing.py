"""Module 3 · W3 — Test helper: a client with an isolated repository (solution)."""

from collections.abc import Iterator
from contextlib import contextmanager

from fastapi.testclient import TestClient

from notes_app import NoteRepo, app, get_repo


@contextmanager
def client_with_fresh_repo(repo: NoteRepo | None = None) -> Iterator[TestClient]:
    fake = repo if repo is not None else NoteRepo()
    app.dependency_overrides[get_repo] = lambda: fake
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()

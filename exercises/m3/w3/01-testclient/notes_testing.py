"""Module 3 · W3 — Test helper: a client with an isolated repository.

Write `client_with_fresh_repo`. Inside the `with` block:
  - `get_repo` must be overridden so the app uses `repo` (or a brand-new
    NoteRepo() when none is given) instead of the shared one;
  - the yielded object is a TestClient for the app.
When the block ends — even if the test failed — the override must be removed,
so the next test starts clean.
"""

from collections.abc import Iterator
from contextlib import contextmanager

from fastapi.testclient import TestClient

from notes_app import NoteRepo, app, get_repo


@contextmanager
def client_with_fresh_repo(repo: NoteRepo | None = None) -> Iterator[TestClient]:
    # YOUR CODE HERE
    yield None  # type: ignore[misc]

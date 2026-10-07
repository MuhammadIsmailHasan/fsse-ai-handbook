from notes_app import NoteRepo, app, get_repo
from notes_testing import client_with_fresh_repo


def test_create_and_read_note():
    with client_with_fresh_repo() as client:
        created = client.post("/notes", json={"text": "buy milk"})
        assert created.status_code == 201
        assert created.json() == {"id": 1, "text": "buy milk"}
        assert client.get("/notes/1").json()["text"] == "buy milk"


def test_missing_note_is_404():
    with client_with_fresh_repo() as client:
        assert client.get("/notes/999").status_code == 404


def test_each_test_starts_with_an_empty_repo():
    # Two separate blocks must not share notes: both create id 1.
    with client_with_fresh_repo() as client:
        assert client.post("/notes", json={"text": "a"}).json()["id"] == 1
    with client_with_fresh_repo() as client:
        assert client.get("/notes").json() == []
        assert client.post("/notes", json={"text": "b"}).json()["id"] == 1


def test_a_prefilled_repo_is_used():
    repo = NoteRepo()
    repo.add("already here")
    with client_with_fresh_repo(repo) as client:
        assert [n["text"] for n in client.get("/notes").json()] == ["already here"]


def test_override_is_active_inside_and_removed_after():
    with client_with_fresh_repo():
        assert get_repo in app.dependency_overrides
    assert app.dependency_overrides == {}


def test_override_is_removed_even_when_the_test_body_fails():
    try:
        with client_with_fresh_repo():
            raise RuntimeError("test body blew up")
    except RuntimeError:
        pass
    assert app.dependency_overrides == {}

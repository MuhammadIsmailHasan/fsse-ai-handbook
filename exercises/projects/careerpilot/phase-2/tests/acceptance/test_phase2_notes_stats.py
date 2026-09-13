"""C5 · Notes and stats. Don't edit."""

import pytest


def test_notes_crud(client, auth, other_auth, helpers):
    company = helpers.company(client, auth)
    application = helpers.application(client, auth, company["id"])
    base = f"/api/v1/applications/{application['id']}/notes"

    first = client.post(base, json={"body": "  Recruiter call on Monday "}, headers=auth)
    assert first.status_code == 201
    note = first.get_json()["data"]
    assert note["body"] == "Recruiter call on Monday" and set(note) == {"id", "body", "created_at"}
    second = client.post(base, json={"body": "Take-home test received"}, headers=auth).get_json()["data"]
    assert [n["id"] for n in client.get(base, headers=auth).get_json()["data"]] == [second["id"], note["id"]], "newest first"

    assert client.delete(f"/api/v1/notes/{note['id']}", headers=other_auth).status_code == 404
    assert client.post(base, json={"body": "sneaky"}, headers=other_auth).status_code == 404
    assert client.delete(f"/api/v1/notes/{note['id']}", headers=auth).status_code == 204
    assert [n["id"] for n in client.get(base, headers=auth).get_json()["data"]] == [second["id"]]


@pytest.mark.parametrize("body", [{"body": ""}, {"body": "   "}, {"body": "x" * 5001}, {}])
def test_note_validation(client, auth, helpers, body):
    company = helpers.company(client, auth)
    application = helpers.application(client, auth, company["id"])
    response = client.post(f"/api/v1/applications/{application['id']}/notes", json=body, headers=auth)
    assert response.status_code == 422 and "body" in response.get_json()["error"]["fields"]


def test_stats(client, auth, other_auth, helpers):
    empty = client.get("/api/v1/stats", headers=auth).get_json()["data"]
    assert empty == {"total": 0, "active": 0, "by_status": dict.fromkeys(["saved", "applied", "screening", "interview", "offer", "accepted", "rejected", "withdrawn"], 0)}

    company = helpers.company(client, auth)
    paths = [[], [], ["applied"], ["applied", "interview"], ["applied", "interview", "offer", "accepted"], ["rejected"]]
    for path in paths:
        application = helpers.application(client, auth, company["id"])
        helpers.move(client, auth, application["id"], *path)
    other_company = helpers.company(client, other_auth)
    helpers.application(client, other_auth, other_company["id"])

    stats = client.get("/api/v1/stats", headers=auth).get_json()["data"]
    assert stats["total"] == 6 and stats["active"] == 4
    assert stats["by_status"] == {"saved": 2, "applied": 1, "screening": 0, "interview": 1, "offer": 0, "accepted": 1, "rejected": 1, "withdrawn": 0}

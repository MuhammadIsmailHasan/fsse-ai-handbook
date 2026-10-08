"""C3 · The help center: articles are chunked by `##` headings, embedded and stored."""

import pytest

from p_support import ARTICLES


def post(client, admin, **overrides):
    body = {**ARTICLES["refund-policy"], **overrides}
    return client.post("/v1/articles", json=body, headers=admin)


def test_create_returns_the_chunk_count(client, admin):
    r = post(client, admin)
    assert r.status_code == 201
    assert r.json() == {"data": {"id": "refund-policy", "title": "Refund policy", "lang": "en", "chunks": 3}}


@pytest.mark.parametrize(
    ("article", "chunks"),
    [("refund-policy", 3), ("shipping", 2), ("account-security", 1), ("kebijakan-retur", 1)],
)
def test_chunks_follow_the_second_level_headings(client, admin, article, chunks):
    r = client.post("/v1/articles", json=ARTICLES[article], headers=admin)
    assert r.json()["data"]["chunks"] == chunks


def test_text_before_the_first_heading_is_a_chunk_and_empty_sections_are_not(client, admin):
    body = "Intro text.\n\n## Empty section\n\n## Real section\nSome content here.\n\n### Not a split\nStill the same section."
    r = post(client, admin, id="x", body=body)
    assert r.json()["data"]["chunks"] == 2           # intro + "Real section" ("Empty section" has no body)


def test_an_article_without_headings_is_one_chunk(client, admin):
    assert post(client, admin, id="plain", body="Just a paragraph of text.").json()["data"]["chunks"] == 1


def test_duplicate_id_is_a_409(client, admin):
    assert post(client, admin).status_code == 201
    r = post(client, admin)
    assert r.status_code == 409 and r.json()["error"]["code"] == "article_exists"


@pytest.mark.parametrize(
    "bad",
    [
        {"id": "Has Spaces"},
        {"id": ""},
        {"id": "a" * 65},
        {"title": ""},
        {"title": "t" * 201},
        {"body": ""},
        {"lang": "fr"},
        {"surprise": 1},
    ],
)
def test_validation_errors_are_422_with_fields(client, admin, bad):
    r = post(client, admin, **bad)
    assert r.status_code == 422
    error = r.json()["error"]
    assert error["code"] == "validation_failed" and error["fields"]


def test_a_missing_field_is_named(client, admin):
    body = {k: v for k, v in ARTICLES["refund-policy"].items() if k != "title"}
    r = client.post("/v1/articles", json=body, headers=admin)
    assert r.status_code == 422 and "title" in r.json()["error"]["fields"]


def test_list_is_sorted_by_id_and_has_no_body(client, admin):
    for key in ("shipping", "refund-policy", "account-security"):
        client.post("/v1/articles", json=ARTICLES[key], headers=admin)
    data = client.get("/v1/articles", headers=admin).json()["data"]
    assert [a["id"] for a in data] == ["account-security", "refund-policy", "shipping"]
    assert data[1] == {"id": "refund-policy", "title": "Refund policy", "lang": "en", "chunks": 3}


def test_delete_removes_the_article(client, admin):
    post(client, admin)
    assert client.delete("/v1/articles/refund-policy", headers=admin).status_code == 204
    assert client.get("/v1/articles", headers=admin).json()["data"] == []
    assert client.delete("/v1/articles/refund-policy", headers=admin).status_code == 404


def test_a_deleted_article_is_no_longer_retrieved(kb, admin, customer, llm):
    kb.delete("/v1/articles/refund-policy", headers=admin)
    kb.delete("/v1/articles/kebijakan-retur", headers=admin)
    r = kb.post("/v1/chat", json={"message": "Tell me about refund timing"}, headers=customer)
    assert r.json()["data"]["sources"] == []
    assert llm.calls == []                            # nothing relevant is left, so the model is not called


def test_the_same_id_can_be_created_again_after_delete(client, admin):
    post(client, admin)
    client.delete("/v1/articles/refund-policy", headers=admin)
    assert post(client, admin).status_code == 201

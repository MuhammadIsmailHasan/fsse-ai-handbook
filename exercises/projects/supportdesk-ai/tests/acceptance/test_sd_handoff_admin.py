"""C7 · Human handoff, feedback and the admin view."""

import pytest

from p_support import text, tool_call

HANDOFF = "Sure. I am connecting you with a support agent."


def chat(client, headers, message, conversation_id=None):
    body = {"message": message}
    if conversation_id:
        body["conversation_id"] = conversation_id
    return client.post("/v1/chat", json=body, headers=headers)


@pytest.mark.parametrize("message", ["I want to talk to a human", "Connect me to an agent", "tolong sambungkan ke manusia", "bisa bicara dengan petugas?"])
def test_asking_for_a_person_skips_the_model(kb, customer, llm, message):
    data = chat(kb, customer, message).json()["data"]
    assert data["answer"] == HANDOFF and data["handoff"] is True and data["refused"] is False
    assert llm.calls == []


def test_words_that_only_contain_the_trigger_do_not_count(kb, customer, llm):
    llm.replies = [text("Seven days [1].")]
    data = chat(kb, customer, "My refund agentless humane? How long do refunds take").json()["data"]
    assert data["handoff"] is False and len(llm.calls) == 1


def test_the_model_can_ask_for_a_human(kb, customer, admin, llm):
    llm.replies = [tool_call("request_human", {"reason": "customer is upset"}), text("I have asked an agent to join.")]
    data = chat(kb, customer, "This is unacceptable, my refund timing is too long").json()["data"]
    assert data["handoff"] is True and data["tool_calls"] == ["request_human"]
    handoffs = kb.get("/v1/admin/handoffs", headers=admin).json()["data"]
    assert len(handoffs) == 1 and handoffs[0]["reason"] == "model_requested"


def test_handoff_queue_entries(kb, customer, admin, llm):
    cid = chat(kb, customer, "connect me to an agent").json()["data"]["conversation_id"]
    entries = kb.get("/v1/admin/handoffs", headers=admin).json()["data"]
    assert entries == [{"id": "h-1", "conversation_id": cid, "user": "user-1", "reason": "user_requested", "status": "open"}]


def test_reasons_for_the_other_handoffs(kb, customer, customer2, admin, llm):
    chat(kb, customer, "What is the capital of France?")                                  # nothing relevant
    llm.replies = [text("I do not know the answer to that.")]
    chat(kb, customer2, "How long do refunds take?")                                      # the model does not know
    reasons = sorted(h["reason"] for h in kb.get("/v1/admin/handoffs", headers=admin).json()["data"])
    assert reasons == ["no_answer", "unknown_answer"]


def test_one_open_handoff_per_conversation(kb, customer, admin, llm):
    cid = chat(kb, customer, "connect me to an agent").json()["data"]["conversation_id"]
    chat(kb, customer, "I said, connect me to an agent", cid)
    assert len(kb.get("/v1/admin/handoffs", headers=admin).json()["data"]) == 1


def test_resolving_a_handoff(kb, customer, admin, llm):
    chat(kb, customer, "connect me to an agent")
    r = kb.post("/v1/admin/handoffs/h-1/resolve", headers=admin)
    assert r.status_code == 200 and r.json()["data"]["status"] == "resolved"
    assert kb.get("/v1/admin/handoffs", headers=admin).json()["data"][0]["status"] == "resolved"
    assert kb.post("/v1/admin/handoffs/h-99/resolve", headers=admin).status_code == 404


def test_a_new_handoff_can_open_after_the_old_one_is_resolved(kb, customer, admin, llm):
    cid = chat(kb, customer, "connect me to an agent").json()["data"]["conversation_id"]
    kb.post("/v1/admin/handoffs/h-1/resolve", headers=admin)
    chat(kb, customer, "connect me to an agent again", cid)
    assert [h["status"] for h in kb.get("/v1/admin/handoffs", headers=admin).json()["data"]] == ["resolved", "open"]


def test_handoff_list_can_filter_by_status(kb, customer, customer2, admin, llm):
    chat(kb, customer, "connect me to an agent")
    chat(kb, customer2, "connect me to a human")
    kb.post("/v1/admin/handoffs/h-1/resolve", headers=admin)
    open_only = kb.get("/v1/admin/handoffs?status=open", headers=admin).json()["data"]
    assert [h["id"] for h in open_only] == ["h-2"]
    assert kb.get("/v1/admin/handoffs?status=nonsense", headers=admin).status_code == 422


def test_feedback_is_stored(kb, customer, admin, llm):
    llm.replies = [text("Seven days [1].")]
    cid = chat(kb, customer, "How long do refunds take?").json()["data"]["conversation_id"]
    r = kb.post("/v1/feedback", json={"conversation_id": cid, "rating": "down", "comment": "too slow"}, headers=customer)
    assert r.status_code == 201 and r.json()["data"]["id"] == "f-1"
    transcript = kb.get(f"/v1/admin/conversations/{cid}", headers=admin).json()["data"]
    assert transcript["feedback"] == [{"id": "f-1", "rating": "down", "comment": "too slow"}]


def test_feedback_validation_and_ownership(kb, customer, customer2, llm):
    llm.replies = [text("Seven days [1].")]
    cid = chat(kb, customer, "How long do refunds take?").json()["data"]["conversation_id"]
    assert kb.post("/v1/feedback", json={"conversation_id": cid, "rating": "meh"}, headers=customer).status_code == 422
    assert kb.post("/v1/feedback", json={"conversation_id": cid, "rating": "up", "comment": "x" * 501}, headers=customer).status_code == 422
    assert kb.post("/v1/feedback", json={"conversation_id": cid, "rating": "up", "extra": 1}, headers=customer).status_code == 422
    assert kb.post("/v1/feedback", json={"conversation_id": cid, "rating": "up"}, headers=customer2).status_code == 404
    assert kb.post("/v1/feedback", json={"conversation_id": "c-nope", "rating": "up"}, headers=customer).status_code == 404
    assert kb.post("/v1/feedback", json={"rating": "up"}, headers=customer).status_code == 422
    assert kb.post("/v1/feedback", json={"conversation_id": cid, "rating": "up"}, headers={}).status_code == 401


def make_conversations(kb, llm, customer, customer2):
    llm.replies = [text("Seven days [1].")]
    good = chat(kb, customer, "How long do refunds take?").json()["data"]["conversation_id"]
    kb.post("/v1/feedback", json={"conversation_id": good, "rating": "up"}, headers=customer)
    llm.replies = [text("Wrong answer [1].")]
    bad = chat(kb, customer2, "How long do refunds take?").json()["data"]["conversation_id"]
    kb.post("/v1/feedback", json={"conversation_id": bad, "rating": "down", "comment": "wrong"}, headers=customer2)
    handoff = chat(kb, customer, "connect me to an agent").json()["data"]["conversation_id"]
    return good, bad, handoff


def test_admin_conversation_list_and_filters(kb, customer, customer2, admin, llm):
    good, bad, handoff = make_conversations(kb, llm, customer, customer2)
    everything = kb.get("/v1/admin/conversations", headers=admin).json()["data"]
    assert [c["id"] for c in everything] == [good, bad, handoff]
    first = everything[0]
    assert first == {"id": good, "user": "user-1", "messages": 2, "handoff": False, "ratings": ["up"], "last_answer": "Seven days [1]."}
    assert [c["id"] for c in kb.get("/v1/admin/conversations?rating=down", headers=admin).json()["data"]] == [bad]
    assert [c["id"] for c in kb.get("/v1/admin/conversations?handoff=true", headers=admin).json()["data"]] == [handoff]
    assert [c["id"] for c in kb.get("/v1/admin/conversations?handoff=false", headers=admin).json()["data"]] == [good, bad]
    assert [c["id"] for c in kb.get("/v1/admin/conversations?limit=2", headers=admin).json()["data"]] == [good, bad]


def test_admin_filter_validation(kb, admin):
    assert kb.get("/v1/admin/conversations?rating=meh", headers=admin).status_code == 422
    assert kb.get("/v1/admin/conversations?limit=0", headers=admin).status_code == 422
    assert kb.get("/v1/admin/conversations?handoff=maybe", headers=admin).status_code == 422


def test_admin_transcript(kb, customer, admin, llm):
    llm.replies = [text("Seven days [1].")]
    cid = chat(kb, customer, "How long do refunds take?").json()["data"]["conversation_id"]
    transcript = kb.get(f"/v1/admin/conversations/{cid}", headers=admin).json()["data"]
    assert transcript["id"] == cid and transcript["user"] == "user-1" and transcript["handoff"] is False
    assert [m["role"] for m in transcript["messages"]] == ["user", "assistant"]
    assert transcript["messages"][0]["content"] == "How long do refunds take?"
    assert kb.get("/v1/admin/conversations/c-nope", headers=admin).status_code == 404


def test_failed_answers_view_is_the_union_of_down_ratings_and_handoffs(kb, customer, customer2, admin, llm):
    good, bad, handoff = make_conversations(kb, llm, customer, customer2)
    failed = kb.get("/v1/admin/conversations?failed=true", headers=admin).json()["data"]
    assert [c["id"] for c in failed] == [bad, handoff]

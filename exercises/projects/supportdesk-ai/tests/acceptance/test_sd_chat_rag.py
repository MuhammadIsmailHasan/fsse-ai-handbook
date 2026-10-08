"""C4 · POST /v1/chat — retrieval, grounded prompt, citations, conversations."""

import pytest

from p_support import text

NO_ANSWER = "I could not find this in our help center. A support agent will help you."


def chat(client, headers, message, conversation_id=None):
    body = {"message": message}
    if conversation_id:
        body["conversation_id"] = conversation_id
    return client.post("/v1/chat", json=body, headers=headers)


def test_happy_path_answer_and_cited_sources(kb, customer, llm):
    llm.replies = [text("Refunds are paid back within 7 days after we receive the item [1].")]
    r = chat(kb, customer, "How long do refunds take?")
    assert r.status_code == 200
    data = r.json()["data"]
    assert data["answer"] == "Refunds are paid back within 7 days after we receive the item [1]."
    assert data["handoff"] is False and data["refused"] is False and data["tool_calls"] == []
    assert data["conversation_id"]
    assert len(data["sources"]) == 1
    source = data["sources"][0]
    assert source["n"] == 1 and source["article_id"] == "refund-policy"
    assert source["title"] == "Refund policy" and source["heading"] == "Refund timing"
    assert r.headers["X-Request-ID"]


def test_the_prompt_is_grounded_and_numbered(kb, customer, llm):
    llm.replies = [text("Seven days [1].")]
    chat(kb, customer, "How long do refunds take?")
    assert len(llm.calls) == 1
    system = llm.calls[0]["system"]
    assert "ONLY" in system and "[1]" in system
    assert "Refund policy" in system and "Refunds are paid back within 7 days" in system
    assert "<sources>" in system and "</sources>" in system


def test_the_users_message_is_wrapped_as_data(kb, customer, llm):
    llm.replies = [text("Seven days [1].")]
    chat(kb, customer, "How long do refunds take?")
    last = llm.calls[0]["messages"][-1]
    assert last["role"] == "user"
    assert "<user_message>" in last["content"] and "How long do refunds take?" in last["content"]
    assert "</user_message>" in last["content"]


def test_sources_list_only_the_cited_numbers_in_citation_order(kb, customer, llm):
    llm.replies = [text("Free shipping above Rp 200.000 [2]. Refund in 7 days [1].")]
    r = chat(kb, customer, "How long do refunds take and what are the shipping costs for my refund")
    data = r.json()["data"]
    numbers = [s["n"] for s in data["sources"]]
    assert numbers == [2, 1]
    prompt = llm.calls[0]["system"]
    assert "[2]" in prompt                                      # at least two sources were offered


def test_an_answer_without_any_citation_is_allowed(kb, customer, llm):
    llm.replies = [text("Happy to help with that.")]
    data = chat(kb, customer, "How long do refunds take?").json()["data"]
    assert data["answer"] == "Happy to help with that." and data["sources"] == []


def test_a_citation_to_a_missing_source_is_retried_once(kb, customer, llm):
    llm.replies = [text("Refunds take 30 days [9]."), text("Refunds are paid back within 7 days [1].")]
    data = chat(kb, customer, "How long do refunds take?").json()["data"]
    assert len(llm.calls) == 2
    assert data["answer"] == "Refunds are paid back within 7 days [1]."
    retry = llm.calls[1]["messages"]
    assert retry[-2]["role"] == "assistant" and "[9]" in retry[-2]["content"]
    assert retry[-1]["role"] == "user" and "1" in retry[-1]["content"]
    assert data["handoff"] is False


def test_two_bad_citations_in_a_row_give_the_safe_answer_and_a_handoff(kb, customer, llm):
    llm.replies = [text("Refunds take 30 days [9]."), text("Still wrong [7].")]
    data = chat(kb, customer, "How long do refunds take?").json()["data"]
    assert len(llm.calls) == 2
    assert data["answer"] == NO_ANSWER and data["sources"] == [] and data["handoff"] is True


def test_nothing_relevant_means_no_model_call_and_a_handoff(kb, customer, llm):
    data = chat(kb, customer, "What is the capital of France?").json()["data"]
    assert llm.calls == []
    assert data["answer"] == NO_ANSWER and data["sources"] == [] and data["handoff"] is True
    assert data["refused"] is False


def test_an_i_do_not_know_answer_triggers_a_handoff(kb, customer, llm):
    llm.replies = [text("I do not know the exact refund fee for your bank.")]
    data = chat(kb, customer, "How long do refunds take?").json()["data"]
    assert data["handoff"] is True


def test_indonesian_questions_find_the_indonesian_article(kb, customer, llm):
    llm.replies = [text("Refund dibayarkan dalam 7 hari [1].")]
    data = chat(kb, customer, "Berapa lama refund diproses?").json()["data"]
    system = llm.calls[0]["system"]
    assert "Kebijakan retur" in system
    assert data["sources"] and data["sources"][0]["article_id"] in ("kebijakan-retur", "refund-policy")


def test_top_k_limits_the_number_of_sources(build, customer):
    small, fakes = build(top_k=1)
    fakes.llm.replies = [text("Seven days [1].")]
    small.post("/v1/chat", json={"message": "How long do refunds take?"}, headers=customer)
    system = fakes.llm.calls[0]["system"]
    assert "[1]" in system and "[2]" not in system


def test_min_score_can_make_everything_irrelevant(build, customer):
    strict, fakes = build(min_score=0.99)
    data = strict.post("/v1/chat", json={"message": "How long do refunds take?"}, headers=customer).json()["data"]
    assert fakes.llm.calls == [] and data["answer"] == NO_ANSWER


def test_a_conversation_keeps_its_history(kb, customer, llm):
    llm.replies = [text("Seven days [1]."), text("Yes, the item must be unused [1].")]
    first = chat(kb, customer, "How long do refunds take?").json()["data"]
    second = chat(kb, customer, "And do refund conditions apply to the item?", first["conversation_id"]).json()["data"]
    assert second["conversation_id"] == first["conversation_id"]
    messages = llm.calls[1]["messages"]
    assert [m["role"] for m in messages] == ["user", "assistant", "user"]
    assert "How long do refunds take?" in messages[0]["content"]
    assert messages[1]["content"] == "Seven days [1]."
    assert "refund conditions" in messages[2]["content"]


def test_only_the_last_ten_messages_of_history_are_sent(kb, customer, llm):
    first = None
    for i in range(8):
        llm.replies = [text(f"Answer {i} [1].")]
        r = chat(kb, customer, f"How long do refunds take? (round {i})", first)
        first = first or r.json()["data"]["conversation_id"]
    assert len(llm.calls[-1]["messages"]) == 9           # the last 10 including the new one; a leading assistant message is dropped
    assert llm.calls[-1]["messages"][0]["role"] == "user"


def test_a_conversation_belongs_to_one_user(kb, customer, customer2, llm):
    llm.replies = [text("Seven days [1].")]
    cid = chat(kb, customer, "How long do refunds take?").json()["data"]["conversation_id"]
    r = chat(kb, customer2, "How long do refunds take?", cid)
    assert r.status_code == 404 and r.json()["error"]["code"] == "not_found"
    assert chat(kb, customer, "How long do refunds take?", "c-does-not-exist").status_code == 404


@pytest.mark.parametrize(
    "body",
    [{}, {"message": ""}, {"message": "   "}, {"message": "x" * 2001}, {"message": 5}, {"message": "hi", "extra": 1},
     {"message": "hi", "conversation_id": 7}],
)
def test_invalid_chat_bodies_are_422(kb, customer, body):
    r = kb.post("/v1/chat", json=body, headers=customer)
    assert r.status_code == 422 and r.json()["error"]["code"] == "validation_failed"


def test_message_is_trimmed(kb, customer, llm):
    llm.replies = [text("Seven days [1].")]
    chat(kb, customer, "   How long do refunds take?   ")
    assert "<user_message>\nHow long do refunds take?\n</user_message>" in llm.calls[0]["messages"][-1]["content"]

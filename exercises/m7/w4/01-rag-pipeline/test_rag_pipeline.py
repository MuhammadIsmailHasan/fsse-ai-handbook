from rag_pipeline import NO_ANSWER, answer, build_prompt, estimate_tokens


def chunk(i, text="x" * 40, score=0.9, source="faq.md"):
    return {"id": f"c{i}", "text": text, "score": score, "source": source}


def test_estimate_tokens():
    assert estimate_tokens("") == 0 and estimate_tokens("abcde") == 2


def test_prompt_layout_is_exact():
    chunks = [chunk(1, "Refunds take 7 days.", source="refund.md"), chunk(2, "Shipping is free.", source="ship.md")]
    prompt, used = build_prompt("How long is a refund?", chunks, 1000)
    assert prompt == (
        "Answer the question using ONLY the sources below. Cite them like [1], [2].\n"
        "If the sources do not contain the answer, say you do not know.\n\n"
        "<sources>\n"
        "[1] (refund.md)\n"
        "Refunds take 7 days.\n\n"
        "[2] (ship.md)\n"
        "Shipping is free.\n"
        "</sources>\n\n"
        "Question: How long is a refund?"
    )
    assert used == chunks


def test_token_budget_stops_at_the_first_chunk_that_does_not_fit():
    chunks = [chunk(1, "a" * 40), chunk(2, "b" * 400), chunk(3, "c" * 4)]       # 10, 100, 1 tokens
    prompt, used = build_prompt("q", chunks, 50)
    assert [c["id"] for c in used] == ["c1"]            # c3 would fit but c2 broke the order
    assert "cccc" not in prompt                                   # the small c3 text is not in the prompt


def test_budget_is_on_the_total():
    chunks = [chunk(i, "a" * 40) for i in range(1, 6)]   # 10 tokens each
    _, used = build_prompt("q", chunks, 30)
    assert len(used) == 3
    _, used = build_prompt("q", chunks, 29)
    assert len(used) == 2


def test_empty_sources_block_when_nothing_fits():
    prompt, used = build_prompt("q", [chunk(1, "a" * 400)], 10)
    assert used == [] and "<sources>\n</sources>" in prompt


def test_answer_happy_path():
    seen = {}

    def retriever(question, k):
        seen["k"] = k
        return [chunk(1, "Refunds take 7 days.", 0.9, "refund.md"), chunk(2, "Shipping is free.", 0.8, "ship.md")]

    def llm(prompt):
        seen["prompt"] = prompt
        return "Seven days [1]."

    result = answer("How long?", retriever, llm, k=2)
    assert seen["k"] == 2
    assert result == {
        "answer": "Seven days [1].",
        "sources": [{"n": 1, "id": "c1", "source": "refund.md"}, {"n": 2, "id": "c2", "source": "ship.md"}],
        "used_llm": True,
    }
    assert "Refunds take 7 days." in seen["prompt"]


def test_low_scores_are_dropped_and_the_model_is_not_called_when_nothing_is_left():
    calls = []
    result = answer("q", lambda q, k: [chunk(1, score=0.2), chunk(2, score=0.1)], lambda p: calls.append(p) or "x", min_score=0.5)
    assert result == {"answer": NO_ANSWER, "sources": [], "used_llm": False}
    assert calls == []


def test_min_score_keeps_the_good_ones_only():
    seen = {}
    result = answer("q", lambda q, k: [chunk(1, "good", 0.9), chunk(2, "bad", 0.2)], lambda p: seen.setdefault("p", p) and "ok", min_score=0.5)
    assert [s["id"] for s in result["sources"]] == ["c1"]
    assert "bad" not in seen["p"]


def test_retriever_returns_nothing():
    result = answer("q", lambda q, k: [], lambda p: "should not run")
    assert result["used_llm"] is False and result["answer"] == NO_ANSWER


def test_when_no_chunk_fits_the_budget_the_model_is_not_called():
    calls = []
    result = answer("q", lambda q, k: [chunk(1, "a" * 4000)], lambda p: calls.append(p) or "x", max_context_tokens=10)
    assert result["used_llm"] is False and calls == []


def test_sources_listed_are_only_those_in_the_prompt():
    chunks = [chunk(1, "a" * 40), chunk(2, "b" * 40), chunk(3, "c" * 40)]
    result = answer("q", lambda q, k: chunks, lambda p: "ok", max_context_tokens=20)
    assert [s["n"] for s in result["sources"]] == [1, 2]

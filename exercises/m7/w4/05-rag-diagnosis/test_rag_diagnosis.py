import pytest

from rag_diagnosis import CATEGORIES, FIXES, diagnose, plan, summarize


def trace(**kw):
    base = {
        "question": "q",
        "relevant_ids": ["r1"],
        "retrieved_ids": ["r1", "x"],
        "prompt_ids": ["r1", "x"],
        "answer_is_correct": True,
        "answer_is_grounded": True,
        "refused": False,
    }
    base.update(kw)
    return base


def test_ok():
    assert diagnose(trace()) == "ok"


def test_unanswerable_question():
    assert diagnose(trace(relevant_ids=[], refused=True)) == "correct_refusal"
    assert diagnose(trace(relevant_ids=[], refused=False)) == "hallucinated_answer"


def test_retrieval_miss_beats_everything_else():
    assert diagnose(trace(retrieved_ids=["x", "y"], prompt_ids=["x"])) == "retrieval_miss"
    assert diagnose(trace(retrieved_ids=[], prompt_ids=[], refused=True)) == "retrieval_miss"
    assert diagnose(trace(retrieved_ids=["x"], prompt_ids=["x"], answer_is_correct=False)) == "retrieval_miss"


def test_found_but_dropped_before_the_prompt():
    assert diagnose(trace(retrieved_ids=["x", "y", "r1"], prompt_ids=["x", "y"])) == "dropped_before_prompt"
    assert diagnose(trace(retrieved_ids=["x", "r1"], prompt_ids=["x"], refused=True)) == "dropped_before_prompt"


def test_wrong_refusal():
    assert diagnose(trace(refused=True, answer_is_correct=False)) == "wrong_refusal"


def test_not_used():
    assert diagnose(trace(answer_is_correct=False)) == "not_used"
    assert diagnose(trace(answer_is_correct=False, answer_is_grounded=False)) == "not_used"


def test_ungrounded_even_when_correct():
    assert diagnose(trace(answer_is_grounded=False)) == "ungrounded"


def test_each_category_is_reachable():
    cases = [
        trace(),
        trace(relevant_ids=[], refused=True),
        trace(refused=True),
        trace(retrieved_ids=[], prompt_ids=[]),
        trace(retrieved_ids=["r1"], prompt_ids=[]),
        trace(answer_is_correct=False),
        trace(answer_is_grounded=False),
        trace(relevant_ids=[]),
    ]
    assert sorted(diagnose(t) for t in cases) == sorted(CATEGORIES)


def make_traces():
    return [
        trace(),
        trace(),
        trace(relevant_ids=[], refused=True),
        trace(retrieved_ids=[], prompt_ids=[]),
        trace(retrieved_ids=[], prompt_ids=[]),
        trace(retrieved_ids=[], prompt_ids=[]),
        trace(answer_is_correct=False),
        trace(relevant_ids=[]),
        trace(retrieved_ids=["r1"], prompt_ids=[]),
    ]


def test_summarize():
    s = summarize(make_traces())
    assert s["total"] == 9
    assert s["counts"] == {
        "ok": 2, "correct_refusal": 1, "wrong_refusal": 0, "retrieval_miss": 3,
        "dropped_before_prompt": 1, "not_used": 1, "ungrounded": 0, "hallucinated_answer": 1,
    }
    assert set(s["counts"]) == set(CATEGORIES)
    # answerable = 7 (two have empty relevant_ids); retrieval hit in 4 of them
    assert s["retrieval_recall"] == pytest.approx(4 / 7)
    assert s["worst"] == "retrieval_miss"


def test_summarize_edge_cases():
    s = summarize([])
    assert s["total"] == 0 and s["retrieval_recall"] == 1.0 and s["worst"] is None
    assert summarize([trace(), trace(relevant_ids=[], refused=True)])["worst"] is None
    assert summarize([trace(relevant_ids=[], refused=True)])["retrieval_recall"] == 1.0


def test_worst_ties_go_to_the_earlier_category():
    traces = [trace(refused=True), trace(retrieved_ids=[], prompt_ids=[])]       # wrong_refusal, retrieval_miss (1 each)
    assert summarize(traces)["worst"] == "wrong_refusal"


def test_plan_sorted_by_count():
    lines = plan(make_traces())
    assert lines == [
        f"retrieval_miss (3): {FIXES['retrieval_miss']}",
        f"dropped_before_prompt (1): {FIXES['dropped_before_prompt']}",
        f"not_used (1): {FIXES['not_used']}",
        f"hallucinated_answer (1): {FIXES['hallucinated_answer']}",
    ]


def test_plan_without_failures():
    assert plan([trace(), trace(relevant_ids=[], refused=True)]) == []
    assert plan([]) == []

import pytest

from retrieval_tools import cosine, drop_near_duplicates, jaccard, lost_in_the_middle_order, mmr, rerank


def cand(id, vector, text="", score=0.0):
    return {"id": id, "text": text or id, "vector": vector, "score": score}


def test_cosine():
    assert cosine([1, 0], [1, 0]) == pytest.approx(1.0)
    assert cosine([1, 0], [0, 1]) == pytest.approx(0.0)
    assert cosine([0, 0], [1, 1]) == 0.0


def test_mmr_with_lambda_1_is_pure_relevance():
    q = [1.0, 0.0]
    cands = [cand("a", [1.0, 0.0]), cand("a2", [0.99, 0.1]), cand("b", [0.6, 0.8])]
    assert [c["id"] for c in mmr(q, cands, 3, lambda_=1.0)] == ["a", "a2", "b"]


def test_mmr_skips_a_near_copy_for_something_different():
    q = [1.0, 0.0]
    cands = [cand("a", [1.0, 0.0]), cand("a_copy", [0.999, 0.01]), cand("b", [0.6, 0.8])]
    picked = [c["id"] for c in mmr(q, cands, 2, lambda_=0.3)]
    assert [c["id"] for c in mmr(q, cands, 2, lambda_=0.9)] == ["a", "a_copy"]   # high lambda: relevance wins
    assert picked == ["a", "b"]


def test_mmr_k_larger_than_candidates_and_empty():
    cands = [cand("a", [1.0, 0.0]), cand("b", [0.0, 1.0])]
    assert len(mmr([1.0, 0.0], cands, 10)) == 2
    assert mmr([1.0, 0.0], [], 3) == []


def test_mmr_does_not_change_the_input_and_ties_use_input_order():
    cands = [cand("x", [1.0, 0.0]), cand("y", [1.0, 0.0])]
    snapshot = list(cands)
    result = mmr([1.0, 0.0], cands, 1)
    assert cands == snapshot and result[0]["id"] == "x"


def test_jaccard():
    assert jaccard("a b c", "b c d") == pytest.approx(2 / 4)
    assert jaccard("Same words", "same WORDS!") == 1.0
    assert jaccard("", "") == 1.0
    assert jaccard("a", "b") == 0.0
    assert jaccard("a a a b", "a b") == 1.0           # sets, not counts


def test_drop_near_duplicates():
    chunks = [
        {"id": "1", "text": "Refunds are paid in 7 days after we receive the item"},
        {"id": "2", "text": "refunds are paid in 7 days after we receive the item."},
        {"id": "3", "text": "Shipping to Papua takes up to 10 days"},
        {"id": "4", "text": "Refunds are paid in 7 days after we receive the returned item"},
    ]
    assert [c["id"] for c in drop_near_duplicates(chunks, 0.8)] == ["1", "3"]


def test_drop_near_duplicates_threshold_edge():
    chunks = [{"id": "1", "text": "a b c d"}, {"id": "2", "text": "a b c e"}]        # jaccard = 3/5 = 0.6
    assert len(drop_near_duplicates(chunks, 0.6)) == 1       # >= threshold is a duplicate
    assert len(drop_near_duplicates(chunks, 0.61)) == 2


def test_lost_in_the_middle_order():
    letters = lambda items: [c["id"] for c in lost_in_the_middle_order([{"id": x} for x in items])]
    assert letters("abcde") == ["a", "c", "e", "d", "b"]
    assert letters("ab") == ["a", "b"]
    assert letters("abcd") == ["a", "c", "d", "b"]
    assert letters("a") == ["a"]
    assert letters("") == []


def test_rerank_orders_by_the_scorer_and_keeps_the_top_n():
    cands = [{"id": "a", "text": "cat"}, {"id": "b", "text": "refund policy"}, {"id": "c", "text": "refund"}]
    scorer = lambda q, t: sum(w in t for w in q.split())
    result = rerank("refund policy", cands, scorer, 2)
    assert [c["id"] for c in result] == ["b", "c"]
    assert result[0]["rerank_score"] == 2


def test_rerank_is_stable_and_calls_the_scorer_once_per_candidate():
    calls = []

    def scorer(q, t):
        calls.append(t)
        return 1.0

    cands = [{"id": str(i), "text": f"t{i}"} for i in range(5)]
    result = rerank("q", cands, scorer, 3)
    assert [c["id"] for c in result] == ["0", "1", "2"]
    assert len(calls) == 5


def test_rerank_does_not_change_the_input():
    cands = [{"id": "a", "text": "x"}]
    rerank("q", cands, lambda q, t: 5.0, 1)
    assert "rerank_score" not in cands[0]

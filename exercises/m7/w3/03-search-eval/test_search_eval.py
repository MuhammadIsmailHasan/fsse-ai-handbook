import pytest

from search_eval import chunk_text, evaluate, precision_at_k, recall_at_k, reciprocal_rank


def words(n):
    return " ".join(f"w{i}" for i in range(n))


def test_chunk_example_from_the_docs():
    assert chunk_text(words(10), 4, 1) == ["w0 w1 w2 w3", "w3 w4 w5 w6", "w6 w7 w8 w9"]


def test_chunks_without_overlap():
    assert chunk_text(words(5), 2) == ["w0 w1", "w2 w3", "w4"]


def test_no_extra_tiny_chunk_when_the_last_chunk_already_reaches_the_end():
    assert chunk_text(words(7), 4, 1) == ["w0 w1 w2 w3", "w3 w4 w5 w6"]


def test_text_shorter_than_one_chunk():
    assert chunk_text("just three words", 10, 2) == ["just three words"]


def test_empty_and_whitespace_text():
    assert chunk_text("", 5) == []
    assert chunk_text("   \n\t ", 5) == []


def test_whitespace_is_normalised():
    assert chunk_text("a   b\n\nc\td", 2) == ["a b", "c d"]


def test_bad_arguments():
    for size, overlap in ((0, 0), (-1, 0), (4, 4), (4, 5), (4, -1)):
        with pytest.raises(ValueError):
            chunk_text("a b c", size, overlap)


def test_every_word_is_covered_and_overlap_is_respected():
    text = words(103)
    chunks = chunk_text(text, 10, 3)
    assert all(len(c.split()) <= 10 for c in chunks)
    covered = set()
    for c in chunks:
        covered |= set(c.split())
    assert covered == set(text.split())
    for a, b in zip(chunks, chunks[1:]):
        assert a.split()[-3:] == b.split()[:3]


def test_precision_at_k():
    ranked = ["a", "b", "c", "d"]
    assert precision_at_k(ranked, {"a", "c"}, 2) == 0.5
    assert precision_at_k(ranked, {"a", "c"}, 4) == 0.5
    assert precision_at_k(["a"], {"a"}, 4) == 0.25        # a short list is punished
    with pytest.raises(ValueError):
        precision_at_k(ranked, {"a"}, 0)


def test_recall_at_k():
    ranked = ["a", "b", "c", "d"]
    assert recall_at_k(ranked, {"a", "d"}, 2) == 0.5
    assert recall_at_k(ranked, {"a", "d"}, 4) == 1.0
    assert recall_at_k(ranked, {"z"}, 4) == 0.0
    assert recall_at_k(ranked, set(), 4) == 1.0


def test_reciprocal_rank():
    assert reciprocal_rank(["x", "y", "a"], {"a", "b"}) == pytest.approx(1 / 3)
    assert reciprocal_rank(["a", "x"], {"a"}) == 1.0
    assert reciprocal_rank(["x", "y"], {"a"}) == 0.0
    assert reciprocal_rank([], {"a"}) == 0.0


def test_evaluate():
    index = {
        "reset password": ["pw", "login", "faq"],
        "refund": ["delivery", "returns", "refund-policy"],
        "invoice": ["faq", "delivery", "login"],
    }
    cases = [
        {"query": "reset password", "relevant": {"pw", "login"}},
        {"query": "refund", "relevant": {"refund-policy"}},
        {"query": "invoice", "relevant": {"invoice-doc"}},
    ]
    result = evaluate(lambda q: index[q], cases, k=3)
    assert result["precision@k"] == pytest.approx((2 / 3 + 1 / 3 + 0) / 3)
    assert result["recall@k"] == pytest.approx((1.0 + 1.0 + 0.0) / 3)
    assert result["mrr"] == pytest.approx((1.0 + 1 / 3 + 0.0) / 3)
    assert result["misses"] == ["invoice"]


def test_evaluate_k_changes_what_counts_as_a_miss():
    cases = [{"query": "q", "relevant": {"c"}}]
    search = lambda q: ["a", "b", "c"]
    assert evaluate(search, cases, k=2)["misses"] == ["q"]
    assert evaluate(search, cases, k=3)["misses"] == []


def test_evaluate_without_cases():
    assert evaluate(lambda q: [], []) == {"precision@k": 0.0, "recall@k": 0.0, "mrr": 0.0, "misses": []}

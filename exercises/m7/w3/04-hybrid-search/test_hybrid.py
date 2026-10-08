import math

import pytest

from hybrid import bm25_scores, hybrid_search, min_max, reciprocal_rank_fusion, tokenize, weighted_fusion


def test_tokenize():
    assert tokenize("Order #A-123, shipped!") == ["order", "a", "123", "shipped"]
    assert tokenize("") == []
    assert tokenize("the the THE") == ["the", "the", "the"]


def test_bm25_single_document_exact_value():
    # N=1, n=1: idf = ln(1 + 0.5/1.5); tf=1, dl=avgdl=1: score = idf * 2.5 / (1 + 1.5) = idf
    assert bm25_scores("a", ["a"]) == [pytest.approx(math.log(1 + 0.5 / 1.5))]


def test_bm25_no_overlap_is_zero_and_empty_cases():
    assert bm25_scores("zebra", ["apple pie", "banana"]) == [0.0, 0.0]
    assert bm25_scores("apple", []) == []
    assert bm25_scores("", ["apple"]) == [0.0]


def test_docs_with_the_term_beat_docs_without():
    scores = bm25_scores("refund", ["how to get a refund", "reset your password", "delivery times"])
    assert scores[0] > 0 and scores[1] == 0 and scores[2] == 0


def test_rare_terms_weigh_more_than_common_ones():
    docs = ["the order shipped", "the order is late", "the order A9731 refund", "the order arrived"]
    rare = bm25_scores("a9731", docs)
    common = bm25_scores("order", docs)
    assert max(rare) > max(common)


def test_shorter_documents_score_higher_for_the_same_term_count():
    docs = ["refund", "refund " + "filler " * 30]
    a, b = bm25_scores("refund", docs)
    assert a > b


def test_more_occurrences_score_higher_but_with_diminishing_returns():
    docs = ["refund policy", "refund refund policy", "refund refund refund policy", "other words here"]
    s = bm25_scores("refund", docs)
    assert s[0] < s[1] < s[2]
    assert (s[2] - s[1]) < (s[1] - s[0])


def test_query_terms_are_counted_once():
    docs = ["refund policy", "something else"]
    assert bm25_scores("refund refund refund", docs) == pytest.approx(bm25_scores("refund", docs))


def test_rrf_basic():
    fused = reciprocal_rank_fusion([["a", "b", "c"], ["b", "a", "d"]])
    scores = dict(fused)
    assert scores["a"] == pytest.approx(1 / 61 + 1 / 62)
    assert scores["b"] == pytest.approx(1 / 62 + 1 / 61)
    assert scores["c"] == pytest.approx(1 / 63)
    assert scores["d"] == pytest.approx(1 / 63)
    assert [i for i, _ in fused] == ["a", "b", "c", "d"]        # a/b tie → id order; c/d tie → id order


def test_rrf_rewards_agreement():
    scores = dict(reciprocal_rank_fusion([["x", "shared"], ["y", "shared"]]))
    assert scores["shared"] == pytest.approx(2 / 62)
    assert scores["shared"] > scores["x"]


def test_rrf_k_parameter_and_edge_cases():
    scores = dict(reciprocal_rank_fusion([["a"]], k=0))
    assert scores["a"] == 1.0
    assert reciprocal_rank_fusion([]) == []
    assert reciprocal_rank_fusion([[], []]) == []


def test_min_max():
    assert min_max({"a": 10, "b": 20, "c": 30}) == {"a": 0.0, "b": 0.5, "c": 1.0}
    assert min_max({"a": 5, "b": 5}) == {"a": 1.0, "b": 1.0}
    assert min_max({}) == {}
    assert min_max({"only": 3.0}) == {"only": 1.0}


def test_weighted_fusion():
    vec = {"a": 0.9, "b": 0.5, "c": 0.1}
    kw = {"b": 12.0, "c": 4.0, "d": 8.0}
    fused = dict(weighted_fusion(vec, kw, alpha=0.5))
    assert fused["a"] == pytest.approx(0.5 * 1.0 + 0.5 * 0.0)
    assert fused["b"] == pytest.approx(0.5 * 0.5 + 0.5 * 1.0)
    assert fused["c"] == pytest.approx(0.5 * 0.0 + 0.5 * 0.0)
    assert fused["d"] == pytest.approx(0.5 * 0.0 + 0.5 * 0.5)       # missing from vec -> 0
    assert [i for i, _ in weighted_fusion(vec, kw, 0.5)][0] == "b"


def test_alpha_moves_the_balance():
    vec = {"a": 1.0, "b": 0.0}
    kw = {"a": 0.0, "b": 1.0}
    assert weighted_fusion(vec, kw, alpha=1.0)[0][0] == "a"
    assert weighted_fusion(vec, kw, alpha=0.0)[0][0] == "b"


DOCS = {
    "pw": "how to reset your password using the email link",
    "login": "trouble signing in to your account",
    "ord": "order A9731 shipping details and tracking",
    "refund": "refund policy for returned items",
}


def test_keyword_search_rescues_an_exact_id_the_vector_search_missed():
    # a pretend embedding search that does not understand the code "A9731"
    vector_ranking = ["pw", "login", "refund", "ord"]
    result = hybrid_search("where is A9731", DOCS, vector_ranking, top=2)
    assert "ord" in result
    assert result[0] == "ord" or result[1] == "ord"


def test_vector_search_rescues_a_synonym_the_keywords_missed():
    # "sign in" shares no word with the "pw"/"login" docs except through meaning
    vector_ranking = ["login", "pw", "refund", "ord"]
    result = hybrid_search("cannot log on", DOCS, vector_ranking, top=1)
    assert result == ["login"]


def test_docs_with_zero_keyword_score_are_left_out_of_the_keyword_list():
    result = hybrid_search("zzz nothing matches", DOCS, ["refund", "pw"], top=3)
    assert result == ["refund", "pw"]


def test_top_limits_the_result():
    assert len(hybrid_search("order", DOCS, ["pw", "login", "ord", "refund"], top=1)) == 1

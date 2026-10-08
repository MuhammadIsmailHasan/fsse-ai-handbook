import math

import pytest

from embedding_basics import cosine, dot, euclidean, hash_embed, normalize, norm, top_k


def test_dot_and_norm():
    assert dot([1, 2, 3], [4, 5, 6]) == 32
    assert norm([3, 4]) == 5
    assert norm([0, 0]) == 0


def test_dimension_mismatch():
    for fn in (dot, cosine, euclidean):
        with pytest.raises(ValueError, match="dimension mismatch"):
            fn([1, 2], [1, 2, 3])


def test_normalize():
    assert normalize([3, 4]) == pytest.approx([0.6, 0.8])
    assert normalize([0, 0, 0]) == [0.0, 0.0, 0.0]
    assert norm(normalize([1, 2, 3, 4])) == pytest.approx(1.0)


def test_cosine_basics():
    assert cosine([1, 0], [0, 1]) == pytest.approx(0.0)
    assert cosine([1, 2], [2, 4]) == pytest.approx(1.0)          # same direction, different length
    assert cosine([1, 0], [-1, 0]) == pytest.approx(-1.0)
    assert cosine([1, 1], [1, 0]) == pytest.approx(math.sqrt(2) / 2)


def test_cosine_ignores_length_but_dot_does_not():
    assert cosine([1, 2], [10, 20]) == pytest.approx(cosine([1, 2], [1, 2]))
    assert dot([1, 2], [10, 20]) > dot([1, 2], [1, 2])


def test_cosine_with_a_zero_vector_is_zero():
    assert cosine([0, 0], [1, 2]) == 0.0
    assert cosine([1, 2], [0, 0]) == 0.0


def test_euclidean():
    assert euclidean([0, 0], [3, 4]) == 5
    assert euclidean([1, 1], [1, 1]) == 0


def test_hash_embed_is_deterministic_unit_length_and_the_right_size():
    a = hash_embed("Where is my order?")
    assert a == hash_embed("Where is my order?")
    assert len(a) == 64
    assert norm(a) == pytest.approx(1.0)
    assert len(hash_embed("hello", dim=16)) == 16


def test_hash_embed_ignores_case_punctuation_and_word_order():
    assert hash_embed("Where is my ORDER?") == pytest.approx(hash_embed("order... my is where"))


def test_hash_embed_empty_text():
    assert hash_embed("") == [0.0] * 64
    assert hash_embed("!!! ???", dim=8) == [0.0] * 8


def test_similar_texts_score_higher_than_unrelated_ones():
    q = hash_embed("how do I reset my password")
    close = hash_embed("reset password help")
    far = hash_embed("delivery takes three days to Surabaya")
    assert cosine(q, close) > cosine(q, far)
    assert cosine(q, q) == pytest.approx(1.0)


ITEMS = [("a", [1.0, 0.0]), ("b", [0.9, 0.1]), ("c", [0.0, 1.0]), ("d", [-1.0, 0.0])]


def test_top_k_cosine():
    result = top_k([1.0, 0.0], ITEMS, 2)
    assert [i for i, _ in result] == ["a", "b"]
    assert result[0][1] == pytest.approx(1.0)


def test_top_k_returns_everything_when_k_is_large():
    assert [i for i, _ in top_k([1.0, 0.0], ITEMS, 10)] == ["a", "b", "c", "d"]
    assert top_k([1.0, 0.0], [], 3) == []


def test_top_k_dot_and_euclidean_disagree_with_cosine_when_lengths_differ():
    items = [("short_same_direction", [1.0, 0.0]), ("long_other_direction", [5.0, 5.0])]
    assert top_k([1.0, 0.0], items, 1, "cosine")[0][0] == "short_same_direction"
    assert top_k([1.0, 0.0], items, 1, "dot")[0][0] == "long_other_direction"
    assert top_k([1.0, 0.0], items, 1, "euclidean")[0][0] == "short_same_direction"


def test_euclidean_scores_are_negative_distances():
    assert top_k([0.0, 0.0], [("p", [3.0, 4.0])], 1, "euclidean") == [("p", -5.0)]


def test_ties_are_broken_by_id():
    items = [("b", [1.0, 0.0]), ("a", [1.0, 0.0]), ("c", [1.0, 0.0])]
    assert [i for i, _ in top_k([1.0, 0.0], items, 3)] == ["a", "b", "c"]


def test_unknown_metric():
    with pytest.raises(ValueError):
        top_k([1.0], [("a", [1.0])], 1, "manhattan")


def test_end_to_end_search_with_the_hash_embedder():
    docs = {
        "refund": "how to get a refund for a returned item",
        "password": "reset your account password with the email link",
        "delivery": "delivery times for orders within Java and Bali",
    }
    items = [(i, hash_embed(t)) for i, t in docs.items()]
    assert top_k(hash_embed("I forgot my password"), items, 1)[0][0] == "password"
    assert top_k(hash_embed("refund my returned item"), items, 1)[0][0] == "refund"

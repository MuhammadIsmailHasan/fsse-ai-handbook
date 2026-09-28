import math

import pytest

from retrieval import chunk_tokens, cosine_similarity, top_k


def test_chunk_with_overlap():
    tokens = list(range(10))  # 0..9
    # size 4, overlap 1 → step 3: [0-3], [3-6], [6-9] (last window reaches the end)
    chunks = chunk_tokens(tokens, size=4, overlap=1)
    assert chunks == [[0, 1, 2, 3], [3, 4, 5, 6], [6, 7, 8, 9]]
    # A shorter tail is kept when the window doesn't line up with the end.
    assert chunk_tokens(list(range(8)), size=4, overlap=1) == [[0, 1, 2, 3], [3, 4, 5, 6], [6, 7]]
    # No overlap → clean split.
    assert chunk_tokens(tokens, size=5, overlap=0) == [[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]]


def test_chunk_rejects_bad_overlap():
    with pytest.raises(ValueError):
        chunk_tokens([1, 2, 3], size=2, overlap=2)  # overlap must be < size


def test_cosine_similarity_values():
    assert cosine_similarity([1, 0], [1, 0]) == pytest.approx(1.0)      # identical
    assert cosine_similarity([1, 0], [0, 1]) == pytest.approx(0.0)      # orthogonal
    assert cosine_similarity([1, 1], [2, 2]) == pytest.approx(1.0)      # same direction
    assert cosine_similarity([1, 2, 3], [0, 0, 0]) == 0.0              # zero vector


def test_top_k_ranks_by_similarity():
    query = [1.0, 0.0]
    corpus = [
        {"id": "a", "vector": [0.0, 1.0]},   # orthogonal → 0
        {"id": "b", "vector": [1.0, 0.0]},   # identical → 1
        {"id": "c", "vector": [1.0, 0.2]},   # close → high
    ]
    assert top_k(query, corpus, k=2) == ["b", "c"]
    assert top_k(query, corpus, k=1) == ["b"]
    assert len(top_k(query, corpus, k=10)) == 3  # k larger than corpus is fine

"""Architecture · I — Chunking, cosine similarity, and top-k retrieval.

The retrieval core of RAG:
- chunk_tokens: split a document (list of tokens) into overlapping windows.
- cosine_similarity: how close two embedding vectors point.
- top_k: the k most similar documents to a query vector.
"""

import math


def chunk_tokens(tokens: list, size: int, overlap: int) -> list[list]:
    """Split `tokens` into windows of `size` that overlap by `overlap` tokens.

    Step forward by (size - overlap) each time. The last window may be shorter.
    Raise ValueError unless 0 <= overlap < size.
    """
    # YOUR CODE HERE
    return []


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """dot(a, b) / (||a|| * ||b||). Return 0.0 if either vector has zero length."""
    # YOUR CODE HERE
    return -1.0


def top_k(query: list[float], corpus: list[dict], k: int) -> list:
    """Return the ids of the k documents most similar to `query`.

    corpus is a list of {"id": ..., "vector": [...]}. Sort by cosine similarity
    descending (ties keep original order) and return the first k ids.
    """
    # YOUR CODE HERE
    return []

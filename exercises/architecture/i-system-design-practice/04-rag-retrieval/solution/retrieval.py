"""Architecture · I — Chunking, cosine similarity, top-k retrieval (solution)."""

import math


def chunk_tokens(tokens: list, size: int, overlap: int) -> list[list]:
    if not (0 <= overlap < size):
        raise ValueError("require 0 <= overlap < size")
    step = size - overlap
    chunks: list[list] = []
    i = 0
    while i < len(tokens):
        chunks.append(tokens[i : i + size])
        if i + size >= len(tokens):
            break
        i += step
    return chunks


def cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def top_k(query: list[float], corpus: list[dict], k: int) -> list:
    scored = sorted(
        corpus,
        key=lambda doc: cosine_similarity(query, doc["vector"]),
        reverse=True,
    )
    return [doc["id"] for doc in scored[:k]]

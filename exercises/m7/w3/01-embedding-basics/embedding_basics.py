"""Module 7 · W3 — Embeddings: vectors, similarity and nearest neighbours (no API key needed).

An embedding turns text into a list of numbers so that texts with similar MEANING get similar numbers.
Real embeddings come from a model. Here you build the maths around them, plus a tiny deterministic
"hashing" embedder that is good enough to see the idea (it matches shared WORDS, not meaning).
"""

import hashlib  # noqa: F401  (you will want it)
import math  # noqa: F401
import re  # noqa: F401


def dot(a: list[float], b: list[float]) -> float:
    """Dot product. Different lengths: ValueError("dimension mismatch")."""
    raise NotImplementedError


def norm(v: list[float]) -> float:
    """Length of the vector (Euclidean norm)."""
    raise NotImplementedError


def normalize(v: list[float]) -> list[float]:
    """The vector scaled to length 1. A zero vector stays a zero vector (a list of 0.0)."""
    raise NotImplementedError


def cosine(a: list[float], b: list[float]) -> float:
    """Cosine similarity: dot(a, b) / (|a| * |b|), between -1 and 1.
    If either vector is all zeros return 0.0. Different lengths: ValueError("dimension mismatch")."""
    raise NotImplementedError


def euclidean(a: list[float], b: list[float]) -> float:
    """Straight-line distance between the two points. Different lengths: ValueError("dimension mismatch")."""
    raise NotImplementedError


def hash_embed(text: str, dim: int = 64) -> list[float]:
    """A tiny deterministic embedder ("feature hashing"):
      1. tokens = lowercase words found by the regex [a-z0-9]+
      2. for each token: h = int(sha256(token.encode()).hexdigest(), 16)
            index = h % dim            sign = +1 if (h >> 20) & 1 else -1
            vector[index] += sign
      3. return normalize(vector)
    Do NOT use Python's built-in hash() (it changes between runs). Text with no tokens -> a zero vector of length dim."""
    raise NotImplementedError


def top_k(query: list[float], items: list[tuple[str, list[float]]], k: int, metric: str = "cosine") -> list[tuple[str, float]]:
    """The k best matches as (id, score), best first. A HIGHER score is always better:
        "cosine"     score = cosine(query, vector)
        "dot"        score = dot(query, vector)
        "euclidean"  score = -euclidean(query, vector)
    Ties are broken by id (alphabetical). Unknown metric: ValueError. k larger than the number of items: return all of them."""
    raise NotImplementedError

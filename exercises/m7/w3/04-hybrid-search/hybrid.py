"""Module 7 · W3 — Hybrid search: keywords + vectors (no API key needed).

Vector search finds MEANING ("login problem" ~ "can't sign in") but can miss exact things: an order id,
a product code, a rare name. Keyword search (BM25) finds exact words but misses synonyms.
Hybrid search runs both and fuses the rankings.
"""

import math  # noqa: F401
import re  # noqa: F401


def tokenize(text: str) -> list[str]:
    """Lowercase words matched by the regex [a-z0-9]+ (keep duplicates, keep order)."""
    raise NotImplementedError


def bm25_scores(query: str, docs: list[str], k1: float = 1.5, b: float = 0.75) -> list[float]:
    """BM25 score of the query for each document (same order as docs).

    N = number of docs, avgdl = average number of tokens per doc (if it is 0, treat it as 1).
    For each DISTINCT query token t:
        n_t   = number of docs that contain t
        idf   = ln(1 + (N - n_t + 0.5) / (n_t + 0.5))
        tf    = how many times t appears in this doc,  dl = tokens in this doc
        score += idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * dl / avgdl))
    A doc without any query token scores 0.0. No docs: [].
    """
    raise NotImplementedError


def reciprocal_rank_fusion(rankings: list[list[str]], k: int = 60) -> list[tuple[str, float]]:
    """Fuse several ranked lists of ids. Each id gets, from every list that contains it,
    1 / (k + position) where position starts at 1. Add the parts up.
    Return (id, fused_score) best first; ties by id. RRF uses only ranks, never the raw scores."""
    raise NotImplementedError


def min_max(scores: dict[str, float]) -> dict[str, float]:
    """Scale scores to 0..1: (s - min) / (max - min). If all scores are equal, every value becomes 1.0. Empty -> {}."""
    raise NotImplementedError


def weighted_fusion(a: dict[str, float], b: dict[str, float], alpha: float = 0.5) -> list[tuple[str, float]]:
    """Combine two score dicts (for example vector similarity and BM25) after min_max-scaling each one.
    fused = alpha * scaled_a + (1 - alpha) * scaled_b, using 0.0 for an id missing from a dict.
    Return (id, fused) best first; ties by id."""
    raise NotImplementedError


def hybrid_search(query: str, docs: dict[str, str], vector_ranking: list[str], top: int = 3) -> list[str]:
    """docs: id -> text.  vector_ranking: ids ranked by an embedding search (best first).
    1. rank all docs by BM25 for the query (drop docs with score 0; ties by id)
    2. fuse that keyword ranking with vector_ranking using reciprocal_rank_fusion
    3. return the ids of the best `top`"""
    raise NotImplementedError

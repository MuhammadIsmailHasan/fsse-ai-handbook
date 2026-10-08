"""Module 7 · W3 — A tiny vector database and an approximate index (no API key needed).

A vector database stores vectors with metadata and finds the nearest ones to a query.
EXACT search compares the query with EVERY vector (always right, slow for millions).
APPROXIMATE search checks only a promising subset (much faster, sometimes misses a neighbour).
pgvector offers both: exact scans and indexes such as HNSW and IVFFlat.
"""

import math  # noqa: F401
import random  # noqa: F401


class VectorStore:
    """Exact search.

    VectorStore(dim, metric="cosine")     metric: "cosine" | "dot" | "euclidean"  (higher score = better; euclidean score = -distance)
    add(id, vector, metadata=None)        wrong length -> ValueError("expected N dimensions"); an existing id is REPLACED
    delete(id) -> bool                    True if it existed
    len(store)                            number of vectors
    get(id) -> (vector, metadata) or None
    search(query, k=5, where=None) -> [(id, score), ...]
        best first, ties by id; wrong query length -> ValueError;
        where = {"lang": "id", "type": "faq"}: keep ONLY vectors whose metadata has ALL these key/value pairs
        (filter first, then rank; a vector with no metadata never matches a non-empty filter)
    """

    def __init__(self, dim: int, metric: str = "cosine") -> None:
        raise NotImplementedError

    def add(self, id: str, vector: list[float], metadata: dict | None = None) -> None:
        raise NotImplementedError

    def delete(self, id: str) -> bool:
        raise NotImplementedError

    def get(self, id: str):
        raise NotImplementedError

    def __len__(self) -> int:
        raise NotImplementedError

    def search(self, query: list[float], k: int = 5, where: dict | None = None) -> list[tuple[str, float]]:
        raise NotImplementedError


class LSHIndex:
    """Approximate search with random hyperplanes (locality-sensitive hashing).

    LSHIndex(store, planes=8, seed=0)
      - make `planes` random vectors with the store's dimension: rng = random.Random(seed), each number rng.gauss(0, 1)
        (create them plane by plane, number by number, so the same seed gives the same planes)
      - the SIGNATURE of a vector is a tuple of `planes` bits: bit i = 1 if dot(vector, plane_i) >= 0 else 0
      - bucket every vector of the store by its signature (do this in __init__; the store is not changed afterwards)
    search(query, k=5, probe_neighbors=False) -> (results, candidates)
      - candidates = the ids in the query's own bucket; if probe_neighbors is True also the buckets whose signature
        differs from the query's in exactly ONE bit
      - results = the best k of the candidates by the store's metric (exact scoring of the candidates only),
        as [(id, score), ...] best first, ties by id
      - candidates = how many vectors were scored (an int), so you can see the saving
    """

    def __init__(self, store: VectorStore, planes: int = 8, seed: int = 0) -> None:
        raise NotImplementedError

    def search(self, query: list[float], k: int = 5, probe_neighbors: bool = False):
        raise NotImplementedError


def recall_at_k(approx_ids: list[str], exact_ids: list[str]) -> float:
    """Share of the exact top-k that the approximate search also found: |approx ∩ exact| / |exact|.
    If exact_ids is empty, return 1.0."""
    raise NotImplementedError

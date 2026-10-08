"""Module 7 · W3 — Chunking text and measuring a search system (no API key needed).

Two jobs every semantic-search project has: cut documents into chunks that can be found,
and MEASURE whether the search returns the right things. "It looks good" is not a measurement.
"""


def chunk_text(text: str, size: int, overlap: int = 0) -> list[str]:
    """Cut text into chunks of at most `size` WORDS (split on whitespace), where each chunk repeats the last
    `overlap` words of the previous one. Chunks are joined with single spaces.

    - size must be > 0 and 0 <= overlap < size, otherwise ValueError
    - the step between chunk starts is size - overlap
    - stop as soon as a chunk reaches the end of the text (no extra tiny chunk that is fully inside the previous one)
    - empty / whitespace-only text -> []
    Example: 10 words w0..w9, size 4, overlap 1 -> [w0..w3], [w3..w6], [w6..w9]
    """
    raise NotImplementedError


def precision_at_k(ranked: list[str], relevant: set[str], k: int) -> float:
    """Of the first k results, what share is relevant? Divide by k (not by len(ranked)) so a short list is punished.
    k <= 0: ValueError."""
    raise NotImplementedError


def recall_at_k(ranked: list[str], relevant: set[str], k: int) -> float:
    """Of all the relevant items, what share appears in the first k results? If `relevant` is empty return 1.0."""
    raise NotImplementedError


def reciprocal_rank(ranked: list[str], relevant: set[str]) -> float:
    """1 / (position of the FIRST relevant result, counting from 1). 0.0 if none is relevant."""
    raise NotImplementedError


def evaluate(search_fn, cases: list[dict], k: int = 5) -> dict:
    """Run a search function over test cases and average the scores.

    search_fn(query) -> ranked list of ids
    cases: [{"query": str, "relevant": set[str]}, ...]
    Return {"precision@k": float, "recall@k": float, "mrr": float, "misses": [queries with NO relevant result in the first k]}
    (the three numbers are averages over all cases; misses keep the case order; no cases -> all zeros and [])
    """
    raise NotImplementedError

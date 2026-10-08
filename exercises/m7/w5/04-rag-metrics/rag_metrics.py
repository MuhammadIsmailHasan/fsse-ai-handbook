"""Module 7 · W5 — What RAG-evaluation libraries measure (no API key needed).

Libraries like Ragas and DeepEval report "faithfulness", "context precision", "context recall", ...
Real ones use a language model as a judge. Here you build SIMPLE, deterministic versions so you understand
exactly what each number means (and where they break).
"""

import re  # noqa: F401

STOPWORDS = {
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "to", "of", "in", "on", "at", "for", "and", "or",
    "it", "its", "this", "that", "with", "as", "by", "from", "we", "you", "your", "our", "can", "will", "after",
}


def split_claims(answer: str) -> list[str]:
    """The separate claims of an answer = its sentences.
    1. remove citation markers like [1] or [2, 3] (a bracket with only digits and commas) TOGETHER with the whitespace right before them
    2. split after . ! ? followed by whitespace
    3. strip each piece; drop empty ones"""
    raise NotImplementedError


def content_words(text: str) -> set[str]:
    """Lowercase [a-z0-9]+ words, minus STOPWORDS, as a set."""
    raise NotImplementedError


def claim_supported(claim: str, contexts: list[str], threshold: float = 0.8) -> bool:
    """A claim is supported when at least `threshold` of its content words appear in the contexts (together).
    A claim with no content words counts as supported."""
    raise NotImplementedError


def faithfulness(answer: str, contexts: list[str], threshold: float = 0.8) -> float:
    """Share of the answer's claims that are supported by the contexts. No claims: 1.0.
    (Low faithfulness = the answer says things the sources do not.)"""
    raise NotImplementedError


def context_precision(relevance_flags: list[bool]) -> float:
    """How well are the relevant chunks RANKED? relevance_flags[i] says whether the chunk at rank i+1 is relevant.
    Average precision: for every rank k that holds a relevant chunk, take precision@k (relevant so far / k);
    return the mean of those values. No relevant chunk: 0.0.
    Example: [True, False, True] -> (1/1 + 2/3) / 2 = 0.8333...   [False, True] -> 0.5"""
    raise NotImplementedError


def context_recall(required_facts: list[str], contexts: list[str]) -> float:
    """Share of the required facts that appear (case-insensitive substring) in the contexts joined together.
    No required facts: 1.0. (Low recall = retrieval did not bring the needed information.)"""
    raise NotImplementedError


def answer_coverage(required_facts: list[str], answer: str) -> float:
    """Share of the required facts that appear in the ANSWER (case-insensitive substring). No facts: 1.0."""
    raise NotImplementedError

"""Module 7 · W4 — The RAG pipeline (no API key needed).

RAG = Retrieval-Augmented Generation: find the right passages, put them in the prompt, ask the model
to answer ONLY from them. Retriever and model are passed in, so tests can fake both.

A retrieved chunk is a dict:  {"id": str, "text": str, "score": float, "source": str}
"""

import math  # noqa: F401


def estimate_tokens(text: str) -> int:
    """ceil(len(text) / 4); empty text is 0."""
    raise NotImplementedError


NO_ANSWER = "I could not find this in the documents I have."


def build_prompt(question: str, chunks: list[dict], max_context_tokens: int) -> tuple[str, list[dict]]:
    """Build the user prompt and say which chunks made it in.

    Layout (exactly):
        Answer the question using ONLY the sources below. Cite them like [1], [2].
        If the sources do not contain the answer, say you do not know.

        <sources>
        [1] (<source of chunk 1>)
        <text of chunk 1>

        [2] (<source of chunk 2>)
        <text of chunk 2>
        </sources>

        Question: <question>

    - sources are numbered from 1 in the order given
    - add chunks in order while the TOTAL estimated tokens of the chunk texts stays <= max_context_tokens;
      stop at the first chunk that does not fit (do not skip it to fit a smaller later one)
    - if no chunk fits, the prompt has an empty <sources> block:  "<sources>\\n</sources>"
    Return (prompt, used_chunks) where used_chunks is the list of chunks that were included, in order.
    """
    raise NotImplementedError


def answer(question: str, retriever, llm, *, k: int = 5, min_score: float = 0.0, max_context_tokens: int = 1000) -> dict:
    """The whole RAG flow.

    retriever(question, k) -> list of chunk dicts, best first
    llm(prompt) -> str

    1. chunks = retriever(question, k)
    2. keep only chunks with score >= min_score
    3. if nothing is left: return {"answer": NO_ANSWER, "sources": [], "used_llm": False}   (do NOT call the model)
    4. prompt, used = build_prompt(question, chunks, max_context_tokens)
    5. if no chunk made it into the prompt: same as step 3
    6. text = llm(prompt)
    7. return {"answer": text, "sources": [ {"n": 1, "id": ..., "source": ...}, ... for the used chunks ], "used_llm": True}
    """
    raise NotImplementedError

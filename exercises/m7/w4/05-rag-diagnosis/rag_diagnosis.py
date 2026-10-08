"""Module 7 · W4 — Why did this RAG answer fail? (no API key needed)

When a RAG answer is wrong, WHERE did it go wrong? Retrieval and generation fail differently and are fixed
differently. A trace records one question end to end:

    {
      "question": str,
      "relevant_ids": [ids of the chunks that contain the answer]   (empty list = the corpus has no answer),
      "retrieved_ids": [ids from the search, best first],
      "prompt_ids": [ids that actually went into the prompt, in order],
      "answer_is_correct": bool,        # a human or a judge decided
      "answer_is_grounded": bool,       # every claim is supported by the chunks in the prompt
      "refused": bool,                  # the answer says "I do not know"
    }
"""

CATEGORIES = [
    "ok",
    "correct_refusal",
    "wrong_refusal",
    "retrieval_miss",
    "dropped_before_prompt",
    "not_used",
    "ungrounded",
    "hallucinated_answer",
]


def diagnose(trace: dict) -> str:
    """Return exactly one category, checking the rules IN THIS ORDER:

      relevant_ids is empty (the corpus cannot answer):
          refused                         -> "correct_refusal"
          not refused                     -> "hallucinated_answer"
      refused (and relevant chunks exist):
          no relevant id in retrieved_ids -> "retrieval_miss"
          no relevant id in prompt_ids    -> "dropped_before_prompt"
          otherwise                       -> "wrong_refusal"      (the model had the answer and refused)
      not refused (relevant chunks exist):
          no relevant id in retrieved_ids -> "retrieval_miss"
          no relevant id in prompt_ids    -> "dropped_before_prompt"
          answer_is_correct and answer_is_grounded     -> "ok"
          answer_is_correct but not grounded           -> "ungrounded"   (right by luck or memory: not trustworthy)
          not answer_is_correct                        -> "not_used"     (the right chunk was there but the answer is wrong)
    """
    raise NotImplementedError


def summarize(traces: list[dict]) -> dict:
    """Count the diagnoses. Return
        {"total": n, "counts": {category: count for EVERY category in CATEGORIES (zeros included)},
         "retrieval_recall": share of traces with non-empty relevant_ids where a relevant id is in retrieved_ids (1.0 if there are none),
         "worst": the category (not "ok", not "correct_refusal") with the most traces, or None if all of those are 0;
                  ties go to the category that comes first in CATEGORIES}"""
    raise NotImplementedError


FIXES = {
    "retrieval_miss": "improve retrieval: chunking, query rewriting, hybrid search, embedding model, filters",
    "dropped_before_prompt": "raise k or the context budget, or fix the ranking / re-ranker so the right chunk is kept",
    "not_used": "improve the prompt, reduce noisy context, reorder chunks, or use a stronger model",
    "ungrounded": "require citations, validate quotes, tell the model to answer only from the sources",
    "wrong_refusal": "relax the refusal rule or the score threshold; give the model clearer permission to answer",
    "hallucinated_answer": "add a refusal path: a minimum score, an 'I do not know' instruction, an answerability check",
}


def plan(traces: list[dict]) -> list[str]:
    """A to-do list for the team: for every failure category that has at least one trace, in the order of
    CATEGORIES, one line:  "<category> (<count>): <FIXES text>".  Categories 'ok' and 'correct_refusal' are never listed.
    Sort the lines by count, largest first; ties keep the CATEGORIES order. No failures -> []."""
    raise NotImplementedError

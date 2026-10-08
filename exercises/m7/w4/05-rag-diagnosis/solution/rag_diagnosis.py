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


def diagnose(trace):
    relevant = set(trace["relevant_ids"])
    if not relevant:
        return "correct_refusal" if trace["refused"] else "hallucinated_answer"
    if not relevant & set(trace["retrieved_ids"]):
        return "retrieval_miss"
    if not relevant & set(trace["prompt_ids"]):
        return "dropped_before_prompt"
    if trace["refused"]:
        return "wrong_refusal"
    if trace["answer_is_correct"] and trace["answer_is_grounded"]:
        return "ok"
    if trace["answer_is_correct"]:
        return "ungrounded"
    return "not_used"


def summarize(traces):
    counts = {c: 0 for c in CATEGORIES}
    answerable = hit = 0
    for t in traces:
        counts[diagnose(t)] += 1
        if t["relevant_ids"]:
            answerable += 1
            if set(t["relevant_ids"]) & set(t["retrieved_ids"]):
                hit += 1
    failures = [c for c in CATEGORIES if c not in ("ok", "correct_refusal")]
    worst = max(failures, key=lambda c: counts[c]) if any(counts[c] for c in failures) else None
    return {"total": len(traces), "counts": counts, "retrieval_recall": hit / answerable if answerable else 1.0, "worst": worst}


FIXES = {
    "retrieval_miss": "improve retrieval: chunking, query rewriting, hybrid search, embedding model, filters",
    "dropped_before_prompt": "raise k or the context budget, or fix the ranking / re-ranker so the right chunk is kept",
    "not_used": "improve the prompt, reduce noisy context, reorder chunks, or use a stronger model",
    "ungrounded": "require citations, validate quotes, tell the model to answer only from the sources",
    "wrong_refusal": "relax the refusal rule or the score threshold; give the model clearer permission to answer",
    "hallucinated_answer": "add a refusal path: a minimum score, an 'I do not know' instruction, an answerability check",
}


def plan(traces):
    counts = summarize(traces)["counts"]
    rows = [(c, counts[c]) for c in CATEGORIES if c not in ("ok", "correct_refusal") and counts[c] > 0]
    rows.sort(key=lambda r: -r[1])          # stable: ties keep CATEGORIES order
    return [f"{c} ({n}): {FIXES[c]}" for c, n in rows]

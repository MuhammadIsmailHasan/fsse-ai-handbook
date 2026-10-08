import math

NO_ANSWER = "I could not find this in the documents I have."


def estimate_tokens(text):
    return math.ceil(len(text) / 4)


def build_prompt(question, chunks, max_context_tokens):
    used, total = [], 0
    for chunk in chunks:
        cost = estimate_tokens(chunk["text"])
        if total + cost > max_context_tokens:
            break
        used.append(chunk)
        total += cost
    blocks = [f"[{i}] ({c['source']})\n{c['text']}" for i, c in enumerate(used, start=1)]
    sources = "<sources>\n" + ("\n\n".join(blocks) + "\n" if blocks else "") + "</sources>"
    prompt = (
        "Answer the question using ONLY the sources below. Cite them like [1], [2].\n"
        "If the sources do not contain the answer, say you do not know.\n\n"
        f"{sources}\n\n"
        f"Question: {question}"
    )
    return prompt, used


def answer(question, retriever, llm, *, k=5, min_score=0.0, max_context_tokens=1000):
    chunks = [c for c in retriever(question, k) if c["score"] >= min_score]
    if chunks:
        prompt, used = build_prompt(question, chunks, max_context_tokens)
        if used:
            text = llm(prompt)
            return {
                "answer": text,
                "sources": [{"n": i, "id": c["id"], "source": c["source"]} for i, c in enumerate(used, start=1)],
                "used_llm": True,
            }
    return {"answer": NO_ANSWER, "sources": [], "used_llm": False}

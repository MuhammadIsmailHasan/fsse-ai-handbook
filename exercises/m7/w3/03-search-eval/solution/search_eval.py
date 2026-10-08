def chunk_text(text, size, overlap=0):
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError("bad size/overlap")
    words = text.split()
    chunks = []
    step = size - overlap
    start = 0
    while start < len(words):
        chunks.append(" ".join(words[start : start + size]))
        if start + size >= len(words):
            break
        start += step
    return chunks


def precision_at_k(ranked, relevant, k):
    if k <= 0:
        raise ValueError("k must be positive")
    return sum(1 for r in ranked[:k] if r in relevant) / k


def recall_at_k(ranked, relevant, k):
    if not relevant:
        return 1.0
    return len(set(ranked[:k]) & relevant) / len(relevant)


def reciprocal_rank(ranked, relevant):
    for position, item in enumerate(ranked, start=1):
        if item in relevant:
            return 1 / position
    return 0.0


def evaluate(search_fn, cases, k=5):
    if not cases:
        return {"precision@k": 0.0, "recall@k": 0.0, "mrr": 0.0, "misses": []}
    p = r = m = 0.0
    misses = []
    for case in cases:
        ranked = search_fn(case["query"])
        p += precision_at_k(ranked, case["relevant"], k)
        r += recall_at_k(ranked, case["relevant"], k)
        m += reciprocal_rank(ranked, case["relevant"])
        if not set(ranked[:k]) & case["relevant"]:
            misses.append(case["query"])
    n = len(cases)
    return {"precision@k": p / n, "recall@k": r / n, "mrr": m / n, "misses": misses}

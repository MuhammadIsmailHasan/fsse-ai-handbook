import math
import re


def cosine(a, b):
    na, nb = math.sqrt(sum(x * x for x in a)), math.sqrt(sum(x * x for x in b))
    if na == 0 or nb == 0:
        return 0.0
    return sum(x * y for x, y in zip(a, b)) / (na * nb)


def mmr(query_vector, candidates, k, lambda_=0.7):
    remaining = list(candidates)
    chosen = []
    while remaining and len(chosen) < k:
        best, best_value = None, None
        for c in remaining:
            redundancy = max((cosine(c["vector"], s["vector"]) for s in chosen), default=0.0)
            value = lambda_ * cosine(query_vector, c["vector"]) - (1 - lambda_) * redundancy
            if best_value is None or value > best_value:
                best, best_value = c, value
        chosen.append(best)
        remaining.remove(best)
    return chosen


def _words(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))


def jaccard(a, b):
    wa, wb = _words(a), _words(b)
    if not wa and not wb:
        return 1.0
    return len(wa & wb) / len(wa | wb)


def drop_near_duplicates(chunks, threshold=0.8):
    kept = []
    for chunk in chunks:
        if all(jaccard(chunk["text"], k["text"]) < threshold for k in kept):
            kept.append(chunk)
    return kept


def lost_in_the_middle_order(chunks):
    return chunks[0::2] + chunks[1::2][::-1]


def rerank(query, candidates, scorer, top_n):
    scored = [dict(c, rerank_score=scorer(query, c["text"])) for c in candidates]
    scored.sort(key=lambda c: -c["rerank_score"])        # sort is stable
    return scored[:top_n]

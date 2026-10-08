import math
import re


def tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())


def bm25_scores(query, docs, k1=1.5, b=0.75):
    if not docs:
        return []
    tokenized = [tokenize(d) for d in docs]
    n_docs = len(docs)
    avgdl = (sum(len(t) for t in tokenized) / n_docs) or 1
    scores = [0.0] * n_docs
    for term in set(tokenize(query)):
        n_t = sum(1 for t in tokenized if term in t)
        if n_t == 0:
            continue
        idf = math.log(1 + (n_docs - n_t + 0.5) / (n_t + 0.5))
        for i, tokens in enumerate(tokenized):
            tf = tokens.count(term)
            if tf:
                scores[i] += idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * len(tokens) / avgdl))
    return scores


def reciprocal_rank_fusion(rankings, k=60):
    fused = {}
    for ranking in rankings:
        for position, item in enumerate(ranking, start=1):
            fused[item] = fused.get(item, 0.0) + 1 / (k + position)
    return sorted(fused.items(), key=lambda pair: (-pair[1], pair[0]))


def min_max(scores):
    if not scores:
        return {}
    low, high = min(scores.values()), max(scores.values())
    if high == low:
        return {k: 1.0 for k in scores}
    return {k: (v - low) / (high - low) for k, v in scores.items()}


def weighted_fusion(a, b, alpha=0.5):
    sa, sb = min_max(a), min_max(b)
    fused = {i: alpha * sa.get(i, 0.0) + (1 - alpha) * sb.get(i, 0.0) for i in set(sa) | set(sb)}
    return sorted(fused.items(), key=lambda pair: (-pair[1], pair[0]))


def hybrid_search(query, docs, vector_ranking, top=3):
    ids = list(docs)
    scores = bm25_scores(query, [docs[i] for i in ids])
    keyword = sorted(((i, s) for i, s in zip(ids, scores) if s > 0), key=lambda pair: (-pair[1], pair[0]))
    fused = reciprocal_rank_fusion([[i for i, _ in keyword], vector_ranking])
    return [i for i, _ in fused[:top]]

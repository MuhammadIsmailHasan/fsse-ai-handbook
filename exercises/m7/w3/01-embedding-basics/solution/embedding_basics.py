import hashlib
import math
import re


def _check(a, b):
    if len(a) != len(b):
        raise ValueError("dimension mismatch")


def dot(a, b):
    _check(a, b)
    return sum(x * y for x, y in zip(a, b))


def norm(v):
    return math.sqrt(sum(x * x for x in v))


def normalize(v):
    n = norm(v)
    return [0.0] * len(v) if n == 0 else [x / n for x in v]


def cosine(a, b):
    _check(a, b)
    na, nb = norm(a), norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return dot(a, b) / (na * nb)


def euclidean(a, b):
    _check(a, b)
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def hash_embed(text, dim=64):
    vector = [0.0] * dim
    for token in re.findall(r"[a-z0-9]+", text.lower()):
        h = int(hashlib.sha256(token.encode()).hexdigest(), 16)
        vector[h % dim] += 1.0 if (h >> 20) & 1 else -1.0
    return normalize(vector)


def top_k(query, items, k, metric="cosine"):
    if metric == "cosine":
        score = lambda v: cosine(query, v)
    elif metric == "dot":
        score = lambda v: dot(query, v)
    elif metric == "euclidean":
        score = lambda v: -euclidean(query, v)
    else:
        raise ValueError(f"unknown metric: {metric}")
    scored = [(item_id, score(vector)) for item_id, vector in items]
    scored.sort(key=lambda pair: (-pair[1], pair[0]))
    return scored[:k]

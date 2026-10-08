import math
import random


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _norm(v):
    return math.sqrt(sum(x * x for x in v))


class VectorStore:
    def __init__(self, dim, metric="cosine"):
        if metric not in ("cosine", "dot", "euclidean"):
            raise ValueError(f"unknown metric: {metric}")
        self.dim, self.metric = dim, metric
        self._items = {}

    def _score(self, a, b):
        if self.metric == "dot":
            return _dot(a, b)
        if self.metric == "euclidean":
            return -math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))
        na, nb = _norm(a), _norm(b)
        return 0.0 if na == 0 or nb == 0 else _dot(a, b) / (na * nb)

    def add(self, id, vector, metadata=None):
        if len(vector) != self.dim:
            raise ValueError(f"expected {self.dim} dimensions")
        self._items[id] = (list(vector), dict(metadata or {}))

    def delete(self, id):
        return self._items.pop(id, None) is not None

    def get(self, id):
        return self._items.get(id)

    def __len__(self):
        return len(self._items)

    def search(self, query, k=5, where=None):
        if len(query) != self.dim:
            raise ValueError(f"expected {self.dim} dimensions")
        scored = []
        for id, (vector, metadata) in self._items.items():
            if where and any(metadata.get(key) != value or key not in metadata for key, value in where.items()):
                continue
            scored.append((id, self._score(query, vector)))
        scored.sort(key=lambda pair: (-pair[1], pair[0]))
        return scored[:k]


class LSHIndex:
    def __init__(self, store, planes=8, seed=0):
        self.store = store
        rng = random.Random(seed)
        self.planes = [[rng.gauss(0, 1) for _ in range(store.dim)] for _ in range(planes)]
        self.buckets = {}
        for id, (vector, _) in store._items.items():
            self.buckets.setdefault(self._signature(vector), []).append(id)

    def _signature(self, vector):
        return tuple(1 if _dot(vector, plane) >= 0 else 0 for plane in self.planes)

    def search(self, query, k=5, probe_neighbors=False):
        signature = self._signature(query)
        candidates = list(self.buckets.get(signature, []))
        if probe_neighbors:
            for i in range(len(signature)):
                flipped = signature[:i] + (1 - signature[i],) + signature[i + 1 :]
                candidates += self.buckets.get(flipped, [])
        scored = [(id, self.store._score(query, self.store._items[id][0])) for id in candidates]
        scored.sort(key=lambda pair: (-pair[1], pair[0]))
        return scored[:k], len(candidates)


def recall_at_k(approx_ids, exact_ids):
    if not exact_ids:
        return 1.0
    return len(set(approx_ids) & set(exact_ids)) / len(exact_ids)

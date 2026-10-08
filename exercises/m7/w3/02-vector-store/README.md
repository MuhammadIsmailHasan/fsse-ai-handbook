# Module 7 · W3 · A Tiny Vector Database

> 🚫🤖 **No-AI** · ⏱️ ~55 min · no API key needed

A **vector database** (or Postgres with the **pgvector** extension) stores vectors next to your normal data and finds the closest ones to a query vector.

| Piece | Does |
|---|---|
| `VectorStore` | **exact** search: compare the query with every vector. Always right, but cost grows with the amount of data. Supports a **metadata filter** (`where={"lang": "id"}`): filter first, then rank |
| `LSHIndex` | **approximate** search: random hyperplanes cut the space into buckets; only the query's bucket (and optionally neighbouring buckets) is scored. Much less work, and it can **miss** a neighbour |
| `recall_at_k` | how much of the true top-k the approximate search found |

```text
exact:        score 1,000,000 vectors   → always the true top 10
approximate:  score  ~5,000 candidates  → usually 9 or 10 of the true top 10, in a fraction of the time
```

This is the trade-off behind every vector index (HNSW, IVFFlat, ...): **speed against recall**. A good engineer measures recall on their own data instead of trusting a default.

```bash
cd exercises
uv run pytest m7/w3/02-vector-store
```

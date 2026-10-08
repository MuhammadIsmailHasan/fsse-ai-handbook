# Module 7 · W3 · Embeddings: Vectors and Similarity

> 🚫🤖 **No-AI** · ⏱️ ~45 min · no API key needed

An **embedding** turns text into a list of numbers (a **vector**). Texts with similar *meaning* get vectors that point in similar directions, so "how close are these two texts?" becomes simple maths.

```text
"reset my password"      → [0.12, -0.40, 0.88, ...]   (hundreds or thousands of numbers)
"I forgot my login"      → [0.10, -0.37, 0.85, ...]   ← points almost the same way: similar
"delivery to Surabaya"   → [-0.52, 0.31, 0.04, ...]   ← points elsewhere: different
```

| Function | Does |
|---|---|
| `dot`, `norm`, `normalize` | the building blocks |
| `cosine(a, b)` | the angle between two vectors: 1 = same direction, 0 = unrelated, −1 = opposite; **ignores length** |
| `euclidean(a, b)` | the straight-line distance |
| `hash_embed(text)` | a tiny deterministic embedder (hashing words into buckets) so you can run the whole idea offline. It matches shared **words**; a real model matches **meaning** |
| `top_k(query, items, k, metric)` | the k nearest items; a higher score is always better |

```bash
cd exercises
uv run pytest m7/w3/01-embedding-basics
```

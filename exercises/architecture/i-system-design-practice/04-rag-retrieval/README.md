# Architecture · I · RAG Retrieval Core

> 🚫🤖 **No-AI** · ⏱️ ~35 min

Build the retrieval heart of a RAG system.

| Function | Does |
|---|---|
| `chunk_tokens(tokens, size, overlap)` | Split a document into overlapping windows |
| `cosine_similarity(a, b)` | How close two embedding vectors point (`0.0` for a zero vector) |
| `top_k(query, corpus, k)` | Ids of the k most similar documents |

The tests check overlapping chunks (and reject `overlap >= size`), a few known similarity values, and correct top-k ranking.

```bash
cd exercises
uv run pytest architecture/i-system-design-practice/04-rag-retrieval
```

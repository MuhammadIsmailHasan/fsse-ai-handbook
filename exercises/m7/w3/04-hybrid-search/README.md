# Module 7 · W3 · Hybrid Search

> 🚫🤖 **No-AI** · ⏱️ ~55 min · no API key needed

Neither kind of search is enough alone:

| | Finds | Misses |
|---|---|---|
| **Vector (meaning)** | "can't log on" ≈ "trouble signing in" | exact codes, names, rare words: `A9731` |
| **Keyword (BM25)** | the exact word `A9731` | synonyms and other wording |

**Hybrid search** runs both and merges the two ranked lists.

| Function | Does |
|---|---|
| `bm25_scores(query, docs)` | the classic keyword score: rare words count more, repeats help but with diminishing returns, long documents are normalised |
| `reciprocal_rank_fusion(rankings)` | merge lists using **ranks only**: each list gives `1 / (60 + position)`; documents that several lists like rise to the top. No score scaling needed |
| `min_max`, `weighted_fusion` | the other way: scale each score to 0..1 and mix with a weight `alpha` |
| `hybrid_search(...)` | BM25 ranking + your vector ranking, fused with RRF |

```text
vector ranking :  pw   login  refund  ord          (missed the order code)
keyword ranking:  ord                              (found "A9731" exactly)
fused          :  ord  pw     login ...            ← both strengths
```

```bash
cd exercises
uv run pytest m7/w3/04-hybrid-search
```

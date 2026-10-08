# Module 7 · W4 · Clean Up the Candidates

> 🚫🤖 **No-AI** · ⏱️ ~50 min · no API key needed

The first search is rough. Before the chunks go into the prompt, improve the list:

| Tool | Problem it solves |
|---|---|
| `mmr(...)` | the top 5 are five copies of the same paragraph. **Maximal Marginal Relevance** picks results that are relevant *and different* from what you already chose |
| `drop_near_duplicates(...)` | the same text indexed twice (a FAQ and its copy in a manual); keep one |
| `lost_in_the_middle_order(...)` | models read the **start and end** of a long context best. Put the best chunks at both ends, the weakest in the middle: `a b c d e → a c e d b` |
| `rerank(query, candidates, scorer, top_n)` | a slower, smarter scorer (a cross-encoder or a model) re-sorts the top candidates |

```text
MMR value = lambda × (similarity to the query)  −  (1 − lambda) × (similarity to what is already chosen)
lambda = 1 → pure relevance     lambda = 0.5 → balance     lower → more variety
```

```bash
cd exercises
uv run pytest m7/w4/03-retrieval-tools
```

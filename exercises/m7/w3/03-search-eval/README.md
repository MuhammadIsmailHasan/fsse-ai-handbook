# Module 7 · W3 · Chunk It, Then Measure It

> 🚫🤖 **No-AI** · ⏱️ ~45 min · no API key needed

Semantic search has two jobs people skip:

1. **Chunking.** An embedding of a 40-page PDF is a blur. Cut documents into pieces about one idea long, and let neighbouring pieces **overlap** a little so an idea cut in half still appears whole in one of them.
2. **Measuring.** Collect real questions with the documents that should answer them, and score the search.

| Function | Meaning |
|---|---|
| `chunk_text(text, size, overlap)` | word-based chunks with overlap |
| `precision_at_k` | of the first k results, how many are right? |
| `recall_at_k` | of all the right answers, how many did the first k contain? |
| `reciprocal_rank` | 1 / the position of the first right answer (the average of this is **MRR**) |
| `evaluate(search_fn, cases, k)` | the averages, plus the list of **misses**: the questions to study first |

```text
10 words, size 4, overlap 1:
[w0 w1 w2 w3]
            [w3 w4 w5 w6]
                        [w6 w7 w8 w9]
```

```bash
cd exercises
uv run pytest m7/w3/03-search-eval
```

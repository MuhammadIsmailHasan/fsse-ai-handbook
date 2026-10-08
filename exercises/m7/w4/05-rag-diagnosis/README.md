# Module 7 · W4 · Why Did This RAG Answer Fail?

> 🚫🤖 **No-AI** · ⏱️ ~45 min · no API key needed

A wrong RAG answer has many possible causes, and each has a **different fix**. Do not guess: record a **trace** for each test question and classify it.

```text
question ─► retrieved (search) ─► in the prompt (after budget/rerank) ─► answer
              ▲                        ▲                                   ▲
       retrieval_miss        dropped_before_prompt              not_used / ungrounded / wrong_refusal
```

| Category | Meaning | Typical fix |
|---|---|---|
| `retrieval_miss` | the right chunk was never found | chunking, hybrid search, embeddings, filters |
| `dropped_before_prompt` | found, but cut by `k`, the token budget or ranking | raise k, fix the order / re-ranker |
| `not_used` | the right chunk was in the prompt, the answer is still wrong | prompt, noise, ordering, model |
| `ungrounded` | correct but not supported by the sources | require citations, check quotes |
| `wrong_refusal` | the model said "I don't know" though it had the answer | loosen refusal rules |
| `hallucinated_answer` | the corpus has no answer but the model answered anyway | add a refusal path |
| `correct_refusal`, `ok` | good |  |

`diagnose(trace)` picks one category using ordered rules, `summarize` counts them and measures retrieval recall, and `plan` turns the counts into a prioritised to-do list.

```bash
cd exercises
uv run pytest m7/w4/05-rag-diagnosis
```

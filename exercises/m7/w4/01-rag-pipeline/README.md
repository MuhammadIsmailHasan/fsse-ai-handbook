# Module 7 · W4 · The RAG Pipeline

> 🚫🤖 **No-AI** · ⏱️ ~45 min · no API key needed

**RAG** (Retrieval-Augmented Generation) gives a model the pages it needs *with the question*, and tells it to answer only from them:

```text
question ─► retrieve top-k chunks ─► keep the good ones ─► build the prompt with numbered sources ─► model ─► answer + sources
                                          │
                                          └─ nothing good? say "I don't know" WITHOUT calling the model
```

| Function | Does |
|---|---|
| `build_prompt(question, chunks, max_context_tokens)` | the exact prompt layout: numbered `[1] (source)` blocks inside `<sources>`; stops adding chunks when the token budget would be exceeded; returns which chunks made it in |
| `answer(question, retriever, llm, ...)` | the whole flow, with a minimum score and an honest "no answer" path that costs nothing |

Note what the tests care about: the **model is never called** when retrieval found nothing usable (cheaper and safer than letting it guess), and the sources you report are exactly the ones that **really went into the prompt**.

```bash
cd exercises
uv run pytest m7/w4/01-rag-pipeline
```

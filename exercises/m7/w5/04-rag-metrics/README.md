# Module 7 · W5 · What RAG Metrics Really Measure

> 🚫🤖 **No-AI** · ⏱️ ~50 min · no API key needed

Libraries such as **Ragas** and **DeepEval** report a handful of RAG scores. They usually ask a language model to decide each judgement. You will build simple word-matching versions so the *meaning* of each number is clear:

| Metric | Question | Low value means |
|---|---|---|
| `faithfulness` | are the answer's claims supported by the retrieved context? | the model **adds things** the sources do not say (hallucination) |
| `context_recall` | does the retrieved context contain the facts that are needed? | **retrieval** missed information |
| `context_precision` | are the relevant chunks ranked near the top? | noisy or badly **ranked** context |
| `answer_coverage` | does the answer contain the required facts? | the answer is **incomplete** |

```text
low context_recall               → fix retrieval
good recall, low faithfulness    → fix the prompt / grounding
good faithfulness, low coverage  → the answer leaves out needed facts
```

Word overlap is a crude stand-in: it misses paraphrase and negation ("not refundable" overlaps "refundable"). That is exactly why real tools use a judge model — and why you must check that judge against humans (previous exercise).

```bash
cd exercises
uv run pytest m7/w5/04-rag-metrics
```

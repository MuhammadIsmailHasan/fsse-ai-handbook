# Module 7 · W4 · Citations You Can Check

> 🚫🤖 **No-AI** · ⏱️ ~50 min · no API key needed

A citation makes an answer **checkable**. But a model can invent `[7]` when there are three sources, leave a claim with no citation, or put words in quotation marks that the source never said. Checking this is simple code, not another model call.

| Function | Checks |
|---|---|
| `extract_citations(answer)` | which source numbers appear (`[2]`, `[1, 3]`) in order of first use |
| `validate_citations(answer, n)` | unknown numbers, a cited answer with **no** citations, sentences with **no** `[n]` (except honest "I do not know") |
| `quote_supported`, `find_fake_quotes` | is a quoted phrase really inside a source? (whitespace, case and quote marks ignored) |
| `render_sources(answer, sources)` | add a clean "Sources:" list for the sources that were **really** cited |

```text
Refunds take 7 days [1]. They are paid by transfer.          ← second sentence: no citation → flag it
The policy says "refunds are instant and unconditional" [1]. ← that quote is in no source → fake quote
Odd [9].                                                      ← only 3 sources → unknown source
```

What you cannot check by string matching: whether the cited source really **supports** the claim. That needs a human, or a second model as a judge (week 5).

```bash
cd exercises
uv run pytest m7/w4/04-citations
```

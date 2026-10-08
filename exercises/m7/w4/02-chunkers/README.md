# Module 7 · W4 · Chunking That Respects Structure

> 🚫🤖 **No-AI** · ⏱️ ~60 min · no API key needed

What you can *find* depends on where you *cut*. Cutting every 200 words splits sentences, tables and ideas in half. Better chunkers follow the document.

| Function | Idea |
|---|---|
| `split_markdown(text, max_words)` | split at **headings**, keep a **heading path** (`Returns > Refunds`), cut long sections between **paragraphs** |
| `split_sentences`, `sentence_chunks` | group **whole sentences**; optional sentence **overlap**; never split inside `3.5` |
| `parent_child`, `expand_to_parents` | **small-to-big**: search small, precise pieces; hand the model the big parent for context |

```text
# Returns                    chunk path "Returns"           
## Refunds                   chunk path "Returns > Refunds"   ← the heading path travels with the text,
## Exchanges                 chunk path "Returns > Exchanges"    so "7 days" is known to be about refunds

search the CHILD  "paid back in 7 days"        ──►   give the model the PARENT: the whole Refunds section
```

```bash
cd exercises
uv run pytest m7/w4/02-chunkers
```

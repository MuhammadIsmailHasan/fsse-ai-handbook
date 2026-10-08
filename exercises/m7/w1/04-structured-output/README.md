# Module 7 · W1 · JSON You Can Trust

> 🚫🤖 **No-AI** · ⏱️ ~45 min · no API key needed

A model is a very good guesser, not a parser. Even with a good prompt it sometimes wraps JSON in prose or a code fence, forgets a key, or returns `"30"` where you wanted `30`. Production code uses **three safety nets**:

| Function | Net |
|---|---|
| `extract_json(text)` | find the JSON inside the reply (fences, prose around it, braces inside strings) |
| `validate(data, schema)` | check types, required keys, enums, ranges, unknown keys — list **every** problem with its path |
| `extract_with_retry(ask, prompt, schema)` | on failure, ask again and **tell the model what was wrong**; give up after N tries |

Two traps are tested on purpose: in Python `True` is also an `int`, and a `}` inside a string is not the end of an object.

(With the API's own structured-output feature the JSON is guaranteed to match your schema. These nets still matter for other providers, local models, and for checking *business* rules a schema cannot express.)

```bash
cd exercises
uv run pytest m7/w1/04-structured-output
```

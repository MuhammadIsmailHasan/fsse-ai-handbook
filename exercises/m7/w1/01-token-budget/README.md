# Module 7 · W1 · Tokens, Context and Temperature

> 🚫🤖 **No-AI** · ⏱️ ~40 min · no API key needed

Four small tools that sit in front of every LLM call:

| Function | Does |
|---|---|
| `estimate_tokens(text)` | about 4 characters per token, rounded up |
| `request_cost(...)` | dollars for one call; prices are per **million** tokens |
| `fit_history(messages, max_context, reserve_for_output)` | cut the **oldest** messages until the chat fits; keep the system message and the last message |
| `apply_temperature(logits, t)` | softmax with a temperature: low = sharp, high = flat, `0` = always the best |

```text
logits a=2.0 b=1.0 c=0.0
t = 0.3 → a 0.96  b 0.03  c 0.00      sharp: almost always "a"
t = 1.0 → a 0.67  b 0.24  c 0.09
t = 3.0 → a 0.45  b 0.32  c 0.23      flat: more surprises
```

```bash
cd exercises
uv run pytest m7/w1/01-token-budget
```

# Module 7 · W1 · Choose a Model With Numbers

> 🚫🤖 **No-AI** · ⏱️ ~35 min · no API key needed

"Use the best model" is not an answer. A real choice is **the cheapest model that is good enough, fast enough and big enough**, checked with numbers.

| Function | Does |
|---|---|
| `call_cost(model, in_tokens, out_tokens)` | dollars for one call |
| `choose_model(models, ...)` | the cheapest model that meets quality, speed and context limits (`None` if none does) |
| `monthly_cost(model, requests_per_day, ...)` | the bill, with an optional **cache hit rate** (cached input costs 10%) |
| `run_cascade(models, ask, is_good)` | try the cheap model first; escalate only when the answer is not good; add up **every** attempt |

```text
cheap model good enough 80% of the time at $0.001, strong model $0.02:
  always strong : 0.020 per request
  cascade       : 0.001 + 0.2 × 0.02 = 0.005 per request   (if the quality check is reliable)
```

```bash
cd exercises
uv run pytest m7/w1/02-model-choice
```

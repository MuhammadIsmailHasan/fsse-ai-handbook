# Architecture · I · Mini LLM Gateway

> 🚫🤖 **No-AI** · ⏱️ ~35 min

Build a small gateway that fronts every AI call: cache, fallback, and cost tracking in one place.

| Piece | Does |
|---|---|
| `estimate_cost(tokens, price_per_1k)` | `tokens / 1000 * price` |
| `LLMGateway.complete(prompt)` | Cache hit → free; miss → try providers in order, track spend |

Providers are `(name, fn)` pairs tried in fallback order; `fn(prompt)` returns `{"text", "tokens"}` or raises to simulate failure.

The tests prove a cached prompt skips the providers (and adds no cost), and that a failing primary provider falls back to the next one.

```bash
cd exercises
uv run pytest architecture/i-system-design-practice/05-llm-gateway
```

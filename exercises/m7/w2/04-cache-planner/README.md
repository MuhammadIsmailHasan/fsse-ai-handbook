# Module 7 · W2 · How Prompt Caching Behaves

> 🚫🤖 **No-AI** · ⏱️ ~45 min · no API key needed

Prompt caching saves money on the part of a prompt you send again and again (instructions, rules, documents). It is a **prefix match**, so *order* decides everything:

```text
prompt = [ tools ][ system prompt ][ big document ][ the user's question ]
          └────────── stable, cache this ───────────┘└─ changes every time ─┘
                                  ▲
                          breakpoint here
```

| Function | Does |
|---|---|
| `simulate_cache(requests, ttl_s, min_tokens)` | for each request: tokens **read** from cache, **written** to cache, or **uncached** — with a 5-minute lifetime that a read refreshes, and a minimum length |
| `first_difference(prev, current)` | the first block that changed: where a silent cache-killer hides (a timestamp, a request id, a reordered tool list) |
| `prompt_cost(usage, price)` | reads cost about a tenth of the normal price, writes a quarter more |
| `cache_savings(...)` | money saved, which can be **negative** for a prompt used only once |

Things the tests make you feel: a timestamp at the top of the system prompt means **zero** hits; a breakpoint placed after the changing question caches nothing useful; a short prompt is never cached; waiting more than the TTL means paying the write again.

```bash
cd exercises
uv run pytest m7/w2/04-cache-planner
```

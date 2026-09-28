# Architecture · I · URL Shortener Core

> 🚫🤖 **No-AI** · ⏱️ ~30 min

Build the heart of a URL shortener plus the estimates you'd give in a system design interview.

| Function | Does |
|---|---|
| `encode_base62(n)` | Turn a numeric id into a short code (`0-9a-zA-Z`) |
| `decode_base62(code)` | Inverse of encode |
| `writes_per_sec(monthly_links)` | Back-of-envelope write rate |
| `capacity(code_len)` | How many links a code length addresses (`62**len`) |

Because ids are unique, base62 codes never collide. The tests check the encode/decode round-trip and the scale estimates (100M/month ≈ 38.6 writes/sec; 7 chars ≈ 3.5 trillion links).

```bash
cd exercises
uv run pytest architecture/i-system-design-practice/01-url-shortener
```

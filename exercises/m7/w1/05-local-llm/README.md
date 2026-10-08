# Module 7 · W1 · A Local Model Client With a Cloud Fallback

> 🚫🤖 **No-AI** · ⏱️ ~40 min · Ollama **not** required

Ollama runs open-weight models on your own machine and exposes a small HTTP API. Local models are free per request and keep data on your laptop, but they can be slow, weaker, or simply not running. So real apps wrap them in a client with a **fallback**.

| Piece | Does |
|---|---|
| `build_chat_payload(...)` | the JSON body for `POST /api/chat` (`options` only when you set some) |
| `collect_ollama_stream(lines)` | read the **NDJSON** reply: one JSON object per line, the last one has `"done": true` and the token counts |
| `OllamaClient` | `complete(messages)`; the HTTP call is passed in as `post`, so tests need no server |
| `FallbackClient` | try the local model; on `LocalModelError` or `ConnectionError` use the cloud one; **do not** hide real bugs |

```text
{"message": {"content": "Hel"}, "done": false}
{"message": {"content": "lo"},  "done": false}
{"message": {"content": ""},    "done": true, "done_reason": "stop", "prompt_eval_count": 14, "eval_count": 6}
```

Ollama listens on port 11434 by default; set `OLLAMA_HOST` (for example `127.0.0.1:11491`) to use another port.

```bash
cd exercises
uv run pytest m7/w1/05-local-llm
```

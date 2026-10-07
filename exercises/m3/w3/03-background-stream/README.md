# Module 3 · W3 · Background Task + Streaming

> 🚫🤖 **No-AI** · ⏱️ ~35 min

In `signup_stream_app.py` finish two endpoints:

| Endpoint | Does |
|---|---|
| `POST /signup` | reject a bad email with `400` (schedule nothing); otherwise return `201` **immediately** and send the welcome email **after** the response with `BackgroundTasks` |
| `GET /stream?text=…` | stream one Server-Sent Event per word (`data: word\n\n`), then `data: [DONE]\n\n`, with media type `text/event-stream` |

`send_welcome` is given. `word_events` must be a **generator**, so words are produced one by one, not all at once.

```bash
cd exercises
uv run pytest m3/w3/03-background-stream
```

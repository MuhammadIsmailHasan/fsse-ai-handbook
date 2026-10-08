# Module 7 · W1 · Chat Messages and Streaming Events

> 🚫🤖 **No-AI** · ⏱️ ~45 min · no API key needed

The chat API has no memory: **you** keep the message list and send all of it every time. And the answer arrives as a stream of small events, not one big block. Build both halves with the real event shapes, so you can test your code without paying for a single token.

| Piece | Does |
|---|---|
| `Conversation` | keeps the messages, makes the request dict (the system prompt is a **separate** key, not a message) |
| `collect_stream(events)` | joins the text, reads the stop reason and token counts, raises `StreamError` on an error event |
| `to_sse(events)` | forwards a model stream to a browser as SSE lines (same format as the FastAPI lesson), lazily |

```text
message_start → content_block_start → content_block_delta ("Hel") → content_block_delta ("lo")
              → content_block_stop → message_delta (stop_reason, output_tokens) → message_stop
```

Things the tests check on purpose: thinking deltas and unknown event types are **ignored** (new event types appear over time), a stream that dies early is an **error**, and a token with a blank line inside is sent as **JSON**, so it cannot break the SSE framing.

```bash
cd exercises
uv run pytest m7/w1/03-chat-stream
```

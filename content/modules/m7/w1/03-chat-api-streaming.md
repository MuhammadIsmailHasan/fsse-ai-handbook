---
title: "Chat API & Streaming"
summary: "Call a chat model from Python — messages and roles, the system prompt, max_tokens and stop_reason, usage, errors and retries — then stream the answer token by token and forward it to a browser safely."
type: lesson
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: core, ops: optional }
durationMinutes: 180
tags: [llm, chat-api, streaming, sse, fastapi, errors]
lastReviewed: 2026-10
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- The shape of a **chat request**: model, system prompt, messages, `max_tokens`
- Why the API is **stateless** and what that means for your code
- Reading the **response**: text blocks, `stop_reason`, `usage`
- **Streaming**: events, `text_stream`, and what each event means
- Sending a stream to a browser with **FastAPI + SSE**
- **Errors and retries** that production code needs

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Messages API** | The standard way to chat with a model: a list of messages in, a message out | API pesan |
| **Role** | Who wrote a message: `user` or `assistant` | Peran |
| **System prompt** | Standing instructions for the whole chat | Instruksi sistem |
| **Stateless** | The server remembers nothing between calls | Tanpa ingatan |
| **Stop reason** | Why the model stopped writing | Alasan berhenti |
| **Stream** | The answer arrives in small pieces as it is written | Aliran |
| **SSE** | Server-Sent Events: a simple text format to push a stream to a browser | Event dari server |
| **Rate limit** | A cap on requests or tokens per minute | Batas laju |

## 🧠 The big idea

A chat API is like **a very forgetful expert on the phone**. Every time you call, you must read out the *whole* conversation so far, then ask your new question. The expert answers and forgets everything when you hang up. You keep the notebook.

Streaming is the expert **talking while thinking** instead of staying silent for ten seconds and then reading a whole page. The total time is the same, but the person on the line hears the first words almost at once.

## ❓ Why it matters

This is the base layer under every AI feature: chatbots, summaries, extraction, agents. If you get it right you get:

- **a fast-feeling product** (first words in under a second),
- **a stable one** (retries, timeouts, clear errors),
- **a safe one** (your API key never reaches the browser; cut-off answers are noticed),
- **a cheap one** (you log `usage` and trim what you send).

## 📖 Step by step

### 1. Install and create the client

```python
# pip install anthropic     # the provider's official SDK
import anthropic

client = anthropic.Anthropic()    # reads the API key from the environment (ANTHROPIC_API_KEY)
```

**Never put the key in code, in git, or in front-end JavaScript.** Keep it in an environment variable or a secret manager. Your *backend* calls the model; the browser calls your backend.

### 2. One request

```python
response = client.messages.create(
    model=settings.llm_model,          # from config, see the last lesson
    max_tokens=1000,                   # the most the model may write in this call
    system="You are a polite help-desk assistant for Warung Kita Online.",
    messages=[
        {"role": "user", "content": "How long does delivery take?"},
    ],
)

for block in response.content:         # a list of blocks: check the type first
    if block.type == "text":
        print(block.text)
print(response.stop_reason, response.usage.input_tokens, response.usage.output_tokens)
```

Points to notice:

- **`messages`** is a list of `{"role", "content"}` with roles `user` and `assistant`. The first must be `user`.
- The **system prompt is a separate field**, not a message in the list.
- **`max_tokens` is required.** Set it on purpose (see lesson 1).
- **`response.content` is a list of blocks**, not a string. Normal answers have a `text` block. Other types (tool calls, thinking) appear in later weeks, so always check `block.type`.
- Read **`stop_reason`**: `end_turn` (finished), `max_tokens` (cut off!), `tool_use` (asks for a tool), `refusal` (declined for safety), and a few others.
- Read **`usage`** and log it.

### 3. The API is stateless: you hold the history

```python
from chat_stream import Conversation        # the exercise for this lesson

chat = Conversation(system="You are a polite help-desk assistant.")
chat.add_user("Hi, I need help with an order.")
reply = client.messages.create(**chat.to_request(settings.llm_model, 1000))
chat.add_assistant(reply.content[0].text)
chat.add_user("It is order 1234.")
reply = client.messages.create(**chat.to_request(settings.llm_model, 1000))
```

Each call sends the whole list. Your app (or database) keeps the history per user. Remember lesson 1: the list grows, so trim or summarize it.

Roles must **alternate** (user, assistant, user, ...), and the chat must **start with a user message**. A small `Conversation` class that enforces this saves you from confusing 400 errors.

### 4. Streaming

Without streaming, the user waits for the whole answer. With streaming you get events as the model writes. The SDK helper hides the details:

```python
with client.messages.stream(
    model=settings.llm_model,
    max_tokens=1000,
    messages=[{"role": "user", "content": "Explain what a token is."}],
) as stream:
    for text in stream.text_stream:          # just the new text, piece by piece
        print(text, end="", flush=True)
    final = stream.get_final_message()       # the complete message, with usage and stop_reason
print(final.stop_reason, final.usage.output_tokens)
```

Use streaming for anything a person watches, and also for **long outputs** (large `max_tokens`) because long non-streaming requests can time out.

Behind the helper is a series of small events:

```text
message_start         → starts; input token count
content_block_start   → a text block begins
content_block_delta   → "Hel"   then "lo"   (the pieces)
content_block_stop    → the block ends
message_delta         → stop_reason and output token count
message_stop          → done
ping                  → keep-alive, ignore
error                 → something broke
```

Good readers of this stream do four things: **join** the text deltas, **ignore** event types they do not know (providers add new ones, such as thinking deltas), **treat an error event as an error**, and treat a stream that ends **without `message_stop`** as a failure, not a short answer.

### 5. Forward the stream to a browser (FastAPI + SSE)

You met `StreamingResponse` and SSE in Module 3. Now connect the two. The browser must never see your key, so the browser calls **your** endpoint, and your endpoint calls the model:

```python
import json
import anthropic
from fastapi import Depends
from fastapi.responses import StreamingResponse

@app.post("/v1/chat")
def chat(body: ChatIn, user: str = Depends(current_user)):
    def events():
        try:
            with client.messages.stream(
                model=settings.llm_model,
                max_tokens=1000,
                system=SYSTEM_PROMPT,
                messages=body.messages,
            ) as stream:
                for text in stream.text_stream:
                    yield f"data: {json.dumps({'token': text})}\n\n"
                final = stream.get_final_message()
            if final.stop_reason == "max_tokens":
                yield f"data: {json.dumps({'truncated': True})}\n\n"
            log_usage(user, final.usage)
            yield "data: [DONE]\n\n"
        except anthropic.APIError as error:
            yield f"data: {json.dumps({'error': type(error).__name__})}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
```

Things this does right:

- each token is **JSON**, so a token with a blank line cannot break the SSE format,
- a **truncated** answer is flagged,
- an **error after the first byte** becomes an error event (the HTTP status is already 200),
- **usage is logged** and the user is authenticated,
- proxy buffering is turned off.

Validate the incoming `messages` (roles, length, size) before you forward them. Never trust the client to send a safe system prompt: keep the system prompt on the server.

### 6. Errors and retries

Things go wrong for ordinary reasons: a busy server, a rate limit, a network drop, a bad request.

| Status | Meaning | What to do |
|---|---|---|
| 400 | your request is invalid | fix the code; do not retry |
| 401 / 403 | key missing or not allowed | fix the configuration |
| 404 | unknown model or resource | fix the model name |
| 413 | request too large | trim the input |
| 429 | rate limit | wait and retry (back off) |
| 500 / 503 / 529 | server problem or overload | retry later, maybe fall back to another model |

The SDK already **retries** connection errors, 408, 409, 429 and 5xx a couple of times with backoff. Set a sensible **timeout**. Catch the **most specific** exception first:

```python
try:
    response = client.messages.create(...)
except anthropic.RateLimitError:
    ...                                   # tell the user to retry soon, or queue the job
except anthropic.APIStatusError as error:
    log.error("model error %s", error.status_code)
    ...                                   # 4xx: a bug of ours; 5xx: temporary
except anthropic.APIConnectionError:
    ...                                   # the network failed
```

Never show raw provider errors to users. Give them a short, calm message, and log the details (with the request id) for yourself.

### 7. Testing without paying

Your code that reads events, builds requests and forwards SSE is plain Python. Test it with **fake events** (the exercise does this) and with a fake client that you inject, exactly like `dependency_overrides` in Module 3. Keep only a few "smoke tests" that call the real API, and run them rarely.

### Choosing your setup

| Situation | Do this |
|---|---|
| Short, background answer | `messages.create`, read `response.content` |
| A person is watching | `messages.stream` + SSE |
| Very long output | stream it (avoids timeouts) |
| Chat | keep the history yourself; alternate roles; trim |
| Browser needs the answer | your backend streams to the browser; the key stays on the server |
| Rate limited | back off and retry; queue work; use the batch API for non-urgent jobs |
| Testing | fake events and an injected client |

- ✅ Log `usage`, `stop_reason` and a request id.
- ✅ Treat `max_tokens` and `refusal` as normal outcomes to handle.
- 🚫 The API key in front-end code.
- 🚫 Showing the user a raw stack trace or provider error.

## ⚠️ Common mistakes

- Using `response.content[0].text` without checking that block's type.
- Forgetting that the API is stateless and sending only the last message.
- Two `user` messages in a row, or starting with an `assistant` message.
- Putting the system prompt in the message list.
- No handling for `stop_reason == "max_tokens"`.
- Catching one broad `Exception` and retrying everything, even bad requests.
- Sending raw model text in SSE (a blank line in the text breaks the stream).
- Not turning off proxy buffering, so streaming looks like waiting.
- Letting the client choose the model or the system prompt.

:::revoshop
Design the request RevoShop's "ask about my order" endpoint would send. (1) What is in the system prompt, and what is in `messages`? (2) Where does the order data go, and who is allowed to read it (think about the JWT from Module 2)? (3) What should the endpoint do when the provider returns a 429?
:::

## 🏆 Best practices

- [ ] Keep the API key and system prompt on the server.
- [ ] Set `max_tokens` and a timeout on purpose; handle `max_tokens` and `refusal`.
- [ ] Stream anything a person watches; send tokens as JSON in SSE.
- [ ] Catch the most specific errors first; retry only what is worth retrying.
- [ ] Log `usage`, `stop_reason`, model and a request id for every call.
- [ ] Wrap the provider in your own small interface and test it with fakes.
- [ ] Validate and size-limit user messages before forwarding them.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain "stateless" with the forgetful-expert picture. Then say why a streamed answer feels faster although the total time is the same.

## 📐 Design it

SupportDesk AI's chat endpoint must (1) authenticate the user, (2) stream the answer, (3) survive a provider outage for a few minutes, (4) never expose the system prompt or key, and (5) cost no more than 2 cents per conversation turn on average. Design the request flow and the failure handling.

:::quiz
Show a possible design

- **Flow:** browser → `POST /v1/chat` (JWT) → validate and size-limit messages → add the server-side system prompt and retrieved context → call the model with streaming → forward tokens as JSON SSE → log usage → `[DONE]`.
- **Auth and abuse:** verify the JWT, rate-limit per user, cap message count and size, and never accept a system prompt or model name from the client.
- **Errors:** the SDK retries short problems. For 429/5xx after retries, send an error event and a friendly "try again" message. For a longer outage, **fall back** to a second provider or a smaller model behind the same interface, or switch to "we will email you" with the question queued.
- **Mid-stream failure:** the status is already 200, so send `{"error": ...}`, mark the turn as failed in the database, and let the user retry.
- **Cut-off answers:** detect `max_tokens` and offer "continue".
- **Cost:** log `usage` per turn, estimate with the formula from lesson 1, trim old messages, cache the stable system prompt, use a smaller model for easy turns, and alert when the average turn passes 2 cents.
- **Secrets:** key in a secret manager or environment variable; system prompt stored on the server; logs never contain the key or full customer messages.
- **Client disconnect:** stop the model call when the browser goes away.

**Rule shown:** the backend owns the key, the prompt and the limits; the browser only gets a safe stream of tokens.
:::

### 📝 Self-review checklist

- [ ] The key and the system prompt never leave the server
- [ ] Streaming errors and truncation are reported to the client
- [ ] Failures have a retry or fallback plan
- [ ] Usage is logged and cost is estimated

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m7/w1/03-chat-stream" ai="no-ai" title="Conversation and stream reader"}
Build a `Conversation` (alternating roles, separate system prompt, request dict that is a copy), `collect_stream` (join text deltas, ignore thinking and unknown events, read stop reason and tokens, raise on an error event or an early end) and `to_sse` (lazy SSE lines as JSON, a `truncated` flag, an error event with no `[DONE]`). The tests use the real event shapes, so you need no API key.
:::

:::hints
- `Conversation._add(role, text)`: refuse an `assistant` first message and two equal roles in a row.
- `to_request`: copy the messages (`[dict(m) for m in ...]`) and add `"system"` only when it was given.
- `collect_stream`: loop over events by `event["type"]`; for `content_block_delta` check `delta["type"] == "text_delta"`.
- After the loop, no `message_stop` means `StreamError("stream ended early")`.
- `to_sse`: `yield f"data: {json.dumps({'token': text})}\n\n"`; on an error event `yield` the error and `return` (no `[DONE]`).
:::

## ✅ Quick check

:::quiz
The model's answer ends in the middle of a sentence. What do you check first?

Check `stop_reason`. If it is `"max_tokens"`, the answer hit the output limit. Raise `max_tokens`, ask for a shorter answer, or show a "continue" option. Also check that the prompt left room in the context window.
:::

:::quiz
Why do we send tokens as JSON inside SSE instead of raw text?

SSE separates messages with a blank line. If the model writes a blank line inside a token, raw text would split the message and corrupt the stream. JSON escapes newlines, so every message stays one safe line.
:::

:::quiz
Why must the browser call your backend and not the model provider directly?

A key in browser code is visible to everyone, who could then spend your money. Your backend keeps the key and the system prompt secret, checks who the user is, validates and limits the input, and logs usage.
:::

## 📚 Keep learning

- [Anthropic docs: Messages API](https://platform.claude.com/docs/en/api/messages)
- [Anthropic docs: Streaming messages](https://platform.claude.com/docs/en/build-with-claude/streaming)
- [Anthropic docs: Errors](https://platform.claude.com/docs/en/api/errors)

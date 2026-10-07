---
title: "Background Tasks & Streaming Responses"
summary: Do slow work after the response with BackgroundTasks (and know when a real job queue is needed), and send big or slow answers piece by piece with StreamingResponse and Server-Sent Events — the pattern behind AI chat endpoints.
type: lesson
source: original
roles: { be: core, fe: optional, fs: core, ai: recommended, ops: optional }
durationMinutes: 120
tags: [fastapi, background-tasks, streaming, sse, ai]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Run work **after** the response with **`BackgroundTasks`**
- Know the limits: when a background task is the wrong tool
- Send a response **piece by piece** with **`StreamingResponse`**
- Use **Server-Sent Events (SSE)** to push text to a browser
- Why AI endpoints stream, and what can go wrong

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Background task** | A function that runs after the response is sent | Tugas latar belakang |
| **Job queue** | A separate system that stores jobs and runs them reliably | Antrean pekerjaan |
| **Streaming** | Sending the body in small pieces as they are ready | Mengirim sedikit demi sedikit |
| **Generator** | A function that gives values one at a time with `yield` | Fungsi penghasil bertahap |
| **SSE** | A simple text format for the server to push events to a browser | Event dari server ke browser |
| **Token** | A small piece of text an AI model produces | Potongan teks dari model AI |
| **Time to first byte** | How long the user waits before anything appears | Waktu sampai data pertama |

## 🧠 The big idea

A background task is like a **cashier who hands you the receipt first**, then packs your bag while you walk away. You do not wait for the packing. A streaming response is like a **sushi conveyor belt**: the plates arrive one by one while the chef is still cooking, instead of you waiting for the whole meal at the counter.

## ❓ Why it matters

Some work is slow and the user does not need the result right now: sending an email, resizing an image, writing an audit log. Doing it inside the request makes the user wait for nothing. Other work is slow *and* the user wants to see it grow: an AI answer takes ten seconds, but the first words can show in half a second. Streaming makes the app feel fast even when the work is not. Both are daily tools in an AI service, so you need to know what they can and cannot promise.

## 📖 Step by step

### 1. `BackgroundTasks`: work after the response

Add a `BackgroundTasks` parameter and call `add_task` with the function and its arguments. FastAPI sends the response first, then runs the function.

```python
from fastapi import BackgroundTasks, FastAPI

app = FastAPI()

def send_welcome(email: str) -> None:
    ...   # slow: talk to an email service

@app.post("/signup", status_code=201)
def signup(body: SignupIn, background: BackgroundTasks):
    user = create_user(body)                    # the part the user needs
    background.add_task(send_welcome, body.email)
    return {"email": body.email}                # returns right away
```

The user gets `201` in milliseconds. The email goes out a moment later.

### 2. What a background task does *not* promise

A background task runs **inside your web process**. That has costs:

- If the server restarts or crashes, the task is **lost**. Nothing remembers it.
- If it fails, the client already got a success. Nobody retries it.
- It uses the same CPU and memory as your API, so heavy work slows every request.
- There is no way to ask "did it finish?"

Use it for small, **nice-to-have** work: a log line, a cache warm-up, a welcome email you can afford to miss.

### 3. When you need a real job queue

If the work is important, slow, or must be retried, put a job in a **queue** and let a separate **worker** run it.

| Need | Use |
|---|---|
| Small, can be lost, fast | `BackgroundTasks` |
| Must survive a restart, retries, scheduling | a queue: Celery, ARQ or RQ with Redis, or AWS SQS |
| Runs on a timer | a scheduler (cron, EventBridge) |
| Heavy CPU (video, ML) | a worker process or its own service |

You met Redis queues and SQS in Module 5. The API only **adds the job** to the queue and returns; the worker does the rest.

### 4. Streaming with `StreamingResponse`

Give `StreamingResponse` a **generator**. It sends each yielded piece as soon as it exists.

```python
from fastapi.responses import StreamingResponse

def word_events(text: str):
    for word in text.split():
        yield f"data: {word}\n\n"
    yield "data: [DONE]\n\n"

@app.get("/stream")
def stream(text: str):
    return StreamingResponse(word_events(text), media_type="text/event-stream")
```

Nothing is built up in memory first. The same idea works for a huge CSV export: yield row by row, and the server never holds the whole file.

### 5. Server-Sent Events (SSE)

SSE is a plain-text format. Each message is a line starting with `data:` and ends with a **blank line** (`\n\n`). The browser reads it with `EventSource`.

```javascript
const source = new EventSource("/stream?text=hello big world");
source.onmessage = (event) => {
  if (event.data === "[DONE]") return source.close();
  output.textContent += event.data + " ";
};
```

SSE is one-way (server to browser), works over normal HTTP, and reconnects by itself. For two-way chat you would use WebSockets, but for "show the AI answer as it is written" SSE is simpler.

### 6. Why AI endpoints stream

A language model writes **token by token**. A full answer may take 10 seconds. If you wait for all of it, the user stares at a blank screen. If you stream, the first words appear in under a second. The total time is the same; the **time to first byte** is much better.

```python
async def answer_events(question: str):
    async for token in ai_client.stream(question):   # your AI client
        yield f"data: {token}\n\n"
    yield "data: [DONE]\n\n"
```

An `async` generator is the right shape here, because waiting for the next token is I/O (you saw why in the async lesson).

### 7. What can go wrong

- **Proxies buffer.** nginx or a CDN may hold the pieces and send them in one block. Turn buffering off for that route (for nginx, the header `X-Accel-Buffering: no`).
- **Errors mid-stream.** The status code `200` was already sent. Send an error event (`data: {"error": ...}`) so the client can show it.
- **Client leaves.** The user closes the tab. Stop the work, or you pay for tokens nobody reads.
- **Auth.** `EventSource` cannot set an `Authorization` header. Use a cookie, or `fetch` with a stream reader.

### When to use what

| Situation | Do this |
|---|---|
| Send a welcome email, write a log | `BackgroundTasks` |
| Payment receipt, report, anything that must not be lost | a job queue plus a worker |
| Show an AI answer as it is written | `StreamingResponse` + SSE |
| Export a big file | stream it, row by row |
| Two-way live chat | WebSockets |

## ⚠️ Common mistakes

- Using `BackgroundTasks` for important work and losing it on a restart.
- Heavy CPU work in a background task that slows the whole API.
- Building the full answer first, then "streaming" it (no gain).
- Forgetting the blank line (`\n\n`) after each SSE message.
- A proxy that buffers the stream, so the user sees nothing until the end.
- Ignoring errors after the first byte, because the status code is already `200`.

:::revoshop
RevoShop sends order emails and writes audit logs. (1) Find one thing that should happen *after* the response. Is it done inside the request today? (2) Which of those could you afford to lose on a restart (use `BackgroundTasks`), and which could not (use a queue)? (3) Is there any long list or export where streaming would help?
:::

## 🏆 Best practices

- [ ] Use `BackgroundTasks` only for small, losable work.
- [ ] Put important or slow work in a queue with a worker, retries and monitoring.
- [ ] Make tasks **idempotent** (safe to run twice), because retries happen.
- [ ] Stream AI answers; send a final `[DONE]` event and an error event on failure.
- [ ] Turn off proxy buffering for streaming routes and test through the real proxy.
- [ ] Stop the upstream work when the client disconnects.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain `BackgroundTasks` with the receipt-first cashier, and streaming with the sushi belt. Then say when you would not use a background task.

## 📐 Design it

CareerPilot's endpoint `POST /ai/cover-letter` calls an AI model that takes about 12 seconds. Design the flow: what the user sees, whether you stream, what runs in the background (saving the result, sending an email), what needs a queue, and how you handle an error halfway.

:::quiz
Show a possible design

- **Stream the answer:** `GET`/`POST` returns `StreamingResponse` with SSE; tokens appear in under a second. A final `[DONE]` event closes the stream.
- **Save the result:** after the last token, save the letter to the database. A small background task is fine if losing it is acceptable (the user still has the text on screen); otherwise save it before sending `[DONE]`.
- **Email a copy:** this is "nice to have", so `BackgroundTasks` is fine. If it must not be lost, put a job on a queue.
- **Usage billing or audit:** must not be lost → write to a queue or the database in the same transaction, not a background task.
- **Error halfway:** the status is already `200`, so send `data: {"error": "..."}`, then close. The client shows a retry button.
- **Disconnect:** check for a closed connection and cancel the AI call so you do not pay for unread tokens.
- **Proxy:** disable buffering on this route.

**Rule shown:** stream what the user watches; background what they do not need; queue what must not be lost.
:::

### 📝 Self-review checklist

- [ ] Slow work the user waits to see is streamed
- [ ] Only losable work uses `BackgroundTasks`
- [ ] Important work goes through a queue
- [ ] Errors after the first byte are sent as events
- [ ] Proxy buffering and client disconnects are handled

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m3/w3/03-background-stream" ai="no-ai" title="Background welcome email and a streaming endpoint"}
In `signup_stream_app.py`, finish `POST /signup` (reject a bad email with `400` and schedule nothing; otherwise return `201` at once and send the welcome email with `BackgroundTasks`) and `GET /stream` (stream one SSE event per word, then `data: [DONE]`). `word_events` must be a generator.
:::

:::hints
- `background.add_task(send_welcome, body.email)` — pass the function and its arguments, do not call it.
- Raise `HTTPException(status_code=400, ...)` **before** `add_task` so a bad email schedules nothing.
- `word_events`: `for word in text.split(): yield f"data: {word}\n\n"`, then `yield "data: [DONE]\n\n"`.
- `return StreamingResponse(word_events(text), media_type="text/event-stream")`.
:::

## ✅ Quick check

:::quiz
Why is `BackgroundTasks` the wrong tool for sending an important payment receipt?

The task runs inside the web process. If the server restarts or crashes before it runs, the task is gone, and nothing retries it or reports the failure. Important work needs a job queue and a separate worker, which store the job durably and retry it.
:::

:::quiz
Why does streaming an AI answer improve the user's experience even though the total time is the same?

The model writes token by token, so the first words are ready in well under a second. Streaming shows them at once instead of after the whole answer. The user sees progress right away (better time to first byte) and can start reading while the rest is still being written.
:::

## 📚 Keep learning

- [FastAPI: Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [FastAPI: Custom Response — StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [MDN: Using server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events)

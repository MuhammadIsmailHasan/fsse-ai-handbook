---
title: "Running Local Models with Ollama"
summary: "Run an open-weight model on your own computer with Ollama — what you gain and give up, how much memory you need, how to call its HTTP API from Python, and how to wrap it with a cloud fallback."
type: lesson
source: original
roles: { be: optional, fe: optional, fs: recommended, ai: core, ops: optional }
durationMinutes: 150
tags: [llm, ollama, local-models, open-weight, quantization, privacy]
lastReviewed: 2026-10
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What an **open-weight model** is, and what **Ollama** does
- When a **local model** is a good idea, and when it is not
- How much **memory** a model needs (quantization)
- Calling Ollama's **HTTP API** and reading its streamed answer
- A **fallback client** so your app survives when the local model is down

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Open-weight model** | A model whose weights (its learned numbers) you can download | Model berbobot terbuka |
| **Ollama** | A tool that downloads and runs open models on your computer | Alat menjalankan model lokal |
| **Parameters** | The learned numbers in a model; "7B" means 7 billion | Parameter |
| **Quantization** | Storing the numbers with fewer bits so the model is smaller | Kuantisasi |
| **VRAM** | Memory on the graphics card; fast for models | Memori kartu grafis |
| **NDJSON** | One JSON object per line: how Ollama streams | JSON per baris |
| **Fallback** | A second option used when the first one fails | Cadangan |
| **License** | The rules for how you may use the model | Lisensi |

## 🧠 The big idea

Using a cloud model is like **ordering food delivery**: no kitchen to run, great variety, and you pay per order. Running a local model is like **cooking at home**: the ingredients are on your shelf, nobody sees what you eat, and a second plate costs almost nothing — but you need a kitchen, you do the cleaning, and you probably cannot cook what a top restaurant can.

Ollama is the **kitchen appliance** that makes home cooking easy: one command to get a recipe (download a model), one command to cook (run it), and a small web API so your programs can place an order.

## ❓ Why it matters

Local models give you things the cloud cannot:

- **Privacy:** private text never leaves your machine (useful for health, legal, internal documents, or just practice with real data).
- **Cost shape:** after you have the hardware, each extra request is free. Great for learning, testing and bulk jobs.
- **Offline:** works on a plane or in a closed network.
- **Control:** you choose the exact model file and it never changes under you.

And they have real limits: smaller models are usually weaker, they can be slow without a good GPU, and you must run and update them. A good engineer knows both sides and can **build an app that uses either**.

## 📖 Step by step

### 1. Install and run

Follow the install page on the Ollama website for your system (macOS, Windows or Linux). Then, in a terminal:

```bash
ollama pull llama3.2        # download a model once (example name; pick a size your computer can run)
ollama run llama3.2         # chat in the terminal; type /bye to leave
ollama list                 # see what you have downloaded
```

Ollama also starts a small server on your machine, **port 11434 by default**. If that port is taken, or you like unusual ports, set `OLLAMA_HOST` (for example `127.0.0.1:11491`) before starting it. Keep it bound to `127.0.0.1`: the local server has **no login**, so never expose it to the internet.

### 2. How big a model can your computer run?

A model is a huge list of numbers. Memory needed is roughly:

```text
memory ≈ number of parameters × bytes per parameter   (+ room for the conversation)

7 billion parameters, 16-bit  → about 14 GB
7 billion parameters, 4-bit   → about 4–5 GB     ← "quantized": the usual way to run locally
70 billion parameters, 4-bit  → about 40 GB
```

**Quantization** stores each number with fewer bits. The file shrinks a lot, and quality drops only a little for 4–8 bit versions. Models are often published in several sizes and quantizations, and a model's page shows what each needs.

Rules of thumb:

- If it fits in **GPU memory** (or Apple Silicon's shared memory), it is fast.
- If it spills into normal RAM, it still runs, but **much slower**.
- If it does not fit at all, pick a smaller model.
- The conversation (the *context*) also uses memory. Defaults for the context size are small, so set the context size on purpose when your prompts are long, or the start of your prompt can be dropped without an error.

Speed is measured in **tokens per second**. The final line of a response includes counts and timings, so you can measure your own machine.

### 3. Ollama's HTTP API

Your code talks to the local server with plain HTTP:

```text
POST http://localhost:11434/api/chat
{"model": "llama3.2",
 "messages": [{"role": "user", "content": "Hi"}],
 "stream": true,
 "options": {"temperature": 0.2}}
```

The answer comes as **NDJSON**: one JSON object per line.

```text
{"message": {"role": "assistant", "content": "Hel"}, "done": false}
{"message": {"role": "assistant", "content": "lo"},  "done": false}
{"message": {"role": "assistant", "content": ""},    "done": true, "done_reason": "stop", "prompt_eval_count": 14, "eval_count": 6}
```

Join the `content` of each line. The last line has `"done": true`, why it stopped, and the token counts (`prompt_eval_count` is input, `eval_count` is output). An error comes as `{"error": "..."}`.

```python
import json

def collect_ollama_stream(lines):
    text, done = [], None
    for line in lines:
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            raise LocalModelError("bad line from the model server") from None
        if "error" in obj:
            raise LocalModelError(obj["error"])
        text.append(obj.get("message", {}).get("content", ""))
        if obj.get("done"):
            done = obj
            break
    if done is None:
        raise LocalModelError("stream ended early")
    return {
        "text": "".join(text),
        "done_reason": done.get("done_reason", ""),
        "prompt_tokens": done.get("prompt_eval_count", 0),
        "completion_tokens": done.get("eval_count", 0),
    }
```

The same ideas as the cloud stream: join the pieces, treat an error line as an error, and treat a stream with no final `done` line as a failure.

Ollama also offers an **OpenAI-compatible** endpoint and an official Python library. Those are convenient, but knowing the plain HTTP shape helps you debug anything.

### 4. Put a small interface in front of it

Your app should not care where the answer came from. Define one tiny interface and write two implementations:

```python
class OllamaClient:
    def __init__(self, model, post, host="http://localhost:11434", options=None):
        self.model, self.post, self.host, self.options = model, post, host.rstrip("/"), options

    def complete(self, messages):
        payload = build_chat_payload(self.model, messages, options=self.options)
        try:
            lines = self.post(self.host + "/api/chat", payload)
            return collect_ollama_stream(lines)["text"]
        except ConnectionError:
            raise LocalModelError("local model server is not running") from None
```

Passing `post` in (instead of importing an HTTP library inside) is **dependency injection** again: tests give it a fake and need no Ollama.

### 5. Fallback to the cloud

A local model can be off, busy, or too weak for one request. Wrap two clients:

```python
class FallbackClient:
    def __init__(self, primary, secondary):
        self.primary, self.secondary, self.last_used = primary, secondary, None

    def complete(self, messages):
        try:
            answer = self.primary.complete(messages)
            self.last_used = "primary"
            return answer
        except (LocalModelError, ConnectionError):
            answer = self.secondary.complete(messages)
            self.last_used = "secondary"
            return answer
```

Notice what it catches: only the errors that mean "the local server is unavailable". A `ValueError` from your own bug must **not** be hidden. Also record `last_used`, so you can see how often the fallback happens and what it costs.

Decide the fallback rules with your **data rules** in mind. If the reason for using a local model was privacy, silently sending the same private text to a cloud provider breaks that promise. Make the fallback explicit (a setting, a log line, or "ask the user first").

### 6. Where local models fit

| Good fit | Not a good fit |
|---|---|
| Learning, experiments, demos without a bill | hard reasoning where quality is everything |
| Private text (with the right hardware) | high traffic from many users on a small server |
| Bulk, repetitive jobs (tagging, rough drafts) | tasks that need the latest big-model skills |
| Offline tools, edge devices | when you cannot run and update servers |
| Embedding and small classification models | long, complex agent loops |

Check the **license** of any model before using it in a product. Some are free for any use, some have limits (company size, field of use, naming rules).

### Choosing your setup

| Situation | Do this |
|---|---|
| Practice without spending money | Ollama + a small model |
| Private data, strict rules | local model, tested on your real examples; explicit about fallbacks |
| Production with many users | cloud API (or serious self-hosting with GPUs and monitoring) |
| Unsure it is good enough | run your 30-row test set on the local model first |
| Local model might be down | `FallbackClient`, and log which one answered |
| Different tasks, different needs | route: easy → local, hard → cloud |

- ✅ Keep the server on `127.0.0.1`; use a non-default port if you like.
- ✅ Measure tokens per second and quality on **your** examples.
- 🚫 Exposing Ollama to the internet.
- 🚫 A silent cloud fallback for data that must stay private.

## ⚠️ Common mistakes

- Picking a model too big for the machine, then wondering why it crawls.
- Leaving the context size small, so long prompts lose their beginning.
- Treating "the model is local" as "the app is secure".
- Catching every exception in the fallback (hiding real bugs).
- Not checking the license.
- Comparing a small local model to a large cloud model and expecting equal quality.
- Hard-coding `localhost:11434` everywhere instead of one setting.

:::revoshop
RevoShop has customer addresses and phone numbers. Choose one AI task (for example tagging support messages) and decide: local model, cloud model, or both with a fallback? Write down the data rule that decides it, the hardware you would need, and what the fallback should do when the local model is off.
:::

## 🏆 Best practices

- [ ] Hide the model behind one small interface (`complete(messages) -> text`).
- [ ] Put host, port, model name and options in configuration.
- [ ] Bind local servers to `127.0.0.1`; never expose them without authentication.
- [ ] Measure speed and quality on your own examples before choosing.
- [ ] Make fallbacks explicit, logged, and respectful of data rules.
- [ ] Catch only "server unavailable" errors in the fallback; let bugs surface.
- [ ] Check the model license and pin the model name and version.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain the delivery-versus-home-cooking picture to a manager. Give one reason to choose the local option and one reason against it.

## 📐 Design it

A law firm wants an assistant that summarizes client documents. The documents must **never leave the firm's network**. The firm has one office server with a single GPU. Design the setup: which kind of model, how the app talks to it, what happens when it is slow or down, how you measure quality, and what you refuse to do.

:::quiz
Show a possible design

- **Model:** an open-weight model, quantized to fit the GPU memory, served by Ollama (or a similar server) **inside the office network**, bound to the internal address with authentication in front (a reverse proxy with login), not open to the internet.
- **App:** a small backend with the same `complete(messages)` interface; the browser never talks to the model directly.
- **Quality:** a test set of ~30 real (anonymised or approved) documents with checklist-style expected points; compare two or three sizes for quality and tokens per second; accept a slower, bigger model if summaries are not time-critical.
- **Slow documents:** process long files in chunks (map-reduce summary), use a queue so one big job does not block others, and show progress.
- **Down or overloaded:** **no cloud fallback**, because of the data rule. Instead: queue the job, retry, and tell the user "will be ready in N minutes". Alert the administrator.
- **Context size:** set it on purpose so long documents are not silently cut.
- **Privacy:** log metadata only (timings, token counts), never document text; encrypt the disk; restrict who can call the service.
- **Licence:** confirm the model licence allows commercial use for a firm like this.
- **Refuse:** sending any document text to an outside API, even "just for the hard cases", unless the firm and the client explicitly approve.

**Rule shown:** the data rule decides the architecture; the fallback must not break it.
:::

### 📝 Self-review checklist

- [ ] The data rule is written down and respected
- [ ] The model size matches the hardware
- [ ] Slow and down cases have a plan
- [ ] Quality was measured on real examples

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m7/w1/05-local-llm" ai="no-ai" title="A local model client with a cloud fallback"}
Build `build_chat_payload`, `collect_ollama_stream` (read the NDJSON lines, handle blank lines, error lines, bad lines and an early end), `OllamaClient` (the HTTP call is passed in as `post`) and `FallbackClient` (fall back only on local-server errors; record which client answered). No Ollama needed: the tests use fake lines and fake clients.
:::

:::hints
- `build_chat_payload`: copy the messages with `[dict(m) for m in messages]`; add `"options"` only when it is not empty.
- `collect_ollama_stream`: `json.loads` each non-blank line; an `"error"` key raises `LocalModelError`; stop at the line with `"done": true`.
- `OllamaClient.complete`: URL is `host.rstrip("/") + "/api/chat"`; turn `ConnectionError` into `LocalModelError("local model server is not running")`.
- `FallbackClient`: `except (LocalModelError, ConnectionError)` only; set `last_used` after each success.
:::

## ✅ Quick check

:::quiz
What is quantization, and why does it matter for local models?

Quantization stores the model's numbers with fewer bits (for example 4-bit instead of 16-bit). The file and the memory needed shrink a lot, while quality drops only a little. It is what lets a model with billions of parameters fit on an ordinary computer.
:::

:::quiz
Why should a fallback catch only "server unavailable" errors?

If it caught every exception, real bugs in your own code (like a `ValueError`) would be hidden by silently switching to the cloud, and you would never notice or fix them. Catch only the errors that mean the local service cannot answer.
:::

:::quiz
When can a cloud fallback be the wrong choice?

When the reason for choosing a local model was privacy or a legal rule. A silent fallback would send the private text to an outside provider and break that promise. In that case queue the job, retry, or ask for approval instead.
:::

## 📚 Keep learning

- [Ollama: documentation](https://github.com/ollama/ollama/tree/main/docs)
- [Ollama: API reference](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [Hugging Face: Quantization overview](https://huggingface.co/docs/transformers/main/en/quantization/overview)

---
title: "Tokens, Context Window & Temperature"
summary: "See how a language model really works — it reads and writes tokens, has a limited context window, predicts the next token with some randomness — and learn to count tokens, estimate cost, trim chat history and choose temperature."
type: lesson
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: core, ops: optional }
durationMinutes: 150
tags: [llm, tokens, context-window, temperature, cost]
lastReviewed: 2026-10
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What a **token** is, and why tokens (not words) set your **cost** and **limits**
- What the **context window** is, and why long chats must be trimmed
- Why a model **predicts** the next token, and what that means for facts
- What **temperature** does, and when to change it
- How to **count tokens** and **estimate the price** of a call

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **LLM** | A model trained on lots of text to predict what comes next | Model bahasa besar |
| **Token** | A small piece of text: a word, part of a word, or a symbol | Potongan teks |
| **Context window** | The most tokens the model can read and write in one call | Jendela konteks |
| **Prompt** | The text you send to the model | Perintah / masukan |
| **Completion** | The text the model sends back | Jawaban model |
| **Temperature** | A dial for how random the next-token choice is | Tingkat keacakan |
| **Logits** | The raw scores the model gives to every possible next token | Skor mentah |
| **Hallucination** | A fluent answer that is not true | Jawaban meyakinkan tapi salah |

## 🧠 The big idea

A language model is a **very fast autocomplete with a huge memory of how text looks**. You give it text. It picks the most likely next piece, adds it, and repeats until it stops. It does not "look up" facts. It writes what fits.

Three pictures help:

- **Tokens are Lego pieces.** The model does not see letters or words. It sees small pieces. You pay per piece, and the box has a size limit.
- **The context window is a desk.** Everything the model can think about must fit on the desk: your question, the chat so far, the documents you pasted, **and the space for its answer**. When the desk is full, something must go.
- **Temperature is a dial** between a strict exam-marker (always the safest word) and an improv actor (more surprises).

## ❓ Why it matters

Every real AI feature hits these three things:

- **Cost.** You are billed per token, input and output. A chat that resends 40 messages every turn gets expensive fast.
- **Limits.** If the prompt plus the answer does not fit in the window, the call fails or the answer is cut off.
- **Reliability.** If you forget that the model *predicts*, you trust invented facts. If you leave randomness high for an extraction task, the same input gives different results.

An engineer who knows these can estimate a bill before shipping, keep a chat inside the limit, and explain a wrong answer.

## 📖 Step by step

### 1. Text becomes tokens

The model splits text into tokens with a fixed vocabulary (a *tokenizer*). Common words are one token. Rare words, names and code break into several pieces.

```text
"Hello world"            → 2 tokens
"unbelievably"           → maybe 3 tokens:  "un" "believ" "ably"
"Terima kasih banyak"    → often MORE tokens than the English "Thank you very much"
```

Rules of thumb for English: **1 token ≈ 4 characters ≈ ¾ of a word**. Other languages, code, and numbers usually need **more** tokens for the same meaning. Indonesian text costs somewhat more than English for the same idea, so measure with your own text.

Different model families use different tokenizers. Your estimate is a guess. For a real number, ask the provider:

```python
count = client.messages.count_tokens(
    model=MODEL,
    messages=[{"role": "user", "content": "Explain recursion in one sentence."}],
)
print(count.input_tokens)
```

And after every call, the response tells you what you were charged for:

```python
response = client.messages.create(model=MODEL, max_tokens=500, messages=messages)
print(response.usage.input_tokens, response.usage.output_tokens)
```

Log these two numbers for **every** request. They are the base of every cost and speed investigation.

### 2. The context window is shared

The window counts **everything**: system prompt, all earlier messages, your new message, tool results, **and the answer the model will write**.

```text
context window  =  system prompt + chat history + new message + [room for the answer]
```

Two limits are different:

| Limit | Meaning |
|---|---|
| **Context window** | input + output together |
| **`max_tokens`** | the most the model may *write* in this call |

If the answer reaches `max_tokens`, it stops mid-sentence and `stop_reason` is `"max_tokens"`. Check this value. A silently cut answer is a common bug.

Windows have grown very large (hundreds of thousands to a million tokens on some current models), but a bigger window is not free:

- you **pay** for every input token on **every** call,
- long prompts are **slower**,
- models can miss a detail buried in the middle of a very long input.

So the goal is not "fill the window". It is "put the *right* tokens in".

### 3. Keep a chat inside the window

The API remembers nothing. You resend the whole conversation each turn, so it only grows. A simple, honest strategy:

1. Keep the **system prompt** always.
2. Keep the **latest messages**.
3. Drop the **oldest** turns first (or replace them with a short summary).
4. Reserve room for the answer.

```python
MESSAGE_OVERHEAD = 4

def total(messages):
    return sum(estimate_tokens(m["content"]) + MESSAGE_OVERHEAD for m in messages)

def fit_history(messages, max_context, reserve_for_output):
    budget = max_context - reserve_for_output
    system = [messages[0]] if messages and messages[0]["role"] == "system" else []
    rest = list(messages[len(system):])
    while len(rest) > 1 and (total(system + rest) > budget or rest[0]["role"] == "assistant"):
        rest.pop(0)                      # oldest first; the chat must start with a user message
    return system + rest
```

Better options for long chats: **summarize** old turns into one short message, store facts in a **memory** the app controls, or **retrieve** only the relevant old messages (a later week). Provider features such as prompt caching make a long, stable prefix cheaper.

### 4. The model predicts; it does not look things up

For every next position the model gives a score (a *logit*) to **every token in its vocabulary**. A function called *softmax* turns the scores into probabilities. Then one token is picked.

```text
after "The capital of France is" →  " Paris" 96%   " a" 1%   " the" 1% ...
```

When the model has seen a fact many times, the true answer wins. When it has not, a fluent but wrong answer can win. That is a **hallucination**. The model has no built-in alarm for "I don't know".

What helps (all later in this module): put the real source in the prompt (RAG), ask for citations, validate the output, let the model call tools, and write evals.

### 5. Temperature: how adventurous is the pick?

Before softmax, the scores are divided by the **temperature**:

```python
import math

def apply_temperature(logits, temperature):
    if temperature == 0:                       # always the best token
        best = max(logits, key=lambda k: logits[k])
        return {k: (1.0 if k == best else 0.0) for k in logits}
    top = max(logits.values())                 # subtract the max so exp() cannot overflow
    weights = {k: math.exp((v - top) / temperature) for k, v in logits.items()}
    total = sum(weights.values())
    return {k: w / total for k, w in weights.items()}
```

```text
scores  a=2.0  b=1.0  c=0.0
T = 0.3 → a 0.96  b 0.03  c 0.00     sharp: almost always "a"
T = 1.0 → a 0.67  b 0.24  c 0.09
T = 3.0 → a 0.45  b 0.32  c 0.23     flat: more surprises
```

| Task | Temperature |
|---|---|
| Extraction, classification, JSON, code, SQL | low (0 – 0.3) |
| Q&A over documents | low |
| Writing, brainstorming, names, variations | medium to high |

Two honest cautions:

1. **Even at 0 the output is not guaranteed identical.** Servers do maths in parallel and the order of tiny additions can change. Never build logic that needs byte-identical text.
2. **Some current models do not let you set it.** Several newer models reject sampling settings such as `temperature` and `top_p`, and give you other controls (for example an *effort* setting) instead. Read the docs of the model you use. Your prompt and your validation matter more than this dial.

(`top_p` is a cousin: it only considers the smallest group of tokens whose probabilities add up to *p*. Change one of the two dials, not both.)

### 6. Cost: a small formula

Providers publish prices **per million tokens**, and **output tokens cost more than input tokens** (several times more is common).

```python
def request_cost(input_tokens, output_tokens, input_price_per_m, output_price_per_m):
    return input_tokens * input_price_per_m / 1_000_000 + output_tokens * output_price_per_m / 1_000_000
```

An illustration (not a real price list): input $3 per million, output $15 per million. A call with 2,000 tokens in and 500 out costs 0.006 + 0.0075 = **$0.0135**. At 10,000 calls a day that is **$135 a day**. Multiply before you ship, not after.

Ways to cut cost without losing quality: shorter prompts, a smaller model for easy tasks (next lesson), prompt caching for repeated prefixes, a lower `max_tokens`, and not resending what the model does not need.

Prices and model names change often. Look at the provider's pricing page when you build, and keep prices in config, not in code.

### Choosing your setup

| Situation | Do this |
|---|---|
| Need an exact token count | the provider's count endpoint, or `usage` in the response |
| Quick estimate | about 4 characters per token (English) — and add a safety margin |
| Chat getting long | drop oldest turns, summarize, or retrieve |
| Output cut mid-sentence | check `stop_reason`; raise `max_tokens`; shorten the answer |
| Same input must give a stable result | low temperature, plus validation (not exact repeatability) |
| Creative variations | higher temperature, or ask for several options |

- ✅ Log `input_tokens` and `output_tokens` for every call.
- ✅ Reserve room for the answer before you trim the history.
- 🚫 Trusting a fluent answer as a fact.
- 🚫 Resending a whole 200-message history because "the window is big".

## ⚠️ Common mistakes

- Counting words or characters and calling it tokens, then being surprised by the bill.
- Forgetting that the **output** counts toward the window.
- Not checking `stop_reason == "max_tokens"`.
- Dropping the system prompt when trimming, or starting the chat with an assistant message.
- Setting a high temperature for extraction or JSON.
- Assuming temperature 0 means identical output every time.
- Putting prices as numbers inside the code instead of config.

:::revoshop
Think about a "ask about this order" assistant for RevoShop. (1) What goes into each call: system prompt, order JSON, chat history? Estimate the tokens of each part (4 characters ≈ 1 token). (2) If 1,000 customers each send 5 questions a day, what is the daily input and output token count? (3) Which part would you shrink first to save money, and which part must never be trimmed?
:::

## 🏆 Best practices

- [ ] Log token usage and cost per request, per feature.
- [ ] Estimate the cost of a feature on paper before building it.
- [ ] Reserve output space, and handle `stop_reason == "max_tokens"` explicitly.
- [ ] Trim history from the oldest, keep the system prompt and the latest turn.
- [ ] Use low randomness for structured and factual tasks, and validate the output anyway.
- [ ] Keep prices and model names in configuration; re-check them regularly.
- [ ] Treat every model answer as a **claim to verify**, not a fact.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a non-technical teammate why the AI "forgot" what the customer said 30 messages ago, using the desk picture. What are two fixes?

## 📐 Design it

SupportDesk AI keeps a long chat with each customer. A conversation can reach 60 messages. Each call includes a 1,500-token system prompt and help-article snippets of about 3,000 tokens. Design how you keep each call under budget, keep answers from being cut off, and keep the monthly cost predictable.

:::quiz
Show a possible design

- **Budget per call:** decide a cap (for example 8,000 input tokens) and reserve about 1,000 for the answer. Count with `count_tokens` or use `usage` from earlier calls.
- **Always keep:** the system prompt and the latest user message.
- **Trim:** drop the oldest turns first; keep the chat starting with a user message. For very long chats, replace old turns with a **short running summary** (updated every N turns) and keep the last 6–10 messages verbatim.
- **Retrieve, do not paste:** include only the 2–3 most relevant help-article snippets for *this* question, not the whole knowledge base.
- **Cache the stable prefix:** the system prompt and fixed instructions are the same every call, so use prompt caching if the provider supports it.
- **Do not cut answers:** set `max_tokens` high enough; if `stop_reason == "max_tokens"`, show "continue" or retry with a shorter-answer instruction.
- **Cost control:** log tokens per conversation, set a per-conversation limit and an alert on the daily total, and use a smaller model for easy classification steps.
- **Low temperature** for answers that must follow policy.

**Rule shown:** the window is a shared, paid desk — decide what earns a place on it.
:::

### 📝 Self-review checklist

- [ ] I reserved room for the answer
- [ ] The system prompt and the latest turn are never dropped
- [ ] Long history is summarized or retrieved, not just resent
- [ ] Token usage is logged and the monthly cost is estimated

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m7/w1/01-token-budget" ai="no-ai" title="Token budget, cost and temperature"}
Write four small tools: `estimate_tokens` (about 4 characters per token), `request_cost`, `fit_history` (trim the oldest messages, keep the system message and the last message, start with a user message) and `apply_temperature` (softmax with a temperature, including temperature 0 and no overflow). No API key is needed.
:::

:::hints
- `estimate_tokens`: `math.ceil(len(text) / 4)`.
- `request_cost`: tokens × price ÷ 1,000,000 for input and for output.
- `fit_history`: budget = `max_context - reserve_for_output`; pop the **first** non-system message while the total is over budget or the first message is from the assistant; keep at least the last message.
- A message costs `estimate_tokens(content) + MESSAGE_OVERHEAD`.
- `apply_temperature`: handle `0` first (one-hot); otherwise subtract the largest logit before `math.exp`.
:::

## ✅ Quick check

:::quiz
Why is the answer part of the context-window budget?

The window limits input and output together. The model writes its answer into the same window, so if the prompt already fills most of it, there is little room left, and the answer is cut off at the limit (`stop_reason: "max_tokens"`). Always reserve space for the output.
:::

:::quiz
What does lowering the temperature do?

It makes the probability distribution sharper: the highest-scoring tokens become even more likely, so the output is more predictable. At 0 the model always picks the top token. It helps for extraction and structured output, but it does not guarantee identical results or true facts.
:::

:::quiz
A model gives a confident answer that is false. Why can this happen?

The model predicts a likely continuation of the text; it does not check facts. If the right answer was rare in training or is missing from the prompt, a fluent but wrong continuation can have the highest probability. Fix it by giving sources (RAG), asking for citations, validating output and using evals.
:::

## 📚 Keep learning

- [Anthropic docs: Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting)
- [Anthropic docs: Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows)
- [Anthropic docs: Pricing](https://platform.claude.com/docs/en/about-claude/pricing)

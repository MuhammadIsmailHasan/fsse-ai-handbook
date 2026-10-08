---
title: "Prompt Caching"
summary: "Pay much less for the part of a prompt you send again and again — how prefix caching works, where to put the breakpoint, what silently breaks it, how long it lives, and how to check that it really hits."
type: lesson
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: core, ops: optional }
durationMinutes: 150
tags: [llm, prompt-caching, cost, latency, optimization]
lastReviewed: 2026-10
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What **prompt caching** is and why it saves money **and** time
- Why it is a **prefix match**, and what that means for how you order a prompt
- Where to put the **breakpoint**
- The cost rules: **write**, **read**, **TTL**, **minimum length**
- The **silent invalidators** that give you zero hits
- How to **verify** that caching works

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Prompt caching** | The provider remembers the start of your prompt so you do not pay full price to send it again | Cache prompt |
| **Prefix** | The beginning of the prompt, up to some point | Awalan |
| **Breakpoint** | The marker (`cache_control`) that says "cache everything up to here" | Titik cache |
| **Cache write** | The first time a prefix is stored (a little more expensive) | Menulis cache |
| **Cache read** | Reusing a stored prefix (much cheaper) | Membaca cache |
| **TTL** | How long a stored prefix lives without being used | Masa hidup cache |
| **Invalidation** | A change that makes the stored prefix useless | Cache tak berlaku |
| **Cache hit rate** | The share of input tokens that were read from cache | Tingkat keberhasilan |

## 🧠 The big idea

Imagine a teacher who gives the **same 20-page handout** to every student, then asks each one a different question. Without caching, the teacher re-reads all 20 pages aloud for each question. With caching, the teacher says, "You remember the handout from before; here is only the new question." Reading the handout once costs a bit extra. Every later question is cheap and starts faster.

But there is a catch: the teacher only recognises the handout if it is **word for word identical, from the first page**. If someone changes the first line (say, a date stamp), the teacher cannot tell it is the same handout, and starts again.

## ❓ Why it matters

Many AI apps send a **big, repeated start** on every call:

- a long system prompt with rules and examples,
- tool definitions,
- a policy document or product manual,
- the earlier part of a long conversation.

You pay for those input tokens every single time, and you wait for them to be processed. Caching typically makes the repeated part **around ten times cheaper** and noticeably **faster to first token**. For a support bot with a 6,000-token fixed prompt and 20,000 requests a day, that is a large part of the bill.

It costs nothing to use except careful prompt design, which you should be doing anyway.

## 📖 Step by step

### 1. A prefix match

The cache key is the **exact text from the start of the prompt up to the breakpoint**. Any change anywhere in that stretch means a miss for everything from that point on.

```text
prompt order:   [ tools ] [ system prompt ] [ messages... ]
                └── the provider builds the prefix in this order ──┘

example:        [ tools ][ rules + examples ][ policy document ][ the user's question ]
                └────────────── stable: cache it ──────────────┘└─ changes: not cached ─┘
                                                  ▲
                                          breakpoint here
```

Design rule: **stable things first, changing things last.** Sort the parts of your prompt by how often they change.

| Changes... | Examples | Where |
|---|---|---|
| never | tool definitions, base rules | first |
| per deployment or per day | policy document, product catalogue summary | after those |
| per session | the user's profile, the conversation so far | later |
| per request | the question, a timestamp, a request id | **last** (or leave out) |

### 2. Turn it on

The simplest way is one top-level marker. The provider caches up to the last cacheable block:

```python
response = client.messages.create(
    model=settings.llm_model,
    max_tokens=1000,
    cache_control={"type": "ephemeral"},        # automatic: cache the stable prefix
    system=LONG_SYSTEM_PROMPT,
    messages=[{"role": "user", "content": question}],
)
```

Or place the marker yourself on a block, for fine control:

```python
response = client.messages.create(
    model=settings.llm_model,
    max_tokens=1000,
    system=[
        {
            "type": "text",
            "text": LONG_SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},     # cache everything up to and including this block
        }
    ],
    messages=[{"role": "user", "content": question}],
)
```

For a shared document with a varying question, put the marker on the **document**, not on the question:

```python
messages=[{
    "role": "user",
    "content": [
        {"type": "text", "text": POLICY_DOCUMENT, "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": question},                  # no marker: different every time
    ],
}]
```

If you put the marker after the question, every request writes a **new** cache entry (the prefix includes the question) and nothing is ever read. That is the most common beginner mistake.

For a **long chat**, put the breakpoint on the last block of the newest turn. Each new request then reuses the whole earlier conversation.

(There is a limit on how many markers one request may have; a few are enough.)

### 3. The money rules

| Event | Cost compared with a normal input token |
|---|---|
| Uncached input | 1× |
| **Cache write** (first time, 5-minute life) | about **1.25×** (a small extra) |
| **Cache write**, 1-hour life | about **2×** |
| **Cache read** | about **0.1×** (some newer models are even cheaper) |

Exact numbers differ by model and change over time, so check the pricing page. Break-even with the 5-minute life: **two requests** are enough (1.25 + 0.1 = 1.35 against 2.0 uncached). A prompt used only once loses a little money.

```python
def prompt_cost(usage, input_price_per_m, read_multiplier=0.1, write_multiplier=1.25):
    weighted = usage["read"] * read_multiplier + usage["write"] * write_multiplier + usage["uncached"]
    return weighted * input_price_per_m / 1_000_000
```

Other rules:

- **TTL (time to live):** by default a stored prefix lives about **5 minutes**, and **every read refreshes the timer**. Steady traffic keeps it alive. An optional **1-hour** life costs more to write; it only pays off when requests are spread out, with gaps longer than 5 minutes.
- **Minimum length:** a prefix shorter than a model-specific minimum is **not cached, and you get no error**. The minimum differs per model (from about 500 to a few thousand tokens), so read the docs for yours.
- **Per model:** the cache belongs to one model. Switching models starts from zero.
- **Isolation:** a cache entry is private to your organization/workspace; other customers never read yours.

### 4. Simulate it, to understand it

The exercise builds a small simulator. Its core rule:

```python
def simulate_cache(requests, ttl_s=300, min_tokens=1024):
    store = {}
    results = []
    for request in requests:
        t, blocks, bp = request["t"], request["blocks"], request["breakpoint"]
        tokens = [block_tokens(b) for b in blocks]
        if bp is None:
            results.append({"read": 0, "write": 0, "uncached": sum(tokens)})
            continue
        key = tuple(blocks[: bp + 1])                    # the prefix, exactly
        prefix_tokens = sum(tokens[: bp + 1])
        after = sum(tokens[bp + 1 :])
        last = store.get(key)
        if last is not None and t - last <= ttl_s:       # hit: also refreshes the timer
            store[key] = t
            results.append({"read": prefix_tokens, "write": 0, "uncached": after})
        elif prefix_tokens >= min_tokens:                # miss, long enough: write
            store[key] = t
            results.append({"read": 0, "write": prefix_tokens, "uncached": after})
        else:                                            # too short: no caching at all
            results.append({"read": 0, "write": 0, "uncached": after + prefix_tokens})
    return results
```

Play with it and you will see the rules: a date stamp at the top means no hits; a breakpoint after the changing question caches nothing useful; a gap above the TTL means paying the write again.

### 5. Silent invalidators

These make caching quietly stop working. The API gives no warning, you just do not save:

| Culprit | Example | Fix |
|---|---|---|
| A timestamp or date at the top | `f"Today is {now}"` in the system prompt | move it to the end, or drop it |
| A request id or random id in the prefix | trace id in the system prompt | pass it in headers/metadata, not in the prompt |
| Unstable ordering | tools or JSON keys in a different order each time (a `set`, an unsorted dict) | sort them; build the list the same way every time |
| Changing the system prompt per user | the user's name inside the system prompt | keep the system prompt fixed; put user details after the breakpoint |
| Editing earlier messages | trimming or rewriting old turns | append only; summarize at a controlled moment |
| Different tool set per request | tools added or removed | keep one stable list |
| Prefix below the minimum | a short system prompt | add the breakpoint later in the prompt, or accept no caching |
| Changing a setting that is part of the prefix | thinking or effort changes that reset the cache | keep those settings stable within a session |

`first_difference(prev, current)` in the exercise finds the first block that changed between two requests: that is where your invalidator is.

### 6. Verify it with real numbers

Never assume. Read the usage numbers from the response:

```python
usage = response.usage
print(usage.cache_creation_input_tokens)   # tokens written this time (costs a little extra)
print(usage.cache_read_input_tokens)       # tokens read from cache (cheap)
print(usage.input_tokens)                  # tokens processed normally (after the last breakpoint)
```

Send the same request twice within a few minutes. The second call should show a large `cache_read_input_tokens`. **If it stays at 0**, look for a silent invalidator from section 5, then check the minimum length. Log these three numbers for every request, and chart the **hit rate** = reads ÷ (reads + writes + uncached).

### 7. When caching is worth it

| Situation | Worth it? |
|---|---|
| Long fixed system prompt, many requests | yes, the classic case |
| A big document asked many questions | yes |
| A long conversation | yes (cache the growing prefix) |
| Few requests with long gaps (more than the TTL) | maybe use the 1-hour life, or skip |
| A short prompt, below the minimum | no effect |
| Every request has a different long document | no, nothing repeats |

### Choosing your setup

| Situation | Do this |
|---|---|
| Fixed system prompt and tools | breakpoint after the system prompt |
| One document, many questions | breakpoint on the document, question after it |
| Long chat | breakpoint on the last block of the latest turn |
| Traffic is spread thin | consider the 1-hour life, or schedule a "keep warm" call |
| Hit rate is 0 | look for silent invalidators; check minimum length |
| Prompt has dynamic parts | sort stable → changing; dynamic data last |

- ✅ Order the prompt by how often each part changes.
- ✅ Log cache read/write tokens and track the hit rate.
- 🚫 A timestamp or request id at the top of the prompt.
- 🚫 A breakpoint after the part that changes.

## ⚠️ Common mistakes

- Placing the marker after the varying question.
- A date, time, user name or trace id inside the system prompt.
- Tools or JSON keys in a non-deterministic order.
- Changing earlier messages instead of only appending.
- Expecting caching on a prompt shorter than the minimum.
- Never checking `cache_read_input_tokens`.
- Forgetting that the cache lives only a few minutes without traffic.
- Switching models in the middle of a session and wondering why the cache is cold.

:::revoshop
RevoShop's "ask about this order" assistant has a 3,000-token system prompt with rules, plus the order JSON and the question. Write the prompt order (from stable to changing), say where the breakpoint goes, and name one thing in the current design that would silently break caching.
:::

## 🏆 Best practices

- [ ] Put stable content first, changing content last; place the breakpoint at the boundary.
- [ ] Keep the prefix byte-for-byte identical across requests (sorted tools, no timestamps).
- [ ] Never change earlier messages; append instead.
- [ ] Log `cache_creation_input_tokens`, `cache_read_input_tokens` and `input_tokens` for every call.
- [ ] Track the hit rate and alert when it drops.
- [ ] Check the minimum length and TTL for your model; pick 5 minutes or 1 hour by traffic pattern.
- [ ] Count caching in your cost estimate (see lesson 2 of week 1).

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain caching with the handout picture. Why does a date stamp on the first line ruin it?

## 📐 Design it

SupportDesk AI has: tool definitions (2,000 tokens), a system prompt (3,000), a help-center summary that changes once a day (8,000), the conversation so far, and the new customer message. Traffic is 10,000 conversations a day, busy from 9 to 17 and quiet at night. The first version put "Current time: ..." and the customer's name at the top of the system prompt, and the cache hit rate is 0%. Redesign the prompt order, the breakpoints, the TTL choice, and how you measure success.

:::quiz
Show a possible design

- **Order (stable → changing):** tool definitions → fixed system prompt (rules, examples) → help-center summary (changes daily) → conversation so far → new customer message. The time and the customer's name move to the **end**, in the latest message or a small final block.
- **Breakpoints:** one after the system prompt block (covers tools + system, same for all customers), one after the help-center summary (shared by everyone for a day), and one on the last block of the latest turn so the growing conversation is reused. That is three markers, within the usual limit.
- **TTL:** during the day, busy traffic refreshes the 5-minute entry constantly, so use the default life. Overnight gaps are long, so accept a cold start in the morning, or send one warm-up request before opening time. Use the 1-hour life only for prefixes with gaps of 5–60 minutes.
- **Daily change:** when the help-center summary changes at night, the summary and later blocks are a miss once; the earlier blocks still hit, because the order puts the daily-changing part after the fixed part.
- **Minimum length:** the first block set is 5,000+ tokens, above every model's minimum.
- **Measure:** log `cache_read_input_tokens`, `cache_creation_input_tokens` and `input_tokens` per request; hit rate = reads ÷ (reads + writes + uncached); target above 80% in the daytime; alert if it falls below 50%.
- **Cost check:** compute the bill before and after with the cost formula; confirm the saving with the provider's usage report.
- **Test:** an automated test builds two requests for two different customers and asserts the first N blocks are identical.

**Rule shown:** caching is a prompt-ordering problem; fix the order, then verify with the usage numbers.
:::

### 📝 Self-review checklist

- [ ] Stable parts come first; dynamic parts last
- [ ] Breakpoints sit at stability boundaries
- [ ] TTL fits the traffic pattern
- [ ] There is a measurement and an alert

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m7/w2/04-cache-planner" ai="no-ai" title="Simulate prompt caching"}
Write `block_tokens`, `simulate_cache` (exact-prefix hits, a TTL that a read refreshes, a minimum length, no breakpoint = no caching), `first_difference` (where a silent invalidator hides), `prompt_cost` (read ×0.1, write ×1.25) and `cache_savings`. The tests show a timestamp ruining the cache, a breakpoint in the wrong place, and a single request losing money. No API key needed.
:::

:::hints
- Key the store by `tuple(blocks[: bp + 1])` and remember the last time it was used.
- A hit needs `t - last <= ttl_s`; on a hit set `store[key] = t` (a read refreshes).
- Not a hit and `prefix_tokens >= min_tokens` → write; otherwise count the prefix as uncached.
- `uncached` also includes the blocks after the breakpoint.
- `first_difference`: loop to the longer length; a missing block counts as different; `None` when equal.
- `cache_savings`: all tokens at full price, minus the sum of `prompt_cost` over the simulation.
:::

## ✅ Quick check

:::quiz
Why does a timestamp at the top of the system prompt give a 0% hit rate?

The cache matches the prompt from the very first character. A timestamp changes the first block every request, so the stored prefix never equals the new one, and everything after it is a miss too. Move the timestamp to the end or remove it.
:::

:::quiz
Where should the breakpoint go when many requests share a document and ask different questions?

On the document (the last stable block), not on the question. The cached prefix then includes only text that repeats. If it were after the question, each request would store a new, never-reused entry.
:::

:::quiz
`cache_read_input_tokens` is 0 on every call. What do you check?

First, whether something in the prefix changes each time (timestamp, id, user name, unsorted tools, edited earlier messages). Second, whether the prefix is shorter than the model's minimum cacheable length. Third, whether the requests are further apart than the cache lifetime, or the model or settings changed.
:::

## 📚 Keep learning

- [Anthropic docs: Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [Anthropic docs: Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- [Anthropic docs: Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting)

---
title: "Choosing a Model: Cost, Latency & Quality"
summary: "Pick a model with evidence, not hype — compare quality, cost, speed, context size and data rules on your own test cases, use the cheapest model that is good enough, and keep your code ready to switch."
type: lesson
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: core, ops: optional }
durationMinutes: 150
tags: [llm, model-selection, cost, latency, evals, routing]
lastReviewed: 2026-10
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- The **five things** to compare when choosing a model
- Why you test on **your own examples**, not on leaderboards
- The **cheapest model that is good enough** rule
- Three ways to save money: **cascade**, **caching**, **batching**
- How to keep your app **ready to switch** models

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Model tier** | Small and fast, balanced, or large and strong | Tingkat model |
| **Latency** | How long the user waits for an answer | Waktu tunggu |
| **Time to first token** | Wait before the first word appears | Waktu sampai token pertama |
| **Throughput** | How many requests you can run per minute | Laju pemrosesan |
| **Open-weight model** | A model whose files you can download and run yourself | Model berbobot terbuka |
| **Cascade** | Try a cheap model first, escalate only if needed | Berjenjang |
| **Prompt caching** | Pay less for a prompt prefix you send again | Cache prompt |
| **Deprecation** | The provider retires a model version | Model dipensiunkan |

## 🧠 The big idea

Choosing a model is like **choosing transport for a delivery business**. A motorbike (small model) is cheap, quick and fine for envelopes. A truck (large model) carries more and handles the hard cargo, but each trip costs more and takes longer to start. You do not send a truck to deliver a letter, and you do not send a motorbike to move a fridge.

So the rule is simple: use **the cheapest, fastest model that does this job well enough**, and prove "well enough" with numbers.

## ❓ Why it matters

The model is usually the biggest line in the bill of an AI feature, and it decides the speed the user feels. Teams make two expensive mistakes:

- using the largest model for everything, then watching the bill and the wait time explode,
- picking a model because a blog said it is "the best", then finding out it fails on **their** data.

Models also change fast. New versions arrive, old ones are retired, and prices move. A team that tests with data and keeps a clean interface can switch in a day. A team that guessed and hard-coded a name can be stuck for weeks.

## 📖 Step by step

### 1. Five things to compare

| Thing | Question | How to check |
|---|---|---|
| **Quality** | Does it do *my* task correctly? | your own test set (below) |
| **Cost** | What is the price per call at my sizes? | tokens × price; `usage` in responses |
| **Latency** | Is it fast enough for this screen? | measure time to first token and total time |
| **Context & limits** | Does my input fit? How many requests per minute? | window size, rate limits |
| **Features & rules** | Tools, images, JSON mode, region, data retention, licence | provider docs, your legal/security rules |

Do not stop at "quality". A great answer after 25 seconds is a failed feature for a chat widget. A cheap model that leaks customer data into the wrong region is a failed feature for a bank.

### 2. Tiers, in plain words

Every big provider sells a few tiers. Names change, the idea does not:

| Tier | Good for | Trade-off |
|---|---|---|
| **Small / fast** | classification, routing, extraction, short answers, high volume | weaker at hard reasoning and long tasks |
| **Balanced** | most product features, coding help, support answers | the sensible default |
| **Large / flagship** | hard reasoning, long multi-step work, tricky documents | slowest and most expensive |

Many providers also let you set **how hard the model thinks** (a reasoning or *effort* setting). A strong model at low effort can match an older model at high effort for less money, so measure that option before you add a second model.

Prices and names change often, so always read the provider's pricing and models pages when you decide.

### 3. Test on your own examples

Leaderboards test *general* skill. Your product needs *your* skill: your language, your documents, your tone.

1. Collect **20–50 real examples** of the input (customer questions, invoices, job descriptions). Include easy ones, hard ones and nasty edge cases.
2. Write what a **good answer** looks like for each (a label, a short answer, or a checklist).
3. Run the **same prompt** on 2–3 models.
4. Record **quality** (how many were right), **cost**, **time to first token** and **total time**.
5. Choose the cheapest model that passes your quality bar.

This is a small *eval*. You will build a proper one in week 5. Even a spreadsheet of 30 rows beats opinion.

### 4. Choose with numbers

```python
def call_cost(model, input_tokens, output_tokens):
    return input_tokens * model["input_price"] / 1_000_000 + output_tokens * model["output_price"] / 1_000_000


def choose_model(models, *, min_quality, max_latency_s, input_tokens, output_tokens):
    ok = [
        m for m in models
        if m["quality"] >= min_quality
        and m["latency_s"] <= max_latency_s
        and m["context"] >= input_tokens + output_tokens
    ]
    if not ok:
        return None
    best = min(ok, key=lambda m: (call_cost(m, input_tokens, output_tokens), m["latency_s"], m["name"]))
    return best["name"]
```

Read it as a recipe: **filter** by the hard limits (quality, speed, size), then take the **cheapest** of what is left. If nothing is left, the honest answer is "none of these models fits; change the requirement or the design".

### 5. Money saver 1: a cascade

Most requests are easy. Send them to the cheap model, and **escalate only when the answer looks wrong**.

```python
def run_cascade(models_cheapest_first, ask, is_good):
    total = 0.0
    for name in models_cheapest_first:
        answer, cost = ask(name)
        total += cost                      # failed attempts still cost money
        if is_good(answer):
            return name, answer, total
    return None
```

It only works if `is_good` is **reliable**: a schema check, a rule, a confidence field, or a second cheap check. If your quality check is weak, a cascade quietly lets bad answers through. Also count the failed attempts in the cost, and remember that two calls take longer than one.

### 6. Money saver 2: prompt caching

Many apps send the same long prefix on every call (system prompt, rules, a policy document). Providers can store that prefix and charge a **fraction** for the cached part on later calls (often around a tenth of the normal input price).

```python
def monthly_cost(model, requests_per_day, input_tokens, output_tokens, cache_hit_rate=0.0, days=30):
    price_in = model["input_price"] * ((1 - cache_hit_rate) + cache_hit_rate * 0.1)
    per_call = input_tokens * price_in / 1_000_000 + output_tokens * model["output_price"] / 1_000_000
    return per_call * requests_per_day * days
```

To make caching work: put the **stable** content first (instructions, documents) and the **changing** content last (the user's question), and keep the stable part byte-for-byte identical. A timestamp at the top of the prompt destroys the cache.

### 7. Money saver 3: batch the slow jobs

If nobody is waiting (nightly summaries, labelling a dataset, running evals), use the provider's **batch API**. It usually runs asynchronously within a day and costs about half. Use normal calls only for the screens where a human waits.

### 8. Open-weight and local models

Open-weight models can run on your own server or laptop (week 1, lesson 5):

| | API model | Local / self-hosted |
|---|---|---|
| Quality at the top end | usually higher | usually lower |
| Cost shape | pay per token | pay for hardware, then "free" per call |
| Privacy | data goes to the provider (read their terms) | data stays with you |
| Operations | none | you run it, update it, monitor it |
| Good for | most products | private data, offline use, learning, cheap bulk work |

Neither is "better". Choose by data rules, volume and the team you have.

### 9. Stay ready to switch

Models get replaced. Protect yourself:

- put the model name and prices in **configuration**, not in code,
- wrap calls in **one small interface** (`complete(messages) -> text`) so providers can be swapped or mixed,
- **pin** an exact model version when you need stable behaviour, and read the deprecation notices,
- keep your **test set**. When a new model appears, run it through the same set before switching,
- log which model answered each request.

### Choosing your setup

| Situation | Do this |
|---|---|
| Easy, high volume (tagging, routing) | small model |
| Typical product feature | balanced model, test one tier down |
| Hard reasoning, long documents | large model, maybe with more thinking effort |
| Same long prefix in every call | prompt caching |
| Nobody waits for the answer | batch API |
| Private data or no internet | local model, or a provider with the right data terms |
| Not sure | build the 30-row test, measure three models |

- ✅ Decide with a test set, then re-test when models change.
- 🚫 "The biggest model, to be safe."
- 🚫 A hard-coded model name in twelve files.

## ⚠️ Common mistakes

- Choosing by benchmark scores or by a friend's opinion.
- Comparing models with different prompts (it is not a fair test).
- Looking only at price per token, not **cost per completed task** (a cheap model that needs three tries is not cheap).
- Ignoring latency until users complain.
- A cascade with a weak "is it good?" check.
- A cached prefix that changes slightly each call.
- No plan for deprecation.

:::revoshop
RevoShop could use AI in three places: (1) tagging product reviews as positive or negative, (2) answering "where is my order?" with order data, (3) writing a polite refund-denial email. For each, say which tier you would test first, what the quality bar is, and how many seconds a customer will accept.
:::

## 🏆 Best practices

- [ ] Write the requirement first: quality bar, maximum wait, volume, data rules.
- [ ] Test 2–3 models on 20–50 of your own examples before deciding.
- [ ] Compare **cost per completed task**, not only price per token.
- [ ] Start with the cheapest tier that could work, and move up only with evidence.
- [ ] Use caching for stable prefixes and batching for work nobody waits for.
- [ ] Keep model names and prices in config, behind one interface.
- [ ] Re-run your test set when a new model appears or an old one is retired.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain to a product manager why "use the best model" is not a plan, using the motorbike-and-truck picture. Which two numbers would you ask them for?

## 📐 Design it

SupportDesk AI gets 20,000 customer messages a day. About 70% are simple ("where is my order?", "how do I reset my password?"); 30% are complicated (refund disputes, several problems in one message). Answers must start appearing in under 2 seconds. Design the model setup: which models, how requests are routed, how you check quality, and how you control cost.

:::quiz
Show a possible design

- **Step 1, route (small, fast model):** classify each message as simple or complicated, and detect topic/language. This is a cheap, short call.
- **Step 2, answer:** simple messages go to a **balanced** model with retrieved help articles; complicated ones go to a **larger** model, or the same model with more reasoning effort, or to a human.
- **Cascade check:** the answer must pass cheap checks (cites a help article, matches a schema, no policy keywords). If not, escalate one tier.
- **Latency:** stream tokens so the first words appear in about a second; keep the router prompt short; cache the shared system prompt.
- **Quality:** a test set of 200 real, labelled messages (simple and hard); measure resolution accuracy per tier before launch and weekly after. Track human-handoff rate and thumbs-down.
- **Cost:** estimate per tier (tokens × price × volume), expect the 70% simple traffic to dominate volume, and put a daily budget alert. Use the batch API for nightly evals.
- **Switching:** model names and prices in config, one `complete()` interface, a log of the model used per answer.
- **Privacy:** check the provider's data terms for customer data; mask personal data in prompts when possible.

**Rule shown:** route by difficulty, check the cheap answer, escalate only when needed, and measure everything.
:::

### 📝 Self-review checklist

- [ ] I named quality, cost, latency, size and data rules
- [ ] The choice is backed by a test on real examples
- [ ] There is a reliable check before escalating
- [ ] Model names and prices live in config

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m7/w1/02-model-choice" ai="no-ai" title="Choose a model with numbers"}
Write `call_cost`, `choose_model` (cheapest model that meets quality, speed and context limits; ties go to the faster one), `monthly_cost` (with a cache hit rate where cached input costs 10%) and `run_cascade` (cheap first; the cost includes failed attempts). No API key needed.
:::

:::hints
- `choose_model`: filter first, then `min(..., key=(cost, latency, name))`.
- Context check: `model["context"] >= input_tokens + output_tokens`.
- `monthly_cost`: the effective input price is `price * ((1 - h) + h * 0.1)`; output is never cached.
- `run_cascade`: add `cost` to the total **before** you test `is_good`.
:::

## ✅ Quick check

:::quiz
Why is "cost per completed task" better than "price per token"?

A cheap model that needs several tries, produces wrong answers that need human fixing, or writes long answers can cost more per finished job than a pricier model that gets it right once. Compare the total cost to get a correct result.
:::

:::quiz
When does a model cascade save money, and when does it backfire?

It saves money when most requests are easy and you have a reliable way to tell a good answer from a bad one. It backfires when the quality check is weak (bad answers slip through), when most requests escalate anyway (you pay for two calls), or when the extra delay is not acceptable.
:::

:::quiz
Why keep model names and prices out of your code?

Models are retired, replaced and re-priced often. If they live in configuration behind one interface, you can test a new model and switch (or roll back) by changing a setting instead of editing many files.
:::

## 📚 Keep learning

- [Anthropic docs: Choosing a model](https://platform.claude.com/docs/en/about-claude/models/choosing-a-model)
- [Anthropic docs: Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [Anthropic docs: Batch processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing)

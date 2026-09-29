---
title: "LLM Gateway"
summary: One service in front of every AI model call — centralizing API keys, model routing, caching, cost tracking, rate limits, and provider fallback, so your app stays simple and you control spend, reliability, and safety in one place.
type: lesson
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: core, ops: recommended }
durationMinutes: 130
tags: [architecture, system-design, llm-gateway, caching, fallback, cost]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What an **LLM gateway** is and why teams put one in front of AI calls
- Centralizing **API keys**, **model routing**, and **cost tracking**
- Reusing your resilience toolkit: **caching**, **rate limits**, **retries**, **fallback**
- **Provider fallback**: switch models when one fails or is down
- **Guardrails** and **observability** in one place
- How this ties together the whole track for CareerPilot's AI features

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **LLM gateway** | One service all AI calls go through | Satu pintu untuk panggilan AI |
| **Provider** | A company/model you call (OpenAI, Anthropic, …) | Penyedia model |
| **Routing** | Choosing which model handles a request | Memilih model |
| **Fallback** | Switch to another provider on failure | Beralih penyedia saat gagal |
| **Cost tracking** | Recording spend per request/user | Mencatat biaya |
| **Guardrail** | A safety check on inputs/outputs | Pemeriksa keamanan |
| **Observability** | Logs/metrics to see what's happening | Kemampuan memantau |

## 🧠 The big idea

An LLM gateway is the **front desk of a hotel**. Guests (your app's features) don't wander into the kitchen, laundry, or accounting themselves — they talk to **one desk**, which routes each request to the right department, keeps the master keys, logs everything, enforces the rules, and can send you to a backup service if one is busy. One desk, one place to manage everything.

## ❓ Why it matters

Once more than one feature calls an LLM, sprinkling API keys, retries, caching, and cost logic across the codebase becomes a mess — and a risk (leaked keys, runaway bills, no visibility). A gateway puts all of it in **one place**: your features just call the gateway with a prompt. This is where *everything* from this track comes together — caching, rate limiting, retries, circuit breakers, cost control — applied to the expensive, flaky, fast-changing world of AI providers.

## 📖 Step by step

### 1. What the gateway centralizes

Your app calls `gateway.complete(prompt, ...)`; the gateway handles:

- **Keys**: provider API keys live only in the gateway, never scattered in feature code.
- **Routing**: pick the model per task (a cheap model for classification, a strong one for writing).
- **Caching**: return a stored answer for a repeated prompt (Stage F).
- **Rate limiting**: cap per-user/per-app calls to protect the budget (Stage F).
- **Retries + circuit breaker**: handle provider blips and outages (Stage H).
- **Fallback**: if provider A fails, try provider B.
- **Cost tracking**: record tokens and spend per request/user.
- **Guardrails**: check inputs (block abuse) and outputs (filter unsafe content).
- **Observability**: log prompts, latency, cost, and errors.

### 2. Routing: the right model for the job

Not every task needs the biggest model. Route by task or config:

```
task "classify"  → small, cheap, fast model
task "write_cv"  → larger, higher-quality model
```

This alone can cut costs dramatically without hurting quality where it matters.

### 3. Caching and cost — the money levers

LLM calls cost real money per token. Two habits from Stage F pay off hugely:
- **Cache** identical prompts → skip the paid call entirely.
- **Track cost** per request and per user so you can see spend, set budgets, and rate-limit heavy users.

```
cost = (tokens / 1000) * price_per_1k_tokens   # record this every call
```

### 4. Provider fallback (and circuit breakers)

AI providers have outages. A gateway can **fall back**: try provider A; if it errors (or its circuit breaker is open), try provider B; if all fail, return a graceful message. Combined with retries + backoff (Stage H), this keeps AI features working through provider hiccups.

```
try provider A → fail → try provider B → success ✅
all providers fail → friendly fallback ("AI is busy, try again")
```

### 5. Guardrails and observability

Because every call flows through one place, the gateway is the natural home for **guardrails** (reject prompt-injection or disallowed content; filter unsafe output) and **observability** (one dashboard of latency, cost, error rates, and cache hit-rate). Without a gateway, you'd bolt these onto every feature separately.

### What to route through the gateway

| Concern | Handled in the gateway? |
|---|---|
| API keys / secrets | ✅ only here |
| Model choice per task | ✅ routing |
| Repeated-prompt cost | ✅ cache |
| Per-user spend limits | ✅ rate limit + cost tracking |
| Provider outage | ✅ retries + circuit breaker + fallback |
| Safety checks | ✅ guardrails |

- ✅ Send every AI call through the gateway; keep keys and policy in one place.
- ✅ Route cheap tasks to cheap models; cache repeats; track cost per user.
- ✅ Add fallback + circuit breakers so one provider's outage isn't yours.
- 🚫 Don't scatter keys, retries, and cost logic across features.

## ⚠️ Common mistakes

- API keys copied into many services — a leak or rotation nightmare.
- No caching, so identical prompts are paid for again and again.
- No per-user rate limit or cost tracking, so one user (or a loop) drains the budget.
- Single provider with no fallback, so its outage takes your AI features down.
- Guardrails/logging added per feature instead of once in the gateway.

:::revoshop
RevoShop is mostly non-AI, but if it added AI (e.g. review summaries, a support bot), a gateway would help. (1) Which AI tasks are cheap (classify a review's sentiment) vs expensive (write a summary), and how would routing save money? (2) How would caching and per-user rate limits protect the AI budget? (3) Where would fallback + a circuit breaker keep the feature usable during a provider outage?
:::

## 🏆 Best practices

- [ ] Route all AI calls through one gateway; keep provider keys only there.
- [ ] Route each task to the cheapest model that meets its quality bar.
- [ ] Cache repeated prompts and track token cost per request and per user.
- [ ] Apply per-user rate limits and budgets at the gateway.
- [ ] Add retries, circuit breakers, and provider fallback for resilience.
- [ ] Centralize guardrails and observability (cost, latency, errors, cache hit-rate).

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain an LLM gateway with the hotel-front-desk analogy. Then name three things it centralizes and, for each, one problem you'd have without it.

## 📐 Design it

Design the LLM gateway for CareerPilot, which has three AI features: (a) classify a job posting's seniority (cheap, high volume), (b) tailor a CV (expensive, medium volume), (c) a chat assistant (streaming). Cover routing, caching, per-user cost control, and what happens when the primary provider has an outage.

:::quiz
Show a possible design

**Routing:** (a) seniority classification → a **small cheap model** (high volume, simple task); (b) CV tailoring → a **larger, higher-quality model**; (c) chat → a mid/large model with **streaming**. The gateway maps task → model, so features never hardcode a provider.

**Caching:** classification prompts repeat a lot (same postings) → cache aggressively (big savings). CV tailoring is user-specific → cache little or key on (profile+job) hash. Chat is dynamic → generally not cached.

**Per-user cost control:** the gateway tracks tokens × price per request and per user, enforces per-user rate limits and a monthly budget, and returns `429`/upgrade prompts when exceeded — protecting the overall spend.

**Provider outage:** retries with backoff for blips; a **circuit breaker** per provider; **fallback** to a secondary provider/model when the primary is down; if all fail, a graceful "AI busy, draft saved" message. All of this lives in the gateway, so every feature benefits at once.

**Rule shown:** one gateway centralizes routing, caching, cost control, and resilience — applying the whole track's tools to AI calls in a single place.
:::

### 📝 Self-review checklist

- [ ] Tasks routed to appropriately-sized models
- [ ] Caching strategy matched to how repetitive each task is
- [ ] Per-user cost tracking, rate limits, and budgets at the gateway
- [ ] Retries + circuit breaker + provider fallback for outages

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/architecture/i-system-design-practice/05-llm-gateway" ai="no-ai" title="A mini LLM gateway: cache, fallback, and cost"}
Implement a small LLM gateway: estimate cost from tokens, cache identical prompts, and fall back through a list of providers until one succeeds — tracking total spend. The tests prove a cached prompt skips the providers (and its cost), and that a failing primary provider falls back to the next.
:::

:::hints
- `estimate_cost(tokens, price_per_1k)` = `tokens / 1000 * price_per_1k`.
- Providers are `(name, fn)` pairs tried in order; `fn(prompt)` returns `{"text", "tokens"}` or raises to simulate failure.
- `complete(prompt)`: on a cache hit return `{"text", "provider", "cached": True, "cost": 0.0}` and don't call providers; on a miss, try providers in order, add `estimate_cost` to `total_cost`, cache and return `{"text", "provider", "cached": False, "cost"}`. Raise if every provider fails.
:::

## ✅ Quick check

:::quiz
Why put a single gateway in front of all your LLM calls instead of calling providers directly from each feature?

Because it centralizes keys, model routing, caching, rate limits, cost tracking, retries/fallback, guardrails, and observability in one place. Calling providers directly scatters secrets and policy across features, making cost control, reliability, and safety inconsistent and hard to manage.
:::

:::quiz
Name two things the gateway does to control AI cost.

Caching identical prompts (so a repeated request skips the paid call) and routing each task to the cheapest model that meets its quality bar; it also tracks token cost per user and enforces rate limits/budgets to stop runaway spend.
:::

## 📚 Keep learning

- [Cloudflare AI Gateway](https://developers.cloudflare.com/ai-gateway/)
- [Anthropic: Claude API overview](https://docs.claude.com/en/api/overview)
- [LiteLLM: an open-source LLM gateway/proxy](https://docs.litellm.ai/)

---
title: "Week 1 Placement Check"
summary: Can you explain tokens and the context window, choose a model with evidence, call a chat API with streaming, get structured JSON you can trust, and run a local model? If yes, skim the week.
type: placement-check
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: core, ops: optional }
durationMinutes: 20
tags: [placement, llm, tokens, streaming, structured-output, ollama]
lastReviewed: 2026-10
---

::::placement{id="modules/m7/w1"}
This week covers how LLMs work and how to call them. Can you explain these without looking?

:::quiz
1 · What is a token, and why do tokens (not words) decide your cost and your limits?

A token is a small piece of text: a word, part of a word, or a symbol. Providers bill per token for both input and output, and the context window is measured in tokens. Input and output share the same window, so a long prompt leaves less room for the answer, and the output is usually priced higher than the input.
:::

:::quiz
2 · An answer ends in the middle of a sentence. What do you check, and what are two fixes?

Check `stop_reason`: `"max_tokens"` means the answer hit the output limit. Fixes: raise `max_tokens`, ask for a shorter answer, trim the prompt so there is room, or show a "continue" option.
:::

:::quiz
3 · How do you choose between a small and a large model for a new feature?

Write the requirement (quality bar, maximum wait, volume, data rules). Test 2–3 models on 20–50 of your own examples with the same prompt, and measure quality, cost per completed task and latency. Pick the cheapest model that meets the bar, and keep the model name in configuration so you can switch.
:::

:::quiz
4 · Why does a chat API need you to send the whole conversation every time, and what does that cost you?

The API is stateless: the server remembers nothing between calls. You hold the history and send it all each turn, so cost and latency grow with the conversation. You trim old turns, summarize, or retrieve only what is relevant.
:::

:::quiz
5 · The model returns valid JSON that matches your schema, but the order id in it does not exist. What went wrong, and what do you add?

A schema checks the shape, not the truth: the model invented a value. Add business validation in your code (look the id up in the database), allow `null` for missing facts, and treat extracted values as untrusted input.
:::

:::quiz
6 · When is a local model (for example with Ollama) a good choice, and what must a fallback never do?

Good for private data, offline use, learning and cheap bulk work. A fallback to a cloud API must not silently send data that was supposed to stay private, and it must not hide real bugs by catching every exception.
:::
::::

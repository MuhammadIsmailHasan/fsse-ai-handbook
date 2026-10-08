---
title: "Week 2 Placement Check"
summary: Can you structure and test a prompt, run the tool-calling loop safely, add guardrails that survive a fooled model, and use prompt caching correctly? If yes, skim the week.
type: placement-check
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: core, ops: optional }
durationMinutes: 20
tags: [placement, prompting, tool-calling, guardrails, prompt-caching]
lastReviewed: 2026-10
---

::::placement{id="modules/m7/w2"}
This week covers prompts, tools, safety and cost. Can you explain these without looking?

:::quiz
1 · Why use a strict template function and a prompt version instead of building prompt strings by hand?

A strict template fails loudly on a missing or unused variable, so typos are caught in tests instead of silently producing a broken prompt. A version number and a logged fingerprint let you reproduce a bad answer, compare changes and roll back, and review prompt edits like code.
:::

:::quiz
2 · In the tool-calling loop, who runs the tool, and where must "which user is this" come from?

Your program runs the tool; the model only asks for a call. The user identity must come from your authenticated session (the app context), never from the model's arguments, because model output can be influenced by attackers.
:::

:::quiz
3 · The model asks for two tools in one reply. What do you send back?

Run both and send ONE user message containing both `tool_result` blocks, each with the matching `tool_use_id`. Failed calls return an `is_error` result so the model can recover. Keep a maximum number of steps.
:::

:::quiz
4 · Why is "never reveal the system prompt" in the prompt not a guardrail?

A prompt instruction can be bypassed by well-written text. A guardrail is enforced in code: keep secrets out of the prompt, restrict tools with least privilege and approvals, and check outputs. Assume the model can be fooled and make that survivable.
:::

:::quiz
5 · Prompt caching shows 0 cache reads. Name three likely causes.

Something in the prefix changes each request (timestamp, id, user name, unsorted tools, edited earlier messages); the prefix is shorter than the model's minimum cacheable length; the requests are further apart than the cache lifetime; or the breakpoint was placed after the part that changes.
:::
::::

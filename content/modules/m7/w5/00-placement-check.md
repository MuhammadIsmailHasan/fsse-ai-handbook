---
title: "Week 5 Placement Check"
summary: Can you build an eval harness with gates, assemble a trustworthy test set, calibrate an LLM judge, use RAG metrics wisely, and trace an AI request? If yes, skim the week.
type: placement-check
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: core, ops: optional }
durationMinutes: 20
tags: [placement, evals, test-datasets, llm-judge, tracing]
lastReviewed: 2026-10
---

::::placement{id="modules/m7/w5"}
This week is about measuring AI quality. Can you explain these without looking?

:::quiz
1 · Two versions of a prompt both have a pass rate of 0.80. Why compare more than the average, and what is a release gate?

The same average can hide that the new version broke important cases while fixing others. Compare the fixed and broken cases against a baseline. A gate is a rule in CI that blocks a release when the pass rate is below a floor or when too many (or any critical) cases regress.
:::

:::quiz
2 · Name three properties of a good test dataset, and one trap when splitting it.

Real cases (not only made-up ones), tags for coverage including unanswerable and adversarial cases, stable ids and checkable expectations. A trap: leakage between the dev and test sets (random reshuffling, near-duplicate questions), so use a stable hash split and check for near-duplicates.
:::

:::quiz
3 · An LLM judge agrees with humans 90% of the time. Why might it still be useless, and what do you measure instead?

If 90% of answers are good, a judge that says "pass" to everything gets 90% accuracy by luck. Cohen's kappa removes chance agreement, and the confusion matrix shows whether the judge passes bad answers. Also test position and length bias.
:::

:::quiz
4 · What do faithfulness and context recall each tell you in a RAG system?

Faithfulness tells you whether the answer's claims are supported by the retrieved context (generation vs context). Context recall tells you whether the retrieved context contains the facts needed (retrieval). Low recall points at retrieval; good recall with low faithfulness points at the prompt or model.
:::

:::quiz
5 · What is the difference between a trace and a span, and what should you record on a model-call span?

A trace is one whole request; spans are the steps inside it, nested. On a model call record the model and parameters, prompt version, input and output tokens, cost, latency (and time to first token), stop reason, and errors or retries. Mask personal data and secrets.
:::
::::

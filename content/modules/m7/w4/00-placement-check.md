---
title: "Week 4 Placement Check"
summary: Can you design a RAG pipeline with an honest refusal path, chunk by structure, clean and re-rank candidates, validate citations, and diagnose a failed answer? If yes, skim the week.
type: placement-check
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: core, ops: optional }
durationMinutes: 20
tags: [placement, rag, chunking, reranking, citations]
lastReviewed: 2026-10
---

::::placement{id="modules/m7/w4"}
This week goes deep into RAG. Can you explain these without looking?

:::quiz
1 · When should a RAG system skip the model call entirely?

When retrieval returns nothing usable: no chunks, all below the score floor, or none fitting the token budget. Calling the model with no sources invites a made-up answer; return an honest "not found" with a next step.
:::

:::quiz
2 · Why chunk by headings and paragraphs instead of every N characters, and what does a heading path add?

Structure-based chunks keep one idea together and do not cut sentences, tables or steps. The heading path ("Returns > Refunds") gives each chunk the context that a bare sentence lacks, which improves both matching and understanding.
:::

:::quiz
3 · Retrieval returns 5 near-identical chunks. Which tools help, and what is the two-stage idea?

Drop near-duplicates, use MMR to add variety, and re-rank with a smarter scorer. The two-stage idea: fetch many candidates quickly (high recall), then narrow to the best few (high precision) within the token budget.
:::

:::quiz
4 · What can your code verify about citations, and what can it not?

It can check that cited numbers exist, that sentences have citations, and that quoted text appears in a source. It cannot fully verify that the source really supports the claim, is complete or current; that needs a judge (human sample or model).
:::

:::quiz
5 · A RAG answer is wrong. What are the questions to ask, in order?

Is the answer in the corpus? Was the right chunk retrieved? Did it reach the prompt (after k, budget and ranking)? Was the answer correct and grounded? The first "no" is the root cause to fix.
:::
::::

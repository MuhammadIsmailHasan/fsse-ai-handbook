---
title: "Week 3 Placement Check"
summary: Can you explain embeddings and similarity, store and search vectors in PostgreSQL, build and measure a semantic search, and combine keyword and vector search? If yes, skim the week.
type: placement-check
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: core, ops: optional }
durationMinutes: 20
tags: [placement, embeddings, pgvector, semantic-search, hybrid-search]
lastReviewed: 2026-10
---

::::placement{id="modules/m7/w3"}
This week covers meaning-based search. Can you explain these without looking?

:::quiz
1 · What is an embedding, and why must documents and queries use the same embedding model?

An embedding is a list of numbers that represents the meaning of a text, so similar meanings get nearby vectors. Different models create different "maps", so vectors from two models cannot be compared. Use one model per index and store its name so you can re-embed when you change it.
:::

:::quiz
2 · What is the difference between cosine similarity, dot product and Euclidean distance?

Cosine measures only the angle between vectors (ignores length); dot product combines angle and length (same as cosine for normalised vectors); Euclidean is the straight-line distance (smaller is closer). Text search usually uses cosine or normalised dot product.
:::

:::quiz
3 · In pgvector, when do you add an HNSW or IVFFlat index, and what do you give up?

Start with exact search, which is always correct and fine for tens of thousands of rows. Add an approximate index when measured latency requires it. You trade some recall (it may miss a true neighbour) for speed, plus build time and memory. Measure recall against exact results and tune `ef_search` or `probes`.
:::

:::quiz
4 · What numbers would you use to judge a semantic search, and how do you build the test?

Recall@k (is the right result in the top k), precision@k (how much of the top k is useful) and MRR (how high the first right result is). Build a test set of 20–100 real queries with the ids of the right results, run the search, and read the queries that missed.
:::

:::quiz
5 · Why combine keyword search with vector search, and how does reciprocal rank fusion work?

Vector search finds meaning but can miss exact ids, names and rare words; keyword search finds exact words but misses synonyms. Fusing both covers both weaknesses. RRF gives each document 1/(60 + rank) from every list and adds them, so documents that several lists rank highly rise, and no score scaling is needed.
:::
::::

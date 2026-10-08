---
title: "Retrieval & Reranking"
summary: "Turn a rough first search into a clean context — rewrite the query, fetch wide then narrow, remove duplicates, add variety with MMR, re-rank with a smarter scorer, and order chunks so the model actually uses them."
type: lesson
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: core, ops: optional }
durationMinutes: 180
tags: [rag, retrieval, reranking, mmr, query-rewriting, context]
lastReviewed: 2026-10
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- The **two-stage** idea: fetch wide (recall), then narrow (precision)
- **Query rewriting** and multi-query search
- **Diversity** with MMR and removing **near-duplicates**
- **Re-ranking** with a smarter, slower scorer
- Why **order** matters in the prompt ("lost in the middle")
- How to **evaluate and tune** each stage

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **First-stage retrieval** | The fast search that finds many candidates | Pencarian tahap pertama |
| **Re-ranker** | A slower model that reads query + candidate and scores the match | Pengurut ulang |
| **Cross-encoder** | A re-ranker that reads the query and the text together | Penyandi silang |
| **Query rewriting** | Turning the user's words into a better search query | Menulis ulang kueri |
| **MMR** | Maximal Marginal Relevance: relevant but not repetitive | Relevan tanpa berulang |
| **Near-duplicate** | Two chunks that say almost the same thing | Hampir kembar |
| **Context window budget** | How many tokens of sources you allow in the prompt | Anggaran konteks |
| **Lost in the middle** | Models use the start and end of a long prompt better than the middle | Hilang di tengah |

## 🧠 The big idea

Hiring is a good picture. First you **screen CVs fast**: a quick filter that keeps 50 people from 5,000. It is cheap, and it is allowed to be a bit rough, as long as the good people are *in* the 50. Then you **interview** a few: slow, careful, expensive, and you only do it for the shortlist. Finally you put the best candidates **on the panel** in a sensible order.

Retrieval works the same way: a fast search finds 50 candidates (cast the net wide, so recall is high), a careful re-ranker orders them (precision), you clean the shortlist (no duplicates, some variety), and only the best 3 to 6 go into the prompt.

## ❓ Why it matters

The model can only use what you put in front of it. The prompt usually has room for a handful of chunks, so **which handful** decides the answer. A good first search that returns 5 near-identical chunks gives the model one fact five times. A bad order can bury the key sentence in the middle. A large context full of noise costs money and makes the model worse, not better.

This stage often gives the **biggest quality gain per hour of work** after chunking.

## 📖 Step by step

### 1. Two stages: wide, then narrow

```text
question ─► first search: top 50 (fast, high recall)
        ─► clean: drop duplicates, apply MMR for variety   (cheap, in code)
        ─► re-rank: score top 20–50 with a smarter model   (slower)
        ─► keep the best 3–6 within the token budget
        ─► order them well and build the prompt
```

Measure each stage with the test set from week 3:

| Stage | Metric to watch |
|---|---|
| First search | **recall@50**: is the right chunk in the pool at all? |
| After re-ranking | **precision@5 / MRR**: is it at the top? |
| End to end | answer correctness |

If recall@50 is low, no re-ranker can help: fix chunking, embeddings or hybrid search. If recall@50 is high but precision@5 is low, a re-ranker is exactly the right tool.

### 2. Rewrite the query

Users write short, chatty or incomplete questions. In a chat, the message may depend on earlier turns: "and for the red one?".

Options:

- **Standalone rewrite:** a small model turns the chat history + last message into one complete search query ("return policy for the red running shoes").
- **Multi-query:** generate 2–4 variants (synonyms, different wording, the other language), search each, and **fuse** the results (reciprocal rank fusion, last week).
- **Keyword extraction:** keep codes, names and numbers as exact terms for keyword search.
- **HyDE (hypothetical answer):** ask the model to write a short *fake answer*, embed that, and search with it. It can find chunks that look like answers. It is clever but can drift, so test it.
- **Filters from the query:** "in Indonesian", "for sellers", "after 2025" can become metadata filters.

Rewriting costs a model call and some latency, so use a small, fast model and measure the gain. For a first version, a rewrite step only for multi-turn chats is often enough.

### 3. Remove near-duplicates

The same text often exists in several places (a FAQ and its copy in a manual, two versions of a policy). Duplicates waste the prompt. A simple, effective method compares word sets with **Jaccard similarity**:

```python
import re

def jaccard(a, b):
    wa, wb = set(re.findall(r"[a-z0-9]+", a.lower())), set(re.findall(r"[a-z0-9]+", b.lower()))
    if not wa and not wb:
        return 1.0
    return len(wa & wb) / len(wa | wb)

def drop_near_duplicates(chunks, threshold=0.8):
    kept = []
    for chunk in chunks:
        if all(jaccard(chunk["text"], k["text"]) < threshold for k in kept):
            kept.append(chunk)             # keep the first (the better-ranked) copy
    return kept
```

Do this on the ranked list so you keep the better-ranked copy. Also prefer **fresh** versions: if two near-duplicates differ in date, keep the newer, or filter old ones by metadata at search time.

### 4. Add variety with MMR

Five chunks about the same sentence are less useful than three chunks about three aspects. **Maximal Marginal Relevance** picks the next chunk by balancing relevance to the question against similarity to what you already picked:

```python
def mmr(query_vector, candidates, k, lambda_=0.7):
    remaining = list(candidates)
    chosen = []
    while remaining and len(chosen) < k:
        best, best_value = None, None
        for c in remaining:
            redundancy = max((cosine(c["vector"], s["vector"]) for s in chosen), default=0.0)
            value = lambda_ * cosine(query_vector, c["vector"]) - (1 - lambda_) * redundancy
            if best_value is None or value > best_value:
                best, best_value = c, value
        chosen.append(best)
        remaining.remove(best)
    return chosen
```

`lambda_ = 1` is pure relevance. Lower values push for variety. Start around 0.7 and tune on your test set. Use MMR when questions are broad ("tell me about our refund process"); avoid it for pinpoint questions ("what is the refund window?") where several close chunks may all be needed.

### 5. Re-rank with a smarter scorer

The first search compares the question and each chunk **separately** (two vectors). A **cross-encoder** reads the question and the chunk **together**, so it can notice details. It is slower, so you only run it on the top 20–50.

```python
def rerank(query, candidates, scorer, top_n):
    scored = [dict(c, rerank_score=scorer(query, c["text"])) for c in candidates]
    scored.sort(key=lambda c: -c["rerank_score"])          # sort is stable: ties keep their order
    return scored[:top_n]
```

Where does `scorer` come from?

| Option | Notes |
|---|---|
| A **hosted rerank API** from a model provider | simplest; one call with the query and the texts; pay per call |
| An **open cross-encoder** you run yourself | free per call, needs hardware and updates |
| A **language model as judge** ("score 0–10 how well this passage answers the question") | flexible, but slower and costlier; keep prompts short and results structured |

Rules: call the scorer **once per candidate**, rerank only a short list, and measure `precision@5` and latency before and after. Cache scores for popular queries.

### 6. Order the chunks for the model

Models tend to use the **beginning and the end** of a long prompt better than the middle. If you have 5 chunks ranked 1 to 5, put the best at both ends:

```python
def lost_in_the_middle_order(chunks):
    return chunks[0::2] + chunks[1::2][::-1]
# [1st, 2nd, 3rd, 4th, 5th]  ->  [1st, 3rd, 5th, 4th, 2nd]
```

Gains depend on the model and context length, and are small for short contexts, so treat this as a cheap experiment. Also:

- **Group chunks from the same document** and keep them in their original order (chunk 3 before chunk 4), because that reads naturally.
- Mark every chunk with its source number so the model can cite it (next lesson).

### 7. Fit the budget and compress

Count tokens. If the best chunks exceed the budget:

- keep fewer chunks (quality over quantity),
- use **parent-child** to send a short child instead of a long parent when the question is narrow,
- **compress**: ask a small model to extract only the sentences relevant to the question from each chunk (adds a call, saves tokens, can drop context, so test),
- cut obviously irrelevant parts (boilerplate headers).

More context is not better. A prompt with 20 mostly-irrelevant chunks makes it harder for the model to find the facts, costs more, and increases the chance it mixes sources.

### 8. Tune with the test set

Tune one knob at a time:

| Knob | Typical range | Watch |
|---|---|---|
| First-stage `k` | 20–100 | recall@k |
| Re-rank `top_n` | 3–8 | precision@5, answer quality, tokens |
| MMR `lambda_` | 0.5–1.0 | variety vs recall for pinpoint questions |
| Duplicate threshold | 0.7–0.9 | lost useful variants |
| Score floor | tuned from real examples | "no answer" rate |
| Query rewriting | on/off, per chat vs always | gain vs latency |

Keep a small table of experiments with the numbers. If a step does not improve the numbers, remove it: every stage adds latency and a place for bugs.

### Choosing your setup

| Situation | Do this |
|---|---|
| Right chunk is in the pool but not at the top | add a re-ranker |
| Right chunk is not in the pool | fix chunking / embeddings / hybrid search first |
| Top results are copies of each other | drop near-duplicates; try MMR |
| Chat follow-up questions | standalone query rewrite |
| Many ways to say the same thing | multi-query + fusion |
| Long prompts, key facts missed | fewer chunks, better order, compression |
| Latency too high | rerank fewer candidates, cache, smaller reranker |

- ✅ Fetch wide, then narrow.
- ✅ Measure recall@large-k and precision@small-k separately.
- 🚫 Sending 20 chunks "just in case".
- 🚫 Re-ranking when the right chunk was never retrieved.

## ⚠️ Common mistakes

- Setting `k` equal to the number of chunks you can fit, so there is no room to rerank.
- Using MMR on pinpoint questions that need several close chunks.
- Calling the re-ranker on hundreds of candidates (slow, expensive).
- Dedupe thresholds that remove legitimately different versions (policy 2024 vs 2025).
- Rewriting every query with a big model, adding seconds of latency.
- Changing three things at once and not knowing which helped.
- Ignoring the order of chunks and the token budget.
- Hiding failures: no log of the pool, the re-ranked list and the final chunks.

:::revoshop
A RevoShop customer asks "and the red one?" after talking about running shoes. Write the standalone search query a rewriting step should produce, two multi-query variants (one in English), and say which chunks you would expect in the first-stage pool versus the final three.
:::

## 🏆 Best practices

- [ ] Separate recall (first stage) from precision (re-rank), and measure both.
- [ ] Fetch 20–100 candidates; re-rank down to 3–8 within a token budget.
- [ ] Drop near-duplicates, and prefer fresh versions.
- [ ] Use query rewriting for chat follow-ups, and multi-query only when it helps on the test set.
- [ ] Apply MMR for broad questions, not for pinpoint ones.
- [ ] Re-rank only a short list, once per candidate, and watch latency.
- [ ] Order chunks deliberately and label them with source numbers.
- [ ] Log the candidate pool, the re-ranked list and the final prompt chunks.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain two-stage retrieval with the CV-screening and interview picture. Why can a re-ranker not fix a retrieval miss?

## 📐 Design it

SupportDesk AI's first version returns the top 5 chunks by vector similarity. Evaluation on 200 questions shows recall@5 = 0.68, recall@50 = 0.93, and many answers cite the same paragraph repeated from two articles. Latency budget for retrieval is 400 ms. Design the improved retrieval stage and say how you will know it worked.

:::quiz
Show a possible design

- **Diagnosis:** recall@50 is high (0.93), recall@5 is low (0.68): the right chunk is in the pool but not near the top, and duplicates waste slots. This is a ranking and cleaning problem, not a coverage problem.
- **Pipeline:** hybrid first stage with top 50 → near-duplicate removal (Jaccard ≥ 0.8, keep the newest) → re-rank the top 30 with a hosted rerank API or a cross-encoder → keep the best 5 within the token budget → order with best chunks at both ends → build the prompt.
- **Latency:** first stage ~50 ms (indexed), dedupe ~1 ms, re-rank of 30 short chunks 100–250 ms (batch them in one call), the rest in code: within 400 ms. Cache rerank results for frequent queries.
- **Query rewriting:** only for multi-turn chats, with a small fast model and a 1-second timeout; skip it for the first message of a conversation.
- **MMR:** try it on broad questions only; verify with the test set that pinpoint questions do not lose recall.
- **How to know it worked:** rerun the 200 questions and compare precision@5, MRR, recall@5 and end-to-end answer correctness before and after; check the 0.68 → target (say ≥ 0.85); also compare average tokens per prompt and p95 latency; read the remaining misses.
- **Guardrails:** keep a score floor and a "no answer" path; log pool ids, re-ranked ids and final ids for every request to diagnose regressions.

**Rule shown:** when recall at a large k is high, spend your effort on cleaning and re-ranking, and prove the gain with the same test set.
:::

### 📝 Self-review checklist

- [ ] Recall and precision are measured at different cut-offs
- [ ] The re-ranker only sees a short list
- [ ] Duplicates are removed
- [ ] Prompt order and token budget are controlled
- [ ] Each stage has a measured benefit

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m7/w4/03-retrieval-tools" ai="no-ai" title="Clean up the candidates"}
Write `cosine`, `mmr` (relevance minus redundancy), `jaccard`, `drop_near_duplicates`, `lost_in_the_middle_order` (best at both ends) and `rerank` (one scorer call per candidate, stable ties, input not changed). No API key needed.
:::

:::hints
- `mmr`: `redundancy = max(cosine(c, s) for s in chosen)` with `default=0.0` while nothing is chosen.
- Ties in `mmr` go to the earlier candidate: only replace the best when the new value is strictly greater.
- `jaccard`: sets of `[a-z0-9]+` words; two empty texts give `1.0`.
- `drop_near_duplicates`: keep a chunk only if its Jaccard with every kept chunk is `< threshold`.
- `lost_in_the_middle_order`: `chunks[0::2] + chunks[1::2][::-1]`.
- `rerank`: build copies with `dict(c, rerank_score=...)`, then `sort` (stable) by descending score and slice `[:top_n]`.
:::

## ✅ Quick check

:::quiz
Why fetch 50 candidates and then keep only 5?

The first search is fast but rough, so you cast a wide net to be sure the right chunk is among the candidates (high recall). A slower, more careful step then picks the best few (high precision). Keeping only a few chunks in the prompt also saves tokens and reduces noise.
:::

:::quiz
When can MMR hurt?

For pinpoint questions where the answer needs several very similar chunks (for example different conditions of the same rule). MMR pushes for variety and may skip a second close chunk that you needed. Use it for broad questions and test on both kinds.
:::

:::quiz
recall@50 is 0.45. Should you add a re-ranker?

No. The right chunk is missing from the pool for more than half the questions, and a re-ranker can only reorder what was retrieved. Fix chunking, the embedding model, hybrid search or filters first.
:::

## 📚 Keep learning

- [Sentence-Transformers: Cross-Encoders](https://www.sbert.net/examples/applications/cross-encoder/README.html)
- [Liu et al.: Lost in the Middle (paper)](https://arxiv.org/abs/2307.03172)
- [Carbonell & Goldstein: MMR (paper)](https://www.cs.cmu.edu/~jgc/publication/The_Use_MMR_Diversity_Based_LTMIR_1998.pdf)

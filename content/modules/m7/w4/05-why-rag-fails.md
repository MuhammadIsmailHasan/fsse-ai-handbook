---
title: "Why RAG Fails and How to Fix It"
summary: "Diagnose a bad RAG answer step by step — was it in the data, retrieved, kept in the prompt, used, and supported? — name the failure, pick the right fix, and turn failures into a prioritised plan and a growing test set."
type: lesson
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: core, ops: optional }
durationMinutes: 180
tags: [rag, debugging, evaluation, failure-modes, tracing]
lastReviewed: 2026-10
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- The **four questions** that locate a RAG failure
- A **taxonomy** of failures and the **fix** for each
- How to record a **trace** for every request
- How to **classify** failures in code and build a **fix plan**
- Failures that hide outside the pipeline: **stale data, conflicts, injection**
- How to turn every failure into a **test case**

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Trace** | A saved record of everything that happened for one request | Jejak |
| **Retrieval miss** | The right chunk was never found | Retrieval meleset |
| **Faithfulness** | The answer only says things the sources support | Kesetiaan pada sumber |
| **Hallucination** | A fluent answer not supported by anything | Halusinasi |
| **Answerable question** | The documents really contain the answer | Pertanyaan yang bisa dijawab |
| **Failure mode** | A typical way the system goes wrong | Pola kegagalan |
| **Root cause** | The first step that went wrong | Akar masalah |
| **Regression test** | A saved case that must keep passing | Tes regresi |

## 🧠 The big idea

When a package does not arrive, you do not shout at "the delivery company". You **follow the tracking**: was it packed? did it leave the warehouse? did it reach the city? was it delivered to the wrong door? Each question points to a different person who can fix it.

A RAG answer has the same chain: **Is the fact in the data? Was it retrieved? Did it reach the prompt? Did the model use it correctly?** Without a trace, you only see the bad answer and start changing random things. With a trace, you know which link broke, and the fix is usually obvious.

## ❓ Why it matters

"The AI gave a wrong answer" is not a bug report. Teams that cannot locate failures spend weeks switching models, rewriting prompts and re-chunking without improvement. Teams that **trace and classify** find that two or three causes explain most failures, fix those, and see big jumps. It also protects you from fixing one question and silently breaking ten others.

## 📖 Step by step

### 1. The four questions

For one failed question, ask in this order:

```text
1. Is the answer in the corpus at all?          no → the right outcome is "I do not know" (content gap)
2. Was a right chunk RETRIEVED (in the pool)?   no → retrieval miss
3. Did it reach the PROMPT (after k / budget / re-ranking)?   no → dropped before the prompt
4. Was the answer correct and GROUNDED?         no → generation problem (not used / ungrounded / wrong refusal)
```

The first "no" is the **root cause**. Fix that link first: later links cannot repair an earlier one.

### 2. A taxonomy you can code

| Category | Meaning | Typical fixes |
|---|---|---|
| `ok` | correct and grounded | none |
| `correct_refusal` | no answer in the corpus, and the system said so | none (this is success) |
| `hallucinated_answer` | no answer in the corpus, but the system answered | refusal path: score floor, "I do not know" rule, answerability check |
| `retrieval_miss` | the right chunk was never found | chunking, hybrid search, embedding model, query rewriting, filters |
| `dropped_before_prompt` | found, but cut by `k`, the token budget or ranking | raise `k` or budget, add or fix the re-ranker |
| `not_used` | the right chunk was in the prompt, the answer is still wrong | prompt wording, less noise, chunk order, a stronger model |
| `ungrounded` | correct but not supported by the sources | require citations, check quotes, stricter grounding rule |
| `wrong_refusal` | the model said "I do not know" though it had the answer | loosen refusal rules, clarify permission to answer |

### 3. Record a trace for every request

You can only diagnose what you logged. Keep one record per request:

```python
trace = {
    "question": question,
    "rewritten_query": rewritten,          # if you rewrite
    "filters": filters,                    # tenant, language, status
    "retrieved": [{"id": ..., "score": ...}, ...],          # the pool, best first
    "reranked": [...],                                       # after re-ranking
    "prompt_ids": [...],                                     # exactly what went into the prompt, in order
    "prompt_tokens": ..., "output_tokens": ..., "model": ..., "prompt_version": ...,
    "answer": answer,
    "citations_valid": True,
    "timings_ms": {"retrieve": ..., "rerank": ..., "llm": ...},
}
```

Be careful with personal data in traces: mask it, set a retention period, and restrict who can read them.

For your **test set**, each question also needs the ground truth: `relevant_ids` (the chunks that contain the answer; an empty list means unanswerable), and a judgement of whether the answer was correct and grounded (by a human, or by a judge model that you have checked against humans).

### 4. Classify in code

```python
def diagnose(trace):
    relevant = set(trace["relevant_ids"])
    if not relevant:                                        # nothing in the corpus can answer this
        return "correct_refusal" if trace["refused"] else "hallucinated_answer"
    if not relevant & set(trace["retrieved_ids"]):
        return "retrieval_miss"
    if not relevant & set(trace["prompt_ids"]):
        return "dropped_before_prompt"
    if trace["refused"]:
        return "wrong_refusal"
    if trace["answer_is_correct"] and trace["answer_is_grounded"]:
        return "ok"
    if trace["answer_is_correct"]:
        return "ungrounded"
    return "not_used"
```

The rules are ordered like the chain of questions, so the **first broken link** wins. Then count over the whole test set and make a plan:

```python
def summarize(traces):
    counts = {c: 0 for c in CATEGORIES}
    answerable = hit = 0
    for t in traces:
        counts[diagnose(t)] += 1
        if t["relevant_ids"]:
            answerable += 1
            if set(t["relevant_ids"]) & set(t["retrieved_ids"]):
                hit += 1
    failures = [c for c in CATEGORIES if c not in ("ok", "correct_refusal")]
    worst = max(failures, key=lambda c: counts[c]) if any(counts[c] for c in failures) else None
    return {"total": len(traces), "counts": counts,
            "retrieval_recall": hit / answerable if answerable else 1.0, "worst": worst}
```

```python
def plan(traces):
    counts = summarize(traces)["counts"]
    rows = [(c, counts[c]) for c in CATEGORIES if c not in ("ok", "correct_refusal") and counts[c] > 0]
    rows.sort(key=lambda r: -r[1])                                  # biggest problem first
    return [f"{c} ({n}): {FIXES[c]}" for c, n in rows]
```

Typical output:

```text
retrieval_miss (12): improve retrieval: chunking, query rewriting, hybrid search, embedding model, filters
dropped_before_prompt (5): raise k or the context budget, or fix the ranking / re-ranker so the right chunk is kept
hallucinated_answer (3): add a refusal path: a minimum score, an 'I do not know' instruction, an answerability check
```

Now the team knows what to work on first. Fix the biggest category, re-run the same test set, and compare.

### 5. Deeper causes behind each category

**Retrieval miss.** Look at the missed question and the chunk that should have matched.
- Wording differs from the document (synonyms, slang, another language) → multilingual embeddings, query rewriting, multi-query.
- It contains an exact code or name → hybrid search.
- The chunk lost its context (heading, product name) → heading path, contextual chunk.
- The filter excluded it (wrong tenant, language, status) → check the filter logic.
- The document was never indexed or is out of date → check ingestion and freshness.

**Dropped before the prompt.** Print the pool with scores. If the right chunk is rank 12 and you keep 5, raise the pool for re-ranking or improve ranking. If the token budget cut it, shorten chunks, use parent-child, or compress.

**Not used.** The right chunk is in the prompt but the answer is wrong. Look at the prompt: too many chunks (noise)? contradictory chunks? the key sentence in the middle? an instruction conflict? Try fewer chunks, a better order, a clearer instruction ("if two sources conflict, prefer the newest"), or a stronger model.

**Hallucinated or ungrounded.** The model filled gaps with its own knowledge. Strengthen the grounding rule, require citations and validate them (previous lesson), add a score floor, and test with unanswerable questions on purpose.

**Wrong refusal.** The refusal rule is too eager or the sources were hard to read. Soften the instruction ("answer if the sources contain the answer, even partly; say what is missing"), and check chunk quality.

### 6. Failures that are not in the pipeline

| Problem | Symptom | Fix |
|---|---|---|
| **Stale data** | correct citation, outdated fact | freshness metadata, scheduled re-index, prefer newer sources, show dates |
| **Conflicting sources** | two chunks disagree | resolve at the source; tell the model the rule (newest wins); show both |
| **Multi-hop questions** | answer needs facts from two documents | retrieve per sub-question (query decomposition), agentic RAG |
| **Ambiguous questions** | the user means something else | ask a clarifying question instead of guessing |
| **Prompt injection in documents** | the answer follows an instruction hidden in a chunk | mark documents as data, limit tools, check outputs (week 2) |
| **Permission leak** | the answer mentions a document the user may not see | filter in retrieval; test with two users |
| **Numbers and tables** | wrong figure from a table | table-aware chunks; compute with a tool instead of reading |
| **Language mismatch** | Indonesian question, English document | multilingual embeddings; answer in the user's language |

### 7. Turn every failure into a test

The best test set grows from real failures. For each failure:

1. Add the question, the `relevant_ids` (or "none"), and the expected key facts to the test set.
2. Fix the cause.
3. Run the **whole** set (not only the new case) to check nothing else broke.
4. Keep a short changelog: "Added heading path → retrieval_miss 12 → 6".

Also sample **successes** now and then: a correct answer with a wrong citation is a hidden failure.

### 8. A working rhythm

- **Daily/weekly:** read 20 random traces and 20 flagged ones (thumbs down, no-answer, invalid citations).
- **Before each release:** run the full test set; compare the category counts with the last release; block the release on regressions.
- **Dashboards:** share of `retrieval_miss`, recall of the pool, "no answer" rate, citation validity, tokens per answer, p95 latency.
- **One change at a time**, with the numbers recorded.

### Choosing your setup

| Symptom | Look first at |
|---|---|
| Right document exists, answer wrong | the four questions: retrieved? in the prompt? |
| Answers with confident wrong facts | grounding rule, score floor, citation validation |
| Many "I do not know" for answerable questions | retrieval recall, refusal rule |
| Great on short questions, bad on chat follow-ups | query rewriting |
| Good on prose, bad on tables or codes | table-aware chunks, hybrid search |
| Quality dropped after a content update | indexing, duplicates, stale chunks |

- ✅ Find the first broken link before changing anything.
- ✅ Log the pool, the prompt chunks, scores and versions.
- 🚫 Swapping models before you have looked at one trace.
- 🚫 Fixing a failure without adding it to the test set.

## ⚠️ Common mistakes

- Judging the system only by its final answers.
- Changing several things at once, so the cause of an improvement is unknown.
- A test set without unanswerable questions (hallucination stays invisible).
- Blaming the model for what is a retrieval miss.
- Logging only the answer, not the retrieved ids and scores.
- Forgetting that the "right" documents change when the corpus changes.
- Fixing the loudest complaint instead of the biggest category.
- No regression run after a fix.

:::revoshop
Pretend your RevoShop assistant answered "Shipping to Papua is free" but the real policy says "Rp 50.000". Walk through the four questions: what would you check at each step, what trace fields would you need, and which category and fix are most likely if the right policy chunk was ranked 8th?
:::

## 🏆 Best practices

- [ ] Log a full trace for every request (with personal data masked).
- [ ] Diagnose in order: corpus → retrieved → in prompt → correct and grounded.
- [ ] Keep unanswerable questions in your test set.
- [ ] Count failure categories and fix the biggest one first.
- [ ] Change one thing at a time and re-run the whole test set.
- [ ] Turn every real failure into a regression test.
- [ ] Track recall of the pool, citation validity and "no answer" rate over time.
- [ ] Review random successes too, not only failures.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain RAG debugging with the package-tracking picture. Why is the first broken link the one to fix?

## 📐 Design it

Last month SupportDesk AI's quality score dropped from 82% to 74% after a content team uploaded 400 new articles. Customers complain about outdated answers and about "I could not find this" for things that exist. Design the investigation: what you look at, in what order, what the likely causes are, and how you prevent a repeat.

:::quiz
Show a possible design

- **Start with data, not guesses:** run the 200-question test set and classify each result with `diagnose`; compare the counts with last month's. Expect a rise in `retrieval_miss`, `dropped_before_prompt` and possibly `not_used`.
- **Likely cause 1: duplicates and old versions.** 400 new articles may duplicate or supersede old ones. Check how many near-duplicates exist; the top 5 may now contain two copies and an old version → deduplicate, prefer the newest by `updated_at`, and archive superseded articles.
- **Likely cause 2: pool crowding.** More documents mean more near-matches; the right chunk slid to rank 6–12 → increase the pool, add or tune the re-ranker.
- **Likely cause 3: missing metadata.** If new articles lack `product`, `language` or `status`, filters exclude them or let drafts in → validate metadata at ingestion; reject articles without required fields.
- **Likely cause 4: changed chunking.** Did the ingestion job use a different chunker or settings for new files? Check `chunker_version` and `embedding_model` on the new chunks.
- **Outdated answers:** find answers whose cited chunk is old although a newer article exists; add freshness to ranking and show dates.
- **"I could not find this":** look at the `retrieval_miss` list and open the misses by hand: wording mismatch, filter, or the document is missing/unindexed.
- **Prevention:** an ingestion checklist and automated checks (required metadata, duplicates, chunk count, embedding model), an evaluation run in CI on every content import, an alert when `retrieval_recall` or the category mix shifts, and each failure added to the test set.
- **Communication:** report the root cause with numbers, the fixes, and the before/after test results.

**Rule shown:** classify first, fix the biggest cause, prove it with the same test set, and automate the check so it never surprises you again.
:::

### 📝 Self-review checklist

- [ ] The investigation starts from traces and a test set
- [ ] Failures are classified by the first broken link
- [ ] Fixes are ordered by impact and verified by re-running the set
- [ ] There is automation to catch the next regression

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m7/w4/05-rag-diagnosis" ai="no-ai" title="Diagnose RAG failures"}
Write `diagnose` (ordered rules: unanswerable, retrieval miss, dropped before the prompt, wrong refusal, ok, ungrounded, not used), `summarize` (counts for every category, retrieval recall on answerable questions, the worst category) and `plan` (a to-do list sorted by size). Each trace is a plain dict, so no API key is needed.
:::

:::hints
- Check `relevant_ids` first: empty means the question is unanswerable (`correct_refusal` or `hallucinated_answer`).
- Then compare sets: `relevant & retrieved_ids`, then `relevant & prompt_ids`.
- After those two, `refused` means `wrong_refusal`; otherwise combine `answer_is_correct` and `answer_is_grounded`.
- `summarize`: start counts from `{c: 0 for c in CATEGORIES}`; the recall denominator counts only traces with non-empty `relevant_ids`.
- `worst`: ignore `ok` and `correct_refusal`; with `max` over the `CATEGORIES` order, ties go to the earlier category.
- `plan`: a stable `sort(key=lambda r: -r[1])` keeps the category order for ties.
:::

## ✅ Quick check

:::quiz
The right chunk is rank 9 in the pool, and the prompt keeps 5 chunks. Which category is it, and what is the fix?

`dropped_before_prompt`. The retrieval found it, but ranking and the `k`/budget cut it. Improve the ranking (a re-ranker, hybrid search), or raise the number of chunks or the budget, while watching token cost.
:::

:::quiz
Why must a test set include questions that the documents cannot answer?

Without them, hallucination is invisible: the system gets no penalty for answering from imagination. Unanswerable questions let you measure whether the system correctly says "I do not know", and tune the score floor and refusal rule.
:::

:::quiz
Quality dropped after a big content upload. What do you check first?

Classify the test set results and compare category counts with before. Typical findings are duplicates and old versions crowding the top results, missing metadata that breaks filters, or a different chunker or embedding model used for the new files.
:::

## 📚 Keep learning

- [Anthropic docs: Reduce hallucinations](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations)
- [Barnett et al.: Seven Failure Points When Engineering a RAG System (paper)](https://arxiv.org/abs/2401.05856)
- [Ragas documentation](https://docs.ragas.io/)

---
title: "Evals Libraries: Ragas & DeepEval"
summary: "Use evaluation libraries wisely — what faithfulness, context precision, context recall and answer relevancy really measure, how the libraries compute them with a judge model, cost and noise traps, and how to wire them into pytest and CI."
type: lesson
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: core, ops: optional }
durationMinutes: 150
tags: [evals, ragas, deepeval, rag-metrics, faithfulness, ci]
lastReviewed: 2026-10
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What **Ragas** and **DeepEval** are for, and when a library helps
- The **RAG metrics**: faithfulness, context precision, context recall, answer relevancy
- How these metrics are **computed** (so you can trust or doubt them)
- **Costs and traps**: judge calls, noise, language, black boxes
- How to run evals in **pytest and CI**
- A sensible **workflow**: your own checks first, a library for the rest

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Ragas** | An open-source library of metrics for RAG systems | Pustaka metrik RAG |
| **DeepEval** | An open-source testing framework for LLM apps, in a pytest style | Kerangka uji LLM |
| **Faithfulness** | Are the answer's claims supported by the retrieved context? | Kesetiaan pada konteks |
| **Context precision** | Are the relevant chunks ranked near the top? | Ketepatan konteks |
| **Context recall** | Does the context contain what is needed to answer? | Ketercapaian konteks |
| **Answer relevancy** | Does the answer address the question asked? | Relevansi jawaban |
| **Metric threshold** | The score above which a test passes | Ambang metrik |
| **Judge model** | The LLM the library calls to make each judgement | Model juri |

## 🧠 The big idea

Building every check yourself is like **making your own measuring tape**. It is a great way to learn what a centimetre is. But for real work you buy a good tape measure. Evaluation libraries are the measuring tapes of RAG: ready-made metrics with names everyone uses ("faithfulness 0.82"), a test runner, and reports.

A good craftsperson also **knows how the tape was made**, checks it against a known length once in a while, and does not use a tape measure for something that needs a scale. In this lesson you learn what is inside the tape.

## ❓ Why it matters

- **Shared vocabulary.** "Faithfulness" and "context recall" are the standard words for RAG quality. Interviewers and teammates know them.
- **Speed.** You do not need to write claim extraction, judge prompts and aggregation from scratch.
- **Integration.** They plug into pytest, CI and dashboards.

But libraries can fool you. They make many judge calls (money and time), they are noisy, their default prompts may not suit Indonesian or your domain, and a number like 0.82 means little if you do not know how it was produced. Knowing the idea behind each metric is what lets you trust it for the right job.

## 📖 Step by step

### 1. What the metrics ask

All the standard RAG metrics are answers to simple questions about one test case: a **question**, the **retrieved contexts**, the **answer**, and (sometimes) a **reference answer** or the facts that are needed.

| Metric | Question | Needs a reference? | Low value means |
|---|---|---|---|
| **Faithfulness** | Are the answer's claims supported by the contexts? | no | the answer adds things the sources do not say |
| **Context precision** | Are the relevant chunks ranked at the top? | yes (which are relevant) | noisy or badly ranked retrieval |
| **Context recall** | Does the retrieved context contain the facts needed? | yes (the needed facts) | retrieval missed information |
| **Answer relevancy** | Does the answer address the question? | no | the answer is off-topic or evasive |
| **Answer correctness** | Does the answer match the reference answer? | yes | the answer is wrong or incomplete |

Notice how they point to different stages: **recall and precision** judge **retrieval**; **faithfulness** judges **generation vs the context**; **relevancy and correctness** judge the **final answer**. That is exactly the diagnosis chain from week 4.

### 2. Build simple versions, to understand them

Real libraries use a judge model. To see the idea, build rough word-matching versions.

**Faithfulness:** split the answer into claims, check each against the context.

```python
import re

STOPWORDS = {"a", "an", "the", "is", "are", "was", "were", "be", "been", "to", "of", "in", "on", "at", "for",
             "and", "or", "it", "its", "this", "that", "with", "as", "by", "from", "we", "you", "your", "our",
             "can", "will", "after"}

def split_claims(answer):
    text = re.sub(r"\s*\[\s*\d+(?:\s*,\s*\d+)*\s*\]", "", answer)         # remove [1] markers
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]

def content_words(text):
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS}

def claim_supported(claim, contexts, threshold=0.8):
    words = content_words(claim)
    if not words:
        return True
    available = set()
    for context in contexts:
        available |= content_words(context)
    return len(words & available) / len(words) >= threshold

def faithfulness(answer, contexts, threshold=0.8):
    claims = split_claims(answer)
    if not claims:
        return 1.0
    return sum(claim_supported(c, contexts, threshold) for c in claims) / len(claims)
```

A real library asks a model to (1) break the answer into claims and (2) judge for each claim whether the context supports it. Same shape, much smarter judgement.

**Context precision** is average precision over the ranking:

```python
def context_precision(relevance_flags):
    total, relevant_so_far = 0.0, 0
    for k, flag in enumerate(relevance_flags, start=1):
        if flag:
            relevant_so_far += 1
            total += relevant_so_far / k              # precision at this rank
    return total / relevant_so_far if relevant_so_far else 0.0
```

```text
[True, False, True]  → (1/1 + 2/3) / 2 = 0.83      the relevant chunks are near the top
[False, False, True] → (1/3) / 1       = 0.33      the relevant chunk is buried
```

**Context recall** checks the needed facts:

```python
def _share(facts, text):
    if not facts:
        return 1.0
    lowered = text.lower()
    return sum(f.lower() in lowered for f in facts) / len(facts)

def context_recall(required_facts, contexts):
    return _share(required_facts, " ".join(contexts))
```

In a real library, the "needed facts" are usually statements in a reference answer, and a model checks whether each can be found in the context.

### 3. How a typical library is used

The exact API changes between versions, so read the current docs, but the shape is stable:

```python
# Pseudocode — check the library's documentation for the exact names in your version
from some_eval_library import evaluate, FaithfulnessMetric, ContextRecallMetric

test_cases = [
    {
        "question": "How long do refunds take?",
        "answer": "Refunds take 7 days [1].",
        "contexts": ["Refunds are paid back within 7 days after we receive the item."],
        "reference": "7 days",
    },
    # ... one dict per case, taken from your test set + your system's actual outputs
]

result = evaluate(test_cases, metrics=[FaithfulnessMetric(threshold=0.8), ContextRecallMetric(threshold=0.7)],
                  judge_model="<a model you choose>")
print(result)          # scores per case and averages
```

DeepEval is built around **pytest**: each test case becomes a test, a metric has a threshold, and a failing score fails the test. Ragas is built around **datasets and metrics** you evaluate in bulk. Both can use your own judge model and your own data. Others exist (promptfoo, Inspect, TruLens, Langfuse evaluators): the ideas carry over.

The workflow:

1. Run your RAG system over the test set and **save** the question, contexts, answer, citations and timings (your traces, last lesson).
2. Feed those records to the library.
3. Read the per-case scores, sort by the worst, and open the traces.
4. Store the results with the version of the system, the prompts and the judge.

### 4. Costs and traps

| Trap | Why it matters | What to do |
|---|---|---|
| **Many judge calls** | each metric on each case calls a model several times | start with 50–100 cases; use a cheaper judge for easy metrics; cache results; run the full set nightly, a small set per commit |
| **Noise** | the judge is a model: scores wobble between runs | fix the temperature low; average over repeats; compare on the same cases; ignore tiny differences |
| **Judge quality** | a weak judge gives meaningless scores | choose a strong model; calibrate against human labels on a sample (previous lesson) |
| **Language** | default prompts are English; Indonesian or mixed text may be judged worse | test the metric on your language; translate or adapt the prompts if the library allows |
| **Black box** | you cannot explain why 0.76 | read the per-claim verdicts and reasons; keep your own simple checks beside it |
| **Metric ≠ goal** | high faithfulness with useless answers ("I do not know" to everything) | always read several metrics together plus a task-level metric |
| **Version drift** | a library update changes prompts and scores | pin versions; re-baseline when you upgrade |
| **Data leakage** | tuning the system until the library scores high on your test cases | keep a held-out set; use the library as a signal, not a target |

A good rule: **cheap, deterministic checks first** (citations valid, required facts present, forbidden phrases absent, retrieval recall from labelled ids), then a library for faithfulness and relevancy, then humans for a sample.

### 5. Run it in pytest and CI

Make the eval a test that fails when quality drops:

```python
# tests/test_rag_quality.py
import json
import pytest

CASES = json.load(open("evals/dev_cases.json"))

@pytest.mark.parametrize("case", CASES, ids=lambda c: c["id"])
def test_case(case, rag_run):                       # rag_run: a fixture that runs your system and caches the output
    output = rag_run(case["input"])
    assert faithfulness(output["answer"], output["contexts"]) >= 0.8
    assert context_recall(case["required_facts"], output["contexts"]) >= 0.7
```

Better for large sets: run the whole evaluation as one job, save a JSON report, and then **compare with the last accepted report** using a gate (from lesson 1): no important case may regress, and aggregate scores must stay above a floor. Upload the report as a CI artifact so reviewers can read it. Run a small subset on every pull request, and the full set before release.

### 6. Read the results like an engineer

- Sort cases by **lowest faithfulness**, and read the answer next to its contexts: is it a real hallucination, or a paraphrase that the metric missed?
- Sort by **lowest context recall**: these are retrieval problems; open the traces.
- Check that a **score change after a prompt edit** is larger than the run-to-run noise (run the same version twice to measure it).
- Look at the **score distribution**, not only the mean: a few catastrophic cases hide behind a nice average.
- Track **cost and latency** with the scores.

### Choosing your setup

| Situation | Do this |
|---|---|
| Small project, learning | your own checks (this week's exercises) + a few judge metrics |
| Need standard RAG numbers quickly | Ragas or DeepEval with a strong judge, on 50–100 cases |
| Already use pytest and CI | DeepEval-style tests, or your own pytest wrapper |
| Indonesian or mixed language | test the metrics on your data; adapt prompts; spot-check by humans |
| Scores wobble | fix the judge settings; repeat runs; use larger sets |
| Library upgrade | pin versions; re-baseline |

- ✅ Understand what each metric measures before you trust it.
- ✅ Store traces so you can open low-scoring cases.
- 🚫 Optimising a prompt until the library number is high.
- 🚫 Reporting a library score without the judge model and the version.

## ⚠️ Common mistakes

- Treating "faithfulness 0.9" as "the answers are true" (it only means: consistent with the retrieved context, whatever that context says).
- Using the same model as judge and as system.
- Running the library on three cases and drawing conclusions.
- Ignoring cost: a big eval run can cost more than the day's traffic.
- Not pinning versions, then wondering why the scores jumped.
- Skipping human spot checks.
- No link from a bad score back to the trace.
- Replacing all simple checks with a library.

:::revoshop
Choose two metrics (from faithfulness, context recall, context precision, answer relevancy) that fit RevoShop's returns assistant best, and explain why. For one metric, write the exact trace data you need to log so a library can compute it later.
:::

## 🏆 Best practices

- [ ] Know what each metric measures and which stage it points at.
- [ ] Start with cheap deterministic checks; add library metrics for faithfulness and relevancy.
- [ ] Choose a strong judge model, set low randomness, and pin library and judge versions.
- [ ] Calibrate the judged metrics against human labels on a sample.
- [ ] Save traces (question, contexts, answer, citations) so every score can be inspected.
- [ ] Gate on regressions against a stored report; run a small subset per pull request.
- [ ] Read the worst cases, not only the average.
- [ ] Track cost and latency next to quality.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain evaluation libraries with the measuring-tape picture. Why is it still important to know how the tape was made?

## 📐 Design it

SupportDesk AI wants to report RAG quality in CI. The test set has 150 cases in Indonesian and English. A full run with a library costs about 6 USD and takes 15 minutes; pull requests happen 20 times a day. Design what runs when, which metrics you use, how you control cost and noise, and how a reviewer reads the result.

:::quiz
Show a possible design

- **Three layers.** (1) On every commit: deterministic checks only (valid citations, required facts present, forbidden phrases absent, retrieval recall from labelled chunk ids, schema, length): seconds, free. (2) On every pull request that touches prompts, retrieval or models: a **50-case subset** with the library's faithfulness and context-recall metrics, cheaper judge for context metrics, results cached by (case, system version) so unchanged cases are not re-judged. (3) Nightly and before release: the **full 150 cases**, 3 repeats for the judge metrics, plus a weekly human spot check of 20 judge verdicts.
- **Metrics:** retrieval — context recall and recall@k by labelled ids; generation — faithfulness; end-to-end — answer correctness against reference facts, refusal rate on unanswerable cases; operations — tokens, cost and p95 latency per answer.
- **Cost control:** subset plus caching brings the PR run to roughly 1 USD; stronger judge only for faithfulness; batch API for the nightly run; budget alert on the eval spend.
- **Noise:** judge temperature low; repeat full runs 3×, report mean and spread; gate only on differences above the measured noise (for example more than 3 points) and on any regression in `critical` cases.
- **Language:** compare judge verdicts with human labels on Indonesian cases (kappa) before trusting them; if weak, adapt prompts or use a different judge model.
- **Reading the result:** the CI job posts a short table (scores vs baseline, fixed/broken cases, cost, latency) and links to a report with the worst 10 cases showing question, contexts, answer and the judge's reasoning.
- **Governance:** pin library and judge versions; a change to either triggers a re-baseline and a note in the changelog.

**Rule shown:** layer cheap deterministic checks, targeted library metrics and human spot checks, and make the result readable, bounded in cost, and tied to traces.
:::

### 📝 Self-review checklist

- [ ] Each metric is tied to a stage and a fix
- [ ] Cheap checks run first; library metrics are targeted
- [ ] Cost, noise and judge quality are controlled
- [ ] Versions are pinned and traces are saved
- [ ] The CI output is readable and gates on regressions

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m7/w5/04-rag-metrics" ai="no-ai" title="Simple RAG metrics"}
Write `split_claims` (remove `[n]` markers and the space before them, then split sentences), `content_words`, `claim_supported`, `faithfulness`, `context_precision` (average precision), `context_recall` and `answer_coverage`. They are word-matching stand-ins for what Ragas and DeepEval ask a judge model to decide. No API key needed.
:::

:::hints
- `split_claims`: `re.sub(r"\s*\[\s*\d+(?:\s*,\s*\d+)*\s*\]", "", answer)` then split on `(?<=[.!?])\s+`.
- `content_words`: lowercase `[a-z0-9]+` tokens, minus `STOPWORDS`.
- `claim_supported`: union of the contexts' content words; ratio of the claim's words found; no content words means supported.
- `context_precision`: add `relevant_so_far / k` at each relevant rank, divide by the number of relevant chunks.
- `context_recall` and `answer_coverage`: case-insensitive substring checks; no facts means `1.0`.
:::

## ✅ Quick check

:::quiz
Faithfulness is 0.95 but users say the answers are wrong. What can explain it?

Faithfulness only measures consistency with the retrieved context. If retrieval brought the wrong, outdated or incomplete chunks (low context recall), a faithful answer can still be wrong. Check context recall and the traces.
:::

:::quiz
Why compare a library's judge scores with human labels at least once?

The library's number comes from a judge model with its own biases and its own prompts, which may handle your language or domain poorly. Comparing with human labels (agreement and kappa) tells you how far the score can be trusted.
:::

:::quiz
Why keep simple deterministic checks even when you use a library?

They are free, fast and exactly reproducible, so they catch many failures (invalid citations, forbidden phrases, missing facts) on every commit. The library's judge-based metrics are slower, costlier and noisier, so they complement the cheap checks instead of replacing them.
:::

## 📚 Keep learning

- [Ragas documentation](https://docs.ragas.io/)
- [DeepEval documentation](https://deepeval.com/docs/getting-started)
- [Anthropic docs: Test and evaluate](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)

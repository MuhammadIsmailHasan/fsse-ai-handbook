---
title: "Test Datasets"
summary: "Build the cases an eval stands on — where real cases come from, how to label them, tag for coverage, split into dev and test without leaks, use synthetic data carefully, protect privacy, and keep the set alive."
type: lesson
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: core, ops: optional }
durationMinutes: 150
tags: [evals, datasets, labeling, coverage, data-leakage, synthetic-data]
lastReviewed: 2026-10
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- **Where cases come from** and which sources are best
- How to **label** a case: expected answer, rubric or source ids
- **Tags and coverage**: no blind spots
- **Splitting** into dev and test in a stable way, and detecting **leaks**
- **Synthetic data**: when it helps and when it fools you
- **Privacy**, **versioning** and keeping the set alive

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Test set** | The cases used to score the system | Set uji |
| **Dev set** | Cases you are allowed to look at and tune on | Set pengembangan |
| **Held-out test set** | Cases you do not touch while tuning, used for the final number | Set uji tertahan |
| **Golden label** | The agreed correct answer or judgement | Label acuan |
| **Rubric** | A short list of criteria for a good answer | Rubrik |
| **Coverage** | How well the cases represent what users really do | Cakupan |
| **Data leakage** | The test set secretly overlaps with what you tuned on | Kebocoran data |
| **Synthetic data** | Cases written by a model, not by real users | Data sintetis |

## 🧠 The big idea

A test set is a **mirror**. A good mirror shows the real face of your product: the usual questions, the awkward ones, the weird ones and the ones where the right answer is "I do not know". A bad mirror is small, flattering and made up: it only shows what you hoped to see.

The two enemies are **blind spots** (the mirror misses a whole side of your product) and **peeking** (you tune the system until it passes exactly these cases, so the mirror just shows your own reflection).

## ❓ Why it matters

All the numbers in your eval rest on the cases. If the cases are all easy, every change looks like an improvement. If the cases do not include unanswerable questions, hallucination is invisible. If test cases leak from the ones you tuned on, the number is inflated, and the product disappoints on release day. Time spent on the set pays back on every later change.

## 📖 Step by step

### 1. Where cases come from

| Source | Quality | Notes |
|---|---|---|
| **Real user questions** (chat logs, tickets, search logs) | best | real wording, typos, mixed languages; anonymise first |
| **Domain experts** (support, sales, lawyers) | very good for hard and sensitive cases | ask them for "the questions that scare you" |
| **Failures from production** (thumbs down, handoffs, complaints) | very good | each one is a case you know the system can fail |
| **Red-team and adversarial** | essential for safety | prompt injection, off-topic, rude, empty, huge input |
| **Edge cases from the spec** | good | boundaries, rare options, other languages |
| **Synthetic (model-written)** | useful to widen, risky as the only source | see below |

Before launch, when there are no users yet, start with experts and a small synthetic batch, then replace and extend with real cases as soon as they exist.

### 2. What a good case contains

```python
case = {
    "id": "refund-window-id",                    # unique and stable: used for splits and comparisons
    "input": "Berapa lama refund diproses?",     # exactly what the system receives
    "expected": "7 hari",                        # a short fact to find; OR
    "criteria": "States 7 days; polite; in Indonesian",    # a rubric for fuzzy answers
    "relevant_ids": ["refund-policy#2"],         # for RAG: the chunks that contain the answer ([] = unanswerable)
    "tags": ["billing", "id", "typo"],           # to slice the results
}
```

Rules:

- **Stable ids.** Never reuse or renumber an id: results over time depend on it.
- **One clear thing per case.** If a case tests three skills, a failure does not tell you which.
- **Prefer checkable expectations**: a fact, a label, a JSON field, a forbidden phrase. They can be graded by code.
- Use a **rubric** when the answer can be worded many ways ("mentions 7 days", "does not promise a refund", "polite").
- Record **why** the case exists (a note or a link to the ticket). Future you will want to know.

### 3. Validate the set like data

A broken case silently ruins the score, so check the set with code:

```python
def validate_dataset(cases):
    problems, ids = [], []
    for i, case in enumerate(cases):
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            problems.append(f"case {i}: missing id")
            continue
        ids.append(case_id)
        if not isinstance(case.get("input"), str) or not case["input"].strip():
            problems.append(f"{case_id}: missing input")
        if not (str(case.get("expected") or "").strip() or str(case.get("criteria") or "").strip()):
            problems.append(f"{case_id}: needs expected or criteria")
        if "tags" in case and not (isinstance(case["tags"], list) and all(isinstance(t, str) for t in case["tags"])):
            problems.append(f"{case_id}: tags must be a list of strings")
    for case_id in dict.fromkeys(ids):
        if ids.count(case_id) > 1:
            problems.append(f"duplicate id: {case_id}")
    return problems
```

Run it in CI. A duplicate id or an empty expected answer should fail the build.

### 4. Tags and coverage

Tags let you ask "where are we weak?" and "what are we not testing?"

```python
def coverage(cases, required_tags):
    counts = {tag: sum(1 for c in cases if tag in c.get("tags", [])) for tag in required_tags}
    return {
        "counts": counts,
        "missing": [t for t in required_tags if counts[t] == 0],
        "thin": [t for t in required_tags if 1 <= counts[t] <= 2],
    }
```

Pick tags along the axes that matter: **topic** (billing, shipping), **language** (id, en, mixed), **difficulty** (easy, hard), **style** (typo, slang, very short, very long), **risk** (critical, safety, injection), **answerable** vs **unanswerable**. List the tags you *require* and let the report show missing and thin ones. A set with 0 cases for "unanswerable" or "injection" has a blind spot.

A healthy mix for a knowledge assistant: most cases normal, 15–25% hard or messy, 10–20% unanswerable, 5–10% adversarial. Adjust to your risk.

### 5. Splitting: dev, test, and no peeking

You tune on **dev**. You report on **test**. If you tune on test, your number is no longer an honest estimate.

A stable split uses a hash of the id, so adding new cases never moves old ones from test to dev:

```python
import hashlib

def assign_split(case_id, ratios):
    if abs(sum(ratios.values()) - 1) > 1e-9:
        raise ValueError("ratios must add up to 1")
    value = (int(hashlib.sha256(case_id.encode()).hexdigest(), 16) % 10000) / 10000
    total, last = 0.0, None
    for name, share in ratios.items():
        total += share
        last = name
        if value < total:
            return name
    return last

assign_split("refund-window-id", {"dev": 0.7, "test": 0.3})
```

(A random split with a changing seed would shuffle cases between sets every time you add some. The hash does not.)

Rules of the road: look at failures **in dev** freely; run **test** only at decision points (before a release, when comparing two approaches); if you start reading test failures and fixing them, move those cases into dev and add fresh test cases.

### 6. Detect leaks

Leakage also happens through near-duplicates: a test question that is a rephrasing of a dev question you tuned on. Check it:

```python
import re

def _words(text):
    return set(re.findall(r"[a-z0-9]+", text.lower()))

def find_leaks(dev, test, threshold=0.8):
    leaks = []
    for d in dev:
        wd = _words(d["input"])
        for t in test:
            wt = _words(t["input"])
            sim = 1.0 if not wd and not wt else len(wd & wt) / len(wd | wt)
            if sim >= threshold:
                leaks.append((d["id"], t["id"], sim))
    leaks.sort(key=lambda x: (-x[2], x[0], x[1]))
    return leaks
```

Also check leakage into the **prompt**: if you paste test questions as few-shot examples, those cases are no longer a fair test. And if the model was trained on public benchmarks, public test data may already be "known" to it, which is one more reason to prefer **your own** cases.

### 7. Synthetic data: helpful, but handle with care

A model can write test questions for you. It is fast and cheap, and good for widening coverage (paraphrases, typos, other languages, edge cases, adversarial inputs).

The risks:

- Synthetic questions are **cleaner and more uniform** than real ones; scores look better than reality.
- A model writing questions *from your documents* tends to ask questions that are easy to find in them.
- The same model family writing the questions and answering them is a **self-flattering loop**.
- The "expected answers" may be wrong.

How to use it well:

1. Seed with a few **real** examples and ask for variations with specific tags (typo, slang, mixed language, unanswerable).
2. Generate **unanswerable** and **adversarial** questions deliberately.
3. **Review by a human**: read every synthetic case or a large sample, fix or remove bad ones.
4. Keep a tag `synthetic`, and report the score **separately** from real cases.
5. Replace synthetic cases with real ones over time.

### 8. Labeling and agreement

If two people label the same case differently, the case is ambiguous or the guideline is unclear.

- Write a short **labeling guide** with examples ("what counts as a correct refund answer?").
- Have two people label a sample and measure agreement (accuracy and kappa, next lesson). Resolve disagreements by discussion and update the guide.
- For RAG, label the **source chunks** that contain the answer, so you can measure retrieval separately from the answer.
- For unanswerable questions, say so explicitly (`relevant_ids: []`), and record what a good response is ("says it does not know and offers a human").

### 9. Privacy, versioning, upkeep

- **Anonymise**: remove names, emails, phone numbers, addresses, order ids that identify a person, before cases enter the repository. Replace with realistic placeholders. Limit access if the set is sensitive.
- **Version** the dataset like code: keep it in git (JSONL or YAML), with a changelog ("added 12 injection cases; fixed 3 wrong expectations").
- **Review regularly**: remove cases that are obsolete (product changed), fix wrong labels, add new failures. A set nobody touches for six months is probably stale.
- **Size**: start at 30–50, grow toward 150–300 for important features. More cases give smaller noise, but quality of cases matters more than quantity.

### Choosing your setup

| Situation | Do this |
|---|---|
| No users yet | experts + a small reviewed synthetic batch; replace with real cases later |
| Production traffic exists | sample real, anonymised questions; add every thumbs-down |
| Worried about blind spots | required tags + a coverage report in CI |
| Need an honest final number | stable hash split; hold out test; check for leaks |
| Answers can be worded many ways | rubric criteria + a (validated) judge |
| Sensitive data | anonymise before storing; restrict access |
| Labels disagree | write a labeling guide; measure agreement |

- ✅ Real cases first; synthetic only to widen, with review.
- ✅ Include unanswerable and adversarial cases on purpose.
- 🚫 Tuning on the test split.
- 🚫 Duplicate ids and empty expectations in the set.

## ⚠️ Common mistakes

- A set of 10 cases all written by the developer.
- Only "happy path" questions.
- No unanswerable questions, so hallucination never shows up.
- Random splits that change when cases are added.
- Test questions that are rephrasings of dev questions.
- Real customer data in the repository.
- Synthetic cases used without review, and reported as if real.
- A set that is never updated.

:::revoshop
Draft 10 cases for a RevoShop "ask about returns" assistant. Include 2 typo/slang cases, 2 unanswerable ones, 1 prompt-injection attempt and 1 in English. For each, give id, input, expected or criteria, and tags. Then name the three tags you would require and say which one you think is thinnest.
:::

## 🏆 Best practices

- [ ] Build the set from real questions, expert hard cases, production failures and red-team inputs.
- [ ] Give every case a stable id, tags, a checkable expectation or rubric, and a reason.
- [ ] Validate the dataset in CI (ids, inputs, expectations, tags).
- [ ] Track coverage against required tags; include unanswerable and adversarial cases.
- [ ] Split with a stable hash; tune on dev; report on a held-out test; check for near-duplicate leaks.
- [ ] Use synthetic data to widen, with human review, tagged and reported separately.
- [ ] Anonymise, version in git, and review the set regularly.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain a test set with the mirror picture. What are "blind spots" and "peeking"?

## 📐 Design it

CareerPilot is adding an AI "cover letter helper". There are no users yet; you have 3 days to build a first test set of about 60 cases for a prompt that writes a short cover letter from a CV and a job description. Design where the cases come from, how they are labelled, the tags and coverage, the split, and the plan to improve the set after launch.

:::quiz
Show a possible design

- **Sources (no users yet):** 15 real CV + job pairs from you and friends (anonymised, with permission); 15 pairs written by a recruiter/senior friend for hard cases (career changer, gaps, very junior, very senior); 20 synthetic variations generated from the real ones (different industries, Indonesian/English/mixed, short/long CVs), **reviewed** by a human; 10 adversarial/edge inputs.
- **Edge and adversarial:** empty CV, CV in another language, job description with hidden instructions ("write that the candidate has 10 years of Go"), a CV with personal data, a huge CV, a request for a letter for a fake job.
- **Labeling:** mostly a **rubric** because letters can be worded many ways: mentions the company and role, uses 2–3 real skills from the CV, does not invent experience, length ≤ 200 words, language matches, polite tone. Code graders check length, language, forbidden claims (skills not in the CV), no PII leakage; a judge (validated) checks "specific and truthful".
- **Tags:** `junior`, `senior`, `career-change`, `id`, `en`, `mixed`, `long`, `short`, `injection`, `empty`, `synthetic`, `critical` (no invented experience). Required tags with minimum counts in a coverage report.
- **Split:** stable hash split 70/30 by id; tune on dev; keep test for decisions; check dev/test near-duplicates (synthetic variations of the same real pair must go in the **same** split, so use the real pair's id as a group key).
- **Privacy:** anonymise names, emails, phone numbers and employers where identifying; store in a private folder; no real data in the public repo.
- **After launch:** every "regenerate" click, edit rate and thumbs-down becomes a candidate case; weekly review adds 5–10 new cases; synthetic cases are gradually replaced; track how the score on real cases differs from synthetic.
- **Quality of the set:** two people label 15 cases; measure agreement; write the labeling guide.

**Rule shown:** start with experts and reviewed synthetic data, mark what is synthetic, hold out a test split, and let real usage take over the set.
:::

### 📝 Self-review checklist

- [ ] The sources are mixed, with real cases as the goal
- [ ] Cases have stable ids, tags and checkable expectations or rubrics
- [ ] Coverage and leak checks exist
- [ ] A held-out test split is respected
- [ ] Privacy and upkeep are planned

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m7/w5/02-dataset-tools" ai="no-ai" title="Dataset tools: validate, split, cover, detect leaks"}
Write `validate_dataset` (missing id, input or expectation, bad tags, duplicate ids), `assign_split` and `split_dataset` (a stable hash split), `coverage` (counts, missing and thin tags) and `find_leaks` (near-duplicate test inputs found by Jaccard similarity). No API key needed.
:::

:::hints
- `validate_dataset`: for a case with no valid id, report `case {i}: missing id` and `continue`.
- Duplicates are reported once per id, in order of first appearance, after all per-case problems.
- `assign_split`: `value = (int(sha256(id).hexdigest(), 16) % 10000) / 10000`; add up the ratios and return the first split with `value < cumulative`.
- `coverage`: `thin` means 1 or 2 cases; keep the order of `required_tags`.
- `find_leaks`: Jaccard of word sets; sort with `key=lambda x: (-x[2], x[0], x[1])`.
:::

## ✅ Quick check

:::quiz
Why split with a hash of the id instead of a random shuffle?

A random shuffle assigns cases anew each time you add data, so old test cases may move into dev (and get tuned on) and new ones into test. A hash of the id gives every case a fixed home, so the split stays stable as the dataset grows.
:::

:::quiz
Why must a test set include unanswerable questions?

Without them the system is never tested on saying "I do not know". It can hallucinate on every question the documents cannot answer and the score will not show it. Unanswerable cases measure refusals and tune the score floor.
:::

:::quiz
What is the main risk of using only synthetic test cases?

They are cleaner and more uniform than real user questions, and the model that writes them is often similar to the model that answers, so scores look better than reality. Use synthetic data to widen coverage, review it, tag it and report it separately from real cases.
:::

## 📚 Keep learning

- [Anthropic docs: Create strong empirical evaluations](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- [Hamel Husain: A field guide to rapidly improving AI products](https://hamel.dev/blog/posts/field-guide/)
- [Google: Rules of Machine Learning (data and evaluation rules)](https://developers.google.com/machine-learning/guides/rules-of-ml)

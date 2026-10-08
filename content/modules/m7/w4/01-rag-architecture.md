---
title: "RAG Architecture"
summary: "Understand RAG end to end: why not fine-tuning or a giant prompt, the two pipelines, a grounded prompt with a token budget, an honest 'I do not know' path, and the cost, speed and security points of the design."
type: lesson
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: core, ops: optional }
durationMinutes: 180
tags: [rag, retrieval, grounding, architecture, llm]
lastReviewed: 2026-10
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What **RAG** is and when it beats fine-tuning or a very long prompt
- The **components** and the flow of one request
- How to **assemble a grounded prompt**, with a token budget
- Why you need a **"no answer" path**, and how to build it
- **Cost, latency and security** points of a RAG system
- The common **variants**: naive, with rewriting, hybrid, agentic

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **RAG** | Find relevant text first, then let the model answer using it | Retrieval-Augmented Generation |
| **Retriever** | The part that finds relevant chunks | Pencari |
| **Generator** | The language model that writes the answer | Penghasil jawaban |
| **Grounding** | Making the answer rest on given sources, not on memory | Berpijak pada sumber |
| **Context** | The text you put in the prompt for the model to use | Konteks |
| **Knowledge cutoff** | The date after which the model has seen nothing | Batas pengetahuan |
| **Refusal path** | The answer when the sources do not contain the answer | Jalur "tidak tahu" |
| **Agentic RAG** | The model decides when and what to search, using a tool | RAG berbasis agen |

## 🧠 The big idea

RAG is an **open-book exam**. A plain model takes the exam from memory: it may remember well, may remember wrongly, and knows nothing newer than its studies. With RAG you let the student bring the **right pages** of the textbook into the room. The student still has to read well, but now the answer is on the desk, and can even say "see page 12".

Two rules make the open-book exam fair: the **right pages must be on the desk** (retrieval), and the student must **answer from them**, not from imagination, and say "it is not in these pages" when it is not (grounding).

## ❓ Why it matters

Models have three limits that RAG fixes:

1. **They do not know your private data**: your help articles, contracts, product catalogue, tickets.
2. **They go out of date**: anything after the training cutoff, and anything you changed yesterday.
3. **They invent**: when unsure they still write a fluent answer.

RAG brings in the **right private, fresh facts** at question time, lets you show **sources**, and lets you update knowledge by **changing documents** instead of retraining a model. That is why most company AI assistants are RAG systems.

## 📖 Step by step

### 1. RAG, fine-tuning, or a very long prompt?

| Approach | Good for | Weak at |
|---|---|---|
| **RAG** | changing facts, private documents, citations, big collections | tasks that need to read everything at once; needs a good retriever |
| **Long prompt** (paste it all) | a few documents that fit in the window; prototypes | cost and speed on every call; the "needle" can get lost; no access control |
| **Fine-tuning** | style, format, a specialised skill or vocabulary | adding facts reliably (it forgets and hallucinates); updates are slow and costly |
| **Tools / APIs** | live, exact data (order status, stock) | open-ended questions over text |

A good rule: **facts → RAG or tools; behaviour and style → prompt, then fine-tuning if really needed.** Many systems combine RAG with tools.

### 2. The two pipelines

```text
INDEX (offline, repeatable)
  documents → clean → chunk → embed → store (vectors + text + metadata)

ANSWER (online, per question)
  question → [rewrite] → retrieve (vector + keyword, with filters) → [re-rank] → select chunks within a budget
           → build prompt (rules + numbered sources + question) → model → answer + citations → [check]
```

Treat them as separate parts you can test alone: the **retriever** (does it find the right chunks?) and the **generator** (given the right chunks, does it answer correctly?). Weeks 3 and 5 cover measuring each.

### 3. Build the prompt

The prompt has three parts: rules, sources, question.

```python
def build_prompt(question, chunks, max_context_tokens):
    used, total = [], 0
    for chunk in chunks:
        cost = estimate_tokens(chunk["text"])
        if total + cost > max_context_tokens:
            break                                           # stop at the first chunk that does not fit
        used.append(chunk)
        total += cost
    blocks = [f"[{i}] ({c['source']})\n{c['text']}" for i, c in enumerate(used, start=1)]
    sources = "<sources>\n" + ("\n\n".join(blocks) + "\n" if blocks else "") + "</sources>"
    prompt = (
        "Answer the question using ONLY the sources below. Cite them like [1], [2].\n"
        "If the sources do not contain the answer, say you do not know.\n\n"
        f"{sources}\n\n"
        f"Question: {question}"
    )
    return prompt, used
```

Why this shape:

- **"ONLY the sources"** and **"say you do not know"** set the grounding rule.
- **Numbered sources with their origin** make citations possible (lesson 4).
- **Tags** separate the data from the instructions (week 2). The documents are *untrusted text*: they can contain instructions too ("ignore all rules"), so the prompt treats them as data.
- A **token budget** keeps the call inside the window and under your cost target. Decide how many tokens of context you allow, not only how many chunks.
- Keep the **stable parts first** (rules), and the **changing parts last** (sources, question), which also helps prompt caching.

### 4. The "no answer" path

A RAG system that always answers will sometimes answer from nothing. Build in honesty:

```python
NO_ANSWER = "I could not find this in the documents I have."

def answer(question, retriever, llm, *, k=5, min_score=0.0, max_context_tokens=1000):
    chunks = [c for c in retriever(question, k) if c["score"] >= min_score]
    if chunks:
        prompt, used = build_prompt(question, chunks, max_context_tokens)
        if used:
            text = llm(prompt)
            return {
                "answer": text,
                "sources": [{"n": i, "id": c["id"], "source": c["source"]} for i, c in enumerate(used, start=1)],
                "used_llm": True,
            }
    return {"answer": NO_ANSWER, "sources": [], "used_llm": False}
```

What this does for you:

- If retrieval finds **nothing good**, the model is **not called**. That is cheaper, faster and safer than letting it improvise.
- The **sources you report** are exactly the chunks that went into the prompt, never more.
- A **minimum score** is a tunable guard (choose it from real examples). Make "no answer" a normal, tested outcome and give users a next step ("contact support", "ask differently").

### 5. Where the time and money go

| Step | Cost / time | Ways to improve |
|---|---|---|
| Embedding the question | tiny | cache identical questions |
| Vector + keyword search | milliseconds to tens of ms | indexes, filters, limit candidates |
| Re-ranking | tens to hundreds of ms | re-rank only the top 20–50 |
| **Model call with the context** | **biggest part**: input tokens × price, plus the wait for the first token | fewer, better chunks; prompt caching for the stable prefix; a smaller model for easy questions; stream the answer |
| Checks (citations, safety) | small | run them in code, not with another model |

Stream the answer so users see words in about a second. Log each step's time, and the tokens used.

### 6. Security and permissions

- **Permission filtering belongs in retrieval.** A user must only get chunks they are allowed to read. Put tenant/role in the search filter; never rely on the prompt to hide what was retrieved.
- **Documents are untrusted.** A web page, a PDF, or a user upload may contain hidden instructions (indirect prompt injection). Mark them as data, give the model **no powerful tools** in the same step, and check the output (week 2).
- **Privacy.** Whatever you retrieve is sent to the model provider. Redact what the model does not need; check the provider's data terms.
- **Source quality.** Old, draft or contradictory documents produce bad answers. Index only approved content, keep dates, and prefer fresh sources.

### 7. Variants you will meet

| Variant | What it adds | When |
|---|---|---|
| **Naive RAG** | embed → top-k → prompt | a first version; good for demos |
| **+ query rewriting** | a model turns a chatty question into a good search query (using the chat history) | multi-turn chat ("what about the red one?") |
| **+ hybrid search + re-ranking** | keyword + vector, then a re-ranker | real products with codes and names |
| **+ citations and checks** | numbered sources, validation | any user-facing answer |
| **Agentic RAG** | the model gets a `search` tool and decides whether, when and how often to search, and can try again | hard, multi-step questions (week 6) |
| **Multi-hop / graph RAG** | follows links between documents or entities | questions that join facts from several places |

Start with naive RAG **plus a test set**. Add one improvement at a time, and keep it only if the numbers go up.

### 8. A minimal checklist for a first RAG version

1. A small corpus of approved documents and a **test set** of 30+ real questions (some unanswerable).
2. Indexing job: chunk, embed, store with metadata.
3. Retrieval with filters, top-k, and a score floor.
4. The prompt with numbered sources, a grounding rule and a "do not know" rule.
5. The "no answer" path that skips the model.
6. Citations shown, and validated in code.
7. Logs: question, retrieved ids and scores, prompt ids, answer, tokens, time.
8. An evaluation script you can run after every change.

### Choosing your setup

| Situation | Do this |
|---|---|
| Knowledge changes or is private | RAG |
| Only a few short documents | paste into the prompt first; add RAG when it grows |
| Live data (orders, stock) | a tool call, not RAG |
| Chatty multi-turn questions | add query rewriting |
| Codes, names, jargon | hybrid search |
| Users must trust the answer | citations + validation + refusal path |
| Several customers' data | permission filter in the search |

- ✅ Test retrieval and generation separately.
- ✅ Make "I do not know" a first-class result.
- 🚫 Letting the model answer when retrieval found nothing.
- 🚫 Filtering permissions in the prompt.

## ⚠️ Common mistakes

- Treating RAG as "add a vector database" and skipping evaluation.
- Always answering, even with an empty or irrelevant context.
- Reporting sources that were not in the prompt.
- Stuffing 30 chunks in the prompt "to be safe" (cost up, quality often down).
- Indexing drafts, duplicates and outdated pages.
- Using the same prompt for retrieval-heavy and chatty questions.
- Forgetting that retrieved text can carry prompt injection.
- No logs of what was retrieved, so failures cannot be diagnosed.

:::revoshop
Sketch a RAG assistant for RevoShop's help center and return policy. List the documents you would index, the metadata, what must be a tool instead (order status), the "no answer" message, and the permission rule if sellers and buyers see different documents.
:::

## 🏆 Best practices

- [ ] Separate and test the retriever and the generator.
- [ ] Number the sources, label their origin, and state the grounding rule in the prompt.
- [ ] Budget the context in tokens; keep only the best chunks.
- [ ] Skip the model call and answer "not found" when retrieval is empty or weak.
- [ ] Put permission and tenant filters in retrieval.
- [ ] Treat retrieved documents as untrusted data.
- [ ] Log retrieved ids, scores, prompt contents, tokens and timings.
- [ ] Evaluate on a fixed test set after every change.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain RAG with the open-book exam. What are the two rules that make it fair?

## 📐 Design it

SupportDesk AI must answer customer questions from 3,000 help articles and policies, for several client companies. Answers must cite sources, never reveal another company's documents, handle "I do not know", and respond within 3 seconds to the first word. Design the architecture: components, request flow, prompt, refusal path, security, and what you log.

:::quiz
Show a possible design

- **Components:** an indexing job (chunk, embed, store with `tenant_id`, language, status), a retrieval service (hybrid search with filters), a prompt builder, a model call, a citation validator, and a logging/evaluation layer.
- **Request flow:** authenticate the user and find the tenant → (optional) rewrite the question using the chat history → hybrid search with `tenant_id`, `status = published` and language filters, top 20 → re-rank to top 5 → drop chunks below a score floor → build the prompt within a token budget → stream the model answer → validate citations and quotes → return text + sources.
- **Prompt:** rules (answer only from sources, cite as [n], say you do not know, reply in the customer's language), the numbered `<sources>` block, and the question; stable rules first for caching.
- **Refusal path:** if nothing passes the score floor, skip the model and return the standard message with a next step ("talk to an agent"); if the model says it does not know, treat it as a valid answer and offer handoff.
- **Security:** tenant and permission filters in SQL for every retrieval; documents marked as data; no powerful tools in this step; output checks for leaked personal data; only approved articles indexed.
- **Latency (3 s to first word):** a small embedding call, indexed search in tens of ms, re-rank only 20 candidates, prompt caching on the rules, and **streaming** so the first word appears while the rest is written.
- **Logging:** question, rewritten query, retrieved ids and scores, prompt ids, answer, citations validity, tokens, timings, and the tenant. Used for debugging and for building the test set.
- **Evaluation:** 200 labelled questions (including unanswerable ones) checked for retrieval recall and answer correctness separately, after every change.

**Rule shown:** RAG is a pipeline of small, testable parts around one model call; honesty and permissions are designed in, not added later.
:::

### 📝 Self-review checklist

- [ ] Retrieval and generation can be tested separately
- [ ] The prompt grounds the model and numbers the sources
- [ ] Empty or weak retrieval skips the model
- [ ] Permissions are enforced in retrieval
- [ ] Everything needed to debug a bad answer is logged

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m7/w4/01-rag-pipeline" ai="no-ai" title="The RAG pipeline"}
Write `estimate_tokens`, `build_prompt` (the exact layout, numbered sources, stop at the token budget) and `answer` (retrieve, drop low scores, skip the model when nothing is left, report exactly the sources that went into the prompt). The retriever and the model are fake functions, so no API key is needed.
:::

:::hints
- Add chunks in order while the running total of `estimate_tokens(text)` stays `<= max_context_tokens`; `break` at the first chunk that does not fit.
- Number sources with `enumerate(used, start=1)`.
- An empty sources block is exactly `"<sources>\n</sources>"`.
- In `answer`, filter by `score >= min_score` before building the prompt; if `used` is empty, return the no-answer result without calling `llm`.
:::

## ✅ Quick check

:::quiz
When should a RAG system not call the language model at all?

When retrieval returns nothing relevant: no chunks, all below the score floor, or none fitting the budget. Calling the model with no sources invites a made-up answer. Return a clear "not found" with a next step instead; it is cheaper, faster and honest.
:::

:::quiz
Why must permission checks be part of retrieval and not of the prompt?

The prompt is only text the model may ignore or be tricked about, and once a chunk is in the prompt the user could extract it. If retrieval filters by the user's rights, forbidden chunks never reach the model at all.
:::

:::quiz
Why keep the retriever and the generator testable separately?

When an answer is wrong you must know which part failed. If the right chunk was never retrieved, fix retrieval; if it was in the prompt and the answer was still wrong, fix the prompt or model. Measuring them together hides the cause.
:::

## 📚 Keep learning

- [Anthropic docs: Search and retrieval (RAG)](https://platform.claude.com/docs/en/build-with-claude/search-results)
- [Lewis et al.: Retrieval-Augmented Generation (original paper)](https://arxiv.org/abs/2005.11401)
- [Anthropic: Introducing Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval)

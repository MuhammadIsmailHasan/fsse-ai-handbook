---
title: "RAG System at Scale"
summary: Designing retrieval-augmented generation for real traffic — the ingest and query pipelines, chunking, embeddings and top-k vector search, reranking and citations, plus the caching, cost, and freshness problems that appear at scale.
type: lesson
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: core, ops: recommended }
durationMinutes: 140
tags: [architecture, system-design, rag, embeddings, vector-database, llm]
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What **RAG** is and why it beats stuffing everything into the prompt
- The two pipelines: **ingest** (offline) and **query** (online)
- **Chunking**, **embeddings**, and a **vector index** for top-k search
- **Reranking** and **citations** for better, trustworthy answers
- The scale problems: **caching**, **cost**, **latency**, and **freshness**
- How this powers CareerPilot / StudyMind features

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **RAG** | Fetch relevant text, then let the LLM answer using it | Ambil teks relevan lalu dijawab LLM |
| **Embedding** | A list of numbers capturing a text's meaning | Angka yang menangkap makna teks |
| **Chunk** | A small passage of a document | Potongan dokumen |
| **Vector database** | A store that finds nearest embeddings fast | DB pencari makna terdekat |
| **Top-k retrieval** | Get the k most relevant chunks | Ambil k potongan paling relevan |
| **Rerank** | Re-order candidates with a smarter model | Urutkan ulang kandidat |
| **Citation** | A link back to the source chunk | Rujukan ke sumber |
| **Freshness** | How up to date the indexed data is | Seberapa mutakhir data |

## 🧠 The big idea

An LLM is a **brilliant intern with no access to your files**. **RAG** is giving that intern a **smart librarian**: before answering, the librarian pulls the few most relevant pages (**retrieval**) and hands them over, so the intern answers from *your* documents — with page references (**citations**) — instead of guessing from memory.

Embeddings are how the librarian finds "pages about the same idea" even when the words differ: similar meaning → similar numbers → close together.

## ❓ Why it matters

You can't paste a whole knowledge base into a prompt — it's too big, too expensive, and models have context limits. RAG lets an LLM answer from a large, changing corpus by fetching only the relevant slices. It's the backbone of most real AI features (support bots, doc Q&A, StudyMind). Making it work on a demo is easy; making it fast, cheap, and *fresh* at scale is the real engineering.

## 📖 Step by step

### 1. Two pipelines

RAG has an **offline ingest** pipeline and an **online query** pipeline:

```
INGEST (offline):  documents → chunk → embed → store in vector index
QUERY  (online):   question → embed → top-k search → (rerank) → LLM + chunks → answer + citations
```

### 2. Ingest: chunk, then embed

Documents are split into **chunks** (a few hundred tokens each, often with a little **overlap** so ideas aren't cut mid-thought). Each chunk is turned into an **embedding** (a vector) by an embedding model and stored in a **vector database** alongside its text and source id.

Chunk size is a real trade-off: too big → the retrieved passage is noisy and costs more tokens; too small → it loses context. Overlap avoids losing a sentence that straddles a boundary.

### 3. Query: retrieve top-k

The user's question is embedded the same way, and the vector database returns the **top-k** most similar chunks (by cosine similarity). These are the passages most likely to contain the answer.

### 4. Rerank and cite

The top-k from vector search is fast but rough. An optional **reranker** (a smarter, slower model) re-orders the candidates so the best ones lead. Then you build the prompt: *"Answer using these passages; cite them,"* plus the chunks. The LLM answers and includes **citations** back to the source chunks, so users can verify — critical for trust.

### 5. The scale problems

A demo ignores these; production can't:

| Problem | Why it bites at scale | Fix |
|---|---|---|
| **Cost** | Embedding + LLM calls cost money per request | Cache embeddings; cache answers for repeat questions |
| **Latency** | Embed + search + rerank + LLM adds up | Parallelize, cap k, use a fast vector index, stream the answer |
| **Freshness** | Docs change; the index goes stale | Re-embed changed docs; a background ingest job |
| **Quality** | Wrong chunks → wrong answer | Better chunking, hybrid (keyword + vector) search, reranking |
| **Scale of index** | Millions of vectors | A managed/scalable vector DB with an approximate index (ANN) |

### 6. Caching, the biggest lever

Two caches save the most:
- **Embedding cache**: the same text always embeds to the same vector — cache it, don't pay to re-embed.
- **Answer cache**: identical (or near-identical) questions can return a stored answer instead of a fresh LLM call.

### Choosing your setup

| Situation | Do this |
|---|---|
| Small, static docs | Simple vector store, no rerank needed |
| Large, changing corpus | Background ingest + re-embedding for freshness |
| Latency-sensitive | Cap k, parallelize, stream, cache answers |
| Cost-sensitive | Cache embeddings and answers; smaller models where possible |
| Quality-sensitive | Hybrid search + reranking + citations |

- ✅ Separate offline ingest from online query; keep the index fresh with a background job.
- ✅ Cache embeddings and answers; they're the biggest cost/latency wins.
- ✅ Return citations so answers are verifiable.
- 🚫 Don't stuff the whole corpus into the prompt; don't skip freshness or caching at scale.

## ⚠️ Common mistakes

- Chunks too large (noisy, expensive) or too small (no context); no overlap.
- No freshness plan, so answers cite outdated documents forever.
- Re-embedding the same text every request instead of caching.
- Skipping citations, so users can't trust or verify answers.
- Relying on vector search alone when exact keywords matter (use hybrid search).

:::revoshop
RAG is more a CareerPilot/StudyMind topic than a RevoShop one, but the pattern maps: imagine a "RevoShop help assistant" over its FAQ and policies. (1) What would the ingest pipeline chunk and embed? (2) For a question like "what's the refund window?", how would top-k retrieval + citations produce a trustworthy answer? (3) When policies change, how do you keep the index fresh?
:::

## 🏆 Best practices

- [ ] Split ingest (offline) from query (online); run ingest as a background pipeline.
- [ ] Tune chunk size with overlap; measure retrieval quality, don't guess.
- [ ] Cache embeddings (same text → same vector) and cache answers for repeat questions.
- [ ] Add reranking and hybrid (keyword + vector) search when quality matters.
- [ ] Always return citations to source chunks.
- [ ] Keep the index fresh by re-embedding changed documents; monitor cost and latency.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain RAG with the brilliant-intern-plus-smart-librarian analogy. Then, in two sentences, say what an embedding is and why it lets the librarian find passages by *meaning* rather than exact words.

## 📐 Design it

Design StudyMind's Q&A over this handbook (hundreds of lessons that get edited over time). Cover the ingest pipeline, the query pipeline (retrieval → rerank → answer with citations), how you keep answers fresh when a lesson is edited, and two things you'd cache to control cost and latency.

:::quiz
Show a possible design

**Ingest (offline):** for each lesson, split into ~300-token chunks with small overlap, embed each chunk, and store `{chunk_text, embedding, lesson_id, heading}` in a vector database. Run this as a background job.

**Query (online):** embed the student's question → top-k (say k=8) similar chunks → **rerank** to the best 3–4 → prompt the LLM: "answer using these passages and cite the lesson/heading." Return the answer **with citations** so the student can jump to the source lesson.

**Freshness:** when a lesson is edited, re-embed only that lesson's chunks (keyed by `lesson_id`) and replace them in the index — so answers never cite stale content. A content hash detects which lessons changed.

**Caching (cost + latency):** (1) **embedding cache** — a chunk's text hashes to its vector, so unchanged chunks aren't re-embedded on every ingest; (2) **answer cache** — common questions ("what is idempotency?") return a stored answer instead of a fresh LLM call.

**Rule shown:** two pipelines, freshness by re-embedding changed docs, citations for trust, and embedding/answer caches to keep it fast and affordable.
:::

### 📝 Self-review checklist

- [ ] Ingest and query pipelines are separate; ingest runs in the background
- [ ] Chunking (size + overlap) and top-k/rerank are specified
- [ ] Freshness handled by re-embedding changed documents
- [ ] Citations returned; embedding + answer caching in place

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/architecture/i-system-design-practice/04-rag-retrieval" ai="no-ai" title="Chunking, cosine similarity, and top-k retrieval"}
Implement the retrieval core of RAG: split a token list into overlapping chunks, compute cosine similarity between two vectors, and return the top-k most similar documents to a query vector. The tests check overlap, a known similarity value, and correct ranking.
:::

:::hints
- `chunk_tokens(tokens, size, overlap)`: step by `size - overlap`; each window is `tokens[i:i+size]`; stop when you've covered the end. Require `0 <= overlap < size`.
- `cosine_similarity(a, b)` = `dot(a,b) / (norm(a) * norm(b))`; return `0.0` if either vector is all zeros.
- `top_k(query, corpus, k)`: score each `{"id","vector"}` by cosine to `query`, sort by score descending (stable), return the first k ids.
:::

## ✅ Quick check

:::quiz
Why does RAG split into an offline ingest pipeline and an online query pipeline?

Because embedding and indexing a whole corpus is slow and only needs to happen when documents change (offline), while a user's question must be answered quickly using the already-built index (online). Separating them keeps queries fast and lets you refresh the index in the background.
:::

:::quiz
At scale, what are the two most effective things to cache in a RAG system, and why?

Embeddings (the same text always produces the same vector, so caching avoids paying to re-embed) and answers (identical or near-identical questions can return a stored response instead of a fresh, costly LLM call). Both cut cost and latency the most.
:::

## 📚 Keep learning

- [What is RAG? (AWS)](https://aws.amazon.com/what-is/retrieval-augmented-generation/)
- [Pinecone: RAG and vector search learning center](https://www.pinecone.io/learn/retrieval-augmented-generation/)
- [OpenAI cookbook: question answering with embeddings](https://cookbook.openai.com/examples/question_answering_using_embeddings)

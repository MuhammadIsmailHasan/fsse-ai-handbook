---
title: "Semantic Search"
summary: "Build search that understands meaning: the index and query pipelines, chunk size and overlap, metadata and freshness, and how to measure quality with recall, precision and MRR instead of guessing."
type: lesson
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: core, ops: optional }
durationMinutes: 180
tags: [semantic-search, chunking, retrieval, evaluation, recall, mrr]
lastReviewed: 2026-10
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- The **two pipelines**: indexing documents, and answering a query
- How to **chunk** text, and the trade-offs of chunk size and overlap
- What **metadata** to store with each chunk
- How to keep the index **fresh** when documents change
- How to **measure** search quality: precision, recall, MRR
- How to find and fix **failures**

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Chunk** | A piece of a document that is indexed and found on its own | Potongan dokumen |
| **Overlap** | Words shared between neighbouring chunks, so an idea is not cut in half | Tumpang tindih |
| **Index pipeline** | Load → clean → chunk → embed → store | Alur pengindeksan |
| **Query pipeline** | Embed the question → search → return the best chunks | Alur kueri |
| **Top-k** | The k best results returned | k teratas |
| **Precision@k** | Of the first k results, how many are right | Ketepatan |
| **Recall@k** | Of all right results, how many are in the first k | Ketercapaian |
| **MRR** | Average of 1 / (position of the first right result) | Rata-rata peringkat terbalik |

## 🧠 The big idea

A semantic search system is a **good librarian with a good index card for every page**. When the library is built, the librarian reads each document, splits it into sensible pages, writes a card for each page (the embedding) and files it with details (title, language, date). When someone asks a question, the librarian writes a card for the question, finds the nearest page cards, and hands over the pages themselves.

Two things decide whether this works: **how the pages were cut** (a page that mixes five topics gets a muddy card), and **whether anyone checked** that the librarian really finds the right pages. Most teams under-invest in both.

## ❓ Why it matters

Search quality is the ceiling of every AI feature built on it. A support bot that answers from retrieved articles can only be as good as the articles it retrieves. If the right passage is not in the top results, the best model in the world cannot answer correctly. You will meet this again in RAG next week: **most "AI answered wrong" bugs are retrieval bugs**.

And "it looked fine when I tried three queries" is not evidence. You need a small test set and three numbers.

## 📖 Step by step

### 1. The two pipelines

```text
INDEX (once, then on every change)
  documents → clean → CHUNK → embed (batched) → store vector + text + metadata

QUERY (every request)
  question → embed (same model!) → nearest chunks (+ filters) → [re-rank] → top-k chunks → show / give to the model
```

Keep the two pipelines in separate, simple functions. The index pipeline is a batch job you can re-run. The query pipeline is fast and runs on every request.

### 2. Chunking: cut at ideas, not at random

An embedding of a whole 30-page PDF is a blur of all its topics. An embedding of one sentence has too little context. A good chunk is **about one idea**, usually 100–400 words.

A simple, useful splitter works on words, with overlap:

```python
def chunk_text(text, size, overlap=0):
    if size <= 0 or overlap < 0 or overlap >= size:
        raise ValueError("bad size/overlap")
    words = text.split()
    chunks = []
    step = size - overlap
    start = 0
    while start < len(words):
        chunks.append(" ".join(words[start : start + size]))
        if start + size >= len(words):
            break
        start += step
    return chunks
```

```text
10 words, size 4, overlap 1:
[w0 w1 w2 w3]
            [w3 w4 w5 w6]
                        [w6 w7 w8 w9]
```

Trade-offs:

| | Small chunks | Large chunks |
|---|---|---|
| Precision of the match | high (focused) | lower (mixed topics) |
| Context for the reader | little | more |
| Number of vectors / cost | more | fewer |
| Risk | the answer is split across chunks | the right sentence is buried |

Better than fixed sizes: **split on structure**. Cut at headings, paragraphs and list items first, and only then by size. Keep a heading as a prefix of its chunks ("Returns policy > Refunds > ..."), because it adds meaning. Do not cut code blocks or tables in the middle. Add 10–20% overlap so an idea at a boundary appears whole in at least one chunk.

There is no perfect size. Try 2–3 settings on your test set (below) and keep the one that scores best.

### 3. What to store with each chunk

```text
chunk_id, document_id, chunk_index
text                 (the exact text, so you can show it and give it to the model)
embedding            (the vector)
embedding_model      (name + version)
source               (URL or file, so you can cite it)
title, section       (for display and for context)
language, tenant_id, access_level, product, version   (for FILTERS)
updated_at, content_hash                              (for FRESHNESS)
```

Metadata is what turns a toy into a product: filter by language, by product, by customer, by "published"; show the source; know when something is out of date.

### 4. Keeping the index fresh

Documents change. If the index does not, users get old answers.

- Store a **`content_hash`** of each chunk's text. On re-index, compare hashes: re-embed only changed chunks.
- When a document is **deleted**, delete its chunks (use a foreign key with cascade or a periodic clean-up).
- When a document **changes size**, its chunk boundaries shift: simply replace all chunks of that document in one transaction.
- Run the index job on a **schedule** and on **change events** (a webhook, a queue message).
- When you **change the model or the chunking**, rebuild into a *new* index, test it, then switch (see the last two lessons).

### 5. The query pipeline

```python
def search(query, *, k=5, lang=None, tenant_id=None):
    query_vector = embedder.embed([query])[0]            # the SAME model as the index
    filters = {"tenant_id": tenant_id, **({"lang": lang} if lang else {})}
    candidates = store.search(query_vector, k=k * 4, where=filters)      # fetch more than you need
    results = [c for c in candidates if c.score >= MIN_SCORE][:k]         # optional floor
    return results
```

Useful tricks:

- **Fetch more, then narrow** (k × 4, then re-rank or filter down to k).
- A **minimum score** avoids showing junk when nothing relevant exists ("no result" is a valid answer). Choose it by looking at real good and bad matches, not by copying a number.
- **Query rewriting:** very short or chatty queries ("it doesn't work") search poorly. A language model can rewrite them into a clear search query, using the conversation so far.
- **Filters first:** language, tenant and permissions belong in the filter, never in the prompt.
- **Multilingual:** check a query in Indonesian against English documents and the other way round, if your users mix languages.

### 6. Measure it: the test set and three numbers

Build a test set from real questions: **20–100 queries**, each with the chunk or document ids that are the right answers. Ask your support team, read old tickets, write the hard ones yourself.

```python
def precision_at_k(ranked, relevant, k):
    return sum(1 for r in ranked[:k] if r in relevant) / k

def recall_at_k(ranked, relevant, k):
    if not relevant:
        return 1.0
    return len(set(ranked[:k]) & relevant) / len(relevant)

def reciprocal_rank(ranked, relevant):
    for position, item in enumerate(ranked, start=1):
        if item in relevant:
            return 1 / position
    return 0.0
```

| Metric | Question it answers | Typical use |
|---|---|---|
| **Recall@k** | Is the right answer anywhere in the top k? | RAG: the model can only use what you retrieved |
| **Precision@k** | How much of the top k is useful? | showing a result list to people |
| **MRR** | How high is the *first* right answer? | one-answer questions; the average of 1/rank |

```python
def evaluate(search_fn, cases, k=5):
    p = r = m = 0.0
    misses = []
    for case in cases:
        ranked = search_fn(case["query"])
        p += precision_at_k(ranked, case["relevant"], k)
        r += recall_at_k(ranked, case["relevant"], k)
        m += reciprocal_rank(ranked, case["relevant"])
        if not set(ranked[:k]) & case["relevant"]:
            misses.append(case["query"])
    n = len(cases)
    return {"precision@k": p / n, "recall@k": r / n, "mrr": m / n, "misses": misses}
```

The most valuable part is the list of **misses**: the queries that found nothing useful. Read them one by one.

### 7. Diagnose the misses

For each missed query, ask where it went wrong:

| Symptom | Likely cause | Fix |
|---|---|---|
| The answer is in the documents but not retrieved | chunk too big or too small; heading lost; a rare word or code | change chunking; add the title to each chunk; add keyword search (next lesson) |
| The right chunk ranks 6th–10th | embedding model is weak for your domain or language | try another model; add a re-ranker |
| Right result only for long queries | short queries are vague | query rewriting |
| Results from the wrong product, language or customer | missing filter | add metadata and filter |
| Old answer | stale index | content hash and scheduled re-index |
| Nothing relevant exists | the information is missing from the corpus | add content; return "no answer" |

Change **one thing at a time** and re-run the test set. Keep a table of results per experiment (chunk size 150 → recall@5 0.71; 300 → 0.78; with titles → 0.84). That table is your evidence and your documentation.

### 8. Optional: re-ranking

The first search is fast and rough. A **re-ranker** (a cross-encoder model or a provider's rerank service) reads the query together with each of the top 20–50 candidates and sorts them more carefully. It is slower and costs more, but often improves precision noticeably. Use it when recall@50 is high but precision@5 is low.

### Choosing your setup

| Situation | Do this |
|---|---|
| Starting out | paragraph/heading-based chunks of ~200 words, 10–20% overlap |
| Long structured documents | split by headings; prefix chunks with their heading path |
| Answers split across chunks | more overlap, or larger chunks, or retrieve neighbouring chunks too |
| Many tenants or languages | metadata + filters in the query |
| Documents change often | `content_hash` + scheduled and event-driven re-index |
| Short vague queries | query rewriting |
| Good recall@50, weak precision@5 | add a re-ranker |
| Exact ids and names matter | hybrid search (next lesson) |

- ✅ Build the test set before tuning anything.
- ✅ Change one thing at a time and keep a results table.
- 🚫 Judging quality by trying three queries.
- 🚫 Showing low-score junk instead of "no result".

## ⚠️ Common mistakes

- Chunking by a fixed number of characters and cutting sentences, tables or code in half.
- No metadata, so filters and citations are impossible later.
- Never re-indexing, or re-embedding everything on every run.
- Embedding queries with a different model or settings than the documents.
- A single global similarity threshold copied from a tutorial.
- Tuning without a test set ("it feels better").
- Looking only at the average score and ignoring the misses.
- Putting access control in the prompt instead of in the filter.

:::revoshop
Take ten product questions a RevoShop customer might ask and, for each, write the product ids that should be found. Chunk-wise: would you index one chunk per product, or one per description paragraph and review? Name the metadata you would store, and one query that you expect to be hard.
:::

## 🏆 Best practices

- [ ] Build a test set of real queries with known right answers before tuning.
- [ ] Report recall@k, precision@k and MRR, and read the misses.
- [ ] Chunk by structure, with a small overlap; keep the heading with the chunk.
- [ ] Store source, language, permissions, hash, model and timestamps as metadata.
- [ ] Apply permission and tenant filters in the search query.
- [ ] Keep the index fresh with content hashes and scheduled jobs.
- [ ] Change one variable per experiment and record the numbers.
- [ ] Return "no good result" when scores are low.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain semantic search with the librarian-and-index-cards picture. Why must you test with real questions and not just try a few?

## 📐 Design it

SupportDesk AI will search 3,000 help articles in Indonesian and English that the support team edits daily. Customers type short, messy questions ("barang blm sampe"). Design the chunking, the metadata, the freshness job, the query pipeline and the evaluation plan, including how you decide between two chunk sizes.

:::quiz
Show a possible design

- **Chunking:** split each article by headings, then by paragraphs into ~150–250-word chunks with ~20% overlap; prefix each chunk with `Article title > Section`; keep numbered steps and tables together.
- **Metadata:** `article_id`, `chunk_index`, `title`, `section`, `url`, `lang`, `product`, `status` (published/draft), `updated_at`, `content_hash`, `embedding_model`.
- **Embedding:** a multilingual model chosen by testing Indonesian and mixed queries; documents and queries share the model.
- **Freshness:** when an article is saved, an event enqueues a re-index job for that article; the job compares chunk hashes, re-embeds only changed chunks, replaces the rest in one transaction, and deletes chunks of unpublished articles. A nightly reconciliation catches missed events.
- **Query pipeline:** normalise the text (lowercase, expand "blm" → "belum" with a small slang list), optionally rewrite with a model using the conversation, embed, search with `status = 'published'` and the language filter, fetch top 20, re-rank to 5, drop results below a measured score, and show the source link.
- **Evaluation:** 150 real tickets turned into queries (many short and slangy), each with the correct article ids. Compute recall@5, precision@5 and MRR, and read all misses.
- **Choosing a chunk size:** run the same test set with 150, 250 and 400 words; compare recall@5 and MRR; pick the winner unless it costs much more or loses on the misses that matter most; re-check after any big content change.
- **Monitoring:** log queries with no result or low scores; use them as the next test cases.

**Rule shown:** structure the chunks, store useful metadata, keep the index fresh, and let a test set (not a feeling) pick the settings.
:::

### 📝 Self-review checklist

- [ ] Chunks follow the document's structure
- [ ] Metadata supports filters, citations and freshness
- [ ] There is a test set with recall, precision and MRR
- [ ] Misses are read and turned into fixes

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m7/w3/03-search-eval" ai="no-ai" title="Chunk it, then measure it"}
Write `chunk_text` (word-based chunks with overlap that stop when the end is reached), `precision_at_k`, `recall_at_k`, `reciprocal_rank` and `evaluate` (averages plus the list of queries that missed). No API key needed.
:::

:::hints
- `chunk_text`: validate `size > 0` and `0 <= overlap < size`; step = `size - overlap`; stop right after a chunk that includes the last word.
- `precision_at_k` divides by `k`, not by `len(ranked)`.
- `recall_at_k`: `len(set(ranked[:k]) & relevant) / len(relevant)`; empty `relevant` gives `1.0`.
- `reciprocal_rank`: `enumerate(ranked, start=1)`.
- `evaluate`: a "miss" means no relevant id in `ranked[:k]`; keep misses in case order.
:::

## ✅ Quick check

:::quiz
Why is recall@k the main number for a RAG system?

The language model can only use the passages you give it. If the right passage is not among the retrieved k, the model cannot answer correctly, however good it is. So the first question is whether the answer is in the top k at all.
:::

:::quiz
Why add overlap between chunks?

An idea can sit across a chunk boundary. Overlap repeats the last words of one chunk at the start of the next, so that the idea appears whole in at least one chunk and can be matched properly.
:::

:::quiz
You changed the chunk size and results "feel better". What is missing?

A measurement. Run the same test set before and after, compare recall@k, precision@k and MRR, and read the misses. Feelings are biased by the few queries you happened to try.
:::

## 📚 Keep learning

- [Anthropic docs: Embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)
- [Pinecone: Chunking strategies](https://www.pinecone.io/learn/chunking-strategies/)
- [MTEB: Massive Text Embedding Benchmark](https://huggingface.co/spaces/mteb/leaderboard)

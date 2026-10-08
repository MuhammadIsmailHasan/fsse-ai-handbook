---
title: "Hybrid Search"
summary: "Combine keyword search (BM25, PostgreSQL full-text) with vector search — why each one alone fails, how reciprocal rank fusion merges two rankings, how to do it in one SQL query, and how to prove that hybrid really beats each part."
type: lesson
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: core, ops: optional }
durationMinutes: 180
tags: [hybrid-search, bm25, full-text-search, rrf, reranking, retrieval]
lastReviewed: 2026-10
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Where **vector search fails** and where **keyword search fails**
- How **BM25** scores keyword matches
- **Fusing** two rankings: **reciprocal rank fusion (RRF)** and weighted scores
- Doing hybrid search **inside PostgreSQL**
- **Re-ranking** as an optional last step
- How to **prove** hybrid is better on your data

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Keyword search** | Finds documents that contain the query words | Pencarian kata kunci |
| **BM25** | The classic keyword scoring formula: rare words matter more, long texts are normalised | Rumus skor kata kunci |
| **Full-text search** | The search engine built into a database (PostgreSQL has one) | Pencarian teks penuh |
| **Hybrid search** | Keyword search and vector search together | Pencarian gabungan |
| **Fusion** | Merging two ranked lists into one | Penggabungan peringkat |
| **RRF** | Reciprocal rank fusion: add `1 / (60 + rank)` from each list | Fusi peringkat timbal-balik |
| **Re-ranker** | A model that reads query and candidate together and sorts again | Pengurut ulang |
| **Tokenizer** | Splits text into words (tokens) for matching | Pemecah kata |

## 🧠 The big idea

Imagine you ask two assistants to find a document.

- **Assistant K (keywords)** is a **fast reader with a perfect memory for exact words**. Ask for "A9731" and K finds it at once. Ask for "can't sign in", and K only looks for pages with those words; it misses "Resetting your password".
- **Assistant V (vectors)** is a **thoughtful reader who understands ideas**. V knows that "can't sign in" and "reset password" belong together. But ask for "A9731" and V shrugs: it is just a strange string.

Hybrid search asks **both**, then combines their lists. A page that both assistants like goes to the top. A page only one of them found still gets a chance.

## ❓ Why it matters

Real users type both kinds of queries, often in the same box:

- "refund policy for damaged goods" (meaning),
- "error E-4021" or "order A9731" or "iPhone 15 Pro" (exact),
- "ongkir ke Medan" (slang, names, mixed language).

Studies and practice both show that **hybrid retrieval usually beats pure vector search** on mixed real-world queries, especially with product codes, names, acronyms and domain words that an embedding model has not seen. In a RAG system a missing passage means a wrong answer, so retrieval quality is worth this extra step.

## 📖 Step by step

### 1. Keyword search: BM25 in plain words

BM25 gives each document a score for the query:

- A word counts more if it is **rare** in the collection (the word "refund" says more than "the").
- Seeing the word **more times** helps, but with **diminishing returns** (the 10th "refund" adds little).
- A **long** document is not rewarded just for being long (length normalisation).

```python
import math, re

def tokenize(text):
    return re.findall(r"[a-z0-9]+", text.lower())

def bm25_scores(query, docs, k1=1.5, b=0.75):
    if not docs:
        return []
    tokenized = [tokenize(d) for d in docs]
    n_docs = len(docs)
    avgdl = (sum(len(t) for t in tokenized) / n_docs) or 1
    scores = [0.0] * n_docs
    for term in set(tokenize(query)):                     # each query word counted once
        n_t = sum(1 for t in tokenized if term in t)      # in how many documents does it appear?
        if n_t == 0:
            continue
        idf = math.log(1 + (n_docs - n_t + 0.5) / (n_t + 0.5))
        for i, tokens in enumerate(tokenized):
            tf = tokens.count(term)
            if tf:
                scores[i] += idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * len(tokens) / avgdl))
    return scores
```

Settings: `k1` controls how fast repeated words stop helping; `b` controls length normalisation. The defaults are fine to start.

Keyword search is **great** at: ids, codes, names, error numbers, rare technical words. It is **bad** at: synonyms, other languages, typos, and different wording of the same idea.

### 2. Vector search: the opposite strengths

From the last lessons: vector search is good at meaning and weak at exact strings, numbers and negation. So the two kinds of mistakes are different, and that is exactly why combining them works.

### 3. Fusing two rankings

You have two ranked lists. How do you merge them? The scores are on **different scales** (BM25 might be 0 to 15, cosine similarity 0 to 1), so you cannot just add them.

**Reciprocal rank fusion (RRF)** ignores the scores and uses only the **ranks**:

```python
def reciprocal_rank_fusion(rankings, k=60):
    fused = {}
    for ranking in rankings:
        for position, item in enumerate(ranking, start=1):
            fused[item] = fused.get(item, 0.0) + 1 / (k + position)
    return sorted(fused.items(), key=lambda pair: (-pair[1], pair[0]))
```

```text
vector ranking :  pw   login  refund  ord          (missed the order code)
keyword ranking:  ord                              (found "A9731" exactly)
fused          :  ord  pw     login ...            ← both strengths
```

Each list gives a document `1 / (60 + rank)`. A document at rank 1 in both lists gets about `2/61`; one at rank 1 in a single list gets `1/61`. Documents that **several lists agree on** rise. The constant 60 is a common default that smooths the difference between ranks 1, 2, 3.

RRF is popular because it needs **no tuning and no score scaling**, and it works even when one list has scores from a different system.

**Weighted score fusion** is the alternative: scale each score to 0..1 and mix them.

```python
def min_max(scores):
    if not scores:
        return {}
    low, high = min(scores.values()), max(scores.values())
    if high == low:
        return {k: 1.0 for k in scores}
    return {k: (v - low) / (high - low) for k, v in scores.items()}

def weighted_fusion(a, b, alpha=0.5):
    sa, sb = min_max(a), min_max(b)
    fused = {i: alpha * sa.get(i, 0.0) + (1 - alpha) * sb.get(i, 0.0) for i in set(sa) | set(sb)}
    return sorted(fused.items(), key=lambda pair: (-pair[1], pair[0]))
```

It lets you say "trust vectors 70%, keywords 30%" (`alpha`), but you must tune `alpha` on a test set, and min-max scaling can be thrown off by one outlier score. Start with RRF; try weighted fusion if you have a test set and a reason.

### 4. A complete small hybrid search

```python
def hybrid_search(query, docs, vector_ranking, top=3):
    ids = list(docs)
    scores = bm25_scores(query, [docs[i] for i in ids])
    keyword = sorted(((i, s) for i, s in zip(ids, scores) if s > 0), key=lambda pair: (-pair[1], pair[0]))
    fused = reciprocal_rank_fusion([[i for i, _ in keyword], vector_ranking])
    return [i for i, _ in fused[:top]]
```

Notice: documents with a keyword score of 0 are left out of the keyword list (they did not match at all), so a vector-only match is still found, and a keyword-only match still gets in.

### 5. Hybrid search inside PostgreSQL

PostgreSQL has built-in **full-text search**: store a `tsvector` of the text, index it with GIN, query with `websearch_to_tsquery`.

```sql
ALTER TABLE chunks
  ADD COLUMN tsv tsvector GENERATED ALWAYS AS (to_tsvector('simple', content)) STORED;
CREATE INDEX chunks_tsv_idx ON chunks USING gin (tsv);
```

The `'simple'` configuration splits on words and lower-cases them, with no language-specific stemming. It works for any language, including Indonesian and mixed text, and is predictable. (Language-specific configurations can help for English; test them on your data.)

One query that runs both searches and fuses them with RRF:

```sql
WITH semantic AS (
    SELECT id, row_number() OVER (ORDER BY embedding <=> $1) AS rank
    FROM chunks
    WHERE tenant_id = $3
    ORDER BY embedding <=> $1
    LIMIT 20
),
keyword AS (
    SELECT id, row_number() OVER (ORDER BY ts_rank_cd(tsv, q) DESC) AS rank
    FROM chunks, websearch_to_tsquery('simple', $2) AS q
    WHERE tenant_id = $3 AND tsv @@ q
    ORDER BY ts_rank_cd(tsv, q) DESC
    LIMIT 20
)
SELECT coalesce(s.id, k.id) AS id,
       coalesce(1.0 / (60 + s.rank), 0) + coalesce(1.0 / (60 + k.rank), 0) AS score
FROM semantic s
FULL OUTER JOIN keyword k ON s.id = k.id
ORDER BY score DESC
LIMIT 5;
```

Notes:

- `$1` is the query vector, `$2` the query text, `$3` the tenant. The **tenant filter is in both searches**.
- `ts_rank_cd` is PostgreSQL's ranking function; it is not exactly BM25 but plays the same role. If you want real BM25, use a search engine (OpenSearch, Elasticsearch) or an extension, and keep the same fusion idea.
- Each side fetches the top 20, so fusion has a good pool. The final answer is the top 5.

### 6. Optional: re-ranking

After fusion you have a short list (say 30). A **re-ranker** reads the query together with each candidate and scores how well they match. It is slower and costs more, so apply it only to the short list. Common reasons to add one: your first stage finds the right chunk but not at the top, or your queries are long and subtle. Measure the gain; skip it if the numbers do not justify the added latency and cost.

### 7. Prove it on your data

Never assume "hybrid is better". Use the test set from the last lesson and compare the same queries three ways:

| Mode | recall@5 | MRR |
|---|---|---|
| Vector only | measure | measure |
| Keyword only | measure | measure |
| Hybrid (RRF) | measure | measure |

Then read the queries where the modes **disagree**. You will usually see keyword search rescuing codes and names, and vector search rescuing paraphrases. If hybrid does not beat the best single mode on your data, something is off (a tokenizer, a filter, a tiny corpus), or you do not need it.

Add a few **adversarial queries** on purpose: an exact id, a typo, a synonym, a question in the other language, and a negation.

### Choosing your setup

| Situation | Do this |
|---|---|
| Users search with ids, names, codes, jargon | hybrid, or at least keyword + filters |
| Users ask natural-language questions only | vector alone may be enough; test hybrid anyway |
| Multilingual or slangy queries | `'simple'` full-text config + a multilingual embedding model |
| Want a quick fusion with no tuning | RRF with k = 60 |
| Want to control the balance | weighted fusion, tune `alpha` on a test set |
| First stage good at recall, bad at order | add a re-ranker on the top 20–50 |
| Corpus is huge and keyword quality matters | a search engine with real BM25 next to pgvector |

- ✅ Filters (tenant, permissions) go into **both** searches.
- ✅ Compare vector-only, keyword-only and hybrid on the same test set.
- 🚫 Adding raw BM25 and cosine scores together.
- 🚫 Assuming hybrid wins without measuring.

## ⚠️ Common mistakes

- Adding scores from different scales (BM25 + cosine) without scaling.
- Forgetting the tenant or permission filter in one of the two searches.
- Putting keyword-only matches (score 0 on the other side) at the bottom for ever, so they never reach the top.
- Using a language-specific full-text configuration that breaks Indonesian or mixed text.
- Tiny candidate pools (top 3 from each search), so fusion has nothing to work with.
- Adding a re-ranker without measuring its gain and latency.
- Tuning on three queries.

:::revoshop
List five kinds of RevoShop search queries (an SKU, a brand name, "sepatu murah untuk lari", an Indonesian typo, "not red"). For each, say whether vector search, keyword search or both would find it, and what fusion would do.
:::

## 🏆 Best practices

- [ ] Start with vector + keyword + RRF; measure against each part alone.
- [ ] Apply the same filters to both searches.
- [ ] Fetch a generous candidate pool (20–50) from each side before fusing.
- [ ] Use a predictable full-text configuration for your languages (`simple` is a safe start).
- [ ] Add adversarial queries (ids, typos, synonyms, other language, negation) to the test set.
- [ ] Add a re-ranker only when measurements justify its cost.
- [ ] Log queries with no good result and add them to the test set.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain hybrid search with the two assistants. Why does RRF not need scores to be on the same scale?

## 📐 Design it

CareerPilot search must find jobs by free text. Users type "backend python remote", "kerja data analyst jakarta", "JOB-48213", and "something with Go but not Java". Postings are Indonesian and English; there are 200,000 of them, and each user can also filter by city and salary. Design the search: indexing, query pipeline, fusion, filters, evaluation, and which queries you expect to stay hard.

:::quiz
Show a possible design

- **Indexing:** each posting gets a `tsvector` over title + company + skills + description (config `simple`), a GIN index, and an embedding of title + skills + trimmed description with a multilingual model. Filters (city, salary band, remote, posted date) are normal columns with B-tree indexes.
- **Query pipeline:** normalise the text; detect an id pattern (`JOB-\d+`) and answer it with a direct lookup first; run vector search and keyword search in parallel, each with the structured filters in SQL; take the top 30 from each; fuse with RRF; return the top 10. Optionally re-rank the top 30 with a re-ranker.
- **Filters:** "jakarta" can be a free-text word *and* a city filter. Extract known cities and salary words into filters (rules or a small model) and also leave the word in the keyword query.
- **"Go but not Java":** neither side understands negation well. Handle it with a rule that parses "not X" into an exclusion filter on skills, or let a model rewrite the query into text plus filters.
- **Evaluation:** 150 real queries with the right job ids, including ids, slang, English-Indonesian mixes and negations. Compare vector-only, keyword-only and hybrid on recall@10 and MRR; read the disagreements.
- **Expected hard cases:** negation, very short queries ("data"), salary comparisons ("above 15 juta"), and ambiguous words ("Go" the language vs the verb). Mitigate with query rewriting, filters and clear UI.
- **Operations:** monitor zero-result queries; re-index on posting changes; keep the embedding model name in the table.

**Rule shown:** each retrieval method covers the other's weakness, structured filters and rules cover what neither understands, and a test set tells you which combination to ship.
:::

### 📝 Self-review checklist

- [ ] Both searches apply the same filters
- [ ] Fusion needs no score scaling (RRF) or is tuned (weighted)
- [ ] Exact ids have a direct path
- [ ] Vector-only, keyword-only and hybrid were compared

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m7/w3/04-hybrid-search" ai="no-ai" title="BM25 and fusion"}
Write `tokenize`, `bm25_scores` (the formula above), `reciprocal_rank_fusion`, `min_max`, `weighted_fusion` and `hybrid_search`. The tests include an exact-id query that a pretend vector search misses, and a synonym query that keyword search misses. No API key needed.
:::

:::hints
- `idf = math.log(1 + (N - n_t + 0.5) / (n_t + 0.5))`; skip query terms that appear in no document.
- Count each distinct query term once: loop over `set(tokenize(query))`.
- `reciprocal_rank_fusion`: `1 / (k + position)` with positions starting at 1; sort by `(-score, id)`.
- `min_max`: if all values are equal return `1.0` for each.
- `hybrid_search`: drop BM25-zero documents, then fuse `[keyword_ids, vector_ranking]`.
:::

## ✅ Quick check

:::quiz
Why can't you just add a BM25 score and a cosine similarity?

They are on different scales (BM25 is unbounded and depends on the corpus; cosine is between −1 and 1), so one would dominate. Use rank-based fusion (RRF), or scale each score first (for example min-max) and mix them with a weight.
:::

:::quiz
A user searches "order A9731" and vector search ranks the order page 9th. What does hybrid search do?

Keyword search finds the exact token A9731 and ranks that page 1st. In the fused ranking the page gets a high reciprocal-rank contribution from the keyword list and a small one from the vector list, so it moves to the top.
:::

:::quiz
Why should the tenant filter be in both the vector search and the keyword search?

Each search returns its own candidate list. If one of them is unfiltered, it can pull another tenant's chunks into the fused result. Access rules must apply to every retrieval path.
:::

## 📚 Keep learning

- [PostgreSQL: Full text search](https://www.postgresql.org/docs/current/textsearch.html)
- [Elastic: A Comprehensive Guide to BM25](https://www.elastic.co/blog/practical-bm25-part-2-the-bm25-algorithm-and-its-variables)
- [Cormack et al.: Reciprocal Rank Fusion (paper)](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)

---
title: "Embeddings Explained Simply"
summary: "Understand how text becomes numbers that capture meaning — vectors, similarity (cosine, dot, distance), how to get embeddings, what they cannot do, and the habits (same model, batching, versioning) that keep a search system healthy."
type: lesson
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: core, ops: optional }
durationMinutes: 150
tags: [embeddings, vectors, similarity, cosine, semantic-search]
lastReviewed: 2026-10
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What an **embedding** is, in plain words
- How **similarity** between two embeddings is measured (cosine, dot product, distance)
- How to **get** embeddings and what to watch for (model, dimension, batching, cost)
- What embeddings are **good at** and what they are **bad at**
- The habits that keep an embedding system **consistent**

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Embedding** | A list of numbers that stands for the meaning of a text (or image) | Representasi angka |
| **Vector** | The list of numbers; a point or an arrow in space | Vektor |
| **Dimension** | How many numbers are in the vector (for example 768 or 1536) | Dimensi |
| **Cosine similarity** | How much two vectors point the same way (−1 to 1) | Kemiripan kosinus |
| **Dot product** | Multiply matching numbers and add them up | Hasil kali titik |
| **Euclidean distance** | The straight-line distance between two points | Jarak Euclid |
| **Nearest neighbours** | The stored vectors closest to a query vector | Tetangga terdekat |
| **Embedding model** | The model that turns text into a vector | Model embedding |

## 🧠 The big idea

Imagine a **giant map of meaning**. Every sentence is a pin on the map. "How do I reset my password?" and "I forgot my login" are pins that sit **right next to each other**. "Delivery to Surabaya takes three days" is a pin far away, in another neighbourhood.

An embedding model is the **map-maker**: it takes any text and tells you its coordinates. The coordinates are not two numbers like on a paper map. They are hundreds or thousands of numbers, because meaning has many directions (topic, tone, language, formality, ...). But the idea is the same: **close on the map = similar in meaning**.

So "find texts that mean something similar" becomes "find the pins nearest to this pin": simple maths.

## ❓ Why it matters

Keyword search only matches **words**. A customer who types "can't sign in" will not match an article titled "Resetting your password". Embeddings let a search system match **meaning**, even across different words, and often across languages.

That powers:

- **semantic search** (this week),
- **RAG**: finding the right passages to give the model (next week),
- **recommendations** and "similar items",
- **deduplication** and **clustering** (group similar support tickets),
- **classification** with few examples (is this message about billing or shipping?).

And it is cheap: an embedding call costs a tiny fraction of a chat call, and you do most of it once, when you index your documents.

## 📖 Step by step

### 1. From text to a vector

An embedding model returns a fixed-length list of numbers for any input text.

```python
vector = embed("How do I reset my password?")
len(vector)      # for example 1024: the model's dimension, always the same
vector[:3]       # [0.021, -0.113, 0.067]  (small numbers, usually between -1 and 1)
```

You cannot read the numbers. No single number means "password". Only the **relationships** between vectors are useful.

For learning and tests you can build a **toy embedder** with no model, by hashing words into buckets:

```python
import hashlib, re

def hash_embed(text, dim=64):
    vector = [0.0] * dim
    for token in re.findall(r"[a-z0-9]+", text.lower()):
        h = int(hashlib.sha256(token.encode()).hexdigest(), 16)
        vector[h % dim] += 1.0 if (h >> 20) & 1 else -1.0
    return normalize(vector)
```

It only knows **shared words**. A real model knows that "sign in" and "log on" are close. But the toy shows the whole pipeline (store, compare, rank) and runs offline.

### 2. Measuring "close": cosine, dot product, distance

Three ways to compare two vectors `a` and `b`:

```python
import math

def dot(a, b):
    return sum(x * y for x, y in zip(a, b))

def norm(v):
    return math.sqrt(sum(x * x for x in v))

def cosine(a, b):
    na, nb = norm(a), norm(b)
    return 0.0 if na == 0 or nb == 0 else dot(a, b) / (na * nb)

def euclidean(a, b):
    return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))
```

| Measure | Reads as | Notes |
|---|---|---|
| **Cosine similarity** | the angle between the arrows. 1 = same direction, 0 = unrelated, −1 = opposite | ignores length; the usual choice for text |
| **Dot product** | angle **and** length together | bigger vectors win; fine if vectors are normalised |
| **Euclidean distance** | the straight-line gap | smaller = closer |

If you **normalise** every vector to length 1 first, cosine similarity and dot product give the **same ranking**, and the dot product is faster. Many embedding models already return normalised vectors; check the documentation of yours.

```python
cosine([1, 2], [2, 4])      # 1.0   same direction, different length
cosine([1, 0], [0, 1])      # 0.0   unrelated
cosine([1, 0], [-1, 0])     # -1.0  opposite
```

Practical note: scores are only meaningful **within one model**. A cosine of 0.8 from model A is not comparable to 0.8 from model B, and there is no universal "good" threshold. Find yours by looking at real examples.

### 3. Nearest neighbours

To search: embed the query, compare it with every stored vector, and return the best few.

```python
def top_k(query, items, k, metric="cosine"):
    score = {"cosine": lambda v: cosine(query, v),
             "dot": lambda v: dot(query, v),
             "euclidean": lambda v: -euclidean(query, v)}[metric]
    scored = [(item_id, score(vector)) for item_id, vector in items]
    scored.sort(key=lambda pair: (-pair[1], pair[0]))      # higher is better; ties by id
    return scored[:k]
```

With a few thousand items this brute-force loop is fine. With millions you need an **index** that checks only promising vectors (next lesson).

### 4. Getting embeddings in real projects

| Source | Notes |
|---|---|
| **A provider's embedding API** | send text, get vectors. Some LLM companies do not make their own embedding model and recommend a partner; others offer one. Compare quality, languages, dimension and price. |
| **An open model you run yourself** | for example through sentence-transformers or Ollama. Free per call, data stays with you, needs hardware. |

Whichever you pick, write a tiny wrapper so the rest of your code does not care:

```python
class Embedder:
    model = "some-embedding-model-v2"       # keep the exact name: you will store it
    dim = 1024

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one vector per text, in the same order."""
        ...
```

Things to check when you choose a model:

- **Languages.** Does it work well for Indonesian, and for mixed Indonesian-English text? Test with your own examples.
- **Dimension.** More dimensions can mean better quality but more storage and slower search. Some models let you shorten the vector.
- **Maximum input length.** Longer text is cut off or rejected, which is one reason we chunk.
- **Query vs document.** Some models want a different prefix or setting for a *query* than for a *document*. Read the docs.
- **Price and rate limits.**

### 5. Good habits

- **One model for both sides.** Documents and queries must be embedded by the **same model** (same version). Vectors from different models live on different maps and cannot be compared.
- **Store the model name** (and version) next to each vector. When you change models, you must **re-embed everything**; the stored name tells you what is stale.
- **Batch** your calls (many texts per request) when indexing. It is faster and cheaper per text. Respect rate limits and retry on errors.
- **Embed once, reuse.** Cache embeddings by a hash of the text, so unchanged text is never paid for twice.
- **Clean the text** a little: remove menus, repeated headers, boilerplate that would make every chunk look alike.
- **Keep the dimension in the schema** (`vector(1024)`), so a wrong-size vector fails loudly.
- **Mind privacy.** Text you embed through an API is sent to the provider. Embeddings can leak parts of the text they came from, so protect them like the text itself.

### 6. What embeddings are good at, and what they are not

| Good at | Weak at |
|---|---|
| similar meaning with different words | exact things: ids, codes, names, numbers (`A9731`) |
| finding related passages across a big pile | **negation**: "can refund" and "cannot refund" are very close |
| working across languages (with a multilingual model) | precise logic and comparisons ("under 100,000") |
| grouping and recommending | very short or very vague queries |
| | freshness: they know nothing that you have not indexed |

That second column is why real systems combine embeddings with keyword search and filters (lesson 4) and let the language model read the retrieved text before answering (next week).

### Choosing your setup

| Need | Do this |
|---|---|
| Match meaning, not only words | embeddings + cosine similarity |
| A few thousand items | brute-force search in memory is enough |
| Millions of items | a vector index (next lesson) |
| Exact ids, names, codes | add keyword search (lesson 4) |
| Private or offline data | an open model that you run yourself |
| Changing the embedding model | re-embed everything; keep the model name stored |
| Choosing a threshold | look at real pairs from your data; do not copy a number from a blog |

- ✅ Same model for documents and queries; store the model name.
- ✅ Test on your own language and your own documents.
- 🚫 Comparing vectors from different models.
- 🚫 Trusting a high similarity to mean "this is the right answer".

## ⚠️ Common mistakes

- Embedding the query with one model and the documents with another.
- Forgetting to normalise (or not knowing whether the model already does).
- Using one fixed similarity threshold for all queries and models.
- Embedding a whole 40-page document as one vector.
- Expecting embeddings to handle "not", numbers or exact codes.
- Re-embedding unchanged text on every deploy.
- Not storing which model made which vector.

:::revoshop
Pick ten real RevoShop product names or descriptions. For three pairs, predict whether a good embedding model would put them close (for example "sepatu lari pria" and "men's running shoes") or far apart, and say what keyword search would do with the same pairs. Where would an exact product code break a pure embedding search?
:::

## 🏆 Best practices

- [ ] Use one embedding model per index, for documents and queries, and store its name.
- [ ] Evaluate models on your own text and languages before choosing.
- [ ] Normalise vectors (or know that the model does) and pick one metric.
- [ ] Batch and cache embedding calls; keep a hash of the text.
- [ ] Treat similarity scores as relative within one model; tune thresholds with real examples.
- [ ] Plan for re-embedding when the model or the chunking changes.
- [ ] Combine with keyword search and filters for exact terms.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain embeddings with the map-of-meaning picture. Why can you not compare a vector from model A with a vector from model B?

## 📐 Design it

CareerPilot wants a "similar jobs" feature: for a job the user saved, show five similar job postings from a database of 200,000 postings in Indonesian and English. Design the data you store, how and when you embed, how you search, how you check quality, and what you do when you change the embedding model next year.

:::quiz
Show a possible design

- **What to embed:** a short, cleaned text per posting: title + company + the main skills + a trimmed description (not the whole page of boilerplate). Keep a hash of that text.
- **Model:** a multilingual embedding model, chosen by testing 30 real pairs (Indonesian-Indonesian, English-English, Indonesian-English) and checking quality, dimension and price.
- **Storage:** a table with `job_id`, the text hash, the vector, `embedding_model`, `embedded_at`, and metadata (language, location, seniority, posted date).
- **When:** embed new postings in batches by a background job; re-embed only when the hash changes; cache by hash.
- **Search:** embed the saved job (or reuse its stored vector), take the nearest neighbours with an index, **filter** by recency and location, remove the job itself and near-duplicates, and return five.
- **Quality:** a small set of jobs with hand-picked "good matches"; measure recall@5; look at the misses; collect user clicks later.
- **Hybrid:** combine with a keyword match on exact skills or titles when users search with specific terms.
- **Model change next year:** add the new model's vectors in a **new column or table** (`embedding_model` differs), build a new index in the background, compare quality on the same test set, switch traffic, then drop the old one. Never mix models in one index.
- **Privacy:** job postings are public; user notes are not, so embed those only with an approved provider or a local model.

**Rule shown:** embeddings are cheap to create and expensive to change, so version them from day one.
:::

### 📝 Self-review checklist

- [ ] Documents and queries use the same model
- [ ] The model name is stored with each vector
- [ ] Quality is measured on real, local-language examples
- [ ] A plan exists for changing the model

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m7/w3/01-embedding-basics" ai="no-ai" title="Vectors, similarity and nearest neighbours"}
Write `dot`, `norm`, `normalize`, `cosine`, `euclidean`, a deterministic `hash_embed` (hashing words into buckets) and `top_k` with three metrics (higher score is always better; ties by id). No API key or model is needed.
:::

:::hints
- `cosine = dot / (norm_a * norm_b)`; return `0.0` when either norm is 0; raise `ValueError("dimension mismatch")` for different lengths.
- `hash_embed`: `re.findall(r"[a-z0-9]+", text.lower())`; use `hashlib.sha256(token.encode())`, **not** Python's `hash()`.
- Index is `h % dim`; sign is `+1` if `(h >> 20) & 1` else `-1`; return `normalize(vector)`.
- `top_k`: for "euclidean" use `-distance` as the score, then sort by `(-score, id)`.
:::

## ✅ Quick check

:::quiz
Why does cosine similarity ignore the length of the vectors, and why is that useful?

Cosine measures only the angle between the vectors, so a vector and a scaled copy of it are "the same". For text this is useful because the direction carries the meaning, while length can vary for unrelated reasons.
:::

:::quiz
You switch to a newer embedding model but keep the old stored vectors. What goes wrong?

New query vectors and old document vectors come from different "maps", so their similarities are meaningless and search quality collapses (often silently). Re-embed all documents with the new model, or keep two separate indexes and switch over together.
:::

:::quiz
Why is a pure embedding search a poor way to find order number A9731?

Embeddings capture meaning, not exact strings. A code has no meaning to match, and similar-looking codes may be close or far unpredictably. Exact identifiers need keyword search or a database lookup, often combined with embeddings in a hybrid search.
:::

## 📚 Keep learning

- [Anthropic docs: Embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)
- [Sentence-Transformers documentation](https://www.sbert.net/)
- [Jay Alammar: The Illustrated Word2vec](https://jalammar.github.io/illustrated-word2vec/)

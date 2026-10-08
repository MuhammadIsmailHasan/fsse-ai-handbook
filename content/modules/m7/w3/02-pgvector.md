---
title: "pgvector in PostgreSQL"
summary: "Store embeddings next to your normal data in PostgreSQL — the vector column and distance operators, exact search versus HNSW and IVFFlat indexes, filtering by metadata, measuring recall, and when a dedicated vector database is worth it."
type: lesson
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: core, ops: optional }
durationMinutes: 180
tags: [pgvector, postgresql, vector-search, hnsw, ivfflat, indexing]
lastReviewed: 2026-10
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- What **pgvector** is, and why many teams start with it
- The **`vector` column** and the three distance operators
- **Exact** search versus **approximate** indexes (**HNSW**, **IVFFlat**)
- **Metadata filters** together with vector search
- How to **measure recall** and tune speed against accuracy
- When to stay in PostgreSQL, and when to move to a dedicated vector database

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **pgvector** | A PostgreSQL extension that adds a vector type and vector search | Ekstensi vektor PostgreSQL |
| **Vector column** | A column that holds an embedding, like `vector(1024)` | Kolom vektor |
| **Distance operator** | A symbol such as `<=>` that measures how far apart two vectors are | Operator jarak |
| **ANN** | Approximate nearest neighbours: a fast search that may miss a few | Pencarian perkiraan |
| **HNSW** | An index built as layers of linked neighbours | Indeks graf berlapis |
| **IVFFlat** | An index that groups vectors into clusters and searches only a few | Indeks berkelompok |
| **Recall** | How many of the true nearest neighbours the index found | Ketercapaian |
| **Pre/post-filter** | Apply a metadata filter before or after the vector search | Filter sebelum/sesudah |

## 🧠 The big idea

You already have a **library with a catalogue**: your PostgreSQL tables, with users, orders and documents. pgvector adds a new kind of shelf where books are arranged **by meaning**. Asking "show me five books like this one" takes one query, in the same building, with the same librarian, the same back-ups and the same security rules.

The alternative is building a **second library** (a separate vector database) and keeping it in sync with the first. Sometimes that is the right call. Often it is extra work for no reason.

## ❓ Why it matters

Most AI features need three things together: **the text**, **its vector**, and **normal data to filter by** (customer, language, date, permissions). Keeping them in one PostgreSQL database gives you:

- **transactions**: a document and its vector are saved or deleted together,
- **joins and filters**: "similar articles, only for tenant 7, published this year",
- **one system** to run, back up, monitor and secure,
- tools you already know: SQL, migrations, psycopg, SQLAlchemy.

For many products, up to millions of vectors, this is enough and simple.

## 📖 Step by step

### 1. Run PostgreSQL with pgvector

The standard PostgreSQL image does not include the extension. Use an image that does, on a non-default port so it does not clash with other databases on your machine:

```yaml
# compose.yaml
services:
  vectordb:
    image: pgvector/pgvector:pg17
    environment:
      POSTGRES_USER: app
      POSTGRES_PASSWORD: app
      POSTGRES_DB: app
    ports:
      - "5494:5432"
```

Then, once per database:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

On managed services (RDS, Cloud SQL, Supabase, Neon, ...) the extension is usually available; you enable it with the same statement.

### 2. A table with a vector column

```sql
CREATE TABLE chunks (
    id           bigserial PRIMARY KEY,
    document_id  bigint NOT NULL,
    tenant_id    integer NOT NULL,
    lang         text NOT NULL,
    content      text NOT NULL,
    embedding    vector(1024) NOT NULL,       -- the dimension must match your embedding model
    embedding_model text NOT NULL,            -- store it: you will change it one day
    updated_at   timestamptz NOT NULL DEFAULT now()
);
```

The number in `vector(1024)` is the **dimension**. A vector of another size is rejected, which is exactly what you want. Keep the model name in a column.

Insert from Python (psycopg 3 with the `pgvector` helper package):

```python
import psycopg
from pgvector.psycopg import register_vector

with psycopg.connect(DATABASE_URL) as conn:
    register_vector(conn)                      # lets you pass Python lists / numpy arrays as vectors
    conn.execute(
        "INSERT INTO chunks (document_id, tenant_id, lang, content, embedding, embedding_model) "
        "VALUES (%s, %s, %s, %s, %s, %s)",
        (doc_id, tenant_id, "id", text, embed(text), EMBEDDING_MODEL),
    )
```

### 3. Search with distance operators

pgvector gives you operators; a **smaller distance means closer**:

| Operator | Distance | Use with |
|---|---|---|
| `<->` | Euclidean (L2) | general |
| `<=>` | **cosine distance** (1 − cosine similarity) | most text embeddings |
| `<#>` | **negative** inner product | normalised vectors, fastest |

```sql
-- the 5 chunks nearest to the query vector, by cosine distance
SELECT id, content, embedding <=> $1 AS distance
FROM chunks
ORDER BY embedding <=> $1
LIMIT 5;
```

```python
rows = conn.execute(
    "SELECT id, content, embedding <=> %s AS distance FROM chunks ORDER BY embedding <=> %s LIMIT 5",
    (query_vec, query_vec),
).fetchall()
similarity = 1 - rows[0][2]        # turn cosine distance back into similarity
```

Without an index this is an **exact** search: PostgreSQL computes the distance to every row. It is always correct, and for tens of thousands of rows it is fast enough. Start there. Add an index when it gets slow.

### 4. Approximate indexes: HNSW and IVFFlat

For many rows, an index checks only promising candidates. It is **approximate**: it can miss a true neighbour (lower **recall**) in return for speed. The same trade-off you built with the random-hyperplane index in the exercise.

**HNSW**: a layered graph of neighbours. Good recall and speed, slower and larger to build, can be created on an empty table. The usual first choice.

```sql
CREATE INDEX chunks_embedding_hnsw
ON chunks USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

SET hnsw.ef_search = 100;      -- per session: bigger = better recall, slower queries
```

**IVFFlat**: groups vectors into clusters (`lists`) and searches only the nearest few (`probes`). Faster to build and smaller, a little lower recall. Build it **after** loading data, because the clusters come from existing rows.

```sql
CREATE INDEX chunks_embedding_ivf
ON chunks USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

SET ivfflat.probes = 10;       -- bigger = better recall, slower queries
```

Rules:

- The index operator class must match the operator you query with: `vector_cosine_ops` ↔ `<=>`, `vector_l2_ops` ↔ `<->`, `vector_ip_ops` ↔ `<#>`. Otherwise PostgreSQL ignores the index and does an exact scan.
- Look at `EXPLAIN ANALYZE` to see whether the index is used.
- There is a limit on how many dimensions an indexed `vector` can have (about 2,000); for bigger models use a smaller output dimension or the half-precision type.
- Indexes use memory and disk, and building them takes time. Plan it.

### 5. Metadata filters: the tricky part

Real queries filter: "only tenant 7, only Indonesian, only published".

```sql
SELECT id, content
FROM chunks
WHERE tenant_id = 7 AND lang = 'id'
ORDER BY embedding <=> $1
LIMIT 5;
```

With an approximate index there is a catch: the index finds the nearest candidates first, and the filter removes some of them afterwards. If your filter is very selective (tenant 7 owns 0.1% of rows), you can get **fewer than 5 results**, or poorer ones. Remedies:

- raise `hnsw.ef_search` (or `ivfflat.probes`) so the index looks at more candidates,
- use newer pgvector options for iterative scanning, if your version has them,
- create a **normal index** on the filter columns (`tenant_id`) so PostgreSQL can choose to filter first and then do an exact scan on the small set,
- for strongly separated groups, use **partitioning** or a **partial index per tenant**,
- and always **test with your real filters**.

A very common safe case: each tenant has a modest number of chunks, so "filter by tenant, then exact search" is fast and perfectly accurate.

Permissions belong in the filter too. A user must only retrieve chunks they are allowed to see: put the access rule in the `WHERE`, not in the prompt.

### 6. Measure recall

Never accept an approximate index on faith. Compare it with the exact answer on real queries:

```python
def recall_at_k(approx_ids, exact_ids):
    if not exact_ids:
        return 1.0
    return len(set(approx_ids) & set(exact_ids)) / len(exact_ids)
```

```sql
-- exact answer: force PostgreSQL to ignore the index for this transaction
BEGIN;
SET LOCAL enable_indexscan = off;
SET LOCAL enable_bitmapscan = off;
SELECT id FROM chunks ORDER BY embedding <=> $1 LIMIT 10;
COMMIT;
```

Run 100–200 real queries both ways, average the recall@10, and note the latency. If recall is 0.99 at 5 ms, great. If it is 0.8, raise `ef_search`/`probes` or the index parameters, and measure again. This is how you pick settings with evidence.

### 7. Everyday operations

- **Upserts and deletes** work like any row: update the text, update the vector in the same transaction. Delete a document, delete its chunks.
- **Re-embedding:** to change the model, add a new column (or table) for the new vectors, backfill in batches, build the new index, switch queries, drop the old column.
- **Size:** a 1024-dimension vector uses about 4 KB. A million chunks is about 4 GB of vectors before the index. Plan memory so the index fits in RAM for speed.
- **Backups, replicas, migrations:** same as the rest of your database.
- **Hybrid search:** PostgreSQL also has full-text search, so keyword and vector search can live in one query (lesson 4).

### 8. pgvector or a dedicated vector database?

| Stay with pgvector when | Consider a dedicated vector database when |
|---|---|
| you already run PostgreSQL | you have hundreds of millions of vectors or very high query rates |
| you need joins, filters, transactions | you need advanced features (very fast filtered search, built-in sharding) at large scale |
| millions of vectors, moderate traffic | a search team will own the system full-time |
| you want fewer systems to operate | you accept operating and syncing another system |

Start simple. Migrate when you have evidence (latency, cost or recall numbers) that you must.

### Choosing your setup

| Situation | Do this |
|---|---|
| Up to ~50,000 chunks | exact search; no vector index needed |
| More, and recall matters | HNSW index; tune `ef_search`; measure recall |
| Fast build, less memory, loading a big dataset | IVFFlat after loading; tune `lists` and `probes` |
| Per-tenant or permission filters | filter in SQL; test selective filters; consider per-tenant partitioning |
| Changing the embedding model | new column/table, backfill, new index, switch, drop old |
| Need exact words too | add full-text search (lesson 4) |

- ✅ Store the model name; keep the dimension in the column type.
- ✅ Measure recall and latency with real queries.
- 🚫 Choosing index parameters from a blog without measuring.
- 🚫 Doing permission checks in the prompt instead of the `WHERE`.

## ⚠️ Common mistakes

- Using the wrong operator or operator class, so the index is silently ignored.
- Creating an IVFFlat index on an empty table.
- Forgetting that a selective filter plus an approximate index can return too few rows.
- Different models (or dimensions) mixed in one column.
- No `embedding_model` column, so you cannot tell what is stale.
- Never checking `EXPLAIN ANALYZE`.
- Checking permissions after retrieval, or in the prompt.
- Running the database on the default port with default credentials on a shared machine.

:::revoshop
RevoShop already has PostgreSQL. Sketch the table you would add to search product descriptions by meaning: the columns, the vector dimension, the index you would start with (and why), and the filter for "only products in stock". How many products would you need before an index becomes necessary?
:::

## 🏆 Best practices

- [ ] Start with exact search; add an index when measurements say so.
- [ ] Match the operator, the operator class and the distance you want.
- [ ] Store `embedding_model` and keep the dimension in the type.
- [ ] Put tenant and permission filters in SQL, and test selective filters.
- [ ] Measure recall@k against exact search before and after tuning.
- [ ] Run `EXPLAIN ANALYZE` to confirm the index is used.
- [ ] Plan re-embedding with a new column and a background backfill.
- [ ] Use a non-default port and real credentials; treat vectors as sensitive as the text.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain pgvector with the library-and-catalogue picture. What does "approximate" cost you, and what do you get in return?

## 📐 Design it

SupportDesk AI stores help articles for 40 client companies (tenants). In total there are 800,000 chunks; the biggest tenant has 200,000, the smallest 500. Every query must only see its own tenant's chunks. Latency must stay under 100 ms at 50 queries per second. Design the schema, the index and filter strategy, how you measure quality, and how you handle the model change next year.

:::quiz
Show a possible design

- **Schema:** `chunks(id, tenant_id, article_id, lang, content, embedding vector(D), embedding_model, updated_at)` with a normal B-tree index on `(tenant_id)`; `ON DELETE CASCADE` from articles.
- **Strategy:** because tenants differ wildly in size, choose per size: small tenants (≤ ~20,000 chunks) can use "filter by tenant, then exact scan" — exact and fast; big tenants get an **HNSW** index. Two options for the big ones: list-partition the table by `tenant_id` and index each big partition separately (the query's `WHERE tenant_id = ...` prunes to one partition), or one HNSW index with a raised `ef_search` and iterative scanning if available.
- **Always** put `WHERE tenant_id = $1` in the SQL, never rely on the app to remove other tenants' rows afterwards (it is an access-control rule).
- **Quality:** 200 labelled queries per big tenant and 50 for small ones; compute recall@10 against exact search and answer quality (recall of the right article); tune `ef_search` until recall ≥ 0.95 within the latency budget.
- **Latency:** `EXPLAIN ANALYZE` the real queries; keep the HNSW index in memory (size the instance); a connection pool; measure p95 under load with a test of 50 queries per second.
- **Model change:** add `embedding_v2` and `embedding_model_v2`, backfill in batches by tenant, build the new index (concurrently), run the labelled queries on both, switch by tenant, and finally drop the old column and index.
- **Operations:** nightly job to find chunks whose article changed; delete orphans; back up with the rest of the database; monitor index size and query latency.

**Rule shown:** pick exact search where the data is small, an index where it is big, always filter in SQL, and prove it with recall and latency numbers.
:::

### 📝 Self-review checklist

- [ ] Operator, operator class and metric agree
- [ ] Tenant filtering is in SQL
- [ ] Recall and latency are measured on real queries
- [ ] There is a plan for re-embedding

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m7/w3/02-vector-store" ai="no-ai" title="A tiny vector database: exact and approximate"}
Build `VectorStore` (exact search with cosine, dot or Euclidean score, dimension checks and a metadata filter applied before ranking), `LSHIndex` (random hyperplanes: only the query's bucket, and optionally its one-bit neighbours, are scored) and `recall_at_k`. The tests show the speed-versus-recall trade-off you will meet with HNSW and IVFFlat. No database needed.
:::

:::hints
- `VectorStore.search`: filter first (`all(metadata.get(k) == v and k in metadata ...)`), then score, then sort by `(-score, id)`.
- `LSHIndex`: `rng = random.Random(seed)`; planes are `[[rng.gauss(0, 1) for _ in range(dim)] for _ in range(planes)]`.
- Signature: a tuple of bits `1 if dot(vector, plane) >= 0 else 0`; bucket ids by signature in `__init__`.
- Probing neighbours: for each bit position build the signature with that single bit flipped and add its bucket.
- `recall_at_k`: `len(set(approx) & set(exact)) / len(exact)`, with `1.0` for an empty exact list.
:::

## ✅ Quick check

:::quiz
Why can an approximate index plus a selective filter return fewer than k rows?

The index first picks the nearest candidates among all rows, then the `WHERE` filter removes those that do not match. If the filter keeps only a tiny share of rows, most candidates are removed and few remain. Raise the search breadth, filter first with a normal index, or partition the data.
:::

:::quiz
You created `vector_l2_ops` but query with `<=>`. What happens?

PostgreSQL cannot use that index for cosine distance, so it silently falls back to an exact scan. The results are right but slow. Match the operator class to the operator and confirm with `EXPLAIN ANALYZE`.
:::

:::quiz
Why start with exact search instead of an HNSW index?

Exact search is always correct, needs no tuning and is fast enough for tens of thousands of rows. An approximate index adds build time, memory and a recall trade-off, so add it only when measurements show that latency requires it.
:::

## 📚 Keep learning

- [pgvector on GitHub](https://github.com/pgvector/pgvector)
- [pgvector-python](https://github.com/pgvector/pgvector-python)
- [PostgreSQL: EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html)

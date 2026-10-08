---
title: "Chunking Strategies"
summary: "Cut documents so that retrieval works — split by headings and paragraphs, group whole sentences, search small and answer with the big parent, keep the heading path, and treat tables, code and PDFs with care."
type: lesson
source: original
roles: { be: recommended, fe: optional, fs: recommended, ai: core, ops: optional }
durationMinutes: 180
tags: [rag, chunking, markdown, parent-child, metadata]
lastReviewed: 2026-10
---

::part[Learn the Concept]{n="1"}

## 🎯 What you'll learn

- Why **chunking** is the biggest hidden lever in RAG quality
- **Structure-based** chunking (headings, paragraphs) with a **heading path**
- **Sentence-based** chunking with overlap
- **Parent-child (small-to-big)** retrieval
- How to handle **tables, code, lists and PDFs**
- How to **choose** a strategy with evidence

## 🔤 Key words

| Word | In simple words | Bahasa Indonesia |
|---|---|---|
| **Chunk** | The unit you embed, search and put in a prompt | Potongan |
| **Heading path** | The chain of headings above a chunk: `Returns > Refunds` | Jalur heading |
| **Overlap** | Text repeated at the edge of neighbouring chunks | Tumpang tindih |
| **Parent chunk** | A big piece (a section) that gives context | Potongan induk |
| **Child chunk** | A small piece inside a parent, used for precise search | Potongan anak |
| **Small-to-big** | Search small pieces, return the big parent | Cari kecil, beri besar |
| **Semantic chunking** | Cutting where the topic changes, found with embeddings | Pemotongan semantik |
| **Contextual chunk** | A chunk with a short note of where it comes from added in front | Potongan berkonteks |

## 🧠 The big idea

Think of cutting a **long cake**. You can cut every 3 cm with a ruler and ignore the layers: some slices are all cream, some have half a strawberry. Or you cut **along the layers** so that each slice is one flavour. Search works the same way: a slice that is *one idea* gets a clear "taste" (embedding) and can be found; a slice with half of one idea and half of another is muddy.

And then there is the question of what to **serve**: to find the right slice you want small, precise pieces. To let the model answer well you may want the **whole layer** the slice came from. Parent-child retrieval does both.

## ❓ Why it matters

Chunking happens **before** everything else. If the answer is cut in half across two chunks, or buried in a chunk about three other things, no embedding model or re-ranker can fully repair it. In practice:

- bad chunks → the right text is never retrieved (retrieval miss),
- chunks without their heading → the model sees "7 days" and cannot tell if it is about refunds or delivery,
- huge chunks → the prompt fills with noise and costs more,
- tiny chunks → no context, and the answer is spread over many pieces.

Teams that fix chunking often gain more than teams that switch to a bigger model.

## 📖 Step by step

### 1. Start with the structure

Documents already have structure: headings, paragraphs, lists, tables. Use it first, and apply size limits second.

```text
# Returns                      path: "Returns"
You can return items within 14 days.

## Refunds                     path: "Returns > Refunds"
Refunds are paid back in 7 days.
Shipping costs are not refunded.

## Exchanges                   path: "Returns > Exchanges"
Exchanges depend on stock.
```

Rules for a good markdown chunker:

- A **heading starts a new section**; keep a **heading path** (`A > B`). A new heading of the same or higher level pops the path back.
- A section that fits in `max_words` is **one chunk**.
- A longer section is cut **between paragraphs** first; only a single huge paragraph is cut by words.
- Each chunk keeps its **path** and its **index**, so you can show where it came from and fetch its neighbours.

```python
import re

_HEADING = re.compile(r"^(#{1,6}) (.*)$")

def split_markdown(text, max_words):
    sections, path, body, current_path = [], [], [], ""

    def flush():
        if "".join(body).strip():
            sections.append((current_path, "\n".join(body)))

    for line in text.split("\n"):
        m = _HEADING.match(line)
        if m:
            flush()
            body = []
            level = len(m.group(1))
            path = path[: level - 1] + [m.group(2).strip()]       # a level-2 heading keeps the level-1 parent
            current_path = " > ".join(path)
        else:
            body.append(line)
    flush()
    ...   # then cut each long section between paragraphs, up to max_words
```

### 2. Put the heading path into the text you embed

The sentence "Refunds are paid back in 7 days." says little alone. Embed it with its path:

```text
Returns > Refunds
Refunds are paid back in 7 days.
Shipping costs are not refunded.
```

The path gives the embedding (and the later model) the missing context. Store the path as **metadata** too, for display and filters. This is one of the cheapest improvements you can make.

A stronger version of the same idea is **contextual chunks**: for each chunk, add one or two sentences that situate it in the whole document ("This chunk is from the 2025 refund policy of Warung Kita, section on shipping costs"). A model can write these notes while you index. It costs tokens at indexing time, but helps when chunks are ambiguous on their own. Test it on your questions before you pay for it at scale.

### 3. Sentence-based chunking

For plain text without headings (emails, transcripts, long paragraphs), group **whole sentences**:

```python
def split_sentences(text):
    parts = re.split(r"(?<=[.!?])(?!\d)\s+", text.strip())          # "3.5" or "10.000" is not a sentence end
    return [p.strip() for p in parts if p.strip()]

def sentence_chunks(text, max_words, overlap_sentences=0):
    sentences = split_sentences(text)
    chunks, current = [], []
    words = lambda sents: sum(len(s.split()) for s in sents)
    for sentence in sentences:
        n = len(sentence.split())
        if current and words(current) + n > max_words:
            chunks.append(" ".join(current))
            carry = current[-overlap_sentences:] if overlap_sentences else []
            current = carry if carry and words(carry) + n <= max_words else []
        current.append(sentence)
    if current:
        chunks.append(" ".join(current))
    return chunks
```

Overlap of one sentence means a thought at a boundary appears whole in at least one chunk. Abbreviations ("Dr.", "e.g.") can fool a simple regex; for important text use a proper sentence splitter library.

### 4. Parent-child: search small, answer big

Small chunks match a question precisely. Big chunks give the model enough context to answer. Do both: embed **children**, return the **parent**.

```python
def parent_child(parents, child_words):
    children, parent_of = [], {}
    for parent in parents:
        words = parent["text"].split()
        for n, start in enumerate(range(0, len(words), child_words)):
            child_id = f"{parent['id']}#{n}"
            children.append({"id": child_id, "text": " ".join(words[start : start + child_words])})
            parent_of[child_id] = parent["id"]
    return children, parent_of

def expand_to_parents(hit_ids, parent_of, parents):
    out, seen = [], set()
    for hit in hit_ids:
        pid = parent_of.get(hit)
        if pid is None or pid in seen:
            continue                                  # skip unknown ids and parents we already added
        seen.add(pid)
        out.append({"id": pid, "text": parents[pid]})
    return out
```

```text
search the CHILD "paid back in 7 days"  ──►  hit: refunds#2
return the PARENT: the whole "Refunds" section  ──►  into the prompt (each parent only once)
```

A parent is usually a section or a page. The cost is bigger prompts, so keep the parent count small (top 3–4) and watch your token budget.

A related trick is to return a hit **plus its neighbours** (the chunk before and after), using the `index` you stored.

### 5. Tables, code, lists and PDFs

| Content | Care |
|---|---|
| **Tables** | keep a table in one chunk, and repeat the column headers; for huge tables, one chunk per group of rows with the headers on top; or convert rows into sentences ("Product A costs Rp 50.000 and ships in 2 days") |
| **Code** | cut at function/class boundaries, never in the middle of a block; keep the file path and language as metadata |
| **Lists** | keep a list with its introduction ("To reset your password:") and do not split numbered steps |
| **PDFs** | text extraction may scramble columns, headers, footers, hyphenation. Check the extracted text by eye. Remove repeated headers/footers and page numbers; scanned pages need OCR |
| **HTML pages** | strip menus, cookie banners and footers; keep headings and main content |
| **Chat logs, tickets** | chunk by conversation or by topic, with speaker names and dates as metadata |
| **Slides** | one slide (title + notes) is a natural chunk |

Garbage in, garbage out: **look at your chunks**. Print twenty random chunks and read them like a user would.

### 6. Size and overlap: choose with evidence

There is no universal best size. Typical starting points: **150–300 words** with **10–20% overlap** for prose; structure-based cuts for documents with headings. Then test:

| Setting | recall@5 | MRR |
|---|---|---|
| 100 words | measure | measure |
| 250 words | measure | measure |
| 250 words + heading path | measure | measure |
| sentence-based, overlap 1 | measure | measure |
| parent-child (child 60, parent = section) | measure | measure |

Use the test set from week 3. Change **one** thing, keep the winner, repeat. And compare **end-to-end** answer quality too: a setting with great recall may give prompts that are too long.

### 7. Metadata every chunk should carry

```text
doc_id, chunk_index, path (heading path), title, source URL, language,
tenant / access level, product / version, updated_at, content_hash, parent_id
```

Children inherit the parent's metadata (tenant, language, access). Never let a child lose the access fields: a leaked child is a leaked document.

### 8. Re-chunking later

Changing the chunker means re-embedding everything. Keep your chunking code **versioned** (store `chunker_version` in metadata), index into a **new** collection, run the test set, then switch. Avoid mixing chunkers inside one index.

### Choosing your setup

| Content | Start with |
|---|---|
| Help articles, docs with headings | markdown/heading chunker with heading path, ~200 words |
| Emails, transcripts, plain prose | sentence chunks of ~150 words, 1 sentence overlap |
| Long manuals where context matters | parent-child (child ~60–100 words, parent = section) |
| Tables and price lists | table-aware chunks with headers repeated |
| Code | split at functions/classes |
| Messy PDFs | clean the extraction first, then chunk |
| Ambiguous chunks | add contextual notes or the heading path |

- ✅ Print and read real chunks.
- ✅ Keep the heading path, the index and the access metadata.
- 🚫 Cutting by fixed characters through sentences and tables.
- 🚫 Changing the chunker without re-running the test set.

## ⚠️ Common mistakes

- Fixed-size character chunks that cut sentences, tables and code.
- Dropping headings, so chunks lose their topic.
- One giant chunk per document ("the embedding will figure it out").
- Duplicating text across chunks without limit (huge overlap).
- Forgetting access metadata on child chunks.
- Trusting PDF text extraction without looking at it.
- Mixing old and new chunkers in the same index.
- Optimising chunk size on three examples.

:::revoshop
Take one RevoShop help page (shipping or returns). Mark where you would cut it with a markdown chunker, write the heading path of each chunk, and say which part should be a parent and which children. Name one place where a naive 200-word cut would split an answer.
:::

## 🏆 Best practices

- [ ] Chunk by structure first (headings, paragraphs), then by size.
- [ ] Keep the heading path in both the embedded text and the metadata.
- [ ] Use overlap sparingly (10–20%) and never split a sentence, table row or code block.
- [ ] Consider parent-child retrieval when answers need surrounding context.
- [ ] Inspect random chunks by eye after every change to the pipeline.
- [ ] Carry tenant, language and access metadata on every chunk.
- [ ] Version the chunker and re-index into a new collection when it changes.
- [ ] Pick settings with a test set, not with intuition.

::part[Explain & Design]{n="2"}

## 🗣️ Explain it

Explain chunking with the layered-cake picture. Why is "search small, return the parent" better than either extreme?

## 📐 Design it

SupportDesk AI indexes: markdown help articles, 40-page PDF manuals with tables, and exported email threads. Design the chunking for each source type, the metadata, how you keep answers that span a section intact, and how you decide on sizes.

:::quiz
Show a possible design

- **Help articles (markdown):** heading-based chunker with a heading path, `max_words` about 200, cut between paragraphs; prefix the embedded text with the path; metadata: article id, path, URL, language, product, status, updated date, hash.
- **PDF manuals:** clean extraction first (remove headers, footers, page numbers, fix hyphenation; OCR if scanned). Split by detected headings; tables become their own chunks with repeated column headers (and, for key tables, a row-per-sentence version). Metadata adds manual version and page number so citations can say "page 12".
- **Email threads:** remove quoted replies and signatures; chunk by message or by topic; metadata: thread id, sender role (customer/agent), date. Do not index personal data that is not needed.
- **Parent-child for manuals:** children of ~80 words are searched; the parent (the section) is returned to the model, limited to the top 3 parents and the token budget.
- **Neighbour expansion:** for step-by-step procedures, also fetch the chunk before and after a hit using `chunk_index`.
- **Access metadata:** tenant, language and visibility are copied to every child and parent chunk.
- **Choosing sizes:** a 200-question test set; try 120/200/300-word settings, with and without heading path, and with parent-child; compare recall@5, MRR and end-to-end answer correctness plus tokens per answer; pick the best trade-off.
- **Operations:** `chunker_version` in metadata; rebuilding into a new collection when the chunker changes; a weekly sample review of 30 random chunks.

**Rule shown:** each source type gets a chunker that respects its structure, and the evidence (not taste) picks the sizes.
:::

### 📝 Self-review checklist

- [ ] Each content type has a matching chunking strategy
- [ ] Heading path, index and access metadata are kept
- [ ] Tables, code and PDFs are handled deliberately
- [ ] The chunker is versioned and settings were chosen with a test set

::ai-review{task="design"}

::part[Toy Exercise]{n="3"}

:::exercise{path="exercises/m7/w4/02-chunkers" ai="no-ai" title="Structure-aware chunkers"}
Write `split_markdown` (heading paths, paragraph-aware cuts, indexes), `split_sentences` (not inside `3.5`), `sentence_chunks` (whole sentences with optional overlap), `parent_child` (small children mapped to parents) and `expand_to_parents` (each parent once, best first). No API key needed.
:::

:::hints
- Track a `path` list: for a heading of level `n`, `path = path[: n - 1] + [title]`.
- A section with no body text makes no chunk; the `index` counts chunks over the whole document.
- To cut a long section: group whole paragraphs until adding the next would pass `max_words`; a single paragraph longer than `max_words` is cut by words.
- Sentence split regex: `re.split(r"(?<=[.!?])(?!\d)\s+", text.strip())`.
- `sentence_chunks` overlap: when starting a new chunk, carry the last N sentences only if they still leave room for the next sentence.
- `expand_to_parents`: keep a `seen` set; skip hit ids that are not in `parent_of`.
:::

## ✅ Quick check

:::quiz
Why add the heading path to the text of each chunk?

A chunk like "Refunds are paid in 7 days" can lose its topic when cut out of the document. The path ("Returns > Refunds") gives the embedding and the later model the missing context, so the chunk is matched and understood correctly. It is cheap and usually improves results.
:::

:::quiz
What problem does parent-child retrieval solve?

Small chunks give precise matches but too little context to answer; big chunks give context but blur the match. Parent-child searches small child chunks and returns their bigger parent, so you get precision when finding and context when answering.
:::

:::quiz
You switch to a new chunker. What must you do before sending traffic to it?

Index into a new collection with the new chunks and embeddings, run your test set against both versions, compare retrieval and end-to-end metrics, and only then switch. Never mix two chunkers inside one index.
:::

## 📚 Keep learning

- [Anthropic: Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval)
- [LlamaIndex: Node parsers and chunking](https://docs.llamaindex.ai/en/stable/module_guides/loading/node_parsers/)
- [Pinecone: Chunking strategies](https://www.pinecone.io/learn/chunking-strategies/)

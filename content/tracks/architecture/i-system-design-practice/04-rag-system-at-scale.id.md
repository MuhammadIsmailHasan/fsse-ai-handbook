---
title: "RAG System at Scale"
summary: Merancang retrieval-augmented generation untuk lalu lintas nyata — pipeline ingest dan query, chunking, embedding dan pencarian vektor top-k, reranking dan citation, plus masalah caching, biaya, dan kesegaran yang muncul pada skala besar.
sourceHash: 201f79d4856b
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa itu **RAG** dan kenapa ia mengalahkan menjejalkan semuanya ke prompt
- Dua pipeline: **ingest** (offline) dan **query** (online)
- **Chunking**, **embedding**, dan **vector index** untuk pencarian top-k
- **Reranking** dan **citation** untuk jawaban lebih baik dan tepercaya
- Masalah skala: **caching**, **biaya**, **latensi**, dan **kesegaran**
- Bagaimana ini menggerakkan fitur CareerPilot / StudyMind

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **RAG** | Ambil teks relevan, lalu biarkan LLM menjawab memakainya |
| **Embedding** | Deret angka yang menangkap makna sebuah teks |
| **Chunk** | Potongan kecil sebuah dokumen |
| **Vector database** | Penyimpan yang cepat menemukan embedding terdekat |
| **Top-k retrieval** | Ambil k potongan paling relevan |
| **Rerank** | Mengurutkan ulang kandidat dengan model lebih pintar |
| **Citation** | Rujukan balik ke potongan sumber |
| **Kesegaran** | Seberapa mutakhir data yang ter-index |

## 🧠 Ide besarnya

LLM adalah **magang brilian tanpa akses ke berkasmu**. **RAG** memberi magang itu **pustakawan pintar**: sebelum menjawab, pustakawan menarik beberapa halaman paling relevan (**retrieval**) dan menyerahkannya, jadi magang menjawab dari *dokumenmu* — dengan rujukan halaman (**citation**) — alih-alih menebak dari ingatan.

Embedding adalah cara pustakawan menemukan "halaman tentang ide yang sama" bahkan saat katanya berbeda: makna serupa → angka serupa → berdekatan.

## ❓ Kenapa ini penting

Kamu tak bisa menempel seluruh basis pengetahuan ke prompt — terlalu besar, terlalu mahal, dan model punya batas konteks. RAG membuat LLM bisa menjawab dari korpus besar yang berubah dengan mengambil hanya potongan relevan. Ia tulang punggung kebanyakan fitur AI nyata (bot dukungan, Q&A dokumen, StudyMind). Membuatnya jalan di demo itu mudah; membuatnya cepat, murah, dan *segar* pada skala besar adalah rekayasa yang sebenarnya.

## 📖 Langkah demi langkah

### 1. Dua pipeline

RAG punya pipeline **ingest offline** dan pipeline **query online**:

```
INGEST (offline):  documents → chunk → embed → store in vector index
QUERY  (online):   question → embed → top-k search → (rerank) → LLM + chunks → answer + citations
```

### 2. Ingest: chunk, lalu embed

Dokumen dibagi menjadi **chunk** (masing-masing beberapa ratus token, sering dengan sedikit **overlap** supaya ide tak terpotong di tengah pikiran). Tiap chunk diubah menjadi **embedding** (vektor) oleh model embedding dan disimpan di **vector database** bersama teksnya dan id sumbernya.

Ukuran chunk adalah trade-off nyata: terlalu besar → potongan yang diambil berisik dan lebih mahal token; terlalu kecil → kehilangan konteks. Overlap menghindari kehilangan kalimat yang melintasi batas.

### 3. Query: ambil top-k

Pertanyaan user di-embed dengan cara sama, dan vector database mengembalikan **top-k** chunk paling mirip (berdasarkan cosine similarity). Ini potongan yang paling mungkin memuat jawaban.

### 4. Rerank dan citation

Top-k dari pencarian vektor cepat tapi kasar. **Reranker** opsional (model lebih pintar dan lebih lambat) mengurutkan ulang kandidat supaya yang terbaik memimpin. Lalu kamu bangun prompt: *"Jawab memakai potongan ini; sertakan citation,"* plus chunk-nya. LLM menjawab dan menyertakan **citation** balik ke potongan sumber, supaya user bisa memverifikasi — krusial untuk kepercayaan.

### 5. Masalah skala

Demo mengabaikan ini; produksi tak bisa:

| Masalah | Kenapa menggigit pada skala besar | Perbaikan |
|---|---|---|
| **Biaya** | Panggilan embedding + LLM berbiaya uang per request | Cache embedding; cache jawaban untuk pertanyaan berulang |
| **Latensi** | Embed + search + rerank + LLM menumpuk | Paralelkan, batasi k, pakai vector index cepat, stream jawaban |
| **Kesegaran** | Dokumen berubah; index jadi basi | Re-embed dokumen yang berubah; job ingest latar belakang |
| **Kualitas** | Chunk salah → jawaban salah | Chunking lebih baik, hybrid (keyword + vector) search, reranking |
| **Skala index** | Jutaan vektor | Vector DB terkelola/skalabel dengan index perkiraan (ANN) |

### 6. Caching, tuas terbesar

Dua cache menghemat paling banyak:
- **Cache embedding**: teks yang sama selalu di-embed ke vektor yang sama — cache-lah, jangan bayar untuk re-embed.
- **Cache jawaban**: pertanyaan identik (atau nyaris identik) bisa mengembalikan jawaban tersimpan alih-alih panggilan LLM baru.

### Pilih setup-mu

| Situasi | Lakukan ini |
|---|---|
| Dokumen kecil, statis | Vector store sederhana, tak perlu rerank |
| Korpus besar, berubah | Ingest latar belakang + re-embedding untuk kesegaran |
| Sensitif latensi | Batasi k, paralelkan, stream, cache jawaban |
| Sensitif biaya | Cache embedding dan jawaban; model lebih kecil bila mungkin |
| Sensitif kualitas | Hybrid search + reranking + citation |

- ✅ Pisahkan ingest offline dari query online; jaga index segar dengan job latar belakang.
- ✅ Cache embedding dan jawaban; ini kemenangan biaya/latensi terbesar.
- ✅ Kembalikan citation supaya jawaban bisa diverifikasi.
- 🚫 Jangan jejalkan seluruh korpus ke prompt; jangan lewatkan kesegaran atau caching pada skala besar.

## ⚠️ Kesalahan umum

- Chunk terlalu besar (berisik, mahal) atau terlalu kecil (tanpa konteks); tanpa overlap.
- Tak ada rencana kesegaran, sehingga jawaban mengutip dokumen usang selamanya.
- Re-embed teks yang sama tiap request alih-alih caching.
- Melewatkan citation, sehingga user tak bisa mempercayai atau memverifikasi jawaban.
- Bersandar pada pencarian vektor saja padahal keyword eksak penting (pakai hybrid search).

:::revoshop
RAG lebih topik CareerPilot/StudyMind daripada RevoShop, tapi polanya cocok: bayangkan "asisten bantuan RevoShop" atas FAQ dan kebijakannya. (1) Apa yang akan di-chunk dan di-embed pipeline ingest? (2) Untuk pertanyaan seperti "berapa jendela refund?", bagaimana top-k retrieval + citation menghasilkan jawaban tepercaya? (3) Saat kebijakan berubah, bagaimana kamu menjaga index tetap segar?
:::

## 🏆 Praktik terbaik

- [ ] Pisahkan ingest (offline) dari query (online); jalankan ingest sebagai pipeline latar belakang.
- [ ] Setel ukuran chunk dengan overlap; ukur kualitas retrieval, jangan menebak.
- [ ] Cache embedding (teks sama → vektor sama) dan cache jawaban untuk pertanyaan berulang.
- [ ] Tambah reranking dan hybrid (keyword + vector) search saat kualitas penting.
- [ ] Selalu kembalikan citation ke potongan sumber.
- [ ] Jaga index segar dengan re-embed dokumen yang berubah; pantau biaya dan latensi.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan RAG dengan analogi magang-brilian-plus-pustakawan-pintar. Lalu, dalam dua kalimat, katakan apa itu embedding dan kenapa ia membuat pustakawan menemukan potongan berdasarkan *makna* alih-alih kata eksak.

## 📐 Rancang

Rancang Q&A StudyMind atas handbook ini (ratusan lesson yang diedit seiring waktu). Cakup pipeline ingest, pipeline query (retrieval → rerank → jawaban dengan citation), bagaimana kamu menjaga jawaban segar saat lesson diedit, dan dua hal yang akan kamu cache untuk mengendalikan biaya dan latensi.

:::quiz
Tampilkan satu rancangan yang mungkin

**Ingest (offline):** untuk tiap lesson, bagi menjadi chunk ~300 token dengan overlap kecil, embed tiap chunk, dan simpan `{chunk_text, embedding, lesson_id, heading}` di vector database. Jalankan ini sebagai job latar belakang.

**Query (online):** embed pertanyaan siswa → top-k (katakanlah k=8) chunk mirip → **rerank** ke 3–4 terbaik → prompt LLM: "jawab memakai potongan ini dan sertakan citation lesson/heading." Kembalikan jawaban **dengan citation** supaya siswa bisa lompat ke lesson sumber.

**Kesegaran:** saat lesson diedit, re-embed hanya chunk lesson itu (berkunci `lesson_id`) dan ganti di index — supaya jawaban tak pernah mengutip konten basi. Hash konten mendeteksi lesson mana yang berubah.

**Caching (biaya + latensi):** (1) **cache embedding** — teks chunk di-hash ke vektornya, jadi chunk yang tak berubah tak di-embed ulang tiap ingest; (2) **cache jawaban** — pertanyaan umum ("apa itu idempotency?") mengembalikan jawaban tersimpan alih-alih panggilan LLM baru.

**Aturan yang ditunjukkan:** dua pipeline, kesegaran dengan re-embed dokumen yang berubah, citation untuk kepercayaan, dan cache embedding/jawaban agar tetap cepat dan terjangkau.
:::

### 📝 Checklist review mandiri

- [ ] Pipeline ingest dan query terpisah; ingest jalan di latar belakang
- [ ] Chunking (ukuran + overlap) dan top-k/rerank dispesifikasikan
- [ ] Kesegaran ditangani dengan re-embed dokumen yang berubah
- [ ] Citation dikembalikan; caching embedding + jawaban ada

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/architecture/i-system-design-practice/04-rag-retrieval" ai="no-ai" title="Chunking, cosine similarity, dan top-k retrieval"}
Implementasikan inti retrieval RAG: bagi daftar token menjadi chunk yang overlap, hitung cosine similarity antara dua vektor, dan kembalikan k dokumen paling mirip dengan vektor query. Tes memeriksa overlap, nilai similarity yang diketahui, dan pemeringkatan yang benar.
:::

:::hints
- `chunk_tokens(tokens, size, overlap)`: melangkah `size - overlap`; tiap jendela `tokens[i:i+size]`; berhenti saat kamu sudah menutupi akhir. Wajib `0 <= overlap < size`.
- `cosine_similarity(a, b)` = `dot(a,b) / (norm(a) * norm(b))`; kembalikan `0.0` kalau salah satu vektor semua nol.
- `top_k(query, corpus, k)`: skor tiap `{"id","vector"}` dengan cosine ke `query`, urutkan skor menurun (stabil), kembalikan k id pertama.
:::

## ✅ Cek cepat

:::quiz
Kenapa RAG dibagi menjadi pipeline ingest offline dan pipeline query online?

Karena meng-embed dan meng-index seluruh korpus itu lambat dan hanya perlu terjadi saat dokumen berubah (offline), sementara pertanyaan user harus dijawab cepat memakai index yang sudah dibangun (online). Memisahkannya menjaga query tetap cepat dan membuatmu bisa menyegarkan index di latar belakang.
:::

:::quiz
Pada skala besar, dua hal paling efektif untuk di-cache di sistem RAG, dan kenapa?

Embedding (teks yang sama selalu menghasilkan vektor yang sama, jadi caching menghindari bayar untuk re-embed) dan jawaban (pertanyaan identik atau nyaris identik bisa mengembalikan respons tersimpan alih-alih panggilan LLM baru yang mahal). Keduanya paling memangkas biaya dan latensi.
:::

## 📚 Lanjut belajar

- [What is RAG? (AWS)](https://aws.amazon.com/what-is/retrieval-augmented-generation/)
- [Pinecone: RAG and vector search learning center](https://www.pinecone.io/learn/retrieval-augmented-generation/)
- [OpenAI cookbook: question answering with embeddings](https://cookbook.openai.com/examples/question_answering_using_embeddings)

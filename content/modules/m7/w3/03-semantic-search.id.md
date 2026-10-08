---
title: "Semantic Search"
summary: "Bangun pencarian yang memahami makna: alur indeks dan kueri, ukuran chunk dan overlap, metadata dan kesegaran, serta cara mengukur kualitas dengan recall, precision dan MRR, bukan menebak."
sourceHash: f02ee8005d7f
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- **Dua alur**: mengindeks dokumen, dan menjawab kueri
- Cara **memotong (chunk)** teks, dan kompromi ukuran chunk serta overlap
- **Metadata** apa yang disimpan bersama setiap chunk
- Cara menjaga indeks tetap **segar** saat dokumen berubah
- Cara **mengukur** kualitas pencarian: precision, recall, MRR
- Cara menemukan dan memperbaiki **kegagalan**

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Chunk** | Potongan dokumen yang diindeks dan ditemukan sendiri |
| **Overlap** | Kata yang dibagi antar chunk bertetangga, supaya ide tidak terpotong dua |
| **Alur indeks** | Muat → bersihkan → chunk → embed → simpan |
| **Alur kueri** | Embed pertanyaan → cari → kembalikan chunk terbaik |
| **Top-k** | k hasil terbaik yang dikembalikan |
| **Precision@k** | Dari k hasil pertama, berapa yang benar |
| **Recall@k** | Dari semua hasil yang benar, berapa yang ada di k pertama |
| **MRR** | Rata-rata 1 / (posisi hasil benar pertama) |

## 🧠 Ide besarnya

Sistem semantic search adalah **pustakawan yang baik dengan kartu indeks yang baik untuk setiap halaman**. Saat perpustakaan dibangun, pustakawan membaca tiap dokumen, memecahnya jadi halaman yang masuk akal, menulis kartu untuk tiap halaman (embedding) dan mengarsipkannya dengan keterangan (judul, bahasa, tanggal). Saat seseorang bertanya, pustakawan menulis kartu untuk pertanyaan, menemukan kartu halaman terdekat, dan menyerahkan halaman-halamannya.

Dua hal menentukan apakah ini berhasil: **bagaimana halaman dipotong** (halaman yang mencampur lima topik mendapat kartu yang keruh), dan **apakah ada yang memeriksa** bahwa pustakawan benar-benar menemukan halaman yang tepat. Kebanyakan tim kurang berinvestasi di keduanya.

## ❓ Kenapa ini penting

Kualitas pencarian adalah langit-langit setiap fitur AI yang dibangun di atasnya. Bot support yang menjawab dari artikel hasil retrieval hanya bisa sebaik artikel yang diambilnya. Kalau bagian yang tepat tidak ada di hasil teratas, model terbaik di dunia pun tak bisa menjawab dengan benar. Kamu akan bertemu ini lagi di RAG minggu depan: **kebanyakan bug "AI menjawab salah" adalah bug retrieval**.

Dan "tampak baik saat kucoba tiga kueri" bukan bukti. Kamu butuh set uji kecil dan tiga angka.

## 📖 Langkah demi langkah

### 1. Dua alur

```text
INDEX (once, then on every change)
  documents → clean → CHUNK → embed (batched) → store vector + text + metadata

QUERY (every request)
  question → embed (same model!) → nearest chunks (+ filters) → [re-rank] → top-k chunks → show / give to the model
```

Jaga kedua alur dalam fungsi terpisah yang sederhana. Alur indeks adalah job batch yang bisa dijalankan ulang. Alur kueri cepat dan jalan di setiap request.

### 2. Chunking: potong di ide, bukan sembarangan

Embedding PDF 30 halaman utuh adalah kekaburan semua topiknya. Embedding satu kalimat terlalu sedikit konteks. Chunk yang baik **tentang satu ide**, biasanya 100–400 kata.

Pemotong sederhana yang berguna bekerja pada kata, dengan overlap:

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

Kompromi:

| | Chunk kecil | Chunk besar |
|---|---|---|
| Ketepatan kecocokan | tinggi (terfokus) | lebih rendah (topik campur) |
| Konteks untuk pembaca | sedikit | lebih banyak |
| Jumlah vektor / biaya | lebih banyak | lebih sedikit |
| Risiko | jawaban terpecah antar chunk | kalimat yang tepat terkubur |

Lebih baik daripada ukuran tetap: **pecah menurut struktur**. Potong di heading, paragraf dan item daftar dulu, baru kemudian menurut ukuran. Simpan heading sebagai awalan chunk-nya ("Kebijakan retur > Refund > ..."), karena menambah makna. Jangan memotong blok kode atau tabel di tengah. Tambahkan overlap 10–20% agar ide di batas muncul utuh di setidaknya satu chunk.

Tak ada ukuran sempurna. Coba 2–3 pengaturan pada set ujimu (di bawah) dan simpan yang skornya terbaik.

### 3. Apa yang disimpan bersama setiap chunk

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

Metadata yang mengubah mainan menjadi produk: filter menurut bahasa, produk, pelanggan, "terbit"; tampilkan sumber; tahu kapan sesuatu sudah usang.

### 4. Menjaga indeks tetap segar

Dokumen berubah. Kalau indeks tidak, user mendapat jawaban lama.

- Simpan **`content_hash`** dari teks tiap chunk. Saat re-index, bandingkan hash: embed ulang hanya chunk yang berubah.
- Saat dokumen **dihapus**, hapus chunk-nya (pakai foreign key dengan cascade atau pembersihan berkala).
- Saat dokumen **berubah ukuran**, batas chunk-nya bergeser: cukup ganti semua chunk dokumen itu dalam satu transaksi.
- Jalankan job indeks **terjadwal** dan pada **peristiwa perubahan** (webhook, pesan antrean).
- Saat kamu **mengganti model atau chunking**, bangun ke indeks *baru*, uji, lalu alihkan (lihat dua lesson terakhir).

### 5. Alur kueri

```python
def search(query, *, k=5, lang=None, tenant_id=None):
    query_vector = embedder.embed([query])[0]            # the SAME model as the index
    filters = {"tenant_id": tenant_id, **({"lang": lang} if lang else {})}
    candidates = store.search(query_vector, k=k * 4, where=filters)      # fetch more than you need
    results = [c for c in candidates if c.score >= MIN_SCORE][:k]         # optional floor
    return results
```

Trik berguna:

- **Ambil lebih banyak, lalu persempit** (k × 4, lalu re-rank atau saring ke k).
- **Skor minimum** menghindari menampilkan sampah saat tak ada yang relevan ("tidak ada hasil" adalah jawaban sah). Pilih dengan melihat kecocokan baik dan buruk yang nyata, bukan menyalin angka.
- **Menulis ulang kueri:** kueri sangat pendek atau bertele-tele ("nggak bisa") mencari dengan buruk. Model bahasa dapat menulis ulangnya jadi kueri pencarian yang jelas, memakai percakapan sejauh ini.
- **Filter dulu:** bahasa, tenant dan izin ada di filter, tidak pernah di prompt.
- **Multibahasa:** cek kueri berbahasa Indonesia terhadap dokumen berbahasa Inggris dan sebaliknya, jika usermu mencampur bahasa.

### 6. Ukur: set uji dan tiga angka

Bangun set uji dari pertanyaan nyata: **20–100 kueri**, masing-masing dengan id chunk atau dokumen yang menjadi jawaban benar. Tanya tim support-mu, baca tiket lama, tulis yang sulit sendiri.

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

| Metrik | Pertanyaan yang dijawabnya | Pemakaian khas |
|---|---|---|
| **Recall@k** | Apakah jawaban benar ada di k teratas? | RAG: model hanya bisa memakai yang kamu ambil |
| **Precision@k** | Seberapa banyak k teratas yang berguna? | menampilkan daftar hasil ke orang |
| **MRR** | Seberapa tinggi jawaban benar *pertama*? | pertanyaan satu jawaban; rata-rata 1/peringkat |

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

Bagian paling berharga adalah daftar **misses**: kueri yang tak menemukan apa pun yang berguna. Baca satu per satu.

### 7. Diagnosis misses

Untuk tiap kueri yang meleset, tanyakan di mana salahnya:

| Gejala | Kemungkinan penyebab | Perbaikan |
|---|---|---|
| Jawaban ada di dokumen tapi tidak terambil | chunk terlalu besar atau kecil; heading hilang; kata langka atau kode | ubah chunking; tambahkan judul ke tiap chunk; tambahkan pencarian kata kunci (lesson berikutnya) |
| Chunk yang tepat berperingkat 6–10 | model embedding lemah untuk domain atau bahasamu | coba model lain; tambahkan re-ranker |
| Benar hanya untuk kueri panjang | kueri pendek samar | menulis ulang kueri |
| Hasil dari produk, bahasa atau pelanggan yang salah | filter hilang | tambahkan metadata dan filter |
| Jawaban lama | indeks basi | content hash dan re-index terjadwal |
| Tak ada yang relevan | informasinya tidak ada di korpus | tambahkan konten; kembalikan "tak ada jawaban" |

Ubah **satu hal sekali** dan jalankan ulang set uji. Simpan tabel hasil per eksperimen (chunk 150 → recall@5 0,71; 300 → 0,78; dengan judul → 0,84). Tabel itu buktimu dan dokumentasimu.

### 8. Opsional: re-ranking

Pencarian pertama cepat dan kasar. **Re-ranker** (model cross-encoder atau layanan rerank penyedia) membaca kueri bersama setiap 20–50 kandidat teratas dan mengurutkannya lebih cermat. Lebih lambat dan lebih mahal, tapi sering meningkatkan precision dengan nyata. Pakai saat recall@50 tinggi tapi precision@5 rendah.

### Memilih caranya

| Situasi | Lakukan ini |
|---|---|
| Baru mulai | chunk berbasis paragraf/heading ~200 kata, overlap 10–20% |
| Dokumen panjang terstruktur | pecah menurut heading; awali chunk dengan jalur heading-nya |
| Jawaban terpecah antar chunk | lebih banyak overlap, atau chunk lebih besar, atau ambil chunk tetangga juga |
| Banyak tenant atau bahasa | metadata + filter di kueri |
| Dokumen sering berubah | `content_hash` + re-index terjadwal dan berbasis peristiwa |
| Kueri pendek samar | menulis ulang kueri |
| Recall@50 bagus, precision@5 lemah | tambahkan re-ranker |
| Id dan nama persis penting | hybrid search (lesson berikutnya) |

- ✅ Bangun set uji sebelum menyetel apa pun.
- ✅ Ubah satu hal sekali dan simpan tabel hasil.
- 🚫 Menilai kualitas dengan mencoba tiga kueri.
- 🚫 Menampilkan sampah berskor rendah, bukan "tak ada hasil".

## ⚠️ Kesalahan umum

- Chunking dengan jumlah karakter tetap dan memotong kalimat, tabel atau kode jadi dua.
- Tanpa metadata, sehingga filter dan kutipan mustahil nanti.
- Tidak pernah re-index, atau meng-embed ulang semuanya di setiap jalan.
- Meng-embed kueri dengan model atau pengaturan berbeda dari dokumen.
- Satu ambang kemiripan global yang disalin dari tutorial.
- Menyetel tanpa set uji ("rasanya lebih baik").
- Hanya melihat skor rata-rata dan mengabaikan misses.
- Menaruh kontrol akses di prompt, bukan di filter.

:::revoshop
Ambil sepuluh pertanyaan produk yang mungkin ditanyakan pelanggan RevoShop dan, untuk masing-masing, tulis id produk yang seharusnya ditemukan. Soal chunk: apakah kamu mengindeks satu chunk per produk, atau satu per paragraf deskripsi dan ulasan? Sebutkan metadata yang kamu simpan, dan satu kueri yang kamu perkirakan sulit.
:::

## 🏆 Praktik terbaik

- [ ] Bangun set uji kueri nyata dengan jawaban benar yang diketahui sebelum menyetel.
- [ ] Laporkan recall@k, precision@k dan MRR, dan baca misses.
- [ ] Chunk menurut struktur, dengan overlap kecil; simpan heading bersama chunk.
- [ ] Simpan sumber, bahasa, izin, hash, model dan timestamp sebagai metadata.
- [ ] Terapkan filter izin dan tenant di kueri pencarian.
- [ ] Jaga indeks segar dengan content hash dan job terjadwal.
- [ ] Ubah satu variabel per eksperimen dan catat angkanya.
- [ ] Kembalikan "tak ada hasil bagus" saat skor rendah.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan semantic search dengan gambaran pustakawan dan kartu indeks. Kenapa kamu harus menguji dengan pertanyaan nyata dan bukan sekadar mencoba beberapa?

## 📐 Rancang

SupportDesk AI akan mencari 3.000 artikel bantuan berbahasa Indonesia dan Inggris yang diedit tim support tiap hari. Pelanggan mengetik pertanyaan pendek dan berantakan ("barang blm sampe"). Rancang chunking, metadata, job kesegaran, alur kueri dan rencana evaluasi, termasuk cara memutuskan antara dua ukuran chunk.

:::quiz
Tampilkan rancangan yang mungkin

- **Chunking:** pecah tiap artikel menurut heading, lalu menurut paragraf ke chunk ~150–250 kata dengan overlap ~20%; awali tiap chunk dengan `Judul artikel > Bagian`; jaga langkah bernomor dan tabel tetap bersama.
- **Metadata:** `article_id`, `chunk_index`, `title`, `section`, `url`, `lang`, `product`, `status` (published/draft), `updated_at`, `content_hash`, `embedding_model`.
- **Embedding:** model multibahasa yang dipilih dengan menguji kueri Indonesia dan campuran; dokumen dan kueri berbagi model.
- **Kesegaran:** saat artikel disimpan, sebuah event mengantre job re-index untuk artikel itu; job membandingkan hash chunk, meng-embed ulang hanya chunk yang berubah, mengganti sisanya dalam satu transaksi, dan menghapus chunk artikel yang tak diterbitkan. Rekonsiliasi malam menangkap event yang terlewat.
- **Alur kueri:** normalisasi teks (huruf kecil, ubah "blm" → "belum" dengan daftar slang kecil), opsional tulis ulang dengan model memakai percakapan, embed, cari dengan `status = 'published'` dan filter bahasa, ambil 20 teratas, re-rank ke 5, buang hasil di bawah skor terukur, dan tampilkan tautan sumber.
- **Evaluasi:** 150 tiket nyata diubah jadi kueri (banyak yang pendek dan slang), masing-masing dengan id artikel yang benar. Hitung recall@5, precision@5 dan MRR, dan baca semua misses.
- **Memilih ukuran chunk:** jalankan set uji yang sama dengan 150, 250 dan 400 kata; bandingkan recall@5 dan MRR; pilih pemenangnya kecuali ia jauh lebih mahal atau kalah pada misses yang paling penting; cek ulang setelah perubahan konten besar.
- **Pemantauan:** catat kueri tanpa hasil atau berskor rendah; pakai sebagai kasus uji berikutnya.

**Aturan yang ditunjukkan:** susun chunk, simpan metadata berguna, jaga indeks segar, dan biarkan set uji (bukan perasaan) memilih pengaturan.
:::

### 📝 Daftar cek diri

- [ ] Chunk mengikuti struktur dokumen
- [ ] Metadata mendukung filter, kutipan dan kesegaran
- [ ] Ada set uji dengan recall, precision dan MRR
- [ ] Misses dibaca dan diubah menjadi perbaikan

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m7/w3/03-search-eval" ai="no-ai" title="Chunk, lalu ukur"}
Tulis `chunk_text` (chunk berbasis kata dengan overlap yang berhenti saat akhir tercapai), `precision_at_k`, `recall_at_k`, `reciprocal_rank` dan `evaluate` (rata-rata plus daftar kueri yang meleset). Tak perlu API key.
:::

:::hints
- `chunk_text`: validasi `size > 0` dan `0 <= overlap < size`; langkah = `size - overlap`; berhenti tepat setelah chunk yang memuat kata terakhir.
- `precision_at_k` membagi dengan `k`, bukan `len(ranked)`.
- `recall_at_k`: `len(set(ranked[:k]) & relevant) / len(relevant)`; `relevant` kosong memberi `1.0`.
- `reciprocal_rank`: `enumerate(ranked, start=1)`.
- `evaluate`: "miss" berarti tak ada id relevan di `ranked[:k]`; simpan misses dalam urutan kasus.
:::

## ✅ Cek cepat

:::quiz
Kenapa recall@k adalah angka utama untuk sistem RAG?

Model bahasa hanya bisa memakai bagian yang kamu berikan. Kalau bagian yang tepat tidak ada di k yang diambil, model tak bisa menjawab dengan benar, sebagus apa pun. Jadi pertanyaan pertama adalah apakah jawabannya ada di k teratas sama sekali.
:::

:::quiz
Kenapa menambahkan overlap antar chunk?

Sebuah ide bisa berada di seberang batas chunk. Overlap mengulang kata terakhir satu chunk di awal chunk berikutnya, sehingga ide muncul utuh di setidaknya satu chunk dan bisa dicocokkan dengan benar.
:::

:::quiz
Kamu mengubah ukuran chunk dan hasil "terasa lebih baik". Apa yang kurang?

Pengukuran. Jalankan set uji yang sama sebelum dan sesudah, bandingkan recall@k, precision@k dan MRR, dan baca misses. Perasaan dibiaskan oleh beberapa kueri yang kebetulan kamu coba.
:::

## 📚 Lanjut belajar

- [Anthropic docs: Embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)
- [Pinecone: Chunking strategies](https://www.pinecone.io/learn/chunking-strategies/)
- [MTEB: Massive Text Embedding Benchmark](https://huggingface.co/spaces/mteb/leaderboard)

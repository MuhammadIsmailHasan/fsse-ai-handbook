---
title: "Hybrid Search"
summary: "Gabungkan pencarian kata kunci (BM25, full-text PostgreSQL) dengan pencarian vektor — kenapa masing-masing sendirian gagal, bagaimana reciprocal rank fusion menggabungkan dua peringkat, cara melakukannya dalam satu query SQL, dan cara membuktikan hybrid benar-benar lebih baik."
sourceHash: 0d8b89c886a1
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Di mana **pencarian vektor gagal** dan di mana **pencarian kata kunci gagal**
- Bagaimana **BM25** menilai kecocokan kata kunci
- **Menggabungkan** dua peringkat: **reciprocal rank fusion (RRF)** dan skor berbobot
- Melakukan hybrid search **di dalam PostgreSQL**
- **Re-ranking** sebagai langkah terakhir opsional
- Cara **membuktikan** hybrid lebih baik pada datamu

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Pencarian kata kunci** | Menemukan dokumen yang memuat kata kueri |
| **BM25** | Rumus skor kata kunci klasik: kata langka lebih penting, teks panjang dinormalisasi |
| **Full-text search** | Mesin pencari yang tertanam di database (PostgreSQL punya) |
| **Hybrid search** | Pencarian kata kunci dan pencarian vektor bersama |
| **Fusi** | Menggabungkan dua daftar berperingkat menjadi satu |
| **RRF** | Reciprocal rank fusion: jumlahkan `1 / (60 + rank)` dari tiap daftar |
| **Re-ranker** | Model yang membaca kueri dan kandidat bersama dan mengurutkan lagi |
| **Tokenizer** | Memecah teks menjadi kata (token) untuk pencocokan |

## 🧠 Ide besarnya

Bayangkan kamu meminta dua asisten menemukan sebuah dokumen.

- **Asisten K (kata kunci)** adalah **pembaca cepat dengan ingatan sempurna untuk kata persis**. Minta "A9731" dan K menemukannya seketika. Minta "tidak bisa masuk", dan K hanya mencari halaman dengan kata-kata itu; ia melewatkan "Mengatur ulang kata sandi".
- **Asisten V (vektor)** adalah **pembaca yang berpikir dan memahami ide**. V tahu bahwa "tidak bisa masuk" dan "reset password" satu kelompok. Tapi minta "A9731" dan V angkat bahu: itu hanya string aneh.

Hybrid search bertanya **keduanya**, lalu menggabungkan daftar mereka. Halaman yang disukai kedua asisten naik ke atas. Halaman yang hanya ditemukan satu tetap punya kesempatan.

## ❓ Kenapa ini penting

User nyata mengetik kedua jenis kueri, sering di kotak yang sama:

- "kebijakan refund untuk barang rusak" (makna),
- "error E-4021" atau "pesanan A9731" atau "iPhone 15 Pro" (persis),
- "ongkir ke Medan" (slang, nama, bahasa campuran).

Studi dan praktik sama-sama menunjukkan bahwa **retrieval hybrid biasanya mengalahkan pencarian vektor murni** pada kueri dunia nyata yang campuran, terutama dengan kode produk, nama, akronim dan kata domain yang belum pernah dilihat model embedding. Di sistem RAG, bagian yang hilang berarti jawaban salah, jadi kualitas retrieval layak mendapat langkah tambahan ini.

## 📖 Langkah demi langkah

### 1. Pencarian kata kunci: BM25 dengan kata sederhana

BM25 memberi tiap dokumen skor untuk kueri:

- Sebuah kata lebih berarti bila **langka** di koleksi (kata "refund" lebih bermakna daripada "yang").
- Melihat kata **lebih sering** membantu, tapi dengan **hasil yang menurun** (kata "refund" ke-10 menambah sedikit).
- Dokumen **panjang** tidak diberi hadiah hanya karena panjang (normalisasi panjang).

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

Pengaturan: `k1` mengatur seberapa cepat kata berulang berhenti membantu; `b` mengatur normalisasi panjang. Nilai bawaan cukup untuk memulai.

Pencarian kata kunci **hebat** untuk: id, kode, nama, nomor error, kata teknis langka. Ia **buruk** untuk: sinonim, bahasa lain, salah ketik, dan kata berbeda untuk ide yang sama.

### 2. Pencarian vektor: kekuatan sebaliknya

Dari lesson sebelumnya: pencarian vektor bagus untuk makna dan lemah untuk string persis, angka dan negasi. Jadi kedua jenis kesalahan berbeda, dan itulah kenapa menggabungkannya berhasil.

### 3. Menggabungkan dua peringkat

Kamu punya dua daftar berperingkat. Bagaimana menggabungkannya? Skornya berada di **skala berbeda** (BM25 bisa 0 sampai 15, cosine similarity 0 sampai 1), jadi tak bisa langsung dijumlahkan.

**Reciprocal rank fusion (RRF)** mengabaikan skor dan hanya memakai **peringkat**:

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

Setiap daftar memberi dokumen `1 / (60 + rank)`. Dokumen di peringkat 1 di kedua daftar mendapat sekitar `2/61`; yang peringkat 1 di satu daftar saja mendapat `1/61`. Dokumen yang **disepakati beberapa daftar** naik. Konstanta 60 adalah bawaan umum yang menghaluskan selisih antara peringkat 1, 2, 3.

RRF populer karena **tak butuh penyetelan dan penskalaan skor**, dan bekerja bahkan saat satu daftar punya skor dari sistem berbeda.

**Fusi skor berbobot** adalah alternatifnya: skalakan tiap skor ke 0..1 dan campur.

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

Ia memungkinkanmu berkata "percayai vektor 70%, kata kunci 30%" (`alpha`), tapi kamu harus menyetel `alpha` pada set uji, dan penskalaan min-max bisa terganggu oleh satu skor pencilan. Mulailah dengan RRF; coba fusi berbobot bila punya set uji dan alasan.

### 4. Hybrid search kecil yang lengkap

```python
def hybrid_search(query, docs, vector_ranking, top=3):
    ids = list(docs)
    scores = bm25_scores(query, [docs[i] for i in ids])
    keyword = sorted(((i, s) for i, s in zip(ids, scores) if s > 0), key=lambda pair: (-pair[1], pair[0]))
    fused = reciprocal_rank_fusion([[i for i, _ in keyword], vector_ranking])
    return [i for i, _ in fused[:top]]
```

Perhatikan: dokumen dengan skor kata kunci 0 dikeluarkan dari daftar kata kunci (sama sekali tidak cocok), sehingga kecocokan vektor-saja tetap ditemukan, dan kecocokan kata-kunci-saja tetap masuk.

### 5. Hybrid search di dalam PostgreSQL

PostgreSQL punya **full-text search** bawaan: simpan `tsvector` dari teks, indeks dengan GIN, kueri dengan `websearch_to_tsquery`.

```sql
ALTER TABLE chunks
  ADD COLUMN tsv tsvector GENERATED ALWAYS AS (to_tsvector('simple', content)) STORED;
CREATE INDEX chunks_tsv_idx ON chunks USING gin (tsv);
```

Konfigurasi `'simple'` memecah menurut kata dan menjadikannya huruf kecil, tanpa stemming khusus bahasa. Ia bekerja untuk bahasa apa pun, termasuk Indonesia dan teks campuran, dan dapat diprediksi. (Konfigurasi khusus bahasa bisa membantu untuk bahasa Inggris; uji pada datamu.)

Satu query yang menjalankan kedua pencarian dan menggabungkannya dengan RRF:

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

Catatan:

- `$1` adalah vektor kueri, `$2` teks kueri, `$3` tenant. **Filter tenant ada di kedua pencarian**.
- `ts_rank_cd` adalah fungsi peringkat PostgreSQL; bukan persis BM25 tapi berperan sama. Kalau ingin BM25 sungguhan, pakai mesin pencari (OpenSearch, Elasticsearch) atau ekstensi, dan pertahankan ide fusi yang sama.
- Tiap sisi mengambil 20 teratas, sehingga fusi punya kolam yang baik. Jawaban akhirnya 5 teratas.

### 6. Opsional: re-ranking

Setelah fusi kamu punya daftar pendek (misalnya 30). **Re-ranker** membaca kueri bersama setiap kandidat dan menilai seberapa cocok. Lebih lambat dan lebih mahal, jadi terapkan hanya pada daftar pendek. Alasan umum menambahnya: tahap pertamamu menemukan chunk yang tepat tapi tidak di puncak, atau kuerimu panjang dan halus. Ukur manfaatnya; lewati kalau angkanya tidak membenarkan tambahan latency dan biaya.

### 7. Buktikan pada datamu

Jangan pernah berasumsi "hybrid lebih baik". Pakai set uji dari lesson sebelumnya dan bandingkan kueri yang sama dengan tiga cara:

| Mode | recall@5 | MRR |
|---|---|---|
| Vektor saja | ukur | ukur |
| Kata kunci saja | ukur | ukur |
| Hybrid (RRF) | ukur | ukur |

Lalu baca kueri tempat mode-mode **berbeda pendapat**. Kamu biasanya akan melihat pencarian kata kunci menyelamatkan kode dan nama, dan pencarian vektor menyelamatkan parafrase. Kalau hybrid tidak mengalahkan mode tunggal terbaik pada datamu, ada yang salah (tokenizer, filter, korpus kecil), atau kamu tak membutuhkannya.

Tambahkan beberapa **kueri adversarial** dengan sengaja: id persis, salah ketik, sinonim, pertanyaan dalam bahasa lain, dan negasi.

### Memilih caranya

| Situasi | Lakukan ini |
|---|---|
| User mencari dengan id, nama, kode, jargon | hybrid, atau minimal kata kunci + filter |
| User hanya bertanya bahasa alami | vektor saja mungkin cukup; uji hybrid tetap |
| Kueri multibahasa atau slang | konfigurasi full-text `'simple'` + model embedding multibahasa |
| Ingin fusi cepat tanpa penyetelan | RRF dengan k = 60 |
| Ingin mengendalikan keseimbangan | fusi berbobot, setel `alpha` pada set uji |
| Tahap pertama bagus di recall, buruk di urutan | tambahkan re-ranker pada 20–50 teratas |
| Korpus sangat besar dan kualitas kata kunci penting | mesin pencari dengan BM25 sungguhan di samping pgvector |

- ✅ Filter (tenant, izin) masuk ke **kedua** pencarian.
- ✅ Bandingkan vektor-saja, kata-kunci-saja dan hybrid pada set uji yang sama.
- 🚫 Menjumlahkan skor BM25 mentah dan cosine.
- 🚫 Mengira hybrid menang tanpa mengukur.

## ⚠️ Kesalahan umum

- Menjumlahkan skor dari skala berbeda (BM25 + cosine) tanpa penskalaan.
- Lupa filter tenant atau izin di salah satu dari dua pencarian.
- Menaruh kecocokan kata-kunci-saja (skor 0 di sisi lain) selamanya di bawah, sehingga tak pernah mencapai puncak.
- Memakai konfigurasi full-text khusus bahasa yang merusak teks Indonesia atau campuran.
- Kolam kandidat kecil (3 teratas dari tiap pencarian), sehingga fusi tak punya bahan.
- Menambah re-ranker tanpa mengukur manfaat dan latency-nya.
- Menyetel pada tiga kueri.

:::revoshop
Daftar lima jenis kueri pencarian RevoShop (SKU, nama merek, "sepatu murah untuk lari", salah ketik bahasa Indonesia, "bukan merah"). Untuk masing-masing, katakan apakah pencarian vektor, kata kunci atau keduanya akan menemukannya, dan apa yang dilakukan fusi.
:::

## 🏆 Praktik terbaik

- [ ] Mulai dengan vektor + kata kunci + RRF; ukur terhadap tiap bagian sendirian.
- [ ] Terapkan filter yang sama pada kedua pencarian.
- [ ] Ambil kolam kandidat yang cukup (20–50) dari tiap sisi sebelum fusi.
- [ ] Pakai konfigurasi full-text yang dapat diprediksi untuk bahasamu (`simple` awal yang aman).
- [ ] Tambahkan kueri adversarial (id, salah ketik, sinonim, bahasa lain, negasi) ke set uji.
- [ ] Tambahkan re-ranker hanya bila pengukuran membenarkan biayanya.
- [ ] Catat kueri tanpa hasil bagus dan tambahkan ke set uji.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan hybrid search dengan dua asisten. Kenapa RRF tidak butuh skor berada di skala yang sama?

## 📐 Rancang

Pencarian CareerPilot harus menemukan pekerjaan lewat teks bebas. User mengetik "backend python remote", "kerja data analyst jakarta", "JOB-48213", dan "sesuatu dengan Go tapi bukan Java". Lowongan berbahasa Indonesia dan Inggris; ada 200.000, dan tiap user juga bisa memfilter kota dan gaji. Rancang pencariannya: pengindeksan, alur kueri, fusi, filter, evaluasi, dan kueri mana yang kamu perkirakan tetap sulit.

:::quiz
Tampilkan rancangan yang mungkin

- **Pengindeksan:** tiap lowongan mendapat `tsvector` atas judul + perusahaan + skill + deskripsi (config `simple`), indeks GIN, dan embedding dari judul + skill + deskripsi yang dipangkas dengan model multibahasa. Filter (kota, rentang gaji, remote, tanggal posting) adalah kolom biasa dengan indeks B-tree.
- **Alur kueri:** normalisasi teks; deteksi pola id (`JOB-\d+`) dan jawab dengan lookup langsung lebih dulu; jalankan pencarian vektor dan kata kunci paralel, masing-masing dengan filter terstruktur di SQL; ambil 30 teratas dari tiap sisi; gabungkan dengan RRF; kembalikan 10 teratas. Opsional re-rank 30 teratas dengan re-ranker.
- **Filter:** "jakarta" bisa jadi kata teks bebas *dan* filter kota. Ekstrak kota dan kata gaji yang dikenal menjadi filter (aturan atau model kecil) dan tetap tinggalkan kata itu di kueri kata kunci.
- **"Go tapi bukan Java":** kedua sisi tak paham negasi dengan baik. Tangani dengan aturan yang mengurai "bukan X" menjadi filter pengecualian pada skill, atau biarkan model menulis ulang kueri menjadi teks plus filter.
- **Evaluasi:** 150 kueri nyata dengan id pekerjaan yang benar, termasuk id, slang, campuran Inggris-Indonesia dan negasi. Bandingkan vektor-saja, kata-kunci-saja dan hybrid pada recall@10 dan MRR; baca perbedaan pendapat.
- **Kasus sulit yang diperkirakan:** negasi, kueri sangat pendek ("data"), perbandingan gaji ("di atas 15 juta"), dan kata ambigu ("Go" bahasa vs kata kerja). Redam dengan penulisan ulang kueri, filter dan UI yang jelas.
- **Operasional:** pantau kueri tanpa hasil; re-index saat lowongan berubah; simpan nama model embedding di tabel.

**Aturan yang ditunjukkan:** tiap metode retrieval menutup kelemahan yang lain, filter terstruktur dan aturan menutup apa yang tak dipahami keduanya, dan set uji memberi tahu kombinasi mana yang dirilis.
:::

### 📝 Daftar cek diri

- [ ] Kedua pencarian menerapkan filter yang sama
- [ ] Fusi tak butuh penskalaan skor (RRF) atau sudah disetel (berbobot)
- [ ] Id persis punya jalur langsung
- [ ] Vektor-saja, kata-kunci-saja dan hybrid dibandingkan

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m7/w3/04-hybrid-search" ai="no-ai" title="BM25 dan fusi"}
Tulis `tokenize`, `bm25_scores` (rumus di atas), `reciprocal_rank_fusion`, `min_max`, `weighted_fusion` dan `hybrid_search`. Tes mencakup kueri id persis yang terlewat oleh pencarian vektor pura-pura, dan kueri sinonim yang terlewat oleh pencarian kata kunci. Tak perlu API key.
:::

:::hints
- `idf = math.log(1 + (N - n_t + 0.5) / (n_t + 0.5))`; lewati term kueri yang tak muncul di dokumen mana pun.
- Hitung tiap term kueri yang berbeda sekali: loop `set(tokenize(query))`.
- `reciprocal_rank_fusion`: `1 / (k + position)` dengan posisi mulai dari 1; urutkan menurut `(-score, id)`.
- `min_max`: jika semua nilai sama kembalikan `1.0` untuk masing-masing.
- `hybrid_search`: buang dokumen ber-BM25 nol, lalu gabungkan `[keyword_ids, vector_ranking]`.
:::

## ✅ Cek cepat

:::quiz
Kenapa tidak bisa langsung menjumlahkan skor BM25 dan cosine similarity?

Keduanya di skala berbeda (BM25 tak terbatas dan bergantung pada korpus; cosine di antara −1 dan 1), jadi satu akan mendominasi. Pakai fusi berbasis peringkat (RRF), atau skalakan tiap skor lebih dulu (misalnya min-max) dan campur dengan bobot.
:::

:::quiz
User mencari "pesanan A9731" dan pencarian vektor menaruh halaman pesanan di peringkat 9. Apa yang dilakukan hybrid search?

Pencarian kata kunci menemukan token A9731 persis dan menaruh halaman itu di peringkat 1. Di peringkat gabungan, halaman itu mendapat kontribusi reciprocal-rank tinggi dari daftar kata kunci dan kecil dari daftar vektor, sehingga naik ke puncak.
:::

:::quiz
Kenapa filter tenant harus ada di pencarian vektor dan pencarian kata kunci?

Tiap pencarian mengembalikan daftar kandidatnya sendiri. Jika salah satunya tidak difilter, ia bisa menarik chunk tenant lain ke hasil gabungan. Aturan akses harus berlaku di setiap jalur retrieval.
:::

## 📚 Lanjut belajar

- [PostgreSQL: Full text search](https://www.postgresql.org/docs/current/textsearch.html)
- [Elastic: A Comprehensive Guide to BM25](https://www.elastic.co/blog/practical-bm25-part-2-the-bm25-algorithm-and-its-variables)
- [Cormack et al.: Reciprocal Rank Fusion (paper)](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)

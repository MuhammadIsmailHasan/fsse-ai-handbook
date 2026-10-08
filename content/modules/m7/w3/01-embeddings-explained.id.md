---
title: "Embeddings Explained Simply"
summary: "Pahami bagaimana teks menjadi angka yang menangkap makna — vektor, kemiripan (cosine, dot, jarak), cara mendapat embedding, apa yang tak bisa dilakukannya, dan kebiasaan (model sama, batching, versi) yang menjaga sistem pencarian tetap sehat."
sourceHash: 7ca64663b7b5
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa itu **embedding**, dengan kata sederhana
- Bagaimana **kemiripan** dua embedding diukur (cosine, dot product, jarak)
- Cara **mendapatkan** embedding dan apa yang perlu diperhatikan (model, dimensi, batching, biaya)
- Apa yang **dikuasai** dan **lemah** pada embedding
- Kebiasaan yang menjaga sistem embedding tetap **konsisten**

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Embedding** | Daftar angka yang mewakili makna sebuah teks (atau gambar) |
| **Vektor** | Daftar angka itu; sebuah titik atau panah di ruang |
| **Dimensi** | Berapa banyak angka dalam vektor (misalnya 768 atau 1536) |
| **Cosine similarity** | Seberapa searah dua vektor (−1 sampai 1) |
| **Dot product** | Kalikan angka yang berpasangan lalu jumlahkan |
| **Jarak Euclid** | Jarak garis lurus antara dua titik |
| **Nearest neighbours** | Vektor tersimpan yang terdekat dengan vektor kueri |
| **Model embedding** | Model yang mengubah teks menjadi vektor |

## 🧠 Ide besarnya

Bayangkan **peta raksasa tentang makna**. Setiap kalimat adalah sebuah pin di peta. "Bagaimana cara reset password?" dan "Aku lupa login" adalah pin yang berada **tepat bersebelahan**. "Pengiriman ke Surabaya butuh tiga hari" adalah pin yang jauh, di lingkungan lain.

Model embedding adalah **pembuat peta**: ia mengambil teks apa pun dan memberitahumu koordinatnya. Koordinatnya bukan dua angka seperti di peta kertas. Ia ratusan atau ribuan angka, karena makna punya banyak arah (topik, nada, bahasa, keformalan, ...). Tapi idenya sama: **dekat di peta = mirip maknanya**.

Jadi "temukan teks yang bermakna mirip" menjadi "temukan pin terdekat dengan pin ini": matematika sederhana.

## ❓ Kenapa ini penting

Pencarian kata kunci hanya mencocokkan **kata**. Pelanggan yang mengetik "tidak bisa masuk" tak akan cocok dengan artikel berjudul "Mengatur ulang kata sandi". Embedding membuat sistem pencarian mencocokkan **makna**, bahkan lintas kata berbeda, dan sering lintas bahasa.

Itu yang menggerakkan:

- **semantic search** (minggu ini),
- **RAG**: menemukan bagian yang tepat untuk diberikan ke model (minggu depan),
- **rekomendasi** dan "item serupa",
- **deduplikasi** dan **clustering** (kelompokkan tiket support yang mirip),
- **klasifikasi** dengan sedikit contoh (apakah pesan ini soal tagihan atau pengiriman?).

Dan murah: panggilan embedding berbiaya sebagian kecil dari panggilan chat, dan kebanyakan dikerjakan sekali, saat kamu mengindeks dokumen.

## 📖 Langkah demi langkah

### 1. Dari teks ke vektor

Model embedding mengembalikan daftar angka berukuran tetap untuk teks apa pun.

```python
vector = embed("How do I reset my password?")
len(vector)      # for example 1024: the model's dimension, always the same
vector[:3]       # [0.021, -0.113, 0.067]  (small numbers, usually between -1 and 1)
```

Kamu tak bisa membaca angkanya. Tak ada satu angka pun yang berarti "password". Hanya **hubungan** antar vektor yang berguna.

Untuk belajar dan tes kamu bisa membuat **embedder mainan** tanpa model, dengan meng-hash kata ke dalam keranjang:

```python
import hashlib, re

def hash_embed(text, dim=64):
    vector = [0.0] * dim
    for token in re.findall(r"[a-z0-9]+", text.lower()):
        h = int(hashlib.sha256(token.encode()).hexdigest(), 16)
        vector[h % dim] += 1.0 if (h >> 20) & 1 else -1.0
    return normalize(vector)
```

Ia hanya tahu **kata yang sama**. Model sungguhan tahu bahwa "sign in" dan "log on" berdekatan. Tapi mainan ini menunjukkan seluruh alur (simpan, bandingkan, urutkan) dan jalan offline.

### 2. Mengukur "dekat": cosine, dot product, jarak

Tiga cara membandingkan dua vektor `a` dan `b`:

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

| Ukuran | Dibaca sebagai | Catatan |
|---|---|---|
| **Cosine similarity** | sudut antar panah. 1 = searah, 0 = tak berhubungan, −1 = berlawanan | mengabaikan panjang; pilihan umum untuk teks |
| **Dot product** | sudut **dan** panjang sekaligus | vektor lebih besar menang; tak masalah bila vektor dinormalisasi |
| **Jarak Euclid** | jarak garis lurus | lebih kecil = lebih dekat |

Kalau kamu **menormalisasi** setiap vektor ke panjang 1 lebih dulu, cosine similarity dan dot product memberi **urutan yang sama**, dan dot product lebih cepat. Banyak model embedding sudah mengembalikan vektor ternormalisasi; cek dokumentasi modelmu.

```python
cosine([1, 2], [2, 4])      # 1.0   same direction, different length
cosine([1, 0], [0, 1])      # 0.0   unrelated
cosine([1, 0], [-1, 0])     # -1.0  opposite
```

Catatan praktis: skor hanya bermakna **dalam satu model**. Cosine 0,8 dari model A tidak sebanding dengan 0,8 dari model B, dan tak ada ambang "bagus" yang universal. Temukan milikmu dengan melihat contoh nyata.

### 3. Nearest neighbours

Untuk mencari: embed kueri, bandingkan dengan setiap vektor tersimpan, dan kembalikan beberapa terbaik.

```python
def top_k(query, items, k, metric="cosine"):
    score = {"cosine": lambda v: cosine(query, v),
             "dot": lambda v: dot(query, v),
             "euclidean": lambda v: -euclidean(query, v)}[metric]
    scored = [(item_id, score(vector)) for item_id, vector in items]
    scored.sort(key=lambda pair: (-pair[1], pair[0]))      # higher is better; ties by id
    return scored[:k]
```

Dengan beberapa ribu item, loop brute-force ini cukup. Dengan jutaan kamu butuh **indeks** yang hanya mengecek vektor yang menjanjikan (lesson berikutnya).

### 4. Mendapatkan embedding di proyek nyata

| Sumber | Catatan |
|---|---|
| **API embedding penyedia** | kirim teks, dapat vektor. Beberapa perusahaan LLM tidak membuat model embedding sendiri dan merekomendasikan mitra; yang lain menawarkannya. Bandingkan kualitas, bahasa, dimensi dan harga. |
| **Model terbuka yang kamu jalankan sendiri** | misalnya lewat sentence-transformers atau Ollama. Gratis per panggilan, data tetap padamu, butuh perangkat keras. |

Mana pun yang kamu pilih, tulis pembungkus kecil agar sisa kodemu tidak peduli:

```python
class Embedder:
    model = "some-embedding-model-v2"       # keep the exact name: you will store it
    dim = 1024

    def embed(self, texts: list[str]) -> list[list[float]]:
        """Return one vector per text, in the same order."""
        ...
```

Hal yang dicek saat memilih model:

- **Bahasa.** Apakah bagus untuk bahasa Indonesia, dan teks campuran Indonesia-Inggris? Uji dengan contohmu sendiri.
- **Dimensi.** Dimensi lebih banyak bisa berarti kualitas lebih baik tapi penyimpanan lebih besar dan pencarian lebih lambat. Beberapa model membiarkanmu memperpendek vektor.
- **Panjang masukan maksimum.** Teks lebih panjang dipotong atau ditolak, salah satu alasan kita membuat chunk.
- **Kueri vs dokumen.** Beberapa model ingin awalan atau pengaturan berbeda untuk *kueri* dibanding *dokumen*. Baca dokumentasinya.
- **Harga dan rate limit.**

### 5. Kebiasaan baik

- **Satu model untuk kedua sisi.** Dokumen dan kueri harus di-embed oleh **model yang sama** (versi sama). Vektor dari model berbeda hidup di peta berbeda dan tak bisa dibandingkan.
- **Simpan nama model** (dan versi) di samping setiap vektor. Saat berganti model, kamu harus **meng-embed ulang semuanya**; nama tersimpan memberi tahu apa yang basi.
- **Batch** panggilanmu (banyak teks per request) saat mengindeks. Lebih cepat dan lebih murah per teks. Hormati rate limit dan retry saat error.
- **Embed sekali, pakai ulang.** Cache embedding dengan hash teks, supaya teks yang tak berubah tak dibayar dua kali.
- **Bersihkan teks** sedikit: buang menu, header berulang, boilerplate yang membuat setiap chunk tampak sama.
- **Simpan dimensi di schema** (`vector(1024)`), supaya vektor berukuran salah gagal dengan keras.
- **Perhatikan privasi.** Teks yang kamu embed lewat API dikirim ke penyedia. Embedding bisa membocorkan bagian dari teks asalnya, jadi lindungi seperti teksnya.

### 6. Apa yang dikuasai embedding, dan apa yang tidak

| Dikuasai | Lemah |
|---|---|
| makna mirip dengan kata berbeda | hal persis: id, kode, nama, angka (`A9731`) |
| menemukan bagian terkait di tumpukan besar | **negasi**: "bisa refund" dan "tidak bisa refund" sangat dekat |
| bekerja lintas bahasa (dengan model multibahasa) | logika dan perbandingan presisi ("di bawah 100.000") |
| mengelompokkan dan merekomendasikan | kueri sangat pendek atau sangat samar |
| | kesegaran: ia tak tahu apa pun yang belum kamu indeks |

Kolom kedua itulah kenapa sistem nyata menggabungkan embedding dengan pencarian kata kunci dan filter (lesson 4) dan membiarkan model bahasa membaca teks hasil retrieval sebelum menjawab (minggu depan).

### Memilih caranya

| Kebutuhan | Lakukan ini |
|---|---|
| Mencocokkan makna, bukan hanya kata | embedding + cosine similarity |
| Beberapa ribu item | pencarian brute-force di memori cukup |
| Jutaan item | indeks vektor (lesson berikutnya) |
| Id, nama, kode persis | tambahkan pencarian kata kunci (lesson 4) |
| Data privat atau offline | model terbuka yang kamu jalankan sendiri |
| Mengganti model embedding | embed ulang semuanya; simpan nama model |
| Memilih ambang | lihat pasangan nyata dari datamu; jangan menyalin angka dari blog |

- ✅ Model sama untuk dokumen dan kueri; simpan nama model.
- ✅ Uji pada bahasa dan dokumenmu sendiri.
- 🚫 Membandingkan vektor dari model berbeda.
- 🚫 Memercayai kemiripan tinggi sebagai "ini jawaban yang benar".

## ⚠️ Kesalahan umum

- Meng-embed kueri dengan satu model dan dokumen dengan model lain.
- Lupa menormalisasi (atau tak tahu apakah model sudah melakukannya).
- Memakai satu ambang kemiripan tetap untuk semua kueri dan model.
- Meng-embed dokumen 40 halaman sebagai satu vektor.
- Mengharapkan embedding menangani "tidak", angka atau kode persis.
- Meng-embed ulang teks yang tak berubah di setiap deploy.
- Tidak menyimpan model mana yang membuat vektor mana.

:::revoshop
Pilih sepuluh nama atau deskripsi produk RevoShop nyata. Untuk tiga pasang, prediksikan apakah model embedding bagus akan menaruhnya dekat (misalnya "sepatu lari pria" dan "men's running shoes") atau jauh, dan katakan apa yang akan dilakukan pencarian kata kunci pada pasangan yang sama. Di mana kode produk persis akan merusak pencarian embedding murni?
:::

## 🏆 Praktik terbaik

- [ ] Pakai satu model embedding per indeks, untuk dokumen dan kueri, dan simpan namanya.
- [ ] Evaluasi model pada teks dan bahasamu sendiri sebelum memilih.
- [ ] Normalisasi vektor (atau tahu bahwa model sudah melakukannya) dan pilih satu metrik.
- [ ] Batch dan cache panggilan embedding; simpan hash teks.
- [ ] Perlakukan skor kemiripan sebagai relatif dalam satu model; atur ambang dengan contoh nyata.
- [ ] Rencanakan embed ulang saat model atau chunking berubah.
- [ ] Gabungkan dengan pencarian kata kunci dan filter untuk istilah persis.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan embedding dengan gambaran peta makna. Kenapa kamu tak bisa membandingkan vektor dari model A dengan vektor dari model B?

## 📐 Rancang

CareerPilot ingin fitur "pekerjaan serupa": untuk pekerjaan yang disimpan user, tampilkan lima lowongan serupa dari database 200.000 lowongan dalam bahasa Indonesia dan Inggris. Rancang data yang disimpan, bagaimana dan kapan meng-embed, bagaimana mencari, bagaimana mengecek kualitas, dan apa yang dilakukan saat kamu mengganti model embedding tahun depan.

:::quiz
Tampilkan rancangan yang mungkin

- **Apa yang di-embed:** teks pendek yang dibersihkan per lowongan: judul + perusahaan + skill utama + deskripsi yang dipangkas (bukan seluruh halaman boilerplate). Simpan hash teks itu.
- **Model:** model embedding multibahasa, dipilih dengan menguji 30 pasang nyata (Indonesia-Indonesia, Inggris-Inggris, Indonesia-Inggris) dan mengecek kualitas, dimensi dan harga.
- **Penyimpanan:** tabel dengan `job_id`, hash teks, vektor, `embedding_model`, `embedded_at`, dan metadata (bahasa, lokasi, senioritas, tanggal posting).
- **Kapan:** embed lowongan baru dalam batch oleh job latar belakang; embed ulang hanya saat hash berubah; cache menurut hash.
- **Pencarian:** embed pekerjaan yang disimpan (atau pakai ulang vektor tersimpannya), ambil nearest neighbours dengan indeks, **filter** menurut kebaruan dan lokasi, buang pekerjaan itu sendiri dan duplikat mirip, lalu kembalikan lima.
- **Kualitas:** set kecil pekerjaan dengan "kecocokan bagus" pilihan manual; ukur recall@5; lihat yang meleset; kumpulkan klik user nanti.
- **Hybrid:** gabungkan dengan kecocokan kata kunci pada skill atau judul persis saat user mencari dengan istilah spesifik.
- **Ganti model tahun depan:** tambahkan vektor model baru di **kolom atau tabel baru** (`embedding_model` berbeda), bangun indeks baru di latar belakang, bandingkan kualitas pada set uji yang sama, alihkan lalu lintas, lalu buang yang lama. Jangan pernah mencampur model dalam satu indeks.
- **Privasi:** lowongan bersifat publik; catatan user tidak, jadi embed itu hanya dengan penyedia yang disetujui atau model lokal.

**Aturan yang ditunjukkan:** embedding murah dibuat dan mahal diganti, jadi versikan sejak hari pertama.
:::

### 📝 Daftar cek diri

- [ ] Dokumen dan kueri memakai model yang sama
- [ ] Nama model disimpan bersama setiap vektor
- [ ] Kualitas diukur pada contoh nyata berbahasa lokal
- [ ] Ada rencana untuk mengganti model

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m7/w3/01-embedding-basics" ai="no-ai" title="Vektor, kemiripan dan nearest neighbours"}
Tulis `dot`, `norm`, `normalize`, `cosine`, `euclidean`, `hash_embed` deterministik (meng-hash kata ke keranjang) dan `top_k` dengan tiga metrik (skor lebih tinggi selalu lebih baik; seri menurut id). Tak perlu API key atau model.
:::

:::hints
- `cosine = dot / (norm_a * norm_b)`; kembalikan `0.0` bila salah satu norm 0; `raise ValueError("dimension mismatch")` untuk panjang berbeda.
- `hash_embed`: `re.findall(r"[a-z0-9]+", text.lower())`; pakai `hashlib.sha256(token.encode())`, **bukan** `hash()` Python.
- Indeksnya `h % dim`; tandanya `+1` jika `(h >> 20) & 1` selain itu `-1`; kembalikan `normalize(vector)`.
- `top_k`: untuk "euclidean" pakai `-distance` sebagai skor, lalu urutkan menurut `(-score, id)`.
:::

## ✅ Cek cepat

:::quiz
Kenapa cosine similarity mengabaikan panjang vektor, dan kenapa itu berguna?

Cosine hanya mengukur sudut antar vektor, jadi vektor dan salinan yang diskalakan dianggap "sama". Untuk teks ini berguna karena arah membawa makna, sementara panjang bisa bervariasi karena alasan yang tak berhubungan.
:::

:::quiz
Kamu pindah ke model embedding yang lebih baru tapi menyimpan vektor lama. Apa yang salah?

Vektor kueri baru dan vektor dokumen lama berasal dari "peta" berbeda, jadi kemiripannya tidak bermakna dan kualitas pencarian runtuh (sering diam-diam). Embed ulang semua dokumen dengan model baru, atau simpan dua indeks terpisah dan alihkan bersama.
:::

:::quiz
Kenapa pencarian embedding murni cara yang buruk untuk menemukan nomor pesanan A9731?

Embedding menangkap makna, bukan string persis. Kode tidak punya makna untuk dicocokkan, dan kode yang tampak mirip bisa dekat atau jauh secara tak terduga. Id persis butuh pencarian kata kunci atau lookup database, sering digabung dengan embedding dalam hybrid search.
:::

## 📚 Lanjut belajar

- [Anthropic docs: Embeddings](https://platform.claude.com/docs/en/build-with-claude/embeddings)
- [Sentence-Transformers documentation](https://www.sbert.net/)
- [Jay Alammar: The Illustrated Word2vec](https://jalammar.github.io/illustrated-word2vec/)

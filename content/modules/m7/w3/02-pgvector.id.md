---
title: "pgvector in PostgreSQL"
summary: "Simpan embedding di samping data biasamu di PostgreSQL — kolom vector dan operator jarak, pencarian eksak vs indeks HNSW dan IVFFlat, filter metadata, mengukur recall, dan kapan database vektor khusus layak dipakai."
sourceHash: 2e3aa8c454c0
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa itu **pgvector**, dan kenapa banyak tim memulai dengannya
- **Kolom `vector`** dan tiga operator jarak
- Pencarian **eksak** vs indeks **perkiraan** (**HNSW**, **IVFFlat**)
- **Filter metadata** bersama pencarian vektor
- Cara **mengukur recall** dan menyetel kecepatan terhadap akurasi
- Kapan tetap di PostgreSQL, dan kapan pindah ke database vektor khusus

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **pgvector** | Ekstensi PostgreSQL yang menambah tipe vektor dan pencarian vektor |
| **Kolom vektor** | Kolom yang menyimpan embedding, seperti `vector(1024)` |
| **Operator jarak** | Simbol seperti `<=>` yang mengukur seberapa jauh dua vektor |
| **ANN** | Approximate nearest neighbours: pencarian cepat yang mungkin melewatkan beberapa |
| **HNSW** | Indeks yang dibangun sebagai lapisan tetangga yang terhubung |
| **IVFFlat** | Indeks yang mengelompokkan vektor ke klaster dan hanya mencari beberapa |
| **Recall** | Berapa banyak tetangga terdekat sebenarnya yang ditemukan indeks |
| **Pre/post-filter** | Menerapkan filter metadata sebelum atau sesudah pencarian vektor |

## 🧠 Ide besarnya

Kamu sudah punya **perpustakaan dengan katalog**: tabel PostgreSQL-mu, berisi user, pesanan dan dokumen. pgvector menambah jenis rak baru tempat buku disusun **menurut makna**. Bertanya "tunjukkan lima buku seperti ini" butuh satu query, di gedung yang sama, dengan pustakawan yang sama, backup yang sama dan aturan keamanan yang sama.

Alternatifnya membangun **perpustakaan kedua** (database vektor terpisah) dan menjaganya tetap sinkron dengan yang pertama. Kadang itu pilihan yang tepat. Sering itu kerja tambahan tanpa alasan.

## ❓ Kenapa ini penting

Kebanyakan fitur AI butuh tiga hal bersamaan: **teksnya**, **vektornya**, dan **data biasa untuk memfilter** (pelanggan, bahasa, tanggal, izin). Menyimpan semuanya dalam satu database PostgreSQL memberi:

- **transaksi**: dokumen dan vektornya disimpan atau dihapus bersama,
- **join dan filter**: "artikel serupa, hanya untuk tenant 7, terbit tahun ini",
- **satu sistem** untuk dijalankan, di-backup, dipantau dan diamankan,
- alat yang sudah kamu kenal: SQL, migrasi, psycopg, SQLAlchemy.

Untuk banyak produk, sampai jutaan vektor, ini cukup dan sederhana.

## 📖 Langkah demi langkah

### 1. Jalankan PostgreSQL dengan pgvector

Image PostgreSQL standar tidak menyertakan ekstensinya. Pakai image yang menyertakannya, di port tak bawaan agar tidak bentrok dengan database lain di mesinmu:

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

Lalu, sekali per database:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

Di layanan terkelola (RDS, Cloud SQL, Supabase, Neon, ...) ekstensi biasanya tersedia; kamu mengaktifkannya dengan pernyataan yang sama.

### 2. Tabel dengan kolom vektor

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

Angka di `vector(1024)` adalah **dimensi**. Vektor berukuran lain ditolak, persis yang kamu inginkan. Simpan nama model di kolom.

Masukkan dari Python (psycopg 3 dengan paket pembantu `pgvector`):

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

### 3. Cari dengan operator jarak

pgvector memberimu operator; **jarak lebih kecil berarti lebih dekat**:

| Operator | Jarak | Dipakai dengan |
|---|---|---|
| `<->` | Euclid (L2) | umum |
| `<=>` | **jarak cosine** (1 − cosine similarity) | kebanyakan embedding teks |
| `<#>` | inner product **negatif** | vektor ternormalisasi, tercepat |

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

Tanpa indeks ini adalah pencarian **eksak**: PostgreSQL menghitung jarak ke setiap baris. Ia selalu benar, dan untuk puluhan ribu baris cukup cepat. Mulailah di sini. Tambah indeks saat mulai lambat.

### 4. Indeks perkiraan: HNSW dan IVFFlat

Untuk banyak baris, indeks hanya mengecek kandidat yang menjanjikan. Ia **perkiraan**: bisa melewatkan tetangga sebenarnya (**recall** lebih rendah) sebagai ganti kecepatan. Kompromi yang sama dengan indeks hyperplane acak yang kamu bangun di latihan.

**HNSW**: graf tetangga berlapis. Recall dan kecepatan bagus, lebih lambat dan lebih besar dibangun, bisa dibuat di tabel kosong. Pilihan pertama yang umum.

```sql
CREATE INDEX chunks_embedding_hnsw
ON chunks USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

SET hnsw.ef_search = 100;      -- per session: bigger = better recall, slower queries
```

**IVFFlat**: mengelompokkan vektor ke klaster (`lists`) dan hanya mencari beberapa terdekat (`probes`). Lebih cepat dibangun dan lebih kecil, recall sedikit lebih rendah. Bangun **setelah** memuat data, karena klaster berasal dari baris yang ada.

```sql
CREATE INDEX chunks_embedding_ivf
ON chunks USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

SET ivfflat.probes = 10;       -- bigger = better recall, slower queries
```

Aturan:

- Kelas operator indeks harus cocok dengan operator yang kamu pakai untuk query: `vector_cosine_ops` ↔ `<=>`, `vector_l2_ops` ↔ `<->`, `vector_ip_ops` ↔ `<#>`. Kalau tidak, PostgreSQL mengabaikan indeks dan melakukan scan eksak.
- Lihat `EXPLAIN ANALYZE` untuk memastikan indeks dipakai.
- Ada batas jumlah dimensi `vector` yang diindeks (sekitar 2.000); untuk model lebih besar pakai dimensi keluaran lebih kecil atau tipe setengah-presisi.
- Indeks memakai memori dan disk, dan membangunnya butuh waktu. Rencanakan.

### 5. Filter metadata: bagian yang licin

Query nyata memfilter: "hanya tenant 7, hanya bahasa Indonesia, hanya yang terbit".

```sql
SELECT id, content
FROM chunks
WHERE tenant_id = 7 AND lang = 'id'
ORDER BY embedding <=> $1
LIMIT 5;
```

Dengan indeks perkiraan ada jebakan: indeks menemukan kandidat terdekat lebih dulu, dan filter membuang sebagian sesudahnya. Kalau filtermu sangat selektif (tenant 7 memiliki 0,1% baris), kamu bisa mendapat **kurang dari 5 hasil**, atau yang lebih buruk. Obatnya:

- naikkan `hnsw.ef_search` (atau `ivfflat.probes`) agar indeks melihat lebih banyak kandidat,
- pakai opsi pgvector yang lebih baru untuk pemindaian iteratif, jika versimu punya,
- buat **indeks biasa** pada kolom filter (`tenant_id`) agar PostgreSQL bisa memilih memfilter dulu lalu scan eksak pada set kecil,
- untuk kelompok yang terpisah kuat, pakai **partisi** atau **partial index per tenant**,
- dan selalu **uji dengan filter nyatamu**.

Kasus aman yang sangat umum: tiap tenant punya jumlah chunk sedang, jadi "filter per tenant, lalu pencarian eksak" cepat dan sangat akurat.

Izin juga masuk di filter. User hanya boleh mengambil chunk yang boleh ia lihat: taruh aturan akses di `WHERE`, bukan di prompt.

### 6. Ukur recall

Jangan pernah menerima indeks perkiraan begitu saja. Bandingkan dengan jawaban eksak pada kueri nyata:

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

Jalankan 100–200 kueri nyata dua cara, rata-ratakan recall@10, dan catat latency. Kalau recall 0,99 pada 5 ms, bagus. Kalau 0,8, naikkan `ef_search`/`probes` atau parameter indeks, dan ukur lagi. Begitulah kamu memilih pengaturan dengan bukti.

### 7. Operasional sehari-hari

- **Upsert dan delete** bekerja seperti baris biasa: perbarui teks, perbarui vektor dalam transaksi yang sama. Hapus dokumen, hapus chunk-nya.
- **Embed ulang:** untuk mengganti model, tambahkan kolom (atau tabel) baru untuk vektor baru, backfill per batch, bangun indeks baru, alihkan query, buang kolom lama.
- **Ukuran:** vektor 1024 dimensi memakai sekitar 4 KB. Sejuta chunk sekitar 4 GB vektor sebelum indeks. Rencanakan memori agar indeks muat di RAM untuk kecepatan.
- **Backup, replika, migrasi:** sama seperti sisa databasemu.
- **Hybrid search:** PostgreSQL juga punya full-text search, jadi pencarian kata kunci dan vektor bisa ada dalam satu query (lesson 4).

### 8. pgvector atau database vektor khusus?

| Tetap dengan pgvector bila | Pertimbangkan database vektor khusus bila |
|---|---|
| kamu sudah menjalankan PostgreSQL | kamu punya ratusan juta vektor atau laju query sangat tinggi |
| kamu butuh join, filter, transaksi | kamu butuh fitur lanjutan (pencarian terfilter sangat cepat, sharding bawaan) pada skala besar |
| jutaan vektor, lalu lintas sedang | tim pencarian akan memilikinya penuh waktu |
| kamu ingin lebih sedikit sistem untuk dioperasikan | kamu menerima mengoperasikan dan menyinkronkan sistem lain |

Mulai sederhana. Pindah saat punya bukti (angka latency, biaya atau recall) bahwa kamu harus.

### Memilih caranya

| Situasi | Lakukan ini |
|---|---|
| Sampai ~50.000 chunk | pencarian eksak; tak perlu indeks vektor |
| Lebih banyak, dan recall penting | indeks HNSW; setel `ef_search`; ukur recall |
| Build cepat, memori lebih sedikit, memuat dataset besar | IVFFlat setelah memuat; setel `lists` dan `probes` |
| Filter per-tenant atau izin | filter di SQL; uji filter selektif; pertimbangkan partisi per-tenant |
| Mengganti model embedding | kolom/tabel baru, backfill, indeks baru, alihkan, buang yang lama |
| Butuh kata persis juga | tambahkan full-text search (lesson 4) |

- ✅ Simpan nama model; jaga dimensi di tipe kolom.
- ✅ Ukur recall dan latency dengan kueri nyata.
- 🚫 Memilih parameter indeks dari blog tanpa mengukur.
- 🚫 Mengecek izin di prompt, bukan di `WHERE`.

## ⚠️ Kesalahan umum

- Memakai operator atau kelas operator yang salah, sehingga indeks diam-diam diabaikan.
- Membuat indeks IVFFlat di tabel kosong.
- Lupa bahwa filter selektif ditambah indeks perkiraan bisa mengembalikan terlalu sedikit baris.
- Model (atau dimensi) berbeda dicampur dalam satu kolom.
- Tanpa kolom `embedding_model`, sehingga tak bisa tahu apa yang basi.
- Tidak pernah memeriksa `EXPLAIN ANALYZE`.
- Mengecek izin setelah retrieval, atau di prompt.
- Menjalankan database di port bawaan dengan kredensial bawaan di mesin bersama.

:::revoshop
RevoShop sudah punya PostgreSQL. Gambarkan tabel yang akan kamu tambah untuk mencari deskripsi produk menurut makna: kolomnya, dimensi vektor, indeks yang kamu mulai (dan kenapa), dan filter untuk "hanya produk yang ada stoknya". Berapa banyak produk yang dibutuhkan sebelum indeks jadi perlu?
:::

## 🏆 Praktik terbaik

- [ ] Mulai dengan pencarian eksak; tambah indeks saat pengukuran menyuruhnya.
- [ ] Cocokkan operator, kelas operator dan jarak yang kamu inginkan.
- [ ] Simpan `embedding_model` dan jaga dimensi di tipe.
- [ ] Taruh filter tenant dan izin di SQL, dan uji filter selektif.
- [ ] Ukur recall@k terhadap pencarian eksak sebelum dan sesudah menyetel.
- [ ] Jalankan `EXPLAIN ANALYZE` untuk memastikan indeks dipakai.
- [ ] Rencanakan embed ulang dengan kolom baru dan backfill latar belakang.
- [ ] Pakai port tak bawaan dan kredensial sungguhan; perlakukan vektor sesensitif teksnya.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan pgvector dengan gambaran perpustakaan dan katalog. Apa harga dari "perkiraan", dan apa yang kamu dapat sebagai gantinya?

## 📐 Rancang

SupportDesk AI menyimpan artikel bantuan untuk 40 perusahaan klien (tenant). Totalnya 800.000 chunk; tenant terbesar punya 200.000, terkecil 500. Setiap kueri hanya boleh melihat chunk tenant-nya sendiri. Latency harus di bawah 100 ms pada 50 kueri per detik. Rancang schema, strategi indeks dan filter, cara mengukur kualitas, dan cara menangani pergantian model tahun depan.

:::quiz
Tampilkan rancangan yang mungkin

- **Schema:** `chunks(id, tenant_id, article_id, lang, content, embedding vector(D), embedding_model, updated_at)` dengan indeks B-tree biasa pada `(tenant_id)`; `ON DELETE CASCADE` dari artikel.
- **Strategi:** karena ukuran tenant sangat berbeda, pilih menurut ukuran: tenant kecil (≤ ~20.000 chunk) bisa memakai "filter per tenant, lalu scan eksak" — eksak dan cepat; tenant besar mendapat indeks **HNSW**. Dua opsi untuk yang besar: partisi tabel berdasarkan `tenant_id` dan indeks tiap partisi besar secara terpisah (`WHERE tenant_id = ...` pada query memangkas ke satu partisi), atau satu indeks HNSW dengan `ef_search` dinaikkan dan pemindaian iteratif jika tersedia.
- **Selalu** taruh `WHERE tenant_id = $1` di SQL, jangan pernah mengandalkan app membuang baris tenant lain sesudahnya (itu aturan kontrol akses).
- **Kualitas:** 200 kueri berlabel per tenant besar dan 50 untuk yang kecil; hitung recall@10 terhadap pencarian eksak dan kualitas jawaban (ketercapaian artikel yang benar); setel `ef_search` sampai recall ≥ 0,95 dalam anggaran latency.
- **Latency:** `EXPLAIN ANALYZE` kueri nyata; jaga indeks HNSW di memori (ukur instance); connection pool; ukur p95 di bawah beban dengan tes 50 kueri per detik.
- **Ganti model:** tambahkan `embedding_v2` dan `embedding_model_v2`, backfill per batch per tenant, bangun indeks baru (concurrently), jalankan kueri berlabel di keduanya, alihkan per tenant, lalu buang kolom dan indeks lama.
- **Operasional:** job malam untuk menemukan chunk yang artikelnya berubah; hapus yatim; backup bersama sisa database; pantau ukuran indeks dan latency kueri.

**Aturan yang ditunjukkan:** pilih pencarian eksak saat datanya kecil, indeks saat besar, selalu filter di SQL, dan buktikan dengan angka recall dan latency.
:::

### 📝 Daftar cek diri

- [ ] Operator, kelas operator dan metrik sepakat
- [ ] Filter tenant ada di SQL
- [ ] Recall dan latency diukur pada kueri nyata
- [ ] Ada rencana embed ulang

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m7/w3/02-vector-store" ai="no-ai" title="Database vektor mini: eksak dan perkiraan"}
Bangun `VectorStore` (pencarian eksak dengan skor cosine, dot atau Euclid, pengecekan dimensi dan filter metadata yang diterapkan sebelum pengurutan), `LSHIndex` (hyperplane acak: hanya bucket kueri, dan opsional tetangga satu-bit, yang diberi skor) dan `recall_at_k`. Tes menunjukkan kompromi kecepatan vs recall yang akan kamu temui pada HNSW dan IVFFlat. Tak perlu database.
:::

:::hints
- `VectorStore.search`: filter dulu (`all(metadata.get(k) == v and k in metadata ...)`), lalu beri skor, lalu urutkan menurut `(-score, id)`.
- `LSHIndex`: `rng = random.Random(seed)`; bidang-bidangnya `[[rng.gauss(0, 1) for _ in range(dim)] for _ in range(planes)]`.
- Signature: tuple bit `1 if dot(vector, plane) >= 0 else 0`; kelompokkan id menurut signature di `__init__`.
- Menyelidiki tetangga: untuk tiap posisi bit buat signature dengan satu bit itu dibalik dan tambahkan bucket-nya.
- `recall_at_k`: `len(set(approx) & set(exact)) / len(exact)`, dengan `1.0` untuk daftar eksak kosong.
:::

## ✅ Cek cepat

:::quiz
Kenapa indeks perkiraan plus filter selektif bisa mengembalikan kurang dari k baris?

Indeks lebih dulu memilih kandidat terdekat dari semua baris, lalu filter `WHERE` membuang yang tidak cocok. Kalau filter hanya menyisakan porsi kecil baris, kebanyakan kandidat terbuang dan sedikit yang tersisa. Naikkan keluasan pencarian, filter dulu dengan indeks biasa, atau partisi datanya.
:::

:::quiz
Kamu membuat `vector_l2_ops` tapi query dengan `<=>`. Apa yang terjadi?

PostgreSQL tidak bisa memakai indeks itu untuk jarak cosine, jadi diam-diam kembali ke scan eksak. Hasilnya benar tapi lambat. Cocokkan kelas operator dengan operator dan konfirmasi dengan `EXPLAIN ANALYZE`.
:::

:::quiz
Kenapa mulai dengan pencarian eksak, bukan indeks HNSW?

Pencarian eksak selalu benar, tak butuh penyetelan dan cukup cepat untuk puluhan ribu baris. Indeks perkiraan menambah waktu build, memori dan kompromi recall, jadi tambahkan hanya saat pengukuran menunjukkan latency membutuhkannya.
:::

## 📚 Lanjut belajar

- [pgvector on GitHub](https://github.com/pgvector/pgvector)
- [pgvector-python](https://github.com/pgvector/pgvector-python)
- [PostgreSQL: EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html)

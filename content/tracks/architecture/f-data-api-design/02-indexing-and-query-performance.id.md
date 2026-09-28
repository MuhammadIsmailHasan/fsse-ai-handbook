---
title: "Indexing & Query Performance"
summary: Kenapa query yang sama bisa instan atau lambat menyakitkan — cara kerja index database seperti indeks di belakang buku, kapan composite index membantu, biaya tulis tiap index, dan cara membaca EXPLAIN untuk membuktikannya.
sourceHash: ab7ab87997b7
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa itu index dan kenapa ia membuat pencarian cepat
- Jenis default (B-tree) dan apa kelebihannya
- Index **komposit** dan kenapa urutan kolom penting
- Biaya tersembunyi: index memperlambat tulis dan memakan ruang
- Cara membaca `EXPLAIN` untuk melihat apakah index benar-benar dipakai
- Kolom mana yang harus di-index di aplikasi nyata seperti RevoShop

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Index** | Jalan pintas terurut yang disimpan database agar cepat menemukan baris |
| **Full table scan** | Membaca setiap baris untuk mencari yang cocok (lambat di tabel besar) |
| **B-tree** | Bentuk index default; menjaga kunci terurut untuk pencarian dan rentang cepat |
| **Index komposit** | Satu index atas beberapa kolom sekaligus |
| **Selektivitas** | Seberapa baik sebuah kolom mempersempit hasil (unik = tinggi) |
| **EXPLAIN** | Perintah yang menampilkan rencana yang akan dipakai database |
| **Covering index** | Index yang sudah memuat setiap kolom yang dibutuhkan query |

## 🧠 Ide besarnya

Index itu seperti **indeks di belakang buku**. Tanpa indeks, menemukan tiap penyebutan "Redis" berarti membaca 400 halaman (**full table scan**). Dengan indeks, kamu buka indeksnya, lihat "Redis … 88, 210", lalu langsung lompat ke sana.

Buku yang sama, kata yang sama — indeks hanya membuatmu bisa melewati halaman yang tidak mungkin cocok.

## ❓ Kenapa ini penting

Pada 100 baris, semuanya cepat, jadi pemula tak pernah sadar. Pada 5 juta baris, query tanpa index membaca kelima juta baris itu *setiap kali*, dan aplikasimu macet persis saat akhirnya punya pengguna.

Index mengubah "baca semua" menjadi "lompat ke tempat yang tepat". Tapi mereka tidak gratis, jadi tahu kolom *mana* yang harus di-index — dan membuktikannya dengan `EXPLAIN` — adalah skill backend inti.

## 📖 Langkah demi langkah

### 1. Masalahnya: full table scan

```sql
SELECT * FROM orders WHERE user_id = 42;
```

Tanpa index, database memeriksa **setiap** baris untuk melihat apakah `user_id = 42`. Pada tabel `orders` besar itu jutaan perbandingan untuk satu query.

### 2. Solusinya: sebuah index

```sql
CREATE INDEX idx_orders_user_id ON orders (user_id);
```

Kini database menyimpan nilai `user_id` secara **terurut** (sebuah **B-tree**). Untuk menemukan `42` ia melakukan pencarian cepat — seperti menemukan kata di kamus — alih-alih membaca semuanya. B-tree juga bagus untuk **rentang** (`created_at > '2026-01-01'`) dan **pengurutan**, karena nilainya sudah terurut.

### 3. Index komposit — urutan penting

**Index komposit** mencakup beberapa kolom sekaligus:

```sql
CREATE INDEX idx_orders_user_status ON orders (user_id, status);
```

Bayangkan buku telepon terurut berdasarkan **(nama belakang, nama depan)**. Ia membantumu menemukan "Hasan, Ismail" dan semua "Hasan" — tapi ia **tidak** membantumu menemukan semua orang bernama "Ismail", karena nama depan adalah kunci urut *kedua*.

Aturan: index komposit pada `(a, b)` membantu query yang menyaring `a`, atau `a` **dan** `b` — tapi bukan `b` sendirian. Taruh kolom yang selalu kamu saring **paling depan**.

### 4. Biaya tersembunyi: tulis jadi lebih lambat

Setiap index harus dijaga tetap terkini. Pada setiap `INSERT`, `UPDATE`, atau `DELETE`, database juga memperbarui tiap index dan memakai ruang disk tambahan.

| Lebih banyak index | Efek |
|---|---|
| Baca yang cocok dengan index | ⚡ jauh lebih cepat |
| Tulis (insert/update/delete) | 🐢 sedikit lebih lambat tiap kali |
| Pemakaian disk | 📈 bertambah |

Jadi kamu **tidak** meng-index setiap kolom "untuk jaga-jaga". Kamu meng-index kolom yang benar-benar kamu cari, join, atau urutkan.

### 5. Buktikan dengan EXPLAIN

Jangan pernah menebak apakah index dipakai — tanyakan:

```sql
EXPLAIN SELECT * FROM orders WHERE user_id = 42;
```

- `Seq Scan` → full table scan (tak ada index dipakai). Buruk di tabel besar.
- `Index Scan using idx_orders_user_id` → index-nya bekerja. 

Kalau kamu menambah index tapi masih melihat `Seq Scan`, ada yang salah (urutan kolom keliru, ada fungsi membungkus kolom, atau tabelnya sangat kecil sehingga planner sengaja melewati index).

### 6. Kemenangan cepat: covering index

Kalau sebuah index sudah memuat setiap kolom yang dibutuhkan query, database bisa menjawab dari index saja, tanpa menyentuh tabel:

```sql
-- This index can answer "statuses for a user" without reading the table rows
CREATE INDEX idx_orders_user_status ON orders (user_id, status);
SELECT status FROM orders WHERE user_id = 42;   -- covered
```

### Pilih apa yang di-index

| Situasi | Di-index? |
|---|---|
| Kolom di `WHERE`, `JOIN`, atau `ORDER BY` pada tabel besar | ✅ ya |
| Foreign key (`user_id`, `product_id`) | ✅ biasanya ya |
| Kolom dengan sedikit nilai berbeda (mis. `is_active` true/false) | ⚠️ jarang membantu — selektivitas rendah |
| Tabel banyak-tulis dengan kolom jarang dibaca | 🚫 jangan berlebihan index |
| Tabel lookup kecil | 🚫 tak perlu |

- ✅ Index kolom **selektivitas** tinggi yang kamu saring/join/urutkan.
- ✅ Untuk filter banyak kolom, pakai index komposit dengan kolom paling-sering-disaring di depan.
- 🚫 Jangan tambah index yang tak bisa kamu benarkan dengan query nyata.

## ⚠️ Kesalahan umum

- Menambah index tapi tak pernah cek `EXPLAIN` untuk melihat apakah dipakai.
- Urutan kolom keliru di index komposit, sehingga query tetap scan.
- Membungkus kolom dengan fungsi (`WHERE lower(email) = ...`) sehingga index biasa di `email` tak bisa dipakai.
- Meng-index segalanya, lalu bingung kenapa tulis jadi lambat dan disk penuh.
- Meng-index kolom boolean/sedikit-variasi dan berharap percepatan besar.

:::revoshop
Buka models/migration RevoShop. (1) Kolom mana yang paling sering di-query — `orders.user_id`, `order_items.order_id`, `products.category`? Apakah itu di-index? (2) Halaman "order saya" menyaring `user_id` dan mengurutkan `created_at`. Apakah index komposit `(user_id, created_at)` lebih membantu daripada dua index satu-kolom? Kenapa? (3) Kalau kamu jalankan `EXPLAIN` pada query order-per-user, apakah kamu melihat `Index Scan` atau `Seq Scan`?
:::

## 🏆 Praktik terbaik

- [ ] Index foreign key dan kolom yang kamu saring, join, dan urutkan.
- [ ] Buktikan tiap index dengan `EXPLAIN` pada jumlah data realistis — jangan menebak.
- [ ] Untuk filter banyak kolom, pilih urutan kolom index komposit berdasarkan apa yang kamu saring lebih dulu.
- [ ] Ingat tulis membayar untuk index; simpan hanya yang dibutuhkan query nyata.
- [ ] Hindari fungsi pada kolom ter-index di `WHERE`, atau tambah expression index yang cocok.
- [ ] Cek ulang index saat pola query berubah; buang yang tak dipakai query mana pun.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke teman, pakai analogi indeks-buku, kenapa menambah index membuat baca lebih cepat tapi tulis lebih lambat. Lalu jelaskan kenapa index komposit pada `(nama_belakang, nama_depan)` tidak membantu pencarian dengan nama depan saja.

## 📐 Rancang

Tabel `applications` CareerPilot punya jutaan baris. Tiga query terpanas adalah: (a) semua lamaran satu user, terbaru dulu; (b) semua lamaran dengan `status = 'interviewing'` untuk satu user; (c) hitungan harian global lamaran yang dibuat per hari. Rancang index yang akan kamu tambahkan, sebutkan kolom dan urutannya, dan katakan query mana yang dilayani tiap index. Catat query mana yang index-nya *tidak* banyak membantu.

:::quiz
Tampilkan satu rancangan yang mungkin

- (a) *lamaran user, terbaru dulu* → **komposit** `(user_id, created_at DESC)`. Menyaring `user_id` dan memberi urutan sort gratis — hampir jadi covering index untuk daftarnya.
- (b) *user + status* → index `(user_id, created_at)` yang sama sudah mempersempit per user; tambah `status` hanya bila filter status sering: `(user_id, status, created_at)`. Urutan kolom: `user_id` yang selalu-disaring di depan.
- (c) *hitungan harian global* → index di `created_at` membantu rentang/group per hari, tapi agregat harian penuh atas *semua* baris tetap bisa scan banyak; tabel ringkasan atau materialized view sering lebih baik daripada index di sini.

**Aturan yang ditunjukkan:** rancang index dari query panas nyata dan bentuk filter+sort-nya, bukan kolom per kolom. Beberapa query analitik butuh tabel ringkasan, bukan index.
:::

### 📝 Checklist review mandiri

- [ ] Tiap index memetakan ke query nyata yang disebutkan namanya
- [ ] Urutan kolom komposit cocok dengan filter (paling-disaring di depan)
- [ ] Biaya tulis diakui (tidak meng-index segalanya)
- [ ] Kasus di mana index tak membantu teridentifikasi

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/architecture/f-data-api-design/02-indexing" ai="no-ai" title="Bangun index kecil dan hitung kerjanya"}
Implementasikan pencarian linear yang memindai setiap baris (dan menghitung berapa yang disentuh) dan index kesetaraan (dict dari nilai → baris) yang menjawab query yang sama dengan menyentuh jauh lebih sedikit baris. Lalu bangun index komposit `(a, b)` dan tunjukkan ia bisa melayani query pada `a` sendirian tapi bukan pada `b` sendirian.
:::

:::hints
- `linear_search` mengembalikan `(matches, scanned)` di mana `scanned == len(rows)` tiap kali.
- `build_index(rows, field)`: dict yang memetakan tiap nilai ke daftar baris dengan nilai itu.
- Kunci komposit: pakai tuple `(row[a], row[b])`; untuk melayani "a sendirian", pindai kunci yang elemen pertamanya cocok.
:::

## ✅ Cek cepat

:::quiz
Kenapa menambah index membuat tulis lebih lambat?

Karena setiap insert, update, atau delete juga harus memperbarui tiap index (dan memakai ruang disk tambahan). Index mempercepat baca dengan biaya kecepatan tulis dan ruang, jadi kamu menambah hanya yang dibutuhkan query nyata.
:::

:::quiz
Sebuah index komposit ada di `(user_id, status)`. Mana yang dibantu: filter `user_id`; filter `status` saja; filter keduanya?

Ia membantu filter `user_id`, dan `user_id` **dan** `status` bersama, tapi bukan `status` saja — karena `status` adalah kunci urut kedua, seperti nama depan di buku telepon yang terurut nama belakang dulu.
:::

## 📚 Lanjut belajar

- [Use The Index, Luke — how indexes work](https://use-the-index-luke.com/)
- [PostgreSQL: Using EXPLAIN](https://www.postgresql.org/docs/current/using-explain.html)
- [PostgreSQL: Indexes](https://www.postgresql.org/docs/current/indexes.html)

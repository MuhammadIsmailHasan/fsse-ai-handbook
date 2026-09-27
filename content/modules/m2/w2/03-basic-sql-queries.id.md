---
title: "Kueri SQL Dasar: INSERT, SELECT, UPDATE, DELETE"
summary: Buat, baca, ubah, dan hapus data dengan aman — penyaring, pengurutan, penanganan NULL, fungsi peringkas dengan GROUP BY dan HAVING, serta kueri dengan parameter.
sourceHash: 0bce739b2efc
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Empat operasi di balik hampir setiap aplikasi: **C**reate, **R**ead, **U**pdate, **D**elete
- Menyaring data (`WHERE`, `LIKE/ILIKE`, `IN`, `BETWEEN`) dan mengurutkan (`ORDER BY`, `LIMIT`, `OFFSET`)
- Kenapa `NULL` itu istimewa
- Meringkas data dengan `COUNT`, `SUM`, `AVG`, `GROUP BY` dan `HAVING`
- Membuat `UPDATE`/`DELETE` aman, dan kenapa **parameterized query** mencegah SQL injection

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **CRUD** | Empat operasi dasar data: buat, baca, ubah, hapus |
| **Declarative** | Kamu bilang *apa* yang kamu mau; database mengurus *caranya* |
| **`WHERE`** | Penyaring yang memilih baris mana |
| **`NULL`** | "Tidak diketahui" — bukan nol, tidak sama dengan apa pun, bahkan dengan diri sendiri |
| **Aggregate** | Fungsi yang meringkas banyak baris (`COUNT`, `SUM`, `AVG`) |
| **`GROUP BY`** | Membuat satu baris hasil per kelompok |
| **`HAVING`** | Penyaring yang diterapkan *setelah* pengelompokan |
| **Pagination** | Menampilkan hasil halaman demi halaman (`LIMIT` / `OFFSET`) |
| **Parameterized query** | Mengirim nilai terpisah agar tidak bisa jadi perintah SQL |
| **SQL injection** | Serangan saat teks pengguna menjadi bagian dari SQL-mu |

## 🧠 Ide besarnya

SQL itu **deklaratif**: kamu menjelaskan **apa** yang kamu mau, dan database mengurus **caranya**.

> "Berikan saya judul lowongan kerja remote yang masih dibuka, diurutkan dari judul."

```sql
SELECT title FROM job_listings WHERE status = 'open' AND is_remote ORDER BY title;
```

Kamu tidak menulis loop, pencarian indeks, atau algoritma pengurutan. Seperti memesan *nasi goreng* alih-alih menjelaskan setiap langkah memasaknya — kamu masak sendiri di Modul 1; sekarang database yang masak, dan sangat cepat.

## ❓ Kenapa ini penting

Setiap layar di aplikasi adalah kueri: halaman daftar adalah `SELECT … ORDER BY … LIMIT`, form yang dikirim adalah `INSERT`, pengeditan adalah `UPDATE`, tombol hapus adalah `DELETE`, dashboard adalah `GROUP BY`. SQL sudah jadi bahasa standar untuk ini puluhan tahun, dan bekerja hampir sama di PostgreSQL, MySQL, SQLite, dan data warehouse.

Kalau tidak hati-hati, SQL adalah cara tercepat untuk menghancurkan data:

```sql
UPDATE job_listings SET status = 'closed';          -- forgot WHERE: closed ALL jobs
DELETE FROM applications WHERE user_id = user_id;   -- always true: deleted everything
SELECT * FROM job_listings WHERE salary_max = NULL; -- returns nothing, silently
```

Dan di kode aplikasi:

```python
# 🚨 SQL injection: a "search term" like  ' OR '1'='1  returns every row
cursor.execute(f"SELECT * FROM users WHERE email = '{email}'")
```

## 📖 Langkah demi langkah

### 1. INSERT

```sql
INSERT INTO job_listings (title, company, city, posted_on)
VALUES ('Data Analyst', 'Kopi Data', 'Bandung', '2026-09-13')
RETURNING id, status;

-- several rows at once
INSERT INTO job_listings (title, company, posted_on) VALUES
    ('QA Engineer', 'Awan Cloud', '2026-09-13'),
    ('ML Engineer', 'Lintas AI',  '2026-09-13');
```

Selalu **daftar kolom-kolom** — pernyataan tetap bekerja saat kolom baru ditambahkan nanti.

### 2. SELECT: pilih kolom dan baris

```sql
SELECT title, company, salary_max
FROM job_listings
WHERE city = 'Jakarta'
  AND salary_max >= 15000000
ORDER BY salary_max DESC, title
LIMIT 10;
```

Urutan logika evaluasi (bukan urutan penulisan):

```mermaid
flowchart LR
    F[FROM] --> W[WHERE] --> G[GROUP BY] --> H[HAVING] --> S[SELECT] --> O[ORDER BY] --> L[LIMIT / OFFSET]
```

Itulah kenapa kamu tidak bisa memakai alias `SELECT` di dalam `WHERE`, tapi boleh di `ORDER BY`.

### 3. Perangkat penyaring

| Kebutuhan | SQL |
|---|---|
| cocok tepat | `city = 'Jakarta'` |
| tidak sama | `status <> 'closed'` |
| salah satu dari beberapa | `city IN ('Jakarta', 'Bandung')` |
| jangkauan (termasuk batas) | `salary_max BETWEEN 10000000 AND 20000000` |
| pola, peka huruf besar-kecil | `title LIKE 'Junior%'` (`%` = karakter apa pun, `_` = satu karakter) |
| pola, tidak peka huruf besar-kecil (PostgreSQL) | `title ILIKE '%engineer%'` |
| nilai hilang | `salary_max IS NULL` / `IS NOT NULL` |
| gabung | `AND`, `OR`, `NOT` — pakai kurung saat mencampur |

### 4. NULL berarti "tidak diketahui"

`NULL` berperilaku seperti amplop yang tertutup rapat: kamu tidak bisa membandingkan dua amplop tertutup dan bilang mereka sama, jadi pakai `IS NULL` alih-alih `= NULL`.

`NULL` bukan nol atau teks kosong — ini **tidak diketahui**. Perbandingan apa pun dengan tidak-diketahui adalah tidak-diketahui, jadi:

- `salary_max = NULL` → tidak pernah benar. Pakai `IS NULL`.
- `salary_max <> 10000000` **tidak** mengembalikan baris di mana `salary_max` itu `NULL`.
- `COUNT(salary_max)` melewati NULL; `COUNT(*)` menghitung baris.
- `COALESCE(city, 'Remote')` mengganti NULL dengan cadangan.

### 5. Aggregate, GROUP BY, HAVING

```sql
SELECT city,
       COUNT(*)                 AS total_jobs,
       ROUND(AVG(salary_max))   AS avg_max_salary,
       MAX(salary_max)          AS highest
FROM job_listings
WHERE status = 'open'            -- filter ROWS first
GROUP BY city
HAVING COUNT(*) >= 2             -- then filter GROUPS
ORDER BY total_jobs DESC;
```

Aturan: setiap kolom yang dipilih harus **ada di `GROUP BY`** atau **di dalam aggregate**.

### 6. Pagination

```sql
SELECT id, title FROM job_listings ORDER BY posted_on DESC, id DESC LIMIT 20 OFFSET 40;  -- page 3
```

`OFFSET` jadi lambat untuk halaman dalam dan bisa melompati/duplikat baris saat data berubah; aplikasi besar memakai **keyset pagination** (`WHERE (posted_on, id) < (:last_date, :last_id)`) — kamu akan membuatnya di Minggu 5. Selalu sertakan kolom unik (seperti `id`) di `ORDER BY` untuk urutan yang stabil.

### 7. UPDATE dan DELETE — aman

```sql
UPDATE applications
SET status = 'interview', updated_at = now()
WHERE id = 42 AND user_id = 7          -- the ownership check matters!
RETURNING id, status;

DELETE FROM job_listings
WHERE status = 'closed' AND posted_on < '2026-01-01'
RETURNING id;
```

Rutinitas yang aman untuk perubahan manual:

1. Tulis `WHERE` sebagai `SELECT` dulu dan cek baris-barisnya.
2. Jalankan perubahan di dalam transaksi: `BEGIN;` → `UPDATE …` → cek → `COMMIT;` (atau `ROLLBACK;`).
3. Pakai `RETURNING` untuk melihat persis apa yang berubah.

**Soft delete** alih-alih `DELETE` saat kamu perlu riwayat: `UPDATE … SET deleted_at = now()` dan saring `WHERE deleted_at IS NULL` di mana-mana.

### 8. Parameterized queries (from Python)

Parameterized query menjaga **pertanyaan** dan **slot jawaban** terpisah, seperti form dengan kolom kosong. Teks yang diketik di kolom kosong tidak pernah bisa jadi instruksi baru.

```python
# ✅ The driver sends the value separately — it can never become SQL
conn.execute("SELECT id, full_name FROM users WHERE email = %s", (email,))

# ❌ Never build SQL with f-strings / concatenation from user input
conn.execute(f"SELECT id FROM users WHERE email = '{email}'")
```

ORM seperti SQLAlchemy (Minggu 4) parameterisasi secara otomatis — tapi saat kamu menulis SQL mentah, aturan ini adalah tanggung jawabmu.

### Memilih pengaturan kamu

Setiap pilihan di sini adalah trade-off:

| Pilihan | ✅ | ❌ |
|---|---|---|
| `SELECT *` | cepat untuk eksplorasi | mudah pecah di aplikasi, mengirim data yang tidak perlu, rusak saat kolom berubah |
| Daftar kolom eksplisit | stabil, efisien | perlu mengetik sedikit lebih banyak |
| `OFFSET` pagination | sederhana | lambat untuk halaman dalam, tidak stabil saat insert |
| Keyset pagination | cepat, stabil | tidak bisa melompat ke "halaman 37" langsung |
| Hard `DELETE` | sederhana, hemat ruang | tidak ada riwayat atau undo |
| Soft delete | bisa dipulihkan, bisa diaudit | setiap kueri harus ingat filter-nya |
| Menyaring di SQL | pakai indeks, transfer data lebih sedikit | logika terbagi antara SQL dan aplikasi |
| Menyaring di Python | fleksibel | memuat terlalu banyak data |

- ✅ Penyaring, pengurutan, aggregate, dan pagination **di database**, bukan setelah memuat semuanya ke Python.
- ✅ Pakai `RETURNING` untuk menghindari kueri kedua setelah insert/update/delete.
- 🚫 Jangan jalankan `UPDATE`/`DELETE` tanpa `WHERE` yang sudah kamu uji dengan `SELECT`.
- 🚫 Jangan pernah menggabung masukan pengguna ke SQL.

## ⚠️ Kesalahan umum

- `= NULL` alih-alih `IS NULL`.
- Memilih kolom yang tidak di-aggregate tanpa ada di `GROUP BY`.
- Memakai `WHERE` untuk menyaring aggregate (pakai `HAVING`).
- Bergantung pada urutan insert tanpa `ORDER BY`.
- `LIKE '%engineer%'` melewati "Engineer" (huruf besar-kecil) — pakai `ILIKE` atau `lower()`.

:::revoshop
Buka `queries/queries.sql` dan `queries/tests.sql` di RevoShop. Untuk setiap kueri, identifikasi: apakah C, R, U atau D? Apakah menyaring dengan `WHERE`, mengurutkan, aggregate? Lalu buka satu file repositori, mis. `app/repositories/order_repository.py`: cari tempat di mana kueri menyaring berdasarkan **pengguna sekarang** (pemeriksaan kepemilikan). Bisakah endpoint apa pun membiarkan pengguna A membaca atau mengubah pesanan pengguna B? Tulis cara kamu memverifikasinya.
:::

## 🏆 Praktik terbaik

- [ ] **Parameterisasi setiap kueri** yang mencakup masukan eksternal.
- [ ] Daftar kolom secara eksplisit di `SELECT` dan `INSERT` di kode aplikasi.
- [ ] Selalu `ORDER BY` saat urutan penting (tanpanya, urutan baris **tidak dijamin**), dengan tie-breaker unik untuk pagination.
- [ ] Uji klausa `WHERE` dengan `SELECT` sebelum `UPDATE`/`DELETE`; bungkus perubahan manual di transaksi.
- [ ] Sertakan **pemeriksaan kepemilikan** (`AND user_id = :current_user`) di kueri pada data pengguna.
- [ ] Tangani `NULL` dengan sengaja (`IS NULL`, `COALESCE`, `COUNT(column)` vs `COUNT(*)`).
- [ ] Pakai `RETURNING` alih-alih mem-query ulang.
- [ ] Format SQL untuk manusia: satu klausa per baris, keyword huruf besar, alias bermakna.
- [ ] Jangan pernah jalankan penulisan ad-hoc di production tanpa proses backup/review.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan perbedaan antara `WHERE` dan `HAVING` menggunakan contoh dunia nyata (mis. menghitung siswa per kelas, lalu menyimpan hanya kelas besar). Lalu jelaskan SQL injection ke orang yang bukan programmer.

## 📐 Rancang

Tulis SQL (di atas kertas) yang API CareerPilot jalankan untuk setiap endpoint. Pakai placeholder `:name` untuk parameter:

1. `GET /applications?status=interview&page=2` — aplikasi pengguna sekarang dengan status itu, paling baru dulu, 20 per halaman
2. `GET /stats` — jumlah aplikasi pengguna sekarang per status
3. `PATCH /applications/:id` — ubah catatan satu aplikasi (hanya kalau milik pengguna sekarang); kembalikan baris yang diubah
4. `DELETE /applications/:id` — soft delete

:::quiz
Lihat SQL yang mungkin

```sql
-- 1
SELECT id, company_id, role_title, status, applied_on
FROM applications
WHERE user_id = :user_id AND status = :status AND deleted_at IS NULL
ORDER BY created_at DESC, id DESC
LIMIT 20 OFFSET 20;

-- 2
SELECT status, COUNT(*) AS total
FROM applications
WHERE user_id = :user_id AND deleted_at IS NULL
GROUP BY status
ORDER BY total DESC;

-- 3
UPDATE applications
SET notes = :notes, updated_at = now()
WHERE id = :id AND user_id = :user_id AND deleted_at IS NULL
RETURNING id, role_title, status, notes, updated_at;
-- 0 rows returned → respond 404

-- 4
UPDATE applications
SET deleted_at = now()
WHERE id = :id AND user_id = :user_id AND deleted_at IS NULL
RETURNING id;
```
:::

### 📝 Checklist review mandiri

- [ ] Setiap kueri menyaring berdasarkan `user_id` (kepemilikan)
- [ ] Pagination punya urutan stabil dengan tie-breaker unik
- [ ] Parameter adalah placeholder, bukan nilai yang digabung
- [ ] Saya tahu apa yang API kembalikan saat 0 baris terkena dampak

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m2/w2/03-crud-queries" ai="no-ai" title="Sepuluh kueri pada daftar lowongan"}
Tulis 10 file SQL kecil — penyaring, NULL, aggregate, `HAVING`, `LIMIT`, `INSERT … RETURNING`, `UPDATE` yang aman, dan `DELETE`. Test memuat data seed fiktif ke skema segar dan membandingkan hasilmu persis (kolom, nilai, dan urutan).
:::

:::hints
- Jalankan kuerimu di psql atau GUI terhadap data seed sebelum menjalankan test.
- Untuk "mengandung engineer di huruf besar-kecil apa pun", pikirkan `ILIKE`.
- `ROUND(AVG(…))` pembulatan ke bilangan bulat.
- q06: saring baris *yang punya gaji* di `WHERE`, lalu hitung per kota di `HAVING`.
:::

### 🏆 Tantangan lebih jauh

Tulis `q11_salary_bands.sql`: hitung lowongan per band — `'< 10 juta'`, `'10–20 juta'`, `'> 20 juta'`, `'unknown'` — memakai `CASE WHEN … END` di dalam `GROUP BY`.

## ✅ Cek cepat

:::quiz
Kenapa `WHERE salary_max <> 10000000` tidak mengembalikan baris di mana `salary_max` itu NULL?

Perbandingan dengan NULL menghasilkan "tidak diketahui", dan `WHERE` menyimpan hanya baris di mana kondisinya benar. Tambahkan `OR salary_max IS NULL` kalau kamu mau mereka.
:::

:::quiz
Apa bedanya `COUNT(*)` dan `COUNT(salary_max)`?

`COUNT(*)` menghitung baris; `COUNT(salary_max)` menghitung hanya baris di mana `salary_max` bukan NULL.
:::

:::quiz
Bagaimana parameterized query mencegah SQL injection?

Teks SQL dan nilainya dikirim terpisah; database memperlakukan nilai ketat sebagai data, jadi masukan tidak bisa mengubah struktur kueri.
:::


## 📚 Lanjut belajar

- [Tutorial PostgreSQL: Querying a table](https://www.postgresql.org/docs/current/tutorial-select.html)
- [Dokumentasi PostgreSQL: Aggregate functions](https://www.postgresql.org/docs/current/functions-aggregate.html)
- [OWASP: SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)

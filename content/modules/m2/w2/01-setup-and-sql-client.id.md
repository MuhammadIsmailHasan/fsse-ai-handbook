---
title: "Setup PostgreSQL & SQL Client"
summary: Apa itu relational database, menjalankan PostgreSQL lokal dengan Docker, koneksi dengan psql dan GUI client, dan pilih tipe kolom yang tepat.
sourceHash: 44891aa20b78
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa itu **relational database** dan kenapa aplikasi tidak pakai file saja
- Kenapa **PostgreSQL** pilihan yang bagus
- Menjalankan PostgreSQL di lokal dengan **Docker Compose**
- Koneksi dengan **psql** dan **GUI client**; membaca **connection string**
- Buat tabel pertama dengan **data type** dan **default** yang tepat

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Relational database** | Basis data dengan tabel ketat yang bisa dihubungkan |
| **Table / row / column** | Tabel / satu baris data / satu kolom dengan tipe tetap |
| **PostgreSQL** | Server basis data populer, gratis, dan bisa diandalkan |
| **SQL** | Bahasa untuk bertanya kepada database |
| **Connection string** | Satu baris dengan user, password, host, port, dan nama database |
| **psql** | Klien database PostgreSQL di terminal |
| **Data type** | Jenis isi kolom (text, integer, numeric, timestamptz) |
| **Default value** | Nilai yang basis data pakai kalau kamu tidak isi |
| **`numeric`** | Tipe angka presisi untuk uang (jangan pakai `float`) |

## 🧠 Ide besarnya

:term[Relational database]{bahasa="basis data relasional — simpan data di tabel (baris & kolom) yang saling terhubung"} itu seperti **lemari filing yang sangat ketat**, dengan **satpam** menjaga depannya.

- Setiap **table** adalah satu lemari (`users`, `applications`), setiap **row** adalah satu berkas, setiap **column** adalah satu field dengan **type** tetap.
- Si satpam — server database — **paksakan aturan** (email harus ada, gaji tidak boleh negatif), biarkan banyak orang baca dan tulis **di waktu yang sama**, dan jawab pertanyaan ditulis dalam **SQL**.

File biasa tidak ada satpamnya: siapa saja bisa tulis apa saja, dan dua orang nulis bersamaan rusak berkas.

## ❓ Kenapa ini penting

Simpan data aplikasi di JSON atau CSV berhasil sampai:

- dua request tulis file yang sama di saat bersamaan → data rusak,
- kamu perlu "semua aplikasi user 7 dengan status interview" dari jutaan baris → harus baca file lengkap,
- server crash saat tulis → file setengah jadi,
- kamu butuh aturan "setiap aplikasi harus milik user yang ada".

Database pecahkan empat masalah ini: banyak user sekaligus, cepat cari jawaban, aman dari crash, dan jaga aturan data.

Pilih tipe kolom yang salah bawa masalah sendiri:

- `applications.json` jadi 2 GB, setiap page load baca semuanya.
- Gaji simpan sebagai teks: `'9000000'` urut sebelum `'10000000'`, dan `'9 juta'` masuk juga.
- Tanggal simpan sebagai `'13/09/2026'` string: urut dan hitungan tanggal rusak.
- Uang simpan sebagai `float`: kesalahan pembulatan di invoice.

## 📖 Langkah demi langkah

### 1. Kenapa PostgreSQL

| Kekuatan | Kenapa penting |
|---|---|
| Gratis, kode terbuka, sangat matang | tidak bayar, komunitas besar, dari startup sampai bank pakai |
| Ketat dan sesuai standar | tangkap data buruk lebih awal |
| Tipe kaya (`jsonb`, array, `uuid`, range) | fleksibel saat perlu |
| Extension (**pgvector**, PostGIS) | cari vektor untuk AI (Modul 7), peta |
| Ada di cloud mana saja (AWS RDS, Supabase, Neon) | gampang di-deploy |

Database lain yang akan kamu dengar: MySQL/MariaDB (relational juga), SQLite (database file — bagus untuk test dan aplikasi kecil), MongoDB (document), Redis (key-value di memori).

### 2. Jalankan PostgreSQL dengan Docker

Handbook punya `exercises/compose.yaml` yang sudah atur database di port **5491**:

```bash
cd exercises
docker compose up -d        # start in the background
docker compose ps           # should show "healthy"
docker compose logs -f db   # watch logs (Ctrl+C to stop watching)
docker compose down         # stop (data stays in the volume)
```

### 3. Connection string

Baca seperti alamat rumah: siapa kamu, rahasia, gedung mana, pintu mana, kamar mana — `postgresql://user:password@host:port/database`.

Aplikasi koneksi dengan URL:

```text
postgresql://fsse:fsse@localhost:5491/fsse
└── scheme ─┘ └user┘└pwd┘ └─ host ─┘└port┘└db┘
```

Di proyek sungguhan ini simpan di environment variable (`DATABASE_URL`), jangan di kode.

### 4. psql: klien command-line

```bash
docker compose exec db psql -U fsse -d fsse
```

| Perintah | Artinya |
|---|---|
| `\l` | lihat semua database |
| `\dt` | lihat semua table |
| `\d applications` | lihat detail satu table (kolom, tipe, aturan, index) |
| `\dn` | lihat schema |
| `\x` | toggle tampilan lebar untuk baris panjang |
| `\timing` | tampil berapa lama query jalan |
| `\i file.sql` | jalankan file SQL |
| `\q` | keluar |

Statement SQL akhiri dengan `;`. Perintah backslash tidak perlu.

### 5. GUI client

| Klien | Catatan |
|---|---|
| **DBeaver** | gratis, semua database didukung |
| **TablePlus** | cepat, rapi (gratis terbatas) |
| **pgAdmin** | alat official PostgreSQL |
| VS Code **PostgreSQL** extension | query dari editor |

Koneksi dengan host `localhost`, port `5491`, user `fsse`, password `fsse`, database `fsse`. GUI bagus untuk **jelajahi**; buat perubahan schema di **file SQL / migrasi** supaya tercatat versi (Minggu 4).

### 6. PostgreSQL type yang paling sering kamu pakai

Pilih type seperti pilih tempat makan di warung: yang tepat jangan sampai sup di dalam kantong plastik. Uang selalu di `numeric`, waktu selalu di `timestamptz`.

| Untuk | Type | Catatan |
|---|---|---|
| Id | `bigint GENERATED ALWAYS AS IDENTITY` | primary key auto-naik (pengganti `serial` modern) |
| Id publik/tidak bisa ditebak | `uuid` | contoh `gen_random_uuid()` |
| Hitung, angka kecil | `integer` | ±2,1 miliar |
| Uang | `bigint` (unit terkecil) atau `numeric(12,2)` | **jangan** `real`/`double precision` |
| Teks | `text` | tidak beda dengan `varchar(n)` di PostgreSQL; tambah `CHECK` kalau perlu batas panjang |
| Ya/tidak | `boolean` | |
| Tanggal kalender | `date` | |
| Saat di waktu | `timestamptz` | simpan saat absolut — pakai ini, bukan `timestamp` tanpa zona waktu |
| Dokumen fleksibel | `jsonb` | untuk data benar-benar variable; jangan pakai untuk menghindari rancang table |

### 7. Tabel pertama kamu

```sql
CREATE TABLE study_sessions (
    id          bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    topic       text        NOT NULL,
    minutes     integer     NOT NULL CHECK (minutes > 0),
    studied_on  date        NOT NULL DEFAULT CURRENT_DATE,
    created_at  timestamptz NOT NULL DEFAULT now()
);

INSERT INTO study_sessions (topic, minutes) VALUES ('Git basics', 90)
RETURNING id, studied_on;

SELECT * FROM study_sessions;
```

- `PRIMARY KEY` = unik, tidak boleh kosong, identifier setiap baris.
- `NOT NULL`, `CHECK` dan `DEFAULT` adalah **aturan yang basis data paksakan** — tidak peduli aplikasi atau script mana yang tulis data.
- `RETURNING` beri balik nilai yang di-generate tanpa query kedua.

### Pilih setup kamu

Setiap pilihan di sini ada trade-off:

| Pilihan | ✅ | ❌ |
|---|---|---|
| PostgreSQL | kuat, ketat, bisa diperluas | server yang harus dijalankan |
| SQLite | nol setup, satu file | tulis bersamaan terbatas; fitur kurang |
| MongoDB (dokumen) | bentuk fleksibel | relasi/join lebih lemah; aturan di kode aplikasi |
| Database di Docker lokal | setup sama semua orang | perlu Docker |
| Database cloud terkelola di production | backup, failover, patch otomatis | bayar; kontrol kurang |

- ✅ PostgreSQL default untuk aplikasi web dengan data terhubung: user, pesanan, aplikasi.
- ✅ Constraint di database untuk aturan yang **harus** berlaku selalu.
- 🚫 Jangan pakai relational database sebagai cache atau antrian di volume tinggi (Redis/queue ada untuk itu).
- 🚫 Jangan simpan file besar (CV, foto) di table — simpan di object storage, catat **path/URL** saja.

## ⚠️ Kesalahan umum

- Lupa `;` di psql dan heran tidak ada yang terjadi (prompt jadi `fsse-#`).
- Koneksi ke `5432` padahal container di `5491`.
- Pakai `timestamp` bukan `timestamptz`.
- Nama table `user` atau `order` (reserved word → menyebalkan paksa quote).
- Hilang data dengan `docker compose down -v` (flag `-v` hapus volume).

:::revoshop
Buka `queries/schema.sql` di RevoShop. Cari: primary key, `NOT NULL UNIQUE` di `users.username` dan `users.email`, dan `CHECK (price > 0)` di product. Tipe apa yang kamu pakai untuk uang (`price`, `total_amount`) dan timestamp? Bandingkan dengan table di bagian 6 — ada yang mau kamu ubah hari ini, kenapa? Cek juga `docker-compose.yml`: PostgreSQL versi berapa yang RevoShop kunci?
:::

## 🏆 Praktik terbaik

- [ ] Jalankan **PostgreSQL versi major sama** di lokal dan di production (kunci tag Docker image).
- [ ] Simpan detail koneksi di **`DATABASE_URL`** / environment variable; commit cuma `.env.example`.
- [ ] Pakai `bigint ... GENERATED ALWAYS AS IDENTITY` (atau `uuid`) untuk primary key.
- [ ] Pakai **`timestamptz`** untuk saat di waktu; simpan UTC dan konversi untuk tampil.
- [ ] Jangan pakai floating point untuk uang.
- [ ] Tambah `NOT NULL` default; biarkan `NULL` cuma saat "tidak tahu/tidak berlaku" adalah keadaan nyata.
- [ ] Letakkan perubahan schema di **file SQL versi atau migrasi**, jangan cuma klik di GUI.
- [ ] Pakai **least-privilege** database user untuk aplikasi (bukan superuser) di environment sungguhan.
- [ ] Pakai `snake_case` nama; hindari reserved word (`user`, `order`) sebagai nama table — lebih suka `users`, `orders`.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan kepada orang awam kenapa aplikasi dengan ribuan user simpan data di server database, bukan di file spreadsheet besar. Sebutkan minimal dua masalah yang database pecahkan.

## 📐 Rancang

Pilih tipe PostgreSQL, nullable, dan default (kalau ada) untuk setiap kolom di table CareerPilot `job_listings`:

`id`, `title`, `company_name`, `city`, `is_remote`, `salary_min`, `salary_max`, `currency`, `posted_on`, `source_url`, `raw_description`, `imported_at`, `extra_metadata` (beda banyak antara job board)

:::quiz
Lihat contoh rancangan

| Kolom | Type | Null? | Default / aturan |
|---|---|---|---|
| `id` | `bigint GENERATED ALWAYS AS IDENTITY` | tidak | primary key |
| `title` | `text` | tidak | `CHECK (length(title) BETWEEN 1 AND 200)` |
| `company_name` | `text` | tidak | |
| `city` | `text` | ya | job remote tidak punya kota |
| `is_remote` | `boolean` | tidak | `DEFAULT false` |
| `salary_min`, `salary_max` | `bigint` | ya | `CHECK (salary_min <= salary_max)` |
| `currency` | `text` | tidak | `DEFAULT 'IDR'`, `CHECK (currency ~ '^[A-Z]{3}$')` |
| `posted_on` | `date` | ya | |
| `source_url` | `text` | tidak | `UNIQUE` (cegah import duplikat) |
| `raw_description` | `text` | tidak | |
| `imported_at` | `timestamptz` | tidak | `DEFAULT now()` |
| `extra_metadata` | `jsonb` | tidak | `DEFAULT '{}'` — beda per sumber |
:::

### 📝 Checklist review mandiri

- [ ] Uang adalah `bigint`/`numeric`, bukan floating point
- [ ] Saat di waktu pakai `timestamptz`
- [ ] `NULL` diizinkan cuma saat "tidak tahu" nyata
- [ ] Pakai `UNIQUE`/`CHECK` untuk jaga kualitas data

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m2/w2/01-postgres-setup" ai="no-ai" title="Tabel PostgreSQL pertama kamu"}
1. Mulai database: `cd exercises && docker compose up -d`
2. Koneksi dengan psql (`docker compose exec db psql -U fsse -d fsse`) **dan** dengan GUI client pilihan kamu. Jalankan `SELECT version();` di dua tempat.
3. Tulis `study_log.sql` (spek di folder README): table `study_log` dengan tipe, constraint, dan default yang tepat, plus 3 baris insert.

Test jalankan file kamu di schema baru dan lihat hasilnya.
:::

:::hints
- `bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY`
- `CHECK (minutes BETWEEN 1 AND 600)`
- `DEFAULT CURRENT_DATE` untuk tanggal, `DEFAULT now()` untuk timestamp
- Jangan masukkan `CREATE SCHEMA` atau `SET search_path` — test urus itu.
:::

### 🏆 Tantangan lebih

Di psql, jalankan `\d study_log`, lalu coba insert baris dengan `minutes = 0` dan baca pesan error-nya. Constraint name apa yang PostgreSQL laporkan? Beri nama jelas: `CONSTRAINT study_log_minutes_range CHECK (…)`.

## ✅ Cek cepat

:::quiz
Kenapa pakai `timestamptz` bukan `timestamp`?

`timestamptz` simpan saat absolut (normalized ke UTC) dan konversi benar antar zona waktu. `timestamp` tanpa zona waktu, jadi nilai yang sama bisa berarti saat berbeda di server berbeda.
:::

:::quiz
`RETURNING` di `INSERT` apa artinya?

Balikin kolom dari baris yang di-insert — seperti `id` yang di-generate dan default — dalam satu statement.
:::

:::quiz
Connection string untuk aplikasi kamu harus di mana?

Di environment variable (contoh `DATABASE_URL`), muat dari `.env` git-ignored lokal dan dari secret setting platform di production.
:::


## 📚 Lanjut belajar

- [Dokumentasi PostgreSQL: Data Types](https://www.postgresql.org/docs/current/datatype.html)
- [PostgreSQL wiki: Don't Do This](https://wiki.postgresql.org/wiki/Don%27t_Do_This)
- [Referensi psql](https://www.postgresql.org/docs/current/app-psql.html)

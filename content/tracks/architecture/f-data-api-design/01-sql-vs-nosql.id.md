---
title: "SQL vs NoSQL"
summary: Pilih database yang tepat — bedanya database relasional dan document/key-value, kelebihan dan kekurangan masing-masing, dan kenapa "mulai dari PostgreSQL" adalah pilihan aman untuk kebanyakan aplikasi.
sourceHash: 384c6cbd0f20
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa arti "SQL" (relasional) dan database "NoSQL"
- Keluarga utama NoSQL: document, key-value, wide-column, graph
- Kelebihan database relasional, dan di mana ia kesulitan
- Apa yang kamu dapat dari NoSQL, dan apa harganya
- Aturan sederhana untuk memilih — dan kenapa PostgreSQL adalah pilihan aman
- Bagaimana ini terhubung ke data RevoShop (user, produk, order)

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Relasional (SQL)** | Data disimpan dalam tabel berisi baris dan kolom, dengan bentuk ketat |
| **Schema** | Bentuk data yang disepakati (kolom apa, tipe apa) |
| **NoSQL** | Database apa pun yang bukan model tabel-dan-baris relasional |
| **Document store** | Menyimpan objek utuh (seperti JSON) alih-alih baris |
| **Key-value store** | Kamus raksasa: satu kunci → satu nilai |
| **JOIN** | Menggabungkan baris dari dua tabel lewat kunci yang sama |
| **Transaksi** | Sekelompok perubahan yang semuanya terjadi, atau tidak sama sekali |
| **Denormalisasi** | Menyalin data yang sama ke beberapa tempat agar cepat dibaca |

## 🧠 Ide besarnya

**Database relasional** seperti **spreadsheet dengan aturan**: setiap baris di sheet "orders" punya kolom yang persis sama, dan database menolak baris yang melanggar aturan. Ketat, dan ketatnya itu melindungi datamu.

**Database document** seperti **map berisi formulir**: tiap formulir (dokumen) adalah objek utuh, dan dua formulir di map yang sama boleh sedikit berbeda. Fleksibel, dan fleksibelnya membuatmu cepat bergerak — sampai kamu butuh aturannya lagi.

## ❓ Kenapa ini penting

Memilih database adalah salah satu keputusan yang paling sulit dibatalkan. Seluruh aplikasimu dibentuk olehnya. Kalau salah pilih, kamu tidak memperbaikinya dengan perubahan kecil — kamu memindahkan data, menulis ulang query, dan menguji ulang semuanya.

Kabar baiknya: untuk kebanyakan aplikasi, jawaban jujurnya adalah **PostgreSQL** (relasional). Pemula sering langsung memilih NoSQL karena terdengar modern atau "web scale", lalu terkena masalah menyakitkan yang sudah lama dipecahkan database relasional — misalnya menjaga order dan pembayarannya tetap konsisten. Tahu untuk apa tiap alat menyelamatkanmu dari rasa sakit itu.

## 📖 Langkah demi langkah

### 1. Apa itu database relasional (SQL)

Data hidup dalam **tabel**. Tiap tabel punya **schema** tetap (kolom dan tipe). Kamu menghubungkan tabel dengan kunci dan menggabungkannya dengan **JOIN**. Contoh: **PostgreSQL**, MySQL, SQLite.

```sql
-- Two tables, linked by user_id
SELECT users.name, orders.total
FROM orders
JOIN users ON users.id = orders.user_id
WHERE orders.status = 'paid';
```

Kekuatan super mereka adalah **konsistensi**: bentuk ketat, relasi yang dipaksakan oleh database, dan **transaksi** — "buat order DAN kurangi stok, atau jangan lakukan keduanya". Kamu bertemu ini di Modul 2 Minggu 2.

### 2. Apa itu database NoSQL

"NoSQL" hanya berarti "bukan model klasik tabel-dan-baris". Ini keluarga, bukan satu benda:

| Keluarga | Menyimpan | Cocok untuk | Contoh |
|---|---|---|---|
| **Document** | Objek utuh (mirip JSON) | Data yang bepergian bersama, bentuk fleksibel | MongoDB |
| **Key-value** | key → value (kamus raksasa) | Cache, sesi, pencarian sangat cepat | Redis |
| **Wide-column** | Baris dengan set kolom besar dan jarang | Volume tulis masif, time-series | Cassandra |
| **Graph** | Node dan koneksi | "Teman dari teman", rekomendasi | Neo4j |

Document store membuatmu bisa menyimpan order sebagai satu objek, tanpa JOIN:

```javascript
// One document = the whole order, read in a single lookup
{
  "_id": "order_123",
  "user": { "id": 7, "name": "Ismail" },
  "items": [ { "product": "Mug", "qty": 2, "price": 50000 } ],
  "status": "paid"
}
```

### 3. Trade-off sebenarnya: bentuk ketat vs bentuk fleksibel

Inilah inti dari pilihan ini.

| | Relasional (SQL) | Document (NoSQL) |
|---|---|---|
| Bentuk data | Schema tetap, dipaksakan | Fleksibel, per-dokumen |
| Relasi | JOIN antar tabel | Sering disalin ke dalam dokumen (**denormalisasi**) |
| Transaksi kuat | ✅ dibuat untuk itu | ⚠️ terbatas (lebih baik di versi baru) |
| Ubah tipe sebuah field | Perlu migrasi | Cukup tulis bentuk baru |
| Data terduplikasi | Dihindari | Umum (dan bisa jadi tidak sinkron) |

Denormalisasi (menyalin `user.name` ke tiap order) membuat baca cepat, tapi kini perubahan nama harus diperbarui di banyak tempat. Database relasional menghindari itu dengan menyimpan satu sumber kebenaran dan JOIN.

### 4. Kelebihan asli masing-masing

**Relasional bersinar saat:**
- Data punya relasi jelas (user → order → item).
- Kamu butuh transaksi ("semua atau tidak").
- Kamu menjalankan query beragam yang belum bisa diprediksi (laporan, filter, JOIN).

**NoSQL bersinar saat:**
- Data dibaca dan ditulis sebagai satu gumpalan (dokumen, entri cache, event).
- Bentuknya sering berubah atau berbeda per record.
- Kamu butuh satu hal spesifik pada skala ekstrem (jutaan baca/tulis key-value per detik → Redis; aliran tulis besar → Cassandra).

### 5. Kenyataan modern: garisnya kabur

PostgreSQL punya tipe kolom `JSONB` — kamu bisa menyimpan dokumen fleksibel *di dalam* tabel relasional dan query ke dalamnya. Jadi kamu sering mendapat fleksibilitas ala NoSQL tanpa meninggalkan keamanan database relasional:

```sql
-- Flexible attributes in a JSONB column, still inside PostgreSQL
SELECT name FROM products WHERE attributes->>'color' = 'red';
```

Inilah kenapa "cukup pakai PostgreSQL" mencakup begitu banyak kasus: ia melakukan bagian ketat *sekaligus* sebagian besar bagian fleksibel.

### Pilih database-mu

| Situasimu | Pilihan bagus |
|---|---|
| Aplikasi web/mobile biasa (user, order, konten) | **PostgreSQL** — mulai di sini |
| Cache, penyimpan sesi, penghitung rate-limit | **Redis** (key-value) — *berdampingan* dengan DB utama |
| Satu bagian fleksibel di dalam aplikasi relasional | **`JSONB`** PostgreSQL |
| Volume tulis benar-benar besar / time-series | Cassandra atau DB time-series |
| Data yang sebagian besar koneksi (social graph) | Database graph |

- ✅ Default ke relasional (PostgreSQL) kecuali ada alasan konkret untuk tidak.
- ✅ Wajar memakai **dua** penyimpanan: PostgreSQL untuk sumber kebenaran, Redis untuk cache.
- 🚫 Jangan pilih NoSQL demi "skala" yang belum kamu punya — kebanyakan aplikasi tak pernah mencapainya.
- 🚫 Jangan menyebar sumber kebenaran ke banyak database sejak awal; itu menggandakan bug.

## ⚠️ Kesalahan umum

- Memilih NoSQL untuk "menghindari schema", lalu membangun ulang aturan schema dengan tangan di kode aplikasi (dengan buruk).
- Menyimpan uang atau order di penyimpanan tanpa transaksi kuat, lalu total jadi tidak konsisten.
- Denormalisasi di mana-mana, lalu memburu nilai yang sama di puluhan dokumen saat ia berubah.
- Memperlakukan Redis sebagai sumber kebenaran — ia pembantu cepat, bukan penyimpan jangka panjang yang aman.

:::revoshop
RevoShop memakai PostgreSQL. (1) Sebutkan tabel utamanya dan relasi di antaranya (user, produk, order, item order). Kenapa transaksi penting saat membuat order yang juga mengurangi stok produk? (2) Bagian RevoShop mana yang cocok dengan key-value store seperti Redis — misalnya keranjang atau penghitung rate-limit — dan kenapa menyimpannya *terpisah* dari tabel sumber kebenaran? (3) Bisakah `attributes` produk (ukuran, warna) tinggal di kolom `JSONB` alih-alih banyak kolom nullable? Apa untung ruginya?
:::

## 🏆 Praktik terbaik

- [ ] Mulai dengan database relasional (PostgreSQL) dan schema yang jelas; beralih hanya karena alasan yang terbukti.
- [ ] Jaga **satu sumber kebenaran**; tambahkan penyimpanan lain (seperti Redis) sebagai pembantu, bukan pengganti.
- [ ] Pakai transaksi untuk apa pun yang harus "semua atau tidak" (uang, stok, tulis banyak langkah).
- [ ] Pakai `JSONB` saat beberapa field fleksibel — sebelum menambah database kedua.
- [ ] Saat denormalisasi, catat di mana salinannya berada dan bagaimana mereka tetap sinkron.
- [ ] Cocokkan penyimpanan dengan pola akses: sumber kebenaran → relasional; cache/penghitung → key-value.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke orang non-programmer kenapa toko online menyimpan order-nya di database "ketat" (relasional) tapi mungkin menyimpan keranjang belanjanya di yang "cepat dan sederhana" (key-value). Pakai analogi spreadsheet-dengan-aturan vs map-berisi-formulir.

## 📐 Rancang

CareerPilot menyimpan: profil user, lamaran kerja tersimpan (dengan status), dan log setiap saran AI yang pernah dibuat (jutaan record kecil, tulis-sekali). Putuskan penyimpanan mana untuk masing-masing dari ketiganya dan kenapa. Untuk bagian profil-dan-lamaran, sketsa tabel relasionalnya; untuk log saran AI, perdebatkan apakah relasional masih cocok atau apakah penyimpanan lain layak dipakai.

:::quiz
Tampilkan satu rancangan yang mungkin

**Profil + lamaran → PostgreSQL (relasional).** Mereka punya relasi jelas (`user` → `application` → `status_history`) dan butuh transaksi (ubah status *dan* catat perubahannya bersamaan). Query beragam di masa depan ("semua lamaran yang interview bulan ini") mudah dengan SQL.

**Log saran AI → tetap PostgreSQL dulu.** Ia tulis-sekali dan bervolume tinggi, yang *terdengar* seperti tugas NoSQL, tapi PostgreSQL modern menangani jutaan baris dengan baik lewat index di `(user_id, created_at)`. Menyimpannya di satu database berarti satu backup, satu tempat query, dan transaksi saat sebuah saran terhubung ke lamaran. Baru pindahkan ke wide-column/time-series bila pengukuran nanti menunjukkan PostgreSQL kesulitan.

**Aturan yang ditunjukkan:** jangan pisahkan penyimpanan berdasarkan tebakan. Mulai relasional, ukur, dan pisahkan satu tabel spesifik hanya saat ia terbukti butuh penyimpanan khusus.
:::

### 📝 Checklist review mandiri

- [ ] Tiap pilihan penyimpanan dibenarkan oleh pola akses dan kebutuhan konsistensi, bukan hype
- [ ] Transaksi diidentifikasi di mana "semua atau tidak" penting
- [ ] Satu sumber kebenaran jelas
- [ ] Denormalisasi/duplikasi apa pun disebut dengan rencana sinkronisasi

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/architecture/f-data-api-design/01-sql-vs-nosql" ai="no-ai" title="Modelkan data yang sama dengan dua cara"}
Diberi dataset order kecil, implementasikan dua "penyimpanan" dalam-memori kecil: satu relasional (tabel ternormalisasi + join) dan satu document (objek yang didenormalisasi). Tes yang sama memeriksa bahwa keduanya mengembalikan total order dan nama user yang benar — dan bahwa mengubah nama user adalah satu tulis di model relasional tapi banyak tulis di model document.
:::

:::hints
- Relasional: simpan `users` dan `orders` sebagai dict terpisah berkunci id; `join_orders` mencari user lewat `user_id`.
- Document: tiap order menyimpan salinan nama user; `rename_user` harus memindai tiap order untuk memperbaruinya.
- Tujuan tes adalah *menunjukkan* trade-off, bukan membuat satu model "menang".
:::

## ✅ Cek cepat

:::quiz
Kenapa "cukup pakai PostgreSQL" adalah default yang masuk akal untuk kebanyakan aplikasi?

Karena kebanyakan aplikasi punya data berelasi, butuh transaksi, dan menjalankan query beragam — persis yang paling dikuasai database relasional — dan PostgreSQL juga menyediakan `JSONB` untuk bagian yang fleksibel, jadi kamu jarang butuh database jenis kedua sejak awal.
:::

:::quiz
Apa risiko utama denormalisasi (menyalin data ke banyak dokumen)?

Salinannya bisa jadi tidak sinkron. Saat nilai aslinya berubah, kamu harus memperbarui setiap salinan, dan melewatkan satu saja membuat datamu tidak konsisten.
:::

## 📚 Lanjut belajar

- [PostgreSQL: JSON types](https://www.postgresql.org/docs/current/datatype-json.html)
- [MongoDB: data modeling introduction](https://www.mongodb.com/docs/manual/core/data-modeling-introduction/)
- [Martin Kleppmann, *Designing Data-Intensive Applications*, Ch. 2 (data models)](https://dataintensive.net/)

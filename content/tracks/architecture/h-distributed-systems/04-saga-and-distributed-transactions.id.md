---
title: "Saga & Distributed Transactions"
summary: Cara menjaga operasi multi-layanan tetap konsisten saat satu transaksi database tak bisa mencakup semuanya — pola saga menjalankan rantai langkah lokal, masing-masing dengan undo pembatal, supaya kegagalan di akhir membatalkan semuanya dengan rapi.
sourceHash: b5b23b33c68a
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Kenapa satu transaksi database tak bisa mencakup banyak layanan
- Apa itu **saga**: rantai langkah lokal dengan **kompensasi**
- Bagaimana **aksi kompensasi** membatalkan langkah yang selesai
- Cara **orchestration** vs **choreography** menjalankan saga
- Kenapa saga memberi konsistensi **eventual**, bukan atomik seketika
- Bagaimana ini berlaku untuk checkout yang menyentuh stok, pembayaran, dan pengiriman

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Transaksi** | Sekelompok perubahan yang semuanya terjadi atau tidak |
| **Atomik** | Semua-atau-tidak, tak ada state setengah jadi |
| **Saga** | Urutan langkah lokal yang masing-masing bisa dibatalkan |
| **Transaksi lokal** | Satu transaksi biasa di dalam satu layanan |
| **Kompensasi** | Aksi yang membatalkan langkah yang selesai |
| **Orchestration** | Satu koordinator menjalankan langkah-langkah |
| **Choreography** | Layanan bereaksi ke event satu sama lain |

## 🧠 Ide besarnya

Memesan perjalanan berarti tiga meja terpisah: **pesawat**, **hotel**, **mobil**. Tak ada satu "transaksi perjalanan" — tiap meja hanya mengendalikan pemesanannya sendiri. **Saga** adalah **agen perjalanan** yang memesannya satu per satu, dan kalau meja mobil bilang "habis" setelah pesawat dan hotel dipesan, agen **membatalkan** hotel dan pesawat (**kompensasi**) supaya kamu tak berakhir setengah-terpesan.

Kompensasi bukan mundur ajaib — ia undo nyata dan masuk akal: batalkan reservasi, kembalikan pembayaran, lepaskan stok.

## ❓ Kenapa ini penting

Di Modul 2 kamu memakai satu transaksi untuk membuat beberapa perubahan atomik — tapi itu hanya bekerja **di dalam satu database**. Begitu operasi melintasi layanan (layanan order, layanan pembayaran, layanan pengiriman), masing-masing punya database *sendiri*, dan tak ada satu transaksi yang bisa membungkus semuanya.

Tanpa rencana, kegagalan di tengah meninggalkan kekacauan: stok dipesan tapi tak ada pembayaran, atau uang diambil tapi tak ada order. Pola saga adalah cara standar menjaga operasi multi-layanan seperti itu tetap konsisten — tidak seketika, tapi andal.

## 📖 Langkah demi langkah

### 1. Kenapa tidak satu transaksi besar saja?

Jawaban klasiknya adalah **two-phase commit (2PC)**: koordinator bertanya ke tiap layanan "siap?", lalu "commit". Ia memberi atomicity sejati, tapi lambat, dan ia **memblokir**: kalau koordinator atau satu layanan macet, semua menunggu dengan lock tertahan. Pada skala besar ini rapuh, jadi kebanyakan sistem menghindari 2PC untuk kerja lintas-layanan.

### 2. Saga: langkah lokal + kompensasi

Saga memecah operasi besar menjadi **urutan transaksi lokal**, masing-masing di satu layanan. Tiap langkah punya **kompensasi** yang membatalkannya:

| Langkah (do) | Kompensasi (undo) |
|---|---|
| Pesan stok | Lepas stok |
| Tagih pembayaran | Kembalikan pembayaran |
| Buat pengiriman | Batalkan pengiriman |

Jalankan langkah secara berurutan. Kalau sebuah langkah gagal, jalankan **kompensasi untuk langkah yang sudah selesai, dalam urutan terbalik**.

```
reserve stock ✅ → charge payment ✅ → create shipment ❌
                          ↓ fail → compensate in reverse:
                    refund payment ↩ → release stock ↩
```

State akhirnya konsisten: entah semuanya sukses, atau semuanya dibatalkan.

### 3. Kompensasi harus nyata dan idempotent

Kompensasi adalah logika bisnis, bukan rollback database. "Kembalikan pembayaran" berarti benar-benar menerbitkan refund. Dan karena langkah dan kompensasi bisa di-retry (messaging at-least-once), masing-masing harus **idempotent** — merefund dua kali tak boleh mengirim dua refund.

Sebagian langkah tak bisa dibatalkan sempurna (email yang sudah terkirim). Untuk itu kamu kompensasi sebisanya (kirim koreksi) — alasan untuk mengurutkan langkah supaya yang paling sulit dibatalkan datang **terakhir**.

### 4. Orchestration vs choreography

Dua cara menjalankan rantainya:

- **Orchestration**: satu **koordinator** ("saga order") secara eksplisit memanggil tiap langkah dan memicu kompensasi saat gagal. Mudah melihat seluruh alur di satu tempat; koordinatornya bagian pusat yang harus dipelihara.
- **Choreography**: tak ada koordinator — tiap layanan memancarkan **event** (`StockReserved`, `PaymentCharged`) dan layanan berikutnya bereaksi. Sangat decoupled, tapi alur keseluruhan tersebar di banyak layanan dan lebih sulit diikuti.

Pemula sebaiknya biasanya mulai dengan **orchestration**: logikanya ada di satu tempat yang mudah dibaca.

### 5. Eventual, bukan seketika

Selama saga berjalan, sistem sesaat *tidak konsisten* (stok dipesan, pembayaran belum ditagih). Itu wajar — saga memberi konsistensi **eventual**. Jadi state seperti `order: pending` itu normal, dan user diberi tahu "kami sedang mengonfirmasi order-mu" sampai saga selesai.

### Pilih pendekatanmu

| Situasi | Lakukan ini |
|---|---|
| Semua perubahan di satu database | Pakai transaksi biasa — tak perlu saga |
| Operasi mencakup beberapa layanan | Saga dengan kompensasi |
| Alur kecil, mudah dibaca, dimiliki satu tim | Orchestration (satu koordinator) |
| Layanan yang sangat decoupled, event-driven | Choreography (event), dengan hati-hati |

- ✅ Pakai transaksi biasa saat semuanya di satu database.
- ✅ Untuk operasi multi-layanan, definisikan kompensasi tiap langkah sejak awal.
- ✅ Urutkan langkah supaya aksi paling sulit dibatalkan terakhir; buat langkah idempotent.
- 🚫 Jangan memakai 2PC lintas-layanan secara default — ia lambat dan memblokir.

## ⚠️ Kesalahan umum

- Menganggap satu transaksi bisa mencakup layanan — tak bisa; masing-masing punya database sendiri.
- Lupa menulis kompensasi untuk sebuah langkah, sehingga kegagalan di akhir tak bisa dibatalkan.
- Langkah/kompensasi non-idempotent → refund atau reservasi ganda di bawah retry.
- Mengurutkan langkah yang tak bisa dibatalkan (kirim email, kirim barang) lebih awal, sebelum langkah berisiko.
- Menyembunyikan state sedang-berjalan, sehingga user mengira order gagal padahal saga masih berjalan.

:::revoshop
Checkout RevoShop hari ini satu transaksi PostgreSQL (pesan stok, buat order, catat pembayaran bersama). (1) Kalau pembayaran pindah ke layanan terpisah (atau Midtrans), transaksi itu tak lagi mencakup semuanya — sketsa saganya: langkah dan kompensasi tiap langkah. (2) Langkah mana yang paling sulit dibatalkan, dan di mana ia harus berada dalam urutan? (3) Webhook pembayaran bisa menyala dua kali — bagaimana kamu menjaga langkah "charge" dan kompensasi "refund"-nya idempotent?
:::

## 🏆 Praktik terbaik

- [ ] Jaga kerja satu-database dalam satu transaksi; hanya pakai saga lintas layanan.
- [ ] Definisikan kompensasi untuk tiap langkah sebelum merilis saga.
- [ ] Buat tiap langkah dan kompensasi idempotent (retry pasti terjadi).
- [ ] Urutkan langkah supaya aksi paling tak-bisa-dibalik berjalan terakhir.
- [ ] Utamakan orchestration dulu untuk alur pusat yang jelas; tambah choreography hanya saat decoupling menuntutnya.
- [ ] Modelkan dan tampilkan state sedang-berjalan (`pending`, `confirming`) ke user dan monitoring.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan saga dengan analogi agen-perjalanan-memesan-pesawat-hotel-mobil, termasuk apa yang terjadi saat mobil habis. Lalu katakan, dalam satu kalimat, kenapa kompensasi berbeda dari rollback database.

## 📐 Rancang

CareerPilot menawarkan "Priority Application" berbayar: ia (1) menghabiskan 1 kredit, (2) memanggil AI berbayar untuk menyesuaikan CV, (3) mengirim lamaran ke API partner, dan (4) mengirim email konfirmasi. Ini menyentuh layanan berbeda. Rancang saganya: langkah berurutan, tiap kompensasi, langkah mana yang harus terakhir, dan bagaimana kamu menangani fakta bahwa email tak bisa benar-benar di-un-send.

:::quiz
Tampilkan satu rancangan yang mungkin

**Langkah berurutan + kompensasi:**
1. **Habiskan 1 kredit** ↔ kompensasi: **kembalikan kredit**.
2. **AI sesuaikan CV** ↔ kompensasi: **buang draf yang dihasilkan** (murah; tak ada yang berubah di luar).
3. **Kirim ke API partner** ↔ kompensasi: **tarik/batalkan kiriman** (kalau partner mengizinkan).
4. **Email konfirmasi** — praktis **tak bisa dibatalkan**, jadi ia **terakhir**, hanya setelah semua yang lain sukses.

**Saat gagal:** kalau langkah 3 (kirim) gagal, kompensasi terbalik — buang draf dan kembalikan kredit — meninggalkan user persis seperti sebelumnya, dan tak pernah mengirim email konfirmasi.

**Masalah email:** kamu tak bisa un-send-nya, jadi kamu (a) taruh terakhir supaya hanya menyala pada sukses penuh, dan (b) kalau sesuatu harus dibatalkan setelahnya, kirim email **koreksi** sebagai kompensasi. Mengurutkan langkah paling tak-bisa-dibalik terakhir meminimalkan ini.

**Idempotency:** kunci tiap langkah dengan id lamaran supaya "habiskan kredit" atau "refund" yang di-retry tak berganda.

**Aturan yang ditunjukkan:** saga adalah langkah lokal berurutan dengan kompensasi nyata; taruh langkah paling tak-bisa-dibalik terakhir dan buat semuanya idempotent, menerima konsistensi eventual (bukan seketika).
:::

### 📝 Checklist review mandiri

- [ ] Tiap langkah punya kompensasi konkret
- [ ] Langkah paling tak-bisa-dibalik diurutkan terakhir
- [ ] Langkah dan kompensasi idempotent
- [ ] State sedang-berjalan/eventual dimodelkan dan ditampilkan

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/architecture/h-distributed-systems/04-saga" ai="no-ai" title="Runner saga dengan kompensasi"}
Implementasikan runner saga: jalankan aksi tiap langkah secara berurutan; kalau satu gagal, jalankan kompensasi langkah yang sudah selesai dalam urutan terbalik, dan laporkan apa yang commit vs apa yang di-rollback. Tes menggiring saga booking ke sukses penuh dan ke kegagalan di tengah yang harus membatalkan langkah sebelumnya.
:::

:::hints
- Tiap langkah adalah dict: `{"name", "action", "compensate"}`; `action(ctx)` dan `compensate(ctx)` mengambil context dict bersama. Aksi yang gagal me-raise exception.
- Lacak langkah yang selesai; saat exception, iterasi `reversed(completed)` memanggil tiap `compensate`.
- Kembalikan sesuatu seperti `{"status": "committed"|"aborted", "committed": [names], "compensated": [names urutan undo], "failed_at": name|None}`.
:::

## ✅ Cek cepat

:::quiz
Kenapa kamu tak bisa memakai satu transaksi database untuk membuat operasi multi-layanan atomik?

Karena tiap layanan punya database sendiri, dan transaksi hanya mencakup satu database. Untuk menjaga seluruh operasi konsisten lintas layanan kamu memakai saga: rantai transaksi lokal, masing-masing dengan kompensasi yang membatalkannya kalau langkah berikutnya gagal.
:::

:::quiz
Apa itu aksi kompensasi, dan bagaimana ia berbeda dari rollback?

Ia aksi bisnis yang membatalkan langkah yang selesai — lepas stok, kembalikan pembayaran, batalkan pengiriman. Tidak seperti rollback database (yang menghapus perubahan yang belum commit secara otomatis), kompensasi adalah kerja nyata yang kamu jalankan eksplisit, karena langkahnya sudah commit di layanan lain.
:::

## 📚 Lanjut belajar

- [Microservices.io: Saga pattern](https://microservices.io/patterns/data/saga.html)
- [AWS: saga pattern](https://docs.aws.amazon.com/prescriptive-guidance/latest/cloud-design-patterns/saga.html)
- [Martin Kleppmann, *DDIA*, Ch. 7 (transactions)](https://dataintensive.net/)

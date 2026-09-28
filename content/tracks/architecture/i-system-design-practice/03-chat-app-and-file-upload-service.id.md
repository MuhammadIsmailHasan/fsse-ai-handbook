---
title: "Chat App & File Upload Service"
summary: Dua desain klasik lagi — chat real-time (WebSocket vs polling, menyimpan dan mengurutkan pesan, presence) dan layanan upload berkas yang mengirim berkas besar langsung ke object storage dengan presigned URL dan chunk yang bisa dilanjutkan.
sourceHash: e417a1a180da
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Pengiriman real-time: **polling** vs **WebSocket**, dan kapan masing-masing cocok
- Menyimpan dan **mengurutkan** pesan chat per percakapan
- **Presence** (siapa yang online) dan fan-out ke anggota percakapan
- Mengupload berkas besar tanpa mencekik server-mu: **presigned URL** ke object storage
- Upload **chunk / bisa dilanjutkan** untuk koneksi besar atau labil
- Melayani berkas dengan cepat lewat **CDN**

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Polling** | Klien terus bertanya "ada yang baru?" |
| **WebSocket** | Koneksi dua arah yang tetap terbuka untuk push langsung |
| **Presence** | Apakah user online sekarang |
| **Object storage** | Penyimpan berkas/blob (seperti S3) |
| **Presigned URL** | Tautan sementara yang membiarkan klien upload langsung ke storage |
| **Chunk** | Potongan berkas besar yang diupload terpisah |
| **Resumable** | Bisa melanjutkan upload setelah putus |
| **CDN** | Server tepi yang melayani berkas dekat user |

## 🧠 Ide besarnya

- **Chat** adalah perbedaan antara **mengecek kotak surat tiap menit** (polling) dan **punya jalur telepon terbuka** (WebSocket) — jalur terbuka mengirim saat sesuatu diucapkan, alih-alih kamu bertanya berulang-ulang.
- **Upload berkas** seperti **mengirim lemari**: kamu tak membawanya melewati kantor depan (app server-mu). Kamu memberi kurir **alamat langsung ke gudang** (presigned URL ke object storage), dan untuk barang besar kamu mengirimnya dalam **kotak** (chunk) yang bisa dikirim ulang kalau satu hilang.

## ❓ Kenapa ini penting

Keduanya terlihat sederhana ("kirim pesan saja", "upload berkas saja") dan keduanya menghukum desain naif. Polling untuk chat memboroskan sumber daya besar dan tetap terasa lambat. Mengupload berkas besar *melewati* app server-mu menahan memori dan bandwidth dan tumbang pada koneksi putus. Pola yang tepat — WebSocket dan upload chunk langsung-ke-storage — yang dipakai produk nyata, dan muncul terus di wawancara.

## 📖 Langkah demi langkah

### Bagian A — Chat real-time

**1. Requirement**: kirim/terima pesan mendekati real-time; chat 1:1 dan grup; riwayat pesan; urutan; idealnya presence dan tanda terima kirim/baca.

**2. Pengiriman: polling vs WebSocket**

| | Polling | WebSocket |
|---|---|---|
| Cara | Klien bertanya tiap beberapa detik | Server push lewat koneksi terbuka |
| Latensi | Lambat (sampai interval poll) | Instan |
| Beban server | Boros (banyak pengecekan kosong) | Efisien untuk update langsung |
| Terbaik untuk | Update jarang | Chat, feed langsung, presence |

Chat ingin **WebSocket** (atau transport push serupa): server mendorong pesan baru ke penerima yang terhubung seketika.

**3. Menyimpan dan mengurutkan pesan**: simpan pesan per **percakapan**. Urutkan dengan **nomor urut per-percakapan** atau timestamp yang andal — bukan jam klien, yang bisa salah. Baca memakai paginasi cursor (Stage F) untuk memuat riwayat.

```
messages( id, conversation_id, sender_id, seq BIGINT, body, created_at )
-- ordered within a conversation by seq
```

**4. Fan-out dan presence**: saat pesan tiba, kirim ke anggota percakapan yang terhubung (lewat WebSocket mereka), dan simpan untuk yang offline untuk diambil nanti. **Presence** (online/offline) disimpan di penyimpanan cepat (Redis) dan diperbarui saat koneksi buka/tutup.

**5. Catatan skala**: dengan banyak server, user di server *berbeda* harus tetap bisa saling menjangkau. Pub/sub bersama (mis. Redis pub/sub) merutekan pesan ke server mana pun yang memegang koneksi penerima.

### Bagian B — Layanan upload berkas

**1. Requirement**: upload berkas (sebagian besar) dengan andal; simpan tahan lama; layani cepat; tangani koneksi mobile labil.

**2. Jangan upload lewat app server-mu.** Mengalirkan video 2 GB melewati proses web-mu memakan memori dan bandwidth. Sebaliknya, beri klien **presigned URL** — tautan sementara berlingkup-izin yang membiarkannya upload **langsung ke object storage** (S3). Server-mu hanya menerbitkan tautan dan mencatat metadata.

```
1. client → app: "I want to upload video.mp4"
2. app → client: presigned URL (valid 15 min, write-only, this key)
3. client → object storage: PUT the file directly
4. client → app: "done" ; app saves metadata (owner, key, size)
```

**3. Upload chunk / bisa dilanjutkan**: untuk berkas besar atau koneksi goyah, bagi berkas menjadi **chunk** dan upload terpisah. Kalau satu chunk gagal, kirim ulang chunk itu saja — tanpa memulai ulang seluruh upload. Saat semua chunk masuk, upload **selesai** dan bisa dirakit.

**4. Metadata vs blob**: simpan *byte berkas* di object storage; simpan *metadata* (owner, nama berkas, ukuran, content-type, key) di database-mu. Ini mencerminkan pelajaran pastebin: DB untuk data terstruktur kecil, object storage untuk blob besar.

**5. Melayani cepat**: taruh **CDN** di depan object storage supaya unduhan datang dari tepi dekat user. Pakai presigned URL berumur pendek (atau signed CDN URL) untuk berkas privat.

### Pilih pendekatan

| Kebutuhan | Lakukan ini |
|---|---|
| Pesan langsung / presence | WebSocket + Redis pub/sub lintas server |
| Update jarang saja | Polling cukup dan lebih sederhana |
| Upload berkas besar apa pun | Presigned URL langsung ke object storage |
| Upload besar / labil | Upload chunk, bisa dilanjutkan |
| Unduhan global cepat | CDN di depan storage |

- ✅ Urutkan chat dengan urutan yang ditetapkan server, bukan jam klien.
- ✅ Upload berkas besar langsung-ke-storage dengan presigned URL; simpan hanya metadata di DB.
- ✅ Chunk upload besar/labil supaya kegagalan mengirim ulang satu chunk, bukan semuanya.
- 🚫 Jangan polling untuk chat real-time, dan jangan alirkan berkas besar lewat app server-mu.

## ⚠️ Kesalahan umum

- Polling tiap detik untuk chat — beban berat dan tetap lambat; pakai WebSocket.
- Mengurutkan pesan dengan jam klien, sehingga pesan tampil tak berurutan.
- Mengupload berkas besar lewat app server, menghabiskan memori dan gagal saat putus.
- Menyimpan byte berkas di database alih-alih object storage.
- Tak ada resumability, sehingga koneksi putus memulai ulang upload besar dari nol.

:::revoshop
Dua kemungkinan fitur RevoShop. (1) **Chat penjual–pembeli**: apakah kamu akan polling atau memakai WebSocket, bagaimana kamu mengurutkan dan menyimpan pesan, dan di mana presence tinggal? (2) **Upload gambar produk**: sketsa alur presigned-URL supaya gambar langsung ke object storage (bukan lewat Flask), metadata apa yang kamu simpan di PostgreSQL, dan bagaimana CDN mempercepat penyajian gambar produk.
:::

## 🏆 Praktik terbaik

- [ ] Pakai WebSocket (atau push serupa) untuk real-time; cadangkan polling untuk update jarang.
- [ ] Tetapkan urutan/timestamp sisi-server untuk pengurutan pesan; paginasi riwayat dengan cursor.
- [ ] Simpan presence dan routing lintas-server di penyimpanan bersama / pub-sub.
- [ ] Upload berkas besar langsung ke object storage lewat presigned URL berumur pendek.
- [ ] Chunk upload besar untuk resumability; verifikasi semua chunk sebelum menandai selesai.
- [ ] Simpan blob di object storage dan metadata di DB; layani lewat CDN.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan polling vs WebSocket dengan analogi kotak-surat vs jalur-telepon-terbuka. Lalu jelaskan presigned upload dengan analogi kirim-lemari-langsung-ke-gudang, termasuk kenapa chunk membantu pada koneksi labil.

## 📐 Rancang

Rancang upload berkas untuk CareerPilot: user mengupload CV (PDF kecil) dan, pada beberapa paket, **video** perkenalan singkat (sampai 500 MB) dari mobile. Rancang jalur upload untuk keduanya, bagaimana kamu menangani upload video besar yang labil, apa yang kamu simpan di mana, dan bagaimana kamu melayani berkas kembali dengan cepat dan privat.

:::quiz
Tampilkan satu rancangan yang mungkin

**CV (PDF kecil):** tetap pakai **presigned URL** ke object storage supaya byte tak pernah melewati app server. Aplikasi menerbitkan URL, klien PUT langsung, lalu aplikasi menyimpan metadata (`user_id`, `key`, `size`, `content_type`) di PostgreSQL. Satu PUT cukup pada ukuran ini.

**Video perkenalan (sampai 500 MB, mobile):** pakai upload **chunk, bisa dilanjutkan** — bagi menjadi, katakanlah, chunk 5–10 MB, masing-masing dengan presigned URL sendiri; kirim ulang hanya chunk yang gagal. Tandai upload selesai hanya saat tiap chunk ada, lalu rakit/finalisasi di object storage.

**Pembagian penyimpanan:** blob (PDF, video) di object storage; metadata di DB. Jangan pernah simpan byte video di PostgreSQL.

**Melayani privat + cepat:** layani lewat **CDN** dengan **signed URL berumur pendek** supaya hanya pemilik (atau penonton berwenang) bisa mengambil, dan unduhan datang dari tepi dekat user.

**Aturan yang ditunjukkan:** upload presigned langsung-ke-storage untuk semuanya, chunk/bisa-dilanjutkan untuk berkas besar labil, metadata di DB, dan CDN dengan signed URL untuk penyajian privat yang cepat.
:::

### 📝 Checklist review mandiri

- [ ] Upload langsung ke object storage (bukan lewat app server)
- [ ] Upload besar/labil di-chunk dan bisa dilanjutkan
- [ ] Blob di object storage, metadata di DB
- [ ] Penyajian cepat (CDN) dan terkontrol akses (signed URL)

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/architecture/i-system-design-practice/03-chunked-upload" ai="no-ai" title="Pelacak upload chunk yang bisa dilanjutkan"}
Implementasikan pelacak di balik upload yang bisa dilanjutkan: terima chunk berdasarkan indeks (idempoten), laporkan chunk mana yang masih hilang, beri tahu kapan upload selesai, dan rakit chunk secara berurutan begitu semuanya ada. Tes mengirim ulang chunk duplikat dan menyelesaikan upload di luar urutan.
:::

:::hints
- Simpan chunk yang diterima di dict `{index: data}`; `receive` kembalikan `"stored"` atau `"duplicate"` (sudah punya indeks itu).
- `missing()` = daftar terurut indeks di `range(total)` yang belum diterima.
- `is_complete()` = kita punya semua `total` indeks. `assemble()` raise kalau belum lengkap, kalau tidak kembalikan data urut indeks (`0..total-1`).
:::

## ✅ Cek cepat

:::quiz
Kenapa WebSocket lebih cocok daripada polling untuk aplikasi chat?

Polling membuat klien bertanya berulang, memboroskan sumber daya pada pengecekan yang kebanyakan kosong dan tetap lambat sampai interval poll. WebSocket menjaga koneksi terbuka supaya server mendorong tiap pesan baru seketika — latensi lebih rendah dan beban terbuang jauh lebih sedikit untuk update langsung.
:::

:::quiz
Kenapa mengupload berkas besar dengan presigned URL ke object storage alih-alih lewat app server-mu?

Karena mengalirkan berkas besar lewat app server menghabiskan memori dan bandwidth-nya dan gagal parah pada koneksi putus. Presigned URL membiarkan klien upload langsung ke object storage tahan lama; server hanya menerbitkan tautan dan mencatat metadata, dan chunking membuat upload bisa dilanjutkan.
:::

## 📚 Lanjut belajar

- [MDN: WebSockets API](https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API)
- [AWS S3: presigned URLs](https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html)
- [AWS S3: multipart (chunked) upload](https://docs.aws.amazon.com/AmazonS3/latest/userguide/mpuoverview.html)

---
title: "How to Approach System Design"
summary: Kerangka berulang untuk pertanyaan system design apa pun — perjelas requirement, perkirakan skala, sketsa API dan model data, lalu desain tingkat tinggi dan bottleneck — dikerjakan tuntas pada URL shortener klasik.
sourceHash: addd0404b521
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- **Kerangka** langkah demi langkah yang bisa kamu pakai untuk pertanyaan desain apa pun
- Cara mengubah prompt kabur menjadi **requirement** jelas
- Perkiraan skala **back-of-the-envelope** kasar
- Menyketsa **API** dan **model data** sebelum menggambar kotak
- Contoh lengkap: merancang **URL shortener**
- Cara membahas **bottleneck** dan trade-off seperti engineer senior

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Functional requirement** | Apa yang harus *dilakukan* sistem |
| **Non-functional** | Seberapa baik ia harus melakukannya (cepat, andal) |
| **Back-of-envelope** | Perkiraan kasar untuk mengukur sistem |
| **Read-heavy** | Jauh lebih banyak baca daripada tulis |
| **Bottleneck** | Bagian yang membatasi seluruh sistem |
| **Base62** | Menyandi angka memakai 0-9, a-z, A-Z |

## 🧠 Ide besarnya

Pertanyaan system design seperti diminta **merancang rumah**. Kamu tak langsung memasang bata. Kamu pertama bertanya **siapa yang tinggal di sini dan apa kebutuhannya** (requirement), memperkirakan **seberapa besar** (skala), menyepakati **ruangan dan pintu** (API dan data), lalu menyketsa **denah** (desain tingkat tinggi), dan akhirnya mengecek **di mana ia bisa retak** (bottleneck). Urutan yang sama, tiap kali.

## ❓ Kenapa ini penting

System design muncul di wawancara senior dan, lebih penting, di proyek nyata saat kamu merencanakan fitur. Pemula membeku karena promptnya ("rancang Twitter") terasa raksasa. **Kerangka** mengubah kepanikan itu menjadi percakapan tenang dan berurutan — dan pewawancara menilai *proses dan trade-off*-mu, bukan satu jawaban benar ajaib.

## 📖 Langkah demi langkah

### Kerangkanya (hafalkan urutan ini)

1. **Perjelas requirement** — functional (apa yang dilakukan) dan non-functional (skala, latensi, keandalan). Ajukan pertanyaan; jangan mengasumsikan.
2. **Perkirakan skala** — baca/tulis per detik dan penyimpanan secara kasar. Ini menentukan semua yang di bawahnya.
3. **Definisikan API** — segelintir endpoint, input dan output-nya.
4. **Rancang model data** — tabel/entitas utama dan kuncinya.
5. **Desain tingkat tinggi** — kotak-kotaknya (klien, server, database, cache) dan bagaimana request mengalir.
6. **Deep-dive & bottleneck** — temukan bagian yang paling tertekan dan atasi (cache, replika, sharding — dari pelajaran sebelumnya).

Sekarang mari terapkan keenamnya pada prompt nyata.

### Contoh dikerjakan: rancang URL shortener (seperti bit.ly)

**1. Requirement**
- Functional: diberi URL panjang, kembalikan yang pendek; mengunjungi URL pendek mengalihkan ke yang panjang.
- Non-functional: pengalihan harus **cepat** (ada di jalur kritis tiap klik), sangat tersedia, dan link tak boleh bentrok.
- Pertanyaan klarifikasi: alias kustom? kedaluwarsa link? analitik? (Asumsi: tak ada alias kustom untuk v1, kedaluwarsa opsional, hitungan klik dasar.)

**2. Perkirakan skala**
- Katakanlah 100 juta link baru/bulan, dan sangat **read-heavy** — orang mengklik jauh lebih banyak daripada membuat. Asumsikan rasio baca:tulis 100:1.
- Tulis ≈ 100 juta / (30 × 86.400) ≈ **~40 tulis/detik**; baca ≈ **~4.000 baca/detik**.
- Penyimpanan: 100 juta/bulan × 12 × ~500 byte ≈ puluhan GB/tahun — kecil. Tantangannya **baca cepat**, bukan penyimpanan.

**3. API**
```
POST /shorten   { "url": "https://very/long/link" }  → { "short": "aB3xY" }
GET  /{code}                                          → 302 redirect to the long URL
```

**4. Model data**
```
links( id BIGSERIAL PK, code VARCHAR UNIQUE, long_url TEXT,
       created_at, expires_at NULL, clicks BIGINT DEFAULT 0 )
```
Index `code` (tiap pengalihan mencari lewatnya).

**5. Membuat kode pendek**
Pakai `id` auto-increment baris dan sandi dalam **base62** (0-9, a-z, A-Z). String base62 panjang 7 mencakup 62⁷ ≈ 3,5 triliun link — cukup banyak — dan kodenya pendek serta bebas bentrok karena id unik.

```
id 125 → base62 → "cb"     (short, unique, no random collisions)
```

**6. Desain tingkat tinggi & bottleneck-nya**
```
             ┌──────── cache (Redis): code → long_url ───────┐
 client ──▶ app servers ──▶                                   ──▶ PostgreSQL
   click        │  (redirect: check cache, then DB)                (source of truth)
```
- **Bottleneck-nya baca pengalihan** (4.000/detik, kritis-latensi). Perbaiki dengan alat yang kamu pelajari: **cache** kode panas di Redis (kebanyakan klik ke link populer), tambah **read replica**, dan taruh pengalihan di belakang CDN/edge kalau global.
- Tulis hanya ~40/detik — satu primary PostgreSQL menanganinya dengan mudah.

### Sentuhan senior: trade-off dengan lantang

- Base62-dari-id vs kode acak: berbasis-id bebas bentrok dan sederhana, tapi membocorkan urutan/volume pembuatan kasar; kode acak atau ter-hash menyembunyikan itu dengan biaya pengecekan bentrok. Nyatakan trade-off-nya dan pilih satu.
- Pengalihan pakai `302` (sementara) kalau kamu ingin analitik klik pada tiap hit, atau `301` (permanen) untuk caching terbaik tapi analitik lebih sedikit. Sebutkan pilihannya.

### Memakai kerangkanya

| Langkah | Lewati dan… |
|---|---|
| Requirement | Kamu membangun hal yang salah |
| Perkirakan skala | Kamu over- atau under-engineer |
| API + model data | Kotakmu tak terhubung ke apa pun yang nyata |
| Desain tingkat tinggi | Kamu tak bisa menalar aliran |
| Bottleneck | Kamu melewatkan bagian yang benar-benar rusak |

- ✅ Selalu berurutan; ucapkan asumsimu dengan lantang.
- ✅ Biarkan angka skala menggerakkan desain (read-heavy → cache + replika).
- 🚫 Jangan langsung ke "microservice dan Kafka" sebelum requirement dan skala.

## ⚠️ Kesalahan umum

- Merancang sebelum klarifikasi — menyelesaikan masalah yang tak diminta pewawancara.
- Melewatkan perkiraan, lalu tak bisa membenarkan kenapa kamu butuh cache atau replika.
- Langsung ke teknologi kompleks (sharding, microservice) untuk sistem yang tak membutuhkannya.
- Melupakan rasio baca/tulis, yang biasanya menentukan seluruh bentuknya.
- Tak pernah menyebut trade-off — wawancaranya *tentang* trade-off.

:::revoshop
Terapkan kerangka ke fitur RevoShop: "rancang pencarian produk". (1) Requirement: apa yang harus dilakukan pencarian (per nama, kategori, harga), seberapa cepat, seberapa segar? (2) Perkiraan: apakah pencarian read-heavy? Kira-kira berapa pencarian/detik pada 10 ribu user harian? (3) Sketsa API, data/index yang dibutuhkan, dan sebutkan bottleneck yang mungkin (index full-text vs scan `LIKE`) dan cara memperbaikinya.
:::

## 🏆 Praktik terbaik

- [ ] Mulai tiap desain dengan requirement functional + non-functional dan pertanyaan klarifikasi.
- [ ] Lakukan matematika skala kasar; biarkan rasio baca/tulis dan penyimpanan menggerakkan desain.
- [ ] Definisikan API dan model data sebelum menggambar arsitektur.
- [ ] Identifikasi satu bottleneck terbesar dan atasi dengan alat yang dikenal (cache, replika, sharding).
- [ ] Ucapkan trade-off dengan lantang dan buat pilihan eksplisit.
- [ ] Jaga v1 sesederhana yang diizinkan requirement; catat apa yang akan kamu tambahkan nanti.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan kerangka enam langkah memakai analogi merancang-rumah. Lalu, dalam dua kalimat, katakan kenapa URL shortener "read-heavy" dan apa implikasinya bagi desainnya.

## 📐 Rancang

Pakai kerangka lengkap untuk merancang **pastebin** (user menempel teks, mendapat link pendek yang bisa dilihat orang lain; paste bisa kedaluwarsa). Lalui keenam langkah: requirement, perkiraan skala, API, model data, desain tingkat tinggi, dan bottleneck utama dengan perbaikannya.

:::quiz
Tampilkan satu rancangan yang mungkin

- **Requirement**: buat paste (teks, kedaluwarsa opsional, sintaks opsional), lihat paste lewat id pendeknya; baca cepat, link privat-lewat-ketidakjelasan; tanpa edit di v1.
- **Skala**: read-heavy seperti URL shortener (lebih banyak lihat daripada buat). Katakan 1 juta paste/bulan → ~0,4 tulis/detik, ~40 baca/detik pada 100:1 — kecil; penyimpanan tumbuh dengan ukuran teks, jadi batasi ukuran paste (mis. 1 MB) dan simpan body besar di object storage (S3), simpan metadata di DB.
- **API**: `POST /pastes {text, expires_at?}` → `{id}`; `GET /{id}` → paste-nya (atau 404/410 kalau kedaluwarsa).
- **Model data**: `pastes(id, code UNIQUE, body_ref, created_at, expires_at)`. Kode lewat base62 dari id.
- **Tingkat tinggi**: klien → app server → PostgreSQL (metadata) + object storage (body besar); cache Redis untuk paste panas.
- **Bottleneck**: latensi baca pada paste populer dan body besar. Perbaiki: cache paste panas di Redis, layani body besar dari object storage/CDN, dan job latar belakang menghapus paste kedaluwarsa.

**Aturan yang ditunjukkan:** kerangka enam-langkah yang sama dan alat yang sama (cache, replika, object storage) menyelesaikan prompt baru — skill-nya adalah prosesnya, bukan jawaban yang dihafal.
:::

### 📝 Checklist review mandiri

- [ ] Requirement (functional + non-functional) dinyatakan dengan asumsi
- [ ] Perkiraan skala kasar yang menggerakkan desain
- [ ] API dan model data didefinisikan sebelum arsitektur
- [ ] Satu bottleneck jelas disebutkan dan diatasi dengan alat yang dikenal

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/architecture/i-system-design-practice/01-url-shortener" ai="no-ai" title="Kode pendek base62 dan perkiraan kapasitas"}
Implementasikan inti URL shortener: sandi id auto-increment ke kode pendek base62 dan sandi baliknya, plus beberapa helper back-of-the-envelope (tulis/detik dari volume bulanan, dan berapa link yang bisa dialamati oleh panjang kode). Tes memeriksa round-trip dan perkiraannya.
:::

:::hints
- Alfabet base62: `0-9` lalu `a-z` lalu `A-Z` (indeks 0–61). `encode(0)` harus `"0"`.
- `encode`: berulang ambil `n % 62`, tambahkan huruf di depan, `n //= 62`. `decode`: lipat digit kembali dengan `n = n*62 + value`.
- `writes_per_sec(monthly)` = `monthly / (30 * 86400)`. `capacity(code_len)` = `62 ** code_len`.
:::

## ✅ Cek cepat

:::quiz
Apa dua langkah pertama kerangka, dan kenapa mereka datang lebih dulu?

Perjelas requirement (functional + non-functional), lalu perkirakan skala. Mereka datang lebih dulu karena mendefinisikan *apa* yang kamu bangun dan *seberapa besar*, yang menggerakkan tiap keputusan selanjutnya — API, model data, dan terutama di mana bottleneck (dan kebutuhan cache/replika) akan berada.
:::

:::quiz
URL shortener sangat didominasi baca. Apa implikasinya bagi desainnya?

Bahwa jalur pengalihan (baca) adalah bottleneck kritis, bukan tulis atau penyimpanan. Kamu mengoptimalkan baca: cache kode panas di Redis, tambah read replica, dan mungkin layani pengalihan dari CDN/edge, sementara satu primary dengan mudah menangani volume tulis yang kecil.
:::

## 📚 Lanjut belajar

- [System Design Primer (GitHub)](https://github.com/donnemartin/system-design-primer)
- [ByteByteGo: how to answer a system design interview](https://bytebytego.com/)
- [Designing a URL shortener — worked example](https://www.educative.io/courses/grokking-the-system-design-interview/m2ygV4E81AR)

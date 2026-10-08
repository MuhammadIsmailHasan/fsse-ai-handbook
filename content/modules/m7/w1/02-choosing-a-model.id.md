---
title: "Choosing a Model: Cost, Latency & Quality"
summary: "Pilih model dengan bukti, bukan hype — bandingkan kualitas, biaya, kecepatan, ukuran konteks dan aturan data pada kasus ujimu sendiri, pakai model termurah yang cukup baik, dan jaga kodemu siap berganti."
sourceHash: 8ab6dfcd362c
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- **Lima hal** yang dibandingkan saat memilih model
- Kenapa kamu menguji pada **contohmu sendiri**, bukan leaderboard
- Aturan **model termurah yang cukup baik**
- Tiga cara menghemat uang: **cascade**, **caching**, **batching**
- Cara menjaga app-mu **siap berganti** model

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Tier model** | Kecil dan cepat, seimbang, atau besar dan kuat |
| **Latency** | Berapa lama user menunggu jawaban |
| **Time to first token** | Waktu tunggu sebelum kata pertama muncul |
| **Throughput** | Berapa banyak request yang bisa dijalankan per menit |
| **Open-weight model** | Model yang file-nya bisa diunduh dan dijalankan sendiri |
| **Cascade** | Coba model murah dulu, naikkan hanya jika perlu |
| **Prompt caching** | Bayar lebih sedikit untuk awalan prompt yang dikirim ulang |
| **Deprecation** | Penyedia mempensiunkan versi model |

## 🧠 Ide besarnya

Memilih model itu seperti **memilih kendaraan untuk bisnis pengiriman**. Motor (model kecil) murah, cepat dan cukup untuk amplop. Truk (model besar) membawa lebih banyak dan menangani muatan sulit, tapi tiap perjalanan lebih mahal dan lebih lama mulai. Kamu tidak mengirim truk untuk mengantar surat, dan tidak mengirim motor untuk memindahkan kulkas.

Jadi aturannya sederhana: pakai **model termurah dan tercepat yang mengerjakan tugas ini dengan cukup baik**, dan buktikan "cukup baik" dengan angka.

## ❓ Kenapa ini penting

Model biasanya baris terbesar di tagihan fitur AI, dan menentukan kecepatan yang dirasakan user. Tim membuat dua kesalahan mahal:

- memakai model terbesar untuk semuanya, lalu melihat tagihan dan waktu tunggu meledak,
- memilih model karena sebuah blog bilang "terbaik", lalu mendapati ia gagal pada data **mereka**.

Model juga berubah cepat. Versi baru datang, yang lama dipensiunkan, dan harga bergerak. Tim yang menguji dengan data dan menjaga antarmuka bersih bisa berganti dalam sehari. Tim yang menebak dan meng-hardcode nama bisa terjebak berminggu-minggu.

## 📖 Langkah demi langkah

### 1. Lima hal yang dibandingkan

| Hal | Pertanyaan | Cara mengecek |
|---|---|---|
| **Kualitas** | Apakah ia mengerjakan tugas *-ku* dengan benar? | set ujimu sendiri (di bawah) |
| **Biaya** | Berapa harga per panggilan pada ukuranku? | token × harga; `usage` di response |
| **Latency** | Cukup cepat untuk layar ini? | ukur time to first token dan waktu total |
| **Konteks & batas** | Apakah masukanku muat? Berapa request per menit? | ukuran jendela, rate limit |
| **Fitur & aturan** | Tool, gambar, mode JSON, region, retensi data, lisensi | dokumen penyedia, aturan legal/keamananmu |

Jangan berhenti di "kualitas". Jawaban bagus setelah 25 detik adalah fitur gagal untuk widget chat. Model murah yang membocorkan data pelanggan ke region yang salah adalah fitur gagal untuk bank.

### 2. Tier, dengan kata sederhana

Setiap penyedia besar menjual beberapa tier. Namanya berubah, idenya tidak:

| Tier | Cocok untuk | Kompromi |
|---|---|---|
| **Kecil / cepat** | klasifikasi, routing, ekstraksi, jawaban pendek, volume tinggi | lebih lemah untuk penalaran sulit dan tugas panjang |
| **Seimbang** | kebanyakan fitur produk, bantuan koding, jawaban support | pilihan bawaan yang masuk akal |
| **Besar / unggulan** | penalaran sulit, kerja multi-langkah panjang, dokumen rumit | paling lambat dan paling mahal |

Banyak penyedia juga membiarkanmu mengatur **seberapa keras model berpikir** (pengaturan penalaran atau *effort*). Model kuat pada effort rendah bisa menyamai model lama pada effort tinggi dengan biaya lebih murah, jadi ukur opsi itu sebelum menambah model kedua.

Harga dan nama sering berubah, jadi selalu baca halaman harga dan model penyedia saat memutuskan.

### 3. Uji pada contohmu sendiri

Leaderboard menguji kemampuan *umum*. Produkmu butuh kemampuan *-mu*: bahasamu, dokumenmu, nadamu.

1. Kumpulkan **20–50 contoh nyata** masukan (pertanyaan pelanggan, invoice, deskripsi pekerjaan). Sertakan yang mudah, sulit dan kasus tepi yang jahat.
2. Tulis seperti apa **jawaban yang baik** untuk tiap contoh (label, jawaban pendek, atau daftar cek).
3. Jalankan **prompt yang sama** di 2–3 model.
4. Catat **kualitas** (berapa yang benar), **biaya**, **time to first token** dan **waktu total**.
5. Pilih model termurah yang lolos standar kualitasmu.

Ini *eval* kecil. Kamu akan membangun yang sebenarnya di minggu 5. Bahkan spreadsheet 30 baris mengalahkan opini.

### 4. Pilih dengan angka

```python
def call_cost(model, input_tokens, output_tokens):
    return input_tokens * model["input_price"] / 1_000_000 + output_tokens * model["output_price"] / 1_000_000


def choose_model(models, *, min_quality, max_latency_s, input_tokens, output_tokens):
    ok = [
        m for m in models
        if m["quality"] >= min_quality
        and m["latency_s"] <= max_latency_s
        and m["context"] >= input_tokens + output_tokens
    ]
    if not ok:
        return None
    best = min(ok, key=lambda m: (call_cost(m, input_tokens, output_tokens), m["latency_s"], m["name"]))
    return best["name"]
```

Bacalah seperti resep: **saring** dengan batas keras (kualitas, kecepatan, ukuran), lalu ambil yang **termurah** dari sisanya. Kalau tak ada yang tersisa, jawaban jujurnya "tak ada model ini yang cocok; ubah kebutuhan atau rancangannya".

### 5. Penghemat 1: cascade

Kebanyakan request mudah. Kirim ke model murah, dan **naikkan hanya saat jawaban tampak salah**.

```python
def run_cascade(models_cheapest_first, ask, is_good):
    total = 0.0
    for name in models_cheapest_first:
        answer, cost = ask(name)
        total += cost                      # failed attempts still cost money
        if is_good(answer):
            return name, answer, total
    return None
```

Ini hanya bekerja jika `is_good` **andal**: pengecekan schema, aturan, field kepercayaan diri, atau pengecekan murah kedua. Kalau pengecekan kualitasmu lemah, cascade diam-diam meloloskan jawaban buruk. Hitung juga percobaan yang gagal dalam biaya, dan ingat bahwa dua panggilan lebih lama daripada satu.

### 6. Penghemat 2: prompt caching

Banyak app mengirim awalan panjang yang sama di setiap panggilan (system prompt, aturan, dokumen kebijakan). Penyedia dapat menyimpan awalan itu dan menagih **sebagian kecil** untuk bagian yang di-cache pada panggilan berikutnya (sering sekitar sepersepuluh harga masukan normal).

```python
def monthly_cost(model, requests_per_day, input_tokens, output_tokens, cache_hit_rate=0.0, days=30):
    price_in = model["input_price"] * ((1 - cache_hit_rate) + cache_hit_rate * 0.1)
    per_call = input_tokens * price_in / 1_000_000 + output_tokens * model["output_price"] / 1_000_000
    return per_call * requests_per_day * days
```

Agar caching bekerja: taruh konten **stabil** lebih dulu (instruksi, dokumen) dan konten **berubah** terakhir (pertanyaan user), dan jaga bagian stabil identik sampai ke byte. Timestamp di atas prompt menghancurkan cache.

### 7. Penghemat 3: batch untuk pekerjaan lambat

Jika tak ada yang menunggu (ringkasan malam, pelabelan dataset, menjalankan eval), pakai **batch API** penyedia. Biasanya berjalan asinkron dalam sehari dan berbiaya sekitar separuh. Pakai panggilan normal hanya untuk layar tempat manusia menunggu.

### 8. Model open-weight dan lokal

Model open-weight bisa dijalankan di server atau laptopmu sendiri (minggu 1, lesson 5):

| | Model API | Lokal / self-hosted |
|---|---|---|
| Kualitas di kelas teratas | biasanya lebih tinggi | biasanya lebih rendah |
| Bentuk biaya | bayar per token | bayar perangkat keras, lalu "gratis" per panggilan |
| Privasi | data ke penyedia (baca ketentuannya) | data tetap padamu |
| Operasional | tidak ada | kamu menjalankan, memperbarui, memantau |
| Cocok untuk | kebanyakan produk | data privat, pemakaian offline, belajar, kerja massal murah |

Tak ada yang "lebih baik". Pilih berdasarkan aturan data, volume dan tim yang kamu punya.

### 9. Tetap siap berganti

Model digantikan. Lindungi dirimu:

- taruh nama model dan harga di **konfigurasi**, bukan di kode,
- bungkus panggilan dalam **satu antarmuka kecil** (`complete(messages) -> text`) agar penyedia bisa ditukar atau dicampur,
- **pin** versi model tepat saat butuh perilaku stabil, dan baca pemberitahuan deprecation,
- simpan **set ujimu**. Saat model baru muncul, jalankan melalui set yang sama sebelum berganti,
- catat model mana yang menjawab setiap request.

### Memilih caranya

| Situasi | Lakukan ini |
|---|---|
| Mudah, volume tinggi (tagging, routing) | model kecil |
| Fitur produk umum | model seimbang, uji satu tier di bawahnya |
| Penalaran sulit, dokumen panjang | model besar, mungkin dengan effort berpikir lebih tinggi |
| Awalan panjang yang sama di tiap panggilan | prompt caching |
| Tak ada yang menunggu jawaban | batch API |
| Data privat atau tanpa internet | model lokal, atau penyedia dengan ketentuan data yang tepat |
| Tidak yakin | buat tes 30 baris, ukur tiga model |

- ✅ Putuskan dengan set uji, lalu uji ulang saat model berubah.
- 🚫 "Model terbesar, biar aman."
- 🚫 Nama model hardcode di dua belas file.

## ⚠️ Kesalahan umum

- Memilih berdasarkan skor benchmark atau opini teman.
- Membandingkan model dengan prompt berbeda (itu bukan tes yang adil).
- Hanya melihat harga per token, bukan **biaya per tugas selesai** (model murah yang butuh tiga percobaan tidak murah).
- Mengabaikan latency sampai user mengeluh.
- Cascade dengan pengecekan "apakah ini bagus?" yang lemah.
- Awalan yang di-cache berubah sedikit di tiap panggilan.
- Tidak punya rencana untuk deprecation.

:::revoshop
RevoShop bisa memakai AI di tiga tempat: (1) menandai ulasan produk positif atau negatif, (2) menjawab "di mana pesananku?" dengan data pesanan, (3) menulis email penolakan refund yang sopan. Untuk masing-masing, katakan tier mana yang kamu uji dulu, apa standar kualitasnya, dan berapa detik yang diterima pelanggan.
:::

## 🏆 Praktik terbaik

- [ ] Tulis kebutuhan dulu: standar kualitas, waktu tunggu maksimum, volume, aturan data.
- [ ] Uji 2–3 model pada 20–50 contohmu sendiri sebelum memutuskan.
- [ ] Bandingkan **biaya per tugas selesai**, bukan hanya harga per token.
- [ ] Mulai dengan tier termurah yang mungkin berhasil, dan naik hanya dengan bukti.
- [ ] Pakai caching untuk awalan stabil dan batching untuk pekerjaan yang tak ditunggu.
- [ ] Simpan nama model dan harga di config, di balik satu antarmuka.
- [ ] Jalankan ulang set ujimu saat model baru muncul atau yang lama dipensiunkan.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke product manager kenapa "pakai model terbaik" bukan rencana, dengan gambaran motor dan truk. Dua angka apa yang kamu minta darinya?

## 📐 Rancang

SupportDesk AI menerima 20.000 pesan pelanggan sehari. Sekitar 70% sederhana ("di mana pesananku?", "bagaimana reset password?"); 30% rumit (sengketa refund, beberapa masalah dalam satu pesan). Jawaban harus mulai muncul dalam kurang dari 2 detik. Rancang susunan modelnya: model apa, bagaimana request dirutekan, bagaimana kamu mengecek kualitas, dan bagaimana mengendalikan biaya.

:::quiz
Tampilkan rancangan yang mungkin

- **Langkah 1, rute (model kecil, cepat):** klasifikasikan tiap pesan sebagai sederhana atau rumit, dan deteksi topik/bahasa. Ini panggilan murah dan pendek.
- **Langkah 2, jawab:** pesan sederhana ke model **seimbang** dengan artikel bantuan hasil retrieval; yang rumit ke model **lebih besar**, atau model yang sama dengan effort penalaran lebih tinggi, atau ke manusia.
- **Pengecekan cascade:** jawaban harus lolos pengecekan murah (mengutip artikel bantuan, cocok dengan schema, tanpa kata kunci kebijakan). Jika tidak, naik satu tier.
- **Latency:** stream token supaya kata pertama muncul dalam sekitar satu detik; jaga prompt router tetap pendek; cache system prompt bersama.
- **Kualitas:** set uji 200 pesan nyata berlabel (sederhana dan sulit); ukur akurasi penyelesaian per tier sebelum rilis dan tiap minggu sesudahnya. Pantau tingkat handoff ke manusia dan jempol-bawah.
- **Biaya:** perkirakan per tier (token × harga × volume), harapkan 70% lalu lintas sederhana mendominasi volume, dan pasang alarm anggaran harian. Pakai batch API untuk eval malam.
- **Berganti:** nama model dan harga di config, satu antarmuka `complete()`, catatan model yang dipakai per jawaban.
- **Privasi:** cek ketentuan data penyedia untuk data pelanggan; samarkan data pribadi di prompt jika bisa.

**Aturan yang ditunjukkan:** rutekan menurut kesulitan, cek jawaban murah, naik hanya bila perlu, dan ukur semuanya.
:::

### 📝 Daftar cek diri

- [ ] Aku menyebut kualitas, biaya, latency, ukuran dan aturan data
- [ ] Pilihan didukung tes pada contoh nyata
- [ ] Ada pengecekan andal sebelum menaikkan tier
- [ ] Nama model dan harga ada di config

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m7/w1/02-model-choice" ai="no-ai" title="Pilih model dengan angka"}
Tulis `call_cost`, `choose_model` (model termurah yang memenuhi batas kualitas, kecepatan dan konteks; seri dimenangkan yang lebih cepat), `monthly_cost` (dengan cache hit rate yang masukan ter-cache berbiaya 10%) dan `run_cascade` (murah dulu; biaya termasuk percobaan gagal). Tak perlu API key.
:::

:::hints
- `choose_model`: saring dulu, lalu `min(..., key=(cost, latency, name))`.
- Cek konteks: `model["context"] >= input_tokens + output_tokens`.
- `monthly_cost`: harga masukan efektif adalah `price * ((1 - h) + h * 0.1)`; keluaran tidak pernah di-cache.
- `run_cascade`: tambahkan `cost` ke total **sebelum** menguji `is_good`.
:::

## ✅ Cek cepat

:::quiz
Kenapa "biaya per tugas selesai" lebih baik daripada "harga per token"?

Model murah yang butuh beberapa percobaan, menghasilkan jawaban salah yang perlu diperbaiki manusia, atau menulis jawaban panjang bisa lebih mahal per pekerjaan selesai daripada model yang lebih mahal tapi benar sekali jalan. Bandingkan biaya total untuk mendapat hasil yang benar.
:::

:::quiz
Kapan cascade model menghemat uang, dan kapan malah merugikan?

Ia menghemat uang saat kebanyakan request mudah dan kamu punya cara andal membedakan jawaban bagus dari buruk. Ia merugikan saat pengecekan kualitas lemah (jawaban buruk lolos), saat kebanyakan request tetap naik tier (kamu membayar dua panggilan), atau saat tambahan waktu tunggu tidak dapat diterima.
:::

:::quiz
Kenapa nama model dan harga dijauhkan dari kodemu?

Model dipensiunkan, digantikan dan diubah harganya sering. Jika ada di konfigurasi di balik satu antarmuka, kamu bisa menguji model baru dan berganti (atau kembali) dengan mengubah satu pengaturan, bukan mengedit banyak file.
:::

## 📚 Lanjut belajar

- [Anthropic docs: Choosing a model](https://platform.claude.com/docs/en/about-claude/models/choosing-a-model)
- [Anthropic docs: Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [Anthropic docs: Batch processing](https://platform.claude.com/docs/en/build-with-claude/batch-processing)

---
title: "async/await: When It Helps"
summary: Panduan jujur tentang async di FastAPI — bagaimana await membebaskan server menangani request lain selama menunggu I/O, kenapa ia tak berguna untuk kerja terikat-CPU, dan bagaimana gather menjalankan banyak panggilan I/O sekaligus.
sourceHash: c6ed8308785d
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa yang sebenarnya dilakukan `async def` dan `await`
- Kenapa async membantu kerja **terikat-I/O** tapi bukan **terikat-CPU**
- Bagaimana server melayani request lain saat satu menunggu
- Menjalankan banyak panggilan I/O sekaligus dengan `asyncio.gather`
- Jebakannya: panggilan blocking di dalam async, dan memakai async di tempat tak berguna

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **async / await** | Menandai kode yang bisa jeda saat menunggu |
| **Terikat-I/O** | Kerja yang kebanyakan menunggu (jaringan, disk, DB) |
| **Terikat-CPU** | Kerja yang kebanyakan menghitung |
| **Event loop** | Penjadwal yang menjalankan tugas async |
| **Concurrency** | Membuat kemajuan banyak hal sekaligus |
| **gather** | Menjalankan beberapa awaitable pada saat yang sama |
| **Blocking** | Kode yang menghentikan semua selama jalan |

## 🧠 Ide besarnya

Async seperti **pelayan melayani banyak meja**. Selagi dapur memasak pesanan meja 1 (menunggu I/O), pelayan tak berdiri diam — ia mengambil pesanan meja 2 dan mengisi air meja 3. Satu pelayan, banyak meja, karena sebagian besar waktu dihabiskan *menunggu* dapur, bukan memasak. Tapi kalau pelayan harus memotong sendiri semua sayuran (kerja CPU), butuh tubuh kedua — satu pelayan tak bisa mempercepatnya.

## ❓ Kenapa ini penting

FastAPI populer sebagian karena membuat async mudah. Tapi async banyak disalahpahami: orang menaburkan `async` di mana-mana berharap kecepatan, atau memblokir event loop dan membuatnya *lebih lambat*. Aturan jujurnya — **async membantu saat kamu menunggu I/O, bukan saat menghitung** — yang membuatmu memakainya dengan benar. Untuk layanan yang memanggil database, API lain, dan model AI, async bisa melipatgandakan throughput; untuk hitung-hitungan, ia tak berguna.

## 📖 Langkah demi langkah

### 1. Apa yang dilakukan await

`await` menandai titik di mana fungsi bisa **jeda** selagi sesuatu yang lain selesai, menyerahkan kendali ke **event loop** supaya ia bisa menjalankan kerja lain:

```python
@app.get("/profile")
async def profile():
    user = await db.fetch_user()      # pause here; loop serves other requests
    posts = await api.fetch_posts()   # pause again
    return {"user": user, "posts": posts}
```

Selama tiap `await`, server tak macet — ia menangani request masuk lain. Itu seluruh kemenangannya.

### 2. Terikat-I/O vs terikat-CPU

| Jenis | Contoh | Async membantu? |
|---|---|---|
| **Terikat-I/O** | Query DB, panggilan HTTP, baca berkas, panggilan LLM | ✅ ya — menunggunya dibebaskan |
| **Terikat-CPU** | Resize gambar, matematika besar, parse berkas raksasa | 🚫 tidak — tak ada yang ditunggu |

Async tak menambah CPU. Kalau kerjanya *menghitung*, tak ada tunggu idle untuk dipakai ulang, jadi `async` tak memberi percepatan (dan bisa memblokir loop). Kerja CPU berat masuk ke worker latar belakang atau process pool.

### 3. Menjalankan panggilan bersamaan dengan gather

Dua panggilan I/O independen tak boleh jalan satu-demi-satu. `asyncio.gather` menjalankannya **pada saat yang sama**:

```python
import asyncio

# Sequential: total ≈ time(a) + time(b)
user = await fetch_user()
posts = await fetch_posts()

# Concurrent: total ≈ max(time(a), time(b))
user, posts = await asyncio.gather(fetch_user(), fetch_posts())
```

Untuk halaman yang butuh tiga sumber independen, gather bisa mengubah 3× tunggu jadi 1× tunggu.

### 4. Jebakan blocking

Di dalam `async def`, memanggil fungsi **blocking** (driver DB sinkron, `time.sleep`, CPU berat) membekukan seluruh event loop — tiap request lain ikut menunggu. Aturan:

- Pakai **pustaka async** untuk I/O di dalam handler async (driver DB async, `httpx.AsyncClient`).
- Untuk kerja blocking/CPU yang tak terhindarkan, offload (`run_in_executor`, worker/queue).
- Kalau handler tak punya `await` dan hanya kerja sinkron cepat, handler `def` biasa cukup — FastAPI menjalankannya di threadpool.

### Pilih sync vs async

| Situasi | Pakai |
|---|---|
| Handler menunggu I/O DB/HTTP/LLM | `async def` + pustaka async |
| Beberapa panggilan I/O independen | `async def` + `asyncio.gather` |
| Kerja sinkron cepat, tanpa menunggu | `def` biasa cukup |
| Kerja CPU berat | offload ke worker/executor, jangan blokir loop |

- ✅ Pakai async untuk handler terikat-I/O dan gather panggilan independen.
- ✅ Jaga semua di dalam handler async tetap non-blocking.
- 🚫 Jangan pakai async untuk kerja CPU; jangan panggil pustaka blocking di handler async.

## ⚠️ Kesalahan umum

- Menambah `async` di mana-mana berharap kecepatan, bahkan untuk kerja CPU — tanpa manfaat, mungkin merugikan.
- Memanggil pustaka **blocking** (driver DB sinkron, `time.sleep`, `requests`) di dalam `async def`, membekukan loop.
- Menunggu panggilan independen berurutan padahal `gather` bisa menjalankannya sekaligus.
- Melakukan komputasi berat di handler async dan membuat request lain kelaparan.
- Mencampur session DB sinkron dan async tanpa hati-hati.

:::revoshop
Lihat I/O RevoShop. (1) Panggilan Midtrans dan query DB terikat-I/O — di FastAPI mereka kandidat `async` bagus; identifikasi. (2) Adakah langkah berat-CPU (mis. membuat laporan/PDF) yang TAK boleh async tapi di-offload ke worker? (3) Halaman checkout mungkin memuat keranjang, user, dan opsi pengiriman — bisakah `gather` mengambil ini bersamaan alih-alih satu-satu?
:::

## 🏆 Praktik terbaik

- [ ] Pakai `async def` hanya saat handler menunggu I/O; `def` biasa untuk kerja sinkron cepat.
- [ ] Jangan pernah panggil pustaka blocking di dalam handler async — pakai klien/driver async.
- [ ] Jalankan panggilan I/O independen dengan `asyncio.gather` untuk memangkas total tunggu.
- [ ] Offload kerja berat-CPU ke worker/executor, menjaga event loop bebas.
- [ ] Ukur sebelum mengasumsikan async membuat lebih cepat.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan async dengan analogi satu-pelayan-banyak-meja, dan nyatakan jelas kenapa ia membantu kerja terikat-I/O tapi bukan terikat-CPU. Lalu jelaskan apa yang diubah `asyncio.gather` untuk dua panggilan independen.

## 📐 Rancang

Endpoint dashboard CareerPilot butuh: profil user (DB), lamaran mereka (DB), dan daftar "pekerjaan yang mungkin kamu suka" dari API partner eksternal. Masing-masing ~150 ms. Rancang handler-nya: sync atau async, berurutan atau di-gather, dan perkirakan latensi tiap pendekatan. Catat langkah mana yang tak boleh memblokir loop.

:::quiz
Tampilkan satu rancangan yang mungkin

**Async + gather.** Ketiganya terikat-I/O (dua baca DB, satu API eksternal), jadi pakai `async def` dengan klien DB/HTTP async. Ketiga panggilan independen, jadi jalankan dengan `asyncio.gather`:

```python
@app.get("/dashboard")
async def dashboard(user_id: int):
    profile, apps, jobs = await asyncio.gather(
        fetch_profile(user_id),
        fetch_applications(user_id),
        fetch_recommended_jobs(user_id),
    )
    return {"profile": profile, "applications": apps, "jobs": jobs}
```

**Latensi:** await berurutan ≈ 150 + 150 + 150 = **~450 ms**; di-gather ≈ **~150 ms** (panggilan tunggal terpanjang). Async juga membuat server menangani request user *lain* selama menunggu itu.

**Tak boleh blokir:** pakai klien async (driver DB async, `httpx.AsyncClient`) — driver sinkron di sini akan membekukan loop dan membatalkan manfaatnya. Pemrosesan pasca berat-CPU harus dijaga keluar dari handler.

**Aturan yang ditunjukkan:** async + gather mengubah tunggu I/O independen dari aditif menjadi paralel, sambil menjaga server responsif terhadap request lain.
:::

### 📝 Checklist review mandiri

- [ ] Async dipakai karena kerjanya terikat-I/O
- [ ] Panggilan independen dijalankan dengan `gather`
- [ ] Hanya klien async (non-blocking) dipakai di dalam handler
- [ ] Kerja berat-CPU dijaga keluar dari event loop

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m3/w2/01-async-gather" ai="no-ai" title="I/O berurutan vs bersamaan"}
Implementasikan dua fungsi async yang memanggil `fetch` async palsu untuk beberapa id: satu yang menunggunya satu-demi-satu, dan satu yang menjalankan semuanya sekaligus dengan `asyncio.gather`. Penghitung bersama membuktikan versi bersamaan punya semua panggilan berjalan serentak sementara yang berurutan tak pernah melebihi satu. Tes menjalankannya dengan `asyncio.run` — tanpa timing, sepenuhnya deterministik.
:::

:::hints
- `fetch` palsu menaikkan penghitung `in_flight` bersama saat masuk, mencatat max terlihat, `await asyncio.sleep(0)` untuk yield, lalu menurunkan dan mengembalikan id.
- `fetch_all_sequential`: `for id in ids: results.append(await fetch(id))` → max in-flight tetap 1.
- `fetch_all_concurrent`: `await asyncio.gather(*(fetch(i) for i in ids))` → max in-flight sama dengan len(ids).
- Keduanya harus mengembalikan hasil untuk tiap id (bersamaan mengembalikannya dalam urutan input lewat gather).
:::

## ✅ Cek cepat

:::quiz
Kenapa `async` mempercepat endpoint terikat-I/O tapi bukan terikat-CPU?

Untuk kerja I/O, handler menghabiskan sebagian besar waktu *menunggu* (DB, API, atau berkas), dan `await` membuat server memakai waktu idle itu melayani request lain. Kerja CPU tak punya tunggu idle — kode sibuk menghitung — jadi async tak bisa memakai ulang apa pun dan bahkan bisa memblokir event loop.
:::

:::quiz
Handler async-mu butuh data dari dua layanan independen. Apa yang kamu pakai, dan apa yang berubah?

`asyncio.gather` — ia menjalankan kedua awaitable pada saat yang sama, jadi total latensi kira-kira yang *lebih lama* dari keduanya alih-alih jumlahnya. Menunggunya satu demi satu akan menambahkan tunggunya.
:::

## 📚 Lanjut belajar

- [FastAPI: async and await](https://fastapi.tiangolo.com/async/)
- [Python docs: asyncio — gather](https://docs.python.org/3/library/asyncio-task.html#asyncio.gather)
- [Real Python: async IO in Python](https://realpython.com/async-io-python/)

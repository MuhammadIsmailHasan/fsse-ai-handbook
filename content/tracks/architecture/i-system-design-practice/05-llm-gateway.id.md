---
title: "LLM Gateway"
summary: Satu layanan di depan tiap panggilan model AI — memusatkan API key, routing model, caching, pelacakan biaya, rate limit, dan fallback penyedia, supaya aplikasimu tetap sederhana dan kamu mengendalikan biaya, keandalan, dan keamanan di satu tempat.
sourceHash: ef83d66b6ea8
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa itu **LLM gateway** dan kenapa tim menaruhnya di depan panggilan AI
- Memusatkan **API key**, **routing model**, dan **pelacakan biaya**
- Memakai ulang perkakas ketahananmu: **caching**, **rate limit**, **retry**, **fallback**
- **Fallback penyedia**: beralih model saat satu gagal atau mati
- **Guardrail** dan **observability** di satu tempat
- Bagaimana ini menyatukan seluruh track untuk fitur AI CareerPilot

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **LLM gateway** | Satu layanan yang dilewati semua panggilan AI |
| **Provider** | Perusahaan/model yang kamu panggil (OpenAI, Anthropic, …) |
| **Routing** | Memilih model mana yang menangani request |
| **Fallback** | Beralih ke penyedia lain saat gagal |
| **Pelacakan biaya** | Mencatat biaya per request/user |
| **Guardrail** | Pemeriksaan keamanan pada input/output |
| **Observability** | Log/metrik untuk melihat apa yang terjadi |

## 🧠 Ide besarnya

LLM gateway seperti **meja resepsionis hotel**. Tamu (fitur aplikasimu) tak berkeliaran sendiri ke dapur, binatu, atau akunting — mereka bicara ke **satu meja**, yang merutekan tiap permintaan ke departemen yang tepat, memegang kunci induk, mencatat semuanya, menegakkan aturan, dan bisa mengarahkanmu ke layanan cadangan kalau satu sibuk. Satu meja, satu tempat mengelola segalanya.

## ❓ Kenapa ini penting

Begitu lebih dari satu fitur memanggil LLM, menaburkan API key, retry, caching, dan logika biaya ke seluruh basis kode menjadi kekacauan — dan risiko (key bocor, tagihan liar, tanpa visibilitas). Gateway menaruh semuanya di **satu tempat**: fiturmu cukup memanggil gateway dengan prompt. Di sinilah *segalanya* dari track ini bersatu — caching, rate limiting, retry, circuit breaker, kontrol biaya — diterapkan pada dunia penyedia AI yang mahal, labil, dan cepat berubah.

## 📖 Langkah demi langkah

### 1. Apa yang dipusatkan gateway

Aplikasimu memanggil `gateway.complete(prompt, ...)`; gateway menangani:

- **Key**: API key penyedia tinggal hanya di gateway, tak pernah tersebar di kode fitur.
- **Routing**: pilih model per tugas (model murah untuk klasifikasi, yang kuat untuk menulis).
- **Caching**: kembalikan jawaban tersimpan untuk prompt berulang (Stage F).
- **Rate limiting**: batasi panggilan per-user/per-app untuk melindungi anggaran (Stage F).
- **Retry + circuit breaker**: tangani kedip dan gangguan penyedia (Stage H).
- **Fallback**: kalau penyedia A gagal, coba penyedia B.
- **Pelacakan biaya**: catat token dan biaya per request/user.
- **Guardrail**: cek input (blokir penyalahgunaan) dan output (saring konten tak aman).
- **Observability**: log prompt, latensi, biaya, dan error.

### 2. Routing: model yang tepat untuk tugasnya

Tak tiap tugas butuh model terbesar. Rutekan per tugas atau konfigurasi:

```
task "classify"  → small, cheap, fast model
task "write_cv"  → larger, higher-quality model
```

Ini saja bisa memangkas biaya drastis tanpa merusak kualitas di tempat yang penting.

### 3. Caching dan biaya — tuas uang

Panggilan LLM berbiaya uang nyata per token. Dua kebiasaan dari Stage F sangat berbuah:
- **Cache** prompt identik → lewati panggilan berbayar sepenuhnya.
- **Lacak biaya** per request dan per user supaya kamu bisa melihat biaya, menetapkan anggaran, dan rate-limit user berat.

```
cost = (tokens / 1000) * price_per_1k_tokens   # record this every call
```

### 4. Fallback penyedia (dan circuit breaker)

Penyedia AI mengalami gangguan. Gateway bisa **fallback**: coba penyedia A; kalau error (atau circuit breaker-nya terbuka), coba penyedia B; kalau semua gagal, kembalikan pesan yang anggun. Dikombinasikan dengan retry + backoff (Stage H), ini menjaga fitur AI tetap bekerja lewat cegukan penyedia.

```
try provider A → fail → try provider B → success ✅
all providers fail → friendly fallback ("AI is busy, try again")
```

### 5. Guardrail dan observability

Karena tiap panggilan mengalir lewat satu tempat, gateway adalah rumah alami untuk **guardrail** (tolak prompt-injection atau konten terlarang; saring output tak aman) dan **observability** (satu dashboard latensi, biaya, tingkat error, dan cache hit-rate). Tanpa gateway, kamu akan menempelkan ini ke tiap fitur terpisah.

### Apa yang dirutekan lewat gateway

| Kepedulian | Ditangani di gateway? |
|---|---|
| API key / secret | ✅ hanya di sini |
| Pilihan model per tugas | ✅ routing |
| Biaya prompt berulang | ✅ cache |
| Batas biaya per-user | ✅ rate limit + pelacakan biaya |
| Gangguan penyedia | ✅ retry + circuit breaker + fallback |
| Pemeriksaan keamanan | ✅ guardrail |

- ✅ Kirim tiap panggilan AI lewat gateway; simpan key dan kebijakan di satu tempat.
- ✅ Rutekan tugas murah ke model murah; cache yang berulang; lacak biaya per user.
- ✅ Tambah fallback + circuit breaker supaya gangguan satu penyedia bukan gangguanmu.
- 🚫 Jangan taburkan key, retry, dan logika biaya ke seluruh fitur.

## ⚠️ Kesalahan umum

- API key disalin ke banyak layanan — mimpi buruk kebocoran atau rotasi.
- Tanpa caching, prompt identik dibayar lagi dan lagi.
- Tanpa rate limit atau pelacakan biaya per-user, satu user (atau loop) menguras anggaran.
- Satu penyedia tanpa fallback, jadi gangguannya menjatuhkan fitur AI-mu.
- Guardrail/logging ditambahkan per fitur alih-alih sekali di gateway.

:::revoshop
RevoShop kebanyakan non-AI, tapi kalau menambah AI (mis. ringkasan review, bot dukungan), gateway akan membantu. (1) Tugas AI mana yang murah (klasifikasi sentimen review) vs mahal (menulis ringkasan), dan bagaimana routing menghemat uang? (2) Bagaimana caching dan rate limit per-user melindungi anggaran AI? (3) Di mana fallback + circuit breaker menjaga fitur tetap bisa dipakai selama gangguan penyedia?
:::

## 🏆 Praktik terbaik

- [ ] Rutekan semua panggilan AI lewat satu gateway; simpan key penyedia hanya di sana.
- [ ] Rutekan tiap tugas ke model termurah yang memenuhi standar kualitasnya.
- [ ] Cache prompt berulang dan lacak biaya token per request dan per user.
- [ ] Terapkan rate limit dan anggaran per-user di gateway.
- [ ] Tambah retry, circuit breaker, dan fallback penyedia untuk ketahanan.
- [ ] Pusatkan guardrail dan observability (biaya, latensi, error, cache hit-rate).

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan LLM gateway dengan analogi meja-resepsionis-hotel. Lalu sebutkan tiga hal yang dipusatkannya dan, untuk masing-masing, satu masalah yang akan kamu hadapi tanpanya.

## 📐 Rancang

Rancang LLM gateway untuk CareerPilot, yang punya tiga fitur AI: (a) klasifikasi senioritas lowongan (murah, volume tinggi), (b) menyesuaikan CV (mahal, volume sedang), (c) asisten chat (streaming). Cakup routing, caching, kontrol biaya per-user, dan apa yang terjadi saat penyedia utama mengalami gangguan.

:::quiz
Tampilkan satu rancangan yang mungkin

**Routing:** (a) klasifikasi senioritas → **model kecil murah** (volume tinggi, tugas sederhana); (b) penyesuaian CV → **model lebih besar, kualitas tinggi**; (c) chat → model sedang/besar dengan **streaming**. Gateway memetakan tugas → model, jadi fitur tak pernah hardcode penyedia.

**Caching:** prompt klasifikasi sering berulang (lowongan sama) → cache agresif (hemat besar). Penyesuaian CV spesifik-user → cache sedikit atau berkunci pada hash (profil+lowongan). Chat dinamis → umumnya tak di-cache.

**Kontrol biaya per-user:** gateway melacak token × harga per request dan per user, menegakkan rate limit per-user dan anggaran bulanan, dan mengembalikan `429`/ajakan upgrade saat terlampaui — melindungi biaya keseluruhan.

**Gangguan penyedia:** retry dengan backoff untuk kedip; **circuit breaker** per penyedia; **fallback** ke penyedia/model sekunder saat utama mati; kalau semua gagal, pesan anggun "AI sibuk, draf tersimpan". Semua ini tinggal di gateway, jadi tiap fitur diuntungkan sekaligus.

**Aturan yang ditunjukkan:** satu gateway memusatkan routing, caching, kontrol biaya, dan ketahanan — menerapkan perkakas seluruh track ke panggilan AI di satu tempat.
:::

### 📝 Checklist review mandiri

- [ ] Tugas dirutekan ke model berukuran tepat
- [ ] Strategi caching dicocokkan dengan seberapa berulang tiap tugas
- [ ] Pelacakan biaya per-user, rate limit, dan anggaran di gateway
- [ ] Retry + circuit breaker + fallback penyedia untuk gangguan

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/architecture/i-system-design-practice/05-llm-gateway" ai="no-ai" title="LLM gateway mini: cache, fallback, dan biaya"}
Implementasikan LLM gateway kecil: perkirakan biaya dari token, cache prompt identik, dan fallback melewati daftar penyedia sampai satu sukses — melacak total biaya. Tes membuktikan prompt yang di-cache melewati penyedia (dan biayanya), dan penyedia utama yang gagal fallback ke berikutnya.
:::

:::hints
- `estimate_cost(tokens, price_per_1k)` = `tokens / 1000 * price_per_1k`.
- Provider adalah pasangan `(name, fn)` yang dicoba berurutan; `fn(prompt)` mengembalikan `{"text", "tokens"}` atau raise untuk simulasi kegagalan.
- `complete(prompt)`: pada cache hit kembalikan `{"text", "provider", "cached": True, "cost": 0.0}` dan jangan panggil penyedia; pada miss, coba penyedia berurutan, tambahkan `estimate_cost` ke `total_cost`, cache dan kembalikan `{"text", "provider", "cached": False, "cost"}`. Raise kalau tiap penyedia gagal.
:::

## ✅ Cek cepat

:::quiz
Kenapa menaruh satu gateway di depan semua panggilan LLM-mu alih-alih memanggil penyedia langsung dari tiap fitur?

Karena ia memusatkan key, routing model, caching, rate limit, pelacakan biaya, retry/fallback, guardrail, dan observability di satu tempat. Memanggil penyedia langsung menyebarkan secret dan kebijakan ke seluruh fitur, membuat kontrol biaya, keandalan, dan keamanan tidak konsisten dan sulit dikelola.
:::

:::quiz
Sebutkan dua hal yang dilakukan gateway untuk mengendalikan biaya AI.

Caching prompt identik (jadi request berulang melewati panggilan berbayar) dan routing tiap tugas ke model termurah yang memenuhi standar kualitasnya; ia juga melacak biaya token per user dan menegakkan rate limit/anggaran untuk menghentikan biaya liar.
:::

## 📚 Lanjut belajar

- [Cloudflare AI Gateway](https://developers.cloudflare.com/ai-gateway/)
- [Anthropic: Claude API overview](https://docs.claude.com/en/api/overview)
- [LiteLLM: an open-source LLM gateway/proxy](https://docs.litellm.ai/)

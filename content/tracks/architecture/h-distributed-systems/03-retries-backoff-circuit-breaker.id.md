---
title: "Retries, Backoff & Circuit Breaker"
summary: Cara menangani dependency yang labil tanpa memperburuk keadaan — ulang hanya operasi yang aman, tunggu makin lama tiap kali dengan jitter, dan trip circuit breaker untuk berhenti menghantam layanan yang jelas mati.
sourceHash: 48255c582e11
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Kapan **retry** membantu dan kapan malah merugikan
- **Exponential backoff**: menunggu makin lama setelah tiap percobaan gagal
- **Jitter**: menambah keacakan supaya klien tak retry serentak
- Masalah **thundering herd** / badai retry
- **Circuit breaker**: berhenti memanggil layanan yang jelas mati
- Bagaimana ini melindungi dependency nyata (payment gateway, API AI)

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Transient error** | Kegagalan singkat yang kemungkinan lewat |
| **Retry** | Coba panggilan yang sama lagi |
| **Backoff** | Menunggu lebih lama sebelum tiap retry |
| **Exponential backoff** | Gandakan waktu tunggu tiap percobaan |
| **Jitter** | Goyangan acak yang ditambahkan ke waktu tunggu |
| **Thundering herd** | Banyak klien retry pada saat yang sama |
| **Circuit breaker** | Sakelar yang menghentikan panggilan ke layanan gagal |

## 🧠 Ide besarnya

- **Retry dengan backoff** seperti **mengetuk pintu**: kalau tak ada jawaban, kamu tak menggedor terus — kamu menunggu sebentar, lalu lebih lama, memberi mereka waktu untuk datang.
- **Jitter** seperti **tak semua orang mengetuk pada ketukan yang sama**: kalau seluruh kerumunan mengetuk serempak, pintu tak pernah dapat momen tenang; menyebar ketukan membantu.
- **Circuit breaker** seperti **sekring rumah**: saat ada yang sangat salah, sekring trip dan memutus listrik supaya rumah tak terbakar. Setelah beberapa saat kamu menyalakannya lagi untuk menguji apakah sudah aman.

## ❓ Kenapa ini penting

Jaringan dan layanan gagal singkat sepanjang waktu — kedip, timeout, kelebihan beban sesaat. Aplikasi naif entah menyerah terlalu mudah (gagal pada kedip yang satu retry akan perbaiki) atau retry terlalu agresif (menghantam layanan yang sedang kesulitan sampai runtuh total, dan menyeret aplikasimu turun juga).

Retry, backoff, jitter, dan circuit breaker adalah perkakas standar untuk jadi **tangguh tanpa jadi perundung**: pulih dari kedip, tapi mundur dan berhenti saat dependency benar-benar mati.

## 📖 Langkah demi langkah

### 1. Retry — tapi hanya yang aman

Retry masuk akal untuk error **transient** (timeout, `503 Service Unavailable`, koneksi terputus). Ia berbahaya untuk operasi yang tak **idempotent**: mengulang "tagih kartu" bisa menagih dua kali. Jadi:

- Retry **baca** dan tulis idempotent dengan bebas.
- Retry tulis non-idempotent (pembayaran) **hanya** dengan idempotency key (pelajaran sebelumnya).
- Jangan retry `400 Bad Request` — ia akan gagal dengan cara sama tiap kali.

### 2. Exponential backoff

Jangan retry seketika dalam loop ketat — itu hanya menumpuk beban. Tunggu **lebih lama setelah tiap percobaan**, menggandakan jeda:

```python
def backoff_delay(attempt, base=0.5, cap=30):
    return min(cap, base * (2 ** attempt))
# attempt 0 → 0.5s, 1 → 1s, 2 → 2s, 3 → 4s ... capped at 30s
```

Ini memberi layanan yang kesulitan ruang bernapas alih-alih gempuran konstan, dan **cap** menghentikan waktu tunggu tumbuh selamanya.

### 3. Jitter — putuskan sinkron

Kalau 1.000 klien semuanya gagal pada saat yang sama dan semuanya backoff dengan jumlah persis sama, mereka retry dalam gelombang sempurna — **thundering herd** yang terus menumbangkan layanan. Tambah **jitter** (keacakan) supaya retry menyebar:

```python
import random
def backoff_with_jitter(attempt, base=0.5, cap=30):
    delay = min(cap, base * (2 ** attempt))
    return random.uniform(0, delay)   # spread retries across the window
```

Kini kerumunan mengetuk pada waktu sedikit berbeda, dan layanan mendapat momen tenang untuk pulih.

### 4. Circuit breaker

Kalau sebuah layanan sudah gagal beberapa waktu, retry sama sekali percuma dan berbahaya. **Circuit breaker** mengawasi kegagalan dan, melewati ambang, **trip terbuka** — panggilan baru gagal cepat (atau memakai fallback) tanpa bahkan mencoba layanan mati. Ia punya tiga state:

```
CLOSED  → calls flow normally; count failures
   │  too many failures
   ▼
OPEN    → calls are blocked immediately (fail fast) for a cooldown period
   │  cooldown elapsed
   ▼
HALF-OPEN → allow ONE trial call
   ├─ success → back to CLOSED (recovered)
   └─ failure → back to OPEN (still down)
```

Ini melindungi kedua sisi: aplikasimu berhenti membuang waktu pada panggilan yang pasti gagal, dan layanan yang kesulitan mendapat istirahat dari lalu lintas sehingga bisa pulih.

### 5. Menyatukannya

Panggilan tangguh ke dependency:

1. Coba panggilannya.
2. Pada error transient, **retry dengan exponential backoff + jitter**, beberapa kali.
3. Umpankan sukses/gagal ke **circuit breaker**; kalau terbuka, gagal cepat atau pakai fallback alih-alih retry.

### Kapan memakai apa

| Situasi | Alat |
|---|---|
| Satu timeout / `503` pada sebuah baca | Retry dengan backoff + jitter |
| Pembayaran atau tulis non-idempotent | Retry hanya dengan idempotency key |
| Dependency gagal berulang beberapa waktu | Circuit breaker (gagal cepat) |
| Error `400`/validasi | Jangan retry — perbaiki request-nya |

- ✅ Retry kegagalan transient dengan exponential backoff bertutup dan jitter.
- ✅ Bungkus dependency labil dalam circuit breaker dengan fallback.
- 🚫 Jangan retry tulis non-idempotent tanpa idempotency key.
- 🚫 Jangan retry seketika atau serempak — itu menyebabkan badai retry.

## ⚠️ Kesalahan umum

- Retry seketika tak terbatas tanpa backoff → badai retry yang memperburuk gangguan.
- Backoff tanpa jitter → thundering herd tersinkron.
- Retry operasi non-idempotent → tagihan ganda.
- Tak ada cap pada backoff → waktu tunggu tumbuh jadi menit; atau tak ada circuit breaker → menghantam layanan mati.
- Retry error yang tak akan pernah sukses (`400`, `404`, kegagalan auth).

:::revoshop
RevoShop memanggil Midtrans (pembayaran) dan nanti mungkin memanggil layanan AI. (1) Panggilan mana yang aman di-retry apa adanya, dan mana yang butuh idempotency key dulu (membuat charge)? (2) Tambah exponential backoff dengan jitter ke panggilan eksternal yang labil — base dan cap berapa yang masuk akal? (3) Kalau Midtrans mati beberapa menit, bagaimana circuit breaker membantu RevoShop gagal cepat dan menampilkan pesan jelas "pembayaran sementara tak tersedia" alih-alih hang lama?
:::

## 🏆 Praktik terbaik

- [ ] Retry hanya operasi transient dan aman (idempotent atau berkunci); jangan pernah retry pembayaran secara buta.
- [ ] Pakai exponential backoff bertutup **dengan jitter** untuk menghindari retry tersinkron.
- [ ] Batasi jumlah retry; menyerah dan tampilkan error jelas pada akhirnya.
- [ ] Bungkus dependency tak andal dalam circuit breaker dengan fallback masuk akal.
- [ ] Log dan alert saat breaker trip — itu menandakan gangguan nyata.
- [ ] Bedakan error yang bisa di-retry (5xx/timeout) dari yang tak bisa (4xx).

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan retry-dengan-backoff dengan analogi mengetuk-pintu, jitter dengan ide tak-mengetuk-serempak, dan circuit breaker dengan analogi sekring-rumah. Lalu katakan dalam satu kalimat kenapa panggilan pembayaran tak boleh di-retry tanpa idempotency key.

## 📐 Rancang

CareerPilot bergantung pada API LLM berbayar yang kadang timeout dan, jarang, mati beberapa menit. Rancang strategi pemanggilan tangguh: error mana yang kamu retry dan bagaimana (backoff/jitter/batas), bagaimana circuit breaker melindungi aplikasi dan LLM selama gangguan lebih panjang, dan apa yang user lihat di tiap kasus.

:::quiz
Tampilkan satu rancangan yang mungkin

**Retry:** pada timeout atau `503`, retry sampai 3 kali dengan exponential backoff + jitter (mis. base 0.5s, cap 8s, `random.uniform(0, delay)`). Panggilan "generate" LLM efektif idempotent untuk retry kalau kamu berkunci pada request-nya (atau menerima completion yang mungkin berbeda); `400` (prompt buruk) **tidak** di-retry.

**Circuit breaker:** bungkus klien LLM. Setelah, katakanlah, 5 kegagalan berturut-turut, breaker **terbuka** selama cooldown 30s — panggilan gagal cepat alih-alih menumpuk 3 retry × banyak user ke layanan mati. Setelah cooldown ia jadi **half-open**, membiarkan satu panggilan percobaan lewat; sukses → tertutup, gagal → terbuka lagi.

**Yang user lihat:** kedip transient tak terlihat (retry memperbaikinya). Selama breaker terbuka, aplikasi gagal cepat dengan fallback ramah — "saran AI sementara tak tersedia, draf-mu kami simpan" — alih-alih spinner lama, dan pulih otomatis begitu panggilan percobaan sukses.

**Aturan yang ditunjukkan:** retry error transient dengan backoff + jitter dan batas, dan pakai circuit breaker untuk gagal cepat (dengan fallback) selama gangguan nyata supaya kamu tak menghantam dependency.
:::

### 📝 Checklist review mandiri

- [ ] Error yang bisa dan tak bisa di-retry dibedakan
- [ ] Backoff bertutup dan punya jitter; retry dibatasi
- [ ] Tulis non-idempotent berkunci sebelum retry apa pun
- [ ] Circuit breaker dengan fallback menangani gangguan lebih panjang

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/architecture/h-distributed-systems/03-backoff-breaker" ai="no-ai" title="Exponential backoff dan circuit breaker"}
Implementasikan exponential backoff bertutup dan circuit breaker tiga-state (closed → open → half-open). Tes memeriksa penggandaan-dan-tutup jeda dan menggiring breaker melewati rentetan kegagalan, cooldown, percobaan half-open, dan pemulihan.
:::

:::hints
- `backoff_delay(attempt, base, cap)` = `min(cap, base * (2 ** attempt))`, dengan `attempt` mulai 0.
- State breaker: lacak `state`, `failures`, dan `opened_at`. `allow(now)` kembalikan True di CLOSED; di OPEN kembalikan False sampai `now - opened_at >= cooldown`, lalu balik ke HALF-OPEN dan kembalikan True.
- `on_success` → CLOSED, reset failures. `on_failure(now)` → hitung failures; pada ambang (atau kegagalan apa pun saat HALF-OPEN) jadi OPEN dan set `opened_at = now`.
:::

## ✅ Cek cepat

:::quiz
Kenapa menambah jitter ke exponential backoff alih-alih memakai penggandaan jeda tetap?

Tanpa jitter, banyak klien yang gagal pada saat sama retry pada waktu yang persis sama, menciptakan gelombang tersinkron (thundering herd) yang terus membanjiri layanan. Jitter mengacak waktu tunggu tiap klien sehingga retry menyebar dan layanan mendapat momen tenang untuk pulih.
:::

:::quiz
Apa yang dilakukan circuit breaker terbuka, dan bagaimana ia membantu kedua sisi?

Ia memblokir panggilan seketika (gagal cepat, atau pakai fallback) alih-alih mencoba layanan yang jelas mati. Ini menyelamatkan aplikasimu dari membuang waktu pada panggilan yang pasti gagal dan memberi dependency yang kesulitan istirahat dari lalu lintas sehingga bisa pulih, setelah itu percobaan half-open mengecek apakah ia sehat lagi.
:::

## 📚 Lanjut belajar

- [AWS: timeouts, retries, and backoff with jitter](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/)
- [Martin Fowler: CircuitBreaker](https://martinfowler.com/bliki/CircuitBreaker.html)
- [Google SRE book: addressing cascading failures](https://sre.google/sre-book/addressing-cascading-failures/)

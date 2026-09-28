---
title: "Rate Limiter & Notification System"
summary: Dua pertanyaan desain klasik dikerjakan tuntas — rate limiter terdistribusi (fixed vs sliding window, di mana penghitungnya tinggal) dan notification system yang menyebar satu event ke email, push, dan SMS dengan preferensi dan tanpa duplikat.
sourceHash: 2b8cc546da8b
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Merancang **rate limiter terdistribusi** dengan kerangka
- **Fixed window** vs **sliding window**, dan bug tepi dari fixed window
- Di mana penghitung tinggal supaya bekerja lintas banyak server
- Merancang **notification system** yang **menyebar** satu event ke banyak saluran
- Menghormati **preferensi user** dan menghindari notifikasi **duplikat**
- Kenapa notifikasi cocok di queue dengan retry

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Rate limiter** | Membatasi berapa request diizinkan dalam jendela waktu |
| **Fixed window** | Hitungan reset pada jam bulat (mis. tiap menit) |
| **Sliding window** | Hitungan atas N detik terakhir dari *sekarang* |
| **Fan-out** | Satu event berubah jadi banyak pesan |
| **Channel** | Rute kirim: email, push, SMS |
| **Preferensi** | Saluran mana yang diinginkan user |
| **Deduplikasi** | Jangan kirim hal yang sama dua kali |

## 🧠 Ide besarnya

- **Rate limiter** seperti **penghitung wahana taman hiburan**: hanya sekian penunggang per jam. Bagian rumitnya adalah cara kamu menghitung waktu — reset pada jam bulat (fixed) atau selalu melihat 60 menit terakhir (sliding)?
- **Notification system** seperti **meja pengumuman orang tua di sekolah**: satu pengumuman keluar, tapi tiap orang tua memilih cara mereka menerimanya — SMS, email, atau aplikasi — dan tak ada yang boleh menerima pemberitahuan sama dua kali.

## ❓ Kenapa ini penting

Keduanya muncul terus, di wawancara dan di produk nyata. Mereka juga mengajarkan kebiasaan kunci: desain bukan sekadar "kotak", tapi **aturan penghitungan** (rate limiter) atau **aturan routing + dedupe** (notifikasi) yang menentukan kebenaran. Membuat aturan itu benar yang memisahkan desain yang bekerja dari yang mengirim ganda atau membiarkan lonjakan lolos.

## 📖 Langkah demi langkah

### Bagian A — Rate limiter terdistribusi

**1. Requirement**: batasi tiap user (atau IP) ke, katakanlah, 100 request/menit; kembalikan `429` saat terlampaui; bekerja lintas banyak instance server; cepat (dicek pada tiap request).

**2. Skala**: ia jalan pada *tiap* request, jadi pengecekan harus O(1)-an dan memakai penyimpanan bersama.

**3. Fixed window**: hitung request per menit jam.
```
key = "rl:user42:2026-09-29T10:15"   # per-minute bucket
INCR key ; if count > 100 → reject ; set expiry 60s
```
Sederhana, tapi punya **bug tepi**: 100 request pada 10:15:59 dan 100 lagi pada 10:16:00 = 200 request dalam satu detik nyata, karena jendela reset pada batas jam.

**4. Sliding window**: hitung atas 60 detik terakhir dari *sekarang*, bukan menit jam. Ini menghaluskan tepi — tak ada lonjakan di batas. Ia berbiaya sedikit lebih (lacak timestamp atau bobot dua jendela berdampingan).

**5. Di mana penghitung tinggal**: di **Redis**, dibagi semua server (memori satu server akan memberi tiap instance batasnya sendiri yang terpisah). Ini pelajaran yang sama dari Stage F, kini ditempatkan dalam desain penuh.

### Bagian B — Notification system

**1. Requirement**: saat event terjadi (mis. "order-mu dikirim"), beri tahu user di saluran pilihannya (email/push/SMS); hormati **preferensi**; jangan pernah kirim **duplikat**; andal (retry kegagalan); tangani lonjakan.

**2. Aliran tingkat tinggi**:
```
event  ──▶  Notification Service  ──▶  QUEUE  ──▶  channel workers
(order shipped)   │ fan-out per user prefs         email / push / SMS
                  └ dedupe by (user, event, channel)
```

**3. Fan-out**: satu event menjadi beberapa pesan — satu per saluran yang user aktifkan. User yang ingin email + push mendapat dua pesan; user yang membisukan tipe ini tak mendapat apa pun.

**4. Preferensi**: cek pengaturan tiap user sebelum membuat pesan. Jangan pernah spam saluran yang user matikan (dan hormati "jangan ganggu"/unsubscribe — sering wajib secara hukum).

**5. Dedupe**: event yang sama bisa diproses dua kali (queue at-least-once). Kunci tiap pengiriman dengan `(user_id, event_id, channel)` dan lewati kalau sudah terkirim — supaya retry tak mengirim dua SMS.

**6. Keandalan**: taruh pengiriman di **queue** dengan retry, backoff, dan dead-letter queue (Stage H). Penyedia email/SMS kadang gagal; queue menyerap lonjakan dan retry dengan aman.

### Pilih aturan penghitungan / pengiriman

| Keputusan | Pilih |
|---|---|
| Batas sederhana, lonjakan tepi kecil OK | Fixed window (paling mudah) |
| Pembatasan halus, tak ada lonjakan batas | Sliding window |
| Penghitung untuk banyak server | Selalu Redis (bersama) |
| Pengiriman multi-saluran yang andal | Queue + retry + dedupe |

- ✅ Simpan penghitung limiter di penyimpanan bersama; kedaluwarsakan key otomatis.
- ✅ Fan out per preferensi user; dedupe tiap pengiriman dengan kunci stabil.
- ✅ Kirim lewat queue dengan retry dan dead-letter queue.
- 🚫 Jangan rate-limit di memori per-server; jangan kirim tanpa mengecek preferensi.

## ⚠️ Kesalahan umum

- Fixed-window limiter membiarkan ~2× batas melewati batas; pakai sliding window saat itu penting.
- State rate-limit di memori satu server, sehingga batas berbeda per instance.
- Mengirim notifikasi sinkron dalam request, sehingga penyedia SMS lambat menahan aplikasi.
- Tak ada dedupe, sehingga pemrosesan at-least-once mengirim email ganda.
- Mengabaikan preferensi/unsubscribe — mengganggu user dan bisa melanggar hukum.

:::revoshop
Rancang dua fitur RevoShop. (1) **Rate limit login**: batasi login gagal per akun/IP — fixed atau sliding window, dan di mana penghitungnya tinggal? Apa yang kamu kembalikan pada percobaan gagal ke-6? (2) **Notifikasi order**: "order dikirim" harus menjangkau pembeli lewat saluran pilihannya; sketsa fan-out, cara kamu menghormati preferensi, dan cara kamu dedupe supaya webhook yang di-retry tak mengirim email dua kali.
:::

## 🏆 Praktik terbaik

- [ ] Pilih fixed vs sliding window berdasarkan apakah lonjakan batas penting; dokumentasikan.
- [ ] Simpan penghitung limiter di Redis dengan kedaluwarsa otomatis; kembalikan `429` + `Retry-After`.
- [ ] Fan out notifikasi per preferensi user; jangan pernah kirim ke saluran yang dimatikan.
- [ ] Dedupe tiap pengiriman dengan `(user, event, channel)`.
- [ ] Kirim lewat queue dengan retry, backoff, dan dead-letter queue.
- [ ] Hormati unsubscribe/jangan-ganggu sebagai aturan keras.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan fixed vs sliding window dengan analogi penghitung-wahana, termasuk bug lonjakan-batas. Lalu jelaskan fan-out notifikasi dengan analogi meja-pengumuman-orang-tua, termasuk kenapa dedupe penting.

## 📐 Rancang

Rancang notification system untuk CareerPilot: saat status lamaran berubah jadi "interview dijadwalkan", beri tahu user lewat saluran pilihannya (email, push, SMS), menghormati preferensi dan jam jangan-ganggu, tak pernah menduplikasi, dan tetap andal kalau penyedia SMS sesaat mati. Cakup fan-out, dedupe, dan jalur pengiriman.

:::quiz
Tampilkan satu rancangan yang mungkin

**Aliran:** aplikasi memancarkan event `interview_scheduled {event_id, user_id, application_id}` → Notification Service.

**Fan-out + preferensi:** muat pengaturan saluran user; buat satu pesan per saluran yang **diaktifkan** (katakanlah email + push, bukan SMS kalau mereka mematikannya). Lewati saluran dalam jendela jangan-ganggu (atau tunda sampai jendela berakhir).

**Dedupe:** kunci tiap pengiriman `(user_id, event_id, channel)` di Redis/DB; kalau ada, lewati — supaya event yang dipancarkan ulang atau redelivery queue tak mengirim dua email.

**Pengiriman + keandalan:** enqueue tiap pesan; channel worker memanggil penyedia email/push/SMS. Pada error penyedia transient, retry dengan backoff (Stage H); setelah max attempts, dead-letter dan alert. Penyedia SMS mati hanya menunda SMS; email/push tetap keluar.

**Aturan yang ditunjukkan:** fan out per preferensi, dedupe dengan kunci stabil, dan kirim lewat queue dengan retry — supaya notifikasi benar, sopan, dan andal.
:::

### 📝 Checklist review mandiri

- [ ] Aturan penghitungan (fixed/sliding) dipilih dengan alasan; penghitung di penyimpanan bersama
- [ ] Fan-out menghormati preferensi dan jangan-ganggu
- [ ] Tiap pengiriman di-dedupe dengan kunci stabil
- [ ] Pengiriman lewat queue dengan retry dan dead-letter

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/architecture/i-system-design-practice/02-notifications" ai="no-ai" title="Fan-out notifikasi, preferensi, dan dedupe"}
Implementasikan inti notification system: sebarkan satu event hanya ke saluran user yang diaktifkan, dan kirim tiap pesan paling banyak sekali (dedupe berdasarkan user + event + channel). Tes memeriksa saluran yang dimatikan dilewati dan event yang dikirim ulang tak mengirim duplikat.
:::

:::hints
- `fan_out(event, subscribers)`: untuk tiap subscriber, pancarkan `{"user_id", "channel", "event_id"}` untuk tiap saluran yang preferensinya True, dalam urutan saluran tetap (`email`, `push`, `sms`).
- `deliver_once(sent, message)`: bangun kunci `(user_id, event_id, channel)`; kalau ada di `sent` kembalikan `"duplicate"`, kalau tidak tambahkan dan kembalikan `"delivered"`.
- Jaga keduanya murni dan deterministik — tanpa pengiriman nyata, tanpa jam.
:::

## ✅ Cek cepat

:::quiz
Apa bug tepi dari fixed-window rate limiter, dan bagaimana sliding window memperbaikinya?

Fixed window reset pada jam, jadi user bisa mengirim batas penuh tepat sebelum batas dan lagi tepat sesudahnya — hampir dua kali batas dalam sesaat. Sliding window menghitung atas N detik terakhir dari *sekarang*, jadi tak ada batas reset untuk dieksploitasi dan lajunya tetap halus.
:::

:::quiz
Kenapa notification system harus mendeduplikasi pengiriman, dan kunci apa yang cocok?

Karena event dan pesan queue bisa diproses lebih dari sekali (at-least-once), dan tanpa dedupe user mendapat email/SMS yang sama dua kali. Mengunci tiap pengiriman dengan `(user_id, event_id, channel)` dan melewati yang sudah terkirim membuat pengiriman efektif sekali.
:::

## 📚 Lanjut belajar

- [Cloudflare: rate limiting best practices](https://developers.cloudflare.com/waf/rate-limiting-rules/)
- [System Design: notification service](https://systemdesign.one/notification-service/)
- [Redis: rate limiting patterns](https://redis.io/glossary/rate-limiting/)

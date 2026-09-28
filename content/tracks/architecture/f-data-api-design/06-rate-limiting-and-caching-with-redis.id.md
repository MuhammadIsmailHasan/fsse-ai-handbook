---
title: "Rate Limiting & Caching with Redis"
summary: Dua tugas yang dilakukan Redis dengan baik — rate limiting untuk melindungi API dari kelebihan beban, dan caching baca panas agar database tak ditanya hal yang sama berulang kali — dengan token-bucket dan cache-aside dibangun langsung.
sourceHash: a6d37ae47b17
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Kenapa API butuh **rate limiting**, dan ide **token-bucket**
- Kenapa **caching** baca panas melindungi database-mu
- Pola **cache-aside** dan apa arti **TTL**
- **Cache invalidation**: bagian yang sulit, dan cara menangani data basi
- Kenapa Redis biasanya rumah untuk keduanya
- Bagaimana ini terhubung ke RevoShop (Modul 5 sudah menambah Redis)

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Rate limit** | Batas berapa banyak request boleh dibuat seseorang |
| **Token bucket** | Ember token yang terisi ulang seiring waktu; tiap request menghabiskan satu |
| **Cache** | Simpanan cepat jawaban yang baru kamu hitung |
| **Cache-aside** | Cek cache dulu; saat miss, muat dari DB dan simpan |
| **TTL** | Time to live — berapa lama nilai cache tetap valid |
| **Cache hit / miss** | Jawaban sudah / belum ada di cache |
| **Invalidation** | Membuang entri cache basi saat data berubah |
| **Redis** | Penyimpan key-value cepat di memori untuk kedua tugas |

## 🧠 Ide besarnya

- **Rate limiting** seperti **pintu putar di stadion**: ia memasukkan orang dengan laju aman supaya tribun tak terinjak. Satu orang tak bisa mendorong masuk 10.000 kali per detik.
- **Caching** seperti **notes di dekat telepon**: pertama kali seseorang tanya "jam buka hari ini apa?", kamu cari dan catat; seratus penelepon berikutnya dapat jawaban dari notes, bukan pergi mengecek lagi.

Keduanya menjaga sumber dayamu yang lambat dan berharga (database) dari dihantam.

## ❓ Kenapa ini penting

Tanpa rate limiting, satu klien bermasalah atau satu penyerang bisa membanjiri API-mu dan menjatuhkan seluruh situs untuk semua orang — dan kalau API-mu berbiaya uang per panggilan (model AI), ia juga bisa menguras anggaranmu dalam menit.

Tanpa caching, database-mu menjawab query populer yang persis sama ribuan kali per detik. Ia jadi bottleneck, dan semuanya melambat. Caching mengubah "tanya database tiap kali" menjadi "tanya sekali, pakai ulang jawabannya".

## 📖 Langkah demi langkah

### 1. Rate limiting dengan token bucket

Beri tiap user **ember** yang memuat sampai N **token** dan terisi ulang dengan laju tetap. Tiap request menghabiskan satu token. Ember kosong → request ditolak (HTTP `429 Too Many Requests`).

```python
class TokenBucket:
    def __init__(self, capacity, refill_per_sec):
        self.capacity = capacity
        self.refill_per_sec = refill_per_sec
        self.tokens = capacity
        self.last = 0.0

    def allow(self, now, cost=1):
        self.tokens = min(self.capacity, self.tokens + (now - self.last) * self.refill_per_sec)
        self.last = now
        if self.tokens >= cost:
            self.tokens -= cost
            return True
        return False        # 429: slow down
```

Kenapa ember dan bukan penghitung biasa? Ia mengizinkan **burst** singkat (menghabiskan token tabungan) sambil tetap membatasi laju jangka panjang — lebih ramah daripada tembok keras "N per menit".

### 2. Di mana batasnya tinggal: Redis

Di aplikasi nyata kamu menjalankan banyak salinan server, jadi hitungannya tak bisa tinggal di memori satu server. Ia tinggal di **Redis**, yang dibagi semua server, dan Redis cukup cepat untuk dicek pada tiap request.

### 3. Caching: jangan tanya hal yang sama dua kali

Membaca halaman produk populer mengenai database tiap kali. Taruh jawabannya di cache (Redis) supaya baca berulang hampir instan.

### 4. Pola cache-aside

Pola caching yang paling umum:

```python
def get_product(cache, db, product_id, now, ttl=60):
    hit = cache.get(product_id)
    if hit and hit["expires"] > now:
        return hit["value"], "hit"          # fast path
    value = db.load(product_id)             # miss: go to the slow source
    cache[product_id] = {"value": value, "expires": now + ttl}
    return value, "miss"
```

- **Hit**: nilai ada di cache dan masih segar → kembalikan cepat.
- **Miss**: tak ada (atau kedaluwarsa) → muat dari database, simpan dengan **TTL**, kembalikan.

`ttl` (time to live) adalah jaring pengamanmu: bahkan kalau kamu lupa membuang entri basi, ia kedaluwarsa sendiri setelah beberapa saat.

### 5. Bagian yang sulit: invalidation

> "Hanya ada dua hal sulit di Ilmu Komputer: cache invalidation dan penamaan." — Phil Karlton

Kalau harga produk berubah tapi cache masih menyimpan harga lama, user melihat angka yang salah. Dua perbaikan umum:

| Strategi | Bagaimana | Trade-off |
|---|---|---|
| **TTL saja** | Biarkan entri kedaluwarsa setelah N detik | Sederhana; user bisa lihat data basi hingga N detik |
| **Write-through / delete-on-write** | Saat kamu update DB, hapus/update juga key cache | Segar seketika; lebih banyak kode, tak boleh lewatkan jalur tulis |

Kombinasi umum: hapus key cache saat tulis **dan** simpan TTL pendek sebagai cadangan.

### Pilih apa dan bagaimana caching

| Situasi | Lakukan ini |
|---|---|
| Sering dibaca, jarang berubah (katalog produk) | Cache dengan TTL lebih panjang |
| Sering dibaca, sering berubah (jumlah stok) | TTL pendek, atau jangan cache field yang volatil |
| Harus selalu akurat (saldo akun) | Jangan cache; baca sumbernya |
| API publik terbuka ke internet | Rate limit per user/IP |
| Downstream mahal/berbayar (panggilan AI) | Rate limit **dan** cache hasilnya |

- ✅ Cache baca panas yang jarang berubah; beri tiap entri TTL.
- ✅ Hapus atau update key cache saat data yang mendasarinya berubah.
- ✅ Rate limit endpoint publik dan mahal; kembalikan `429` dengan `Retry-After`.
- 🚫 Jangan cache data yang harus akurat sekarang (saldo, stok live untuk checkout).

## ⚠️ Kesalahan umum

- Caching tanpa TTL, sehingga data basi hidup selamanya setelah invalidation terlewat.
- Lupa membersihkan cache di salah satu jalur tulis, sehingga sebagian update tak pernah muncul.
- Rate limiting di memori satu server, sehingga ia reset/berbeda antar salinan server.
- Caching data privat per-user di bawah key bersama, membocorkan data satu user ke yang lain.
- Tak ada rate limit di endpoint yang memanggil API berbayar — satu loop menguras anggaran.

:::revoshop
Modul 5 sudah menambah Redis ke RevoShop. (1) Baca mana yang panas dan jarang berubah — katalog produk? Detail produk? Beri TTL dan katakan bagaimana kamu invalidasi saat update harga/stok. (2) Data mana yang **tidak** boleh di-cache saat checkout (stok live, total keranjang pembeli) dan kenapa? (3) Di mana rate limit akan melindungi RevoShop — percobaan login, endpoint pembayaran, atau pencarian publik? Apa yang kamu kembalikan saat batas tercapai?
:::

## 🏆 Praktik terbaik

- [ ] Rate limit endpoint publik, auth, dan downstream berbayar; jawab `429` dengan `Retry-After`.
- [ ] Simpan state rate-limit di Redis supaya dibagi semua salinan server.
- [ ] Cache baca panas, lambat, jarang berubah; selalu set TTL sebagai cadangan.
- [ ] Invalidasi (hapus/update key) di tiap jalur tulis yang mengubah data ter-cache.
- [ ] Beri namespace pada key cache dan jangan pernah bagi key antar-user untuk data privat.
- [ ] Jangan pernah cache data yang harus akurat saat itu juga (saldo, stok checkout).

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan rate limiting dengan analogi pintu-putar-stadion dan caching dengan analogi notes-di-dekat-telepon. Lalu jelaskan kenapa cache invalidation terkenal sulit: apa yang salah saat data berubah tapi notes masih menunjukkan jawaban lama.

## 📐 Rancang

CareerPilot punya endpoint AI `POST /suggestions` yang memanggil LLM berbayar (lambat dan berbiaya uang per panggilan), dan endpoint `GET /companies/:id` yang terus dihantam halaman daftar. Rancang: (a) rate limit untuk endpoint AI dan apa yang kamu kembalikan saat terlampaui; (b) cache untuk endpoint companies termasuk TTL dan cara kamu invalidasi saat info perusahaan diedit; (c) yang mana dari keduanya yang akan kamu cache hasilnya dan kenapa.

:::quiz
Tampilkan satu rancangan yang mungkin

- **(a) Rate limit endpoint AI**: token bucket per user di Redis, mis. kapasitas 5, isi ulang 1 token / 12 detik (≈5/menit dengan burst kecil). Saat ember kosong kembalikan `429` dengan `Retry-After: <detik>` supaya klien tahu kapan mencoba lagi. Ini melindungi anggaran LLM dan layanan.
- **(b) Cache companies (cache-aside)**: pada `GET`, cek Redis (`company:<id>`); hit → kembalikan; miss → muat dari DB, simpan dengan TTL 300 detik. Saat edit sebuah perusahaan, **hapus** `company:<id>` (delete-on-write) supaya baca berikutnya mengisi ulang; TTL adalah cadangan kalau satu jalur tulis terlewat.
- **(c) Cache yang mana?** Cache baca **companies** (jawaban sama, dibaca terus, jarang berubah). Untuk **suggestions** AI, cache hanya kalau input yang sama andal memberi output sama (mis. hash prompt-nya) — kalau tidak, rate limiting adalah perlindungan utama, bukan caching.

**Aturan yang ditunjukkan:** rate limit endpoint mahal/publik; cache baca panas jarang-berubah dengan TTL dan invalidasi delete-on-write.
:::

### 📝 Checklist review mandiri

- [ ] Rate limit ditempatkan di endpoint mahal/publik dengan `429` + `Retry-After`
- [ ] Cache punya TTL dan invalidasi jelas saat tulis
- [ ] State bersama (batas, cache) tinggal di Redis, bukan memori satu server
- [ ] Tak ada yang harus akurat di-cache; tak ada data privat di bawah key bersama

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/architecture/f-data-api-design/06-ratelimit-cache" ai="no-ai" title="Limiter token-bucket dan cache-aside"}
Implementasikan rate limiter token-bucket (terisi ulang seiring waktu, mengizinkan burst singkat, menolak saat kosong) dan `get` cache-aside (hit kembali cepat; miss memuat dari sumber, menyimpan dengan TTL, dan kedaluwarsa). Tes membuktikan limiter terisi ulang setelah menunggu dan bahwa loader jalan hanya saat miss.
:::

:::hints
- Oper `now` (nilai detik float) ke tiap panggilan supaya tes deterministik — jangan baca jam nyata.
- Isi ulang ember: `tokens = min(capacity, tokens + (now - last) * refill_per_sec)`, update `last = now`, lalu belanjakan kalau cukup.
- Cache-aside: perlakukan entri sebagai miss kalau tak ada **atau** `entry["expires"] <= now`; hitung panggilan loader untuk membuktikan miss vs hit.
:::

## ✅ Cek cepat

:::quiz
Kenapa menyimpan hitungan rate-limit dan cache di Redis alih-alih di memori tiap server?

Karena aplikasi nyata menjalankan banyak salinan server. State di memori akan berbeda per server (batas yang reset saat request mengenai server berbeda, atau cache yang tak dibagi). Redis adalah penyimpan bersama yang cepat yang dipakai semua server, jadi batas dan cache konsisten di mana-mana.
:::

:::quiz
Apa itu cache invalidation, dan kenapa sulit?

Ia membuang atau memperbarui entri ter-cache saat data yang mendasarinya berubah. Sulit karena kamu harus menangkap *setiap* jalur tulis yang memengaruhi nilai ter-cache; lewatkan satu dan user terus melihat data basi — itulah kenapa TTL disimpan sebagai cadangan.
:::

## 📚 Lanjut belajar

- [Redis: caching patterns](https://redis.io/learn/howtos/solutions/caching-architecture/write-through)
- [Cloudflare: what is rate limiting?](https://www.cloudflare.com/learning/bots/what-is-rate-limiting/)
- [Token bucket algorithm](https://en.wikipedia.org/wiki/Token_bucket)

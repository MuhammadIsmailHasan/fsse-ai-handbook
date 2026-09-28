---
title: "Replication & Sharding"
summary: Dua cara menumbuhkan database melewati satu mesin — replication (salinan untuk lebih banyak baca dan keamanan) dan sharding (membagi data ke banyak mesin untuk lebih banyak tulis) — plus biaya nyatanya, replication lag dan query lintas-shard yang sulit.
sourceHash: 9cfe77c23e43
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- **Replication**: menyimpan salinan database untuk lebih banyak baca dan keamanan
- Apa itu **replication lag** dan bug yang ditimbulkannya
- **Sharding**: membagi satu tabel besar ke beberapa mesin
- Cara memilih **shard key** dan apa itu **hotspot**
- Kenapa query dan transaksi lintas-shard sulit
- Urutan memakai ini (dan kenapa kamu mungkin belum butuh sharding)

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Replication** | Menyimpan salinan database yang sama secara langsung |
| **Primary** | Satu salinan yang menerima tulis |
| **Replica** | Salinan hanya-baca yang selalu sinkron dengan primary |
| **Replication lag** | Jeda singkat sebelum sebuah tulis sampai ke replika |
| **Sharding** | Membagi baris ke beberapa database |
| **Shard key** | Nilai yang menentukan sebuah baris tinggal di shard mana |
| **Hotspot** | Satu shard mendapat jauh lebih banyak lalu lintas daripada lainnya |
| **Failover** | Mengangkat replika saat primary mati |

## 🧠 Ide besarnya

**Replication** seperti **memfotokopi buku besar**: satu salinan induk (**primary**) tempat kamu menulis, dan beberapa fotokopi (**replica**) dibagikan supaya banyak orang bisa *membaca* sekaligus. Salinan dibuat cepat, tapi untuk sepersekian detik sebuah fotokopi bisa sedikit tertinggal dari induknya.

**Sharding** seperti **membelah satu buku telepon raksasa menjadi jilid A–M dan N–Z**, masing-masing di ruangan berbeda. Tak ada satu jilid pun yang terlalu berat — tapi "daftarkan semua yang bernama Ismail" kini berarti mengunjungi *kedua* ruangan.

## ❓ Kenapa ini penting

Satu database di satu mesin punya batas: hanya sekian baca, tulis, dan sekian data yang muat. Dua masalah yang sangat berbeda menabrak batas itu, dan mereka butuh alat berbeda:

- **Terlalu banyak baca** (halaman produk toko ramai) → **replication**.
- **Terlalu banyak tulis / terlalu banyak data untuk satu mesin** → **sharding**.

Memakai yang salah — atau sharding terlalu dini — menambah kompleksitas besar tanpa manfaat. Tahu masalah mana yang kamu punya adalah seluruh skill-nya.

## 📖 Langkah demi langkah

### 1. Replication: salinan untuk baca dan keamanan

Kamu menyimpan satu **primary** (menerima tulis) dan satu atau lebih **replica** (salinan hanya-baca). Primary mengalirkan setiap perubahan ke replika.

```
        writes                 reads
  app  ───────▶  PRIMARY  ──▶  REPLICA 1  ◀───  app
                    │      ──▶  REPLICA 2  ◀───  app
                    └──────▶ (stream of changes)
```

Dua kemenangan besar:
- **Skalakan baca**: kirim query baca ke replika, sehingga primary lega. Kebanyakan aplikasi jauh lebih banyak membaca daripada menulis, jadi ini sangat membantu.
- **Keamanan / failover**: kalau primary mati, angkat sebuah replika menjadi primary baru (**failover**).

### 2. Jebakannya: replication lag

Salinan tidak *instan*. Untuk sesaat sebuah replika bisa sedikit tertinggal dari primary — inilah **replication lag**. Ia menyebabkan bug klasik:

```
1. User updates their profile name    → written to PRIMARY
2. Page reloads, reads from a REPLICA → replica hasn't caught up yet
3. User sees their OLD name and thinks the save failed
```

Perbaikan: baca data yang **baru saja kamu tulis** dari primary (atau tunggu replika menyusul). Ini disebut "read-your-writes". Baca yang bisa menoleransi basi sedetik (daftar produk) aman di replika.

### 3. Sharding: membagi datanya sendiri

Replication menyalin *seluruh* database berkali-kali — ia tidak membantu saat datanya terlalu besar atau tulisnya terlalu banyak untuk satu mesin. **Sharding** membagi baris ke banyak mesin:

```
users 1–1,000,000      → SHARD A
users 1,000,001–2,000,000 → SHARD B
users 2,000,001–3,000,000 → SHARD C
```

Tiap shard adalah database penuh yang menyimpan **sepotong** baris. Tulis dan penyimpanan kini tersebar di banyak mesin.

### 4. Shard key menentukan segalanya

**Shard key** adalah nilai yang dipakai untuk memilih shard sebuah baris (sering lewat hash):

```python
shard = hash(user_id) % number_of_shards
```

Memilihnya dengan baik adalah bagian yang sulit:
- Pilih kunci yang **menyebar beban merata**. `user_id` biasanya bagus; `country` buruk kalau 90% user di satu negara (shard itu jadi **hotspot**).
- Pilih kunci yang **sudah kamu punya** saat query. Kalau kamu shard berdasarkan `user_id` tapi sering mencari lewat `email`, kamu tak tahu harus tanya shard mana → kamu harus tanya semuanya.

### 5. Kenapa sharding menyakitkan

| Mudah di satu DB | Dengan sharding |
|---|---|
| JOIN atas semua data | ❌ data ada di mesin berbeda |
| `COUNT(*)` atas segalanya | ❌ harus tanya tiap shard dan jumlahkan |
| Transaksi mencakup dua user | ❌ melintasi mesin — sangat sulit |
| Menambah kapasitas | ⚠️ resharding memindahkan banyak data |

Inilah kenapa sharding adalah **pilihan terakhir**. Kamu menambah kompleksitas nyata dan permanen ke tiap query dan transaksi.

### Urutan memakai penskalaan

| Langkah | Lakukan ini dulu |
|---|---|
| 1 | Optimasi: tambah index, perbaiki query lambat, cache baca panas (Redis) |
| 2 | Skalakan naik: mesin lebih besar (CPU/RAM lebih banyak) — efektif meski membosankan |
| 3 | **Replication**: pindahkan baca ke replika |
| 4 | **Sharding**: hanya saat satu mesin benar-benar tak muat tulis/data |

- ✅ Selesaikan penskalaan baca dengan caching dan replika jauh sebelum sharding.
- ✅ Kalau harus sharding, pilih shard key yang menyebar beban dan cocok dengan query-mu.
- 🚫 Jangan sharding "biar siap" — kebanyakan aplikasi tak pernah butuh, dan itu memperlambat seluruh pengembanganmu.

## ⚠️ Kesalahan umum

- Membaca data yang baru ditulis dari replika dan menampilkan hasil basi ke user (replication lag).
- Menganggap replika sebagai backup — ia menyalin kesalahan juga (`DELETE` tereplikasi seketika). Kamu tetap butuh backup nyata.
- Sharding dengan kunci yang miring (`country`, `is_premium`) dan menciptakan hotspot.
- Sharding terlalu dini, lalu bergelut dengan JOIN dan hitungan lintas-shard selamanya.

:::revoshop
RevoShop berjalan di satu PostgreSQL. (1) Halaman mana yang **banyak-baca** (daftar produk, detail produk) dan bisa aman memakai replika? Baca mana yang harus segar (keranjang/order pembeli sendiri tepat setelah checkout)? (2) Kalau RevoShop suatu saat harus sharding, shard key apa yang menyebar beban dan cocok dengan query utamanya — `user_id`, `order_id`, atau `product_id`? Query apa yang jadi menyakitkan? (3) Sebelum sharding, langkah lebih murah apa (index, caching Redis, mesin lebih besar, read replica) yang akan kamu coba dulu?
:::

## 🏆 Praktik terbaik

- [ ] Habiskan index, caching, mesin lebih besar, dan read replica sebelum sharding.
- [ ] Kirim baca yang toleran ke replika; baca-tulisanmu-sendiri dari primary.
- [ ] Simpan backup nyata — replika bukan backup (mereka menyalin delete juga).
- [ ] Kalau sharding, pilih shard key yang menyebar beban merata dan kamu punya saat query.
- [ ] Rancang untuk menghindari JOIN/transaksi lintas-shard; simpan data terkait di shard yang sama.
- [ ] Punya rencana failover yang teruji supaya mengangkat replika bukan percobaan pertamamu saat gangguan.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan replication vs sharding dengan analogi buku-besar-difotokopi dan buku-telepon-dibelah. Lalu jelaskan replication lag: kenapa user bisa memperbarui namanya dan sesaat masih melihat nama lama.

## 📐 Rancang

Sebuah aplikasi sosial punya 50 juta user. Feed (membaca post) adalah 95% lalu lintas; posting 5%. Kemudian, tabel *posts* saja tumbuh terlalu besar untuk satu mesin. Rancang jalur penskalaan: apa yang kamu lakukan untuk feed yang banyak-baca, dan apa yang akan kamu lakukan saat tabel posts melampaui satu mesin — termasuk shard key dan satu query yang jadi lebih sulit.

:::quiz
Tampilkan satu rancangan yang mungkin

**Feed banyak-baca dulu → replication + cache.** Tambah read replica dan arahkan baca feed ke sana; cache feed panas di Redis. Ini menangani 95% dengan murah. Tulis (posting) tetap ke primary — 5% mudah untuk satu mesin.

**Tabel posts terlalu besar → shard posts.** Shard key: `user_id` (penulis), supaya semua post satu user di satu shard dan "tampilkan post user ini" mengenai satu shard. Hash `user_id` untuk menyebar beban merata.

**Yang jadi lebih sulit:** feed global yang mencampur banyak penulis, atau "hitung semua post hari ini", kini mencakup tiap shard — kamu harus query semua shard dan gabungkan, atau prakomputasi feed/hitungan. Read-your-writes (user melihat post barunya sendiri) sebaiknya baca dari primary atau shard-nya sendiri.

**Aturan yang ditunjukkan:** replikasi untuk baca, sharding hanya satu tabel yang benar-benar melampaui mesin, dan pilih shard key yang menjaga data tiap user tetap bersama.
:::

### 📝 Checklist review mandiri

- [ ] Penskalaan baca diselesaikan dengan replika/cache sebelum sharding apa pun
- [ ] Shard key menyebar beban dan cocok dengan query utama
- [ ] Satu query lintas-shard yang kini sulit disebutkan
- [ ] Kesegaran ditangani (read-your-writes dari primary)

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/architecture/f-data-api-design/03-sharding" ai="no-ai" title="Shard router dan biaya resharding"}
Implementasikan shard router berbasis hash, router baca/tulis (tulis → primary, baca → replica), dan fungsi yang menghitung berapa key berpindah shard saat kamu berubah dari N ke N+1 shard. Tes menunjukkan sharding `hash % n` naif memindahkan *sebagian besar* key saat resize — alasan sistem nyata memakai consistent hashing.
:::

:::hints
- Pakai hash stabil (`hashlib.md5`), bukan `hash()` bawaan Python, supaya hasilnya sama tiap run.
- `shard_for(key, n)` = `stable_hash(key) % n`.
- `keys_moved` : hitung key yang `shard_for(key, old_n) != shard_for(key, new_n)`.
- Router baca/tulis: tulis selalu ke `"primary"`; baca ke `"replica"`.
:::

## ✅ Cek cepat

:::quiz
Kamu punya terlalu banyak request baca tapi tulis baik-baik saja. Replication atau sharding?

**Replication.** Tambah read replica dan kirim query baca ke sana, melegakan primary. Sharding untuk saat tulis atau ukuran data melampaui satu mesin — masalah yang berbeda.
:::

:::quiz
Kenapa memilih shard key yang baik begitu penting?

Karena ia menentukan keseimbangan beban dan biaya query: kunci yang miring menciptakan hotspot (satu shard kelebihan beban), dan kunci yang tak kamu punya saat query memaksamu bertanya ke tiap shard. Kunci yang baik menyebar beban merata dan cocok dengan cara kamu query.
:::

## 📚 Lanjut belajar

- [PostgreSQL: high availability & replication](https://www.postgresql.org/docs/current/high-availability.html)
- [Martin Kleppmann, *DDIA*, Ch. 5–6 (replication, partitioning)](https://dataintensive.net/)
- [Consistent hashing explained](https://www.toptal.com/big-data/consistent-hashing)

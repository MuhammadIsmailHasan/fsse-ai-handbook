---
title: "Batas Layanan & Kepemilikan Data"
summary: Setiap layanan memiliki datanya sendiri dan hanya boleh menyentuh tabel miliknya; layanan lain harus minta lewat API. Satu aturan ini membuat layanan benar-benar independen — melanggarnya mengubah microservice kembali menjadi monolith.
sourceHash: 0d061387fd58
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa artinya sebuah layanan **memiliki** datanya sendiri
- Mengapa aturannya: **hanya pemilik yang menyentuh tabel**; yang lain minta lewat API
- Apa yang dilakukan **database bersama** terhadap layananmu (ia menempel mereka kembali)
- Bagaimana layanan mendapatkan data yang mereka butuhkan tanpa menyelinap ke tabel milik orang lain
- Cara menemukan batas yang rusak sebelum ia melukai sistemmu

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Kepemilikan data** | Satu layanan adalah satu-satunya yang boleh membaca/menulis sejumlah tabel |
| **Batas** | Tepi dari apa yang dimiliki dan dikontrol oleh sebuah layanan |
| **Database bersama** | Dua atau lebih layanan pakai tabel yang sama secara langsung |
| **API** | Pintu depan yang diberikan layanan agar orang lain bisa minta hal dari layanan itu |
| **Sumber kebenaran** | Satu tempat yang memegang nilai asli yang benar |
| **Saling bergantung** | Seberapa erat dua bagian saling tergantung |

## 🧠 Ide besarnya

Bayangkan setiap layanan sebagai **warung dengan kasir sendiri dan buku catatan stok sendiri**. Aturan di pasar sederhana: **hanya pemilik warung yang buka kasirnya sendiri.** Kalau warung sate mau tahu harga es teh, dia *minta* ke warung minuman — dia tidak pernah masuk ke belakang dan buka laci warung minuman.

Kalau semua orang bisa buka laci orang lain, kamu tidak benar-benar punya warung terpisah. Kamu punya satu laci bersama yang beberapa orang ambil — dan saat satu orang mengubah posisi barangnya, tangan orang lain ambil yang salah.

Laci bersama itu adalah **database bersama**, dan itu adalah cara paling umum bagaimana "microservice" diam-diam berubah kembali menjadi monolith yang berantakan.

## ❓ Kenapa ini penting

Alasan membagi menjadi beberapa layanan adalah agar setiap layanan bisa berubah sendiri — deploy sendiri, schema sendiri, kecepatannya sendiri. **Kepemilikan data adalah yang membuat itu benar.** Kalau layanan Orders adalah satu-satunya yang menyentuh tabel `orders`, maka ia bisa mengubah nama kolom, menambah index, atau mengubah cara order disimpan, dan tidak ada orang lain yang perhatian.

Tapi saat layanan kedua membaca atau menulis tabel yang sama secara langsung:

- Orders tidak bisa lagi mengubah tabelnya dengan aman — mengubah nama sekarang merusak layanan lain juga.
- Untuk mengubah schema, **kedua** tim harus terkoordinasi dan deploy bersama. Itu persis rasa sakit yang ingin dihilangkan microservice.
- Bug di layanan lain bisa merusak data Orders, dan Orders disalahkan karena data yang tidak dia tulis.
- Tidak ada lagi satu **sumber kebenaran** yang jelas — dua layanan "memiliki" nilai itu, dan mereka bergeser terpisah.

Jadi database bersama memberikan semua biaya microservice (jaringan, banyak aplikasi, kerumitan) dengan **tanpa** independensi. Kamu benar-benar lebih baik dengan satu monolith yang bersih. Aturan batas — *miliki data kamu, minta data orang lain* — adalah yang membeli independensi kembali.

## 📖 Langkah demi langkah

### 1. Satu pemilik per tabel

Setiap tabel punya tepat **satu** layanan pemilik. Layanan itu adalah satu-satunya kode yang menjalankan `SELECT`, `INSERT`, `UPDATE` atau `DELETE` di atasnya.

| Tabel | Pemilik |
|---|---|
| `products`, `product_images` | Layanan Catalog |
| `orders`, `order_items` | Layanan Orders |
| `payments`, `refunds` | Layanan Payments |

Kalau kamu tidak bisa sebutkan siapa pemilik tabel dalam satu kata, itu tanda bahwa batasnya belum jelas — alasan untuk tetap simpan bagian-bagian itu bersama (monolith dulu).

### 2. Cara orang lain dapat data: minta, jangan menyelinap

Layanan Orders butuh nama dan harga produk. Ia **tidak** query tabel `products`. Sebaliknya ia minta ke layanan Catalog lewat API:

```python
# Inside the Orders service — it has NO access to the products table.
product = catalog_client.get_product(product_id)   # an HTTP call to Catalog
line_total = product.price * quantity
```

Catalog tetap dalam kendali apa itu "produk" dan bagaimana ia disimpan. Orders hanya terima jawabannya.

### 3. Saat kamu tidak bisa panggil setiap waktu: simpan salinannya

Minta lewat jaringan setiap waktu bisa lambat, dan ia rusak kalau layanan lain tidak aktif. Jadi layanan sering **simpan salinan kecil** dari bit-bit yang mereka butuhkan — dan ingat bahwa salinan itu *bukan* sumber kebenaran.

Misalnya, saat order ditempatkan, Orders bisa simpan **nama produk dan harga saat itu** langsung di baris `order_items`:

```python
# Store the price AS IT WAS when the order was placed.
order_item = OrderItem(
    product_id=product.id,
    product_name=product.name,   # a snapshot, owned by Orders now
    unit_price=product.price,    # the price the customer actually paid
    quantity=quantity,
)
```

Ini bukan melanggar aturan — ini hal yang *benar*. Sebuah order harus ingat harga apa yang dibayar pelanggan bahkan kalau Catalog ubah harga besok. Salinan itu milik order. Catalog tetap sumber kebenaran untuk harga *saat ini*.

### 4. Tetap terkini

Kalau sebuah layanan perlu bereaksi saat data orang lain berubah (Catalog turunkan harga, dan Search harus indeks ulang), pemilik **publikasikan event** — "produk 42 berubah" — dan layanan yang tertarik perbarui salinan mereka sendiri. Kamu akan lihat pola async ini di pelajaran berikutnya. Ide utamanya tetap sama: **pemilik umumkan; orang lain simpan salinan mereka sendiri.** Tidak ada orang yang menyelinap ke tabel pemilik.

### Pilih pengaturan kamu

- ✅ Satu pemilik jelas per tabel; semua orang lain pakai API pemilik.
- ✅ Salinan data yang tidak boleh berubah nanti (harga dibayar, alamat dikirim).
- 🚫 Dua layanan menulis tabel yang sama — itu satu layanan menyamar; simpan mereka bersama.
- 🚫 Database "bersama" "hanya untuk laporan" yang pelan-pelan tumbuh menjadi penulisan bersama.

## ⚠️ Kesalahan umum

- **Database bersama** di mana beberapa layanan membaca dan menulis tabel yang sama — perangkap klasik.
- Satu layanan menyelinap ke tabel orang lain "hanya untuk baca" — baca hari ini menjadi tulis besok, dan kalau saja pemilik tidak bisa lagi ubah schema-nya dengan bebas.
- Membagi kode menjadi layanan tapi tinggalkan **satu database besar** di belakangnya. Database adalah tempat saling bergantung hidup, jadi itu monolith dengan lompatan jaringan ekstra.
- Perlakukan salinan lokal sebagai sumber kebenaran dan biarkan dua layanan "miliki" nilai yang sama.

## 🏆 Praktik terbaik

- [ ] Beri setiap tabel tepat **satu** layanan pemilik.
- [ ] Biarkan hanya pemilik baca dan tulis tabel miliknya; orang lain pakai API.
- [ ] Simpan **salinan** dari nilai yang harus tetap tetap (harga dibayar, alamat dipakai).
- [ ] Simpan salinan lokal untuk kecepatan, tapi ingat pemilik adalah sumber kebenaran.
- [ ] Kalau dua bagian harus berbagi database, perlakukan itu sebagai tanda untuk simpan mereka sebagai **satu** layanan.

:::revoshop
1. **Daftar pemiliknya.** Kelompokkan tabel RevoShop dengan siapa yang akan milikinya kalau kamu pisah: catalog (`products`…), orders (`orders`, `order_items`…), payments (berkaitan Midtrans), users/auth. Apakah setiap tabel mudah diletakkan di bawah satu pemilik?
2. **Cari kerumitannya.** Apakah ada tabel yang beberapa bagian baca *dan* tulis (misalnya, apakah kode order tulis ke product stock)? Itu batas-batas sulit — saling bergantung yang akan membuat pisah itu menyakitkan.
3. **Cek salinan.** Saat order RevoShop ditempatkan, apakah baris order simpan harga saat beli, atau apakah ia baca harga produk sekarang nanti? Yang mana yang benar, dan kenapa?
4. **Panggilan jujur.** Karena RevoShop bagikan satu database hari ini, pisah layanan akan arti terlebih dahulu *tidak bagi* tabel-tabel itu. Apakah pekerjaan itu layak sekarang? (Sebutkan pekerjaannya adalah pokok — kamu tidak harus lakukannya.)
:::

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Teman satu tim ingin pisah RevoShop menjadi layanan Orders dan layanan Catalog tapi "simpan database yang sama supaya lebih mudah". Gunakan analogi warung pasar, jelaskan kenapa database bersama itu membuang seluruh manfaat pisah.

## 📐 Rancang

Rancang batas Orders ↔ Catalog. Sebutkan tabel mana yang dimiliki setiap layanan, persis apa yang Orders butuh dari Catalog, apakah ia minta setiap waktu atau simpan salinan, dan apa yang terjadi ke harga order lama saat Catalog ubah harganya besok.

:::quiz
Lihat contoh jawaban

Catalog miliki `products` dan `product_images`; Orders miliki `orders` dan `order_items`. Saat tempatkan order, Orders minta Catalog untuk nama dan harga sekarang (panggilan API), lalu **simpan salinan** dari `product_name` dan `unit_price` di baris order. Nanti, kalau Catalog naikkan harga, order lama tidak terpengaruh — mereka simpan harga yang benar-benar dibayar pelanggan, karena nilai itu sekarang milik order. Catalog tetap sumber kebenaran untuk harga *sekarang* yang ditampilkan di halaman produk.
:::

### 📝 Checklist review mandiri

- [ ] Setiap tabel punya tepat satu pemilik
- [ ] Tidak ada layanan yang baca atau tulis tabel orang lain secara langsung
- [ ] Nilai yang tidak boleh berubah nanti disimpan sebagai salinan

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m5/w5/02-data-ownership" ai="no-ai" title="Cari batas kepemilikan yang rusak"}
Diberi satu set layanan dan tabel yang dimiliki dan ditulis oleh setiap layanan, tulis `find_ownership_violations(services)` yang laporkan setiap kasus di mana sebuah layanan menulis tabel yang dimiliki layanan lain — perangkap database bersama yang ubah microservice kembali menjadi monolith.
:::

:::hints
- Pertama buat peta dari `table -> owner name` dengan berjalan di setiap `owns` set layanan.
- Lalu, untuk setiap layanan, lihat setiap tabel yang ia `writes` yang dimiliki layanan *berbeda*.
- Buat setiap pesan dengan f-string dan `sorted(...)` daftar akhir jadi hasil stabil.
:::

## ✅ Cek cepat

:::quiz
Kenapa database bersama membatalkan sebagian besar manfaat pisah menjadi layanan?

Independensi datang dari setiap layanan yang kontrol datanya sendiri. Kalau dua layanan sentuh tabel yang sama, tidak ada yang bisa ubah schema tanpa rusak yang lain, jadi mereka harus deploy bersama dan terkoordinasi terus-menerus — persis saling bergantung yang ingin dihilangkan microservice. Kamu bayar biaya banyak aplikasi dan dapat tidak ada kebebasan.
:::

:::quiz
Baris order simpan `unit_price` saat pembelian, walaupun layanan Catalog miliki harga produk. Apakah itu melanggar batas?

Tidak — itu benar. Harga yang dibayar pelanggan adalah fakta yang milik order dan tidak boleh pernah berubah, jadi Orders simpan salinannya sendiri. Catalog tetap sumber kebenaran untuk harga *sekarang*. Orders tidak baca tabel Catalog; ia salin nilai saat order dibuat.
:::

## 📚 Lanjut belajar

- [Microservices.io: Database per service](https://microservices.io/patterns/data/database-per-service.html)
- [Martin Fowler: BoundedContext](https://martinfowler.com/bliki/BoundedContext.html)
- [microservices.io: Shared database anti-pattern](https://microservices.io/patterns/data/shared-database.html)

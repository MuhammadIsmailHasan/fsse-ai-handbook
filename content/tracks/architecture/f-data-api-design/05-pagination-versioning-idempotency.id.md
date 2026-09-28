---
title: "Pagination, Versioning & Idempotency"
summary: Tiga kebiasaan yang menjaga API tetap aman saat tumbuh — paginasi daftar besar (offset vs cursor), versioning agar tak merusak klien lama, dan idempotency key agar pembayaran yang diulang menagih sekali, bukan dua kali.
sourceHash: 3d205858fda9
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Kenapa mengembalikan seluruh daftar berbahaya, dan cara **memaginasinya**
- Paginasi **offset** vs **cursor**, dan kapan masing-masing cocok
- Cara **memversikan** API agar aplikasi lama tetap bekerja
- **Idempotency**: membuat request berulang aman (menagih sekali, bukan dua kali)
- Bagaimana ini muncul di alur checkout nyata seperti RevoShop

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Pagination** | Mengirim daftar besar dalam halaman kecil |
| **Offset** | "Lewati N baris, lalu beri aku halaman berikutnya" |
| **Cursor** | Penunjuk ke "lanjut setelah item ini" |
| **Versioning** | Menjaga perilaku API lama dan baru berdampingan |
| **Breaking change** | Perubahan yang membuat klien lama gagal |
| **Idempotent** | Melakukannya lagi punya efek sama seperti sekali |
| **Idempotency key** | Id yang dikirim klien agar server mengabaikan duplikat |

## 🧠 Ide besarnya

- **Pagination** seperti **buku, bukan gulungan**: kamu membaca halaman demi halaman, bukan satu strip tak berujung. Tak ada yang memberimu 2 juta baris sekaligus.
- **Versioning** seperti **menjaga jalan lama tetap terbuka sambil membangun yang baru**: mobil yang sudah di jalan lama tak menabrak hanya karena kamu membuka rute yang lebih baik.
- **Idempotency** seperti **cap "sudah dibayar" di struk**: kalau pelayan datang lagi dengan tagihan yang sama, cap itu bilang "yang ini selesai — jangan tagih lagi".

## ❓ Kenapa ini penting

Ketiganya yang memisahkan API mainan dari API produksi:

- Tanpa pagination → satu request mencoba mengembalikan segalanya, dan server atau HP kehabisan memori.
- Tanpa versioning → hari kamu mengubah sebuah field, tiap aplikasi mobile lama di lapangan rusak.
- Tanpa idempotency → koneksi goyah membuat klien mengulang request "bayar", dan pelanggan ditagih dua kali.

Mereka murah ditambahkan sejak awal dan menyakitkan dipasang setelah pengguna nyata datang.

## 📖 Langkah demi langkah

### 1. Pagination: jangan pernah kembalikan seluruh daftar

Kembalikan satu **halaman** dan beri tahu klien cara mendapat berikutnya.

**Paginasi offset** — "lewati N, ambil M":

```
GET /orders?limit=20&offset=40      → rows 41–60
```

Sederhana dan membuatmu bisa lompat ke halaman mana pun. Tapi di tabel besar, `offset=1000000` tetap membuat database menghitung melewati sejuta baris (lambat), dan kalau baris baru disisipkan saat kamu paginasi, item bisa bergeser sehingga kamu melihat duplikat atau celah.

**Paginasi cursor** — "beri aku 20 berikutnya setelah item ini":

```
GET /orders?limit=20&after=order_1042    → the 20 orders after id 1042
```

Server memakai cursor dengan kolom ter-index (`WHERE id > 1042 ORDER BY id LIMIT 20`), yang tetap cepat sedalam apa pun kamu pergi, dan stabil saat baris ditambahkan. Trade-off-nya: kamu tak bisa lompat langsung ke "halaman 500", hanya maju/mundur.

| | Offset | Cursor |
|---|---|---|
| Lompat ke halaman mana pun | ✅ | ❌ (hanya maju/mundur) |
| Cepat di halaman dalam | ❌ melambat | ✅ tetap cepat |
| Stabil saat data berubah | ❌ bisa bergeser | ✅ stabil |
| Terbaik untuk | tabel kecil/admin | infinite scroll, feed besar |

### 2. Versioning: berubah tanpa merusak klien lama

**Breaking change** adalah apa pun yang membuat klien yang ada gagal: menghapus field, mengganti namanya, mengubah tipe, atau membuat field opsional jadi wajib. Aplikasi mobile di saku seseorang tak bisa diperbarui seketika, jadi kamu menjaga bentuk lama tetap bekerja.

Pendekatan umum:

```
/v1/orders   and   /v2/orders          # version in the URL (most visible)
Accept: application/vnd.api+json; version=2   # version in a header
```

Aturan praktis: **tambah** field dengan bebas (non-breaking); **jangan pernah hapus atau alihfungsikan** field di versi yang sama; perkenalkan breaking change hanya di versi baru, dan beri klien lama waktu untuk pindah.

### 3. Idempotency: buat retry aman

Jaringan tidak andal. Klien mengirim "buat pembayaran", responsnya hilang, jadi klien **mengulang** — tapi pembayaran mungkin sudah lolos. Tanpa perlindungan, itu tagihan ganda.

Perbaikan: klien mengirim **idempotency key** (id unik yang ia hasilkan untuk aksi itu):

```
POST /payments
Idempotency-Key: 7f3a-...-9c2
```

Logika server:

```python
def create_payment(key, amount):
    if key in seen:            # already processed this exact request
        return seen[key]       # return the SAME result, don't charge again
    result = charge(amount)
    seen[key] = result
    return result
```

Kini mengulang dengan key yang sama mengembalikan hasil pertama alih-alih menagih dua kali — request-nya **idempotent**. Catatan: `GET`, `PUT`, dan `DELETE` secara alami idempotent; `POST` (create) yang berbahaya dan butuh key.

### Pilih pendekatanmu

| Situasi | Lakukan ini |
|---|---|
| Daftar yang bisa tumbuh tak terbatas | Selalu paginasi |
| Tabel admin, lompat ke halaman N | Paginasi offset |
| Infinite scroll / feed besar | Paginasi cursor |
| API publik/mobile yang akan kamu kembangkan | Versikan sejak hari pertama (bahkan `/v1`) |
| Setiap "buat pembayaran / buat order" | Wajibkan idempotency key |

- ✅ Paginasi tiap endpoint daftar sejak awal.
- ✅ Rilis `/v1` di hari pertama supaya `/v2` punya tempat tujuan.
- ✅ Buat operasi pemindah-uang dan create idempotent.
- 🚫 Jangan kembalikan daftar tak terbatas "karena sekarang kecil".

## ⚠️ Kesalahan umum

- Endpoint yang mengembalikan semua baris, baik saat testing, yang ambruk dengan data nyata.
- Paginasi offset dalam yang makin lambat tiap halaman di tabel besar.
- Menghapus atau mengganti nama field tanpa versi baru, merusak aplikasi lama dalam semalam.
- `POST /payments` yang diulang tanpa idempotency key → tagihan ganda.
- Memakai ulang idempotency key yang sama untuk aksi yang benar-benar berbeda (menyembunyikan request nyata).

:::revoshop
Lihat endpoint checkout dan daftar RevoShop. (1) Apakah daftar order/produk berpaginasi, atau bisa mengembalikan segalanya? Apakah offset atau cursor cocok untuk halaman "order saya"? (2) Webhook pembayaran Midtrans bisa terkirim lebih dari sekali — apakah penanganan RevoShop **idempotent** (apakah memproses pembayaran yang sama dua kali mengubah stok/saldo dua kali)? (3) Kalau kamu harus mengubah field respons order, bagaimana melakukannya tanpa merusak klien mobile lama hipotetis?
:::

## 🏆 Praktik terbaik

- [ ] Paginasi tiap daftar; pilih offset untuk admin/lompat-halaman, cursor untuk feed besar/tumbuh.
- [ ] Kembalikan metadata paginasi (cursor berikutnya atau total) supaya klien tahu cara melanjutkan.
- [ ] Versikan API-mu; hanya tambah field dalam satu versi, jangan hapus/ganti nama.
- [ ] Wajibkan idempotency key di endpoint create/pembayaran; simpan dan kembalikan hasil pertama.
- [ ] Buat handler webhook idempotent — penyedia mengulang pengiriman.
- [ ] Dokumentasikan jadwal deprecation supaya klien punya waktu bermigrasi.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan idempotency ke orang non-programmer dengan analogi cap "sudah dibayar": kenapa toko yang mengecap struk tak akan menagihmu dua kali kalau mesin kartu tersendat dan kasir mengulang.

## 📐 Rancang

CareerPilot membiarkan user impor massal pekerjaan tersimpan (bisa ribuan) dan nanti "melamar", yang memakan kredit berbayar. Rancang: (a) bagaimana daftar pekerjaan-impor dipaginasi dan kenapa; (b) bagaimana kamu memversikan API saat nanti menambah field wajib ke request lamaran; (c) bagaimana kamu membuat "melamar" aman terhadap double-click atau retry jaringan supaya user tak pernah ditagih dua kredit.

:::quiz
Tampilkan satu rancangan yang mungkin

- **(a) Pagination**: daftar pekerjaan-impor bisa sangat besar dan di-scroll, jadi pakai paginasi **cursor** (`after=<job_id>`, ter-index oleh `created_at, id`) — cepat di kedalaman apa pun dan stabil saat impor baru tiba. Offset akan melambat dan bisa menduplikasi baris saat impor ditambahkan.
- **(b) Versioning**: menambah field *wajib* adalah breaking change. Rilis sebagai `/v2/apply` (atau header versi), jaga `/v1/apply` tetap bekerja dengan default masuk akal untuk field baru, umumkan tanggal deprecation, dan hapus `/v1` hanya setelah klien pindah.
- **(c) Idempotency**: klien menghasilkan satu `Idempotency-Key` per aksi lamaran (per tekanan tombol). Server menyimpan `key → result`; retry atau double-click dengan key yang sama mengembalikan hasil pertama dan menghabiskan persis satu kredit. Pengurangan kredit dan record "melamar" terjadi dalam satu transaksi.

**Aturan yang ditunjukkan:** paginasi berdasarkan pola akses, kembangkan di balik versi, dan lindungi aksi kredit/pembayaran dengan idempotency key.
:::

### 📝 Checklist review mandiri

- [ ] Paginasi daftar dipilih berdasarkan pola akses (offset vs cursor) dengan alasan
- [ ] Breaking change ditangani dengan versi dan jalur migrasi
- [ ] Aksi create/kredit dilindungi idempotency key + transaksi
- [ ] Retry dan double-click dipertimbangkan secara eksplisit

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/architecture/f-data-api-design/05-pagination-idempotency" ai="no-ai" title="Pagination dan idempotency key"}
Implementasikan paginasi offset, paginasi cursor (mengembalikan item plus cursor berikutnya), dan "buat pembayaran" idempotent yang menagih sekali meski dipanggil berulang dengan key yang sama. Tes membuktikan paging cursor stabil saat sebuah baris disisipkan, dan bahwa key pembayaran yang diulang mengembalikan hasil pertama tanpa menagih lagi.
:::

:::hints
- `offset_page(items, offset, limit)` → `items[offset:offset+limit]`.
- `cursor_page(items, after_id, limit)`: temukan indeks setelah item yang id-nya == after_id (atau mulai 0 kalau `after_id is None`); kembalikan `(page, next_cursor)` di mana next_cursor adalah id item terakhir atau `None` di akhir.
- `create_payment(store, key, amount)`: kalau key ada di store kembalikan hasil tersimpan; kalau tidak buat `{"id": ..., "amount": amount, "charged": True}`, simpan di key, kembalikan.
:::

## ✅ Cek cepat

:::quiz
Kenapa paginasi cursor tetap cepat di halaman dalam padahal paginasi offset melambat?

Offset membuat database melewati semua baris sebelumnya (mis. menghitung sejuta baris untuk mencapai `offset=1000000`), yang makin lambat sedalam kamu pergi. Cursor memakai lookup ter-index `WHERE id > last`, jadi ia lompat langsung ke halaman berikutnya tanpa peduli kedalaman.
:::

:::quiz
Sebuah request pembayaran diulang setelah respons hilang. Bagaimana idempotency key mencegah tagihan ganda?

Klien mengirim key yang sama pada retry; server melihat key sudah diproses dan mengembalikan hasil pertama yang tersimpan alih-alih menagih lagi, jadi efeknya sama seperti memanggil sekali.
:::

## 📚 Lanjut belajar

- [Stripe: idempotent requests](https://docs.stripe.com/api/idempotent_requests)
- [Slack: pagination (cursor-based)](https://api.slack.com/docs/pagination)
- [Google: API design — versioning](https://cloud.google.com/apis/design/versioning)

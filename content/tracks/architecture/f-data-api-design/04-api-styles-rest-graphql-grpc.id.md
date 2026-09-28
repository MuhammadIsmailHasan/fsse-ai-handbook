---
title: "REST vs GraphQL vs gRPC"
summary: Tiga cara membentuk API — sumber daya sederhana REST, query minta-persis-yang-kamu-butuhkan GraphQL, dan panggilan antar-layanan cepat gRPC — dengan over-fetching ditunjukkan langsung dan aturan jelas untuk memilih.
sourceHash: 77f471531e05
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa itu REST, GraphQL, dan gRPC masing-masing, dalam bahasa sederhana
- **Over-fetching** dan **under-fetching** — masalah yang disasar GraphQL
- Cara query GraphQL meminta field yang persis diinginkan
- Di mana gRPC cocok (panggilan internal antar-layanan yang cepat)
- Aturan sederhana untuk memilih di antara ketiganya

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **API** | Cara yang disepakati satu program meminta data ke program lain |
| **REST** | API yang dibangun di sekitar sumber daya di URL (`/users/1`) |
| **Endpoint** | Satu URL yang melakukan satu tugas |
| **GraphQL** | Satu endpoint di mana klien meminta field yang persis |
| **gRPC** | Cara biner cepat untuk server saling memanggil |
| **Over-fetching** | Mendapat data lebih banyak dari yang dibutuhkan layar |
| **Under-fetching** | Satu panggilan tidak cukup, jadi kamu memanggil beberapa kali |
| **Schema (GraphQL)** | Katalog berjenis tentang apa yang bisa kamu minta |

## 🧠 Ide besarnya

Bayangkan memesan makanan:

- **REST** seperti **warung menu tetap**: tiap hidangan (endpoint) disiapkan satu cara. `/users/1` memberimu seluruh hidangan "user", bahkan bagian yang tak akan kamu makan.
- **GraphQL** seperti **mangkuk racik sendiri**: kamu bilang ke dapur bahan (field) apa persis yang kamu mau, dan kamu dapat persis itu — tak lebih, tak kurang, dalam satu perjalanan.
- **gRPC** seperti **interkom internal dapur**: koki bicara dengan koki, cepat dan ringkas, bukan untuk pelanggan di depan.

## ❓ Kenapa ini penting

Sebagian besar kariermu kamu akan membangun dan memanggil API. Memilih gaya yang salah membuat frontend lambat (terlalu banyak bolak-balik) atau boros (mengunduh field yang tak ditampilkan siapa pun). Memilih yang tepat — biasanya REST, kadang GraphQL, gRPC untuk panggilan internal — menjaga aplikasi cepat dan sederhana. Kamu juga perlu *membaca* ketiganya, karena sistem nyata mencampurnya.

## 📖 Langkah demi langkah

### 1. REST: sumber daya di URL

REST memodelkan datamu sebagai **sumber daya**, masing-masing di URL, memakai verb HTTP (kamu belajar ini di Modul 2):

```
GET    /users/1          → one user
GET    /users/1/orders   → that user's orders
POST   /orders           → create an order
```

Sederhana, bisa di-cache, dan semua orang paham. Ini **default** untuk API web publik.

Kelemahannya: tiap **endpoint** mengembalikan bentuk tetap. Layar yang hanya menampilkan nama dan avatar user tetap mengunduh seluruh objek user — **over-fetching**. Dan menampilkan user *beserta* order-nya mungkin butuh dua panggilan — **under-fetching**.

### 2. GraphQL: minta persis yang kamu butuhkan

GraphQL punya **satu endpoint**. Klien mengirim query yang menggambarkan field persis — termasuk yang bersarang — dan mendapat bentuk itu:

```graphql
query {
  user(id: 1) {
    name
    avatarUrl
    orders(last: 3) {
      total
    }
  }
}
```

Respons mencerminkan query — hanya `name`, `avatarUrl`, dan total 3 order terakhir. Satu perjalanan, tanpa over-fetching, tanpa under-fetching. Ini bersinar saat banyak layar berbeda (web, mobile) butuh potongan berbeda dari data yang sama.

Biayanya: server GraphQL lebih berat dibangun dan diamankan. Satu query bisa meminta data bersarang yang sangat mahal, jadi kamu harus menambah batas (kedalaman, kompleksitas). Caching HTTP sederhana berdasarkan URL tak lagi berlaku, karena semuanya satu endpoint.

### 3. gRPC: panggilan antar-layanan yang cepat

gRPC dibangun untuk **server bicara dengan server** di dalam sistemmu. Ia mengirim pesan **biner** ringkas (didefinisikan di file `.proto`) alih-alih JSON teks, yang lebih cepat dan lebih kecil.

```proto
service Orders {
  rpc GetOrder (OrderRequest) returns (Order);
}
```

Kamu akan memakai gRPC antar microservice-mu sendiri (order service ↔ payment service), biasanya bukan untuk browser atau klien publik. Ia menukar keterbacaan-manusia dan debugging mudah dengan kecepatan dan kontrak ketat.

### 4. Over-fetching, terasa

Bayangkan objek user dengan 15 field, tapi layar daftar hanya menampilkan `name`:

| Gaya | Yang didapat layar |
|---|---|
| REST `/users` | ke-15 field per user (over-fetch) |
| GraphQL `{ users { name } }` | hanya `name` per user |

Pada daftar besar lewat koneksi HP, perbedaan itu adalah byte nyata dan detik nyata. (REST bisa menambah `?fields=name`, tapi kemudian kamu perlahan menciptakan ulang GraphQL.)

### Pilih gaya API-mu

| Situasi | Pilihan bagus |
|---|---|
| API web publik, sumber daya sederhana, ingin caching | **REST** — mulai di sini |
| Banyak klien butuh pemilihan field berbeda; data bersarang kompleks | **GraphQL** |
| Panggilan internal antar-layanan di mana kecepatan penting | **gRPC** |
| Aplikasi kecil dengan satu frontend | **REST** — jangan over-engineer |

- ✅ Default ke REST; ia paling sederhana, bisa di-cache, dan dipahami universal.
- ✅ Pakai GraphQL saat klien yang beragam benar-benar menderita over/under-fetching.
- ✅ Pakai gRPC untuk panggilan internal berthroughput tinggi — bukan API browser publik.
- 🚫 Jangan adopsi GraphQL "karena modern" untuk satu frontend sederhana.

## ⚠️ Kesalahan umum

- Memilih GraphQL untuk satu klien sederhana, lalu memelihara server kompleks tanpa manfaat.
- Mengekspos gRPC langsung ke browser (ia butuh proxy; ia untuk panggilan internal).
- Endpoint REST yang mengembalikan objek raksasa saat layar butuh tiga field.
- GraphQL tanpa batas kedalaman/kompleksitas, membiarkan satu query menghantam database.
- Melupakan caching HTTP gratis REST yang dilepas GraphQL.

:::revoshop
API RevoShop adalah REST (flask-smorest). (1) Temukan endpoint yang mengembalikan objek besar padahal layar hanya menampilkan beberapa field — apakah itu over-fetching? (2) Halaman daftar produk lalu mengambil review tiap produk terpisah — apakah itu under-fetching, dan apakah satu respons gabungan akan membantu? (3) Kalau RevoShop nanti dipecah jadi layanan (catalog, orders, payments), di mana panggilan gRPC antar mereka masuk akal, sementara browser tetap bicara REST ke edge?
:::

## 🏆 Praktik terbaik

- [ ] Default ke REST; adopsi GraphQL atau gRPC hanya untuk masalah yang jelas mereka selesaikan.
- [ ] Rancang endpoint REST di sekitar layar yang memakainya untuk membatasi over/under-fetching.
- [ ] Di GraphQL, terapkan batas kedalaman/kompleksitas dan paginasi field daftar.
- [ ] Simpan gRPC untuk lalu lintas internal antar-layanan; taruh REST atau GraphQL di edge publik.
- [ ] Versikan dan dokumentasikan gaya apa pun yang kamu pilih; jaga kontrak tetap stabil.
- [ ] Ukur ukuran payload dan jumlah bolak-balik sebelum ganti gaya demi "performa".

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan REST vs GraphQL ke orang non-programmer dengan analogi warung-menu-tetap vs mangkuk-racik-sendiri. Lalu katakan, dalam satu kalimat masing-masing, apa itu over-fetching dan under-fetching.

## 📐 Rancang

CareerPilot punya tiga klien untuk data yang sama: dashboard web (menampilkan banyak per lamaran), aplikasi mobile (menampilkan kartu kecil: perusahaan + status), dan job ekspor malam hari (butuh tiap field). Putuskan apakah REST atau GraphQL lebih baik melayani ketiganya, dan kenapa. Lalu katakan di mana gRPC mungkin muncul kalau mesin saran AI CareerPilot menjadi layanan internalnya sendiri.

:::quiz
Tampilkan satu rancangan yang mungkin

**API publik untuk ketiga klien → GraphQL cocok kuat**, karena data yang sama dilihat pada tingkat detail yang sangat berbeda: mobile minta `{ application { company status } }`, web minta banyak field, dan ekspor minta semua — masing-masing dalam satu bolak-balik, tanpa over/under-fetching. REST akan butuh respons gemuk (over-fetch untuk mobile) atau banyak endpoint khusus.

**Kalau aplikasi masih kecil / satu klien utama**, REST dengan beberapa endpoint yang berbentuk baik lebih sederhana dan bisa di-cache — jangan tambah GraphQL dulu.

**gRPC**: antara layanan API utama dan layanan saran AI internal (`GetSuggestions(profile) → suggestions`), di mana kecepatan dan kontrak ketat penting dan tak ada browser terlibat. Browser tetap bicara REST/GraphQL ke edge.

**Aturan yang ditunjukkan:** cocokkan gaya dengan siapa yang memanggil — klien eksternal beragam → GraphQL; antar-layanan internal → gRPC; sumber daya publik sederhana → REST.
:::

### 📝 Checklist review mandiri

- [ ] Pilihan dibenarkan oleh keberagaman klien dan bentuk data, bukan hype
- [ ] Over/under-fetching ditangani untuk tiap klien
- [ ] gRPC ditempatkan hanya pada panggilan internal
- [ ] Trade-off caching dan kompleksitas diakui

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/architecture/f-data-api-design/04-graphql-select" ai="no-ai" title="Pemilih field ala GraphQL kecil"}
Bangun ide inti di balik GraphQL dengan tangan: `graphql_select` yang mengembalikan hanya field yang diminta dari sebuah objek (termasuk yang bersarang), dan `over_fetch_count` yang menunjukkan berapa field ekstra yang dikirim respons ala REST "kembalikan semua" dibanding yang dipilih field-nya. Tes membuktikan pemilih menghindari over-fetching.
:::

:::hints
- Selection adalah dict: `{"name": True, "orders": {"total": True}}` — nilai `True` berarti "sertakan leaf ini", dict berarti "rekursi".
- Untuk field list (seperti `orders`), terapkan selection bersarang ke tiap item.
- `over_fetch_count` = (field di objek penuh) − (field yang benar-benar diminta), dihitung sebagai leaf.
:::

## ✅ Cek cepat

:::quiz
Masalah apa yang terutama diselesaikan GraphQL dibanding REST?

Over-fetching dan under-fetching: klien meminta persis field yang dibutuhkannya (termasuk data bersarang) dalam satu request, alih-alih mengunduh seluruh objek tetap atau membuat beberapa panggilan REST.
:::

:::quiz
Kenapa gRPC biasanya tidak cocok untuk bicara langsung ke browser web?

gRPC memakai pesan biner ringkas yang ditujukan untuk panggilan antar-layanan cepat dan butuh proxy khusus untuk menjangkau browser; ia melepas HTTP/JSON yang terbaca-manusia, mudah di-cache, dan didukung luas yang diharapkan browser dan klien publik.
:::

## 📚 Lanjut belajar

- [MDN: REST & designing web APIs](https://developer.mozilla.org/en-US/docs/Glossary/REST)
- [GraphQL: learn / queries](https://graphql.org/learn/queries/)
- [gRPC: introduction](https://grpc.io/docs/what-is-grpc/introduction/)

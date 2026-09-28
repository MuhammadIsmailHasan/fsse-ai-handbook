---
title: "CAP & Eventual Consistency"
summary: Apa yang terjadi saat bagian sistem tak bisa saling bicara — ide CAP dalam bahasa sederhana, kenapa network split memaksa memilih antara konsistensi dan ketersediaan, dan bagaimana eventual consistency membiarkan replika berbeda sesaat lalu menyatu.
sourceHash: db5e88f8d135
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa itu **network partition** dan kenapa tak terhindarkan pada skala besar
- Ide **CAP**, dijelaskan tanpa teori yang menakutkan
- Kenapa partition memaksa pilihan: **konsistensi** atau **ketersediaan**
- Apa arti **eventual consistency** dan bagaimana replika **menyatu**
- **Last-write-wins** sebagai satu cara sederhana menyelesaikan konflik
- Pilihan mana cocok untuk fitur mana (saldo bank vs hitungan suka)

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Node** | Satu server dalam kelompok yang bekerja bersama |
| **Partition** | Node tak bisa saling bicara untuk sementara |
| **Consistency (CAP)** | Semua membaca nilai terbaru yang sama |
| **Availability** | Tiap request tetap mendapat jawaban |
| **Eventual consistency** | Salinan berbeda sesaat, lalu cocok |
| **Menyatu (converge)** | Replika menetap pada nilai akhir yang sama |
| **Last-write-wins** | Saat bentrok, tulis terbaru menang |

## 🧠 Ide besarnya

Bayangkan dua kasir di **warung** yang biasanya menyinkronkan buku catatannya. Tiba-tiba jalur telepon di antara mereka putus (sebuah **partition**). Seorang pelanggan ingin membayar. Dua pilihan:

- **Tetap konsisten**: "Maaf, saya tak bisa menghubungi kasir satunya untuk memastikan — mohon tunggu." (Menolak mengambil risiko jawaban salah.)
- **Tetap tersedia**: "Baik, saya catat dan kita sinkron nanti." (Menjawab sekarang, rekonsiliasi belakangan.)

Kamu tak bisa punya keduanya selagi jalurnya putus. Trade-off itu adalah keseluruhan **CAP**.

## ❓ Kenapa ini penting

Begitu datamu tinggal di lebih dari satu mesin, jaringan *pasti* kadang gagal — kabel, switch, seluruh data center. Ini tidak langka; pada skala besar ini konstan. CAP memberitahumu kebenaran jujur: **selama** partition kamu harus memilih konsistensi atau ketersediaan. Berpura-pura sebaliknya menghasilkan sistem yang diam-diam menampilkan data salah atau membeku di saat terburuk.

Mengetahui ini membuatmu bisa memilih *per fitur*: saldo bank sebaiknya menolak daripada salah; hitungan suka boleh saja sedikit tertinggal.

## 📖 Langkah demi langkah

### 1. Tiga huruf

CAP tentang tiga properti sistem yang tersebar di banyak **node**:

- **C — Consistency**: tiap baca melihat tulis terbaru (semua node sepakat).
- **A — Availability**: tiap request mendapat respons (non-error).
- **P — Partition tolerance**: sistem terus bekerja bahkan saat node tak bisa bicara.

### 2. Aturan sebenarnya: P bukan opsional

Pada skala besar, partition *terjadi*, jadi **P adalah keharusan** — kamu tak bisa menolak kegagalan jaringan. Artinya pilihan sebenarnya, **selama partition**, adalah antara **C dan A**:

- **CP** (pilih konsistensi): menolak atau memblokir request yang tak bisa dibuat konsisten. Kasir bank yang bilang "mohon tunggu".
- **AP** (pilih ketersediaan): tetap menjawab dan rekonsiliasi nanti. Kasir yang mencatat dan sinkron belakangan.

(Saat *tak ada* partition, sistem yang baik memberimu C dan A sekaligus. CAP tentang momen kegagalan.)

### 3. Eventual consistency: cara AP

Sistem **AP** menerima tulis di node mana pun yang bisa dijangkau, jadi untuk sesaat dua replika bisa menyimpan nilai berbeda. Lalu, begitu mereka bisa bicara lagi, mereka bertukar update sampai **menyatu** pada nilai yang sama. Inilah **eventual consistency**: bukan salah selamanya, hanya *sesaat* usang.

```
Partition:
  Replica A:  likes = 10  (+1 here → 11)
  Replica B:  likes = 10  (+1 there → 11)   ← can't see A
Heal + merge:
  Both →      likes = 12                      ← converge
```

Kamu melihat ini tiap hari: hitungan tayangan YouTube yang berbeda antar refresh, postingan sosial yang muncul untukmu sebelum temanmu melihatnya.

### 4. Menyelesaikan konflik: last-write-wins

Saat dua replika mengubah nilai yang *sama* selama partition, penggabungan harus memilih pemenang. Aturan paling sederhana adalah **last-write-wins (LWW)**: pasang timestamp ke tiap tulis; saat merge, simpan yang timestamp-nya lebih baru.

```python
def merge(a, b):
    # a, b are (value, timestamp); keep the newer write
    return a if a.timestamp >= b.timestamp else b
```

LWW sederhana tapi bisa *kehilangan* salah satu dari dua suntingan bersamaan. Sistem yang lebih kaya memakai merge yang lebih pintar (mis. penghitung yang menjumlah, atau CRDT) — tapi LWW yang harus dipahami dulu.

### Pilih konsistensi vs ketersediaan, per fitur

| Fitur | Pilih | Kenapa |
|---|---|---|
| Saldo bank, stok saat checkout | **CP** (konsistensi) | Jawaban salah lebih buruk daripada yang lambat |
| Hitungan suka, tayangan, feed | **AP** (ketersediaan) | Sedikit tertinggal tak apa; downtime tidak |
| Keunikan username | **CP** | Dua orang tak boleh mengambil nama yang sama |
| Isi keranjang belanja | sering **AP** | Gabungkan item nanti daripada memblokir user |

- ✅ Putuskan C-vs-A per fitur, berdasarkan biaya jawaban salah vs jawaban hilang.
- ✅ Untuk fitur AP, rancang bagaimana replika menyatu dan menyelesaikan konflik.
- 🚫 Jangan anggap "sangat konsisten di mana-mana" itu gratis — ia berbiaya ketersediaan selama partition.

## ⚠️ Kesalahan umum

- Percaya kamu bisa punya C, A, dan P sekaligus selama partition — tidak bisa.
- Memakai penyimpanan eventually-consistent untuk uang atau stok, lalu melihat total yang mustahil.
- Membaca dari replika tepat setelah menulis dan menganggapnya terkini (lihat replication lag).
- Mengabaikan penyelesaian konflik, sehingga merge diam-diam kehilangan perubahan seorang user.
- Menganggap partition langka itu mustahil — pada skala besar itu rutin.

:::revoshop
RevoShop hari ini satu PostgreSQL (sangat konsisten). (1) Bagian mana yang *harus* tetap konsisten meski berarti error — stok saat checkout, status pembayaran? (2) Bagian mana yang bisa menoleransi eventual consistency kalau RevoShop tumbuh — hitungan "produk dilihat", daftar "trending" di beranda? (3) Kalau dua admin mengedit produk yang sama saat gangguan jaringan antar replika, apa yang dilakukan last-write-wins, dan bisakah itu diam-diam kehilangan sebuah suntingan?
:::

## 🏆 Praktik terbaik

- [ ] Perlakukan partition tolerance sebagai wajib; putuskan C-vs-A per fitur untuk kasus partition.
- [ ] Simpan uang, stok, dan keunikan di jalur yang sangat konsisten (CP).
- [ ] Untuk fitur AP, definisikan konvergensi dan aturan penyelesaian konflik sejak awal.
- [ ] Utamakan aturan merge yang tak kehilangan data (penghitung, himpunan) daripada last-write-wins polos saat suntingan penting.
- [ ] Atur ekspektasi user untuk data eventual ("hitungan mungkin butuh sesaat untuk update").
- [ ] Uji perilaku *selama* partition tersimulasi, bukan hanya saat semuanya sehat.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan CAP dengan analogi dua-kasir-dan-jalur-telepon-putus. Lalu, dalam satu kalimat, katakan apa arti eventual consistency dan beri satu contoh sehari-hari (seperti hitungan tayangan).

## 📐 Rancang

Aplikasi sosial global menampilkan: (1) saldo akun untuk "payout kreator" berbayar, (2) hitungan suka postingan, dan (3) @handle unik. Untuk masing-masing, putuskan CP atau AP selama partition dan benarkan. Lalu, untuk hitungan suka, jelaskan bagaimana dua data center yang keduanya menerima suka selama partition akan menyatu tanpa kehilangan suka.

:::quiz
Tampilkan satu rancangan yang mungkin

- **(1) Saldo kreator → CP.** Uang harus benar; selama partition, blokir atau error daripada berisiko saldo salah atau payout ganda. Lambat boleh; salah tidak.
- **(2) Hitungan suka → AP.** Ketersediaan lebih penting daripada tepat untuk sedetik. Tiap data center menerima suka selama partition dan mereka rekonsiliasi sesudahnya.
- **(3) @handle unik → CP.** Keunikan butuh kesepakatan; dua center tak boleh sama-sama memberikan `@ismail`. Registrasi memblokir selama partition daripada berisiko duplikat.

**Menyatukan hitungan suka tanpa kehilangan:** jangan pakai last-write-wins pada *angka*-nya (itu akan membuang suka satu center). Sebaliknya perlakukan suka sebagai **penambahan** dan jumlahkan: tiap center mencatat "+N" selama partition, dan saat sembuh total-total dijumlahkan (counter CRDT). Jadi 10 → (+1 di sini, +1 di sana) → 12, bukan 11.

**Aturan yang ditunjukkan:** pilih C-vs-A per fitur, dan untuk penghitung AP pakai merge aditif, bukan last-write-wins, supaya tak ada penambahan yang hilang.
:::

### 📝 Checklist review mandiri

- [ ] Tiap fitur punya pilihan CP-atau-AP yang dibenarkan untuk kasus partition
- [ ] Uang/keunikan disimpan di jalur konsisten
- [ ] Konvergensi dijelaskan untuk fitur AP
- [ ] Aturan merge dipilih supaya data tak diam-diam hilang

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/architecture/h-distributed-systems/01-eventual-consistency" ai="no-ai" title="Berbeda saat partition, lalu menyatu"}
Modelkan dua replika penyimpan key-value yang menerima tulis secara independen selama partition, lalu merge. Implementasikan last-write-wins untuk nilai tunggal dan merge aditif untuk penghitung. Tes menunjukkan LWW menyatukan kedua replika ke state yang sama (tapi bisa membuang suntingan bersamaan), sementara merge penghitung menyatu tanpa kehilangan penambahan apa pun.
:::

:::hints
- Representasikan nilai sebagai `(value, timestamp)`; `apply` hanya menimpa kalau timestamp baru lebih baru.
- `merge_lww(a, b)`: untuk tiap key, simpan entri dengan timestamp lebih besar (pemecah seri deterministik, mis. nilai lebih besar).
- `merge_counter(a, b)`: untuk tiap key, hitungan yang menyatu adalah jumlah penambahan kedua sisi — jangan hanya satu sisi.
:::

## ✅ Cek cepat

:::quiz
Selama partition jaringan, dua properti CAP mana yang harus kamu pilih, dan kenapa tak bisa ketiganya?

Kamu memilih antara **Consistency** dan **Availability**, karena partition tolerance (P) tak terhindarkan begitu data ada di banyak mesin — jaringan *pasti* terputus. Selagi terputus, kamu bisa menolak menjawab agar tetap konsisten, atau menjawab dan rekonsiliasi nanti agar tetap tersedia, tapi tidak keduanya.
:::

:::quiz
Kenapa last-write-wins pilihan buruk untuk menggabungkan hitungan suka, dan apa yang lebih baik?

LWW hanya menyimpan angka satu sisi dan membuang yang lain, kehilangan suka yang terjadi di replika lain. Memperlakukan suka sebagai penambahan dan **menjumlahkannya** (merge aditif/penghitung) menyatu tanpa kehilangan apa pun.
:::

## 📚 Lanjut belajar

- [Martin Kleppmann, *DDIA*, Ch. 9 (consistency & consensus)](https://dataintensive.net/)
- [The CAP theorem, explained simply](https://www.ibm.com/think/topics/cap-theorem)
- [A brief introduction to CRDTs](https://crdt.tech/)

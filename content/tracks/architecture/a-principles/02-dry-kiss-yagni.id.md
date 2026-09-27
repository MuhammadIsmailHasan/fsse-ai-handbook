---
title: "DRY, KISS, YAGNI: Tiga Aturan Menghindari Usaha Sia-sia"
summary: Hindari duplikasi pengetahuan, kompleksitas yang tidak perlu dan fitur yang tidak diminta siapa pun — dan pelajari kapan setiap aturan salah.
sourceHash: a278a9c67e1d
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- **DRY** — Don't Repeat Yourself (pengetahuan, bukan hanya baris kode)
- **KISS** — Keep It Simple (buat sesederhana mungkin)
- **YAGNI** — You Aren't Gonna Need It (jangan bangun yang belum perlu)
- **Rule of Three** — kapan menghapus duplikasi
- Mengapa menerapkan aturan-aturan ini sembarangan menimbulkan masalah baru

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **DRY** | Jangan ulangi pengetahuan yang sama di beberapa tempat |
| **KISS** | Buat sesederhana mungkin: yang paling jelas yang berfungsi |
| **YAGNI** | Jangan bangun yang belum diminta siapa pun |
| **Rule of Three** | Tunggu sampai ada tiga kali sebelum mengekstrak duplikasi |
| **Accidental duplication** | Kode yang mirip tapi punya makna berbeda |
| **Premature abstraction** | Membuat helper bersama terlalu cepat dan menyesal kemudian |
| **Over-engineering** | Membangun untuk kebutuhan masa depan yang belum nyata |

## 🧠 Ide besarnya

Ketiga aturan itu melindungi hal yang sama: **waktu kamu di masa depan**.

| Aturan | Siapa yang dirugikan |
|---|---|
| **DRY** | Memperbaiki bug yang sama di 5 tempat (dan melewatkan satu) |
| **KISS** | Menghabiskan sehari memahami sesuatu yang bisa jadi 10 baris jelas |
| **YAGNI** | Membangun, menguji dan merawat fitur yang tidak pernah dipakai siapa pun |

## ❓ Kenapa ini penting

Software terus berubah. Setiap aturan duplikasi, trik pintar dan fitur "kita mungkin butuh" membuat perubahan **berikutnya** lebih lambat dan berisiko. Ketiga nama singkat ini adalah pelajaran yang dipelajari industri dengan cara yang keras.

| Aturan | Siapa yang dirugikan |
|---|---|
| **DRY** | Memperbaiki bug yang sama di lima tempat — dan melewatkan satu |
| **KISS** | Menghabiskan sehari memahami apa yang bisa jadi sepuluh baris jelas |
| **YAGNI** | Membangun, menguji dan merawat fitur yang tidak pernah dipakai siapa pun |

Tapi setiap aturan punya cara salahnya: DRY diterapkan pada kode yang hanya *mirip* membuat fungsi bersama dengan lima flag; KISS digunakan sebagai alasan melewatkan struktur yang perlu; YAGNI ke ekstrem mengabaikan perubahan yang sudah kamu tahu akan datang.

## 📖 Langkah demi langkah

### 1. DRY tentang **pengetahuan**, bukan teks

```python
TAX_RATE_PERCENT = 11                      # one source of truth

def add_tax(amount: int) -> int:
    return amount * (100 + TAX_RATE_PERCENT) // 100
```

Setiap tempat yang butuh pajak memanggil `add_tax`. Ubah aturannya sekali.

Tapi dua kode yang **mirip** bisa mewakili **pengetahuan** berbeda:

```python
def max_username_length() -> int:
    return 30

def max_cart_items() -> int:
    return 30
```

Ini bukan duplikasi — mereka akan berubah karena alasan berbeda. Menggabungnya jadi `MAX_THINGS = 30` akan mengikat aturan yang tidak berhubungan. **Tanya: "Kalau satu berubah, apakah yang lain harus berubah juga?"** Hanya kalau itu duplikasi sungguhan.

### 2. Rule of Three

Dua kode serupa mungkin kebetulan; tiga adalah pola. Menunggu yang ketiga menyelamatkanmu dari menggabungkan dua hal yang tidak pernah benar-benar sama.

- **Kali pertama**: cukup tulis saja.
- **Kali kedua**: perhatikan duplikasinya, terimalah.
- **Kali ketiga**: ekstrak potongan bersama — sekarang kamu tahu apa yang benar-benar berbeda.

Mengekstrak terlalu cepat sering menghasilkan **abstraksi yang salah**: fungsi dengan 7 flag yang mencoba melayani kasus yang ternyata berbeda.

:::tip
Duplikasi lebih murah daripada abstraksi yang salah. Mudah menggabungkan kode serupa nanti; menyakitkan melepas fungsi bersama yang buruk dipakai di 20 tempat.
:::

### 3. KISS: hal paling sederhana yang berfungsi

Pilih, berdasarkan urutan:

1. Fitur bahasa bawaan dan standar library
2. Beberapa fungsi jelas
3. Class, kalau ada state dan behavior sungguhan untuk dikelompokkan
4. Pattern atau framework, kalau masalah nyata sekarang membutuhkannya

```python
# ❌ Clever
is_weekend = bool((date.weekday() + 2) // 7)

# ✅ Simple
is_weekend = date.weekday() >= 5   # Saturday=5, Sunday=6
```

Sederhana ≠ mudah ditulis. Sederhana = **mudah dipahami dan diubah**. Sering kali membutuhkan pikiran lebih banyak.

### 4. YAGNI: bangun untuk kebutuhan hari ini

Saat tergoda menambah sesuatu "karena mungkin kita butuhnya":

- Apakah ada user atau ticket yang minta **sekarang**?
- Berapa biaya menambahnya **nanti**, saat dibutuhkan? (Biasanya: tidak lebih banyak.)
- Berapa biaya membawanya **sampai** saat itu? (Kode untuk dibaca, diuji, diaman, dimigrasikan.)

YAGNI **tidak** berarti "tulis kode yang tidak bisa diperluas". Kode bersih, bernama jelas, diuji mudah diperluas nanti. Artinya: jangan bangun perluasannya **sebelum** dibutuhkan.

### Memilih setup-mu

Setiap pilihan di sini adalah trade-off:

| Prinsip | Terlalu jauh | Keseimbangan |
|---|---|---|
| DRY | Semuanya bagian dari satu mega-fungsi; aturan yang tidak berhubungan jadi terikat | Ekstrak **pengetahuan** duplikasi; Rule of Three |
| KISS | "Sederhana" trick yang mengabaikan kebutuhan nyata (tidak ada error handling) | Solusi paling sederhana yang memenuhi kebutuhan **nyata** |
| YAGNI | Mengabaikan kebutuhan terdekat yang sudah tahu; melukis diri sendiri ke sudut | Jangan bangunnya — tapi jangan halangi juga |

Security, integritas data dan backup **bukan** YAGNI. "Kita tambah authentication nanti" adalah cara breach terjadi.

- ✅ DRY untuk business rule, konstanta, validasi, formatting.
- ✅ KISS secara default, terutama saat belajar dan prototype.
- ✅ YAGNI untuk fitur, opsi konfigurasi dan "fleksibilitas".
- 🚫 Jangan DRY kode tes sampai setiap tes jadi sulit dibaca — beberapa pengulangan di tes itu sehat.
- 🚫 Jangan pakai YAGNI sebagai alasan melewatkan validasi, tes atau security.


## ⚠️ Kesalahan umum

- Menggabungkan kode yang hanya mirip.
- Menambah boolean flag ke fungsi bersama untuk setiap kasus baru (`def send(email, is_invoice, is_reminder, skip_footer, …)`).
- Membangun "framework" untuk proyek pertamamu.
- Optimasi prematur sebagai bentuk kompleksitas.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan YAGNI dengan analogi kehidupan nyata (packing untuk perjalanan, membangun rumah, membeli peralatan dapur). Lalu jelaskan kenapa duplikasi **pengetahuan** lebih buruk daripada duplikasi **baris**.

## 📐 Rancang

Untuk setiap situasi, putuskan: terapkan DRY, KISS, YAGNI, atau **biarkan saja**. Benarkan dalam satu kalimat.

1. Regex validasi format email muncul di endpoint sign-up, edit profil dan admin user-create.
2. Seorang rekan mengusulkan abstract `NotificationChannel` class hierarchy dengan Email, SMS, WhatsApp dan Push. Produk saat ini hanya kirim email.
3. Dua fungsi tes masing-masing membangun dict `user` serupa dengan 5 field.
4. Kamu menulis list comprehension 3-baris; rekan menyarankan ganti dengan custom `Pipeline().filter().map().collect()` class.
5. `MAX_UPLOAD_MB = 10` dan `MAX_ATTACHMENTS = 10` — seseorang ingin satu konstanta.

:::quiz
Lihat kemungkinan jawaban

1. **DRY** — pengetahuan sama (apa yang email valid) di tiga tempat; ekstrak `is_valid_email`.
2. **YAGNI** — satu channel hari ini; fungsi `send_email` sederhana cukup. Tambah struktur saat channel kedua benar-benar dibutuhkan.
3. **Biarkan (sebagian besar)** — pengulangan kecil membuat tes mudah dibaca; tiny helper/fixture baik kalau berkembang.
4. **KISS** — comprehension jelas dan standar; custom class tambah kompleksitas tanpa manfaat.
5. **Biarkan saja** — angka sama, pengetahuan berbeda; mereka akan berubah karena alasan berbeda.
:::

### 📝 Checklist review mandiri

- [ ] Aku tanya "apakah ini wakili pengetahuan yang sama?" untuk keputusan DRY
- [ ] Aku pisahkan "mungkin butuh" dari "butuh sekarang"
- [ ] Aku perhatikan bahwa beberapa duplikasi bisa diterima

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/architecture/a-principles/02-dry-kiss-yagni" ai="no-ai" title="Hapus pengetahuan duplikasi"}
`notifications.py` membangun tiga macam reminder message CareerPilot. Setiap fungsi copy-paste greeting, date formatting, dan signature yang sama — dengan ketidaksesuaian kecil (satu bahkan bug yang test ungkap).

Refactor sehingga:
- greeting, date formatting dan signature masing-masing hidup di **exactly one** helper
- tiga public function tetap nama dan signature-nya
- semua tes pass, termasuk yang mengungkap ketidaksesuaian
:::

:::hints
- Jalankan tes dulu — satu fail karena satu copy format tanggal berbeda dari yang lain.
- Ekstrak `format_date(d)`, `greeting(name)`, `signature()`; lalu bangun lagi setiap message dari mereka.
- Tahan godaan menambah generic `build_message(kind, **options)` dengan flag — tiga fungsi kecil lebih sederhana (KISS).
:::

## ✅ Cek cepat

:::quiz
Dua fungsi punya body yang sama. Apakah kamu harus selalu menggabungkannya?

Tidak — hanya kalau mereka wakili pengetahuan yang sama dan harus berubah bersama. Kode yang sama dengan alasan berbeda untuk berubah harus tetap terpisah.
:::

:::quiz
Apa itu Rule of Three?

Terima duplikasi dua kali pertama; ekstrak abstraksi bersama di ketiga kalinya, saat kamu lihat apa yang benar-benar berbeda.
:::


## 📚 Lanjut belajar

- [Martin Fowler: Yagni](https://martinfowler.com/bliki/Yagni.html)
- [Sandi Metz: The Wrong Abstraction](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction)

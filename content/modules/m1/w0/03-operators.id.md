---
title: "Operator: Aritmatika, Perbandingan, dan Logika"
summary: Hitung, bandingkan, dan gabungkan kondisi — termasuk operator yang sering disalahpahami pemula (//, %, and, or).
sourceHash: 8485aac8f009
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Operator aritmatika, termasuk `//` (bagi lalu bulatkan) dan `%` (sisa bagi)
- Operator perbandingan dan kenapa selalu menghasilkan `True` atau `False`
- Logika dengan `and`, `or`, `not` — dan **short-circuiting**
- **Precedence** operator dan kapan harus pakai tanda kurung

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Operator** | Simbol yang melakukan aksi pada nilai (`+`, `==`) |
| **Aritmatika** | Perhitungan: `+ - * /` |
| **`//` floor division** | Bagi lalu bulatkan ke bawah |
| **`%` modulo** | Sisa setelah dibagi |
| **Perbandingan** | Pertanyaan ya/tidak (`>`, `==`) |
| **`=` vs `==`** | Memberi nilai / membandingkan |
| **Logika (`and`, `or`, `not`)** | Menggabungkan kondisi ya/tidak |
| **Short-circuit** | Python berhenti lebih awal saat jawaban sudah jelas |
| **Precedence** | Urutan operator dijalankan |

## 🧠 Ide besarnya

Operator itu seperti mesin kecil: nilai masuk, nilai baru keluar.

- **Mesin aritmatika** menghasilkan angka: `3 + 4` → `7`
- **Mesin perbandingan** menghasilkan ya/tidak: `3 > 4` → `False`
- **Mesin logika** menggabungkan ya/tidak: `True and False` → `False`

Setiap "keputusan" di software — *boleh user checkout? password cukup panjang?* — dibangun dari tiga mesin ini.

## ❓ Kenapa penting

Aturan bisnis itu matematika dan logika berpakaian:

- "gratis ongkir di atas Rp 200.000" → perbandingan,
- "admin **atau** pemilik boleh edit" → logika,
- "tampilkan 20 item per halaman" → bagi dan sisa,
- "password panjang **dan** punya angka?" → keduanya.

Salah di sini tidak terlihat tapi mahal: `=` daripada `==`, atau `and` di tempat `or`, membuat kode jalan baik-baik saja tapi jawabnya salah.

## 📖 Langkah demi langkah

### 1. Aritmatika

| Operator | Artinya | Contoh | Hasil |
|---|---|---|---|
| `+` `-` `*` | tambah, kurang, kali | `7 * 3` | `21` |
| `/` | bagi (selalu desimal) | `7 / 2` | `3.5` |
| `//` | bagi bulat — hanya bagian utuh | `7 // 2` | `3` |
| `%` | sisa bagi (modulo) | `7 % 2` | `1` |
| `**` | pangkat | `2 ** 10` | `1024` |

`//` dan `%` adalah pasangan — mereka tanya "berapa **kelompok utuh**, berapa **sisa**?"

```python
items = 23
per_box = 5
full_boxes = items // per_box    # 4
left_over = items % per_box      # 3
```

Pakai `%` untuk: genap/ganjil (`n % 2 == 0`), "setiap baris ke-3" (`i % 3 == 0`), berputar-putar (`(index + 1) % len(items)`).

Jalan pintas: `total += price` berarti `total = total + price`. Juga `-=`, `*=`, `//=`.

### 2. Perbandingan

| Operator | Artinya |
|---|---|
| `==` | sama |
| `!=` | tidak sama |
| `<` `<=` `>` `>=` | lebih kecil / lebih besar (atau sama) |
| `in` | ada di dalam (string, list, …) |

```python
print(5 == 5.0)                 # True
print("Jakarta" == "jakarta")   # False — text comparison is case-sensitive
print("@" in "ana@mail.com")    # True
print(18 <= 20 < 65)            # True — Python lets you chain comparisons
```

### 3. Logika

| Operator | True kalau… |
|---|---|
| `a and b` | **kedua**nya true |
| `a or b` | **paling tidak satu** true |
| `not a` | `a` false |

Tabel kebenaran:

| a | b | `a and b` | `a or b` |
|---|---|---|---|
| True | True | True | True |
| True | False | False | True |
| False | True | False | True |
| False | False | False | False |

### 4. Short-circuiting

Inilah mengapa `if user and user.is_active:` aman: kalau `user` adalah `None`, Python tidak pernah lihat `.is_active`. Cek pintu sebelum membuka.

Python berhenti evaluasi segera jawaban sudah jelas:

- `False and apa saja` → `False` (kanan tidak pernah jalan)
- `True or apa saja` → `True` (kanan tidak pernah jalan)

Berguna untuk hindari error:

```python
# If items is empty, len(items) > 0 is False and items[0] is never touched.
if len(items) > 0 and items[0] == "urgent":
    ...
```

### 5. Precedence: siapa duluan

Kalau ragu, tambah kurung. Tidak ada yang pernah mengeluh kondisi terlalu mudah dibaca.

Dari tinggi ke rendah (sederhana):

1. `**`
2. `*` `/` `//` `%`
3. `+` `-`
4. perbandingan `<` `==` `in` …
5. `not`
6. `and`
7. `or`

```python
print(2 + 3 * 4)          # 14, not 20
print(True or False and False)   # True — `and` binds tighter than `or`
```

:::tip[Aturan keterbacaan]
Kalau **kamu** harus pikir tentang precedence, tambah kurung. Teman tim masa depan akan berterima kasih.
`(age < 18) or (is_student and age < 25)`
:::

### Pilihan yang perlu dibuat

Setiap pilihan di sini punya untung-rugi:

| Pilihan | ✅ | ❌ |
|---|---|---|
| Satu ekspresi boolean panjang | Ringkas | Susah dibaca dan debug |
| Variabel perantara bernama (`is_adult = age >= 18`) | Jelasin sendiri, mudah print | Beberapa baris lagi |
| Andalkan short-circuit hindari error | Ringkas | Urutan kondisi jadi penting — ubah urutan bisa crash |
| `/` lalu `int()` vs `//` | — | `int(-7 / 2)` adalah `-3` tapi `-7 // 2` adalah `-4`: beda untuk negatif |

- ✅ Pakai `//` dan `%` untuk kelompokan, halaman (`page_count = (total + per_page - 1) // per_page`), dan siklus.
- ✅ Beri nama ke kondisi kompleks.
- 🚫 Jangan bandingkan boolean ke `True`: tulis `if is_member:` bukan `if is_member == True:`.
- 🚫 Jangan bandingkan desimal dengan `==` setelah hitung (`0.1 + 0.2 == 0.3` adalah `False`). Pakai `math.isclose()`.


## ⚠️ Kesalahan umum

- `=` (beri nilai) daripada `==` (bandingkan).
- `if x == 1 or 2:` — selalu true! Artinya `(x == 1) or 2`. Tulis `if x in (1, 2):`.
- Harap `/` menghasilkan `int`.
- Campur `and`/`or` tanpa kurung.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan `//` dan `%` pakai contoh nyata yang tidak ada hubungan programming (telur di kardus, siswa di grup…). Lalu jelaskan short-circuiting seolah-olah ke teman.

## 📐 Rancang

Tulis **satu ekspresi boolean mudah dibaca** (kamu boleh pakai variabel bernama) untuk aturan ini dari platform kursus online:

> User boleh tonton pelajaran kalau sudah **beli kursus**, **atau** pelajaran itu **free preview**. Admin bisa tonton semua. User yang di-ban tidak boleh tonton apa saja — bahkan free preview, bahkan kalau admin.

:::quiz
Lihat rancangan yang mungkin

```python
is_allowed_normally = has_purchased or is_free_preview or is_admin
can_watch = is_allowed_normally and not is_banned
```

Beri nama langkah tengah membuat aturan "ban mengalahkan semuanya" jelas sekali.
:::

### 📝 Checklist review mandiri

- [ ] Analogi ku untuk `//` dan `%` beri angka yang sama seperti Python
- [ ] Ekspresi ku beri `False` untuk admin yang di-ban
- [ ] Ku pakai kurung atau variabel bernama daripada andalkan precedence

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

## 🧸 Kalkulator checkout

:::exercise{path="exercises/m1/w0/03-operators" ai="no-ai" title="Aturan checkout"}
Di `checkout.py`, terapkan aturan toko online kecil:

- `split_bill(total, people)` → `(each, remainder)` dalam rupiah utuh
- `page_count(total_items, per_page)` → berapa halaman satu daftar butuhkan
- `is_even(n)` → `True`/`False`
- `gets_free_shipping(cart_total, is_member, is_oversized)` → member dengan keranjang **≥ Rp 500.000** dapat gratis ongkir, tapi **tidak pernah** barang besar
:::

:::hints
- `split_bill` langsung pakai `//` dan `%`.
- Untuk halaman, pikir: 10 item, 3 per halaman → 4 halaman. Coba `(total_items + per_page - 1) // per_page`. Kenapa itu jalan?
- Angka genap tidak ada sisa kalau dibagi 2.
- Bangun `gets_free_shipping` dari tiga fakta digabung dengan `and` dan `not`.
:::

### 🏆 Tujuan peregangan

Tambah `shipping_fee(weight_kg)`: Rp 10.000 per kg pertama (atau sebagiannya), plus Rp 5.000 untuk **setiap** kg tambahan yang dimulai. `0.5` → `10000`, `1` → `10000`, `1.2` → `15000`, `3` → `20000`.

## ✅ Cek cepat

:::quiz
`-7 // 2` dan `-7 % 2` menghasilkan apa?

`-4` dan `1`. Floor division bulatkan **ke bawah** (ke arah negatif tak terhingga), dan sisanya punya tanda pembagi sehingga `(-4 * 2) + 1 == -7`.
:::

:::quiz
Kenapa `if role == "admin" or "owner":` adalah bug?

Dibaca sebagai `(role == "admin") or "owner"`. String tidak kosong `"owner"` adalah truthy, jadi kondisi **selalu** true. Pakai `role in ("admin", "owner")`.
:::

:::quiz
Bagaimana urutan kondisi di `and` cegah crash?

Dengan short-circuiting, kanan jalan hanya kalau kiri true — contoh `user is not None and user.is_active` tidak pernah sentuh `user.is_active` saat `user` adalah `None`.
:::


## 📚 Lanjut belajar

- [Dokumentasi Python: Operator precedence](https://docs.python.org/3/reference/expressions.html#operator-precedence)
- [Dokumentasi Python: Boolean operations](https://docs.python.org/3/reference/expressions.html#boolean-operations)

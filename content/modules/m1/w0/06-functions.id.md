---
title: "Function: Membuat Blok Kode yang Bisa Dipakai Berulang"
summary: Bungkus logika ke dalam function bernama — parameter, return value, scope, dan bedanya pure function dengan side effect.
sourceHash: 6f72b595b8bb
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Membuat function dengan **parameter**, **nilai bawaan**, dan **return value**
- Bedanya `return` dan `print`
- **Scope**: variabel mana yang bisa dilihat function
- **Pure function** vs function dengan **side effect**, dan kenapa penting untuk testing
- Docstring dan type hint

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Function** | Blok kode bernama yang bisa dijalankan berkali-kali |
| **Parameter / argument** | Nama di definisi / nilai yang dikirim |
| **`return`** | Mengembalikan nilai ke yang memanggilnya |
| **`print`** | Tampilkan sesuatu ke layar (beda dari return) |
| **Default value** | Nilai yang dipakai kalau tidak dikirim |
| **Scope** | Variabel mana yang bisa dilihat di bagian kode itu |
| **Pure function** | Input sama → output sama, tidak ubah apa pun di luar |
| **Side effect** | Apa yang diubahnya di luar dirinya (file, database, layar) |
| **Docstring** | Teks singkat yang jelasin apa fungsi itu |

## 🧠 Ide besarnya

:term[Function]{bahasa="function — blok kode bernama yang menerima input dan menghasilkan output"} itu seperti **kartu resep**. Ada nama ("Nasi Goreng"), bahan yang dikasih (parameter), langkah-langkahnya, dan makanan yang keluar (return value). Kalau sudah ditulis, siapa pun bisa membuatnya lagi tinggal pakai namanya — tanpa baca ulang semua langkahnya.

```python
def format_rupiah(amount: int) -> str:
    return f"Rp {amount:,}".replace(",", ".")

print(format_rupiah(1500000))   # Rp 1.500.000
```

## ❓ Kenapa ini penting

Tanpa function, logika yang sama ditempel di lima tempat — dan diperbaiki di empat tempat. Dengan function, kamu nama satu perilaku, test sekali, dan pakai di mana pun.

Bayar kartu resep: nama ada di kartu, bahan masuk, dan makanan keluar. Orang bisa membuatnya tanpa baca semua langkah lagi.

Kesalahan paling umum pemula adalah mix-up `print` sama `return`. `print` tampilkan ke manusia; `return` kembalikan nilai ke program. Function yang cuma print tidak bisa dipakai lagi, ditest, atau digabung.

## 📖 Langkah demi langkah

### 1. Buat dan panggil

```python
def greet(name):            # define: parameter `name`
    return f"Hello, {name}!"

message = greet("Ana")      # call: argument "Ana"
print(message)
```

- `def` buat function. Tubuhnya indentasi.
- :term[Parameter]{bahasa="parameter — nama input di definisi function"} itu nama di definisi; **argument** itu nilai yang dikirim.
- Tidak ada yang jalan sampai kamu **panggil** function-nya.

### 2. `return` vs `print`

```python
def add_print(a, b):
    print(a + b)       # shows it on screen, gives back None

def add_return(a, b):
    return a + b       # gives the value back to the caller

result = add_print(2, 3)    # prints 5
print(result)               # None 😬

result = add_return(2, 3)
print(result * 10)          # 50 ✅ — we can keep using the value
```

`print` bicara ke **manusia**. `return` bicara ke **program kamu**. Function yang hitung sesuatu hampir selalu harus `return`.

`return` juga **hentikan** function langsung — itulah cara guard clause bekerja.

### 3. Nilai bawaan dan keyword argument

```python
def apply_discount(price: int, percent: int = 10) -> int:
    return price * (100 - percent) // 100

apply_discount(200_000)               # 180000   (uses default 10)
apply_discount(200_000, 25)           # 150000
apply_discount(price=200_000, percent=25)   # keyword arguments: clearer
```

:::danger[Jangan pernah pakai mutable default]
`def add_item(item, cart=[]):` — list itu **dibagi antar panggilan** dan terus bertambah. Pakai `cart=None` dan buat list di dalam: `if cart is None: cart = []`.
:::

### 4. Return beberapa nilai

```python
def min_max(values: list[int]) -> tuple[int, int]:
    return min(values), max(values)

low, high = min_max([4, 9, 1])   # "unpacking"
```

### 5. Scope: apa yang bisa dilihat function

Function itu dapur dengan meja hitam sendiri: apa yang kamu taruh di sana hilang waktu kamu keluar, dan itulah kenapa function aman untuk dipakai ulang.

```python
tax_rate = 11            # global variable

def with_tax(price):
    total = price * (100 + tax_rate) // 100   # can READ the global
    return total

print(with_tax(100))     # 111
print(total)             # ❌ NameError — `total` only exists inside the function
```

Variabel yang dibuat dalam function itu **lokal**: muncul waktu function jalan dan hilang waktu return. Itu fitur — function tidak bisa kebetulan rusak variabel milik function lain.

Andalkan global membuat function sulit ditest dan dipakai ulang. Lebih baik kirim nilai sebagai parameter: `def with_tax(price, tax_rate=11)`.

### 6. Pure function vs side effect

Pure function paling mudah ditest: tidak ada database, tidak ada setup, cuma input dan output yang diharap. Jaga logika itu pure, dan dorong bagian berantakan (file, network, print) ke pinggir.

| Pure function | Function dengan side effect |
|---|---|
| Output tergantung **cuma** dari input | Baca/ubah dunia di luar |
| Input sama → output sama, selalu | Hasil bisa beda (waktu, file, database, network) |
| `cart_total(items)` | `save_order(order)`, `send_email(...)`, `print(...)`, `datetime.now()` |
| Trivial untuk ditest | Butuh setup, fake, atau database sungguhan |

Desain yang bagus: jaga **keputusan** di pure function, dan dorong side effect ke pinggir.

```python
def build_welcome_email(name: str) -> str:     # pure: easy to test
    return f"Hi {name}, welcome to CareerPilot!"

def send_welcome(user):                        # side effect: thin wrapper
    email_service.send(user.email, build_welcome_email(user.name))
```

### 7. Docstring dan type hint

```python
def page_count(total_items: int, per_page: int = 20) -> int:
    """Return how many pages are needed to show all items.

    >>> page_count(45, 20)
    3
    """
    return (total_items + per_page - 1) // per_page
```

Type hint (`: int`, `-> int`) dan docstring bilang ke pembaca — dan editor — gimana pakai function tanpa baca tubuhnya.

### Pilih setup kamu

Semua pilihan di sini adalah trade-off:

| Pilihan | ✅ | ❌ |
|---|---|---|
| Banyak function kecil | Mudah dibaca, ditest, dipakai ulang | Lompat-lompat antar function waktu baca |
| Satu function besar | Semua di satu tempat | Sulit ditest dan diubah dengan aman |
| Pure function | Bisa diprediksi, test mudah | Sesuatu tetap perlu buat side effect |
| Global | Cepat ditulis | Ketergantungan tersembunyi, bug mengejutkan |
| Default parameter | API praktis | Terlalu banyak opsi bingung |

- ✅ Ambil function dari kode kalau kamu copy kedua kali, atau kalau blok itu layak dapat nama.
- ✅ Targetkan function yang **satu pekerjaan** (kalau nama butuh "dan", pikir split).
- 🚫 Jangan buat function untuk satu baris jelas yang pakai sekali (`def add_one(x): return x + 1`).
- 🚫 Jangan sembunyikan side effect di function yang namanya terlihat pure (`get_total()` yang juga save ke database).


## ⚠️ Kesalahan umum

- Pakai `print` bukannya `return`, terus dapat `None`.
- Lupa **panggil** function (`total = cart_total` bukannya `cart_total(items)`).
- Mutable default argument.
- Function yang diam-diam ubah list input (kejutan!). Kembalikan list baru, atau nama jelas (`sort_in_place`).
- Parameter terlalu banyak (lebih dari ~4 isarat untuk kelompok).

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan bedanya `return` dan `print` ke orang yang cuma pernah pakai kalkulator. Terus jelaskan dalam dua kalimat kenapa pure function lebih mudah ditest.

## 📐 Rancang

Rekan kamu tulis satu function 60 baris `process_order(order)` yang: validasi order, hitung subtotal, terapkan voucher, tambah ongkir, save ke database, email customer.

Split jadi function kecil. Untuk tiap-tiap, tulis **nama**, **parameter**, **tipe return**, dan tandai **pure** atau **side effect**.

:::quiz
Tunjukkan satu kemungkinan desain

| Function | Kembalikan | Tipe |
|---|---|---|
| `validate_order(order) -> list[str]` | list pesan error (kosong = valid) | pure |
| `subtotal(items) -> int` | rupiah | pure |
| `apply_voucher(amount, voucher) -> int` | rupiah setelah diskon | pure |
| `shipping_fee(weight_kg, express) -> int` | rupiah | pure |
| `order_total(order) -> int` | gabung ketiga di atas | pure |
| `save_order(order, total) -> int` | order id baru | side effect |
| `send_confirmation(email, order_id, total) -> None` | — | side effect |
| `process_order(order)` | koordinasi semua, pendek | side effect |

Lima dari delapan pure → banyak logika bisa ditest tanpa database atau email server.
:::

### 📝 Self-review checklist

- [ ] Tiap function satu pekerjaan dan namanya bilang apa
- [ ] Perhitungan pure; database/email work terpisah
- [ ] Tidak ada function dengan lebih dari ~4 parameter
- [ ] Aku bisa tulis test untuk tiap pure function tanpa setup

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

## 🧸 Rancang ulang ke function

:::exercise{path="exercises/m1/w0/06-functions" ai="no-ai" title="Dari copy-paste jadi function"}
`pricing.py` punya satu script berantakan dengan logika duplikat. Bangun ulang jadi function:

- `format_rupiah(amount)` → `"Rp 1.500.000"`
- `apply_discount(price, percent=10)` → harga rupiah utuh setelah diskon (bulatkan **ke bawah**)
- `line_total(price, qty)` → harga × jumlah
- `cart_total(items)` → jumlah `line_total` untuk setiap item (`items` itu list tuple `(price, qty)`)
- `receipt(items, discount_percent=0)` → string multi-baris (format di README)

`receipt` harus **pakai ulang** function lain — test cek output, reviewer (kamu!) cek penggunaan ulang.
:::

:::hints
- `f"{1500000:,}"` beri `"1,500,000"`. Ganti koma dengan titik.
- Bulatkan ke bawah dengan integer: `price * (100 - percent) // 100`.
- Loop tuple dengan unpacking: `for price, qty in items:`.
- Bangun `receipt` sebagai list baris, terus `"\n".join(lines)`.
:::

### 🏆 Tantangan lebih

Buat `apply_discount` raise `ValueError` untuk persen di bawah 0 atau di atas 100, dan tambah docstring dengan contoh untuk setiap function.

## ✅ Cek cepat

:::quiz
Function kembalikan apa kalau tidak ada `return` statement?

`None`.
:::

:::quiz
Kenapa `def add_tag(tag, tags=[])` berbahaya?

Default list dibuat **sekali** dan dibagi antar panggilan, jadi tag dari panggilan terdahulu bocor ke yang baru. Pakai `tags=None` dan buat list baru di dalam.
:::

:::quiz
Apakah `def total_with_tax(price): return price * (100 + TAX) // 100` pure kalau `TAX` global constant yang tidak pernah berubah?

Praktis iya — input sama selalu dapat output sama. Jadi impure (dan lebih sulit ditest) kalau `TAX` bisa berubah saat runtime. Kirim sebagai parameter buat ketergantungan jelas.
:::


## 📚 Lanjut belajar

- [Python tutorial: Defining functions](https://docs.python.org/3/tutorial/controlflow.html#defining-functions)
- [Python tutorial: More on defining functions](https://docs.python.org/3/tutorial/controlflow.html#more-on-defining-functions)

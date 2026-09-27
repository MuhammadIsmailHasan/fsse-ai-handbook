---
title: "Wadah Data: Variabel & Tipe Data"
summary: Bagaimana program mengingat sesuatu — variabel, tipe data inti Python, dan mengubah tipe dengan aman.
sourceHash: 27b249e4bcbc
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa itu **variable** (variabel) yang sebenarnya di Python
- Tipe inti: `int`, `float`, `str`, `bool`, `None` (dan pandangan pertama `list` dan `dict`)
- Cara **cek** tipe data dan **ubah** antar tipe
- Kenapa data dari form dan file selalu datang sebagai **teks**

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Variabel** | Nama yang menunjuk ke sebuah nilai |
| **Nilai** | Data yang sebenarnya (`450000`, `"Sari"`) |
| **Tipe data** | Jenis nilai apa, dan apa yang boleh kamu lakukan dengannya |
| **`int` / `float`** | Bilangan bulat / bilangan dengan desimal |
| **`str`** | Teks |
| **`bool`** | Benar atau salah |
| **`None`** | "Belum ada nilai" |
| **Type conversion** | Mengubah satu tipe jadi tipe lain (`int("12")`) |
| **Truthy / falsy** | Nilai yang Python anggap benar atau salah dalam kondisi ya/tidak |

## 🧠 Ide besarnya

Bayangkan variabel seperti **label di sebuah kotak**. Kamu tulis nama di labelnya, masukin nilai ke kotak, dan nanti kapan perlu nilai itu, kamu tinggal lihat labelnya.

```python
price = 450000
```

Python membuat nilai `450000` di memori dan nempel label `price` di situ. Nanti, `price` memberikan nilai itu kembali.

:term[Tipe data]{bahasa="tipe data — jenis nilai (angka, teks, benar/salah) yang menentukan apa yang boleh dilakukan"} bercerita **jenis nilai apa** itu — dan karena itu, apa yang boleh kamu lakukan. Kamu bisa bagi bilangan. Kamu bisa buat teks huruf besar. Tapi kamu nggak bisa buat bilangan huruf besar.

## ❓ Kenapa ini penting

Setiap program menyimpan hal-hal: harga, nama, apakah pengguna sudah login. Tipe memutuskan apa yang bisa kamu lakukan dengan masing-masing — kamu bisa bagi bilangan, bisa buat teks besar, tapi nggak bisa buat bilangan besar.

Paling penting di tepi. Data dari form, file, atau API selalu datang sebagai **teks**:

```python
age = input("Your age: ")   # "25" — a string, not a number
age + 1                      # 💥 TypeError
```

Satu fakta ini jelaskan banyak kesalahan pemula, dan itu kenapa biasakan diri mengubah tipe dengan hati-hati mulai sekarang.

## 📖 Langkah demi langkah

### 1. Membuat dan mengubah variabel

```python
name = "Ismail"      # create
age = 29
age = age + 1        # change: read the old value, compute, re-attach the tag
print(name, age)     # Ismail 30
```

`=` artinya **assign** ("nempel label ini ke nilai itu"), bukan "sama dengan". Sama dengan itu `==` (pelajaran berikutnya).

Aturan dan kebiasaan penamaan:

| ✅ Bagus | ❌ Hindari | Kenapa |
|---|---|---|
| `total_price` | `tp`, `x` | Pembaca nggak boleh tebak-tebakan |
| `is_logged_in` | `logged` | Prefiks `is_`/`has_` buat boolean jelas |
| `user_count` | `userCount` | Gaya Python itu `snake_case` |
| `MAX_RETRIES = 3` | `max_retries` untuk konstanta | UPPER_CASE bilang "jangan ganti aku" |

### 2. Tipe-tipe inti

| Tipe | Contoh | Pakai untuk |
|---|---|---|
| `int` | `42`, `-7`, `1_000_000` | Bilangan bulat: jumlah, id, jumlah rupiah |
| `float` | `3.14`, `0.5` | Bilangan dengan desimal: rating, ukuran |
| `str` | `"hello"`, `'Jakarta'` | Teks |
| `bool` | `True`, `False` | Ya/tidak |
| `None` | `None` | "Belum ada nilai (buat nanti)" |
| `list` | `["a", "b"]` | Koleksi berurutan (Pelajaran 05) |
| `dict` | `{"name": "Ana", "age": 20}` | Field bernama, seperti objek JSON (Minggu 1) |

```python
print(type(42))        # <class 'int'>
print(type("42"))      # <class 'str'>
print(type(None))      # <class 'NoneType'>
```

### 3. String: tipe paling sering kamu pakai

```python
city = "  jakarta  "
print(city.strip())            # "jakarta"      remove spaces at both ends
print(city.strip().title())    # "Jakarta"
print(len("hello"))            # 5
print("Rp" + " " + "15000")    # "Rp 15000"     joining = concatenation

name = "Ana"
age = 20
print(f"{name} is {age} years old")   # f-string: the cleanest way to build text
```

:::tip[f-string]
Tulis `f` sebelum tanda kutip dan variabel di dalam `{}`. Kamu bahkan bisa format bilangan: `f"{1234567:,}"` → `"1,234,567"`.
:::

### 4. Ubah antar tipe

Ubah di **tepi** — tepat saat data masuk — terus percaya tipe di mana-mana. Ubah berulang kali dalam kode adalah cara bug sembunyi.

| Dari → Ke | Kode | Hasil |
|---|---|---|
| teks → int | `int("42")` | `42` |
| teks → float | `float("3.5")` | `3.5` |
| bilangan → teks | `str(42)` | `"42"` |
| apa saja → bool | `bool("")`, `bool("hi")`, `bool(0)` | `False`, `True`, `False` |

Konversi bisa **gagal**:

```python
int("12abc")    # ValueError: invalid literal for int()
int("3.5")      # ValueError — int() won't parse a decimal string
int(3.9)        # 3  — converting a float drops the decimals (no rounding!)
```

Bersihkan teks dulu kalau dari pengguna:

```python
raw = " 25 "
age = int(raw.strip())   # 25
```

### 5. "Truthy" dan "falsy"

Python anggap ini sebagai `False` dalam situasi ya/tidak: `False`, `None`, `0`, `0.0`, `""`, `[]`, `{}`. Yang lain hitung sebagai `True`. Itu kenapa `bool("false")` itu `True` — itu string nggak kosong!

### 6. Kejutan float

`0.1 + 0.2` nggak persis `0.3` karena komputer simpen desimal pakai biner, sama seperti 1/3 nggak bisa ditulis persis di desimal. Itu kenapa uang pakai `Decimal`, bukan pernah `float`.

```python
print(0.1 + 0.2)   # 0.30000000000000004
```

Komputer simpen float pakai biner dan beberapa desimal nggak bisa diwakilkan persis. Untuk **uang**, pakai bilangan bulat unit terkecil (rupiah, atau sen) sebagai `int`, atau Python punya `Decimal`.

### 7. Dynamic typing (dan pandangan pertama type hint)

Python biarkan variabel tunjuk tipe apa saja, dan ubah nanti:

```python
value = 10
value = "ten"   # allowed in Python
```

Kamu bisa **jelaskan** tipe yang kamu maksud pakai **type hint**. Python nggak paksa di saat jalankan, tapi editor dan tools pakai untuk tangkap kesalahan lebih awal:

```python
age: int = 29
name: str = "Ismail"
```

Kamu pakai type hint di mana-mana nanti — FastAPI (Modul 3) bahkan pakai untuk validasi input API.

### Pilih setup mu

Setiap pilihan di sini adalah trade-off:

| Pilihan | ✅ Untung | ❌ Rugi |
|---|---|---|
| **Dynamic typing** (Python) | Cepat tulis dan coba | Kesalahan tipe keluar saat kode jalan |
| **Static typing** (TypeScript, Java) | Banyak kesalahan ketangkap sebelum jalan | Lebih banyak tulis; lambat untuk coba |
| Python **+ type hint** | Tengah-tengah: fleksibel, tapi tools bisa cek | Harus jaga hint tetap akurat |
| Uang sebagai `float` | Gampang | Kesalahan pembulatan |
| Uang sebagai `int` (unit terkecil) | Persis | Ingat format untuk tampilan |

- ✅ Ubah **di batas**: detik data masuk (form, file, API), ubah ke tipe yang tepat sekali saja.
- ✅ Pakai `None` untuk "nggak tahu / belum set" bukan nilai pura-pura seperti `-1` atau `""`.
- 🚫 Jangan pakai `float` untuk uang.
- 🚫 Jangan pakai ulang satu variabel buat tipe beda (`result = 5` terus `result = "error"`). Ini bingungkan pembaca dan tools.


## ⚠️ Kesalahan umum

- Lupa `input()` beri `str` → `"3" * 2 == "33"`.
- `bool("False")` → `True` (string nggak kosong). Bandingkan teks: `text.lower() == "true"`.
- `int("3.5")` gagal; pakai `float("3.5")` dulu kalau desimal mungkin.
- Pakai `=` padahal maksud `==`.
- Nama variabel `list`, `str`, atau `type` — ini sembunyikan built-in Python yang sama.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke orang yang bukan programmer kenapa form daftar minta **umur** memberikan program teks `"29"` bukan bilangan `29`, dan apa yang bisa salah kalau program lupa ubah. Maksimal 5 kalimat.

## 📐 Rancang

Kamu simpen **lowongan kerja** untuk CareerPilot. Untuk setiap field, pilih tipe dan tulis satu contoh nilai:

`title`, `company`, `salary_min`, `salary_max`, `is_remote`, `posted_date`, `application_deadline` (beberapa lowongan nggak punya), `rating` (contohnya 4.3)

:::quiz
Tunjukkan desain yang mungkin

| Field | Tipe | Contoh | Kenapa |
|---|---|---|---|
| `title` | `str` | `"Junior Backend Engineer"` | teks |
| `company` | `str` | `"Nusantara Tech"` | teks |
| `salary_min` | `int` | `9000000` | uang jadi rupiah bulat |
| `salary_max` | `int` | `14000000` | sama |
| `is_remote` | `bool` | `True` | ya/tidak |
| `posted_date` | `str` (ISO) buat sekarang | `"2026-09-01"` | nanti: `datetime.date` |
| `application_deadline` | `str` **atau `None`** | `None` | hilang itu status nyata |
| `rating` | `float` | `4.3` | desimal, bukan uang |
:::

### 📝 Daftar review sendiri

- [ ] Field uang adalah `int`, bukan `float`
- [ ] Field ya/tidak adalah `bool`, bukan string `"yes"`/`"no"`
- [ ] Field "mungkin hilang" izinkan `None`
- [ ] Penjelasanku sebutkan *kapan* konversi seharusnya terjadi

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

## 🧸 Bersihkan data form

:::exercise{path="exercises/m1/w0/02-data-types" ai="no-ai" title="Ubah input form mentah"}
Form daftar kirim semuanya jadi teks. Di `form_data.py`, lengkapi tiga fungsi:

- `parse_age(text)` → `int`, abaikan spasi di sekeliling bilangan
- `parse_height_m(text)` → `float` tinggi dalam meter dari teks sentimeter (`"172"` → `1.72`)
- `parse_newsletter(text)` → `True` hanya untuk `"yes"`, `"y"` atau `"true"` (huruf besar atau kecil, spasi boleh)

Terus `describe_user(name, age)` beri tepat `"Ana (20 years old)"` pakai f-string.

Kamu belum belajar fungsi — gpp. Tulis kode kamu di tempat yang bilang `# YOUR CODE HERE` dan akhiri dengan `return`.
:::

:::hints
- `"  25 ".strip()` buang spasi, terus `int(...)` ubah.
- 172 cm itu 1.72 m — bagi 100.
- Seragamkan dulu: `text.strip().lower()`, terus bandingkan dengan `==` atau `in ("yes", "y", "true")`.
- F-string lihat seperti `f"{name} ({age} years old)"`.
:::

### 🏆 Tantangan stretch

Tambah `parse_price_idr(text)` yang ubah `"Rp 15.000"` atau `"15000"` jadi `int` `15000`. (Petunjuk: `.replace()`.)

## ✅ Cek cepat

:::quiz
`int(7.99)` beri apa, dan kenapa itu masalah di toko?

`7` — `int()` potong desimal, nggak dibulatkan. Hitung uang bisa kaga nilai diam-diam; pakai `round()` dengan sengaja atau simpen uang jadi integer.
:::

:::quiz
Kenapa `bool("0")` sama dengan `True`?

Karena `"0"` itu **string nggak kosong**. Hanya string kosong yang falsy. Ubah teks jadi bilangan dulu kalau maksud angka nol.
:::

:::quiz
Tempat terbaik ubah input pengguna jadi tipe yang tepat di mana?

Di **batas** — sedetik data masuk program (form handler, file reader, API endpoint), ubah jadi tipe yang tepat sekali saja.
:::


## 📚 Lanjut belajar

- [Python tutorial: An Informal Introduction](https://docs.python.org/3/tutorial/introduction.html)
- [Python docs: Built-in Types](https://docs.python.org/3/library/stdtypes.html)

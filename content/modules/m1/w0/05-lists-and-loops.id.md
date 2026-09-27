---
title: "List dan Loop: Mengulang Pekerjaan"
summary: Simpan banyak nilai dalam list dan proses dengan for dan while loop — pola accumulator yang kamu pakai setiap hari.
sourceHash: 3de6e752c601
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Buat, baca, ubah, dan potong **list**
- Loop dengan `for`, `range()`, `enumerate()`, dan `while`
- Pola **accumulator** (total, hitung, cari maksimal, kumpulkan)
- `break`, `continue`, dan cara hindari loop tanpa akhir

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **List** | Kumpulan nilai berurutan di bawah satu nama |
| **Index** | Nomor posisi item, dimulai dari 0 |
| **Slice** | Potongan dari list (`items[1:4]`) |
| **Loop** | Mengulang pekerjaan yang sama untuk tiap item |
| **`for` loop** | Jalan melewati setiap item satu per satu |
| **`while` loop** | Ulangi selama syarat masih benar |
| **`range()`** | Deret angka untuk diloop |
| **Accumulator** | Variabel yang menampung hasil (total, hitung, list) |
| **`break` / `continue`** | Hentikan loop / lewati ke item berikutnya |
| **Loop tanpa akhir** | `while` yang syaratnya tidak pernah jadi salah |

## 🧠 Ide besarnya

List itu seperti **kereta**: satu nama, banyak gerbong berurutan, tiap gerbong punya nomor mulai dari **0**.

Loop itu seperti **ban berjalan di pabrik**: ia bawa gerbong ke depanmu satu per satu supaya kamu bisa lakukan pekerjaan yang sama di tiap gerbong.

Aplikasi nyata itu kebanyakan list dan loop: list produk → tampilkan tiap satu; list pesanan → jumlahkan total; list pesan → cari yang belum dibaca.

## ❓ Kenapa ini penting

Data datang dalam kelompok: 30 siswa, 1000 transaksi, 50 lowongan kerja. Kamu tidak bisa buat seribu variabel (`harga1`, `harga2`, …), dan tidak bisa paste baris yang sama seribu kali — apalagi kalau kamu tidak tahu **berapa banyak** sampai program jalan.

List menampung kelompok; loop mengerjakan satu hal untuk tiap anggota. Hampir setiap layar yang akan kamu bangun nanti seperti ini: list produk → tampilkan tiap satu; list pesanan → jumlahkan totalnya; list pesan → cari yang belum dibaca.

## 📖 Langkah demi langkah

### 1. List

```python
fruits = ["apple", "banana", "cherry"]

print(fruits[0])      # "apple"   — first item is index 0
print(fruits[-1])     # "cherry"  — negative index counts from the end
print(len(fruits))    # 3

fruits.append("durian")        # add to the end
fruits.insert(1, "avocado")    # insert at position 1
fruits.remove("banana")        # remove first matching value
last = fruits.pop()            # remove and return the last item
fruits[0] = "apricot"          # replace

print("cherry" in fruits)      # True
```

**Slice** memberi kamu potongan (list baru): `list[mulai:selesai]`, di mana `selesai` **tidak** dimasukkan.

```python
numbers = [10, 20, 30, 40, 50]
print(numbers[1:3])   # [20, 30]
print(numbers[:2])    # [10, 20]    first two
print(numbers[-2:])   # [40, 50]    last two
print(numbers[::-1])  # [50, 40, 30, 20, 10]  reversed copy
```

### 2. Loop `for`

```python
for fruit in fruits:
    print(fruit.upper())
```

Baca begini: "untuk **tiap** fruit di fruits, jalankan blok yang indentasi". Variabel `fruit` pegang item sekarang.

Butuh nomor posisi juga? Pakai `enumerate`:

```python
for index, fruit in enumerate(fruits, start=1):
    print(f"{index}. {fruit}")
```

Butuh ulangi berkali-kali? Pakai `range`:

```python
for i in range(3):        # 0, 1, 2
    print("Hello", i)

for i in range(2, 10, 2): # 2, 4, 6, 8   (start, stop, step)
    print(i)
```

### 3. Pola accumulator

Ini bentuk di balik kebanyakan "laporan": mulai dengan keranjang kosong, jalan list, masukkan barang. Total, hitung, terbesar, atau list baru yang disaring — pola sama, keranjang beda.

Hampir setiap loop kerjakan salah satu dari empat hal ini. Pelajari bentuknya:

```python
prices = [45_000, 120_000, 30_000, 99_000]

# 1. TOTAL: start at 0, add each
total = 0
for price in prices:
    total += price

# 2. COUNT: start at 0, add 1 when something matches
expensive = 0
for price in prices:
    if price > 50_000:
        expensive += 1

# 3. BEST SO FAR: start with the first item, replace when you find better
highest = prices[0]
for price in prices:
    if price > highest:
        highest = price

# 4. COLLECT: start with an empty list, append matches
cheap = []
for price in prices:
    if price < 50_000:
        cheap.append(price)
```

:::tip
Python punya fungsi bawaan untuk kasus umum: `sum(prices)`, `max(prices)`, `min(prices)`, `len(prices)`. Tulis loop sendiri **dulu** supaya kamu mengerti apa yang mereka kerjakan — baru pakai bawaan di kode sungguhan.
:::

### 4. Loop `while`

`while` ulangi **selama** syarat benar. Pakai saat tidak tahu terlebih dahulu berapa kali:

```python
balance = 1_000_000
months = 0
while balance > 0:
    balance -= 150_000
    months += 1
print(months)   # 7
```

:::danger[Loop tanpa akhir]
Kalau syarat tidak pernah jadi salah, loop tidak berhenti. Selalu pastikan ada yang **di dalam** loop bergerak menuju berhenti. Macet? Tekan `Ctrl + C` di terminal.
:::

### 5. `break` dan `continue`

```python
for order in orders:
    if order == "CANCELLED":
        continue          # skip this one, go to the next item
    if order == "STOP":
        break             # leave the loop completely
    process(order)
```

### 6. Jangan ubah list saat loop di atasnya

Hapus gerbong saat jalan di kereta bikin kamu loncati beberapa. Buat list baru, atau loop copy-nya.

```python
numbers = [1, 2, 2, 3]
for n in numbers:
    if n == 2:
        numbers.remove(n)   # 🐛 skips items because positions shift
print(numbers)              # [1, 2, 3]  — one 2 survived!
```

Build a **new** list instead: `numbers = [n for n in numbers if n != 2]` (that's a *list comprehension* — you'll use them a lot in Week 1).

### Pilih setup kamu

Setiap pilihan punya trade-off:

| Pilihan | ✅ | ❌ |
|---|---|---|
| `for item in items` | Jelas, tidak bisa out of range | Tidak ada index (pakai `enumerate`) |
| `for i in range(len(items))` | Punya index | Ribut, mudah off-by-one salah |
| `while` | Fleksibel stop | Risiko loop tanpa akhir |
| Bawaan (`sum`, `max`) | Singkat dan cepat | Sembunyikan logika saat belajar |
| Ubah di tempat | Hemat memori | Bug mengejutkan saat loop |

- ✅ `for` saat jalan koleksi atau jumlah langkah sudah tahu.
- ✅ `while` untuk "sampai hal terjadi": coba ulang, baca sampai akhir, game loop.
- 🚫 Jangan list kalau perlu cari hal berdasarkan nama — itu `dict` (Minggu 1).
- 🚫 Jangan loop berlapis di list besar tanpa pikir: 10.000 × 10.000 = 100 juta langkah (kamu pelajar *Big-O* di track DSA).


## ⚠️ Kesalahan umum

- **Off-by-one**: `range(1, 10)` berhenti di 9. Index terakhir adalah `len(items) - 1`.
- `max([])` crash di list kosong — cek dulu kalau kosong.
- Lupa update variabel di `while` loop.
- Reset accumulator **di dalam** loop (`total = 0` di badan loop).
- Hapus item dari list saat loop di atasnya.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan pola accumulator memakai contoh nyata — misalnya kasir tambah-tambah keranjang, atau guru hitung siswa yang lulus. Peta tiap langkah (nilai mulai, apa per item, hasil akhir) ke bentuk kode.

## 📐 Rancang

Sebelum kode, tulis **pseudocode** (langkah dalam bahasa biasa) untuk masalah ini:

> Diberi list langkah harian sebulan, laporkan: total langkah, berapa hari kamu capai **10.000 atau lebih**, **streak** terpanjang hari berturut-turut 10.000+, dan list nomor hari (mulai 1) saat kamu jalan di bawah 3.000 langkah.

:::quiz
Lihat pseudocode mungkin

```text
total = 0, goal_days = 0, current_streak = 0, best_streak = 0, lazy_days = []
untuk tiap (day_number mulai 1, steps) di list:
    total += steps
    kalau steps >= 10000:
        goal_days += 1
        current_streak += 1
        best_streak = max(best_streak, current_streak)
    kalau tidak:
        current_streak = 0
    kalau steps < 3000:
        tambah day_number ke lazy_days
```

Lihat: **satu loop** tangani keempat jawab. Streak perlu dua variabel — run sekarang dan run terbaik sejauh ini.
:::

### 📝 Checklist review mandiri

- [ ] Aku identifikasi bentuk accumulator apa untuk tiap jawab
- [ ] Streak-ku reset saat goal terlewat
- [ ] Nomor hari mulai 1, bukan 0
- [ ] Aku pikir bulan kosong (tidak ada data)

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

## 🧸 Keranjang dan step tracker

:::exercise{path="exercises/m1/w0/05-lists-and-loops" ai="no-ai" title="Loop it"}
Di `loops.py`, buat **tanpa** `sum`, `max`, `min` atau list comprehension (tulis loop sendiri kali ini):

- `cart_total(prices)` → total semua harga
- `count_expensive(prices, limit)` → berapa harga **lebih besar dari** `limit`
- `highest_price(prices)` → harga terbesar, atau `None` kalau list kosong
- `first_over(prices, limit)` → harga pertama di atas `limit`, atau `None` (berhenti loop setelah ketemu!)
- `longest_streak(steps, goal)` → run terpanjang hari berturut-turut dengan `steps >= goal`
:::

:::hints
- `highest_price`: lindungi dulu dari list kosong, baru pakai bentuk "terbaik sejauh ini".
- `first_over`: kamu bisa `return` langsung dari dalam loop — itu juga berhentikan loopnya.
- `longest_streak`: pegang `current` dan `best`. Saat hari tidak capai goal, `current = 0`.
:::

### 🏆 Tantangan ekstra

Tambah `chunk(items, size)` yang potong list jadi potongan: `chunk([1,2,3,4,5], 2)` → `[[1,2],[3,4],[5]]`. Pakai `range` dengan langkah dan slice.

## ✅ Cek cepat

:::quiz
`list(range(5, 0, -2))` hasilkan apa?

`[5, 3, 1]` — mulai 5, berhenti **sebelum** 0, langkah −2.
:::

:::quiz
Kenapa hapus item dari list di dalam `for` loop atas list yang sama itu bug?

Hapus geser posisi item belakang, jadi loop loncati item tepat setelah yang dihapus. Buat list baru sebagai ganti.
:::

:::quiz
Kapan pilih `while` daripada `for`?

Saat tidak tahu berapa repetisi terlebih dahulu — kamu ulangi sampai syarat berubah (coba ulang, baca input sampai "quit", bayar saldo).
:::


## 📚 Lanjut belajar

- [Tutorial Python: List](https://docs.python.org/3/tutorial/introduction.html#lists)
- [Tutorial Python: for statement dan range()](https://docs.python.org/3/tutorial/controlflow.html#for-statements)

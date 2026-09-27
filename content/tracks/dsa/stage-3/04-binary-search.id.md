---
title: "Pencarian Biner"
summary: Belah dua ruang pencarian setiap langkah — pencarian tepat, posisi pertama/terakhir, larik yang diputar, dan teknik "pencarian biner pada jawaban" yang ampuh.
sourceHash: 4fb97af82282
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Kenapa membelah dua memberikan **O(log n)** — 1 miliar item dalam ~30 langkah
- Template yang bisa diandalkan dengan **interval invariant** yang jelas (tidak perlu panik dengan off-by-one)
- Lower bound / upper bound (posisi pertama `>= x`, posisi pertama `> x`)
- Mencari data yang "hampir terurut" (larik yang diputar)
- **Pencarian biner pada jawaban** untuk masalah optimasi
- 🧭 Cara mengenali masalah pencarian biner — termasuk yang tanpa larik

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Pencarian biner** | Membelah dua rentang jawaban yang mungkin setiap langkah |
| **O(log n)** | Satu miliar item dalam sekitar 30 langkah |
| **Interval invariant** | Janji tentang rentang yang masih bisa punya jawaban |
| **Lower bound** | Posisi pertama dengan nilai ≥ x |
| **Upper bound** | Posisi pertama dengan nilai > x |
| **Predicate** | Pertanyaan ya/tidak yang sekali berubah dari tidak ke ya |
| **Larik yang diputar** | Larik terurut yang dipotong dan ditukar di satu tempat |
| **Cari pada jawaban** | Menebak jawaban dan tanya "apakah ini cukup?" |

## 🧠 Ide besarnya

Tebak angka antara 1 dan 1.000. Setiap kali menebak, kamu dengar "lebih tinggi" atau "lebih rendah". Menebak 500 duluan **menghilangkan setengah** pilihan, apa pun jawabannya; lalu 250 atau 750; dan seterusnya. Kamu selalu menang dalam 10 tebakan, karena 2¹⁰ = 1.024.

Pencarian biner bekerja kapan pun pertanyaan punya struktur **"lebih tinggi / lebih rendah"** itu.

## ❓ Kenapa ini penting

| n | Scan linear | Pencarian biner |
|---|---|---|
| 1.000 | 1.000 | 10 |
| 1.000.000 | 1.000.000 | 20 |
| 1.000.000.000 | 1.000.000.000 | 30 |

Itu saja argumennya. Kapan pun pertanyaan punya jawaban "lebih tinggi atau lebih rendah?" — larik terurut, database index, "berapa ukuran server paling kecil yang masih bisa tangani beban?" — kamu bisa buang setengah kemungkinan setiap langkah.

Tangkapannya: kebanyakan orang menulis dari ingatan, salah sedikit di batasan, dan loop selamanya. Makanya pelajaran ini настаing pada satu template dengan janji yang jelas tentang rentang yang tersisa.

## 📖 Langkah demi langkah

### 1. Pencarian tepat (closed interval)

```python
def find_index(nums, target):
    low, high = 0, len(nums) - 1          # search space: [low, high] inclusive
    while low <= high:                     # non-empty
        mid = (low + high) // 2
        if nums[mid] == target:
            return mid
        if nums[mid] < target:
            low = mid + 1                  # target is right of mid
        else:
            high = mid - 1                 # target is left of mid
    return -1
```

**Invariant**: kalau target ada, ia ada di `[low, high]`. Setiap cabang jaga janji itu dan kecilkan interval.

### 2. Lower bound: posisi pertama dengan nilai `>= x` (half-open interval)

```python
def first_at_least(nums, x):
    low, high = 0, len(nums)               # answer is in [low, high] — high = len means "none"
    while low < high:
        mid = (low + high) // 2
        if nums[mid] < x:
            low = mid + 1                  # mid is too small → answer is after it
        else:
            high = mid                     # mid might be the answer → keep it
    return low
```

Template ini jawab seluruh keluarga: pertama `>= x`, posisi sisip, hitung item `< x` (= indexnya), pertama `> x` (pakai `<=`), terakhir `< x` (jawaban − 1). Python `bisect_left` / `bisect_right` implement persis ini.

### 3. Berpikir dalam istilah predicate

Jangan pikir "cari nilainya" dan mulai pikir "di mana jawaban berubah dari tidak ke ya?". Hampir setiap varian jadi masalah yang sama.

Tulis ulang setiap pencarian biner sebagai: *cari posisi pertama di mana `condition(i)` jadi True*, diberi urutan yang mirip ini:

```text
False False False False True True True
                        ^ jawaban
```

Kalau kamu bisa buktikan kondisinya **monotonic** (sekali True, tetap True), pencarian biner bekerja — bahkan tanpa larik sama sekali.

### 4. Larik terurut yang diputar

`[13, 15, 18, 2, 5, 9, 11]`: di setiap `mid`, **satu setengah terurut**. Kalau `nums[low] <= nums[mid]`, setengah kiri terurut: cek apakah target ada dalam `nums[low]..nums[mid]`; kalau ya, ke kiri, kalau tidak, ke kanan. Atau setengah kanan terurut — cermin logikanya.

### 5. Pencarian biner pada jawaban

Di sini tidak ada larik — kamu menebak jawaban (kecepatan, kapasitas, batas waktu) dan tanya checker "apakah ini cukup?". Tebakan-tebakannya tetap belah dua.

*"Berapa kapasitas harian paling kecil untuk selesaikan semua review dalam D hari?"*

- Jawaban calon: dari `max(sizes)` (harus muat aplikasi terbesar) sampai `sum(sizes)` (satu hari).
- Predicate: `can_finish(capacity)` — simulasi greedy O(n).
- Monotonic: kalau kapasitas c bekerja, c + 1 juga bekerja.

```python
low, high = max(sizes), sum(sizes)
while low < high:
    mid = (low + high) // 2
    if can_finish(mid):
        high = mid        # works → maybe smaller works too
    else:
        low = mid + 1     # doesn't work → need more
return low
```

Total: O(n · log(sum)). Bentuk sama: pisah tugas ke k sprint meminimalkan yang terberat, kecepatan paling kecil untuk sampai tepat waktu, ambang batas paling kecil yang muat budget, akar kuadrat bilangan bulat terbesar.

:::tip[🧭 Cara mengenali pencarian biner]
- Data **terurut** (atau terurut setelah rotasi) dan kamu butuh posisi, kemunculan pertama/terakhir, atau posisi sisip.
- Masalah minta **nilai minimum/maksimum yang penuhi kondisi**, dan pengecekan kelayakan `works(x)` **monotonic**.
- Batasan besar (nilai sampai 10⁹, n sampai 10⁵) dan solusi O(n log n) atau O(n log V) diharapkan.
- Kamu tertangkap coba jawaban satu per satu: "coba 1, coba 2, coba 3…".
:::

### Pilih setup-mu

Setiap pilihan di sini ada trade-off:

| Cara | Waktu | Butuh |
|---|---|---|
| Scan linear | O(n) | tidak ada |
| Pencarian biner | O(log n) | data terurut / predicate monotonic |
| Pencarian hash | O(1) rata-rata | cocok persis saja — tidak "pertama ≥ x", tidak rentang |
| Cari biner pada jawaban | O(check × log rentang) | pengecekan kelayakan monotonic |
| B-tree index (database) | O(log n) disk-friendly | pemeliharaan database |

- ✅ Larik terurut, rentang, "pertama/terakhir", optimasi dengan pengecekan monotonic.
- ✅ Debug: `git bisect` cari commit yang mulai ada bug.
- 🚫 Data tidak terurut yang harus diurut untuk **satu** pencarian (O(n log n) > O(n)).
- 🚫 Pencarian cocok-tepat berulang kali pada data berubah → gunakan set/dict.

## ⚠️ Kesalahan umum

- `while low < high` dengan template closed (lewatkan kandidat terakhir) atau `<=` dengan template half-open (error index).
- `high = mid - 1` saat `mid` bisa jadi jawaban.
- Lupa logika larik yang diputar butuh nilai **berbeda** (duplikat rusak test "setengah mana yang terurut").
- Pakai pencarian biner pada jawaban tanpa pengecekan monotonic.

## 🏆 Praktik terbaik

- [ ] Pilih **satu** template dan interval-invariant-nya (closed `[low, high]` atau half-open `[low, high)`) dan pakai konsisten.
- [ ] Tulis invariant sebagai komentar; periksa setiap cabang jaga dan kecilkan interval.
- [ ] Uji input kecil: kosong, satu elemen, dua elemen, target lebih kecil/besar dari semua.
- [ ] Saat loop pakai `low = mid`, hitung `mid` dengan pembulatan **ke atas** (`(low + high + 1) // 2`) untuk hindari infinite loop.
- [ ] Untuk "cari pada jawaban", tulis predikat, buktikan monotonicity, dan pilih batas ketat.
- [ ] Di Python production, pakai `bisect` — implement tangan di wawancara dan untuk mengerti.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan `git bisect` ke teman kerja yang tidak pernah pakai: "bug muncul di suatu tempat dalam 500 commit terakhir" — berapa test run yang perlu dan kenapa?

## 📐 Rancang

Setelah materi 03 Minggu 6, kamu mau cari **berapa pengguna bersamaan paling banyak** yang bisa ditangani API CareerPilot sambil jaga p95 latency di bawah 300 ms. Setiap Locust run butuh 5 menit. Rancang pencarian otomatis: batas, predikat, berapa run, dan apa yang bikin hasil tidak bisa diandalkan.

:::quiz
Lihat contoh rancangan

- **Predikat**: `ok(users)` = jalankan Locust headless dengan `users` selama 5 menit (setelah warm-up), pulang `p95 <= 300 ms and error_rate < 1%`.
- **Anggapan monotonic**: lebih banyak pengguna tidak pernah buat latency lebih baik → sekali `ok` False, tetap False.
- **Batas**: cari batas atas dengan dua kalinya: 50 ✅, 100 ✅, 200 ✅, 400 ❌ → cari `[200, 400]`.
- **Pencarian biner** ke presisi 10 pengguna: 400−200 = 200 → sekitar log₂(20) ≈ 5 run lagi. Total ≈ 4 + 5 = 9 run ≈ 45 menit (vs 20+ run step 10).
- **Keandalan**: ukuran bising — ulangi run di batas, pakai data volume sama dan lingkungan baru, cache hangat, dan lapor margin aman (misalnya rencana kapasitas di 70% dari maksimum yang ketemu). Bising bisa rusak monotonicity di dekat batas, jadi perlakukan hasil sebagai taksiran.
:::

### 📝 Checklist review mandiri

- [ ] Predikat dan monotonicity tulis jelas
- [ ] Batas atas cari sebelum pencarian biner
- [ ] Jumlah run diestimasi
- [ ] Bising ukuran ditangani

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::problem{id="dsa-s3-binary-search-basics" title="Dasar Pencarian Biner" difficulty="easy" path="exercises/dsa/stage-3/13-binary-search-basics"}
Pencarian tepat, lower bound, dan akar kuadrat bilangan bulat dengan cari jawaban — tanpa `bisect` atau `math`.
:::

:::problem{id="dsa-s3-search-rotated" title="Cari Jadwal yang Diputar" difficulty="medium" path="exercises/dsa/stage-3/14-search-rotated"}
Temukan nilai dalam O(log n) saat larik terurut diputar di titik yang tidak diketahui.
:::

:::problem{id="dsa-s3-min-daily-capacity" title="Kapasitas Review Harian Paling Kecil" difficulty="medium" path="exercises/dsa/stage-3/15-min-daily-capacity"}
Cari biner pada jawaban dengan pengecekan kelayakan greedy.
:::

:::problem{id="dsa-s3-fair-sprint-split" title="Pisah Sprint Adil" difficulty="hard" path="exercises/dsa/stage-3/16-split-largest-sum"}
Cari: minimalkan yang terberat dari k sprint berturut-turut — dan jelaskan kenapa "paling banyak k" cukup.
:::

:::hints
- Test hitung berapa banyak elemen larik yang kamu baca: pencarian biner yang benar baca sekitar log₂(n) dari mereka.
- `integer_sqrt`: predikat `mid * mid <= n` True…True False…False; kamu mau True **terakhir**, jadi pembulat `mid` ke atas.
- `search_rotated`: bandingkan `nums[low] <= nums[mid]` untuk cari setengah yang terurut dulu, lalu periksa rentang target.
- `min_daily_capacity`: pengecekan greedy mulai hari baru saat tambah aplikasi berikutnya melebihi kapasitas.
:::

## ✅ Cek cepat

:::quiz
Kira-kira berapa langkah yang perlu pencarian biner untuk 1 juta item terurut?

Sekitar 20, karena 2²⁰ ≈ 1.048.576.
:::

:::quiz
Sifat apa yang harus punya kondisi agar "pencarian biner pada jawaban" bekerja?

Monotonicity: sekali kondisi jadi true untuk sesuatu nilai, tetap true untuk semua nilai lebih besar (atau semua nilai lebih kecil).
:::


## 📚 Lanjut belajar

- [Dokumentasi Python: bisect](https://docs.python.org/3/library/bisect.html)
- [Dokumentasi Git: git bisect](https://git-scm.com/docs/git-bisect)

---
title: "Backtracking"
summary: "Cari semua kemungkinan tanpa tenggelam di dalamnya — template pilih/jelajahi/batalkan, subset, permutasi, kombinasi, menangani nilai kembar, jalan di grid, N-Queens, dan pruning yang mengubah pencarian mustahil jadi seketika."
sourceHash: 0992d00c5961
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Satu template di balik semua soal backtracking: **pilih → jelajahi → batalkan**
- Membuat **subset**, **permutasi** dan **kombinasi** — dan tahu soal ini minta yang mana
- Menangani **nilai kembar** tanpa menghasilkan jawaban yang sama dua kali
- Berjalan di **grid** sambil menandai dan membatalkan tanda
- Menyelesaikan **N-Queens** dengan cek konflik O(1)
- **Pruning**: kenapa memotong cabang mati itu *adalah* algoritmanya, bukan sekadar optimasi
- 🧭 Cara mengenali soal backtracking

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Backtracking** | Coba satu pilihan, kalau gagal mundur satu langkah dan coba yang lain |
| **Decision tree** | Pohon bayangan berisi semua pilihan yang bisa kamu ambil |
| **Path** | Pilihan-pilihan yang sudah kamu ambil sejauh ini |
| **State** | Apa yang sedang kamu catat: item terpakai, jumlah, tanda |
| **Un-choose** | Membatalkan satu pilihan supaya pilihan berikutnya mulai bersih |
| **Pruning** | Memotong cabang lebih awal karena mustahil berhasil |
| **Subset** | Pilihan apa pun; urutan tidak penting |
| **Permutasi** | Susunan; urutan *justru* penting |

## 🧠 Ide besarnya

> Backtracking itu seperti **mencoba baju di toko**.

Kamu ambil satu kemeja, pakai, lihat kaca. Kurang cocok? Kamu **lepas dan kembalikan ke gantungannya**, lalu coba yang berikutnya. Kamu tidak pernah keluar dari kamar pas memakai lima kemeja sekaligus, dan tidak pernah meninggalkan kemeja teronggok di lantai — raknya harus kelihatan sama seperti semula, kalau tidak, orang berikutnya menemukan kekacauan.

"Mengembalikan ke gantungan" itu inti seluruh pelajaran ini. Rekursi berjalan maju. Backtracking berjalan maju **dan membersihkan saat pulang**.

```python
def explore(state):
    if state is complete:
        record it
        return
    for each option:
        if option is impossible:
            continue          # ← pruning
        apply option          # ← choose
        explore(state)        # ← explore
        undo option           # ← un-choose
```

Semua soal di pelajaran ini adalah fungsi itu dengan `option` yang berbeda dan `impossible` yang berbeda.

## ❓ Kenapa ini penting

Dua alasan, dan yang kedua lebih besar.

**Sering muncul di interview.** "Hasilkan semua…", "temukan satu susunan yang valid", "selesaikan puzzle ini" — subset, permutasi, combination sum, word search, N-Queens dan Sudoku semuanya satu template. Mengenalinya berarti kamu mulai menulis di menit pertama, bukan diam menatap layar.

**Dan ini bentuk pekerjaan nyata:**

| Pekerjaan nyata | Pencariannya |
|---|---|
| Matriks tes QA: kombinasi feature flag mana yang perlu dites | subset, dikurangi kombinasi yang tidak valid bersama |
| Penjadwal: membagi shift, ruangan, slot interview | satu keputusan per slot, dengan set konflik |
| Package manager memilih versi yang memenuhi semua dependensi | backtracking dengan pruning (ini memang cara `pip` menyelesaikannya) |
| Mesin regex mencocokkan `a*b?c` | coba, gagal, mundur, coba panjang berikutnya |
| Form builder memvalidasi "opsi ini tidak boleh dipilih bersamaan" | potong cabangnya |

Saat kamu berkata "saya modelkan sebagai pencarian atas keputusan, lalu saya potong state yang tidak valid", kamu sedang menggambarkan sebuah dependency resolver — dan itu kalimat level senior.

## 📖 Langkah demi langkah

### 1. Subset: catat di setiap simpul

Untuk `[1, 2]`, setiap titik di pohon itu sudah jadi jawaban yang sah, jadi kamu mencatat sambil turun.

```text
                []
        ┌───────┴───────┐
     ambil 1         lewati 1
       [1]              []
     ┌──┴──┐          ┌──┴──┐
   [1,2]   [1]       [2]    []
```

```python
def subsets(nums):
    result, path = [], []

    def explore(start):
        result.append(path[:])                 # a copy! see Common mistakes
        for i in range(start, len(nums)):
            path.append(nums[i])               # choose
            explore(i + 1)                     # explore (i + 1: never look back)
            path.pop()                         # un-choose

    explore(0)
    return result
```

`start` itulah yang mencegah `[1, 2]` dan `[2, 1]` dua-duanya muncul: begitu kamu melewati satu index, kamu tidak pernah kembali ke sana. Ada **2ⁿ** subset, jadi ini O(n · 2ⁿ) — bagian `· n` adalah biaya menyalin tiap path.

### 2. Permutasi: catat hanya di dasar

Sekarang urutan penting, jadi setiap item boleh dipakai di posisi mana pun — kamu hanya tidak boleh memakai item yang sama dua kali.

```python
def permutations(nums):
    result, path = [], []
    used = [False] * len(nums)

    def explore():
        if len(path) == len(nums):
            result.append(path[:])
            return                             # only complete arrangements count
        for i in range(len(nums)):
            if used[i]:
                continue
            used[i] = True
            path.append(nums[i])
            explore()
            path.pop()
            used[i] = False

    explore()
    return result
```

**n!** hasil. `n = 10` sudah 3,6 juta, jadi permutasi hanya muncul untuk input kecil. Kalau pewawancara memberi `n = 1000` lalu kamu memilih permutasi, berarti kamu salah membaca soalnya.

| | Catat di mana | Loop atas apa | Jumlah |
|---|---|---|---|
| Subset | setiap simpul | `start … n` | 2ⁿ |
| Permutasi | simpul dasar | semua yang belum terpakai | n! |
| Kombinasi ukuran k | simpul di kedalaman k | `start … n` | C(n, k) |

### 3. Nilai kembar: jawaban sama dua kali

`[1, 2, 2]` punya 8 cabang tapi hanya **6 subset berbeda**. Cara memperbaikinya selalu sama: **sortir**, lalu tolak memakai nilai yang sama dua kali *di level yang sama*.

```python
ordered = sorted(nums)
...
for i in range(start, len(ordered)):
    if i > start and ordered[i] == ordered[i - 1]:
        continue                               # same value, same position → same shape
```

Baca `i > start` dengan teliti. Artinya "saya bukan pilihan pertama di level ini". Angka `2` yang pertama boleh; `2` yang kedua *sebagai pilihan sebelah* tidak boleh. Tapi turun **lebih dalam** dengan `2` lagi tetap boleh, dan itulah yang membuat `[2, 2]` selamat.

Untuk permutasi dengan nilai kembar, syaratnya berbeda, karena posisi berpengaruh:

```python
if i > 0 and ordered[i] == ordered[i - 1] and not used[i - 1]:
    continue                                   # my equal twin before me is not placed yet
```

> Analogi: dua koin `2` yang identik. Menentukan koin identik *mana* yang kamu ambil itu tidak ada artinya, jadi kamu buat aturan — selalu ambil yang kiri dulu. Susunan yang mengambil yang kanan dulu adalah susunan yang sama, terhitung dua kali.

### 4. Grid: tandai, jalan, batalkan tanda

Grid adalah graf yang tetangganya atas/bawah/kiri/kanan. Word search itu DFS plus satu baris:

```python
def exists(board, word):
    rows, cols = len(board), len(board[0])

    def walk(row, col, index):
        if index == len(word):
            return True
        if not (0 <= row < rows and 0 <= col < cols) or board[row][col] != word[index]:
            return False
        board[row][col] = "\0"                 # mark: I am standing here
        found = (walk(row + 1, col, index + 1) or walk(row - 1, col, index + 1)
                 or walk(row, col + 1, index + 1) or walk(row, col - 1, index + 1))
        board[row][col] = word[index]          # un-mark on the way out
        return found

    return any(walk(r, c, 0) for r in range(rows) for c in range(cols))
```

Hilangkan baris terakhir itu dan satu percobaan gagal akan meracuni papan selamanya: pencarian berikutnya melihat sel yang sebenarnya tidak terpakai. Ucapkan ini di interview: *"saya tandai selnya, dan saya pulihkan saat keluar, jadi papan yang diberikan pemanggil tidak berubah."*

### 5. Pruning: ini algoritmanya

Semua di atas hanya pembukuan. **Pruning-lah yang membuat backtracking layak disebut backtracking.** Bandingkan dua bagian combination sum:

```python
for i in range(start, len(ordered)):
    if ordered[i] > remaining:
        break              # sorted, so every later candidate is too big as well
```

Satu baris, dan seluruh sub-pohon tidak pernah dibangun.

N-Queens memperlihatkannya paling jelas. Taruh satu ratu per baris, jadi baris mustahil bentrok. Untuk sisanya, perhatikan bahwa setiap sel di satu diagonal punya angka yang sama:

```text
row + col  (↗ naik)            row - col  (↘ turun)
  0 1 2 3                        0 -1 -2 -3
  1 2 3 4                        1  0 -1 -2
  2 3 4 5                        2  1  0 -1
  3 4 5 6                        3  2  1  0
```

```python
def count_queen_placements(n):
    columns, rising, falling = set(), set(), set()

    def place(row):
        if row == n:
            return 1
        found = 0
        for col in range(n):
            if col in columns or row + col in rising or row - col in falling:
                continue                       # attacked → dead branch, cost: 3 lookups
            columns.add(col); rising.add(row + col); falling.add(row - col)
            found += place(row + 1)
            columns.remove(col); rising.remove(row + col); falling.remove(row - col)
        return found

    return place(0)
```

Tiga set lookup O(1) menggantikan pemindaian papan. Itu bedanya antara `n = 9` menjawab seketika dan tidak selesai sama sekali.

Tiga jenis pruning yang perlu kamu kenali namanya:

- **Cek state mustahil** — "ini melanggar aturan, berhenti" (N-Queens, kombinasi flag yang tidak valid).
- **Cek batas (bound)** — "bahkan di kasus terbaik, cabang ini tidak mungkin mengalahkan yang sudah saya punya, berhenti". Simpan yang terbaik sejauh ini lalu bandingkan; ini disebut *branch and bound*.
- **Urutkan pilihannya** — coba dulu pilihan dengan **kemungkinan tersisa paling sedikit**, supaya jalan mati muncul di puncak pohon tempat biayanya nol. Solver Sudoku mengisi sel paling terbatas lebih dulu justru karena ini.

:::tip[🧭 Cara mengenali soal backtracking]
- **"Hasilkan semua / daftar semua / cetak semua kemungkinan"** → subset, permutasi atau kombinasi. Tentukan yang mana dengan bertanya: *apakah urutan penting?* dan *apakah item boleh berulang?*
- **"Temukan **satu** … yang valid" / "apakah ada susunan yang …"** → backtracking yang berhenti di keberhasilan pertama (`return True`).
- **"Ada berapa cara …"** dengan `n` kecil → hitung cabang. Dengan `n` besar → itu dynamic programming, bukan pelajaran ini.
- **"Bagi / pecah jadi beberapa kelompok"** → backtracking dengan pruning berat.
- **Kata-kata puzzle** — papan, grid, ratu, sudoku, labirin, kata — hampir selalu tandai/batalkan tanda.
- Batas input adalah petunjuk terbesar: `n ≤ 20` mengundang 2ⁿ, `n ≤ 10` mengundang n!. `n ≤ 100000` tidak pernah.
:::

### Memilih caranya

| Situasi | Pakai |
|---|---|
| Butuh semua jawaban | kumpulkan ke list `result` |
| Butuh satu jawaban saja | `return True` lalu langsung naik |
| Butuh jumlahnya saja | kembalikan `int`, jangan pernah bangun list-nya (hemat memori) |
| Butuh jawaban terbaik | simpan yang terbaik sejauh ini lalu potong dengan bound |
| Ada nilai kembar di input | sortir, lalu lewati tetangga yang nilainya sama |
| `n` besar (> ~20) | berhenti — cari DP, greedy atau rumus |

- ✅ Input kecil, "semua kemungkinan", puzzle berkendala, pencarian validitas.
- 🚫 Input besar yang jawabannya saling tumpang tindih — tumpang tindih itulah yang dimanfaatkan DP (pelajaran berikutnya).
- 🚫 Apa pun yang sudah pasti beres dengan aturan greedy; backtracking hanya lebih lambat untuk jawaban yang sama.

## ⚠️ Kesalahan umum

- `result.append(path)` bukan `result.append(path[:])` — kamu menyimpan *list yang sama* setiap kali, dan karena kamu terus mem-pop darinya, semua jawaban berakhir kosong. Ini bug backtracking paling sering.
- Lupa membatalkan pilihan, sehingga state merembes ke cabang berikutnya (grid tetap tertandai, `used` tetap `True`).
- Mengubah input milik pemanggil lalu tidak memulihkannya.
- Melewati nilai kembar dengan `i > 0` padahal seharusnya `i > start`, yang juga membunuh pengulangan sah yang lebih dalam seperti `[2, 2]`.
- Rekursi dengan `i + 1` padahal kandidat boleh dipakai ulang, atau dengan `i` padahal tidak boleh.
- Membalik syarat: di permutasi dengan nilai kembar syaratnya `not used[i - 1]`, bukan `used[i - 1]`.
- Tidak melakukan pruning sama sekali, lalu menyalahkan bahasanya karena timeout.
- Menabrak batas rekursi Python (~1000 frame) pada pencarian yang dalam — ubah jadi loop dengan stack eksplisit, atau naikkan batasnya secara sadar.
- Membangun semua hasil padahal soalnya cuma bertanya "ada berapa".

## 🏆 Praktik terbaik

- [ ] Tulis template-nya dulu (pilih / jelajahi / batalkan), baru isi tiga bagian kosongnya.
- [ ] Sebutkan apa itu satu "keputusan" sebelum menulis kode: satu kolom untuk baris ini, satu index untuk diambil atau dilewati.
- [ ] Simpan **salinan** path, jangan pernah path-nya sendiri.
- [ ] Setiap `choose` punya tepat satu `un-choose` pasangannya, di semua jalur keluar.
- [ ] Tinggalkan input persis seperti saat kamu menerimanya.
- [ ] Tambahkan pruning sebagai langkah terpisah yang diberi nama, dan sebutkan apa yang dihemat.
- [ ] Sebutkan biayanya dengan jujur: 2ⁿ, n!, atau "eksponensial tapi dipotong keras".
- [ ] Tes input kosong, satu item, item yang semuanya sama, dan kasus yang sama sekali tidak punya jawaban.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke temanmu, pakai analogi kamar pas, kenapa `result.append(path)` menghasilkan list berisi list kosong sementara `result.append(path[:])` berhasil — dan kenapa bug itu tidak kelihatan pada input satu elemen.

## 📐 Rancang

CareerPilot menambah **perencana mock interview**. Kamu punya:

- **6 sesi latihan** selama dua minggu (3 per minggu)
- daftar **topik lemah** (array, graf, system design, …) — tidak ada topik dua kali
- **3 partner**, masing-masing punya waktu yang tidak bisa dan topik yang ditolak
- satu aturan: **tidak ada partner dua kali dalam minggu yang sama**

Rancang pencarian yang menghasilkan jadwal valid, melaporkan dengan jelas kalau tidak ada yang mungkin, dan nanti bisa diminta jadwal *terbaik* (partner dipasangkan ke topik terkuatnya) bukan sekadar yang valid.

:::quiz
Lihat salah satu rancangan

- **Satu keputusan per sesi.** Sesi adalah barisnya, seperti N-Queens: sesi 1 mendapat pasangan (topik, partner), lalu sesi 2, dan seterusnya. Jangan "pilih topik untuk semua sesi sekaligus" — itu pohon yang lebih besar untuk jawaban yang sama.
- **State, semuanya O(1) untuk dicek:** `used_topics` (sebuah set), `partner_count_this_week` (dict per minggu), dan tabel ketidaktersediaan tiap partner. Tes konflik sebelum memilih: topik belum terpakai, partner bebas di waktu itu, partner menerima topiknya, partner belum dipakai minggu ini.
- **Template-nya:** untuk tiap pasangan kandidat di sesi ini → kalau bentrok, `continue`; kalau tidak, tambahkan ke set, rekursi ke sesi berikutnya, lalu keluarkan lagi dari set.
- **Berhenti di jadwal penuh pertama** (`return True`) karena soalnya minta *satu* jadwal valid. Mengumpulkan semuanya akan menghasilkan ribuan jadwal yang hampir identik.
- **Pruning yang penting:** (1) kalau jumlah topik yang belum terpakai lebih kecil dari jumlah sesi yang tersisa, menyerah sekarang; (2) urutkan sesi dari **yang pasangan tersedianya paling sedikit** — slot Jumat malam yang hanya satu partner bisa, diputuskan di puncak pohon tempat kegagalan masih murah.
- **Kegagalan yang jelas:** waktu pencarian mengembalikan `False`, jangan bilang "tidak ada jadwal". Laporkan di sesi mana semua cabang mati beserta alasannya: *"Sesi 5: ketiga partner tidak bisa Jumat malam"*. Kumpulkan alasannya selama pencarian.
- **Kalau nanti diminta jadwal terbaik**, ini berubah jadi **branch and bound**: beri skor tiap pasangan (kekuatan partner × kelemahan topik), simpan jadwal lengkap terbaik sejauh ini, lalu potong cabang yang skor terbaiknya pun tidak mungkin mengalahkannya. Template sama, hanya tambah satu perbandingan.
- **Biaya:** paling banyak (topik × partner)⁶ cabang, yang dipotong pruning jadi segelintir. Sangat kecil — dan ini layak diucapkan, karena itu yang membenarkan pakai backtracking daripada library solver.

**Aturan yang ditunjukkan:** satu keputusan per slot, konflik sebagai set, yang paling sedikit pilihannya dulu, dan tambahkan bound kalau butuh yang *terbaik* bukan sekadar yang *valid*.
:::

### 📝 Daftar cek diri

- [ ] Satu keputusan per sesi, bukan per topik
- [ ] Setiap cek konflik O(1)
- [ ] Pilih dan batalkan selalu berpasangan
- [ ] Kegagalan dijelaskan, bukan hanya dilaporkan
- [ ] Jalan dari "valid" ke "terbaik" cuma satu cek bound

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::problem{id="dsa-s5-subsets-permutations" title="Subsets & Permutations" difficulty="medium" path="exercises/dsa/stage-5/01-subsets-and-permutations"}
Empat batu bata dasarnya: semua subset, subset berbeda saat ada nilai kembar, semua permutasi, permutasi berbeda saat ada nilai kembar.
:::

:::problem{id="dsa-s5-combination-sum" title="Combination Sum & Equal Groups" difficulty="medium" path="exercises/dsa/stage-5/02-combination-sum"}
Kombinasi yang pas mencapai target dengan dan tanpa pemakaian ulang, lalu membagi list jadi k kelompok bersum sama — di situ pruning-nya jadi inti latihan.
:::

:::problem{id="dsa-s5-word-search" title="Word Search & Routes on a Grid" difficulty="medium" path="exercises/dsa/stage-5/03-word-search"}
Merangkai kata dengan berjalan di grid, menyaring daftar kata, dan menghitung rute yang melewati setiap sel terbuka tepat sekali.
:::

:::problem{id="dsa-s5-n-queens" title="N-Queens" difficulty="hard" path="exercises/dsa/stage-5/04-n-queens"}
Tantangan: hitung semua solusi dan kembalikan satu papan, dengan cek diagonal O(1) supaya n = 9 selesai seketika.
:::

:::hints
- Subset: `result.append(path[:])` di **awal** `explore`, sebelum loop — setiap simpul adalah jawaban.
- Subset mempertahankan urutan input di dalam tiap subset, jadi loop `for i in range(start, len(nums))` dan rekursi dengan `i + 1`.
- Subset berbeda: sortir dulu; di dalam loop `if i > start and a[i] == a[i - 1]: continue`.
- Permutasi: catat hanya saat `len(path) == len(nums)`; simpan list boolean `used`.
- Permutasi berbeda: sortir, lalu `if i > 0 and a[i] == a[i - 1] and not used[i - 1]: continue`.
- Combination sum: kandidat boleh dipakai ulang, jadi rekursi dengan `i`, bukan `i + 1`; sortir lalu `break` saat `a[i] > remaining`.
- `combination_sum_once`: rekursi dengan `i + 1` **dan** pakai juga lewatan nilai kembar satu level.
- Kelompok bersum sama: langsung `False` kalau `sum(nums) % k`, atau kalau `max(nums) > sum(nums) // k`.
- Kelompok bersum sama: sortir menurun, isi satu kelompok sekaligus, lewati kelompok yang isinya sama dengan yang sudah dicoba, dan `break` setelah gagal di kelompok yang masih **kosong**.
- Word search: tulis `board[row][col] = "\0"` sebelum empat panggilan rekursif dan pulihkan hurufnya setelahnya.
- `count_routes`: hitung dulu jumlah sel terbuka; satu rute hanya dihitung kalau kamu mendarat di `E` setelah melewati semuanya.
- N-Queens: satu ratu per baris; simpan `columns`, `rising = row + col` dan `falling = row - col` sebagai set.
- N-Queens: `first_queen_board` harus `return True` sampai ke atas begitu papan pertama penuh, dan merender baris sebagai `"." * col + "Q" + "." * (n - col - 1)`.
:::

## ✅ Cek cepat

:::quiz
Kenapa harus `path[:]` dan bukan `path`?

`path` adalah satu list yang terus kamu append dan pop. Menyimpan `path` berarti menyimpan referensinya, jadi semua "jawaban" yang tersimpan menunjuk ke list yang sama — dan begitu pencarian selesai, list itu sudah kosong lagi. `path[:]` membuat potret path apa adanya saat ini. Bug-nya bersembunyi pada input satu elemen, karena path-nya tidak pernah di-pop sebelum selesai.
:::

:::quiz
Subset dicatat di setiap simpul pohon, permutasi hanya di simpul dasar. Kenapa?

Subset adalah pilihan apa pun, jadi path setengah jadi seperti `[1]` sudah merupakan subset yang lengkap dan sah. Permutasi harus memuat semua item, jadi path setengah jadi belum jadi jawaban — hanya path dengan panjang penuh yang dihitung.
:::

:::quiz
Pruning sering disebut optimasi. Kenapa kata itu salah untuk backtracking?

Tanpa pruning, pencariannya mengunjungi semua cabang, yang untuk sebagian besar input nyata tidak pernah selesai — jadi tidak ada versi "lambat tapi jalan" yang bisa dioptimasi. Pruning *itulah* yang membuat algoritmanya jalan sama sekali. N-Queens pada n = 9 dan membagi 16 angka jadi 4 kelompok, dua-duanya mustahil tanpa pruning dan seketika dengan pruning.
:::

## 📚 Lanjut belajar

- [VisuAlgo: N-Queens dan pohon rekursi](https://visualgo.net/en/recursion)
- [Wikipedia: Backtracking](https://en.wikipedia.org/wiki/Backtracking)
- [Dokumentasi Python: `sys.setrecursionlimit`](https://docs.python.org/3/library/sys.html#sys.setrecursionlimit)

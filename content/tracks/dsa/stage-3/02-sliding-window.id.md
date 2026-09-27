---
title: "Sliding Window"
summary: Jawab pertanyaan tentang rentang data berdampingan dalam O(n) — jendela ukuran tetap, jendela yang tumbuh dan mengecil dengan pencatatan, dan kenapa bilangan positif itu penting.
sourceHash: 3fa230f8ab0b
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- **Jendela ukuran tetap**: perbarui dalam O(1) bukan menghitung ulang
- **Jendela ukuran berubah**: perluas kanan, kurangi kiri, dengan syarat yang sah
- Lacak isi jendela dengan penghitung dan jumlah "kurang"
- Kapan sliding window **tidak bekerja** (bilangan negatif) dan apa yang dipakai sebagai gantinya
- 🧭 Cara mengenali masalah sliding window

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Window** | Rentang data berdampingan yang sedang kamu lihat |
| **Contiguous** | Data berurutan tanpa celah |
| **Fixed-size window** | Jendela selalu k item lebar |
| **Variable-size window** | Tumbuh dan mengecil untuk tetap sah |
| **Expand / shrink** | Tambah item di kanan / buang di kiri |
| **Validity condition** | Syarat yang harus dipenuhi jendela (tidak ada pengulangan, jumlah ≤ k) |
| **Amortised O(n)** | Setiap data masuk dan keluar paling banyak sekali |

## 🧠 Ide besarnya

Bayangkan kamu di kereta, menatap pemandangan melalui jendela yang menampilkan persis 3 rumah. Ketika kereta bergerak maju satu rumah, kamu tidak menghitung ulang ketiga rumah itu — **satu rumah masuk dari kanan, satu keluar dari kiri**.

Sliding window menyimpan ringkasan (jumlah, pencatatan, set) dari rentang data berdampingan dan **memperbarui**nya saat rentang bergeser. Setiap elemen ditambah sekali dan dihapus sekali: O(n).

## ❓ Kenapa ini penting

Banyak pertanyaan nyata tentang **rentang data yang berdampingan**:

- pendapatan tertinggi dalam periode 7 hari apa pun,
- sesi terpanjang tanpa halaman yang diulang,
- request dalam 60 detik terakhir (rate limiting — Stage 2),
- snippet teks terpendek yang berisi semua kata pencarian.

Menghitung ulang rentang penuh di setiap posisi adalah O(n·k). Menggeser jendela malah memperbarui ringkasan yang terus berjalan dalam O(1) per langkah, yang mengubah seluruh pemindaian menjadi O(n) — seperti penumpang kereta menghitung satu rumah masuk dan satu keluar, bukan menghitung ulang pemandangan.

## 📖 Langkah demi langkah

### 1. Jendela ukuran tetap

```python
window = sum(nums[:k])
best = window
for right in range(k, len(nums)):
    window += nums[right] - nums[right - k]    # enters, leaves
    best = max(best, window)
```

```text
[2 1 5] 1 3 2   sum 8
2 [1 5 1] 3 2   8 + 1 - 2 = 7
2 1 [5 1 3] 2   7 + 3 - 1 = 9 ✅
2 1 5 [1 3 2]   9 + 2 - 5 = 6
```

Bekerja untuk jumlah, penghitung vokal, "ada pengulangan dalam k posisi" (set dari k item terakhir).

### 2. Jendela ukuran berubah: template-nya

Bentuknya selalu sama: perluas ke kanan sampai jendela melanggar aturan, lalu kurangi dari kiri sampai sah lagi, catat jawaban terbaik seiring berjalan.

```python
left = 0
for right, item in enumerate(items):
    add(item)                          # 1. expand
    while not valid():                 # 2. shrink until valid again
        remove(items[left])
        left += 1
    best = max(best, right - left + 1) # 3. record (for "longest" problems)
```

Untuk masalah **"terpendek"**, balikkan: catat di dalam loop pengurangan **saat jendela sah**.

### 3. Terpanjang dengan syarat

*Lari hari terpanjang dalam anggaran* (semua biaya positif):

- perluas: `total += cost`
- tidak sah ketika `total > budget` → kurangi dari kiri
- catat panjang setelah mengecilkan

*Substring terpanjang tanpa pengulangan*: simpan `last_seen[char]`; jika karakter dilihat **di dalam** jendela, loncat `left` ke `last_seen[char] + 1`.

### 4. Jendela terpendek yang berisi segalanya

Lacak **apa yang kurang**, jadi keabsahan adalah O(1):

```python
need = Counter(required)
missing = len(required)
for right, char in enumerate(text):
    if need[char] > 0:
        missing -= 1
    need[char] -= 1                     # negative = extra copies in window
    while missing == 0:                 # valid → try to shrink
        record(left, right)
        need[text[left]] += 1
        if need[text[left]] > 0:
            missing += 1
        left += 1
```

### 5. Kenapa bilangan positif penting

Dengan bilangan negatif, mengecilkan jendela bisa **menambah** jumlah, jadi "terlalu besar → kurangi" berhenti menjadi benar. Di sini prefix sum (materi berikutnya) mengambil alih.

Mengecilkan bekerja karena menghapus elemen **selalu mengurangi** jumlah, menambah selalu menambah. Dengan bilangan negatif, jendela di atas anggaran mungkin menjadi sah dengan **menambah** lebih banyak item, jadi "kurangi saat tidak sah" bisa melewatkan jawaban.

- Masalah jumlah subarray **dengan negatif** → **prefix sum + hash map** (materi berikutnya).
- Jumlah subarray maksimal (panjang apa pun) → **Algoritma Kadane** (kasus khusus dynamic programming).

### 6. Amortised O(n)

Loop `while` di dalam terlihat seperti nesting, tapi `left` hanya bergerak maju dan tidak pernah melewati `right`. Di seluruh keseluruhan, `left` bergerak paling banyak n kali → total O(n).

:::tip[🧭 Cara mengenali sliding window]
- Pertanyaannya tentang **subarray atau substring berdampingan** (bukan subsequence, bukan subset apa pun).
- Kata-kata seperti **terpanjang / terpendek / maksimal / minimal / paling banyak / persis k** di atas rentang.
- Jendela **ukuran tetap** k, atau syarat yang menjadi benar/salah **monotonically** seiring jendela tumbuh (jumlah positif, penghitung unik, penghitung item yang diperlukan).
- Brute force menghitung ulang sesuatu untuk setiap rentang yang bertumpang tindih berat dengan rentang sebelumnya.

Bilangan negatif dan jumlah pasti? → prefix sum. Pilihan tidak berdampingan? → bukan jendela (pikir DP atau greedy).
:::

### Memilih setup-mu

Setiap pilihan di sini adalah trade-off:

| Pendekatan | Waktu | Ruang | Bekerja dengan negatif? |
|---|---|---|---|
| Brute force di semua rentang | O(n²)–O(n³) | O(1) | ya |
| Jendela tetap | O(n) | O(1) | ya |
| Jendela berubah (kurangi saat tidak sah) | O(n) | O(1)–O(alphabet) | hanya ketika syarat monotonic |
| Prefix sum + hash map | O(n) | O(n) | ya (jumlah pasti) |
| Deque untuk jendela max/min | O(n) | O(k) | ya |

- ✅ Metrik menggulung, rata-rata bergerak, rate limit, kendala string/array berdampingan.
- 🚫 Subsequence atau subset arbitrer.
- 🚫 Syarat yang tidak monotonic dengan ukuran jendela (jumlah dengan negatif).

## ⚠️ Kesalahan umum

- Menggunakan jendela pada data dengan bilangan negatif untuk syarat "paling banyak jumlah".
- Menggerakkan `left` mundur dalam masalah "terpanjang tanpa pengulangan" (gunakan `max` atau periksa `last_seen >= left`).
- Menghitung ulang jumlah atau penghitung jendela di dalam loop.
- Mencatat jawaban di tempat yang salah (sebelum mengecilkan untuk "terpanjang").

## 🏆 Praktik terbaik

- [ ] Tanya: *berdampingan? ukuran tetap atau berubah? nilai non-negatif?*
- [ ] Tulis **state jendela** dulu (jumlah, penghitung, set, jumlah kurang) dan kondisi **valid()** dengan kata-kata.
- [ ] Untuk "terpanjang", catat setelah mengecilkan; untuk "terpendek", catat saat sah sebelum mengecilkan.
- [ ] Gunakan `right - left + 1` untuk panjang dan double-check off-by-one dengan contoh 1 elemen.
- [ ] Jaga update O(1): penghitung atau jumlah yang berjalan, jangan pernah `sum(window)` di loop.
- [ ] Jelaskan argumen amortised O(n) — pewawancara mengharapkannya.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke product manager bagaimana dashboard bisa menampilkan "periode penjualan 7 hari terbaik tahun ini" secara instan, tanpa menjumlahkan setiap periode 7 hari yang mungkin — gunakan analogi jendela kereta.

## 📐 Rancang

CareerPilot ingin aturan penipuan: **tandai pengguna yang mengirim lebih dari 20 aplikasi dalam periode 10 menit apa pun**. Aplikasi tiba sebagai aliran `(user_id, timestamp)` dalam urutan waktu. Rancang struktur data dan algoritma per-event, kompleksitasnya, dan pertumbuhan memori untuk 100.000 pengguna aktif.

:::quiz
Lihat desain yang mungkin

Per pengguna, sebuah **deque timestamp** dalam 10 menit terakhir (jendela sliding berbasis waktu):

```text
on event (user, t):
    window = windows[user]           # deque
    window.append(t)
    while window[0] <= t - 600:       # evict events older than 10 min
        window.popleft()
    if len(window) > 20: flag(user)
```

- **Waktu**: amortised O(1) per event (setiap timestamp ditambah dan dikeluarkan sekali).
- **Memori**: paling banyak 21 timestamp per pengguna yang pernah dibutuhkan → batas deque (`maxlen=21` masih bekerja untuk menghitung > 20) → ~100.000 × 21 timestamp, puluhan MB; hapus juga deque untuk pengguna idle > 10 menit.
- **Alternatif**: jika tidak perlu tepat, simpan penghitung per bucket 1 menit (10 bucket per pengguna) — memori lebih sedikit, ketidaktepatan sedikit di tepi bucket.
- **Production**: beberapa server API → simpan jendela di Redis (sorted set dengan `ZREMRANGEBYSCORE` + `ZCARD`) atau di stream processor.
:::

### 📝 Checklist review mandiri

- [ ] Jendela ditentukan oleh waktu, bukan penghitung
- [ ] Eviction terjadi sebelum pengecekan
- [ ] Memori terbatas per pengguna dan pengguna idle dibersihkan
- [ ] Realitas multi-server dipertimbangkan

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::problem{id="dsa-s3-sliding-window-basics" title="Sliding Window Basics" difficulty="easy" path="exercises/dsa/stage-3/05-sliding-window-basics"}
Max sum of k consecutive items, repeats within k positions, and most vowels in a window — all O(n) regardless of k.
:::

:::problem{id="dsa-s3-longest-unique-run" title="Longest Run Without Repeats" difficulty="medium" path="exercises/dsa/stage-3/06-longest-unique-substring"}
Variable window with a last-seen dictionary to jump the left edge.
:::

:::problem{id="dsa-s3-longest-affordable" title="Longest Streak Under Budget" difficulty="medium" path="exercises/dsa/stage-3/07-longest-under-budget"}
Expand and shrink a window of positive costs to find the longest affordable run.
:::

:::problem{id="dsa-s3-shortest-covering" title="Shortest Snippet With All Keywords" difficulty="hard" path="exercises/dsa/stage-3/08-minimum-window"}
Stretch: the minimum window containing all required characters, with a "missing" counter for O(1) validity checks.
:::

:::hints
- `has_nearby_repeat`: keep a set of at most the last `k` items; remove `items[i - k]` once the set is too big.
- `longest_unique_run`: `if last_seen.get(char, -1) >= left: left = last_seen[char] + 1`.
- `longest_affordable`: shrink with `while total > budget`.
- `shortest_covering`: store the best `(start, length)`, not the substring, to avoid copying inside the loop; use `<` (not `<=`) to keep the leftmost.
:::

## ✅ Cek cepat

:::quiz
Kenapa jendela "kurangi saat di atas anggaran" tidak bekerja jika biaya bisa negatif?

Dengan negatif, menambah lebih banyak item bisa mengurangi total, jadi jendela yang sekarang di atas anggaran mungkin menjadi sah dengan perluas — mengecilkan bisa membuang rentang optimal. Pakai prefix sum sebagai gantinya.
:::

:::quiz
Jendela berubah punya `while` di dalam `for`. Kenapa O(n)?

`left` hanya bergerak maju dan paling banyak n kali total di seluruh loop, jadi semua langkah shrink bersama O(n).
:::

## 📚 Lanjut belajar

- [Python docs: collections.Counter](https://docs.python.org/3/library/collections.html#collections.Counter)
- [Redis docs: Sorted sets (used for sliding-window counters)](https://redis.io/docs/latest/develop/data-types/sorted-sets/)

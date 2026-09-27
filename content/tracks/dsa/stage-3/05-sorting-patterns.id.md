---
title: "Pola-Pola Sorting"
summary: Sorting sebagai alat pemecah masalah — custom key dan stabilitas, merge sort vs quicksort, interval dan sweep line, heap untuk top-k, partisi, dan menghitung inversi.
sourceHash: dd97a166ebc5
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Cara membandingkan algoritma sort: merge sort, quicksort, Timsort, counting sort
- **Stabilitas** dan multi-key sorting dengan `key=`
- Pola "sort dulu": interval, sweep line, greedy scheduling
- Heap untuk **top-k** alih-alih sort penuh
- **Partisi** (Dutch national flag) dan **divide & conquer** (inversi)
- 🧭 Cara mengenali kapan sorting membuka solusi masalah

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Stable sort** | Data yang sama tetap urutan aslinya |
| **`key=`** | Fungsi yang memutuskan apa yang di-sort |
| **Timsort** | Sort bawaan Python — cepat di data yang sudah terurut sebagian |
| **Merge sort / quicksort** | Dua algoritma klasik O(n log n) |
| **Interval** | Rentang dengan awal dan akhir |
| **Sweep line** | Berjalan melalui kejadian berurutan waktu, hitung sambil berjalan |
| **Heap** | Struktur yang selalu kasih nilai terkecil (atau terbesar) dengan cepat |
| **Top-k** | k data terbaik, tanpa sort semua |
| **Partisi** | Memisahkan data ke kelompok dalam satu jalan |

## 🧠 Ide besarnya

Sorting itu seperti **mengorganisir tumpukan kuitansi berantakan berdasarkan tanggal** sebelum lapor pajak. Sorting butuh usaha, tapi sesudahnya "kuitansi mana yang tumpang tindih minggu ini?", "celah terbesar berapa?", "ada duplikat?" jadi jalan mudah melalui tumpukan.

Di interview, pertanyaannya jarang "buat sebuah sort" — lebih sering "**apakah sort dulu bikin ini mudah**, dan apakah O(n log n) bisa diterima?"

## ❓ Kenapa ini penting

Urutan membuat struktur, dan struktur bikin pertanyaan mudah. Setelah sort:

- duplikat duduk berdampingan,
- interval tumpang tindih duduk berdampingan,
- two pointer dan binary search jadi mungkin,
- dan pilihan greedy (selesai paling awal dulu) jadi provably correct.

Di interview pertanyaannya hampir tidak pernah "buat sebuah sort". Lebih sering "**apakah sort dulu bikin ini mudah**, dan apakah aku sanggup O(n log n)?**" — penilaian yang sama dengan memutuskan rapi-rapi kuitansi sebelum lapor pajak.

## 📖 Langkah demi langkah

### 1. Algoritma yang kamu harus bisa jelaskan

| Algoritma | Waktu (rata / terburuk) | Ruang | Stabil | Ide |
|---|---|---|---|---|
| **Merge sort** | O(n log n) / O(n log n) | O(n) | ✅ | bagi dua, sort setengah, gabung (dua pointer!) |
| **Quicksort** | O(n log n) / O(n²) | O(log n) | ❌ | pilih pivot, pisahkan lebih kecil/lebih besar, rekurse |
| **Heapsort** | O(n log n) / O(n log n) | O(1) | ❌ | buat heap, pop max berulang |
| **Timsort** (Python) | O(n log n) / O(n log n), O(n) di data hampir terurut | O(n) | ✅ | temukan run yang ada, gabung |
| **Counting sort** | O(n + k) | O(k) | ✅ | saat nilai integer kecil (0..k) |

Sort berbasis perbandingan tidak bisa kalahkan O(n log n) secara umum. Counting/radix sort bisa karena tidak perlu bandingkan.

### 2. Custom key dan stabilitas di Python

```python
jobs.sort(key=lambda job: (-job["salary"], job["title"]))   # salary high→low, then title A→Z
```

- Tuple bandingkan elemen demi elemen — sempurna untuk sort multi-key.
- Tidak bisa negasi string? Pakai **stabilitas**: sort key paling tidak penting dulu, lalu key lebih penting; yang sama tetap urutan sebelumnya.

```python
by_title = sorted(jobs, key=lambda j: j["title"])
by_date = sorted(by_title, key=lambda j: j["posted_on"], reverse=True)   # newest first, ties stay A→Z
```

- Nilai `None`: sort dengan `(value is None, value)` untuk masukkan ke belakang.

### 3. Interval: sort mulai, lalu gabung

Setelah interval di-sort mulai waktu, kamu hanya pernah bandingkan setiap satu dengan interval terakhir disimpan — sisanya tidak bisa tumpang tindih, karena mulai lebih nanti.

```python
merged = []
for start, end in sorted(intervals):
    if merged and start <= merged[-1][1]:     # overlaps (or touches) the last one
        merged[-1][1] = max(merged[-1][1], end)
    else:
        merged.append([start, end])
```

Jelaskan **menyentuh**: apakah `[1, 3]` dan `[3, 5]` tumpang tindih? Untuk slot kalender `[9:00, 10:00)` tidak; untuk hari inklusif ya.

### 4. Sweep line: ruangan dibutuhkan

Ubah interval ke peristiwa dan jalan waktu berurutan:

```python
starts = sorted(s for s, _ in meetings)
ends = sorted(e for _, e in meetings)
# walk starts; before each start, release every room whose end <= start
```

Jumlah maksimum meeting bersamaan = ruangan dibutuhkan. Ide sama: puncak user bersamaan, booking tumpang tindih terbanyak, jam paling ramai.

### 5. Top-k dengan heap

Untuk "10 terbaik dari sejuta", sort semuanya seperti ranking setiap atlet di negara untuk temukan sepuluh teratas. Heap hanya simpan sepuluh terbaik sekarang saat kamu jalan lewat.

```python
import heapq
heapq.nlargest(3, scores)          # O(n log k)
# or keep a min-heap of size k and replace its smallest when you see something bigger
```

Untuk k dekat n, cukup sort. Untuk "k-th largest" quickselect rata rata O(n) (tapi terburuk O(n²)).

### 6. Partisi dalam satu jalan

Tiga kategori (tinggi / sedang / rendah) di-sort **di tempat** dengan tiga pointer — Dutch national flag. Langkah partisi ini juga inti quicksort.

```text
[ high... | medium... | unknown... | low... ]
          low        mid          high
```

### 7. Divide and conquer: hitung inversi

Langkah merge sort tahu sesuatu berguna: saat item dari **setengah kanan** ditempatkan sebelum item **kiri** tersisa, ia lebih kecil dari semuanya — itu `len(left) - i` inversi dihitung sekali. O(n log n) alih-alih O(n²). Trik yang sama ukur seberapa sama dua ranking.

:::tip[🧭 Cara mengenali pola sort]
- **Interval**, jadwal, booking, tumpang tindih → sort mulai (atau akhir untuk greedy selection).
- "Maksimum bersamaan…", "waktu paling ramai" → sweep line atas peristiwa terurut.
- "Top k", "k-th largest", "k terdekat" → heap (atau quickselect).
- Kelompok/duplikat saat hash map tidak boleh → sort, lalu bandingkan tetangga.
- Ranking dengan beberapa kriteria → tuple key dan sort stabil.
- Hanya beberapa nilai unik → counting sort / partisi dalam O(n).
- Pasangan dihitung dengan kondisi urutan (`i < j` dan `a[i] > a[j]`) → merge sort varian.
:::

### Pilih setup-mu

Setiap pilihan di sini trade-off:

| Pilihan | ✅ | ❌ |
|---|---|---|
| Sort dulu | buka two pointer, merge, greedy | O(n log n); hilang urutan asli (simpan index jika butuh) |
| Hash map alih-alih | O(n) | tidak ada pertanyaan berbasis urutan |
| Heap untuk top-k | O(n log k), streaming-friendly | hanya top k, bukan urutan penuh |
| Sort di tempat | O(1)–O(log n) ruang tambahan | ubah data pemanggil |
| Salinan `sorted()` | aman | O(n) ruang tambahan |

- ✅ Masalah interval/jadwal, ranking, masalah tetangga-penting, persiapan binary search.
- ✅ Saat data di-sort sekali dan di-query banyak kali.
- 🚫 Sekali cek keanggotaan (O(n) scan atau set kalahkan sort).
- 🚫 Kamu hanya butuh min/max atau beberapa item teratas → satu jalan atau heap.

## ⚠️ Kesalahan umum

- Sort daftar pemanggil di tempat tanpa sengaja.
- Campur aduk `reverse=True` dengan key dinegasi dan rusak urutan tie.
- Gabung interval tanpa sort dulu.
- Sort penuh untuk 3 teratas dari jutaan item.
- Maju `mid` setelah swap dengan `high` di algoritma Dutch flag (item di-swap belum dicek).

## 🏆 Praktik terbaik

- [ ] Pakai `sorted()`/`.sort()` dengan `key=` — jangan tulis fungsi perbandingan kecuali harus (`functools.cmp_to_key`).
- [ ] Jelaskan tie-breaking dan penanganan `None` sebelum code.
- [ ] Sebutkan stabilitas saat sort multi-key.
- [ ] Simpan index asli dengan `sorted(range(n), key=...)` atau `enumerate` saat butuh posisi.
- [ ] Lebih suka `heapq.nlargest/nsmallest` untuk k kecil; sebutkan O(n log k).
- [ ] Untuk interval, definisikan batas terbuka/tutup dengan jelas.
- [ ] Bisa jelaskan merge sort dan quicksort (dan kenapa terburuk quicksort terjadi).

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan merge sort ke teman pakai dua tumpukan ujian yang sudah terurut: bagaimana kamu gabung jadi satu tumpukan terurut dengan cepat, dan bagaimana ide itu sort tumpukan benar-benar berantakan?

## 📐 Rancang

CareerPilot menambah **penjadwalan interview**: perekrut terbitkan slot tersedia `[start, end)` dan kandidat terbitkan punya mereka. Untuk satu perekrut (sampai 2.000 slot) dan satu kandidat (sampai 2.000 slot), temukan semua rentang waktu sama minimal 45 menit. Rancang algoritma dan kompleksitas; lalu bilang apa berubah saat satu perekrut harus cocokkan 5.000 kandidat.

:::quiz
Lihat contoh rancangan

**Satu pasangan**: sort kedua daftar slot mulai (O(n log n + m log m)), **gabung** slot tumpang tindih dalam setiap daftar dulu (slot sendiri orang itu), lalu jalan kedua dengan **two pointer**:

```text
i, j = 0, 0
while i < len(A) and j < len(B):
    start = max(A[i].start, B[j].start)
    end = min(A[i].end, B[j].end)
    if end - start >= 45 min: output [start, end)
    if A[i].end < B[j].end: i += 1 else: j += 1     # maju yang berakhir lebih dulu
```

Total O(n log n + m log m) — jalan itu O(n + m).

**5.000 kandidat**: sort dan gabung slot perekrut sekali; untuk setiap kandidat ulang jalan two-pointer → O(R + C_k) per kandidat. Hitung dimuka dan simpan slot normal (terurut, digabung) di database sehingga setiap cocok hanya jalan linear; index tanggal sehingga hanya muat slot minggu relevan. Zona waktu: simpan UTC, ubah hanya tampil.
:::

### 📝 Checklist review mandiri

- [ ] Setiap daftar terurut dan self-overlap digabung dulu
- [ ] Aturan two-pointer maju dijustifikasi
- [ ] Cek durasi minimum dan batas half-open ditangani
- [ ] Scaling ke banyak kandidat hindari re-sort perekrut

::ai-review{task="design"}

::part[Soal Latihan]{n="3"}

:::problem{id="dsa-s3-sorting-basics" title="Dasar-Dasar Sorting" difficulty="easy" path="exercises/dsa/stage-3/17-sorting-basics"}
Ranking job multi-key dengan sort stabil, gabung interval, dan k-th largest dengan heap.
:::

:::problem{id="dsa-s3-interview-rooms" title="Ruangan Interview Dibutuhkan" difficulty="medium" path="exercises/dsa/stage-3/18-meeting-rooms"}
Sweep line atas mulai dan akhir terurut untuk temukan puncak konkuren.
:::

:::problem{id="dsa-s3-priority-partition" title="Sort Tugas by Priority dalam Satu Jalan" difficulty="medium" path="exercises/dsa/stage-3/19-three-way-partition"}
Algoritma Dutch national flag: partisi tiga-arah di tempat.
:::

:::problem{id="dsa-s3-count-inversions" title="Seberapa Beda Dua Ranking?" difficulty="hard" path="exercises/dsa/stage-3/20-count-inversions"}
Stretch: hitung inversi dalam O(n log n) dengan memperluas merge sort.
:::

:::hints
- `rank_jobs`: `key=lambda j: (j["salary_max"] is None, -(j["salary_max"] or 0))` tangani gaji; pakai stable sort sebelumnya untuk "tanggal terbaru dulu" di string.
- `merge_intervals`: `sorted(intervals)` sort mulai, lalu akhir.
- `rooms_needed`: proses `ends[e] <= start` sebelum ambil ruangan untuk `start`, karena ruangan bebas **di** waktu akhirnya.
- `sort_priorities`: saat swap `"low"` ke belakang, jangan maju `mid` — cek item yang di-swap dulu.
- `count_inversions`: merge sort bawah-atas (iteratif) hindari batas rekursi Python di input besar.
:::

## ✅ Cek cepat

:::quiz
Apa maksud "stable sort", dan kenapa penting untuk sort multi-key?

Item yang bandingkan sama tetap urutan relatif asli. Kamu bisa sort key sekunder dulu lalu key primer, dan tie di key primer tetap urut key sekunder.
:::

:::quiz
Kenapa heap lebih baik daripada sort untuk "top 5 dari 10 juta score"?

Heap ukuran 5 proses setiap score dalam O(log 5), jadi semua jalan O(n); sort semua O(n log n) dan harus urut item tidak akan pernah pakai.
:::


## 📚 Lanjut belajar

- [Dokumentasi Python: Sorting HOW TO (key, stabilitas)](https://docs.python.org/3/howto/sorting.html)
- [Dokumentasi Python: heapq](https://docs.python.org/3/library/heapq.html)
- [VisuAlgo — visualisasi sorting](https://visualgo.net/en/sorting)

## 📣 Stage 3 selesai — bagikan progresmu

:::linkedin{type="dsa"}
🧩 DSA Stage 3 selesai: pola-pola di balik mayoritas masalah interview coding.

- Two pointer → penjumlahan pasangan dan trik di tempat dalam O(n)
- Sliding window → rentang terpanjang/terpendek bersebelahan dalam O(n)
- Prefix sum → total rentang apa saja dalam O(1), bahkan angka negatif
- Binary search → bukan hanya array: "temukan kapasitas terkecil yang jalan"
- Sorting → interval, sweep line, dan top-k dengan heap

Yang mengejutkan aku: [contoh "binary search di jawaban — aku pakainya temukan berapa user API aku tangani sebelum p95 rusak"].

Cara aku sekarang: brute force dulu, kenali pola, lalu optimalkan — keras-keras.

#Algorithm #CodingInterview #Python #LearningInPublic
:::

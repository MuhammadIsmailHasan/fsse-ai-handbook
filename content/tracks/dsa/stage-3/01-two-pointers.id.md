---
title: "Dua Penunjuk"
summary: Jalan sebuah urutan dari kedua ujung (atau dua kecepatan) untuk mengganti nested loop — cek palindrom, jumlah pasangan di data terurut, merge, three-sum dan masalah air terperangkap.
sourceHash: 75b308661a2f
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Tiga bentuk pola dua-penunjuk: **ujung berlawanan**, **searah (baca/tulis)**, **dua urutan**
- Kenapa input terurut membuka pencarian pasangan O(n)
- Cara **membuktikan** bahwa menggerakkan penunjuk tidak pernah melewatkan jawaban
- Menangani duplikat tanpa set
- 🧭 Cara mengenali masalah dua-penunjuk

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Penunjuk** | Posisi yang sedang kamu lihat |
| **Ujung berlawanan** | Satu penunjuk di awal, satu di akhir, bergerak ke dalam |
| **Searah** | Kedua penunjuk maju, tapi kecepatan berbeda |
| **Penunjuk baca/tulis** | Satu membaca setiap item, satu menulis yang kamu simpan |
| **Input terurut** | Item dalam urutan — apa yang buat pola bekerja |
| **Singkirkan kemungkinan** | Setiap langkah menghapus banyak pasangan |
| **In-place** | Tanpa list tambahan |
| **Coba semua** | Coba setiap pasangan — O(n²) |

## 🧠 Ide besarnya

Dua orang mencari di rak buku terurut untuk dua buku yang jumlah halamannya tepat 1.000. Satu mulai dari buku paling tipis, satu dari paling tebal. Terlalu banyak halaman? Orang di ujung tebal bergerak ke dalam. Terlalu sedikit? Orang di ujung tipis bergerak ke dalam. Mereka tidak pernah perlu coba setiap pasangan — setiap langkah **menghapus** banyak pasangan.

Itulah seluruh pola: **setiap gerak penunjuk menghapus kemungkinan**, jadi n langkah mengganti n² perbandingan.

## ❓ Kenapa ini penting

Cek setiap pasangan adalah O(n²): 100.000 item berarti 5 miliar pasangan. Saat data punya **urutan** — nilai terurut, atau dua ujung yang bisa kamu jalan menuju — dua penunjuk pakai urutan itu untuk jawab pertanyaan pasangan dan partisi dalam O(n), tanpa memori tambahan. Hash map juga dapat O(n) waktu di sini, tapi butuh O(n) memori; dua penunjuk butuh tidak.

Ini salah satu pola tertinggi nilainya di interview, karena versi brute-force sangat mudah ditulis tanpa sengaja.

## 📖 Cara kerjanya, langkah demi langkah

### 1. Bentuk A — ujung berlawanan

```python
left, right = 0, len(nums) - 1
while left < right:
    total = nums[left] + nums[right]
    if total == target:
        return left, right
    if total < target:
        left += 1          # need bigger: only moving left can increase the sum
    else:
        right -= 1         # need smaller: only moving right can decrease it
```

**Kenapa aman** (bilang ini di interview): jika `nums[left] + nums[right] > target`, maka `nums[right]` ditambah **setiap** sisa nilai left juga terlalu besar (semuanya ≥ `nums[left]`). Jadi `right` tidak bisa jadi solusi — buang.

Juga bekerja untuk: palindrom (banding ujung, bergerak ke dalam), reverse in place, container-with-most-water.

### 2. Bentuk B — searah (baca/tulis atau cepat/lambat)

```python
write = 0
for read in range(len(nums)):
    if keep(nums[read]):
        nums[write] = nums[read]
        write += 1
```

`read` jelajahi, `write` tandai di mana item yang disimpan berikutnya. Dipakai untuk hapus duplikat dari array terurut, pindah nol (Stage 2), susutkan data in-place. Linked-list pointer cepat/lambat adalah keluarga yang sama.

### 3. Bentuk C — dua urutan

```python
i = j = 0
while i < len(a) and j < len(b):
    if a[i] <= b[j]:
        merged.append(a[i]); i += 1
    else:
        merged.append(b[j]); j += 1
merged += a[i:] + b[j:]
```

Merge list terurut (jantung merge sort), irisan list terurut, bandingkan versi.

### 4. Sortir dulu, lalu dua penunjuk

Sortir biaya O(n log n) — sering-sering layak bayar, karena sesudah itu setiap langkah bisa hapus seluruh grup pasangan, bukan hanya satu.

Saat input tidak terurut, sortir biaya O(n log n) — sering-sering jauh lebih baik dari O(n²):

**Three-sum**: sortir, tetapkan nomor pertama `nums[i]`, lalu jalankan penunjuk berlawanan di sisanya untuk `-nums[i]`. O(n²) bukan O(n³).

Duplikat: lewati tetangga sama **setelah sortir** bukan simpan hasil di set:

```python
if i > 0 and nums[i] == nums[i - 1]:
    continue
```

### 5. Gerakkan sisi "pembatas"

Aturannya: gerakkan penunjuk yang menahan kamu. Sisi lain hanya buat lebih buruk, jadi lewatkan tidak hilang apa-apa.

Di masalah seperti banner terbesar atau air terperangkap, sisi **lebih pendek** batasi hasil. Gerakkan sisi lebih tinggi hanya susutkan lebar tanpa naikkan batas, jadi selalu gerakkan sisi lebih pendek. Air terperangkap perpanjang ini: sisi dengan maksimum berjalan lebih kecil sudah tahu tingkat airnya.

:::tip[🧭 Cara kenal masalah dua penunjuk]
- Input **terurut** (atau sortir tidak rusak pertanyaan) dan kamu butuh **pasangan/triplet** dengan jumlah atau beda tertentu.
- Kamu bandingkan atau tukar item dari **kedua ujung**: palindrom, reverse, masalah "wadah".
- Kamu harus ubah array **in-place** dengan O(1) ruang tambahan: hapus, susutkan, partisi.
- Kamu **merge atau bandingkan dua urutan terurut**.
- Brute force punya nested loop atas `i < j` dan gerakkan satu index jelas hapus pilihan.

Tidak terurut dan urutan penting (kamu butuh indeks asli, sortir dilarang)? Pikir **hash map** sebagai gantinya.
:::

### Pilih setup-mu

Setiap pilihan di sini adalah trade-off:

| Pendekatan untuk "pasangan dengan jumlah" | Waktu | Ruang tambahan | Butuh terurut? |
|---|---|---|---|
| Coba semua | O(n²) | O(1) | tidak |
| Hash map (Stage 1) | O(n) | O(n) | tidak |
| Sortir + dua penunjuk | O(n log n) | O(1)–O(n) untuk sortir | sortir (hilang indeks asli) |
| Sudah terurut + dua penunjuk | **O(n)** | **O(1)** | ya |

- ✅ Data terurut, target pasangan/triplet, susutkan in-place, cek simetri, merge.
- 🚫 Data tidak terurut saat kamu harus kembalikan **indeks asli** → hash map.
- 🚫 Subarray bersebelahan dengan kondisi atas rentang → biasanya **sliding window** (materi berikutnya) atau **prefix sums**.

## ⚠️ Kesalahan umum

- Pakai dua penunjuk di data **tidak terurut** untuk jumlah pasangan.
- Loop tak akhir: cabang yang gerakkan tanpa penunjuk.
- Kembalikan awal di three-sum dan lewat triplet lain, atau lewat duplikat di waktu salah.
- Off-by-one: `while left <= right` biarkan item pasang dengan dirinya.

## 🏆 Praktik terbaik

- [ ] Mulai tanya: *apa terurut? boleh sortir? butuh indeks asli?*
- [ ] Nama penunjuk berdasar peran: `left/right`, `read/write`, `i/j` cuma untuk dua urutan.
- [ ] Sebelum kode, nyatakan **invariant** dan kenapa setiap gerak tidak bisa lewat jawaban sah.
- [ ] Putuskan kondisi loop dengan sengaja: `left < right` (pasangan item berbeda) vs `left <= right`.
- [ ] Tangani duplikat lewat tetangga sama setelah sortir.
- [ ] Jangan ubah list pemanggil saat sortir kecuali diizinkan — `sorted(nums)` buat salinan.
- [ ] Tes: kosong, satu elemen, semua sama, tanpa jawab, jawab di ujung.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke seseorang bukan programmer kenapa cek sebuah kata palindrom dengan bandingkan huruf pertama dan akhir, lalu bergerak ke dalam, lebih cepat dari buat kata terbalik — dan kenapa pakai memori lebih sedikit.

## 📐 Rancang

CareerPilot punya dua daftar ID pekerjaan, masing-masing **terurut** dan sampai 5 juta ID: pekerjaan yang **disimpan** pengguna dan pekerjaan yang **ditutup** hari ini. Rancang cara cari pekerjaan disimpan yang ditutup, tanpa muat kedua daftar ke dalam set. Nyatakan waktu dan memori.

:::quiz
Lihat rancangan mungkin

**Irisan dua-penunjuk** atas dua aliran terurut:

```text
i, j = 0, 0
while i < len(saved) and j < len(closed):
    if saved[i] == closed[j]: output saved[i]; i += 1; j += 1
    elif saved[i] < closed[j]: i += 1
    else: j += 1
```

- Waktu **O(n + m)** — setiap langkah maju setidaknya satu penunjuk.
- Memori **O(1)** tambahan — dan jika ID datang dari file atau database cursor terurut ID, kamu tidak pernah butuh kedua daftar di memori sekaligus (stream mereka).
- Pendekatan set juga O(n + m) waktu tapi butuh memori untuk 5 juta ID (ratusan MB di Python).
- Ini persis cara database buat **merge join** saat kedua input terurut oleh kunci join.
:::

### 📝 Checklist review mandiri

- [ ] Pakai ketertarurutan untuk maju sisi lebih kecil
- [ ] Setiap iterasi loop gerakkan penunjuk
- [ ] Keuntungan memori atas set dijelaskan

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::problem{id="dsa-s3-two-pointer-basics" title="Dasar Dua Penunjuk" difficulty="easy" path="exercises/dsa/stage-3/01-two-pointer-basics"}
Cek palindrom tanpa salin teks, indeks pasangan di daftar terurut, dan merge dua daftar terurut.
:::

:::problem{id="dsa-s3-three-sum" title="Tiga Anggaran Seimbang" difficulty="medium" path="exercises/dsa/stage-3/02-three-sum"}
Semua triplet unik jumlah ke nol: sortir, tetapkan satu, dua penunjuk untuk sisanya, lewat duplikat.
:::

:::problem{id="dsa-s3-biggest-banner" title="Frame Billboard Terbesar" difficulty="medium" path="exercises/dsa/stage-3/03-container-most-water"}
Maksimalkan lebar × tinggi lebih pendek dengan selalu gerakkan sisi pembatas.
:::

:::problem{id="dsa-s3-rainwater" title="Air di Langit-Langit" difficulty="hard" path="exercises/dsa/stage-3/04-trapping-rain-water"}
Perpanjang: air terperangkap dalam O(n) waktu dan O(1) ruang dengan dua penunjuk dan maksimum berjalan.
:::

:::hints
- `is_clean_palindrome`: lewat non-alphanumeric pada setiap sisi **sebelum** bandingkan.
- `pair_indices`: saat jumlah terlalu besar, gerakkan `right` — itu simpan `left` sah terkecil.
- `three_sum_zero`: setelah catat triplet, gerakkan kedua penunjuk dan lewat nilai `left` diulang.
- `max_banner_area`: hitung luas dulu, lalu gerakkan sisi mana pun yang lebih pendek.
- `trapped_water`: jika `heights[left] <= heights[right]`, air sisi kiri hanya bergantung `left_max`.
:::

## ✅ Cek cepat

:::quiz
Di loop pasangan-jumlah terurut, kenapa aman kurangkan `right` saat jumlah terlalu besar?

Setiap sisa nilai kiri setidaknya `nums[left]`, jadi `nums[right]` ditambah setiap satu masih terlalu besar — `nums[right]` tidak bisa dalam pasangan sah.
:::

:::quiz
Three-sum dengan sortir dan dua penunjuk adalah O(n²). Di mana setiap faktor berasal?

Loop luar tetapkan nomor pertama (n pilihan), dan untuk setiap satu scan dua-penunjuk adalah O(n). Sortir O(n log n) lebih kecil.
:::


## 📚 Lanjut belajar

- [Dokumentasi Python: Sorting HOW TO](https://docs.python.org/3/howto/sorting.html)
- [Dokumentasi PostgreSQL: Merge join dan jenis rencana lain (EXPLAIN)](https://www.postgresql.org/docs/current/using-explain.html)

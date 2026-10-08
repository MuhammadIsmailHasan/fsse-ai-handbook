---
title: "Heaps & Priority Queues"
summary: "Selalu dapatkan item terkecil (atau terbesar) dengan cepat — bagaimana heap hidup di list biasa, sift up dan sift down, heapq Python, dan pola yang dibukanya: top-k, menggabungkan input terurut, scheduler, dan median berjalan."
sourceHash: 47a42f594ec2
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa itu **heap** dan **priority queue**
- Bagaimana heap muat di **list biasa**, dan bagaimana **sift up / sift down** menjaganya benar
- **`heapq`** Python: `heappush`, `heappop`, `heapify`, `nsmallest`
- Empat pola: **top-k**, **menggabungkan k input terurut**, **scheduler**, **median berjalan**
- Kapan heap alat yang tepat, dan kapan bukan
- 🧭 Cara mengenali soal heap

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Heap** | Pohon yang setiap induknya lebih kecil (atau lebih besar) dari anak-anaknya |
| **Priority queue** | Antrean yang item terpenting selalu maju lebih dulu |
| **Min-heap / max-heap** | Item terkecil / terbesar ada di atas |
| **Sift up** | Menaikkan item baru sampai induknya lebih kecil |
| **Sift down** | Menurunkan item dengan menukar ke anak yang lebih kecil |
| **Heapify** | Mengubah seluruh list menjadi heap dalam O(n) |
| **Top-k** | k item terbaik dari banyak item |

## 🧠 Ide besarnya

Heap itu **antrean IGD rumah sakit**. Orang tidak keluar sesuai urutan datang. Pasien yang paling gawat selalu ditangani berikutnya. Orang baru datang, dan perawat menaruhnya di tempat yang tepat dalam antrean. Saat dokter kosong, yang paling gawat dipanggil. Tak ada yang perlu mengurutkan *seluruh* antrean. Kamu hanya perlu tahu siapa yang **berikutnya**.

Itulah inti heap. List terurut menjaga semuanya berurutan, yang lebih banyak kerja daripada yang kamu butuhkan. Heap hanya menjaga urutan secukupnya untuk memberimu item terbaik dengan cepat: O(1) untuk melihat, O(log n) untuk menambah atau menghapus.

## ❓ Kenapa ini penting

"Beri aku yang terbaik, sekarang, sementara item baru terus datang" ada di mana-mana:

- **antrean job dan scheduler** (tugas berikutnya menurut prioritas atau waktu),
- **top-k**: 10 produk terpopuler, 5 request paling lambat,
- **menggabungkan** log terurut dari banyak server menjadi satu garis waktu,
- algoritma **jalur terpendek** seperti Dijkstra (algoritma graph yang terkenal),
- **timer dan rate limiter** (timeout berikutnya yang harus menyala),
- **median berjalan** dari metrik langsung.

Mengurutkan semuanya setiap kali berbiaya O(n log n). Heap hanya membayar O(log n) per perubahan.

## 📖 Langkah demi langkah

### 1. Pohon yang disimpan di list

Heap adalah pohon biner yang **setiap induknya ≤ kedua anaknya** (min-heap). Ia juga *lengkap* (terisi baris demi baris, kiri ke kanan), jadi muat di list tanpa objek node:

```text
index:   0  1  2  3  4  5
items: [ 1, 3, 2, 7, 4, 5 ]          1
                                    / \
parent of i = (i - 1) // 2         3   2
children    = 2i + 1, 2i + 2      / \  /
                                 7  4 5
```

Catatan: ia **tidak terurut**. 3 datang sebelum 2. Satu-satunya janji adalah "induk menang", jadi `items[0]` selalu yang terkecil.

### 2. Push: sift up

Tambahkan item baru di ujung, lalu naikkan selama ia lebih kecil dari induknya.

```python
def push(self, value):
    items = self.items
    items.append(value)
    i = len(items) - 1
    while i > 0:
        parent = (i - 1) // 2
        if items[parent] <= items[i]:
            break
        items[parent], items[i] = items[i], items[parent]
        i = parent
```

Pohon punya sekitar log₂ n tingkat, jadi ini **O(log n)**.

### 3. Pop: sift down

Yang terkecil adalah `items[0]`. Ambil, pindahkan item **terakhir** ke puncak, lalu turunkan, selalu menukar dengan anak yang **lebih kecil**.

```python
def pop(self):
    items = self.items
    smallest = items[0]
    last = items.pop()
    if items:
        items[0] = last
        i, n = 0, len(items)
        while True:
            left, right, small = 2 * i + 1, 2 * i + 2, i
            if left < n and items[left] < items[small]:
                small = left
            if right < n and items[right] < items[small]:
                small = right
            if small == i:
                break
            items[i], items[small] = items[small], items[i]
            i = small
    return smallest
```

Juga **O(log n)**. Kenapa menukar dengan anak yang *lebih kecil*? Supaya induk baru tetap lebih kecil dari anak yang lain.

### 4. Pakai `heapq` di kode nyata

Python memberimu min-heap di list biasa:

```python
import heapq

heap = []
heapq.heappush(heap, 5)
heapq.heappush(heap, 1)
heapq.heappush(heap, 3)
heap[0]                    # 1   (peek)
heapq.heappop(heap)        # 1

numbers = [5, 1, 3, 9, 2]
heapq.heapify(numbers)     # O(n), in place
heapq.nsmallest(2, numbers)   # [1, 2]
heapq.nlargest(2, numbers)    # [9, 5]
```

**Butuh max-heap?** Push yang **negatif** (`-x`) dan negasikan lagi saat pop. **Butuh urutan berdasarkan hal lain?** Push tuple: `(priority, item)`. Tuple dibandingkan dari kiri ke kanan, jadi tambahkan pemecah seri (sebuah indeks) bila item tak bisa dibandingkan.

### 5. Pola: top-k

Simpan **min-heap berukuran k**. Ia berisi k terbaik sejauh ini, dan puncaknya adalah yang terlemah di antaranya, yang harus dikalahkan.

```python
def k_largest(nums, k):
    heap = []
    for n in nums:
        if len(heap) < k:
            heapq.heappush(heap, n)
        elif n > heap[0]:
            heapq.heapreplace(heap, n)       # pop the smallest and push n, in one step
    return sorted(heap, reverse=True)
```

Waktu **O(n log k)** dan ruang **O(k)**. Untuk "10 teratas dari 300.000" ini mengalahkan mengurutkan semuanya. Ia juga bekerja pada **stream** yang tak muat di memori. (Untuk k-th terbesar dari stream, puncak heap ini *adalah* jawabannya.)

### 6. Pola: menggabungkan k input terurut

Taruh **item terdepan dari tiap input** di heap. Yang terkecil adalah keluaran berikutnya. Lalu push item berikutnya dari input yang sama.

```python
def merge_k_sorted(lists):
    heap = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]
    heapq.heapify(heap)
    out = []
    while heap:
        value, i, j = heapq.heappop(heap)
        out.append(value)
        if j + 1 < len(lists[i]):
            heapq.heappush(heap, (lists[i][j + 1], i, j + 1))
    return out
```

Waktu **O(N log k)** untuk N item di k input. Heap tak pernah menyimpan lebih dari k item, jadi ia juga bekerja untuk file log yang terlalu besar untuk memori. Ide yang sama memberi *k jumlah pasangan terkecil*.

### 7. Pola: scheduler

Heap berisi `(waktu, tugas)` selalu memberi tahu **hal berikutnya yang dikerjakan**: timer berikutnya, retry berikutnya, job berprioritas tertinggi. Pop, jalankan, dan push tindak lanjutnya. Soal ruang rapat dan penjadwalan CPU memakai heap **waktu selesai** untuk melihat ruang mana yang bebas lebih dulu.

### 8. Pola: median berjalan (dua heap)

Pisahkan angka menjadi **max-heap untuk separuh yang lebih kecil** dan **min-heap untuk separuh yang lebih besar**, dengan ukuran dijaga sama (atau satu lebih besar). Median ada di puncak-puncaknya.

```text
smaller half (max-heap) | larger half (min-heap)
        [1, 2, 3]       |       [5, 8, 9]          median = (3 + 5) / 2
```

`add` O(log n), `median` O(1). Mengurutkan setiap ada angka baru jauh lebih lambat.

### 9. Greedy dengan heap

"Selalu ambil pilihan termurah sekarang" sering berupa heap. Menyambung tali dengan total biaya terendah: selalu sambung **dua tali terpendek**, kembalikan hasilnya, ulangi. Beginilah kompresi Huffman membangun kodenya.

### 10. Biaya, dan apa yang tak bisa dilakukan heap

| Operasi | Waktu |
|---|---|
| Lihat terkecil | O(1) |
| Push / pop | O(log n) |
| Bangun dari list (`heapify`) | O(n) |
| Top-k dari n item | O(n log k) |
| Mencari nilai tertentu | **O(n)** — heap bukan untuk pencarian |
| Mendapat semuanya terurut | O(n log n) |

Heap **tidak** menjaga semua item terurut, dan tak bisa menemukan atau menghapus item sembarang dengan cepat. Kalau butuh "berikutnya yang lebih besar dari x" atau rentang, pakai BST. Kalau butuh pencarian dengan key, pakai hash map.

:::tip[🧭 Cara mengenali soal heap]
- Kata-kata seperti **k-th terbesar/terkecil, top k, paling sering, k terdekat**.
- "**Selalu yang terkecil/terawal/berprioritas tertinggi berikutnya**" sementara data terus berubah.
- **Menggabungkan** beberapa list, log, atau stream terurut.
- **Median** atau statistik berjalan lain dari sebuah stream.
- Pilihan **greedy**: "ambil yang termurah/terpendek/terawal dulu".

Butuh *semua* item terurut sekali saja? Cukup sort. Butuh pencarian, atau rentang? Hash map atau BST.
:::

### Memilih caranya

| Kebutuhan | Pakai |
|---|---|
| Hanya item terbaik, berulang kali | heap |
| Top k dari input besar atau tak berujung | min-heap berukuran k |
| Menggabungkan k input terurut | heap berisi item terdepan |
| Semuanya terurut, sekali | `sorted()` |
| Pencarian dengan key | hash map |
| Berikutnya yang lebih besar dari x, rentang | BST / sorted container |
| Max-heap di Python | push nilai negatif |

- ✅ Scheduler, top-k, penggabungan, statistik berjalan, algoritma ala Dijkstra.
- 🚫 Mencari sebuah nilai, atau butuh seluruh koleksi berurutan.
- 🚫 List kecil yang `min()` atau `sorted()` lebih sederhana dan cukup cepat.

## ⚠️ Kesalahan umum

- Mengira heap itu terurut (hanya `items[0]` yang dijamin).
- Max-heap tak sengaja: `heapq` selalu min-heap. Push `-x` untuk max-heap.
- Mem-push objek yang tak bisa dibandingkan, sehingga seri membuat crash. Tambahkan indeks sebagai pemecah seri.
- Memakai heap berukuran n untuk top-k (O(n log n)). Jaga ukurannya **k**.
- Memakai `heap[1]` sebagai terkecil kedua. Itu tak dijamin.
- Mencari atau menghapus nilai di tengah heap.

## 🏆 Praktik terbaik

- [ ] Tanyakan: "apakah aku butuh semuanya terurut, atau hanya item terbaik berikutnya?"
- [ ] Untuk top-k, simpan heap berukuran k dan bandingkan dengan `heap[0]`.
- [ ] Bungkus item sebagai `(priority, tie_breaker, item)` saat prioritas bisa sama.
- [ ] Sebut biayanya: O(log n) per push/pop, O(n) untuk heapify, O(n log k) untuk top-k.
- [ ] Pakai `heapq` di kode nyata; pahami cara kerja sift up dan sift down untuk wawancara.
- [ ] Sebut kapan list terurut, hash map atau BST lebih cocok.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke teman kenapa antrean IGD rumah sakit gambaran heap yang lebih baik daripada list terurut. Apa yang *tidak* perlu diketahui perawat?

## 📐 Rancang

CareerPilot mengirim pengingat: "tindak lanjuti lamaran ini dalam 5 hari". Ribuan pengingat punya waktu jatuh tempo berbeda, dan user menambah dan membatalkannya terus. Sebuah worker harus bangun, mengirim setiap pengingat yang sudah jatuh tempo, lalu tidur sampai yang berikutnya. Rancang struktur datanya dan loop worker. Katakan bagaimana menangani pembatalan, dan apa yang berubah saat ada beberapa worker.

:::quiz
Tampilkan rancangan yang mungkin

- **Min-heap dengan key waktu jatuh tempo:** entri `(due_time, reminder_id)`. Push O(log n). Puncaknya selalu **pengingat berikutnya yang dikirim**.
- **Loop worker:** lihat puncak. Jika `due_time <= now`, pop dan kirim; ulangi. Jika belum, **tidur sampai `due_time`** (atau sampai ada pengingat baru yang lebih awal) alih-alih polling tiap detik.
- **Pembatalan:** heap tak bisa menghapus dari tengah dengan cepat. Pakai **lazy deletion**: simpan set id yang dibatalkan; saat pop yang dibatalkan, lewati. Heap dibersihkan seiring jalan.
- **Mengubah waktu jatuh tempo:** push entri baru dan tandai yang lama tidak valid (trik yang sama).
- **Banyak worker / restart:** heap di memori hilang saat restart dan tidak dibagi. Simpan pengingat di database (indeks pada `due_time`) atau antrean dengan pengiriman tertunda; worker mengambil "yang berikutnya jatuh tempo" dengan `SELECT ... WHERE due_time <= now() ORDER BY due_time FOR UPDATE SKIP LOCKED`. Idenya tetap "beri aku yang paling awal".
- **Seri:** tambahkan id pengingat sebagai pemecah seri agar dua entri dengan waktu sama tak membandingkan payload-nya.
- **Biaya:** push/pop O(log n); satu timer tidur sebagai ganti busy loop.

**Aturan yang ditunjukkan:** heap menjawab "apa yang berikutnya?" dengan murah saat item datang dan pergi; penghapusan ditangani secara lazy.
:::

### 📝 Daftar cek diri

- [ ] Aku menjelaskan kenapa heap, bukan list terurut atau scan
- [ ] Worker tidur sampai waktu jatuh tempo berikutnya, bukan polling
- [ ] Pembatalan ditangani (lazy deletion atau database)
- [ ] Restart dan beberapa worker dipertimbangkan

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::problem{id="dsa-s4-heap-basics" title="Build a Min-Heap" difficulty="easy" path="exercises/dsa/stage-4/09-heap-basics"}
Tulis push (sift up), pop (sift down), peek dan heap sort di list biasa — tanpa `heapq`.
:::

:::problem{id="dsa-s4-top-k" title="Top K with a Heap" difficulty="medium" path="exercises/dsa/stage-4/10-top-k"}
k nilai terbesar, k kata paling sering, dan k-th terbesar dari stream, dalam O(n log k).
:::

:::problem{id="dsa-s4-merge-k-sorted" title="Merge Sorted Inputs with a Heap" difficulty="medium" path="exercises/dsa/stage-4/11-merge-k-sorted"}
Gabungkan k list terurut, gabungkan stream tak berujung secara lazy, dan temukan k jumlah pasangan terkecil.
:::

:::problem{id="dsa-s4-median-and-ropes" title="Running Median & Joining Ropes" difficulty="hard" path="exercises/dsa/stage-4/12-median-and-ropes"}
Stretch: median dari himpunan yang tumbuh dengan dua heap, dan cara termurah menyambung tali.
:::

:::hints
- Indeks heap: induk `(i - 1) // 2`, anak `2*i + 1` dan `2*i + 2`.
- Sift down: pilih anak yang **lebih kecil**, dan berhenti saat tak ada anak yang lebih kecil dari item.
- Top-k: `if len(heap) < k: heappush`, selain itu `if n > heap[0]: heapreplace(heap, n)`.
- Paling sering dengan seri: key `(-count, word)` agar hitungan lebih besar menang lalu kata yang lebih kecil.
- Merge: push tuple `(value, list_index, position)`; setelah pop, push item berikutnya dari list yang **sama**.
- Merge lazy: setelah yield sebuah nilai, baca **satu** item dari stream yang sama dan `heapreplace`, atau `heappop` saat stream habis.
- Jumlah pasangan terkecil: mulai dengan `(a[0] + b[0], 0, 0)`; setelah pop `(i, j)` push `(i, j + 1)`, dan push `(i + 1, 0)` hanya saat `j == 0`.
- Median: tambahkan ke max-heap (dinegasikan), pindahkan puncaknya ke min-heap, dan jika min-heap lebih besar pindahkan puncaknya kembali.
- Tali: pop dua, tambahkan ke total, push jumlahnya kembali.
:::

## ✅ Cek cepat

:::quiz
Kenapa heap lebih cepat daripada sort saat kamu hanya butuh 10 teratas dari 300.000 item?

Min-heap berukuran 10 menyentuh tiap item sekali dan berbiaya O(log 10) per item yang perlu masuk heap: total O(n log k), dengan hanya 10 item di memori. Mengurutkan semuanya berbiaya O(n log n) dan menyimpan semua item, padahal kamu hanya mau 10.
:::

:::quiz
Apakah heap itu list terurut? Apa yang dijamin?

Bukan. Yang dijamin hanya aturan heap: setiap induk kurang dari atau sama dengan anak-anaknya (untuk min-heap), jadi item terkecil ada di indeks 0. Item lain hanya terurut sebagian. Untuk hasil terurut kamu pop berulang kali.
:::

:::quiz
`heapq` adalah min-heap. Bagaimana mendapatkan item terbesar lebih dulu?

Push negatif dari tiap angka (`-x`) dan negasikan lagi setelah pop. Untuk tuple, negasikan bagian prioritasnya. Angka negatif terkecil adalah angka asli terbesar.
:::

## 📚 Lanjut belajar

- [Python docs: heapq](https://docs.python.org/3/library/heapq.html)
- [VisuAlgo: Binary heap (interactive)](https://visualgo.net/en/heap)
- [Wikipedia: Priority queue](https://en.wikipedia.org/wiki/Priority_queue)

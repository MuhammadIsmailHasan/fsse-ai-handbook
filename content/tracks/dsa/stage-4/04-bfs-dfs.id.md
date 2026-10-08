---
title: "Graphs: BFS & DFS"
summary: "Modelkan sesuatu sebagai graf (bahkan grid), ingat apa yang sudah dikunjungi, lalu jelajahi dengan queue (BFS, jalur terpendek) atau stack (DFS, pulau dan flood fill) — plus multi-source BFS dan kebiasaan menghindari rekursi yang dalam."
sourceHash: 8b41f5a88347
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa itu **graf**, dan cara menyimpannya sebagai **adjacency list**
- Kenapa kamu butuh set **visited** (siklus!)
- **BFS** dengan queue dan **DFS** dengan stack, dan apa bedanya
- BFS untuk **jalur terpendek** saat setiap langkah berbiaya sama
- Memperlakukan **grid** sebagai graf (pulau, flood fill, labirin)
- **Multi-source BFS**, dan kenapa menghindari rekursi yang dalam
- 🧭 Cara mengenali soal graf

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Graf** | Simpul-simpul yang dihubungkan oleh sisi |
| **Simpul (node/vertex)** | Satu hal: orang, halaman, kota |
| **Sisi (edge)** | Hubungan antara dua simpul |
| **Berarah / tak berarah** | Sisi satu arah / sisi dua arah |
| **Tetangga (neighbour)** | Simpul yang bisa dicapai dengan satu sisi |
| **Visited** | Simpul yang sudah kamu lihat, supaya tidak berputar |
| **BFS** | Jelajahi simpul terdekat dulu, memakai queue |
| **DFS** | Masuk sedalam mungkin dulu, memakai stack |

## 🧠 Ide besarnya

Graf adalah **peta kota**: tempat (simpul) dan jalan (sisi). Pohon adalah kota dengan hanya satu jalan ke tiap tempat. Graf bisa punya putaran, sehingga kamu bisa berjalan berputar-putar selamanya. Obatnya kebiasaan sederhana: **tandai setiap tempat yang sudah kamu kunjungi**.

Sekarang dua cara menjelajah dari rumahmu:

- **BFS** adalah **riak di kolam**. Kamu mengunjungi semua yang berjarak 1 jalan, lalu semua yang berjarak 2 jalan, lalu 3. Saat pertama kali tiba di suatu tempat, kamu memakai jalan paling sedikit. Kamu butuh **queue**: siapa datang dulu, dilayani dulu.
- **DFS** adalah **berjalan di labirin dengan gulungan benang**. Kamu mengikuti satu jalan sejauh ia pergi, dan baru saat buntu kamu kembali ke persimpangan terakhir. Kamu butuh **stack**: terakhir masuk, pertama keluar (atau rekursi, yang merupakan stack tersembunyi).

## ❓ Kenapa ini penting

Graf ada di mana-mana, begitu kamu mulai memperhatikan:

- **jejaring sosial** (teman dari teman), **tautan web** (crawler),
- **peta dan rute**, **koneksi penerbangan**,
- **dependensi** antar paket, tugas dan tabel database,
- **papan permainan**, **foto** (piksel), **labirin**, **denah kantor**,
- **Kubernetes, microservice, dan Terraform** semuanya menggambar graf dependensi.

BFS dan DFS adalah dua gerakan dasar di balik hampir semua algoritma graf. Pewawancara menyukainya karena idenya kecil, dan jebakannya (tanpa set visited, rekursi terlalu dalam) mudah terlihat.

## 📖 Langkah demi langkah

### 1. Simpan graf sebagai adjacency list

Sebuah dictionary: tiap simpul dipetakan ke list tetangganya.

```python
def build_graph(edges, directed=False):
    sets = {}
    for a, b in edges:
        sets.setdefault(a, set()).add(b)
        sets.setdefault(b, set())
        if not directed:
            sets[b].add(a)              # undirected: the road goes both ways
    return {node: sorted(neighbours) for node, neighbours in sets.items()}
```

```text
edges: (1,2) (1,3) (2,4) (3,4) (4,5)

        1
       / \          graph = {1: [2, 3], 2: [1, 4], 3: [1, 4], 4: [2, 3, 5], 5: [4]}
      2   3
       \ /
        4 — 5
```

Untuk `n` simpul dan `m` sisi, list ini memakai ruang O(n + m). Alternatifnya adalah **matriks** adjacency (n × n), yang memboroskan ruang kecuali grafnya sangat padat.

### 2. BFS: queue dan set visited

```python
from collections import deque

def bfs_order(graph, start):
    seen, order, queue = {start}, [], deque([start])
    while queue:
        node = queue.popleft()
        order.append(node)
        for nxt in graph.get(node, []):
            if nxt not in seen:
                seen.add(nxt)             # mark when you ADD it, not when you pop it
                queue.append(nxt)
    return order
```

Menandai simpul sebagai seen **saat memasukkannya ke queue** mencegah satu simpul masuk dua kali. Waktunya **O(V + E)**: setiap simpul dan setiap sisi dilihat sekali.

### 3. DFS: stack (tanpa rekursi)

```python
def dfs_order(graph, start):
    seen, order, stack = set(), [], [start]
    while stack:
        node = stack.pop()
        if node in seen:
            continue
        seen.add(node)
        order.append(node)
        for nxt in reversed(graph.get(node, [])):   # reversed, so the smallest is visited first
            if nxt not in seen:
                stack.append(nxt)
    return order
```

Ini kode yang *sama* dengan BFS dengan queue diganti stack. Versi rekursifnya lebih pendek, tapi Python hanya mengizinkan sekitar 1.000 panggilan bersarang, jadi jalur 50.000 simpul membuatnya crash. Pilih stack bila graf bisa dalam.

```python
def dfs_recursive(graph, node, seen):    # short, fine for small or shallow graphs
    seen.add(node)
    for nxt in graph[node]:
        if nxt not in seen:
            dfs_recursive(graph, nxt, seen)
```

### 4. BFS memberi jalur terpendek

Saat setiap sisi berbiaya sama (satu lompatan, satu langkah), saat pertama BFS mencapai sebuah simpul itulah **langkah paling sedikit**. Catat jarak saat pertama melihat simpul, dan induknya bila kamu butuh jalurnya.

```python
def distances_from(graph, start):
    dist, queue = {start: 0}, deque([start])
    while queue:
        node = queue.popleft()
        for nxt in graph.get(node, []):
            if nxt not in dist:                 # "not in dist" is the visited check
                dist[nxt] = dist[node] + 1
                queue.append(nxt)
    return dist
```

Untuk mendapat jalurnya, simpan `parent[nxt] = node`, lalu telusuri mundur dari tujuan ke awal. DFS **tidak** memberi jalur terpendek.

Banyak teka-teki adalah soal jalur terpendek yang menyamar. **Word ladder** ("hit" → "hot" → "dot" → "dog" → "cog") memakai kata sebagai simpul dan perubahan satu huruf sebagai sisi.

### 5. Grid adalah graf

Peta, foto, atau papan permainan: tiap sel adalah simpul, dan tetangganya adalah atas, bawah, kiri dan kanan. Kamu tak membangun grafnya. Kamu menghitung tetangganya:

```python
for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
    nr, nc = r + dr, c + dc
    if 0 <= nr < rows and 0 <= nc < cols:      # stay inside the grid
        ...
```

**Menghitung pulau:** untuk setiap sel daratan yang belum dilihat, tambah 1 dan banjiri seluruh pulaunya dengan stack.

```python
def count_islands(grid):
    rows, cols = len(grid), len(grid[0]) if grid else 0
    seen, islands = set(), 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == "1" and (r, c) not in seen:
                islands += 1
                seen.add((r, c))
                stack = [(r, c)]
                while stack:
                    x, y = stack.pop()
                    for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                        if 0 <= nx < rows and 0 <= ny < cols and grid[nx][ny] == "1" and (nx, ny) not in seen:
                            seen.add((nx, ny))
                            stack.append((nx, ny))
    return islands
```

Banjir yang sama adalah **ember cat** di editor gambar (flood fill), dan ia mengukur **luas** pulau terbesar.

### 6. Multi-source BFS

Bagaimana jika banyak sel bisa menjadi titik awal: setiap jeruk busuk, setiap `0` di matriks, setiap api di hutan? Masukkan **semuanya ke queue di awal**. Satu BFS lalu memberi tiap sel jaraknya ke sumber *terdekat*.

```python
queue = deque((r, c) for r in range(rows) for c in range(cols) if grid[r][c] == 2)
minutes = 0
while queue and fresh:
    for _ in range(len(queue)):          # one whole round = one minute
        ...
    minutes += 1
```

Menjalankan BFS terpisah dari setiap sel berbiaya O(sel²). Multi-source BFS berbiaya O(sel).

### 7. Putaran: menghitung level

Proses queue **satu putaran sekali** (`for _ in range(len(queue))`). Setelah putaran `k`, kamu sudah mencapai semua yang berjarak `k` langkah. Jumlah putaran adalah jarak, jumlah menit, atau jumlah level.

### 8. Biaya dan batas

| | Waktu | Ruang |
|---|---|---|
| BFS / DFS pada adjacency list | O(V + E) | O(V) |
| Grid dengan R baris dan C kolom | O(R × C) | O(R × C) |
| Jalur terpendek (sisi sama) | O(V + E) | O(V) |

BFS untuk biaya langkah yang **sama**. Kalau sisi punya bobot berbeda (jalan dengan panjang berbeda), kamu butuh algoritma Dijkstra, yaitu BFS dengan heap sebagai ganti queue.

:::tip[🧭 Cara mengenali soal graf]
- Hal-hal yang **terhubung ke hal lain**: teman, tautan, jalan, prasyarat, dependensi.
- **Grid** atau papan tempat kamu bergerak atas, bawah, kiri dan kanan.
- Kata-kata seperti **terhubung, bisa dicapai, jalur, terpendek, jumlah minimum langkah/gerakan, pulau, wilayah**.
- Teka-teki yang tiap keadaannya bisa berubah menjadi beberapa keadaan lain (word ladder, gembok, permainan geser): keadaan adalah simpul.

"Langkah paling sedikit" → **BFS**. "Apakah ada jalur / hitung wilayah / jelajahi semuanya" → BFS atau DFS, keduanya boleh. "Semua jalur yang mungkin" → DFS dengan backtracking.
:::

### Memilih caranya

| Kebutuhan | Pakai |
|---|---|
| Jalur terpendek, biaya langkah sama | BFS (queue) |
| Bisa dicapai? Hitung wilayah? Flood fill? | DFS (stack) atau BFS |
| Banyak titik awal sekaligus | multi-source BFS |
| Graf sangat dalam | stack atau queue, bukan rekursi |
| Bobot sisi berbeda | Dijkstra (heap) |
| Deteksi siklus, pengurutan, bipartit | lesson berikutnya |

- ✅ Konektivitas, wilayah, langkah paling sedikit, penjelajahan dependensi.
- 🚫 BFS untuk jalur terpendek dengan biaya sisi berbeda.
- 🚫 Rekursi pada graf yang bisa sedalam 50.000.

## ⚠️ Kesalahan umum

- Tanpa set `visited`, sehingga pencarian berputar selamanya pada siklus.
- Menandai simpul seen hanya **saat di-pop** (ia masuk queue berkali-kali).
- Memakai DFS dan berharap jalur terpendek.
- Lupa batas grid (`0 <= r < rows`) atau mengecek setelah membaca sel.
- Membaca sel `(r, c)` sebagai `grid[c][r]`.
- Rekursi pada grid 500 × 500 yang semuanya daratan.
- Mengubah grid input tanpa memberi tahu (salin, atau pakai set `seen`).
- `list.pop(0)` sebagai queue (O(n)); pakai `collections.deque`.

## 🏆 Praktik terbaik

- [ ] Gambar grafnya untuk contoh: apa simpulnya, apa sisinya?
- [ ] Mulai dengan tiga bagian: **struktur data** (queue atau stack), **visited**, **tetangga**.
- [ ] Tandai visited saat **menambah** simpul, bukan saat menghapusnya.
- [ ] Pakai `deque` untuk BFS. Pakai list sebagai stack untuk DFS.
- [ ] Sebut biayanya: O(V + E), atau O(baris × kolom) untuk grid.
- [ ] Uji pada: satu simpul, siklus, graf terputus, dan jalur panjang.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan BFS dan DFS ke teman dengan riak kolam dan labirin berbenang. Kenapa BFS menemukan jalur terpendek dan DFS tidak?

## 📐 Rancang

CareerPilot ingin fitur **"orang yang bisa dimintai referral"**. Kontak user membentuk jaringan: kamu kenal beberapa orang, mereka kenal orang lain. Diberi sebuah perusahaan, temukan orang yang bekerja di sana dan **paling dekat dengan user** (perkenalan paling sedikit), dan tampilkan rantai perkenalannya. Rancang datanya dan algoritmanya. Bagaimana jika jaringannya 5 juta orang?

:::quiz
Tampilkan rancangan yang mungkin

- **Model:** orang adalah simpul, "kenal" adalah sisi (tak berarah). Simpan **adjacency list**: `person_id → [id kontak]`.
- **Algoritma:** **BFS dari user**. Orang pertama yang dicapai BFS dan bekerja di perusahaan target adalah yang terdekat. Simpan map `parent` untuk membangun rantai "kamu → Rina → Budi → Dewi".
- **Berhenti lebih awal:** berhenti di level pertama yang berisi kecocokan (atau setelah k kecocokan). Batasi kedalaman sekitar 3, karena rantai panjang bukan perkenalan yang berguna.
- **Keluaran:** rantai dari map `parent`; urutkan seri dengan sesuatu yang berguna (kekuatan hubungan).
- **Banyak titik awal:** untuk mencari, bagi setiap perusahaan, karyawan terdekat, jalankan **multi-source BFS** dari semua karyawan perusahaan itu sekaligus.
- **5 juta orang:** seluruh graf mungkin tak muat di satu proses. Ambil tetangga **sesuai kebutuhan** dari database atau graph store (`WHERE person_id = ?` dengan indeks) dan hanya untuk 2–3 level pertama; cache simpul populer. *BFS dua arah* (dari user dan dari target) memangkas kerja banyak sekali.
- **Siklus:** pakai set `visited` agar kontak bersama tidak diproses dua kali.
- **Privasi:** hanya tampilkan orang yang setuju bisa ditemukan.

**Aturan yang ditunjukkan:** "terdekat / langkah paling sedikit" di jaringan adalah BFS, dengan set visited dan map parent untuk jalurnya.
:::

### 📝 Daftar cek diri

- [ ] Simpul dan sisi disebut dengan jelas
- [ ] BFS, dengan alasan (perkenalan paling sedikit)
- [ ] Set visited dan map parent ada
- [ ] Batas kedalaman dan skala dibahas

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::problem{id="dsa-s4-graph-traversal" title="Graph Traversal: BFS and DFS" difficulty="easy" path="exercises/dsa/stage-4/13-graph-traversal"}
Bangun adjacency list, lalu BFS, DFS (dengan stack sendiri, pada jalur 50.000 simpul) dan pengecekan keterjangkauan.
:::

:::problem{id="dsa-s4-shortest-path" title="Shortest Path with BFS" difficulty="medium" path="exercises/dsa/stage-4/14-shortest-path"}
Jarak, jalur terpendek itu sendiri, dan word ladder dengan 5.000 kata.
:::

:::problem{id="dsa-s4-grid-islands" title="Grids Are Graphs: Islands and Flood Fill" difficulty="medium" path="exercises/dsa/stage-4/15-grid-islands"}
Hitung pulau, temukan yang terbesar, dan isi dengan ember cat, pada grid 500 × 500 tanpa rekursi.
:::

:::problem{id="dsa-s4-grid-shortest" title="Shortest Paths on Grids" difficulty="hard" path="exercises/dsa/stage-4/16-grid-shortest"}
Stretch: labirin, jeruk membusuk dan jarak ke nol terdekat, memakai putaran dan multi-source BFS.
:::

:::hints
- BFS: `deque`, `popleft`, set `seen`, dan tambahkan ke `seen` **saat kamu append**.
- DFS dengan stack: push `reversed(neighbours)` agar yang terkecil keluar dari stack lebih dulu.
- `has_path(a, a)` adalah `True`: simpul mencapai dirinya sendiri.
- Jarak: `dist = {start: 0}`; `if nxt not in dist` sekaligus menjadi pengecekan visited.
- Jalur: simpan `parent[nxt] = node`, lalu ikuti parent mundur dari tujuan dan balik list-nya.
- Word ladder: untuk tiap posisi coba `a..z` dan cek kata baru di `set`; hitung kata, bukan perubahan.
- Pulau: loop semua sel; mulai banjir hanya pada daratan yang belum dilihat; tandai sel seen saat kamu push.
- `flood_fill`: salin gambar dulu; jika warna lama sama dengan warna baru, kembalikan salinan.
- Jeruk busuk: masukkan semua jeruk busuk ke queue lebih dulu; satu putaran per menit; jika `fresh` masih di atas 0 di akhir, kembalikan `-1`.
- Nol terdekat: mulai queue dengan setiap `0` berjarak 0 dan isi sel lain saat BFS mencapainya.
:::

## ✅ Cek cepat

:::quiz
Kenapa BFS menemukan jalur terpendek di graf tak berbobot, tapi DFS tidak?

BFS mengunjungi simpul dalam cincin: semua yang berjarak 1 langkah, lalu 2 langkah, dan seterusnya. Saat pertama ia mencapai sebuah simpul, ia memakai langkah paling sedikit. DFS mengikuti satu jalur sedalam mungkin, jadi ia bisa tiba di sebuah simpul lewat rute panjang lebih dulu.
:::

:::quiz
Kenapa kamu harus menandai simpul visited saat menambahkannya ke queue, bukan saat menghapusnya?

Kalau menunggu sampai di-pop, simpul yang sama bisa ditambahkan berkali-kali oleh tetangga berbeda sebelum diproses. Itu membuang waktu dan memori, dan pada graf padat bisa meledak. Menandai saat penyisipan menjaga tiap simpul di queue paling banyak sekali.
:::

:::quiz
Apa itu multi-source BFS, dan kapan memakainya?

Kamu memasukkan semua titik awal ke queue di awal lalu menjalankan satu BFS. Tiap sel mendapat jaraknya ke titik awal terdekat. Pakai saat banyak sel bisa menjadi sumber (jeruk busuk, nol di matriks, semua karyawan sebuah perusahaan), sebagai ganti menjalankan BFS terpisah dari tiap sel.
:::

## 📚 Lanjut belajar

- [VisuAlgo: Graph traversal (BFS and DFS, interactive)](https://visualgo.net/en/dfsbfs)
- [Python docs: collections.deque](https://docs.python.org/3/library/collections.html#collections.deque)
- [Wikipedia: Breadth-first search](https://en.wikipedia.org/wiki/Breadth-first_search)

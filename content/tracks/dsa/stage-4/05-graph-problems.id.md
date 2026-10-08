---
title: "Basic Graph Problems"
summary: "Selesaikan pertanyaan graf klasik dengan satu alat untuk tiap jenis — union-find untuk kelompok dan siklus, algoritma Kahn untuk urutan dependensi, pewarnaan dua warna untuk konflik, dan Dijkstra untuk rute termurah — dan tahu alat mana yang dipilih."
sourceHash: d9d88ede2190
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Menghitung **kelompok terhubung** dan mendeteksi **siklus** dengan **union-find**
- Menaruh tugas dalam urutan yang valid dengan **topological sort** (algoritma Kahn)
- Mengecek apakah sesuatu bisa dibagi dua dengan **pewarnaan dua warna** (bipartit)
- Mencari **rute termurah** dengan **Dijkstra** saat sisi berbiaya berbeda
- Memilih alat yang tepat untuk sebuah pertanyaan, dan menjelaskan alasannya
- 🧭 Cara mengenali tiap soal

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Komponen terhubung** | Kelompok simpul yang semuanya bisa saling mencapai |
| **Siklus** | Jalur yang kembali ke tempat ia mulai |
| **Union-find** | Alat yang menggabungkan kelompok dan memberi tahu simpul masuk kelompok mana |
| **DAG** | Graf berarah tanpa siklus |
| **Urutan topologis** | Daftar yang semua panahnya menunjuk ke depan |
| **In-degree** | Berapa panah yang menunjuk masuk ke sebuah simpul |
| **Bipartit** | Bisa diwarnai dua warna, tak ada sisi yang menghubungkan warna sama |
| **Bobot** | Biaya sebuah sisi: jarak, harga, waktu |

## 🧠 Ide besarnya

Setelah BFS dan DFS kamu punya **kotak perkakas**. Empat pertanyaan sehari-hari masing-masing punya alat kecil yang terkenal:

- "**Apakah ini satu kelompok? Apakah tautan ini menutup sebuah putaran?**" → **union-find**, seperti sekolah yang tiap pertemanan baru menggabungkan dua kelompok teman.
- "**Apa yang kukerjakan lebih dulu?**" → **topological sort**, seperti resep yang tak bisa memanggang sebelum mengaduk.
- "**Bisakah ini dibagi ke dua tim tanpa bentrok?**" → **pewarnaan dua warna**, seperti mendudukkan dua keluarga yang bertikai di dua meja.
- "**Cara termurah untuk sampai ke sana?**" → **Dijkstra**, seperti aplikasi navigasi yang menjumlahkan tol dan menit.

Kamu tak perlu menemukan ini sendiri. Kamu perlu **mengenali pertanyaannya** dan meraih alatnya.

## ❓ Kenapa ini penting

Ini pekerjaan nyata, bukan hanya teka-teki wawancara:

- **Kelompok dan siklus:** "apakah dua akun ini terhubung?", mendeteksi akun ganda, menemukan putaran di konfigurasi.
- **Urutan dependensi:** `pip install`, `npm`, migrasi database, Terraform, pipeline CI, sistem build, sel spreadsheet. Siklus di sini adalah error sungguhan ("circular dependency").
- **Dua sisi:** menjadwalkan ujian tanpa bentrok, menugaskan reviewer, membagi set tes.
- **Rute termurah:** peta, routing jaringan, harga penerbangan, biaya pengiriman, AI permainan.

Semuanya juga memberi cara bicara yang jelas di wawancara: "ini soal dependensi, jadi topological sort dalam O(V + E)".

## 📖 Langkah demi langkah

### 1. Union-find: kelompok dan siklus

Tiap simpul mulai sebagai kelompoknya sendiri. `union(a, b)` menggabungkan dua kelompok. `find(x)` mengembalikan pemimpin kelompok.

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.size = [1] * n
        self.count = n                       # number of groups

    def find(self, x):
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
        while self.parent[x] != root:        # path compression: point everyone at the leader
            self.parent[x], x = root, self.parent[x]
        return root

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False                     # already together
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra                 # union by size: small group joins the big one
        self.size[ra] += self.size[rb]
        self.count -= 1
        return True
```

```python
def count_components(n, edges):
    uf = UnionFind(n)
    for a, b in edges:
        uf.union(a, b)
    return uf.count

def has_cycle(n, edges):
    uf = UnionFind(n)
    return any(not uf.union(a, b) for a, b in edges)   # an edge inside one group closes a loop
```

Dengan path compression dan union by size, tiap operasi hampir O(1). **Pohon** adalah graf dengan tepat `n - 1` sisi yang terhubung.

**Pakai saat:** sisi datang satu per satu ("tambah pertemanan"), dan kamu bertanya "satu kelompok?" atau "ada putaran?". Untuk graf tetap, BFS/DFS juga bisa.

### 2. Topological sort: urutan dependensi

Sisi berarah `a → b` berarti "a harus lebih dulu". Urutan yang valid menaruh setiap panah menunjuk ke depan. Urutan itu ada **hanya jika tak ada siklus**.

**Algoritma Kahn:** hitung panah yang menunjuk ke tiap simpul (in-degree). Mulai dari simpul yang tak punya (mereka *siap*). Ambil satu, dan kurangi hitungan semua yang ditunjuknya. Yang mencapai 0 menjadi siap.

```python
import heapq

def topo_order(n, edges):
    adj = [[] for _ in range(n)]
    indeg = [0] * n
    for a, b in edges:
        adj[a].append(b)
        indeg[b] += 1
    ready = [i for i in range(n) if indeg[i] == 0]
    heapq.heapify(ready)                         # smallest first, so the result is predictable
    order = []
    while ready:
        node = heapq.heappop(ready)
        order.append(node)
        for nxt in adj[node]:
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                heapq.heappush(ready, nxt)
    return order if len(order) == n else None    # fewer than n taken → there is a cycle
```

Kalau di akhir kamu mengambil kurang dari `n` simpul, sisanya saling menunggu selamanya: **sebuah siklus** (`can_finish` hanyalah pengecekan ini). Ambil queue **satu putaran sekali** untuk menjawab "berapa putaran jika semua tugas siap dikerjakan bersamaan?" (rantai terpanjang).

**Pakai saat:** "urutkan tugas", "apakah semua mata kuliah bisa diambil?", "urutan build", "jumlah putaran minimum".

### 3. Pewarnaan dua warna: cek bipartit

Warnai satu simpul 0, lalu BFS, beri tiap tetangga warna **sebaliknya**. Jika tetangga sudah punya warna yang **sama** denganmu, ada bentrok.

```python
from collections import deque

def two_color(n, edges):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)
    color = [-1] * n
    for start in range(n):                       # the graph may be in several pieces
        if color[start] != -1:
            continue
        color[start] = 0
        queue = deque([start])
        while queue:
            node = queue.popleft()
            for nxt in adj[node]:
                if color[nxt] == -1:
                    color[nxt] = 1 - color[node]
                    queue.append(nxt)
                elif color[nxt] == color[node]:
                    return None                  # two neighbours with the same colour
    return color
```

Graf bipartit **tepat ketika tak punya siklus dengan jumlah simpul ganjil** (segitiga, siklus-5). "Bagi ke dua tim dengan pasangan ini saling tak suka" adalah soal ini.

### 4. Dijkstra: rute termurah

BFS menghitung langkah. Dengan **bobot** (km, harga, menit, tidak pernah negatif), pakai **min-heap** berisi `(biaya sejauh ini, simpul)`. Selalu perluas simpul termurah yang ditemukan sejauh ini.

```python
import heapq

def dijkstra(graph, source):
    dist = {}
    heap = [(0, source)]
    while heap:
        cost, node = heapq.heappop(heap)
        if node in dist:                         # already finished with a cheaper cost
            continue
        dist[node] = cost                        # the first pop of a node is its final cost
        for nxt, weight in graph.get(node, []):
            if nxt not in dist:
                heapq.heappush(heap, (cost + weight, nxt))
    return dist
```

```text
A→B 4, A→C 1, C→B 2, B→D 1, C→D 7

pop A (0) → push B 4, C 1
pop C (1) → push B 3, D 8
pop B (3) → push D 4        ← B costs 3 (via C), not 4
pop D (4)
```

Simpan `parent` untuk tiap simpul untuk membangun ulang rutenya. Waktunya **O((V + E) log V)**. Dijkstra butuh bobot tak negatif; untuk bobot negatif pakai Bellman-Ford.

### 5. Memilih alat

| Pertanyaan | Alat | Waktu |
|---|---|---|
| Langkah paling sedikit, sisi sama | BFS | O(V + E) |
| Rute termurah, bobot ≥ 0 | Dijkstra (heap) | O((V + E) log V) |
| Berapa kelompok? Ada putaran? Sisi datang online | union-find | ≈ O(E) |
| Urutan dengan dependensi; ada dependensi melingkar? | topological sort (Kahn) | O(V + E) |
| Bisa dibagi dua sisi? | pewarnaan dua warna (BFS) | O(V + E) |
| Bisa dicapai? Jelajahi semuanya? | BFS / DFS | O(V + E) |

:::tip[🧭 Cara mengenali tiap soal]
- **"Terhubung / satu kelompok / jumlah kelompok / koneksi berlebih / apakah ini pohon"** → union-find (atau DFS).
- **"Urutan / prasyarat / urutan build / dependensi / dependensi melingkar / jadwal"** → topological sort.
- **"Dua kelompok / tim / dua warna / konflik / siklus ganjil"** → bipartit.
- **"Termurah / tercepat / terpendek dengan bobot / waktu tunda / biaya minimum untuk sampai"** → Dijkstra.
- **"Gerakan paling sedikit"** dengan biaya sama → BFS.

Kata **"berarah"** sering menunjuk ke topological sort atau Dijkstra. Kata **"tak berarah"** dengan **"kelompok"** menunjuk ke union-find.
:::

### Memilih caranya

| Situasi | Pakai |
|---|---|
| Data datang sebagai aliran koneksi | union-find |
| Graf tetap, hitung wilayah | BFS/DFS atau union-find |
| Banyak tugas dengan prasyarat | topological sort |
| Biaya sisi berbeda | Dijkstra |
| Biaya sisi sama | BFS |
| Biaya sisi negatif | Bellman-Ford (sebutkan saja) |

- ✅ Dependensi, jaringan, penjadwalan, routing, pengelompokan.
- 🚫 Dijkstra dengan bobot negatif.
- 🚫 Topological sort pada graf bersiklus (deteksi dan laporkan error).

## ⚠️ Kesalahan umum

- Union-find tanpa path compression atau union by size (jadi O(n) per panggilan pada rantai).
- `find` rekursif pada rantai 200.000 simpul (pakai loop).
- Lupa sisi berulang atau self-loop (`(u, u)`) saat mencari siklus.
- Topological sort: lupa mengecek bahwa semua `n` simpul terambil (pengecekan siklus).
- Membalik arah pasangan prasyarat `(course, needs)`.
- Mewarnai hanya kelompok pertama dan mengabaikan bagian graf yang lain.
- Dijkstra: menandai simpul final saat **push**, bukan saat **pop**.
- Memakai Dijkstra pada bobot negatif, atau BFS pada sisi berbobot.

## 🏆 Praktik terbaik

- [ ] Sebut **simpul** dan **sisi**, dan katakan apakah berarah dan berbobot.
- [ ] Cocokkan pertanyaan dengan alat dalam satu kalimat: "ini soal dependensi, jadi topological sort".
- [ ] Sebut biayanya: O(V + E), atau O((V + E) log V) untuk Dijkstra.
- [ ] Tangani graf terputus: loop semua simpul, bukan hanya simpul 0.
- [ ] Uji pada: tanpa sisi, satu simpul, siklus, self-loop, sisi berulang.
- [ ] Pakai loop (bukan rekursi) untuk graf yang bisa sangat dalam.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke rekan tim, dengan analogi resep, kenapa siklus di dependensi sebuah build berarti build tak bisa jalan, dan bagaimana algoritma Kahn menemukannya tanpa pernah "mencari siklus".

## 📐 Rancang

Fase 5 CareerPilot men-deploy beberapa layanan: `database`, `core-api`, `ai-service`, `worker`, `web`. Masing-masing butuh sebagian yang lain sehat lebih dulu. Alat deploy-mu harus (1) menentukan urutan, (2) menjalankan layanan yang independen **bersamaan**, dan (3) menolak jalan jika konfigurasi punya dependensi melingkar, dengan pesan yang membantu. Rancang algoritma dan pesan errornya.

:::quiz
Tampilkan rancangan yang mungkin

- **Model:** layanan adalah simpul; sisi `a → b` berarti "a harus sehat sebelum b mulai". Baca dari daftar `depends_on` tiap layanan.
- **Algoritma:** **topological sort Kahn, satu putaran sekali.** Putaran 1: layanan tanpa dependensi (`database`). Putaran 2: semua yang hanya butuh itu (`core-api`, `worker`, ...). Semua layanan dalam satu putaran dimulai **paralel**. Jumlah putaran adalah waktu deploy minimum dalam "gelombang".
- **Deteksi siklus:** jika setelah loop layanan yang terjadwal kurang dari yang ada, sisanya saling bergantung. Laporkan: *"Circular dependency among: ai-service, worker"*. Untuk mencetak putaran sebenarnya, jalankan DFS pada simpul sisa dan ikuti sisi sampai kembali ke simpul yang sudah ada di jalur.
- **Validasi sebelum deploy:** cek juga nama tak dikenal (dependensi yang bukan layanan) dan dependensi ke diri sendiri.
- **Keluaran deterministik:** ambil layanan siap dalam urutan abjad, supaya rencananya sama setiap kali dan mudah direview.
- **Biaya:** O(V + E), sepele untuk puluhan layanan.
- **Teardown:** hancurkan dalam urutan **terbalik** (web dulu, database terakhir). Terraform dan Kubernetes melakukan hal yang sama.

**Aturan yang ditunjukkan:** "mulai sesuatu dalam urutan dependensi, dalam gelombang paralel" adalah topological sort per putaran, dan simpul yang tersisa adalah siklusmu.
:::

### 📝 Daftar cek diri

- [ ] Simpul, sisi dan arah disebut
- [ ] Putaran memberi start paralel
- [ ] Siklus dilaporkan dengan jelas
- [ ] Urutan teardown dipertimbangkan

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::problem{id="dsa-s4-components-cycles" title="Components, Cycles and Union-Find" difficulty="medium" path="exercises/dsa/stage-4/17-components-cycles"}
Tulis `UnionFind`, hitung kelompok, deteksi siklus (termasuk self-loop dan sisi berulang) dan cek apakah sebuah pohon.
:::

:::problem{id="dsa-s4-topological-sort" title="Topological Sort" difficulty="medium" path="exercises/dsa/stage-4/18-topological-sort"}
Urutkan tugas menurut dependensi dengan algoritma Kahn, deteksi prasyarat melingkar, dan hitung putaran yang dibutuhkan.
:::

:::problem{id="dsa-s4-bipartite" title="Two-Colouring (Bipartite)" difficulty="medium" path="exercises/dsa/stage-4/19-bipartite"}
Warnai graf dengan dua warna, bagi orang ke dua tim, dan deteksi siklus ganjil.
:::

:::problem{id="dsa-s4-dijkstra" title="Cheapest Routes (Dijkstra)" difficulty="hard" path="exercises/dsa/stage-4/20-dijkstra"}
Stretch: biaya ke setiap simpul, rute termurah itu sendiri, dan waktu sinyal mencapai seluruh jaringan.
:::

:::hints
- `find` union-find: loop naik ke akar, lalu loop lagi untuk mengarahkan setiap simpul ke akar.
- `union` mengembalikan `False` saat kedua simpul sudah punya akar yang sama: itu sinyal siklusmu.
- Pohon valid punya tepat `n - 1` sisi **dan** satu kelompok; cek jumlah sisi dulu.
- Kahn: bangun `adj` dan `indeg`; mulai dengan simpul ber-in-degree 0 di min-heap; `len(order) == n` berarti tak ada siklus.
- `can_finish`: pasangannya `(course, needs)`, jadi sisinya `needs → course`.
- `min_semesters`: simpan putaran saat ini sebagai list; putaran berikutnya mengumpulkan simpul yang in-degree-nya baru menjadi 0.
- Pewarnaan dua warna: loop `for start in range(n)` supaya setiap kelompok diwarnai; tetangga dengan warna sama berarti `None`.
- `can_split_into_two_teams`: orang dinomori dari 1; kurangi 1 untuk simpul `0..n-1`.
- Dijkstra: `if node in dist: continue` tepat setelah pop; isi `dist[node]` saat pop, bukan saat push.
- `cheapest_route`: push `(cost, node, previous)` dan simpan `parent[node] = previous` saat memfinalkan simpul.
- `network_delay_time`: Dijkstra dari `k`; jika kurang dari `n` simpul tercapai kembalikan `-1`, selain itu biaya terbesar.
:::

## ✅ Cek cepat

:::quiz
Topological sort menghasilkan kurang dari n simpul. Apa artinya?

Simpul yang tersisa masing-masing menunggu simpul sisa lain, jadi tak satu pun mencapai in-degree 0. Itu siklus di dependensi, dan tidak ada urutan valid.
:::

:::quiz
Kenapa Dijkstra tidak bisa menangani bobot sisi negatif?

Dijkstra mengasumsikan saat pertama ia mem-pop sebuah simpul, tak akan muncul yang lebih murah kemudian, karena menambah sisi hanya menaikkan biaya. Sisi negatif bisa menurunkan biaya simpul yang sudah difinalkan. Pakai Bellman-Ford saat bobot bisa negatif.
:::

:::quiz
Bagaimana union-find memberi tahu bahwa sebuah sisi menutup siklus?

Jika kedua ujung sisi sudah punya pemimpin yang sama, mereka sudah terhubung lewat sisi lain. Menambah sisi ini menciptakan rute kedua di antara mereka, yaitu siklus.
:::

## 📚 Lanjut belajar

- [VisuAlgo: Single-source shortest paths (Dijkstra, interactive)](https://visualgo.net/en/sssp)
- [VisuAlgo: Union-Find disjoint sets](https://visualgo.net/en/ufds)
- [Wikipedia: Topological sorting](https://en.wikipedia.org/wiki/Topological_sorting)

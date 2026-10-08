---
title: "Binary Trees"
summary: Pahami pohon sebagai simpul dengan anak, selesaikan soal pohon dengan memercayai rekursi (base case plus gabungkan), kunjungi simpul dalam empat urutan, dan hindari crash pada pohon sangat dalam dengan stack atau queue sendiri.
sourceHash: 4d96434e5da6
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa itu **pohon** dan **pohon biner**, beserta istilah di sekitarnya
- Resep pohon: **base case + gabungkan jawaban anak-anaknya**
- Empat cara mengunjungi semua simpul: **preorder, inorder, postorder, level order**
- Mengembalikan nilai ke induk **sekaligus** mencatat jawaban di samping (diameter, LCA)
- Kenapa pohon yang sangat dalam merusak rekursi, dan apa penggantinya
- 🧭 Cara mengenali soal pohon

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Pohon (tree)** | Data berbentuk silsilah keluarga: satu puncak, cabang turun ke bawah |
| **Simpul (node)** | Satu item di dalam pohon |
| **Akar (root)** | Simpul paling atas. Tidak punya induk |
| **Daun (leaf)** | Simpul tanpa anak |
| **Pohon biner** | Tiap simpul punya paling banyak dua anak: kiri dan kanan |
| **Tinggi (height)** | Berapa simpul di jalur terpanjang dari akar ke bawah |
| **Sub-pohon** | Sebuah simpul beserta semua yang ada di bawahnya |
| **Penelusuran (traversal)** | Mengunjungi tiap simpul sekali, dalam suatu urutan |

## 🧠 Ide besarnya

Pohon itu seperti **bagan organisasi perusahaan**. Direktur (akar) punya manajer di bawahnya, dan tiap manajer punya timnya sendiri. Untuk menghitung semua orang di perusahaan, direktur tidak berjalan ke setiap meja. Direktur bertanya ke tiap manajer, "Berapa orang di timmu?", menjumlahkan jawabannya, lalu menambah 1 untuk dirinya sendiri. Tiap manajer melakukan hal yang sama dengan timnya. Orang tanpa tim menjawab "1".

Inilah seluruh trik pohon: **selesaikan masalah untuk satu simpul dengan menanyakan pertanyaan yang sama ke anak-anaknya**, lalu gabungkan. Kamu tak perlu membayangkan seluruh pohon. Kamu cukup percaya bahwa anak-anaknya menjawab dengan benar.

## ❓ Kenapa ini penting

Pohon ada di mana-mana dalam perangkat lunak:

- **file system** (folder di dalam folder) dan **DOM HTML** di browser-mu,
- **komentar dengan balasan**, menu dengan submenu, bagan organisasi,
- **JSON** yang kamu kirim ke API (objek di dalam objek),
- **indeks database** dan **pohon pencarian** (lesson berikutnya),
- **decision tree** dan cara compiler membaca kodemu.

Dan pohon adalah topik favorit wawancara, karena satu ide kecil (rekursi dengan base case) menyelesaikan banyak soal. Kalau kamu menguasai resepnya di sini, BST, heap dan graph akan terasa familiar.

## 📖 Langkah demi langkah

### 1. Simpulnya

Simpul pohon biner menyimpan satu nilai dan paling banyak dua anak.

```python
class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left      # another TreeNode, or None
        self.right = right
```

```text
      1            root = 1
     / \           leaves = 4, 5, 3
    2   3          height = 3 (nodes on the longest path: 1 → 2 → 4)
   / \
  4   5
```

**Pohon kosong** hanyalah `None`. Menganggap `None` sebagai pohon yang sah (kosong) inilah yang membuat kodenya pendek.

### 2. Resepnya: base case + gabungkan

Setiap fungsi pohon bentuknya sama:

```python
def size(root):
    if root is None:                      # 1. base case: the empty tree
        return 0
    return 1 + size(root.left) + size(root.right)   # 2. combine the children's answers
```

```python
def height(root):
    if root is None:
        return 0
    return 1 + max(height(root.left), height(root.right))
```

Untuk menulisnya, tanyakan dua hal:

1. Apa jawaban untuk **pohon kosong**?
2. Kalau kedua anakku sudah memberi jawabannya, bagaimana aku mendapat **jawabanku**?

Jangan telusuri rekursinya sampai dasar di kepalamu. Cek base case, cek langkah gabungnya, dan percayai sisanya. Ini disebut *lompatan keyakinan*.

### 3. Empat cara mengunjungi semua simpul

Satu-satunya beda adalah **kapan** kamu menangani simpul saat ini.

```python
def preorder(node):                 # node, left, right
    if node is None:
        return []
    return [node.val] + preorder(node.left) + preorder(node.right)

def inorder(node):                  # left, node, right
    if node is None:
        return []
    return inorder(node.left) + [node.val] + inorder(node.right)

def postorder(node):                # left, right, node
    if node is None:
        return []
    return postorder(node.left) + postorder(node.right) + [node.val]
```

```text
      1
     / \
    2   3          preorder   [1, 2, 4, 5, 3, 6]   "me first"
   / \   \         inorder    [4, 2, 5, 1, 3, 6]   "left, me, right"
  4   5   6        postorder  [4, 5, 2, 6, 3, 1]   "children first, me last"
```

| Urutan | Pakai saat |
|---|---|
| **Preorder** | kamu harus menangani induk **sebelum** anaknya (menyalin pohon, mencetak outline folder) |
| **Inorder** | kamu ingin nilai pohon pencarian **terurut** (lesson berikutnya) |
| **Postorder** | kamu butuh hasil anak-anak **sebelum** induk (ukuran folder, menghapus pohon) |
| **Level order** | kamu peduli pada **baris**: simpul terdekat dulu, "apa isi tiap level?" |

### 4. Level order memakai queue

Level order bukan rekursi. Ia berjalan baris demi baris, jadi memakai **queue** (masuk pertama, keluar pertama).

```python
from collections import deque

def level_order(root):
    if root is None:
        return []
    levels, queue = [], deque([root])
    while queue:
        level = []
        for _ in range(len(queue)):          # exactly the nodes on this row
            node = queue.popleft()
            level.append(node.val)
            if node.left:
                queue.append(node.left)
            if node.right:
                queue.append(node.right)
        levels.append(level)
    return levels
```

Menghitung `len(queue)` di awal tiap putaran adalah trik untuk tahu di mana sebuah baris berakhir. Ide yang sama kamu pakai untuk graph di lesson BFS.

### 5. Pohon sangat dalam: pakai stack sendiri

Python mengizinkan sekitar 1.000 panggilan bersarang. Pohon yang sebenarnya rantai panjang (50.000 simpul) membuat fungsi rekursif crash dengan `RecursionError`. Perbaikannya: kerjakan tugas call stack sendiri, dengan sebuah list.

```python
def inorder_iterative(root):
    out, stack, node = [], [], root
    while node or stack:
        while node:                 # go as far left as possible
            stack.append(node)
            node = node.left
        node = stack.pop()          # nothing more on the left: visit
        out.append(node.val)
        node = node.right           # then move to the right subtree
    return out
```

Rekursi lebih jelas, jadi pakai saat pohon seimbang (tinggi sekitar log n). Beralih ke stack atau queue saat pohon bisa dalam, atau saat pewawancara memintanya.

### 6. Bandingkan dua simpul sekaligus

Sebagian soal menelusuri **dua** pohon (atau dua sisi satu pohon) pada saat yang sama.

```python
def is_same_tree(a, b):
    if a is None or b is None:
        return a is b                      # both empty → same; only one empty → different
    return a.val == b.val and is_same_tree(a.left, b.left) and is_same_tree(a.right, b.right)

def is_symmetric(root):
    def mirror(a, b):
        if a is None or b is None:
            return a is b
        return a.val == b.val and mirror(a.left, b.right) and mirror(a.right, b.left)
    return root is None or mirror(root.left, root.right)
```

Untuk simetri, pasangan **luar** (`a.left` dengan `b.right`) dan pasangan **dalam** (`a.right` dengan `b.left`) harus cocok.

### 7. Kembalikan satu hal, catat hal lain

Sebagian jawaban bukan "nilai di akar". Jalur terpanjang (**diameter**) bisa ada jauh di dalam satu sub-pohon. Triknya: tiap panggilan **mengembalikan tingginya ke induk**, dan **memperbarui jawaban terbaik di samping**.

```python
def diameter(root):
    best = 0

    def height(node):
        nonlocal best
        if node is None:
            return 0
        left, right = height(node.left), height(node.right)
        best = max(best, left + right)       # a path that bends at this node
        return 1 + max(left, right)          # what the parent needs

    height(root)
    return best
```

Kalau kamu memanggil `height()` terpisah di setiap simpul, biayanya O(n²). Mengerjakan kedua tugas dalam satu lintasan biayanya O(n). Bentuk yang sama menyelesaikan *lowest common ancestor*, *max path sum* dan *apakah pohon ini seimbang?*.

### 8. Biaya

| | Waktu | Ruang tambahan |
|---|---|---|
| Mengunjungi semua simpul | O(n) | O(h), h adalah tinggi (call stack) |
| Pohon seimbang | O(n) | O(log n) |
| Rantai | O(n) | O(n), dan rekursi bisa crash |
| Level order | O(n) | O(w), w adalah baris terlebar |

:::tip[🧭 Cara mengenali soal pohon]
- Datanya berbentuk **induk → anak** (folder, komentar, menu, JSON, bagan organisasi).
- Kata-kata **root, leaf, depth, path, ancestor, subtree**.
- Jawaban sebuah simpul bergantung pada jawaban **anak-anaknya**.
- Kamu diminta sesuatu **per level** (level order) atau **terurut** (inorder pada BST).

Kalau tiap simpul bisa terhubung ke simpul lain mana pun, dan ada lingkaran, itu **graph**, bukan pohon (lesson BFS/DFS).
:::

### Memilih caranya

| Situasi | Pakai |
|---|---|
| Jawaban bergantung pada jawaban anak | rekursi: base case + gabungkan |
| Butuh hasil baris demi baris, atau jarak terpendek | level order dengan queue |
| Pohon bisa sangat dalam | stack sendiri (iteratif) |
| Membandingkan dua pohon atau dua sisi | rekursi pada keduanya sekaligus |
| Jalur terpanjang/terbaik yang bisa menikung di dalam | kembalikan tinggi, perbarui best di samping |

- ✅ Hierarki, data bersarang, soal "untuk tiap level".
- 🚫 Data dengan lingkaran atau banyak induk (pakai graph).
- 🚫 Rekursi pada pohon yang bisa berupa rantai 100.000 simpul.

## ⚠️ Kesalahan umum

- Lupa base case untuk `None`, atau mengecek `root.left` sebelum mengecek `root`.
- Mencampur **tinggi** dalam simpul dan dalam sisi (edge). Pilih satu dan ucapkan keras-keras.
- Jumlah jalur yang berakhir di simpul mana pun, bukan di **daun**.
- Memanggil `height()` di setiap simpul (O(n²)).
- Rekursi pada rantai 50.000 simpul di Python.
- Mengubah list (`path.append`) dan lupa membatalkannya (`path.pop`) saat backtracking.

## 🏆 Praktik terbaik

- [ ] Tulis base case dulu, dalam satu baris.
- [ ] Ucapkan dengan kata-kata: "jawaban sebuah simpul dibuat dari …".
- [ ] Uji dengan **pohon kosong**, **simpul tunggal**, **rantai** dan **pohon seimbang**.
- [ ] Sebut tinggi dalam simpul atau sisi, dan konsisten.
- [ ] Kembalikan nilai yang dibutuhkan induk, dan simpan hasil samping di variabel (`nonlocal`).
- [ ] Sebut waktu (O(n)) dan ruang (O(h)) sebelum pewawancara bertanya.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke rekan tim cara menemukan ukuran total sebuah folder (termasuk semua folder di dalamnya) dengan ide bagan organisasi. Dari mana base case-nya?

## 📐 Rancang

Catatan di CareerPilot punya **balasan bersusun**: sebuah catatan bisa punya balasan, dan tiap balasan bisa punya balasan. Web app perlu (1) menampilkan seluruh thread dengan indentasi, (2) menampilkan "12 balasan" di atas, dan (3) memuat hanya 3 level pertama dulu. Rancang datanya dan algoritmanya.

:::quiz
Tampilkan rancangan yang mungkin

- **Data:** tiap baris balasan punya `id`, `parent_id` (null untuk catatan teratas), `text`. Di memori, bangun pohon: dict `id → node`, lalu pasang tiap node ke list `children` induknya. Satu lintasan, O(n).
- **Tampilan berindentasi:** penelusuran **preorder**, meneruskan `depth` ke bawah: cetak `"  " * depth + text`, lalu telusuri tiap anak dengan `depth + 1`. Induk dulu, lalu balasannya.
- **Jumlah balasan:** perhitungan **postorder**/ukuran: `count(node) = sum(count(child) + 1 for child in children)`. Tiap node bertanya ke anaknya, lalu menjawab induknya.
- **3 level pertama:** penelusuran **level order** (queue) yang berhenti di kedalaman 3, atau penelusuran rekursif dengan argumen `max_depth`. Tampilkan "muat lebih banyak" pada node yang masih punya anak tersembunyi.
- **Thread dalam:** thread bisa berupa rantai panjang, jadi demi aman pakai penelusuran iteratif, atau batasi kedalaman di produk.
- **Skala besar:** ambil hanya level yang dibutuhkan dengan SQL (`WITH RECURSIVE`), bukan seluruh tabel.

**Aturan yang ditunjukkan:** penelusuran pohon dengan urutan yang tepat (induk dulu, anak dulu, atau baris demi baris) menjawab soal tampilan, penghitungan dan paging.
:::

### 📝 Daftar cek diri

- [ ] Aku menyebut urutan penelusuran dan alasannya
- [ ] Base case (pohon kosong) sudah ditangani
- [ ] Pohon dalam dipertimbangkan (stack atau batas kedalaman)
- [ ] Waktu dan ruang disebutkan

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::problem{id="dsa-s4-tree-basics" title="Tree Basics" difficulty="easy" path="exercises/dsa/stage-4/01-tree-basics"}
Ukuran, tinggi, jumlah daun dan jumlah semua nilai. Empat fungsi, satu resep: base case plus gabungkan.
:::

:::problem{id="dsa-s4-tree-traversals" title="Tree Traversals" difficulty="medium" path="exercises/dsa/stage-4/02-tree-traversals"}
Preorder, inorder, postorder dan level order. Inorder dan level order harus selamat dari rantai 50.000 simpul.
:::

:::problem{id="dsa-s4-mirror-compare" title="Mirror & Compare" difficulty="medium" path="exercises/dsa/stage-4/03-mirror-compare"}
Apakah dua pohon sama? Balik sebuah pohon. Apakah pohon simetris? Telusuri dua simpul sekaligus.
:::

:::problem{id="dsa-s4-paths-diameter-lca" title="Paths, Diameter and Lowest Common Ancestor" difficulty="hard" path="exercises/dsa/stage-4/04-paths-diameter-lca"}
Stretch: jumlah dan daftar jalur akar-ke-daun, diameter dalam satu lintasan, dan lowest common ancestor.
:::

:::hints
- Setiap fungsi dimulai dengan `if root is None:`. Tentukan apa yang dikembalikan pohon kosong (0, `[]`, `True`, `False`).
- `height`: `1 + max(height(left), height(right))`. `count_leaves`: simpul tanpa anak dihitung 1.
- Inorder iteratif: dorong rantai kiri, pop lalu kunjungi, kemudian ke kanan.
- Level order: di awal tiap putaran ambil `len(queue)` sebagai ukuran baris.
- `is_symmetric`: bandingkan `left.left` dengan `right.right`, dan `left.right` dengan `right.left`.
- `has_path_sum`: cek target hanya di **daun**; teruskan `target - root.val` ke bawah.
- `root_to_leaf_paths`: `append` saat masuk simpul, `pop` saat keluar; simpan **salinan** (`list(path)`) jalur lengkap.
- `diameter`: fungsi bantu yang mengembalikan tinggi dan memperbarui `best = max(best, left + right)`.
- `lowest_common_ancestor`: kalau kedua sisi mengembalikan node, node saat ini adalah jawabannya; cek juga bahwa kedua nilai ada.
:::

## ✅ Cek cepat

:::quiz
Kenapa fungsi pohon rekursif biasanya pendek?

Ia hanya butuh base case untuk pohon kosong dan cara menggabungkan jawaban sub-pohon kiri dan kanan. Rekursi menangani seluruh kedalaman, jadi kamu tak menelusuri tiap level sendiri.
:::

:::quiz
Kenapa inorder rekursif crash pada rantai 50.000 simpul di Python, dan apa yang kamu lakukan?

Python membatasi panggilan bersarang sekitar 1.000, dan tiap simpul menambah satu panggilan. Kerjakan tugas call stack sendiri: pakai list sebagai stack (atau deque sebagai queue untuk level order), sehingga hanya memori yang membatasi.
:::

:::quiz
Urutan penelusuran mana yang memberi nilai binary search tree secara terurut?

Inorder (kiri, simpul, kanan). Semua di kiri lebih kecil dan semua di kanan lebih besar, jadi mengunjungi kiri, lalu simpul, lalu kanan menghasilkan urutan menaik.
:::

## 📚 Lanjut belajar

- [Python docs: collections.deque](https://docs.python.org/3/library/collections.html#collections.deque)
- [Wikipedia: Tree traversal](https://en.wikipedia.org/wiki/Tree_traversal)
- [VisuAlgo: Binary tree traversals (interactive)](https://visualgo.net/en/bst)

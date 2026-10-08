---
title: "Binary Search Trees"
summary: Pakai aturan BST (lebih kecil di kiri, lebih besar di kanan) untuk mencari, menyisipkan dan menghapus dalam O(h), validasi pohon dengan batas bukan sekadar cek induk, dan pahami kenapa keseimbangan menentukan BST cepat atau menjadi rantai lambat.
sourceHash: 52aa4e959eed
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- **Aturan BST** dan bagaimana ia membuatmu melewati separuh pohon di tiap langkah
- **Search, insert, min dan max** dengan menyusuri satu jalur
- **Menghapus** simpul (tiga kasus) dan menjaga pohon tetap valid
- **Memvalidasi** BST dengan cara yang benar (batas, bukan hanya induk)
- Kenapa BST bisa merosot jadi rantai, dan bagaimana **keseimbangan** memperbaikinya
- 🧭 Cara mengenali soal BST

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **BST** | Pohon biner yang kiri lebih kecil dan kanan lebih besar, di setiap simpul |
| **Invariant** | Aturan yang harus tetap benar setelah setiap operasi |
| **Successor** | Nilai berikutnya yang lebih besar (yang terkecil di sisi kanan) |
| **Floor / ceiling** | Nilai terdekat di bawah atau sama / di atas atau sama |
| **Seimbang (balanced)** | Sisi kiri dan kanan punya tinggi yang hampir sama |
| **Degenerate** | Pohon yang berubah jadi rantai, sehingga lambat |
| **O(h)** | Biaya tumbuh seiring tinggi pohon |

## 🧠 Ide besarnya

BST adalah **kamus** yang bisa kamu buka di tengah. Kamu mencari kata "mangga". Kamu membuka buku di tengah dan melihat "kiwi". "Mangga" datang setelah "kiwi", jadi kamu membuang seluruh separuh pertama dan mencari hanya di separuh kedua. Tiap langkah membuang separuh dari sisanya.

Aturan BST adalah janji yang sama di setiap simpul: **semua di kiri lebih kecil, semua di kanan lebih besar**. Karena janji itu berlaku di mana-mana, satu perbandingan memberitahumu separuh mana yang diabaikan.

## ❓ Kenapa ini penting

Pencarian cepat di koleksi yang **terurut dan berubah** adalah kebutuhan umum:

- **indeks** database (kebanyakan B-tree, kerabat BST),
- **ordered map** di memori ("beri aku key berikutnya yang lebih besar"),
- **rentang autocomplete**, penjadwalan ("slot kosong berikutnya setelah jam 3 sore?"),
- set dan map dengan **urutan terurut** (`TreeMap` di Java, `SortedDict` di library Python).

List terurut biasa mencari cepat (binary search), tapi menyisipkan di tengah memindahkan banyak item. Hash map menyisipkan cepat, tapi tak bisa menjawab "key berikutnya yang lebih besar". BST memberimu ketiganya, selama ia tetap **seimbang**.

## 📖 Langkah demi langkah

### 1. Aturannya, dan petunjuk yang diberikannya

```text
        8
       / \
      3   10         left of 8 :  3, 1, 6, 4, 7   (all smaller than 8)
     / \    \        right of 8:  10, 14, 13      (all larger than 8)
    1   6    14
       / \   /
      4   7 13
```

Aturan yang sama berlaku di **setiap** simpul, bukan hanya di akar. Maka penelusuran **inorder** (kiri, simpul, kanan) memberi nilai **terurut**: `1 3 4 6 7 8 10 13 14`.

### 2. Search: ikuti satu jalur

```python
def search(root, val):
    node = root
    while node:
        if val == node.val:
            return True
        node = node.left if val < node.val else node.right
    return False
```

Kamu tak pernah melihat kedua sisi. Mencari 6 di pohon di atas: `8 → kiri → 3 → kanan → 6`. Itu 3 langkah, bukan 9.

Biayanya **O(h)**, h adalah tinggi. Di pohon seimbang h sekitar log n, jadi sejuta nilai butuh sekitar 20 langkah.

### 3. Insert: cari, lalu pasang daun

```python
def insert(root, val):
    if root is None:
        return TreeNode(val)
    node = root
    while True:
        if val == node.val:
            return root                      # already there
        side = "left" if val < node.val else "right"
        nxt = getattr(node, side)
        if nxt is None:
            setattr(node, side, TreeNode(val))
            return root
        node = nxt
```

Nilai baru selalu menjadi **daun**. Tak ada yang lain yang bergeser.

### 4. Terkecil dan terbesar

Terkecil: terus ke kiri. Terbesar: terus ke kanan. Keduanya O(h).

### 5. Delete: tiga kasus

Menghapus adalah yang rumit, karena kamu harus menjaga aturan tetap benar.

```python
def delete(root, val):
    if root is None:
        return None
    if val < root.val:
        root.left = delete(root.left, val)
    elif val > root.val:
        root.right = delete(root.right, val)
    else:
        if root.left is None:                 # leaf, or only a right child
            return root.right
        if root.right is None:                # only a left child
            return root.left
        successor = root.right                # two children: take the next larger value
        while successor.left:
            successor = successor.left
        root.val = successor.val
        root.right = delete(root.right, successor.val)
    return root
```

```text
leaf          → remove it
one child     → the child takes its place
two children  → copy the INORDER SUCCESSOR (smallest on the right) into this node,
                then delete that successor from the right subtree
```

Kenapa successor? Ia lebih besar dari semua di kiri dan lebih kecil dari semua yang lain di kanan, jadi aturan tetap berlaku.

### 6. Validasi: teruskan batas ke bawah

Kesalahan klasik adalah mengecek tiap simpul hanya terhadap induknya:

```text
      5
     / \
    1   4          4 > 1? fine.   3 < 4? fine.
       / \         But 3 is in the RIGHT side of 5, so it must be larger than 5. This is NOT a BST.
      3   6
```

Sebuah simpul harus berada di antara batas **semua** leluhurnya. Bawa `low` dan `high` ke bawah:

```python
def is_valid_bst(root):
    def ok(node, low, high):
        if node is None:
            return True
        if (low is not None and node.val <= low) or (high is not None and node.val >= high):
            return False
        return ok(node.left, low, node.val) and ok(node.right, node.val, high)

    return ok(root, None, None)
```

Cara lain: penelusuran **inorder harus naik secara ketat**.

### 7. Soal urutan: inorder membantu

Karena inorder terurut, banyak soal jadi mudah:

- **k-th terkecil:** inorder dengan stack, berhenti di simpul ke-k yang kamu pop.
- **floor / ceiling dari x:** susuri satu jalur. Ke kanan? nilai saat ini kandidat floor. Ke kiri? kandidat ceiling.
- **jumlah rentang antara a dan b:** lewati seluruh sub-pohon yang di luar rentang.
- **lowest common ancestor:** jika kedua nilai lebih kecil ke kiri, keduanya lebih besar ke kanan, selain itu simpul ini jawabannya. Ini O(h), lebih baik dari versi pohon umum.

### 8. Keseimbangan adalah segalanya

Sisipkan 1, 2, 3, 4, 5 berurutan:

```text
1
 \
  2             a chain: height 5, search is O(n)
   \
    3
     \
      4
       \
        5
```

Lima nilai yang sama dalam urutan yang baik menghasilkan pohon setinggi 3. BST hanya cepat bila **seimbang**.

Bangun pohon seimbang dari data terurut dengan menjadikan nilai **tengah** sebagai akar, lalu lakukan hal yang sama untuk tiap separuh:

```python
def sorted_array_to_bst(nums):
    def build(lo, hi):
        if lo > hi:
            return None
        mid = (lo + hi) // 2
        return TreeNode(nums[mid], build(lo, mid - 1), build(mid + 1, hi))

    return build(0, len(nums) - 1)
```

Untuk mengecek keseimbangan, jangan memanggil `height()` di setiap simpul (O(n²)). Biarkan satu fungsi bantu mengembalikan tinggi, atau `-1` saat sub-pohon sudah tidak seimbang.

Di sistem nyata, pohon **menyeimbangkan dirinya**: AVL tree, red-black tree (dipakai di dalam banyak library standar) dan B-tree (database). Kamu tak akan menulisnya di wawancara, tapi kamu harus bisa mengatakan kenapa mereka ada: menjaga h dekat log n setelah insert dan delete.

### 9. Biaya

| Operasi | Seimbang | Terburuk (rantai) |
|---|---|---|
| Search / insert / delete | O(log n) | O(n) |
| Min / max | O(log n) | O(n) |
| Inorder (list terurut) | O(n) | O(n) |
| Ruang (rekursif) | O(log n) | O(n) |

:::tip[🧭 Cara mengenali soal BST]
- Datanya **terurut** atau harus dijaga terurut saat berubah.
- Kata-kata seperti **successor, predecessor, floor, ceiling, k-th terkecil, dalam rentang**.
- Soal menyebut "binary search tree" dan kamu bisa memakai aturan kiri/kanan.
- Kamu butuh operasi **berurutan** yang tak bisa dilakukan hash map.

Hanya pencarian berdasarkan key, tanpa urutan? Hash map lebih sederhana dan O(1). Array terurut yang tak pernah berubah? Binary search biasa sudah cukup.
:::

### Memilih caranya

| Kebutuhan | Pakai |
|---|---|
| Hanya pencarian | hash map |
| Data terurut yang tak pernah berubah | array terurut + binary search |
| Data terurut dengan insert dan delete, key berikutnya/sebelumnya | BST seimbang (atau library sorted container) |
| Hanya item terkecil atau terbesar, berulang | heap (lesson berikutnya) |
| Membangun pohon dari data terurut | nilai tengah sebagai akar, rekursif |

- ✅ Ordered map, query rentang, "berikutnya yang lebih besar", jadwal.
- 🚫 Pencarian key biasa (pakai hash map).
- 🚫 Menyisipkan data yang sudah terurut ke BST biasa (jadi rantai).

## ⚠️ Kesalahan umum

- Memvalidasi hanya terhadap induk, bukan meneruskan batas.
- Menganggap nilai sama valid padahal soal menyatakan tidak (sebutkan aturanmu).
- Di `delete`, lupa mengembalikan akar sub-pohon baru, sehingga pohon tidak tersambung lagi.
- Mencari di kedua sub-pohon padahal aturan BST memberi tahu yang mana.
- Menyisipkan data terurut ke BST biasa dan berharap O(log n).
- Memakai rekursi pada pohon degenerate yang sangat dalam.

## 🏆 Praktik terbaik

- [ ] Ucapkan invariant keras-keras: "kiri lebih kecil, kanan lebih besar, di setiap simpul".
- [ ] Pakai aturan untuk menyusuri **satu** jalur. Kalau kamu mengunjungi kedua sisi, tanyakan kenapa.
- [ ] Teruskan batas `low` dan `high` untuk validasi.
- [ ] Tangani tiga kasus delete secara terpisah, dan uji masing-masing.
- [ ] Sebut biaya sebagai O(h), lalu katakan "O(log n) jika seimbang".
- [ ] Sebut pohon penyeimbang diri (AVL, red-black, B-tree) saat ditanya kasus terburuk.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke teman kenapa mencari kata di kamus itu seperti mencari di BST, dan kenapa kamus yang dicetak dengan urutan salah (rantai) tidak berguna.

## 📐 Rancang

Kalender CareerPilot harus menjawab: "Kapan wawancara berikutnya setelah jam ini?", "Apakah slot waktu ini kosong?" dan "Tampilkan semua wawancara di antara dua tanggal". Wawancara sering ditambah, dipindah dan dibatalkan. Rancang struktur datanya dan sebutkan biaya tiap pertanyaan.

:::quiz
Tampilkan rancangan yang mungkin

- **Simpan wawancara di struktur terurut yang seimbang** dengan key waktu mulai (BST seimbang, atau sorted container seperti `sortedcontainers.SortedList`). Tambah, pindah (hapus + sisip) dan batal semuanya O(log n).
- **Wawancara berikutnya setelah t:** *ceiling* dari t (waktu mulai terkecil ≥ t, atau successor) — satu jalur ke bawah, O(log n).
- **Apakah slot ini kosong?** cari *floor* (wawancara sebelumnya) dan *ceiling* (berikutnya) lalu cek apakah slot baru muat di antaranya. O(log n).
- **Semua wawancara antara dua tanggal:** cari yang pertama ≥ awal, lalu telusuri inorder sampai melewati tanggal akhir. O(log n + k) untuk k hasil.
- **Kenapa bukan list biasa?** menyisipkan di tengah memindahkan item, dan pencarian butuh binary search plus urut ulang setelah perubahan.
- **Kenapa bukan hash map?** ia tak bisa menjawab "berikutnya setelah t" atau rentang.
- **Di database:** indeks pada `start_time` adalah B-tree dan memberi operasi yang sama; struktur di aplikasi penting saat data ada di memori.
- **Peringatan:** BST biasa yang diberi timestamp terurut menjadi rantai, jadi pakai yang menyeimbangkan diri.

**Aturan yang ditunjukkan:** saat kamu butuh data tetap terurut dengan pembaruan cepat plus query berikutnya/sebelumnya/rentang, pikirkan BST seimbang.
:::

### 📝 Daftar cek diri

- [ ] Aku menyebut operasi mana yang butuh urutan (berikutnya, sebelumnya, rentang)
- [ ] Aku membandingkan minimal list dan hash map
- [ ] Aku menyebut keseimbangan
- [ ] Aku memberi biaya tiap operasi

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::problem{id="dsa-s4-bst-basics" title="BST Basics" difficulty="easy" path="exercises/dsa/stage-4/05-bst-basics"}
Search, insert, terkecil dan terbesar dengan menyusuri satu jalur ke bawah.
:::

:::problem{id="dsa-s4-validate-kth" title="Validate a BST & k-th Smallest" difficulty="medium" path="exercises/dsa/stage-4/06-validate-kth"}
Batas, bukan hanya induk. Lalu k-th terkecil dengan stack sendiri pada rantai 30.000 simpul.
:::

:::problem{id="dsa-s4-sorted-to-balanced" title="Sorted Array to Balanced BST" difficulty="medium" path="exercises/dsa/stage-4/07-sorted-to-balanced"}
Bangun BST seimbang dari data terurut, dan cek keseimbangan dalam satu lintasan.
:::

:::problem{id="dsa-s4-bst-delete-floor-lca" title="BST: Delete, Floor/Ceiling and LCA" difficulty="hard" path="exercises/dsa/stage-4/08-bst-delete-floor-lca"}
Stretch: delete dengan tiga kasus, floor dan ceiling dalam O(h), dan lowest common ancestor tanpa pencarian penuh.
:::

:::hints
- `search`/`insert`: loop dengan `node = node.left if val < node.val else node.right`; tak perlu rekursi.
- `is_valid_bst`: fungsi bantu menerima `(node, low, high)`; anak kiri mendapat `high = node.val`, anak kanan mendapat `low = node.val`. Nilai sama tidak valid.
- `kth_smallest`: inorder iteratif; kurangi `k` setiap kali pop; kembalikan saat mencapai 0.
- `sorted_array_to_bst`: `mid = (lo + hi) // 2`; separuh kiri `lo..mid-1`, separuh kanan `mid+1..hi`.
- `is_balanced`: kembalikan `-1` dari fungsi bantu saat sub-pohon tidak seimbang; selain itu kembalikan tingginya.
- `delete`: selalu tugaskan hasilnya kembali (`root.left = delete(root.left, val)`); untuk dua anak, salin nilai terkecil sub-pohon kanan, lalu hapus di sana.
- `floor_ceiling`: ke kanan berarti nilai saat ini kandidat floor; ke kiri berarti kandidat ceiling; jika sama, kembalikan `(x, x)`.
- `lca_in_bst`: keduanya lebih kecil → kiri; keduanya lebih besar → kanan; selain itu kembalikan nilai saat ini.
:::

## ✅ Cek cepat

:::quiz
Kenapa mengecek tiap simpul hanya terhadap induknya tidak cukup untuk memvalidasi BST?

Sebuah simpul harus menaati batas **semua** leluhurnya, bukan hanya induknya. Nilai yang dalam di sub-pohon kanan 5 bisa lebih besar dari induknya sendiri dan tetap lebih kecil dari 5, yang melanggar aturan. Teruskan batas `low` dan `high` ke bawah, atau cek bahwa penelusuran inorder naik secara ketat.
:::

:::quiz
Kenapa menyisipkan 1, 2, 3, 4, 5 berurutan ke BST biasa membuat pencarian lambat?

Tiap nilai baru lebih besar dari semua sebelumnya, jadi selalu ke kanan. Pohon menjadi rantai setinggi n, dan search berbiaya O(n) bukan O(log n). Pohon penyeimbang diri (AVL, red-black) atau membangun dari tengah data terurut menjaga tinggi dekat log n.
:::

:::quiz
Saat menghapus simpul dengan dua anak, kenapa kita memakai inorder successor?

Successor adalah nilai terkecil di sisi kanan. Ia lebih besar dari semua di kiri dan lebih kecil dari semua yang lain di kanan, jadi menaruhnya di tempat simpul yang dihapus menjaga aturan BST tetap benar. Lalu kita menghapus successor itu sendiri, yang punya paling banyak satu anak.
:::

## 📚 Lanjut belajar

- [VisuAlgo: Binary Search Tree (interactive)](https://visualgo.net/en/bst)
- [Wikipedia: Self-balancing binary search tree](https://en.wikipedia.org/wiki/Self-balancing_binary_search_tree)
- [sortedcontainers: SortedList and SortedDict](https://grantjenks.com/docs/sortedcontainers/)

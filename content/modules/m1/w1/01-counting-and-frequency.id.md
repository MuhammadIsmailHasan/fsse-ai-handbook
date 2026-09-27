---
title: "Algoritma Hitung & Frekuensi"
summary: Hitung kemunculan dengan dictionary — pola di belakang analytics, deteksi duplikat, dan laporan skill CareerPilot-mu.
sourceHash: 59f0f73abd89
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Pakai **dictionary** sebagai penghitung tally
- Cari item paling sering (dan paling jarang), tangani nilai seri
- Deteksi **duplikat** dan temukan item yang muncul sekali
- Kenapa satu loop dengan dict lebih baik daripada dua loop bersarang
- `collections.Counter` — setelah bisa manual

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Dictionary (dict)** | Pasangan kunci → nilai, seperti kata dan artinya di kamus |
| **Key / value** | Yang kamu cari / yang kamu dapat kembali |
| **Frequency** | Berapa kali sesuatu muncul |
| **Tally** | Menambah satu pada hitungan |
| **`get(key, 0)`** | Ambil nilai, atau 0 jika kunci belum ada |
| **Tie** | Dua item dengan hitungan sama |
| **Duplicate** | Nilai yang muncul lebih dari sekali |
| **`Counter`** | Penghitung siap pakai dari Python |

## 🧠 Ide besarnya

Bayangkan menghitung suara di papan tulis saat pemilihan ketua kelas. Untuk setiap suara, kamu cari nama kandidat dan tambah satu tanda tally — tambah nama dulu jika belum ada di papan. Di akhir, baca hasilnya.

Papan itu adalah :term[dictionary]{bahasa="dictionary — kumpulan pasangan kunci-nilai, seperti kamus: kata → arti"}: **key** adalah nama, **value** adalah jumlah suara.

```python
votes = ["Ana", "Budi", "Ana", "Citra", "Ana", "Budi"]
tally = {}
for name in votes:
    tally[name] = tally.get(name, 0) + 1
print(tally)   # {'Ana': 3, 'Budi': 2, 'Citra': 1}
```

## ❓ Kenapa ini penting

Menghitung ada di belakang lebih banyak fitur daripada algoritma lain: skill teratas di lowongan, produk paling laku, email duplikat, error rate per endpoint, kata di dokumen, suara per kandidat.

Cara naif — untuk setiap item, jalan seluruh daftar dan hitung kecocokan — adalah O(n²) dan diam-diam mati pada data asli. Cara dictionary adalah satu kali jalan: sentuh setiap item sekali, tambah tally.

Belajar manual duluan juga artinya shortcut nanti (`Counter`, `GROUP BY` SQL, `value_counts` pandas) adalah sesuatu yang kamu pahami, bukan magic yang kamu copy.

## 📖 Langkah demi langkah

### 1. Dictionary dasar

```python
stock = {"apple": 5, "banana": 0}

stock["cherry"] = 12          # add or overwrite
print(stock["apple"])         # 5
print(stock.get("durian"))    # None — .get() doesn't crash on missing keys
print(stock.get("durian", 0)) # 0 — with a default
print("banana" in stock)      # True — checks KEYS

for fruit, amount in stock.items():
    print(fruit, amount)
```

Cari key di dict itu **cepat tidak peduli seberapa besar dict-nya** — Python langsung melompat ke sana daripada scanning. Itu rahasia di belakang semuanya dalam pelajaran ini.

### 2. Pola penghitungan

Tiga baris, dan kamu pakai berulang kali sepanjang karir: lihat item, baca hitungnya sekarang (0 jika baru), tulis kembali ditambah satu.

```python
def count_items(items):
    counts = {}
    for item in items:
        counts[item] = counts.get(item, 0) + 1
    return counts
```

Baca `counts.get(item, 0) + 1` sebagai: "hitungan sekarang, atau 0 jika baru — ditambah satu".

### 3. Item paling sering (dan tie)

```python
counts = {"python": 5, "sql": 5, "react": 3}

top_count = max(counts.values())                                 # 5
leaders = [skill for skill, c in counts.items() if c == top_count]
print(leaders)                                                   # ['python', 'sql']
```

`max(counts, key=counts.get)` return hanya **satu** key — mana pun yang pertama. Putuskan dengan sengaja apa yang terjadi pada tie: return semuanya? sort abjad?

### 4. Sort berdasarkan hitungan

```python
ranking = sorted(counts.items(), key=lambda pair: pair[1], reverse=True)
# [('python', 5), ('sql', 5), ('react', 3)]
```

`lambda` adalah fungsi kecil tanpa nama: `lambda pair: pair[1]` artinya "diberi pair, pakai elemen keduanya". Sort dapat pelajaran tersendiri nanti — untuk sekarang, resep ini cukup.

### 5. Duplikat dan unik

```python
emails = ["a@x.com", "b@x.com", "a@x.com"]

counts = count_items(emails)
duplicates = [e for e, c in counts.items() if c > 1]   # ['a@x.com']
uniques    = [e for e, c in counts.items() if c == 1]  # ['b@x.com']

# Only need "is there ANY duplicate?" — a set is enough:
has_duplicates = len(set(emails)) != len(emails)       # True
```

:term[Set]{bahasa="set/himpunan — kumpulan nilai unik tanpa urutan"} tahan hanya nilai unik, dan cek `x in some_set` itu cepat seperti dict.

### 6. Hitung berdasarkan property

Key tidak harus item itu sendiri — bisa apa pun yang kamu ambil darinya: kota, huruf pertama, bulan. Itu `GROUP BY` sebelum kamu pernah bertemu SQL.

Sering kali kamu hitung **field** dari setiap record, bukan record itu sendiri:

```python
jobs = [
    {"title": "Backend Dev", "city": "Jakarta"},
    {"title": "Data Analyst", "city": "Bandung"},
    {"title": "QA Engineer", "city": "Jakarta"},
]
per_city = {}
for job in jobs:
    city = job["city"]
    per_city[city] = per_city.get(city, 0) + 1
# {'Jakarta': 2, 'Bandung': 1}
```

### 7. `collections.Counter`

Pustaka standar Python punya ini siap pakai:

```python
from collections import Counter

skills = ["python", "sql", "python", "react"]
c = Counter(skills)
print(c["python"])        # 2
print(c.most_common(2))   # [('python', 2), ('sql', 1)]
```

:::tip
Tulis versi dictionary sampai otomatis (dan di interview, siap sedia). Di proyek asli, pakai `Counter` — lebih jelas dan sudah teruji.
:::

### Pilih setup-mu

Setiap pilihan di sini adalah trade-off:

| Pendekatan | Kecepatan untuk n item | Memori | Catatan |
|---|---|---|---|
| Loop bersarang | 🐢 n × n | Kecil | Hanya OK untuk daftar sangat kecil |
| Penghitung dict | 🚀 ~n | Satu entry per item berbeda | Pilihan default |
| `Counter` | 🚀 ~n | Sama | Kode lebih sedikit, helper ekstra |
| Sort lalu hitung tetangga | n log n | Kecil tambahan | Berguna kalau data sudah sorted atau memori terbatas |

- ✅ Frekuensi, histogram, "top N", duplikat, cek anagram.
- ✅ Normalize sebelum hitung (`.lower().strip()`), atau `"Python"` dan `"python "` hitung terpisah.
- 🚫 Jika kamu hanya butuh **ya/tidak** "pernah lihat?", `set` lebih sederhana daripada hitung.
- 🚫 Untuk **dataset besar** di database, biarkan database hitung (`GROUP BY` — Module 2).

## ⚠️ Kesalahan umum

- `counts[item] += 1` pada key baru → `KeyError`. Pakai `.get(item, 0) + 1`.
- Lupa normalize text sebelum hitung.
- Pakai `max(..., key=...)` dan diam-diam abaikan tie.
- Hitung di dalam loop bersarang "karena jalan di test 5-item ku".

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke orang non-programmer kenapa hitung dengan "papan tulis nama" (dictionary) jauh lebih cepat daripada baca ulang seluruh daftar suara untuk setiap suara tunggal. Pakai angka untuk bikin perbedaannya terasa asli.

## 📐 Rancang

CareerPilot akan baca lowongan pekerjaan di mana setiap punya field `skills` seperti `"Python, SQL, Docker"`. Rancang (dalam pseudocode) function yang return **top 5 skill** di seluruh lowongan.

Putuskan: Bagaimana kamu split dan bersihkan setiap skill? Bagaimana kamu perlakukan `"python"` vs `"Python "`? Apa yang terjadi pada tie di posisi 5? Apa kalau lowongan tidak punya skill?

:::quiz
Lihat contoh rancangan

```text
counts = dict kosong
untuk setiap lowongan:
    jika field skill kosong: lewati
    untuk setiap raw_skill di skills.split(","):
        skill = raw_skill.strip().lower()
        jika skill == "": lewati
        counts[skill] = counts.get(skill, 0) + 1
ranking = sort counts by (count turun, skill nama naik)
return 5 pertama dari ranking
```

Tie-break pada **nama** bikin output stabil: jalankan dua kali selalu dapat top 5 yang sama.
:::

### 📝 Checklist review mandiri

- [ ] Aku normalize case dan spasi
- [ ] Skill kosong dan lowongan kosong tidak crash
- [ ] Tie ditangani dengan sengaja (dan aku bisa bilang bagaimana)
- [ ] Rancangan ku pakai satu kali jalan untuk hitung, bukan scanning bersarang

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

## 🧸 Tally semuanya

:::exercise{path="exercises/m1/w1/01-counting" ai="no-ai" title="Toolkit hitung"}
Di `counting.py` implementasi, **tanpa** `collections.Counter`:

- `count_items(items)` → dict item → hitung
- `most_frequent(items)` → daftar item paling sering, sorted A→Z; `[]` untuk input kosong
- `first_duplicate(items)` → item pertama yang muncul **kedua kali** saat baca kiri ke kanan, atau `None`
- `count_skills(skill_strings)` → hitung skill dari string seperti `"Python, SQL"`, tidak sensitif case dan dipotong
- `top_skills(skill_strings, n)` → daftar `(skill, count)` sorted hitung turun, lalu skill A→Z, paling `n` item
:::

:::hints
- `first_duplicate`: jalan daftar dengan `seen` set. Saat item sudah ada di `seen`, return itu.
- `most_frequent`: temukan hitung tertinggi, kumpul semua key dengan hitung itu, lalu `sorted(...)`.
- Sort hitung turun dan nama naik dengan `key=lambda pair: (-pair[1], pair[0])`.
- `"".split(",")` return `[""]` — lewati skill kosong setelah potong.
:::

### 🏆 Tujuan stretch

Tambah `are_anagrams(a, b)` yang abaikan spasi dan case: `"Dormitory"` / `"Dirty room"` → `True`. Pakai `count_items`-mu.

## ✅ Cek cepat

:::quiz
Apa yang dilakukan `counts.get("x", 0) + 1` saat `"x"` belum ada di `counts`?

`.get` return default `0`, jadi ekspresi itu `1`. Assign kembali ciptakan key dengan hitung 1.
:::

:::quiz
Kenapa penghitung dictionary kira-kira n langkah sementara versi loop bersarang kira-kira n × n?

Versi dict baca setiap item sekali dan loncat langsung ke penghitungnya. Versi bersarang scan ulang seluruh daftar untuk setiap item.
:::

:::quiz
Kamu hanya butuh tahu apakah daftar punya duplikat. Apa pendekatan paling sederhana?

Bandingkan `len(set(items))` dengan `len(items)` — jika set lebih kecil, sesuatu terulang.
:::

## 📚 Lanjut belajar

- [Tutorial Python: Dictionaries](https://docs.python.org/3/tutorial/datastructures.html#dictionaries)
- [Dokumentasi Python: collections.Counter](https://docs.python.org/3/library/collections.html#collections.Counter)

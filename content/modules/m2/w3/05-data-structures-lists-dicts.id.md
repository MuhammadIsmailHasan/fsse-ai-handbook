---
title: "Struktur Data: List, Dict, Set & Tuple"
summary: Pilih koleksi bawaan yang tepat, pahami biayanya, dan gunakan modul collections dan dataclass untuk data yang lebih jelas.
sourceHash: 3e29c91e9e6c
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa itu `list`, `tuple`, `dict` dan `set` — dan berapa biaya kinerjanya
- Operasi dict dan set yang sering kamu gunakan di API
- `collections`: `Counter`, `defaultdict`, `deque`, `namedtuple`
- Cara merepresentasikan record: dict vs **`dataclass`** vs `TypedDict`
- Data bertingkat (seperti JSON) tanpa kebingungan, dan menyalinnya dengan aman

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **`list`** | Urutan yang bisa diubah |
| **`tuple`** | Urutan tetap, tidak bisa diubah |
| **`dict`** | Pasangan kunci–nilai, cari dengan kunci |
| **`set`** | Kumpulan nilai unik, cepat untuk "ada nggak?" |
| **Hashable** | Nilai stabil cukup untuk jadi kunci dict atau anggota set |
| **O(1) vs O(n)** | Langsung dicari vs periksa semua item |
| **`Counter`** | Penghitung: berapa kali setiap nilai muncul |
| **`defaultdict`** | Dict yang buat nilai hilang otomatis |
| **`dataclass`** | Kelas ringkas untuk data, dengan nama field |
| **Deep copy** | Salinan yang tidak bagikan data di dalamnya |

## 🧠 Ide besarnya

Memilih struktur data itu seperti **memilih wadah di dapur**:

| Wadah | Versi dapur | Python |
|---|---|---|
| Barisan toples bernomor yang bisa diatur ulang | rak | `list` |
| Kotak makan siang tertutup dengan kompartemen tetap | lunch box | `tuple` |
| Laci berlabel ("sendok", "pisau") | lemari laci | `dict` |
| Tas bahan unik — "punya bawang nggak?" | cek stok | `set` |

Wadah yang tepat membuat pekerjaan jadi jelas dan cepat; wadah yang salah membuat hal sederhana jadi lambat dan repot.

## ❓ Kenapa ini penting

Setiap request dan response API adalah data: list pekerjaan, dict per pekerjaan, set izin, tuple koordinat. Memilih dengan tepat memberi kamu **kode yang mudah dibaca** dan **operasi cepat** — Big-O yang kamu ukur di track DSA.

Memilih salah itu diam-diam mahal:

```python
blocked_user_ids = [3, 17, 42, ...]          # 100,000 ids
for request in requests:                     # 10,000 requests
    if request.user_id in blocked_user_ids:  # O(n) scan each time → a billion comparisons
        reject(request)
```

```python
job = ["Backend Dev", "Kopi Data", 12000000, True]
salary = job[2]          # what's index 2? what if someone inserts a field?
```

Yang pertama adalah list dipakai di mana set seharusnya (cek daftar tamu nama demi nama daripada pakai index). Yang kedua adalah data tanpa label, jadi pembaca harus menebak.

## 📖 Langkah demi langkah

### 1. Biaya sekilas

| Operasi | `list` | `tuple` | `dict` | `set` |
|---|---|---|---|---|
| ambil dengan index | O(1) | O(1) | — | — |
| ambil dengan kunci | — | — | O(1) rata-rata | — |
| `x in …` | **O(n)** | **O(n)** | O(1) rata-rata (kunci) | O(1) rata-rata |
| append / add | O(1) | ✗ immutable | O(1) rata-rata | O(1) rata-rata |
| sisip/hapus di awal | **O(n)** | ✗ | — | — |
| terurut | ✅ | ✅ | ✅ (urutan insert) | ❌ |
| duplikat | ✅ | ✅ | kunci unik | ❌ unik |
| hashable (bisa jadi kunci dict) | ❌ | ✅ (kalau isi hashable) | ❌ | ❌ (`frozenset` ✅) |

### 2. Tuple: record tetap dan kunci dict

```python
point = (-6.2, 106.8)
lat, lng = point

visits: dict[tuple[str, str], int] = {}
visits[("Jakarta", "2026-09-13")] = 120      # composite key
```

### 3. Dict: tulang punggung backend Python

```python
job = {"title": "Backend Dev", "salary": 12_000_000}

job.get("city", "Remote")                 # default instead of KeyError
job.setdefault("skills", []).append("sql")
job |= {"remote": True}                   # merge/update (3.9+)
{**job, "salary": 13_000_000}             # new dict with a change (original untouched)

for key, value in job.items(): ...
{k: v for k, v in job.items() if v is not None}   # drop None values

by_id = {j["id"]: j for j in jobs}        # index for O(1) lookups
```

### 4. Set: cek keanggotaan dan perbandingan

Set menjawab "ada di dalamnya nggak?" dalam satu langkah, sekecil atau sebesar apa pun — itulah kenapa cek izin dan blocklist harus pakai set, bukan list.

```python
required = {"python", "sql", "docker"}
mine = {"python", "sql", "react"}

required & mine        # {'python', 'sql'}      intersection — what I have
required - mine        # {'docker'}             difference — what I'm missing
required | mine        # union
required <= mine       # False                  subset: do I have everything?

seen: set[str] = set()
if url in seen: ...    # O(1) duplicate check
```

### 5. Modul `collections`

```python
from collections import Counter, defaultdict, deque, namedtuple

Counter(skills).most_common(3)                # counting (Module 1!)

by_city = defaultdict(list)                   # missing keys start as []
for job in jobs:
    by_city[job["city"]].append(job)

recent = deque(maxlen=100)                    # O(1) add/remove at both ends; keeps the last 100
recent.append(event)

Point = namedtuple("Point", "lat lng")        # tuple with names (dataclasses are usually nicer)
```

### 6. Record: dict, dataclass atau TypedDict?

Aturan jempol: dict untuk data yang lewat (JSON masuk, JSON keluar), `dataclass` kalau bentuk yang sama lewat kodenya sendiri dan kamu ingin nama, default dan typo tertangkap.

```python
from dataclasses import dataclass, field

@dataclass(frozen=True, slots=True)
class JobListing:
    title: str
    company: str
    salary_max: int | None = None
    skills: tuple[str, ...] = ()
    tags: list[str] = field(default_factory=list)   # never a bare [] default

job = JobListing("Backend Dev", "Kopi Data", 12_000_000, ("python", "sql"))
job.title            # attribute access, autocomplete, typo-safe
```

| Gaya record | ✅ | ❌ |
|---|---|---|
| `dict` | fleksibel, map langsung ke JSON | typo di kunci ketahuan hanya saat runtime; tidak ada autocomplete |
| `@dataclass` | field jelas, default, `__eq__`/`__repr__` gratis, `frozen` immutable | konversi ke/dari JSON sendiri (`asdict`) |
| `TypedDict` | type-check kunci dict sambil tetap dict | tidak ada validasi saat runtime |
| Pydantic model (Module 3) | **validasi** runtime + konversi JSON | dependensi tambahan |

Bentuk umum: **dict di tepi** (JSON masuk/keluar), **dataclass/model dalam** logika bisnis kamu.

### 7. Data bertingkat dengan aman

```python
payload = {"user": {"profile": {"city": "Jakarta"}}}

city = payload.get("user", {}).get("profile", {}).get("city")   # no KeyError on missing levels
```

Menyalin (recap DSA Stage 1): `dict.copy()` itu dangkal; dict/list di dalamnya dibagikan. Pakai `copy.deepcopy` atau bangun struktur baru.

### Pilih setup kamu

Setiap pilihan di sini adalah trade-off:

| Pilihan | ✅ | ❌ |
|---|---|---|
| `list` untuk lookup | sederhana | O(n) `in` |
| `set`/`dict` index | O(1) lookup | memori lebih; tidak boleh duplikat / perlu kunci hashable |
| `tuple` | immutable, hashable, ringan | tidak bisa ubah; field by position |
| frozen dataclass | aman dibagikan, hashable | buat object baru untuk ubah (`dataclasses.replace`) |
| `defaultdict` | kode grouping lebih singkat | baca kunci hilang **menciptakannya** diam-diam |

- ✅ `set` untuk keunikan/keanggotaan, `dict` untuk lookup dengan kunci, `list` untuk urutan, `tuple` untuk record tetap dan kunci komposit.
- ✅ Dataclass untuk record domain yang lewat kodemu.
- 🚫 Jangan pakai list of pairs kalau kamu butuh lookup dengan kunci.
- 🚫 Jangan pakai tuple posisional untuk record dengan banyak field — nama cegah bug.

## ⚠️ Kesalahan umum

- `x in big_list` dalam loop.
- Mutable default field di dataclass (`tags: list = []` raise error — memang seharusnya).
- Pakai `defaultdict` lalu nggak sengaja buat kunci dengan membacanya.
- Harap `set` jaga urutan.
- Ubah dict saat iterasi (`RuntimeError: dictionary changed size`).

:::revoshop
Di RevoShop, cari tempat di mana list item dicek keanggotaan atau duplikat (contoh: item cart, product id di order, role yang diizinkan). Apakah `set` atau dict index buat lebih jelas atau lebih cepat? Juga lihat `app/schemas/` — marshmallow schema ubah dict jadi data yang sudah divalidasi. Sama dengan dataclass atau beda?
:::

## 🏆 Praktik terbaik

- [ ] Pilih koleksi berdasarkan **operasi yang kamu butuh** (lookup, urutan, keunikan, mutability).
- [ ] Bangun **index** `dict`/`set` **sekali** kalau kamu lookup berkali-kali.
- [ ] Pakai `dict.get` dengan default dan `setdefault`/`defaultdict` untuk grouping.
- [ ] Pakai **`@dataclass`** (sering `frozen=True, slots=True`) untuk record internal; `field(default_factory=list)` untuk default yang bisa ubah.
- [ ] Jaga dict bentuk JSON di tepi; konversi ke object typed dalam.
- [ ] Lebih suka kembalikan **koleksi baru** daripada ubah input.
- [ ] Pakai operasi set (`&`, `-`, `|`, `<=`) untuk perbandingan izin dan skill.
- [ ] Tambah type hint ke koleksi: `list[JobListing]`, `dict[int, User]`, `set[str]`.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke seseorang bukan programmer kenapa cek "bahan ini ada di stok nggak?" cepat dengan tas berlabel berisi item unik tapi lambat dengan kuitansi belanja panjang. Hubungkan ke `set` vs `list`.

## 📐 Rancang

Untuk fitur **"skill gap"** CareerPilot, pilih struktur data untuk:
1. Skill yang wajib di satu pekerjaan
2. Skill kamu
3. Berapa banyak target job butuh setiap skill yang kurang
4. Record job listing yang lewat antar fungsi
5. 50 job id yang terakhir dilihat (terbaru dulu, tidak duplikat)

:::quiz
Lihat contoh rancangan

1. `frozenset[str]` (unik, hashable, dibanding dengan operasi set)
2. `set[str]`
3. `Counter[str]` — untuk setiap job, `counter.update(job.required_skills - user_skills)`
4. `@dataclass(frozen=True, slots=True) class JobListing` dengan `required_skills: frozenset[str]`
5. `deque(maxlen=50)` plus hapus id sebelum tambah lagi (size kecil bikin `remove` murah), atau `dict` yang dipakai sebagai ordered set (`dict.fromkeys`) dipotong jadi 50.
:::

### 📝 Checklist review mandiri

- [ ] Keunikan dan keanggotaan pakai set
- [ ] Hitung pakai `Counter`
- [ ] Record typed dan immutable
- [ ] Aku pertimbang urutan dan batas ukuran untuk "item terbaru"

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m2/w3/05-data-structures" ai="no-ai" title="Skills gap engine"}
Implementasi mesin skills gap kecil di `skills_gap.py` dengan dataclass frozen `JobListing`, operasi set untuk matching, `Counter` untuk demand skill kurang, `defaultdict` untuk grouping, dan struktur "recently viewed" terbatas. Satu test cek lookup keanggotaan tetap cepat di input besar.
:::

:::hints
- `JobListing.from_dict(data)` harus normalize skill jadi `frozenset` dari string lowercase, trimmed.
- Match score: `len(required & mine) / len(required)` — tentukan apa yang terjadi kalau job tidak butuh apa-apa.
- `RecentlyViewed.add(id)` hapus id dulu kalau ada, lalu append ke kiri.
:::

### 🏆 Tantangan plus

Tambah `to_dict()` di `JobListing` kembalikan data siap JSON (skill sebagai list terurut) pakai `dataclasses.asdict`, dan test round-trip.

## ✅ Cek cepat

:::quiz
Kenapa tuple bisa jadi kunci dict tapi list tidak bisa?

Kunci dict harus hashable, yang butuh immutability. Tuple (dari item hashable) tidak bisa ubah, jadi hash-nya tetap valid; list bisa.
:::

:::quiz
`required - mine` untuk dua set skill memberikan apa?

Skill yang wajib tapi kamu tidak punya (set difference).
:::

:::quiz
Kenapa pakai `field(default_factory=list)` di dataclass?

Default `[]` biasa akan dibagikan setiap instance; `default_factory` buat list baru per object (dataclass malahan raise error untuk default mutable).
:::


## 📚 Lanjut belajar

- [Python tutorial: Data Structures](https://docs.python.org/3/tutorial/datastructures.html)
- [Python docs: collections](https://docs.python.org/3/library/collections.html)
- [Python docs: dataclasses](https://docs.python.org/3/library/dataclasses.html)

---
title: "Setup Python & Gaya Python"
summary: Cara Python benar-benar menjalankan kode kamu — interpreter, REPL, environment. Model data Python, gaya idiomatis, PEP 8 dengan Ruff, dan kebiasaan yang membuat code review lancar.
sourceHash: 4d6a344fd9b4
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Bagaimana Python benar-benar menjalankan kode kamu (interpreter, REPL, virtual environment recap)
- Model **"segala sesuatu adalah object"**: nama, object, bisa diubah atau tidak
- Gaya **Pythonic**: pemberian nilai ke banyak variabel, f-strings, nilai dianggap benar/salah, `enumerate`, `zip`, membuat list dalam satu baris, `with`
- **PEP 8** dan pemeriksa otomatis dengan **Ruff**
- **EAFP** vs **LBYL** — cara Python menangani "bagaimana kalau tidak ada?"

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Interpreter** | Program yang membaca dan menjalankan kode Python |
| **REPL** | Mode interaktif di mana kamu mengetik satu baris dan langsung lihat hasilnya |
| **Object** | Segala nilai di Python: angka, teks, fungsi, class |
| **Nama (variable)** | Label penunjuk nilai, bukan kotak yang menyimpan nilai |
| **Bisa diubah / tidak** | Nilai dapat diubah di tempat / tidak dapat |
| **Pythonic** | Ditulis seperti yang diharapkan developer Python berpengalaman |
| **Comprehension** | Membuat list atau dict dalam satu baris yang mudah dibaca |
| **Nilai dianggap benar/salah** | Hal kosong dianggap salah; tidak perlu bandingkan dengan `== True` |
| **PEP 8** | Panduan gaya komunitas Python untuk kode |
| **Ruff** | Alat cepat yang memeriksa dan merapikan kode sesuai gaya itu |
| **EAFP** | "Coba dulu, tangani error nanti" daripada cek semua dulu |

## 🧠 Ide besarnya

Dua kalimat bisa berarti hal yang sama, tapi yang satu terdengar alami di telinga pembicara asli. :term[Pythonic]{bahasa="Pythonic — gaya menulis yang wajar dan idiomatis menurut komunitas Python"} adalah Python yang ditulis seperti yang diharapkan developer berpengalaman untuk membacanya.

Bukan tentang menjadi pintar. Ini tentang **dipahami dengan cepat** oleh orang lain — termasuk kamu sendiri enam bulan kemudian.

## ❓ Kenapa ini penting

Python menawarkan banyak cara untuk melakukan hal yang sama, jadi tim butuh satu gaya bersama. Hasilnya:

- code review membahas logika, bukan format,
- siapa pun bisa membaca kode siapa pun dengan cepat,
- dan bug biasa (argument bisa diubah sebagai default, `== None`, nama terabaikan) terdeteksi otomatis.

Kode yang bukan Pythonic tetap jalan, tapi menyembunyikan bug:

```python
i = 0
result = []
while i < len(jobs):
    if jobs[i]["remote"] == True:
        if len(jobs[i]["skills"]) != 0:
            result.append(jobs[i]["title"].upper())
    i = i + 1
```

Lima kesempatan untuk membuat kesalahan (off-by-one, `== True`, index errors). Versi Pythonic mengatakan hal yang sama dalam satu baris:

```python
result = [job["title"].upper() for job in jobs if job["remote"] and job["skills"]]
```

## 📖 Langkah demi langkah

### 1. Menjalankan Python

| Cara | Kapan |
|---|---|
| `uv run python` / `python` (REPL) | coba cepat; `help(obj)`, `dir(obj)` |
| `uv run python script.py` | jalankan file |
| `uv run python -m package.module` | jalankan module di dalam package (Lesson 09) |
| IPython / Jupyter | eksplorasi, pekerjaan data |

### 2. Nama menunjuk ke object

Nama adalah **label koper**, bukan kotak: dua label bisa menempel di tas yang sama, jadi mengubah tas lewat satu label mengubah apa yang label lain lihat.

Recap dari DSA Stage 1: variable adalah **nama yang terikat ke object**. Setiap object punya **tipe**, **nilai**, dan **identitas**.

```python
a = [1, 2]
b = a            # same object
b.append(3)      # a is [1, 2, 3] too
a is b           # True — identity
a == [1, 2, 3]   # True — equality
```

Pakai `is` hanya untuk singleton: `if value is None:`.

### 3. Idiom yang kamu pakai setiap hari

```python
# Unpacking
first, *rest = ["python", "sql", "docker"]
lat, lng = coordinates
name, _ = full_name.split(" ", 1)          # _ = "ignored"

# Swap without a temp variable
a, b = b, a

# enumerate and zip instead of index loops
for position, job in enumerate(jobs, start=1): ...
for name, score in zip(names, scores, strict=True): ...

# Truthiness
if skills:                                  # not: if len(skills) != 0
    ...

# Conditional expression
label = "Remote" if job["remote"] else job["city"]

# Chained comparison
if 0 <= score <= 100: ...

# dict.get with default, setdefault
count = counts.get(skill, 0)

# f-strings with formatting and debugging
print(f"{salary:,}")        # 12,000,000
print(f"{ratio:.1%}")       # 45.3%
print(f"{job_id=}")         # job_id=42

# Context managers close resources for you
with open("jobs.csv", encoding="utf-8") as file:
    header = file.readline()

# any / all with generators
has_python = any("python" in job["skills"] for job in jobs)
```

### 4. EAFP vs LBYL

LBYL adalah cek jalan sepuluh kali sebelum menyeberang; EAFP adalah menyeberang hati-hati dan tahu apa yang dilakukan jika mobil datang. Python lebih suka yang kedua, karena situasi bisa berubah antara cek kamu dan aksi kamu.

| Gaya | Artinya | Contoh |
|---|---|---|
| **LBYL** — Lihat Dulu Sebelum Loncat | cek dulu | `if key in data: value = data[key]` |
| **EAFP** — Lebih Mudah Minta Maaf daripada Izin | coba, tangani kegagalan spesifik | `try: value = data[key] except KeyError: …` |

Python sering pilih EAFP, khususnya di mana cek dan aksi bisa race (file, network, database): file bisa hilang antara `os.path.exists()` dan `open()`.

```python
try:
    config = json.loads(path.read_text())
except FileNotFoundError:
    config = DEFAULT_CONFIG
```

### 5. PEP 8 dalam satu tabel

| Hal | Gaya |
|---|---|
| variable, fungsi | `snake_case` |
| class | `PascalCase` |
| constant | `UPPER_SNAKE_CASE` |
| semi-pribadi | `_leading_underscore` |
| indent | 4 spasi |
| panjang baris | ~88–120 karakter (pilihan tim) |
| import | atas file: standard library, third-party, lokal — dipisah baris kosong |
| perbandingan | `is None`, `is not None`; jangan pernah `== True` |

### 6. Biarkan Ruff mengerjakannya

[Ruff](https://docs.astral.sh/ruff/) adalah linter **dan** formatter yang sangat cepat:

```bash
uv add --dev ruff
uv run ruff format .          # format code
uv run ruff check . --fix     # lint and auto-fix what's safe
```

```toml
# pyproject.toml
[tool.ruff]
line-length = 100

[tool.ruff.lint]
select = ["E", "F", "I", "B", "UP", "SIM"]   # errors, pyflakes, isort, bugbear, pyupgrade, simplify
```

`B` (bugbear) menangkap hal seperti argument bisa diubah sebagai default; `UP` memodernisasi syntax; `SIM` sarankan kode lebih sederhana.

### Memilih setup kamu

Setiap pilihan di sini adalah trade-off:

| Pilihan | ✅ | ❌ |
|---|---|---|
| Comprehension | ringkas, cepat | tidak terbaca saat nested atau punya efek samping |
| Loop eksplisit | ruang untuk langkah dan komentar | lebih panjang |
| EAFP | tidak ada race antara cek dan aksi; happy path bersih | exception sebagai control flow bisa sembunyikan logika kalau berlebihan |
| LBYL | eksplisit | race untuk resource eksternal; pencarian duplikat |
| Lint rule ketat | tangkap bug awal | noise awal di kode lama |

- ✅ Pakai idiom yang buat intent jelas (`enumerate`, unpacking, `any`, `with`).
- ✅ Otomasi gaya dengan formatter + linter di editor **dan** CI.
- 🚫 Jangan tulis one-liner yang butuh komentar untuk dijelaskan.
- 🚫 Jangan pakai comprehension untuk efek samping (`[print(x) for x in items]`).

## ⚠️ Kesalahan umum

- `== None`, `== True`.
- Argument bisa diubah sebagai default.
- Variable bernama `list`, `dict`, `str`, `id`.
- Buka file tanpa `with` atau `encoding`.
- One-liner pintar yang tidak ada yang bisa debug.

:::revoshop
RevoShop punya `.pylintrc` dan bagian *Code Quality & Security* di README-nya. Jalankan `pylint app` (atau `uv run ruff check app` kalau kamu coba Ruff) di repo. Pilih **tiga** peringatan dan jelaskan apa yang setiap satu lindungi. Kamu temukan nama terabaikan (`id`, `type`, `filter`) di route atau service kamu?
:::

## 🏆 Praktik terbaik

- [ ] Format dengan **`ruff format`** dan lint dengan **`ruff check`** (atau Black + Flake8) — config yang sama lokal dan di CI.
- [ ] Ikuti penamaan **PEP 8**; jangan pernah terabaikan built-in (`list`, `dict`, `id`, `type`, `input`).
- [ ] `is None` / `is not None`; nilai dianggap benar/salah untuk cek kosong.
- [ ] Pakai `with` untuk file, lock, session database — apa pun yang harus ditutup.
- [ ] Pilih `enumerate`/`zip(strict=True)` daripada aritmatika index.
- [ ] Selalu pass `encoding="utf-8"` saat buka file teks.
- [ ] Jaga comprehension ke satu `for` dan satu `if`; sebaliknya pakai loop.
- [ ] Target Python modern (3.12+) dan biarkan rule `UP` Ruff modernisasi syntax.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan EAFP vs LBYL pakai contoh kehidupan nyata (mis. cek apakah toko buka sebelum pergi ke sana, lawan pergi dan tangani "tutup"). Kapan "cek dulu" gagal dalam software?

## 📐 Rancang

Tulis ulang fungsi ini dalam gaya Pythonic dan daftar setiap peningkatan yang kamu buat:

```python
def summary(data):
    output = ""
    count = 0
    for i in range(len(data)):
        if data[i]["salary"] != None:
            if data[i]["remote"] == True:
                count = count + 1
                output = output + str(count) + ". " + data[i]["title"] + "\n"
    if len(output) == 0:
        return "No remote jobs with salary"
    return output
```

:::quiz
Tunjukkan kemungkinan rewrite

```python
def summary(jobs: list[dict]) -> str:
    matches = [job for job in jobs if job["salary"] is not None and job["remote"]]
    if not matches:
        return "No remote jobs with salary"
    return "".join(f"{number}. {job['title']}\n" for number, job in enumerate(matches, start=1))
```

Peningkatan: nama deskriptif; `is not None`; nilai dianggap benar/salah alih-alih `== True`/`len() == 0`; filtering terpisah dari formatting; `enumerate(start=1)` alih-alih counter manual; f-strings alih-alih concatenation; `"".join` alih-alih pembangunan string berulang; type hint.
:::

### 📝 Checklist self-review

- [ ] Tidak ada loop berbasis index tersisa
- [ ] Filtering dan formatting adalah langkah terpisah
- [ ] Saya bisa namai setiap peningkatan dan kenapa itu penting

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m2/w3/01-pythonic-syntax" ai="no-ai" title="Buat Pythonic"}
`legacy.py` berisi empat fungsi kerja tapi bukan Pythonic. Tulis ulang di `pythonic.py` dengan perilaku sama. Test cek perilaku **dan** gaya: tidak ada `range(len(...))`, tidak ada `== None`/`== True`, tidak ada nama terabaikan, dan file dibuka dengan `with` dan `encoding`.
:::

:::hints
- Salin satu fungsi sekaligus, jalankan test, lalu refactor.
- `enumerate(items, start=1)` ganti counter manual.
- `" ".join(parts)` bangun string dari list.
- Test pakai module `ast` Python untuk tangkap `range(len(...))`.
:::

### 🏆 Stretch goal

Tambah Ruff ke project latihan (`uv add --dev ruff`) dan buat `uv run ruff check m2/w3/01-pythonic-syntax --select E,F,B,UP,SIM` lulus di file kamu.

## ✅ Cek cepat

:::quiz
Kenapa `if skills:` dipilih daripada `if len(skills) > 0:`?

Lebih ringkas, idiomatis, dan bekerja untuk koleksi apa pun (list, dict, set, string) dan cek `None` gabung dengan kosong.
:::

:::quiz
Apa yang ditambah `zip(a, b, strict=True)`?

Muncul `ValueError` kalau iterable punya panjang berbeda, alih-alih senyap drop item lebih.
:::


## 📚 Lanjut belajar

- [PEP 8 — Panduan Gaya untuk Kode Python](https://peps.python.org/pep-0008/)
- [Dokumentasi Ruff](https://docs.astral.sh/ruff/)
- [Glosarium Python: EAFP](https://docs.python.org/3/glossary.html#term-EAFP)

---
title: "Filter, Agregasi & Menggabung Data"
summary: Ubah data mentah jadi jawaban — saring dengan comprehension, kelompokkan dan ringkas, lalu gabung dari beberapa sumber data.
sourceHash: d39e64e69722
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- **Filter** dan **transform** dengan list/dict comprehension
- **Aggregate**: total, rata-rata, min/max per kelompok ("group by")
- **Combine**: `zip`, gabungkan dua daftar record berdasarkan id, merge dictionary
- **De-duplicate** sambil tetap jaga urutan
- Bagaimana ini sama dengan SQL (`WHERE`, `GROUP BY`, `JOIN`) yang akan kamu tulis di Module 2

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Filter** | Ambil hanya item yang kamu mau |
| **Transform / map** | Ubah bentuk setiap item |
| **Comprehension** | Saring dan ubah dalam satu baris yang rapi |
| **Aggregate** | Ringkas banyak baris jadi satu angka |
| **Group by** | Ringkas per kategori (per kota, per status) |
| **Join** | Gabung data dari sumber lain berdasarkan id yang sama |
| **`zip`** | Pasangkan dua daftar item demi item |
| **De-duplicate** | Buang yang ganda, tetap jaga urutan |
| **Lookup dict** | Dictionary yang dibangun untuk pencocokkan cepat |

## 🧠 Ide besarnya

Pengolahan data itu seperti antrean dapur restoran:

1. **Filter** — buang yang tidak perlu (*"hanya job remote"*)
2. **Transform** — ubah bentuk yang tersisa (*"hanya nama job dan gaji"*)
3. **Group & aggregate** — ringkas (*"rata-rata gaji per kota"*)
4. **Combine** — tambah data dari sumber lain (*"pasang rating perusahaan ke setiap job"*)

Hampir setiap laporan, dashboard, atau API response adalah kombinasi dari empat langkah ini.

## ❓ Kenapa ini penting

Data mentah tidak pernah jadi jawaban. Seseorang tanya "berapa rata-rata gaji per kota untuk job remote?" dan kamu dapat daftar 5.000 record yang berantakan. Jalan dari yang satu ke yang lain selalu sama: filter → transform → group → combine.

Bonus: empat langkah ini persis sama dengan SQL `WHERE`, `SELECT`, `GROUP BY` dan `JOIN` yang akan kamu kenal di Module 2. Kerjakan di Python dulu berarti SQL akan terasa akrab, bukan asing.

## 📖 Langkah demi langkah

### 1. Comprehension: filter + transform dalam satu baris

```python
prices = [45_000, 120_000, 30_000, 99_000]

cheap = [p for p in prices if p < 50_000]          # filter
with_tax = [p * 111 // 100 for p in prices]        # transform
cheap_with_tax = [p * 111 // 100 for p in prices if p < 50_000]   # both
```

Baca seperti: **[apa yang disimpan** `for` **setiap item** `in` **daftar** `if` **kondisi]**.

Dict dan set comprehension bekerja sama:

```python
price_by_name = {item["name"]: item["price"] for item in items}
unique_cities = {job["city"] for job in jobs}
```

:::tip[Jaga comprehension tetap sederhana]
Satu `for` dan satu `if` itu bagus. Kalau kamu perlu loop bertingkat atau beberapa kondisi, loop `for` biasa biasanya lebih mudah dibaca.
:::

### 2. Agregasi bawaan

```python
salaries = [job["salary"] for job in jobs]

total = sum(salaries)
average = sum(salaries) / len(salaries) if salaries else 0
highest_job = max(jobs, key=lambda job: job["salary"])   # the whole record, not just the number
any_remote = any(job["remote"] for job in jobs)
all_verified = all(job["verified"] for job in jobs)
```

### 3. Group by

Polanya adalah dictionary penghitung lagi, tapi nilainya daftar (atau total yang terus bertambah) bukan hanya angka.

Polanya dari Materi 01, tapi kumpulkan **nilai** bukan hitung:

```python
sales = [("Jakarta", 100), ("Bandung", 50), ("Jakarta", 30)]

by_city: dict[str, list[int]] = {}
for city, amount in sales:
    by_city.setdefault(city, []).append(amount)   # create the list the first time
# {'Jakarta': [100, 30], 'Bandung': [50]}

summary = {
    city: {"total": sum(amounts), "count": len(amounts), "average": sum(amounts) / len(amounts)}
    for city, amounts in by_city.items()
}
```

`setdefault(key, [])` mengembalikan daftar yang ada, atau masukkan dan kembalikan daftar kosong baru. (`collections.defaultdict(list)` melakukan hal yang sama otomatis.)

### 4. Gabung dengan `zip`

```python
names = ["Ana", "Budi", "Citra"]
scores = [88, 92, 79]

for name, score in zip(names, scores):
    print(name, score)

report = dict(zip(names, scores))   # {'Ana': 88, 'Budi': 92, 'Citra': 79}
```

`zip` berhenti di daftar **paling pendek** — panjang tidak sama diam-diam terpotong. Pakai `zip(a, b, strict=True)` (Python 3.10+) untuk dapat error sebagai gantinya.

### 5. Join record berdasarkan id

Bangun dictionary lookup dulu, lalu jalan daftar lain sekali. Loop dalam loop untuk cocokkan id adalah versi O(n²) dari pekerjaan yang sama.

Bangun **index** dari satu sisi (Materi 02!), lalu cari untuk setiap record sisi lain:

```python
companies = [{"id": 1, "name": "Nusantara Tech"}, {"id": 2, "name": "Kopi Data"}]
jobs = [{"title": "Backend Dev", "company_id": 2}, {"title": "QA", "company_id": 3}]

company_by_id = {c["id"]: c for c in companies}

joined = []
for job in jobs:
    company = company_by_id.get(job["company_id"])
    joined.append({**job, "company": company["name"] if company else None})
```

`{**job, "company": ...}` membuat dictionary **baru** dengan semua field job plus satu lagi — yang asli tidak berubah.

| Tipe join | Tetap job tanpa perusahaan yang cocok? | Nama di SQL |
|---|---|---|
| Tetap semua job, `None` kalau tidak ada | ✅ | `LEFT JOIN` |
| Tetap hanya job yang punya perusahaan | ❌ | `INNER JOIN` |

### 6. Merge dictionary

```python
defaults = {"page": 1, "per_page": 20, "sort": "newest"}
user_choice = {"per_page": 50}

settings = defaults | user_choice   # {'page': 1, 'per_page': 50, 'sort': 'newest'}
```

Kalau key bentrok, **sisi kanan menang**.

### 7. De-duplicate sambil jaga urutan

```python
seen = set()
unique = []
for email in emails:
    key = email.strip().lower()
    if key not in seen:
        seen.add(key)
        unique.append(email)
```

`list(set(emails))` juga buang ganda tapi **hilang urutan** (dan tidak bisa normalize).

### Ide yang sama di SQL (preview)

| Python | SQL (Module 2) |
|---|---|
| `[j for j in jobs if j["remote"]]` | `SELECT * FROM jobs WHERE remote = true` |
| group by + `sum` | `SELECT city, SUM(amount) FROM sales GROUP BY city` |
| index + lookup | `SELECT ... FROM jobs LEFT JOIN companies ON ...` |

### Pilih setup kamu

Setiap pilihan punya trade-off:

| Pilihan | ✅ | ❌ |
|---|---|---|
| Comprehension | Pendek, jelas untuk aturan sederhana | Sulit dibaca kalau bertingkat |
| Loop jelas | Ada tempat untuk komentar dan beberapa langkah | Lebih panjang |
| Join dengan loop bertingkat | Tidak perlu setup | n × m langkah |
| Join dengan index dict | ~n + m langkah | Ingatan untuk index |
| Proses di Python | Fleksibel, mudah ditest | Lambat dan boros ingatan untuk jutaan row |
| Proses di database | Cepat, pakai index | Perlu SQL; logic tersebar di layer |

- ✅ Pisahkan langkah: `filter → transform → aggregate → format`. Tiap satu bisa fungsi kecil pure.
- ✅ Putuskan jelas apa terjadi kalau cocoknya **tidak ada** (LEFT vs INNER join behavior).
- 🚫 Jangan muat seluruh table database ke Python hanya untuk filter — pakai `WHERE`.
- 🚫 Jangan hitung rata-rata daftar kosong tanpa pengaman.


## ⚠️ Kesalahan umum

- `zip` diam-diam buang item kalau daftar panjangnya berbeda.
- Ubah record saat join (ubah dict bersama) bukan bikin baru.
- `ZeroDivisionError` di rata-rata grup kosong.
- Pakai `list(set(...))` kalau urutan penting.
- Comprehension panjang sampai perlu scroll horizontal.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan "group by" dengan contoh sungguhan seperti sortir kwitansi ke amplop per bulan lalu total setiap amplop. Lalu jelaskan beda antara tetap atau buang job yang perusahaannya tidak ketemu.

## 📐 Rancang

Rancang laporan **"Insight Gaji"** untuk CareerPilot dari `jobs` (title, city, salary, remote, company_id) dan `companies` (id, name, rating). Laporan harus tampilkan, per kota: jumlah job, rata-rata gaji, job gaji paling tinggi dengan nama perusahaannya, dan share job remote (%).

Tulis langkah sebagai pipeline dan beri nama setiap fungsi.

:::quiz
Lihat contoh desain

```text
1. valid_jobs     = filter_jobs_with_salary(jobs)                  # drop salary=None
2. company_by_id  = index_by_id(companies)
3. enriched       = attach_company_names(valid_jobs, company_by_id) # LEFT JOIN, name=None if missing
4. groups         = group_by(enriched, key="city")
5. insights       = {city: summarize(city_jobs) for city, city_jobs in groups.items()}
   summarize → count, average salary, top job (title + company), remote share
6. formatted      = format_report(insights)                         # sorted by average salary desc
```

Tiap langkah adalah fungsi pure yang bisa kamu test sendiri dengan 3–4 record tulis tangan.
:::

### 📝 Checklist review mandiri

- [ ] Filter terjadi sebelum langkah yang mahal
- [ ] Join pakai index, bukan scan bertingkat
- [ ] Perusahaan yang tidak ada dan grup kosong ditangani
- [ ] Format terpisah dari kalkulasi

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

## 🧸 Insight pasar job

:::exercise{path="exercises/m1/w1/04-filter-aggregate" ai="no-ai" title="Filter, group, join"}
Di `insights.py` implementasikan:

- `remote_titles(jobs, min_salary)` → judul job remote dengan `salary >= min_salary`, di urutan asli (pakai comprehension)
- `group_by_city(jobs)` → `{city: [jobs...]}`
- `city_summary(jobs)` → `{city: {"count": int, "average_salary": int, "remote_share": int}}` — rata-rata dibulatkan ke rupiah utuh, remote share sebagai persen utuh (bulatkan ke bawah)
- `attach_company(jobs, companies)` → dict job baru dengan key `"company"` berisi nama perusahaan, atau `None` kalau tidak ketemu (jangan ubah input dict)
- `unique_emails(emails)` → de-duplikasi case-insensitive, tetap **spelling pertama** dan urutan asli
:::

:::hints
- `setdefault(city, []).append(job)` untuk grouping.
- Remote share: `remote_count * 100 // count`.
- Index companies dulu: `{c["id"]: c for c in companies}`.
- `{**job, "company": name}` copy dict dengan key tambahan.
:::

### 🏆 Tantangan lanjut

Tambah `top_company_per_city(jobs, companies)` yang return perusahaan dengan rata-rata gaji **tertinggi** per kota. Pakai ulang fungsi lain.

## ✅ Cek cepat

:::quiz
Tulis ulang sebagai comprehension: kumpulkan `name.upper()` untuk setiap nama panjangnya lebih dari 3 huruf.

`[name.upper() for name in names if len(name) > 3]`
:::

:::quiz
`list(zip([1, 2, 3], ["a", "b"]))` kembalikan apa, dan kenapa itu berbahaya?

`[(1, 'a'), (2, 'b')]` — `3` yang extra diam-diam hilang. Pakai `strict=True` untuk tangkap panjang tidak sama.
:::

:::quiz
Kenapa bangun dictionary index sebelum join dua daftar record?

Supaya setiap cari ~1 langkah bukan scan daftar lain untuk setiap record (n × m langkah).
:::


## 📚 Lanjut belajar

- [Tutorial Python: List comprehensions](https://docs.python.org/3/tutorial/datastructures.html#list-comprehensions)
- [Dokumentasi Python: zip](https://docs.python.org/3/library/functions.html#zip)
- [Dokumentasi Python: collections.defaultdict](https://docs.python.org/3/library/collections.html#collections.defaultdict)

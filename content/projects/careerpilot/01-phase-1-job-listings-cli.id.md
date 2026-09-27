---
title: "Fase 1: Penganalisis Job Listings CLI"
summary: Bangun alat command-line Python yang teruji untuk membersihkan data job listing dan laporan skill paling dicari, statistik gaji, dan pembagian per kota.
sourceHash: 5a1b87c623e8
---

## 🎯 Tujuan

Bangun potongan pertama `careerpilot`: sebuah **command-line tool** yang membaca CSV berisi job listing dan menjawab pertanyaan setiap job seeker:

> *Skill apa yang paling dicari? Pekerjaan ini bayaran berapa? Lowongan ada di mana? Apa yang tersedia untuk saya?*

```text
$ python cli.py data/jobs.csv --city Jakarta --top 3

CareerPilot · Job Market Report
Jobs analyzed: 13

Top skills:
  1. python (8)
  2. sql (5)
  3. aws (3)

Salary (IDR/month, jobs with salary data: 12):
  Average range: 11.875.000 – 18.208.333
  Median max: 19.000.000

Jobs per city:
  Jakarta: 13
```

## 👤 User stories

User story itu satu kalimat yang menceritakan siapa yang ingin apa, dan mengapa. Ini memastikan kamu membangun untuk seorang manusia, bukan hanya menambah fitur.

1. Sebagai job seeker, saya ingin melihat **top N skill** di semua listing, jadi saya tahu apa yang harus dipelajari selanjutnya.
2. Sebagai job seeker, saya ingin **statistik gaji**, jadi saya tahu berapa yang harus diminta.
3. Sebagai job seeker, saya ingin **filter** berdasarkan kota, remote, dan gaji minimum, jadi laporannya sesuai situasi saya.
4. Sebagai job seeker, saya ingin tool ini **menangani data berantakan** (spasi ekstra, uppercase/lowercase campur-campur, gaji hilang) tanpa crash.

## 📦 Starter kit

:::exercise{path="exercises/projects/careerpilot/phase-1" ai="no-ai" title="Starter kit Fase 1"}
Kit berisi **data fiktif** (`data/jobs.csv`), function stub di `analyze.py` dan `cli.py`, dan **acceptance test**.

1. Buat repository `careerpilot` kamu dan folder `cli/`.
2. Salin isi kit ke dalam `cli/`.
3. Buat acceptance test-nya pass — lalu terus maju dengan stretch goal.

Kamu bisa jalankan test di folder handbook juga (perintah di bawah), tapi project sungguhan hidup di repository **kamu** sendiri.
:::

## 📋 Requirement

### Data (`data/jobs.csv`)

Kolom: `id, title, company, city, remote, salary_min, salary_max, skills, posted_on`

Aturan pembersihan untuk `load_jobs(path)`:

| Field | Aturan |
|---|---|
| `title` | dipotong spasi; baris **tanpa title dilewatkan** |
| `city` | dipotong spasi, Title Case (`" jakarta"` → `"Jakarta"`) |
| `remote` | `True` untuk `yes`/`true`/`1` (case apapun), kalau tidak `False` |
| `salary_min`, `salary_max` | `int`, atau `None` kalau kosong |
| `skills` | list berisi skill lowercase yang sudah dipotong spasi, **duplikat dihapus**, urutan asli dipertahankan, item kosong dibuang |
| `posted_on` | `datetime.date`, atau `None` kalau kosong |

### Fungsi analysis (`analyze.py`)

| Function | Mengembalikan |
|---|---|
| `filter_jobs(jobs, city=None, remote=None, min_salary=None)` | job yang cocok dengan **semua** filter yang diberikan; `city` tidak peduli huruf besar/kecil; `min_salary` dibandingkan dengan `salary_max` dan mengeluarkan job tanpa gaji |
| `top_skills(jobs, n)` | `[(skill, count)]` diurutkan count turun, lalu skill A→Z |
| `salary_stats(jobs)` | `{"count", "average_min", "average_max", "median_max"}` dari job yang punya **kedua** gaji; rata-rata dibulatkan ke bawah; median `salary_max` (rata-rata dua nilai tengah kalau genap, dibulatkan ke bawah); semua `0` kalau tidak ada data |
| `jobs_by_city(jobs)` | `{city: count}` diurutkan count turun, lalu city A→Z |
| `format_rupiah_number(amount)` | `18208333` → `"18.208.333"` |
| `format_report(jobs, top_n=5)` | teks laporan yang ditampilkan di atas. Kalau tidak ada data gaji, blok gaji hanya satu baris `Salary: No salary data` |

### CLI (`cli.py`)

```text
python cli.py PATH [--city CITY] [--remote] [--min-salary AMOUNT] [--top N]
```

- Gunakan `argparse`
- File tidak ditemukan → cetak `Error: file not found: PATH` ke **stderr** dan keluar dengan kode `1`
- Filter diterapkan sebelum laporan

## 🧭 Checkpoint

| # | Checkpoint | Selesai saat |
|---|---|---|
| **C1** | Load & clean | `load_jobs` test pass; kamu menangani setiap baris CSV yang berantakan |
| **C2** | Analyze | `filter_jobs`, `top_skills`, `salary_stats`, `jobs_by_city` test pass |
| **C3** | Report & CLI | `format_report` dan CLI test pass; kamu menjalankannya di file asli |
| **C4** | Portfolio-ready | README, screenshot output terminal, `git tag phase-1`, LinkedIn post |

Setelah setiap checkpoint: commit, dan tulis 3 baris di catatan kamu — *apa yang saya bangun, apa yang sulit, apa yang saya pelajari*.

## 🧪 Acceptance criteria

Ini aturan yang memutuskan "selesai": kalau setiap baris di sini benar, fase berakhir — tanpa tebakan, tanpa polishing tanpa akhir.

- [ ] Semua test di `test_acceptance.py` pass
- [ ] Function kecil dan punya nama yang jelas (Architecture Stage A!)
- [ ] Business logic (`analyze.py`) tidak ada `print` dan tidak ada baca file kecuali `load_jobs`
- [ ] CLI hanya parse argument, panggil function, dan cetak output
- [ ] README jelaskan install, run, test, dan tunjukkan sample output

## 🏆 Stretch goals

1. Flag `--json` yang cetak data laporan sebagai JSON (hint: `json.dumps`).
2. Filter `--skills python,sql`: job yang **membutuhkan semua** skill yang disebutkan.
3. Tambahkan listing asli kamu ke CSV kedua (anonim nama perusahaannya kalau mau) dan bandingkan market-nya.
4. `skill_pairs(jobs, n)`: **pasangan** skill yang paling sering muncul (e.g. `python + sql`). Pikirkan kompleksitasnya!
5. Tambahkan GitHub Actions untuk jalankan test di setiap push (preview Module 5).

## ❓ Pertanyaan yang mungkin ditanya interviewer tentang Fase 1

Jawab ini dengan keras sebelum lanjut. Project yang tidak bisa kamu jelaskan belum menjadi portfolio piece.

- Kenapa kamu pisahkan `analyze.py` dari `cli.py`?
- Bagaimana cara kamu menangani CSV dengan 10 juta baris? (Hint: streaming, bukan load semuanya.)
- Berapa kompleksitas `top_skills`? Bagaimana cara kamu dapatkan top 5 tanpa sort semuanya?
- Bagaimana kamu test CLI-nya?

Tulis jawaban kamu di **My notes** — kamu akan pakai ulang di Module 8.

## 📣 Bagikan

:::linkedin{type="build"}
🚀 Bangun potongan pertama portfolio project saya: CareerPilot, CLI yang analisis job listing.

Ia baca CSV berisi listing dan lapor:
📊 skill paling banyak diminta
💰 range gaji dan median
📍 job per kota — dengan filter kota, remote, dan gaji minimum

Keputusan teknis yang saya bangga dengan:
- Pisahkan business logic dari CLI, jadi fully unit-tested
- Bersihkan data berantakan (uppercase/lowercase campur, gaji hilang, skill duplikat) di perbatasan

Challenge terbesar: [jawaban kamu]. Selanjutnya: jadikan REST API dengan Flask dan PostgreSQL.

Repo: [link] · [screenshot output terminal]

#Python #LearningInPublic #BuildInPublic #SoftwareEngineering
:::

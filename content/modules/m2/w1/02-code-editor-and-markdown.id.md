---
title: "Code Editor & Markdown"
summary: Siapkan editor seperti profesional dan tulis dokumentasi jelas di Markdown — mulai dari README yang betul-betul dibaca rekruter.
sourceHash: cb1d0ff35023
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa yang editor yang bagus kasih: navigasi, linting, formatting, debugging
- Shortcut keyboard yang hemat jam-jam
- Syntax **Markdown** (GitHub Flavored), termasuk tabel, task list, code block dan diagram Mermaid
- Cara menulis **README** yang berfungsi sebagai dokumentasi *dan* portofolio

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Editor / IDE** | Program untuk menulis kode (VS Code, PyCharm) |
| **Extension** | Tambahan kecil yang mengajarkan editor trik baru |
| **Linter** | Alat yang menunjuk kesalahan dan pola buruk saat kamu mengetik |
| **Formatter** | Alat yang memperbaiki spasi dan tata letak otomatis, sama setiap kali |
| **Go to definition** | Lompat langsung ke tempat fungsi atau class ditulis |
| **Markdown** | Format teks sederhana yang berubah jadi judul, daftar, tabel, dan kode |
| **Code fence** | Tiga backtick mengelilingi kode, supaya bentuknya tetap dan dapat warna |
| **README** | File pertama yang orang baca di repository — apa itu dan cara menjalankannya |
| **Mermaid** | Teks yang jadi diagram, jadi diagram bisa hidup di Git |

## 🧠 Ide besarnya

Editor-mu adalah **bengkel kerja**. Tukang kayu dengan alat tajam dan teratur tidak hanya lebih cepat — mereka buat lebih sedikit kesalahan. Editor yang menunjuk kesalahan saat kamu mengetik, format otomatis saat simpan, dan lompat ke definisi mengubah jam mencari menjadi detik.

:term[Markdown]{bahasa="Markdown — format teks sederhana yang diubah jadi dokumen rapi (judul, daftar, tabel, kode)"} adalah **bahasa dokumentasi developer**: README, pull request, issue, docs site — dan setiap materi di handbook ini.

## ❓ Kenapa ini penting

- Kode dibaca dan dinavigasi jauh lebih sering daripada diketik: *di mana fungsi ini dipakai? tipe ini terlihat seperti apa?*
- Orang membuat kesalahan format dan ejaan yang alat tangkap langsung.
- Proyek butuh dokumentasi yang dibaca bagus sebagai teks polos (di terminal, di diff) **dan** juga render cantik di GitHub.

Tanpa setup yang baik:

- Kamu cari file dengan tangan untuk nama fungsi, ketinggalan satu pakaiannya → bug.
- Review penuh dengan "spasi hilang" dan "indentasi salah" bukan feedback sungguhan.
- Proyek hebat yang README-nya cuma bilang `# my-project` → rekruter tutup tab dalam sepuluh detik.

## 📖 Cara kerjanya, langkah demi langkah

### 1. Pilih editor

| Editor | Catatan |
|---|---|
| **VS Code** | Gratis, paling populer, ekosistem extension besar |
| **Cursor / Kiro / Windsurf** | Berbasis VS Code, dengan fitur AI lebih dalam (Modul 6) |
| **PyCharm / WebStorm** | IDE kuat, lebih berat, refactoring bagus |
| **Neovim** | Keyboard-driven, kurva pembelajaran curam |

Semuanya di bawah pakai nama VS Code; editor berbasis VS Code berperilaku sama.

### 2. Setup penting

Set ini sekali saja dan jalan untuk setiap proyek sesudahnya — seperti rapikan toolbox sebelum pekerjaan pertama, bukan saat kerja.

| Extension / setting | Apa yang dilakukannya |
|---|---|
| **Python** + **Pylance** | IntelliSense, go-to-definition, type checking |
| **Ruff** | Python linting + formatting (sangat cepat) |
| **ESLint** + **Prettier** | JS/TS linting + formatting (Modul 4) |
| **GitLens** *(opsional)* | Siapa yang mengubah baris ini dan mengapa |
| **Docker**, **Even Better TOML**, **YAML** | Dukungan file yang kamu butuh segera |
| `"editor.formatOnSave": true` | Format otomatis |
| `"files.trimTrailingWhitespace": true` | Diff yang bersih |
| Pilih **Python interpreter** proyek-mu (`.venv`) | Jadi import dan type terselesaikan |

Setting level proyek bisa hidup di `.vscode/settings.json` dan extension yang disarankan di `.vscode/extensions.json` — berguna untuk tim.

### 3. Shortcut yang perlu kamu pelajari minggu ini

| Aksi | macOS | Windows/Linux |
|---|---|---|
| Command palette | `Cmd Shift P` | `Ctrl Shift P` |
| Buka file nama | `Cmd P` | `Ctrl P` |
| Cari di semua file | `Cmd Shift F` | `Ctrl Shift F` |
| Go to definition | `F12` | `F12` |
| Cari semua referensi | `Shift F12` | `Shift F12` |
| Rename simbol di mana-mana | `F2` | `F2` |
| Multi-cursor | `Option Click` | `Alt Click` |
| Toggle terminal | ``Ctrl ` `` | ``Ctrl ` `` |
| Pindah baris atas/bawah | `Option ↑/↓` | `Alt ↑/↓` |

:::tip
`F2` (rename simbol) lebih aman daripada find-and-replace: ia mengerti kode, jadi rename `user` tidak akan sentuh `username`.
:::

### 4. Markdown basics

````md
# Title (one per document)
## Section
### Subsection

**bold**, *italic*, `inline code`, [link](https://example.com)

- bullet
  - nested bullet
1. numbered

> A quote or note

```python
print("fenced code block with a language")
```

| Column | Another |
|---|---|
| cell | cell |

- [ ] task not done
- [x] task done

![Screenshot](docs/screenshot.png)
````

GitHub juga render diagram **Mermaid** di blok ` ```mermaid ` — sempurna untuk diagram arsitektur di README.

### 5. Anatomi README yang bagus

README adalah **etalase proyek-mu**. Rekruter habis kurang dari satu menit di situ: mereka mau lihat apa yang dilakukannya, screenshot atau diagram, dan cara menjalankannya.

| Bagian | Kenapa penting |
|---|---|
| **Nama + deskripsi satu baris** | apa itu, dalam 5 detik |
| **Screenshot / GIF / demo link** | bukti jalan |
| **Fitur** | apa yang dilakukan |
| **Tech stack** | rekruter scan untuk keywords |
| **Arsitektur** (diagram) | tunjuk pemikiran engineering |
| **Getting started** (prasyarat, install, env var, jalan) | siapa pun bisa jalankan |
| **Testing** | tunjuk kebiasaan kualitas |
| **API docs / usage** | cara memakainya |
| **Keputusan & trade-off** *(opsional tapi kuat)* | tunjuk pertimbangan |
| **Roadmap / batasan terkenal** | kejujuran dan arah |

### Pilih setup-mu

Setiap pilihan di sini punya trade-off:

| Pilihan | ✅ | ❌ |
|---|---|---|
| Editor ringan + extension | cepat, fleksibel | waktu setup; konflik extension |
| IDE penuh | kuat langsung jalan | lebih berat, kadang lambat |
| Fitur AI editor berat | cepat | bisa sembunyikan apa terjadi; belajar rugi kalau overdose |
| README sangat panjang | lengkap | tidak ada yang baca — taruh detail di `docs/` dan link |

- ✅ Pakai Markdown untuk README, doc, deskripsi PR, catatan dan catatan keputusan.
- ✅ Jaga doc **sebelah kode** (di repo) jadi berubah bersama.
- 🚫 Jangan andalkan format-by-hand; biarkan alat melakukannya.
- 🚫 Jangan taruh secret, URL internal atau data pribadi asli di README dan screenshot.

## ⚠️ Kesalahan umum

- Jalankan proyek dengan Python interpreter salah dipilih di editor.
- README dengan langkah install yang tidak jalan lagi (tidak pernah re-test).
- Screenshot berisi token, email atau nilai `.env`.
- Dinding teks tanpa judul, tabel atau code block.

:::revoshop
README RevoShop-mu sudah kuat: *Live Demo* dengan akun demo, *Arsitektur*, *Order Lifecycle*, dua cara jalankan (dengan dan tanpa Docker), API doc, testing dan bagian kualitas kode. Review seperti rekruter dengan **timer 30 detik**: Apa yang kamu pelajari dalam 30 detik? Ada screenshot atau diagram dekat puncak? Ada yang **tidak bisa kamu jelaskan** di interview? Tulis 3 perbaikan di catatan-mu.
:::

## 🏆 Praktik terbaik

- [ ] **Format on save** + **linter** di editor, dengan **sama** config jalan di CI.
- [ ] Commit config editor bersama: `.editorconfig`, `.vscode/extensions.json` (bukan setting pribadi).
- [ ] Pelajari shortcut navigasi dulu (go to definition, reference, rename) — mereka bayar setiap hari.
- [ ] README **bagian puncak jawab**: apa, kenapa, demo, cara jalankan — dalam kurang 30 detik baca.
- [ ] Pakai **relative link** dan jaga gambar di repo (`docs/images/`) jadi tidak putus.
- [ ] Satu `#` judul per dokumen; pakai judul berurutan (`##` lalu `###`) untuk aksesibilitas dan alat toc.
- [ ] Selalu tambah **bahasa** ke code block (` ```python `) untuk highlight.
- [ ] Jaga diagram sebagai **kode Mermaid** kalau bisa — mereka versioned dan reviewable, tidak seperti gambar.
- [ ] Update README di **PR yang sama** yang ubah perilaku.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke non-programmer kenapa GitHub README developer penting untuk dapat kerja, dan apa yang layar pertama seharusnya tunjuk.

## 📐 Rancang

Outline (hanya judul, plus satu kalimat masing-masing) README **CareerPilot** seperti terlihat setelah Phase 2 (Flask API). Putuskan apa yang ke README dan apa pindah ke `docs/`.

:::quiz
Lihat contoh outline

```md
# CareerPilot — track your job hunt, powered by data (and soon AI)
<one-line pitch + demo link + screenshot/GIF>

## Features            ← applications pipeline, notes, auth, job market report (Phase 1 CLI)
## Tech stack          ← Python, Flask, PostgreSQL, SQLAlchemy, pytest, Docker
## Architecture        ← Mermaid: client → Flask API → PostgreSQL; link to docs/architecture.md
## Getting started     ← prerequisites, .env.example, docker compose up, migrations, seed
## API                 ← link to Swagger UI + 3 example requests
## Testing             ← how to run, coverage
## Decisions           ← link to docs/decisions/ (e.g. "why JWT", "why soft delete")
## Roadmap             ← Phase 3 AI matching, Phase 4 web app
```

Pindah ke `docs/`: referensi endpoint penuh, arsitektur detail, catatan keputusan, runbook deployment.
:::

### 📝 Checklist review mandiri

- [ ] Layar pertama jawab *apa, kenapa, bukti, cara jalankan*
- [ ] Detail hidup di `docs/`, linked dari README
- [ ] Ada bagian tunjuk kualitas engineering (test, keputusan)

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m2/w1/02-markdown-readme" ai="no-ai" title="Tulis README CareerPilot"}
Tulis README untuk **Phase 1 CLI CareerPilot** kamu di `README.md` dalam folder latihan (lalu copy ke repo asli-mu).

Test cek struktur, bukan wording: satu judul `#`, bagian wajib, code block `bash` terpagar dengan command jalankan, tabel, diagram Mermaid, hanya relative link, dan tidak ada secret. Baca `README_REQUIREMENTS.md` untuk daftar pasti.
:::

:::hints
- Jalankan test dulu — pesan mereka bilang persis apa yang hilang.
- Tempel output terminal asli dari CLI-mu ke blok ` ```text `.
- Flowchart Mermaid sederhana cukup: CSV → load & clean → analisis → report.
:::

### 🏆 Tujuan stretch

Rekam terminal GIF 10 detik CLI-mu (misal dengan [asciinema](https://asciinema.org/) + agg, atau [VHS](https://github.com/charmbracelet/vhs)) dan taruh di bawah judul.

## ✅ Cek cepat

:::quiz
Kenapa `F2` rename lebih baik daripada find-and-replace?

Ia rename **simbol** memakai pemahaman kode — setiap penggunaan asli di semua file, dan bukan hanya teks yang mirip.
:::

:::quiz
Di mana seharusnya dokumentasi detail hidup, dan kenapa?

Di repository (misal `docs/`), sebelah kode, jadi versioned, di-review dan update di PR yang sama seperti perilaku yang jelaskan.
:::


## 📚 Lanjut belajar

- [VS Code: Python in VS Code](https://code.visualstudio.com/docs/python/python-tutorial)
- [GitHub Docs: Basic writing and formatting syntax](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax)
- [GitHub Docs: Creating Mermaid diagrams](https://docs.github.com/en/get-started/writing-on-github/working-with-advanced-formatting/creating-diagrams)

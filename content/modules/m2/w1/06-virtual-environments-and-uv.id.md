---
title: "Virtual Environment & uv: Proyek Python yang Bisa Diulang"
summary: Pisahkan dependensi setiap proyek, kunci versi dengan lock file, dan gunakan uv — alat modern pengelola proyek Python yang sangat cepat.
sourceHash: 370c997b173c
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Kenapa setiap proyek Python butuh **virtual environment** sendiri
- Dependensi **langsung** vs **tidak langsung**, aturan versi, dan **lock file**
- `pyproject.toml`: tempat standar untuk metadata dan dependensi proyek
- Alur kerja **uv**: `init`, `add`, `sync`, `run`, `lock`
- Bagaimana `requirements.txt` + `venv` + `pip` dibandingkan (kamu akan temui di proyek lama, seperti RevoShop)

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Virtual environment** | Folder terpisah berisi paket khusus untuk satu proyek saja |
| **Dependency** | Pustaka yang dibutuhkan proyekmu untuk jalan |
| **Transitive dependency** | Pustaka yang dibutuhkan oleh pustaka yang kamu pakai |
| **Version specifier** | Aturan versi mana yang boleh (`flask>=3,<4`) |
| **Lock file** | Daftar versi pasti yang dipasang, supaya setiap mesin sama |
| **`pyproject.toml`** | Berkas standar untuk keterangan proyek dan dependensi |
| **uv** | Alat cepat yang bikin environment, cari versi, dan kunci dependensi |
| **Sync** | Menyamakan environment-mu dengan isi lock file persis |

## 🧠 Ide besarnya

Virtual environment itu **kotak alat terpisah per proyek**. Proyek A butuh Flask 2, proyek B butuh Flask 3 — kalau dua-duanya pakai satu kotak alat di rumah, instal untuk yang satu bisa rusak yang lain.

Lock file itu **tanda terima belanja pasti**: bukan "ada tepung", tapi "tepung Brand X, 1 kg, batch 2026-09". Siapa pun yang instal dapat **versi yang sama** — laptopmu, rekan kerjamu, CI, dan production.

## ❓ Kenapa ini penting

- Proyek beda butuh **versi beda** dari pustaka yang sama.
- Hari ini `pip install flask` dan bulan depan bisa pasang versi **beda** → "jalan di mesinku".
- Pustaka butuh pustaka lain, jadi itu juga perlu dikunci.
- Instal ke Python sistem bisa rusak alat yang dibutuhkan sistem operasi.

Tanpa disiplin ini:

- Kamu `pip install` ke Python global; enam bulan kemudian tiga proyek saling tabrakan dan tidak ada yang jalan.
- `requirements.txt` bilang `flask` tanpa versi; rilis major baru ubah perilaku; production rusak saat deploy berikutnya.
- Rekan kerja baru habis sehari cuma buat proyek bisa mulai.

## 📖 Langkah demi langkah

### 1. Cara lama: `venv` + `pip`

```bash
python3 -m venv .venv              # create an isolated environment in .venv/
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install flask==3.1.3
pip freeze > requirements.txt      # record EVERYTHING installed, exact versions
deactivate
```

Jalan di mana saja, tapi manual: aktivasi, jaga `requirements.txt` tetap selaras, pisahkan alat dev dari dependensi runtime (RevoShop pakai `requirements.txt` + `requirements-dev.txt`).

### 2. Cara modern: `pyproject.toml` + lock file

`pyproject.toml` adalah **berkas standar** untuk pengaturan proyek Python:

```toml
[project]
name = "careerpilot-api"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "flask>=3.1,<4",
    "sqlalchemy>=2.0,<3",
]

[dependency-groups]
dev = ["pytest>=8", "ruff>=0.6"]
```

- `dependencies` berisi dependensi **langsung** dengan **aturan versi** yang cocok.
- Lock file (`uv.lock`) catat versi **pasti** dari *semua*, termasuk transitive dependency.
- Alat dev saja di grup terpisah.

### 3. uv di praktik

[uv](https://docs.astral.sh/uv/) adalah alat paket Python dan proyek yang sangat cepat (bisa juga pasang Python sendiri).

```bash
uv init careerpilot-api          # create a project with pyproject.toml
cd careerpilot-api
uv add flask sqlalchemy          # add runtime deps → updates pyproject.toml and uv.lock
uv add --dev pytest ruff         # add dev deps
uv run pytest                    # run inside the project's environment (creates .venv automatically)
uv sync                          # make .venv match uv.lock exactly (e.g. after git pull)
uv lock --upgrade-package flask  # deliberately upgrade one package
uv python pin 3.12               # pin the Python version for the project
```

Tidak perlu aktivasi manual: `uv run` selalu pakai environment yang tepat. (Folder `exercises/` di handbook ini adalah proyek uv — kamu sudah pernah pake.)

### 4. Version specifier

Pikirnya seperti pesan baju: `>=3,<4` artinya "ukuran 3 apa pun, tapi bukan 4" — ruang untuk perbaikan, tanpa kejutan redesain.

| Specifier | Maksudnya | Pakai untuk |
|---|---|---|
| `flask==3.1.3` | persis ini | lock file, aplikasi yang bisa diulang |
| `flask>=3.1,<4` | 3.x apa pun dari 3.1 | aturan di `pyproject.toml` |
| `flask~=3.1` | ≥3.1, <4.0 | singkat untuk rilis kompatibel |
| `flask` | apa pun | ❌ hindari |

Kebanyakan pustaka ikuti **semantic versioning**: `MAJOR.MINOR.PATCH` — major bisa rusak, minor tambah fitur, patch perbaiki bug.

### 5. Apa yang di-commit

Aturan mudah: commit **resep dan tanda terima** (`pyproject.toml` dan lock file), jangan **barang belanja** (`.venv/`).

| Berkas | Di-commit? |
|---|---|
| `pyproject.toml` | ✅ |
| `uv.lock` (atau `requirements.txt` yang dikunci) | ✅ untuk aplikasi |
| `.python-version` | ✅ |
| `.venv/` | ❌ jangan (khusus mesin dan besar) |

### Pilih setup-mu

Setiap pilihan di sini adalah trade-off:

| Alat | ✅ | ❌ |
|---|---|---|
| `venv` + `pip` + `requirements.txt` | bawaan Python, universal | manual; transitive dep tidak dikunci kecuali `pip freeze`; lambat |
| **uv** | sangat cepat, lock file, kelola Python, satu alat | baru; tim harus pasang |
| Poetry / PDM | lock file, matang | lambat; konvensi konfigurasi beda |
| Conda | bagus untuk data science dengan pustaka native (C/CUDA) | berat untuk web app |

| Penguncian | ✅ | ❌ |
|---|---|---|
| Versi pasti di mana-mana | bisa diulang | harus update sengaja (patch keamanan!) |
| Aturan longgar saja | update otomatis | kejutan rusak |

**Keseimbangan:** aturan di `pyproject.toml`, versi pasti di lock file, dan alat (Dependabot/Renovate) yang usul update sebagai PR.

- ✅ Selalu: satu environment per proyek.
- ✅ Commit lock file untuk **aplikasi** (API, CLI, layanan).
- ✅ Untuk **pustaka** yang kamu terbitkan, jaga aturan luwes supaya user bisa gabung dengan paket lain.
- 🚫 Jangan `sudo pip install` atau instal ke Python sistem.
- 🚫 Jangan commit `.venv/`.

## ⚠️ Kesalahan umum

- Jalankan `pip install` tanpa venv aktif (instal global).
- Editor pakai interpreter beda dari terminal.
- Lupa commit lock file setelah `uv add`.
- Dependensi tidak dikunci di production.
- Campur `pip install` ke environment yang dikelola uv (pakai `uv add`).

:::revoshop
Buka `requirements.txt` dan `requirements-dev.txt` RevoShop. Perhatikan komentar ("Production runtime dependencies only", "Shared transitive runtime deps (pinned for reproducible installs)") dan `-r requirements.txt` di awal file dev. Jelaskan dengan kata-katamu sendiri: kenapa dependensi **transitive** seperti `Werkzeug` dan `Jinja2` juga dikunci? Kenapa `locust` hanya di file dev? Lalu gambar bagaimana pisahan yang sama kelihatan di `pyproject.toml` dengan dependency group.
:::

## 🏆 Praktik terbaik

- [ ] Pakai **`pyproject.toml`** sebagai satu sumber kebenaran untuk metadata dan dependensi proyek.
- [ ] Commit **lock file** dan instal dengan `uv sync` (atau `pip install -r` file yang dikunci penuh) di CI dan Docker.
- [ ] Pisahkan dependensi **runtime** dan **dev** (dependency group).
- [ ] Kunci **versi Python** (`.python-version` / `requires-python`).
- [ ] Update dependensi **teratur dan sengaja**: PR otomatis (Dependabot/Renovate) + tes.
- [ ] Cari kerentanan keamanan (`pip-audit`, GitHub Dependabot alert).
- [ ] Jangan instal paket global; jalankan alat via `uv run` (atau venv aktif).
- [ ] Jaga daftar dependensi tetap tipis — setiap paket adalah kode yang kamu percaya dan harus update.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke orang yang bukan programmer kenapa "instal pustaka" saja tidak cukup untuk tim, pakai ide resep/tanda terima belanja (atau analogi versimu). Sertakan istilah *virtual environment* dan *lock file*.

## 📐 Rancang

Rancang dependensi untuk **CareerPilot Phase 2** (Flask API). Golongkan setiap ke *runtime* atau *dev*, dan pilih gaya aturan versi untuk `pyproject.toml`:

`flask`, `flask-sqlalchemy`, `psycopg[binary]`, `alembic`/`flask-migrate`, `pyjwt`, `pytest`, `pytest-cov`, `ruff`, `locust`, `python-dotenv`, `gunicorn`

:::quiz
Lihat contoh rancangan

**Runtime:** flask, flask-sqlalchemy, psycopg[binary], flask-migrate, pyjwt, python-dotenv, gunicorn — setiap sebagai `>=versi sekarang,<major berikutnya` (mis. `flask>=3.1,<4`).

**Dev:** pytest, pytest-cov, ruff, locust.

Versi pasti dari semua (termasuk transitive dependency) hidup di `uv.lock`. Docker dan CI jalankan `uv sync --frozen --no-dev` (hanya runtime) atau `uv sync --frozen` (dengan tes).

`python-dotenv` bisa dipertanyakan: di production, variabel environment asli diatur platform, jadi beberapa tim simpan sebagai dev-only.
:::

### 📝 Checklist review mandiri

- [ ] Alat tes dan kinerja bukan dependensi runtime
- [ ] Saya pakai aturan di `pyproject.toml` dan versi pasti di lock file
- [ ] Saya pertimbangkan apa yang sebenarnya dibutuhkan production

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{ai="no-ai" title="Bootstrap CareerPilot API project dengan uv"}
Di repositori **careerpilot** milikmu sendiri:

1. `uv init api --app` (buat `api/pyproject.toml`) dan `uv python pin 3.12` di dalam `api/`
2. `uv add flask` dan `uv add --dev pytest ruff`
3. Buat `api/app.py` dengan aplikasi Flask yang balas `{"status": "ok"}` di `GET /health`
4. Buat `api/test_app.py` pakai Flask test client untuk cek endpoint itu
5. Jalankan `uv run pytest` dan `uv run ruff check .`
6. Commit `pyproject.toml`, `uv.lock`, `.python-version`, kodenya — **bukan** `.venv/`
7. Hapus `.venv/`, jalankan `uv sync`, dan tes lagi: harusnya langsung jalan

Tulis di **My notes**: berkas mana saja yang dibuat uv, dan apa saja isi `uv.lock` untuk Flask (versinya dan paling tidak dua transitive dependency).
:::

:::hints
- Flask test client: `client = app.test_client(); response = client.get("/health"); assert response.json == {"status": "ok"}`.
- Cek apa yang di-track dengan `git status` sebelum commit.
- `uv tree` tunjukkan dependency tree — cari transitive dependency Flask di sana.
:::

## ✅ Cek cepat

:::quiz
Apa bedanya `pyproject.toml` dan `uv.lock`?

`pyproject.toml` berisi **dependensi langsung** dengan aturan versi yang dibolehkan (edit manual). `uv.lock` catat versi **pasti** dari semua dependensi yang sudah di-resolve, termasuk yang transitive (tool-generated), untuk instal yang bisa diulang.
:::

:::quiz
Kenapa `.venv/` jangan di-commit?

Ukurannya besar, khusus mesin dan OS, dan bisa diulang penuh dari `pyproject.toml` + lock file.
:::


## 📚 Lanjut belajar

- [Dokumentasi uv: Working on projects](https://docs.astral.sh/uv/guides/projects/)
- [Python Packaging User Guide: Writing pyproject.toml](https://packaging.python.org/en/latest/guides/writing-pyproject-toml/)
- [Dokumentasi Python: venv](https://docs.python.org/3/library/venv.html)

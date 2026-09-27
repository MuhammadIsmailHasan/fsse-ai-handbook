---
title: "🔥 CI dengan GitHub Actions"
summary: Buat setiap push membuktikan dirinya sendiri — pipeline GitHub Actions yang melakukan lint, pengecekan tipe, dan tes terhadap PostgreSQL asli, membangun image Docker, melaporkan hasil dengan jelas, cepat, murah dan aman.
sourceHash: ddd58700581e
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- **CI** vs **CD**, dan apa yang diperiksa pipeline yang baik
- Anatomi GitHub Actions: workflow, event, job, step, runner, action
- Service container (PostgreSQL), matrix, caching, job dependency, kondisi
- Job summary dan annotation: kegagalan yang bisa dibaca dalam 10 detik
- **Keamanan**: token dengan privilege minimal, action yang dipinkan SHA, secret, bahaya `pull_request_target`
- Branch protection: CI sebagai **gerbang merge**

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **CI** | Pemeriksaan otomatis pada setiap push dan pull request |
| **CD** | Pengiriman atau deploy otomatis untuk kode yang lolos |
| **Workflow** | File YAML yang menjelaskan langkah-langkah otomatis itu |
| **Job** | Satu bagian pekerjaan dalam workflow, di mesin bersih sendiri |
| **Runner** | Mesin yang GitHub sediakan untuk menjalankan job |
| **Action** | Langkah siap pakai yang ditulis orang lain |
| **Service container** | Kontainer pendukung (PostgreSQL) yang dijalankan untuk tes |
| **Cache** | Menggunakan ulang dependency yang sudah diunduh antar run |
| **SHA pinning** | Mengunci action ke satu commit pasti, untuk keamanan |
| **Merge gate** | Aturan yang PR tidak bisa merge sampai check selesai |

## 🧠 Ide besarnya

CI itu seperti **pos pemeriksaan keamanan bandara** untuk kode. Setiap tas (commit) melewati scanner yang sama — lint, tipe, tes, build — tidak peduli siapa yang paket atau seberapa yakin mereka. Kalau scanner berbunyi, tas tidak naik pesawat (merge).

Pos pemeriksaan itu otomatis, sama untuk semua orang, dan tidak pernah lelah pada jam 11 malam di hari Jumat.

## ❓ Kenapa ini penting

- "Jalan di mesinku" — CI jalan di mesin **bersih** dengan dependency yang **terkunci**.
- Orang lupa menjalankan tes sebelum push, terutama dekat deadline.
- Reviewer harus membaca desain dan logika, bukan format atau cek apakah tes lolos.
- Deploy otomatis hanya aman kalau CI bisa dipercaya.
- Pull request yang dibuat AI butuh pemeriksaan otomatis lebih banyak.

Tanpa itu:

- `main` rusak Senin, dan tiga orang menghabiskan pagi mencari merge mana yang membuatnya.
- Tes lolos di SQLite tapi gagal di production di PostgreSQL (pelajaran 02).
- Dependency rilis versi baru semalam, dan tidak ada yang tahu sampai deploy.
- Workflow memakai `some-org/cool-action@main`; penulis-nya — atau penyerang yang ambil akun — push kode yang mencuri repository secret-mu.

## 📖 Langkah demi langkah

### 1. Anatomi

```mermaid
flowchart LR
    E["Peristiwa<br/>push / pull_request"] --> W["Workflow<br/>.github/workflows/ci.yml"]
    W --> L["Job: lint<br/>(runner VM)"]
    W --> T["Job: test × matrix<br/>(runner VM + Postgres)"]
    L & T --> B["Job: build<br/>needs: [lint, test]"]
```

- **Workflow**: file YAML di `.github/workflows/`.
- **Event** (`on:`): push, pull_request, schedule, workflow_dispatch (tombol manual), release…
- **Job**: jalan di mesin **runner** segar; job jalan **sejajar** kecuali dihubung dengan `needs`.
- **Step**: perintah shell (`run:`) atau **action** siap pakai (`uses:`).

### 2. Pipeline lengkap

```yaml
name: CI

on:
  push:
    branches: [main]
  pull_request:

permissions:
  contents: read                      # least privilege for GITHUB_TOKEN

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true            # new push cancels the outdated run

jobs:
  lint:
    runs-on: ubuntu-24.04
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - uses: astral-sh/setup-uv@bec219d24cd3e171d82865faccec33120bb574f4 # v10.1.0
        with:
          enable-cache: true
      - run: uv sync --locked
      - run: uv run ruff check .
      - run: uv run ruff format --check .
      - run: uv run mypy .

  test:
    runs-on: ubuntu-24.04
    timeout-minutes: 15
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.13", "3.14"]
    services:
      postgres:
        image: postgres:17-alpine
        env: { POSTGRES_USER: ci, POSTGRES_PASSWORD: ci-only-password, POSTGRES_DB: careerpilot_test }
        ports: ["5432:5432"]
        options: >-
          --health-cmd "pg_isready -U ci -d careerpilot_test"
          --health-interval 5s --health-timeout 3s --health-retries 10
    env:
      DATABASE_URL: postgresql://ci:ci-only-password@localhost:5432/careerpilot_test
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - uses: astral-sh/setup-uv@bec219d24cd3e171d82865faccec33120bb574f4 # v10.1.0
        with:
          enable-cache: true
          python-version: ${{ matrix.python-version }}
      - run: uv sync --locked
      - run: uv run pytest --junitxml=report.xml
      - name: Test summary
        if: always()
        run: uv run python junit_summary.py report.xml >> "$GITHUB_STEP_SUMMARY"

  build:
    needs: [lint, test]
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    runs-on: ubuntu-24.04
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
      - uses: docker/setup-buildx-action@37fe631027851001ddb9b187196cc803df7f5f0e # v4.3.0
      - uses: docker/build-push-action@53b7df96c91f9c12dcc8a07bcb9ccacbed38856a # v7.3.0
        with:
          push: false
          tags: careerpilot-api:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

:::note[Versi berubah]
SHA-SHA di atas benar saat pelajaran ini ditulis. Selalu ambil SHA rilis terbaru dari halaman Releases setiap action, dan biarkan **Dependabot** memperbaruinya.
:::

### 3. Fitur utama dijelaskan

| Fitur | Apa yang dilakukan | Kenapa |
|---|---|---|
| `services:` | mulai Docker container di sebelah job, bisa dijangkau di `localhost:<port>` | tes di **PostgreSQL asli** |
| `options: --health-cmd` | job menunggu sampai service sehat | tidak ada "connection refused" yang goyah |
| `strategy.matrix` | jalankan job sekali per nilai | tes beberapa versi Python / OS |
| `fail-fast: false` | job matrix lain tetap jalan kalau satu gagal | lihat **semua** kegagalan dalam satu run |
| `needs:` | dependency job | build hanya setelah check lolos |
| `if:` | kondisi | build/deploy hanya di push `main` |
| `enable-cache` / `cache-from: type=gha` | pakai ulang unduhan & layer Docker | menit → detik |
| `concurrency` | batalkan run yang sudah ketinggalan | hemat menit runner |
| `timeout-minutes` | matikan job yang macet | standarnya **360 menit** |
| `$GITHUB_STEP_SUMMARY` | markdown ditampilkan di halaman run | hasil yang bisa dibaca |
| `::error title=…::msg` | perintah workflow → annotation | kegagalan disorot di UI |

:::warning[Gotcha YAML]
- `python-version: [3.10]` → YAML baca **angka** `3.1`. Kutip versi: `["3.10"]`.
- `on:` diparse sebagai boolean `true` oleh parser YAML 1.1 seperti PyYAML (GitHub menanganinya; script-mu juga harus).
- Kesalahan indentasi diam-diam ubah arti — validasi dengan **actionlint**.
:::

### 4. Check yang baik dilakukan (urutan kecepatan)

Check termurah duluan: typo harus gagal dalam 30 detik, bukan setelah build enam menit. Umpan balik cepat itu yang bikin orang jalankan pipeline daripada hindari.

1. **Format & lint** (detik) — ruff
2. **Tipe** (detik) — mypy / pyright, `tsc --noEmit` untuk frontend
3. **Unit test** (detik)
4. **Test integrasi** dengan PostgreSQL (puluhan detik)
5. **Migrasi berlaku** bersih di database kosong (`flask db upgrade`)
6. **Keamanan**: audit dependency (`pip-audit`), scan secret (gitleaks), scan image (Trivy)
7. **Build** image Docker

Check cepat, murah duluan — developer dapat umpan balik cepat.

### 5. Secret dan permission

- `GITHUB_TOKEN` dibuat per run; atur `permissions:` ke **minimum** (`contents: read`) dan beri lebih banyak per job hanya kalau perlu (misal `packages: write` untuk push image).
- Repository secret: `${{ secrets.NAME }}` — disembunyikan di log, **tidak** tersedia untuk pull request dari fork.
- Test tidak boleh butuh key pihak ketiga asli: pakai palsu (pelajaran 02). Password database CI adalah nilai sekali pakai untuk container yang hidup beberapa menit.
- Lebih suka **OIDC** (`id-token: write`) untuk dapat kredensial cloud jangka pendek daripada simpan kunci AWS jangka panjang (Module 5).

### 6. Supply-chain security untuk workflow

Tag bisa dipindah ke kode berbeda; commit SHA tidak. Pinning adalah perbedaan antara "action yang saya review" dan "apapun di sana hari ini".

- **Pinning action ke SHA commit penuh** (tag seperti `v7` bisa dipindah ke kode berbeda; SHA tidak). Simpan komentar `# v7.0.1` untuk manusia; Dependabot perbarui keduanya.
- Pilih action resmi/terverifikasi; baca sumber yang kecil dari pihak ketiga.
- ⚠️ `pull_request_target` jalan dengan **token tulis dan secret** dalam konteks repo dasar — dikombinasi dengan checkout kode PR, ia biarkan PR orang mencuri secret. Hindari kecuali kamu betul-betul mengerti.
- Jangan interpolasi input tidak terpercaya langsung ke `run:` (`${{ github.event.pull_request.title }}` → shell injection); lewat via `env:` dan kutip.

### 7. CI sebagai gerbang merge

Di *Settings → Rules → Rulesets* (atau branch protection) untuk `main`:
- butuh pull request (opsional 1 approval),
- butuh status check `lint` dan `test (3.13)`, `test (3.14)` lolos,
- butuh branch selalu terbaru, blok force push.

Sekarang kode rusak **tidak bisa** capai `main` — bahkan punyamu.

### 8. Biaya di akun gratis

Repository publik dapat runner standar gratis; repository private di paket gratis dapat kuota menit runner bulanan. Pembatalan concurrency, caching, timeout dan path filter (`paths-ignore: ["**.md"]`) jaga kamu di bawah batas. Cek halaman billing GitHub saat ini untuk angka pasti.

### Pilih setup-mu

Setiap pilihan di sini adalah trade-off:

| Pilihan | ✅ | ❌ |
|---|---|---|
| Matrix besar (banyak versi/OS) | kompatibilitas luas | lebih banyak menit, umpan balik lambat |
| PostgreSQL asli | realistis | ~10 s startup |
| SHA pinning | tamper-proof | update bising (otomasi dengan Dependabot) |
| Satu job besar | sederhana | tanpa paralelisme; satu gagal sembunyikan yang lain |
| Banyak job kecil | sejajar, status jelas | setup berulang (kurangi dengan caching) |
| Required check di `main` | lindungi main | tes goyah blok semua → perbaiki goyah cepat |

- ✅ Setiap repository yang kamu tampilkan majikan — lencana CI hijau dan pipeline asli adalah sinyal portofolio kuat.
- ✅ Jalan di pull request **dan** di `main` setelah merge.
- 🚫 Jangan jalankan load test penuh atau suite E2E panjang setiap push — jadwalkan malam atau sebelum rilis.
- 🚫 Jangan pakai CI sebagai satu-satunya loop umpan balik; jalankan check cepat lokal juga (pre-commit).

## ⚠️ Kesalahan umum

- `uses: something@main` atau tag `@v1` dari penulis tidak jelas.
- Tidak ada `timeout-minutes` → tes macet bakar berjam-jam menit.
- `pip install` tanpa lockfile → CI tes versi berbeda daripada production.
- Test butuh key API asli → CI rusak setiap fork dan bocor biaya.
- Abaikan build merah "karena goyah" sampai tidak ada yang percaya CI.

:::revoshop
RevoShop tidak punya folder `.github/workflows`, tapi README-nya list pytest, Pylint, Bandit dan pip-audit. (1) Tulis `ci.yml` untuk RevoShop dengan job: `lint` (pylint + bandit), `audit` (pip-audit pada `requirements.txt`), `test` (pytest di PostgreSQL 16 service — dan pindahkan test DB dari SQLite, pelajaran 02), dan `build` (image Docker, `push: false`). (2) RevoShop pakai `requirements.txt` dengan pip, bukan uv: ganti setup-uv dengan `actions/setup-python` (SHA-pinned) dan `cache: pip`. (3) Tambah lencana status ke README. (4) Push ke branch, buka PR di fork-mu, dan screenshot run hijau untuk portofolio-mu.
:::

## 🏆 Praktik terbaik

- [ ] Trigger di `pull_request` dan `push` ke `main`; tambah `workflow_dispatch` untuk run manual.
- [ ] Top-level `permissions: contents: read`; perluas per job hanya kalau perlu.
- [ ] Pinning setiap action ke **SHA commit penuh** dengan komentar versi; aktifkan **Dependabot** untuk `github-actions` dan ekosistem package-mu.
- [ ] Install dengan **lockfile** (`uv sync --locked`, `npm ci`); cache dependency.
- [ ] Urutan check cepat → lambat; split ke parallel job; `fail-fast: false` di matrix.
- [ ] Tes terhadap **service asli** (PostgreSQL) dengan health check; jalankan migrasi di CI.
- [ ] Atur `timeout-minutes` dan `concurrency` dengan `cancel-in-progress`.
- [ ] Terbitkan hasil bisa dibaca: job summary, annotation, upload artifact (coverage, report) kalau berguna.
- [ ] Tidak ada secret jangka panjang di mana OIDC jalan; jangan pernah buka secret ke fork PR; hindari `pull_request_target`.
- [ ] Buat CI **required check** di `main`; perbaiki test goyah langsung.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke teman kerja kenapa `uses: actions/checkout@v7` kurang aman daripada SHA commit penuh, dan kenapa SHA pinning tidak berarti kamu akan terjebak di versi lama.

## 📐 Rancang

Rancang set workflow CI/CD lengkap CareerPilot untuk monorepo dengan `api/` (Flask), `web/` (React) dan `infra/` (Terraform, nanti): workflow dan job mana, trigger dan path filter, required check, caching, di mana image dipush, job mana yang deploy ke staging vs production dan dengan approval apa, dan secret/permission apa yang setiap job perlu.

:::quiz
Lihat rancangan mungkin

**Workflow**
1. `api-ci.yml` — di PR/push kalau `api/**` berubah: `lint` (ruff, mypy) → parallel `test` (service Postgres, matrix 3.13/3.14), `migrations` (upgrade di DB kosong + `alembic check`), `audit` (pip-audit, gitleaks) → `build` image.
2. `web-ci.yml` — di `web/**`: `npm ci`, `tsc --noEmit`, eslint, vitest, `npm run build`; Playwright E2E malam.
3. `infra-ci.yml` — di `infra/**`: `terraform fmt -check`, `validate`, `tflint`, `plan` dipost sebagai PR comment.
4. `deploy.yml` — di push ke `main` (setelah CI via `workflow_run` atau dalam workflow yang sama dengan `needs`): push `careerpilot-api:<sha>` ke GHCR/ECR → deploy **staging** otomatis → smoke test → job **production** pakai GitHub **Environment** dengan approval reviewer perlu.
5. `nightly.yml` — schedule: Locust smoke load test di staging, audit dependency, AI eval suite.

**Required check di main:** `api-ci / lint`, `api-ci / test (3.13)`, `api-ci / test (3.14)`, `web-ci / build`, gitleaks. Workflow path-filter pakai job kecil "selalu lolos kalau dilewat" atau rulesets yang izinkan check dilewat.

**Permission/secret:** default `contents: read`; `build` dapat `packages: write`; job deploy dapat `id-token: write` untuk **AWS OIDC** (tidak ada kunci AWS tersimpan) scoped sama environment; secret production hanya di `production` Environment.

**Kecepatan:** uv/npm caching, Docker `type=gha` cache, `concurrency` batalkan di PR (tidak di deploy — deploy antri daripada batalkan).
:::

### 📝 Checklist review mandiri

- [ ] Check cepat gerbang yang lambat
- [ ] Deploy production butuh approval dan pakai kredensial jangka pendek
- [ ] Path filter tidak biarkan perubahan lewati check wajib
- [ ] Deploy concurrency tidak batalkan deploy yang sedang berjalan

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m2/w6/07-github-actions-ci" ai="ai-allowed" title="Perbaiki workflow lemah dan terbitkan hasil tes bisa dibaca"}
Ubah workflow satu-job naif jadi pipeline asli — trigger, permission privilege minimal, concurrency, action SHA-pinned, job lint/type-check, service PostgreSQL dengan matrix Python, dan build image main-only — plus config Dependabot. Lalu tulis `junit_summary.py`, yang ubah laporan JUnit pytest asli jadi job summary dan annotation error yang di-escape dengan benar.
:::

:::hints
- `xml.etree.ElementTree.fromstring` + `root.findall("testsuite")` / `suite.iter("testcase")`.
- `case.find("failure")` return `None` kalau tidak ada — jangan andalkan truthiness Element.
- Escape `%` **duluan**, kalau tidak kamu double-escape `%` di `%0A`.
- Test baca YAML dengan PyYAML, yang ubah `on:` jadi `True` — fixture menangani untuk kamu.
- Dapat SHA dengan `git ls-remote https://github.com/<owner>/<repo> refs/tags/<tag>`.
:::

### 🏆 Stretch goal

Install **actionlint** (`brew install actionlint`) dan jalankan di `workflows/ci.yml`-mu. Lalu buat repo publik kecil dengan workflow ini dan test gagal — lihat job summary dan annotation di GitHub.

## ✅ Cek cepat

:::quiz
Bagaimana job dalam workflow jalan secara default, dan bagaimana kamu buat satu tunggu yang lain?

Sejajar di runner terpisah; pakai `needs: [job_a, job_b]` untuk tunggu.
:::

:::quiz
Kenapa atur `permissions: contents: read` di atas?

Supaya `GITHUB_TOKEN` otomatis hanya punya akses baca — kalau step atau action dikompromi, tidak bisa push kode, buat rilis atau ubah issue.
:::

:::quiz
Kenapa kutip `"3.10"` dalam matrix?

Tanpa kutip, YAML parse sebagai angka 3.1, yang pilih versi Python salah.
:::


## 📚 Lanjut belajar

- [GitHub Docs — Understanding GitHub Actions](https://docs.github.com/en/actions/get-started/understand-github-actions)
- [GitHub Docs — Security hardening for GitHub Actions](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions)
- [GitHub Docs — Creating PostgreSQL service containers](https://docs.github.com/en/actions/use-cases-and-examples/using-containerized-services/creating-postgresql-service-containers)
- [uv: Using uv in GitHub Actions](https://docs.astral.sh/uv/guides/integration/github/)
- [actionlint](https://github.com/rhysd/actionlint)

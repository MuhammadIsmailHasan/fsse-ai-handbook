---
title: "GitHub Actions: Lint → Test → Build → Push → Deploy"
summary: Bangun pipeline GitHub Actions lengkap — job graph dan output, service container, caching, push ke GHCR dengan digest, workflow deploy yang bisa dipakai ulang, deploy SSH dan AWS, smoke test, rollback, dan keamanan workflow.
sourceHash: 11cbc05ee472
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Merancang **job graph** dengan `needs`, kondisi, dan **job output**
- **Service container** (PostgreSQL, Redis) untuk tes integrasi
- Caching (`setup-python`, Docker `type=gha`), **matrix**, dan path filter
- Build dan push ke **GHCR** dengan `docker/metadata-action`, dan teruskan **digest**-nya
- **Reusable workflow** (`workflow_call`) untuk deploy
- Target deploy: **server lewat SSH** (Week 3–4 EC2) dan **AWS API dengan OIDC**
- **Smoke test** setelah deploy, riwayat deploy, dan workflow **rollback**
- **Keamanan** workflow: permission, SHA pinning, script injection, `pull_request_target`

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Workflow** | File YAML yang menjelaskan langkah otomatis yang dijalankan GitHub |
| **Job** | Satu bagian dari workflow yang berjalan di mesin segar sendiri |
| **Runner** | Mesin sementara yang GitHub berikan untuk menjalankan job |
| **Job output** | Potongan kecil teks yang satu job teruskan ke job berikutnya |
| **Service container** | Container pembantu (PostgreSQL, Redis) yang menyala khusus untuk tes |
| **GHCR** | GitHub Container Registry — tempat image-mu disimpan |
| **Reusable workflow** | Satu file workflow yang dipanggil oleh workflow lain, bukan copy-paste |
| **OIDC** | Login ke AWS dengan token sesaat, bukan kunci tersimpan |
| **Script injection** | Teks dari orang lain masuk ke dalam perintah shell-mu |
| **Concurrency group** | Aturan agar dua run dari hal yang sama tidak saling tumpang-tindih |

## 🧠 Ide besarnya

Workflow itu seperti **estafet dengan papan tulis**. Setiap runner (job) menyala di trek segar (mesin baru), menjalankan satu sesi, dan menulis hasilnya di papan tulis (job output, artifact) untuk runner berikutnya.

Hal terpenting di papan tulis itu adalah **image digest**: setiap sesi berikutnya harus membawa build yang persis sama, bukan "apa pun yang `latest` menjadi sekarang".

## ❓ Kenapa ini penting

Di Module 2 CI-mu sudah membuktikan kode berjalan. Sekarang pipeline juga harus **mengirimkan** kode itu: push image, deploy ke staging, cek masih hidup, dan biarkan kamu mempromosi image yang sama ke production dengan satu approval — aman, bahkan saat orang asing membuka pull request di repo publikmu.

Tanpa hati-hati ini:

- Job deploy membangun image lagi → staging dan production jalan kode berbeda.
- `run: ssh deploy@server "docker pull app:latest"` — dan `latest` berubah antara staging dan production.
- Pull request dari fork mengubah workflow jadi mencetak `secrets.DEPLOY_KEY`.
- Deploy dibatalkan di tengah-tengah karena commit baru tiba (`cancel-in-progress: true` di deploy).

## 📖 Langkah demi langkah

### 1. Job graph-nya

```mermaid
flowchart LR
    lint --> test --> build
    build -->|main| staging["deploy-staging<br/>(reusable workflow)"]
    build -->|tag v*| production["deploy-production<br/>(reusable workflow, approval)"]
```

```yaml
jobs:
  build:
    needs: test
    outputs:
      image: ghcr.io/${{ github.repository }}@${{ steps.build.outputs.digest }}
    steps: [...]
  deploy-staging:
    needs: build
    if: github.ref == 'refs/heads/main'
    uses: ./.github/workflows/deploy.yml
    with:
      environment: staging
      image: ${{ needs.build.outputs.image }}
    secrets: inherit
```

- Job berjalan di **mesin terpisah**, jadi tidak ada yang dibagikan otomatis: teruskan string kecil dengan **output** dan file dengan **artifact**.
- Kondisi level-job `if` melompati job itu. Kalau job di `needs` dilewat atau gagal, job setelahnya dilewat juga — kecuali `if`-nya pakai `!cancelled()` atau `always()`. Jaga kondisinya tetap sederhana.

### 2. Tes integrasi dengan service

```yaml
test:
  services:
    postgres:
      image: postgres:16-alpine
      env: { POSTGRES_PASSWORD: postgres, POSTGRES_DB: test }
      ports: ["5432:5432"]
      options: >-
        --health-cmd pg_isready --health-interval 5s --health-timeout 3s --health-retries 10
    redis:
      image: redis:8-alpine
      ports: ["6379:6379"]
      options: --health-cmd "redis-cli ping" --health-interval 5s --health-retries 10
  env:
    DATABASE_URL: postgresql://postgres:postgres@localhost:5432/test
    REDIS_URL: redis://localhost:6379/0
```

Pakai **mesin database dan versi major yang sama seperti production**. Test di SQLite itu seperti latihan pernikahan di ruang tamu: langkah-langkahnya muat, tapi ruangan sungguhan berperilaku lain (constraint, JSON, timezone, locking).

### 3. Kecepatan: caching, matrix, filter

```yaml
- uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0
  with: { python-version: "3.12", cache: pip }

strategy:
  fail-fast: false
  matrix:
    python-version: ["3.12", "3.13"]     # libraries: test several versions; apps: test the one you deploy

on:
  pull_request:
    paths-ignore: ["docs/**", "**.md"]
```

### 4. Build dan push dengan digest

```yaml
build:
  permissions: { contents: read, packages: write }
  steps:
    - uses: docker/setup-buildx-action@37fe631027851001ddb9b187196cc803df7f5f0e # v4.3.0
    - uses: docker/login-action@dbcb813823bdd20940b903addbd779551569679f # v4.6.0
      if: github.event_name != 'pull_request'
      with: { registry: ghcr.io, username: "${{ github.actor }}", password: "${{ secrets.GITHUB_TOKEN }}" }
    - id: meta
      uses: docker/metadata-action@dc802804100637a589fabce1cb79ff13a1411302 # v6.2.0
      with:
        images: ghcr.io/${{ github.repository }}
        tags: |
          type=sha
          type=ref,event=branch
          type=semver,pattern={{version}}
    - id: build
      uses: docker/build-push-action@53b7df96c91f9c12dcc8a07bcb9ccacbed38856a # v7.3.0
      with:
        target: prod
        push: ${{ github.event_name != 'pull_request' }}
        tags: ${{ steps.meta.outputs.tags }}
        labels: ${{ steps.meta.outputs.labels }}
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

`GITHUB_TOKEN` dengan `packages: write` cukup untuk push ke GHCR — tidak butuh personal token. Pull request masih membangun image (untuk tangkap error Dockerfile) tapi tidak push-nya.

### 5. Satu workflow deploy yang bisa dipakai ulang

```yaml
# .github/workflows/deploy.yml
on:
  workflow_call:
    inputs:
      environment: { required: true, type: string }
      image: { required: true, type: string }
permissions:
  contents: read
jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: ${{ inputs.environment }}
    concurrency: { group: "deploy-${{ inputs.environment }}", cancel-in-progress: false }
    timeout-minutes: 20
    steps: [...]
```

Satu resep, dimasak untuk staging dan untuk production — hanya variable, secret, dan aturan approval lingkungan yang berbeda. `cancel-in-progress: false` penting di sini: batalkan deploy di tengah-tengah bisa tinggalkan migration sudah diterapkan tapi kode lama masih jalan.

### 6. Target deploy

**Server dengan Docker Compose (EC2-mu di Week 4)**:

```yaml
- name: Deploy over SSH
  env:
    IMAGE: ${{ inputs.image }}
    SSH_KEY: ${{ secrets.DEPLOY_SSH_KEY }}
    HOST: ${{ vars.DEPLOY_HOST }}
    KNOWN_HOSTS: ${{ vars.DEPLOY_KNOWN_HOSTS }}
  run: |
    install -m 600 /dev/null ~/.ssh/deploy_key && printf '%s\n' "$SSH_KEY" > ~/.ssh/deploy_key
    printf '%s\n' "$KNOWN_HOSTS" >> ~/.ssh/known_hosts          # pin the host key: no "yes" to strangers
    ssh -i ~/.ssh/deploy_key "deploy@$HOST" "API_IMAGE=$IMAGE /opt/revoshop/deploy.sh"
```

Tulis `known_hosts` sendiri jadi pipeline hanya bicara ke server yang sudah tahu — seperti cek plat nomor pengemudi sebelum naik.

Di server, `deploy.sh` tarik digest, jalankan service `migrate`, buat ulang `api`, tunggu sehat, dan catat digest jadi kamu bisa rollback.

**AWS API (ECS, App Runner) dengan OIDC** — tidak SSH, tidak kunci berumur panjang (pelajaran 04):

```yaml
- uses: aws-actions/configure-aws-credentials@cbe3b392738ccf3f987d68400dafcf4b0624a56c # v6.2.4
  with:
    role-to-assume: ${{ vars.AWS_ROLE_ARN }}
    aws-region: ${{ vars.AWS_REGION }}
```

### 7. Smoke test, riwayat, dan rollback

```yaml
- name: Smoke test
  env: { REVOSHOP_URL: "${{ vars.APP_URL }}" }
  run: python -m pytest tests/smoke -q
```

- GitHub catat deploy per lingkungan (URL, commit, status) — itu riwayat deploy-mu.
- Tambah **rollback** workflow manual (`workflow_dispatch` dengan input `image`) yang panggil `deploy.yml` yang sama dengan digest lebih lama.
- Kalau smoke test gagal setelah deploy production, gagalkan job dengan keras. Rollback otomatis langkah baik berikutnya begitu kamu percayai smoke test.

### 8. Keamanan workflow

| Risiko | Pertahanan |
|---|---|
| Action pihak ketiga jadi berbahaya (misalnya tag pindah ke kode baru) | pin **full commit SHA** dengan komentar versi; biarkan Dependabot/Renovate update-nya |
| `GITHUB_TOKEN` terlalu banyak hak | `permissions: contents: read` di atas; tambah lebih banyak hanya di job yang perlu |
| **Script injection** dari judul PR, nama branch, isi issue | jangan pernah taruh `${{ github.event.* }}` dalam `run:`; teruskan via `env:` dan tanda kutip `"$VAR"` |
| `pull_request_target` jalankan kode orang lain dengan secret-mu | hindari; jangan pernah checkout kode PR sendiri di dalamnya |
| Secret jangkau fork | GitHub tidak beri secret ke workflow fork — jangan coba kerja sekali |
| Kredensial cetak di log | `::add-mask::` untuk nilai yang kamu buat saat runtime; lebih suka OIDC daripada kunci tersimpan |
| Deploy dari branch tidak diulas | lingkungan dengan reviewer wajib dan aturan branch/tag |

Alat: **actionlint** (sintaks dan kesalahan ekspresi) dan **zizmor** (ulasan keamanan workflow) di CI.

### Pilih setup-mu

- ✅ Bentuk ini — verifikasi → build sekali → deploy staging → approval → production — cocok untuk hampir semua layanan.
- ✅ Pindahkan langkah deploy ke workflow yang bisa dipakai ulang begitu dua lingkungan atau dua layanan deploy dengan cara yang sama.
- 🚫 Jangan pernah beri pull request workflow izin tulis atau secret deploy.
- 🚫 Jangan pernah deploy dengan `latest` atau nama branch — deploy digest.
- SSH ke server sederhana dan murah tapi kamu urus kunci; deploy cloud-native (ECS/App Runner) beri IAM, rollback, dan scaling tapi tambah konsep dan biaya AWS.

## ⚠️ Kesalahan umum

- Pakai **tag** image sebagai job output daripada digest.
- Service container tanpa pilihan health → test mulai sebelum PostgreSQL siap.
- `needs.build.outputs.image` kosong karena output tidak dideklarasikan di level job.
- Lupa `packages: write` → "denied: installation not allowed to Create organization package".

## 🏆 Praktik terbaik

- [ ] Job graph dengan `needs` eksplisit; teruskan digest lewat output.
- [ ] Tes integrasi lawan mesin database production, pakai service.
- [ ] Cache dependency dan Docker layer; jaga run PR cepat.
- [ ] Push image hanya dari event terpercaya; tag dengan SHA; deploy dengan digest.
- [ ] Satu workflow deploy yang bisa dipakai ulang; lingkungan pegang konfigurasi, secret, dan approval.
- [ ] Deploy concurrency group yang tidak batalkan; `timeout-minutes` di setiap job.
- [ ] Smoke test setelah setiap deploy; workflow rollback yang sudah kamu coba sungguh-sungguh.
- [ ] Least privilege, action SHA-pinned, tidak ada ekspresi dalam `run:`, tidak `pull_request_target` dengan kode PR.
- [ ] Lint workflow sendiri (actionlint, zizmor) di CI.

:::revoshop
1. **SQLite vs PostgreSQL.** `tests/conftest.py` atur `os.environ['DATABASE_URL'] = 'sqlite:///:memory:'` dan pakai `db.create_all()`. Jadi 467 test-mu tidak pernah latihan **Alembic migration** atau PostgreSQL constraint (output test bahkan cetak DDL `ck_payments_status_valid` CHECK constraint-mu untuk SQLite). Rancang job CI terpisah yang mulai service `postgres:16-alpine`, jalankan `flask db upgrade` dari database kosong, lalu boot aplikasi lawan itu.
2. **Lint.** Kamu sudah punya `.pylintrc` dan `pylint` di `requirements-dev.txt`. Jalankan `pylint app config` lokal. Akan CI gagal pada warning dari hari pertama, atau mulai dengan `--fail-under` dan naikkan seiring waktu?
3. **Yang dibangun.** Di CI job `build` harus pakai target `prod` dari pelajaran W1·05. Job output apa yang perlu job deploy (petunjuk: digest), dan apa yang harus terjadi di pull request?
4. **Job end-to-end.** `compose.prod.yaml` dari W1·05 bisa jalan dalam GitHub runner: buat secret sekali pakai, `docker compose … up -d --build --wait`, lalu jalankan smoke test dengan `REVOSHOP_URL=http://localhost:8080`. Di mana dalam job graph itu cocok, dan berapa lama yang boleh kamu habiskan?
5. **Target deploy.** Kamu belum punya server (itu Week 3–4). Rancang `deploy-staging` sekarang tapi lindungi dengan `if: vars.STAGING_ENABLED == 'true'` jadi pipeline tetap hijau sampai server ada.
:::

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan estafet dengan papan tulis, dan kenapa papan tulis harus bawa digest daripada tag.

## 📐 Rancang

Tulis daftar job (nama, trigger, `needs`, permission, output) untuk repo dengan **dua layanan** — RevoShop API (Python) dan storefront Next.js — yang deploy terpisah ke staging di main dan ke production di tag. Sertakan path filter, caching, dan bagaimana kamu hindari duplikasi logika deploy.

:::quiz
Lihat rancangan mungkin

- **Trigger:** PR + push ke main + tag `api-v*` dan `web-v*` (rilis terpisah).
- **changes** job: `dorny/paths-filter` (SHA-pinned) → output `api`, `web` boolean (atau native `paths` filter di dua workflow).
- **api-verify** (`if: needs.changes.outputs.api == 'true'`): pip cache, ruff, pytest pada PostgreSQL + Redis service.
- **web-verify**: npm cache, lint, typecheck, Vitest; Playwright lawan production build.
- **api-build** / **web-build**: `packages: write` hanya pada non-PR event; setiap output `image` digest-nya.
- **deploy-api-staging** / **deploy-web-staging** (`main`): `uses: ./.github/workflows/deploy.yml` dengan `service`, `environment: staging`, `image`; `id-token: write` hanya di sini.
- **deploy-*-production** pada tag `api-v*` / `web-v*` dengan lingkungan `production` (reviewer wajib, aturan tag).
- **rollback.yml**: `workflow_dispatch` dengan input `service`, `environment`, `image` → workflow deploy yang sama bisa dipakai ulang.
- Top-level `permissions: contents: read`; concurrency `deploy-${service}-${environment}` tanpa pembatalan; action SHA-pinned; job zizmor + actionlint.
:::

### 📝 Checklist review mandiri

- [ ] Satu implementasi deploy, dipakai ulang
- [ ] Secret dan OIDC hanya di job deploy
- [ ] Layanan yang tidak berubah tidak dibangun atau di-deploy ulang

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m5/w2/02-ci-cd-workflow" ai="no-ai" title="Workflow CI/CD lengkap"}
Tulis `ci-cd.yml` (lint, test pada PostgreSQL dan Redis, build dan push dengan digest, staging di main, production di tag) dan `deploy.yml` yang bisa dipakai ulang (lingkungan, concurrency tanpa pembatalan, kredensial OIDC, script deploy, dan smoke test) — dengan action pinned, least privilege, dan tidak ada script injection.
:::

:::hints
- YAML baca `on:` sebagai boolean `True` — test menangani itu, tapi ingat saat kamu debug dengan Python.
- Job yang `uses:` workflow yang bisa dipakai ulang tidak bisa punya `steps` atau `runs-on` juga.
- Teruskan `${{ inputs.image }}` lewat `env:` dan tanda kutip `"$IMAGE"` dalam script.
:::

## ✅ Cek cepat

:::quiz
Kenapa job `deploy-staging` yang panggil workflow yang bisa dipakai ulang tidak bisa punya `timeout-minutes` sendiri?

Job yang panggil workflow yang bisa dipakai ulang hanya terima beberapa kunci (`needs`, `if`, `with`, `secrets`, `permissions`, `concurrency`, `strategy`). Timeout milik job di dalam workflow yang dipanggil.
:::

:::quiz
Pull request dari fork ubah `ci-cd.yml` jadi cetak `secrets.DEPLOY_SSH_KEY`. Apa yang terjadi dengan trigger `pull_request`?

Workflow fork berjalan tanpa secret repo-mu dan dengan token read-only, jadi secret tidak ada saja. Pakai `pull_request_target` dan checkout kode PR akan patahkan perlindungan itu.
:::

## 📚 Lanjut belajar

- [Dokumentasi GitHub: Reusing workflows](https://docs.github.com/en/actions/sharing-automations/reusing-workflows) · [Security hardening for GitHub Actions](https://docs.github.com/en/actions/security-for-github-actions/security-guides/security-hardening-for-github-actions)
- [Dokumentasi Docker: GitHub Actions](https://docs.docker.com/build/ci/github-actions/)
- [zizmor](https://docs.zizmor.sh/) · [actionlint](https://github.com/rhysd/actionlint)

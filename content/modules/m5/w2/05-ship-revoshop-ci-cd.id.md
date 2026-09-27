---
title: "🚀 Kirim RevoShop 2: Pipeline CI/CD"
summary: Letakkan RevoShop di balik pipeline sungguhan — suite test hijau dan cepat, lint, migrasi diuji di PostgreSQL, stack production diuji asap di CI, gambar di GHCR pakai digest, cabang terlindungi dan job deploy siap untuk AWS.
sourceHash: efa307181e10
---

## 🎯 Tujuan

Setelah Lab 1, RevoShop *bisa* jalan di production. Setelah lab ini, **setiap perubahan harus membuktikannya**: tidak ada yang merge tanpa cek hijau, setiap commit di `main` menghasilkan gambar di GHCR, dan job deploy menunggu dengan siap, hanya butuh server yang akan kamu buat di Minggu 3–4.

Bayangkan menyewa inspektur kualitas yang tidak pernah lelah: cek yang sama berjalan setiap perubahan, urutan sama, tanpa perlu kamu ingatkan.

```text
Sebelumnya                                    Setelah lab ini
────────────────────────────────────────────    ────────────────────────────────────────────────────
tidak ada .github/workflows                 ci-cd.yml + deploy.yml (bisa dipakai ulang)
5 test gagal di checkout bersih              suite hijau, keputusan terdokumentasi
~7.5 menit test run (bcrypt cost 12)         detik (bcrypt cost 4 hanya di tes)
Hanya tes SQLite, migrasi tidak pernah uji   Alembic upgrade → downgrade → upgrade di PostgreSQL 16
"jalan di mesinku"                           stack compose.prod.yaml + tes asap di dalam CI
gambar dibangun di server                    ghcr.io/<kamu>/revoshop@sha256:… tiap commit di main
siapa saja bisa push ke main                 ruleset: perlu PR + cek wajib; environment siap
```

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Pipeline job** | Satu bagian workflow yang jalan di mesin baru sendiri (lint, test, build…) |
| **bcrypt cost** | Berapa banyak kerja untuk hash password; tinggi aman di production, lambat di tes |
| **Migration check** | Membuktikan script database bisa jalan maju, mundur, lalu maju lagi |
| **Service container** | Container pembantu (PostgreSQL) yang hanya dimulai untuk job itu |
| **Digest** | Sidik jari gambar (`sha256:…`), jadi deploy memakai persis build yang sudah diuji |
| **Ruleset** | Aturan GitHub untuk cabang: wajib PR, wajib cek hijau, blok force push |
| **Dependabot** | Bot yang buka PR untuk update action yang dikunci, paket, dan gambar dasar |
| **Smoke test** | Beberapa cek cepat terhadap aplikasi yang jalan untuk membuktikan deploy jalan |

:::note[Yang harus ada dulu]
Lab 1 sudah merge di salinan RevoShop **milikmu** (target Dockerfile, `gunicorn.conf.py`, `compose.prod.yaml`, Caddyfile, endpoint liveness, rate limiter). Kerja di cabang baru: `git switch -c ci/pipeline`.
:::

## 🧭 Checkpoint

### C1 · Buat test cepat (45 menit)

Setiap user test hashing passwordnya dengan bcrypt default cost (`bcrypt.gensalt()` di `app/auth.py`). Hashing kuat sengaja lambat — itu poin di production, bencana saat kamu lakukan 467 kali dalam test run. Seperti memakai pintu brankas bank untuk kotak penyimpanan yang kamu buka seratus kali sehari.

```python
# app/auth.py
import os

import bcrypt


def hash_password(plain_password):
    rounds = int(os.getenv('BCRYPT_ROUNDS', '12'))
    return bcrypt.hashpw(str(plain_password).encode('utf-8'), bcrypt.gensalt(rounds=rounds)).decode('utf-8')
```

```python
# tests/conftest.py — at the very top, before importing the app
import os

os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
os.environ.setdefault('BCRYPT_ROUNDS', '4')   # fast hashing in tests only
```

Ukur sebelum dan sesudah dengan `time python -m pytest -q`. Di salinan RevoShop bersih ini mengubah suite dari **7 menit 27 detik menjadi 9 detik**, dengan hasil sama. Masukkan angkamu sendiri di deskripsi PR — itu perbaikan pertamamu yang terukur untuk pipeline.

Lalu jaga production: tambah tes membuktikan `hash_password` memakai cost 12 saat `BCRYPT_ROUNDS` tidak diset (bcrypt hash mulai dengan `$2b$12$`), dan jangan pernah set `BCRYPT_ROUNDS` di `compose.prod.yaml`. Percepatan yang diam-diam melemahkan password production adalah trade-off buruk.

### C2 · Buat suite hijau (1 jam)

Di checkout bersih ini gagal:

```text
tests/integration/test_cart.py::TestCartAvailabilityIsLive::test_cancel_restores_cart_item_availability
tests/integration/test_categories.py::TestGetCategories::test_get_categories_with_products_no_auth
tests/integration/test_categories.py::TestGetCategories::test_get_categories_no_auth
tests/integration/test_product_images.py::TestListProductImages::test_list_no_auth
tests/integration/test_products.py::TestGetProducts::test_get_products_no_auth
```

1. **Empat tes `*_no_auth`** menharap `401`, tapi endpoint listing itu mengembalikan `200` tanpa token. Untuk toko, browsing produk dan kategori tanpa login normal — pelanggan tidak harus punya kartu member untuk lihat rak. Jadi putuskan dengan tujuan: kalau public dimaksud, ubah nama jadi `test_*_is_public` menharap `200`, dan tambah tes membuktikan endpoint **tulis** (`POST /products/`, `DELETE /categories/<id>`, …) masih kembalikan `401` tanpa token. Catat keputusan di PR.
2. **Tes availability cart**: jalankan sendiri (`-k test_cancel_restores_cart_item_availability -vv`), lalu di file-nya sendiri, lalu dengan suite seluruhnya. Gagal sendiri? Kalau hanya gagal dengan yang lain, test-nya berbagi state. Baca kode `OrderService` cancellation dan bagaimana `available` cart dihitung, lalu perbaiki bug atau tes — jangan skip tanpa issue menjelaskan kenapa.
3. Commit saat `python -m pytest -q` sepenuhnya hijau lokal **tanpa** `.env`-mu ter-load (`env -u JWT_SECRET_KEY -u DATABASE_URL python -m pytest -q`), karena CI tidak akan punya.

### C3 · Smoke test hidup di repo (15 menit)

Salin smoke test dari handbook (`exercises/m5/w1/05-revoshop-smoke/test_revoshop_smoke.py`) ke `tests/smoke/test_smoke.py`. Mereka **skip** diri sendiri saat `REVOSHOP_URL` tidak diset, jadi test run normalmu tidak berubah.

### C4 · Workflow-nya (2 jam)

**`.github/workflows/ci-cd.yml`**

```yaml
name: CI/CD

on:
  pull_request:
    branches: [main]
  push:
    branches: [main]
    tags: ["v*.*.*"]
  workflow_dispatch:

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

jobs:
  lint:
    runs-on: ubuntu-latest
    timeout-minutes: 10
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0
        with:
          python-version: "3.12"
          cache: pip
      - run: pip install -r requirements-dev.txt
      - name: Pylint
        run: pylint app config --fail-under=9.5

  test:
    needs: lint
    runs-on: ubuntu-latest
    timeout-minutes: 15
    env:
      BCRYPT_ROUNDS: "4"
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0
        with:
          python-version: "3.12"
          cache: pip
      - run: pip install -r requirements-dev.txt
      - name: Unit and API tests
        run: python -m pytest -q --cov=app --cov-report=xml --junitxml=reports/junit.xml
      - uses: actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a # v7.0.1
        if: always()
        with:
          name: test-reports
          path: |
            reports/
            coverage.xml
          retention-days: 7

  migrations:
    needs: lint
    runs-on: ubuntu-latest
    timeout-minutes: 10
    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: revoshop
        ports: ["5432:5432"]
        options: >-
          --health-cmd pg_isready
          --health-interval 5s
          --health-timeout 3s
          --health-retries 10
    env:
      APP_ENV: development
      FLASK_APP: run:application
      DATABASE_URL: postgresql://postgres:postgres@localhost:5432/revoshop
      LOG_TO_FILE: "false"
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0
        with:
          python-version: "3.12"
          cache: pip
      - run: pip install -r requirements.txt
      - name: Upgrade, downgrade and upgrade again on PostgreSQL
        run: |
          flask db upgrade
          flask db downgrade base
          flask db upgrade
          flask db check   # fails if models and migrations disagree

  e2e:
    needs: [test, migrations]
    runs-on: ubuntu-latest
    timeout-minutes: 20
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0
        with:
          python-version: "3.12"
      - name: Throwaway secrets for this run
        run: |
          {
            echo "POSTGRES_PASSWORD=$(openssl rand -hex 16)"
            echo "JWT_SECRET_KEY=$(openssl rand -hex 32)"
            echo "HTTP_PORT=8080"
            echo "HTTPS_PORT=8443"
          } > .env.ci
      - name: Start the production stack
        run: docker compose --env-file .env.ci -f compose.prod.yaml up -d --build
      - name: Wait until healthy
        run: |
          for attempt in $(seq 1 60); do
            if curl -fsS http://localhost:8080/api/v1/health; then exit 0; fi
            sleep 3
          done
          docker compose --env-file .env.ci -f compose.prod.yaml logs
          exit 1
      - name: Smoke tests
        env:
          REVOSHOP_URL: http://localhost:8080
        run: |
          pip install pytest
          python -m pytest tests/smoke -v
      - name: Logs on failure
        if: failure()
        run: docker compose --env-file .env.ci -f compose.prod.yaml logs --no-color

  build:
    needs: [test, migrations]
    runs-on: ubuntu-latest
    timeout-minutes: 20
    permissions:
      contents: read
      packages: write
    outputs:
      image: ghcr.io/${{ github.repository }}@${{ steps.build.outputs.digest }}
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - uses: docker/setup-buildx-action@37fe631027851001ddb9b187196cc803df7f5f0e # v4.3.0
      - uses: docker/login-action@dbcb813823bdd20940b903addbd779551569679f # v4.6.0
        if: github.event_name != 'pull_request'
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - id: meta
        uses: docker/metadata-action@dc802804100637a589fabce1cb79ff13a1411302 # v6.2.0
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=sha
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
      - id: build
        uses: docker/build-push-action@53b7df96c91f9c12dcc8a07bcb9ccacbed38856a # v7.3.0
        with:
          context: .
          target: prod
          platforms: linux/amd64
          push: ${{ github.event_name != 'pull_request' }}
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          build-args: |
            VERSION=${{ steps.meta.outputs.version }}
            REVISION=${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max

  deploy-staging:
    needs: [build, e2e]
    if: github.ref == 'refs/heads/main' && vars.STAGING_ENABLED == 'true'
    uses: ./.github/workflows/deploy.yml
    with:
      environment: staging
      image: ${{ needs.build.outputs.image }}
    secrets: inherit
    permissions:
      contents: read
      id-token: write

  deploy-production:
    needs: [build, e2e]
    if: startsWith(github.ref, 'refs/tags/v') && vars.PRODUCTION_ENABLED == 'true'
    uses: ./.github/workflows/deploy.yml
    with:
      environment: production
      image: ${{ needs.build.outputs.image }}
    secrets: inherit
    permissions:
      contents: read
      id-token: write
```

- `platforms: linux/amd64` karena runner GitHub dan instans `t3` EC2 adalah x86. Kalau kamu pilih Graviton (`t4g`) di Minggu 3, ubah jadi `linux/arm64`.
- Di salinan RevoShop bersih, upgrade → `downgrade base` → upgrade → `flask db check` semua lulus di PostgreSQL 16 (`No new upgrade operations detected`). Kalau perubahan model nanti lupa migrasi, `flask db check` gagal — itu potongannya.
- `pylint --fail-under=9.5`: salinan bersih RevoShop hari ini scoring **9.77/10**, jadi 9.5 tangkap regresi tanpa blok kamu; naikkan seiring kamu perbaiki warning.

**`.github/workflows/deploy.yml`** — siap untuk Minggu 4 (EC2 atas SSH); disabled sampai kamu set `STAGING_ENABLED=true`:

```yaml
name: Deploy

on:
  workflow_call:
    inputs:
      environment:
        required: true
        type: string
      image:
        required: true
        type: string

permissions:
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    timeout-minutes: 20
    environment: ${{ inputs.environment }}
    concurrency:
      group: deploy-${{ inputs.environment }}
      cancel-in-progress: false
    permissions:
      contents: read
      id-token: write
    steps:
      - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
        with:
          persist-credentials: false
      - name: Deploy over SSH
        env:
          IMAGE: ${{ inputs.image }}
          SSH_KEY: ${{ secrets.DEPLOY_SSH_KEY }}
          HOST: ${{ vars.DEPLOY_HOST }}
          KNOWN_HOSTS: ${{ vars.DEPLOY_KNOWN_HOSTS }}
        run: |
          mkdir -p ~/.ssh
          install -m 600 /dev/null ~/.ssh/deploy_key
          printf '%s\n' "$SSH_KEY" > ~/.ssh/deploy_key
          printf '%s\n' "$KNOWN_HOSTS" >> ~/.ssh/known_hosts
          ssh -i ~/.ssh/deploy_key "deploy@$HOST" "API_IMAGE=$IMAGE /opt/revoshop/deploy.sh"
      - uses: actions/setup-python@5fda3b95a4ea91299a34e894583c3862153e4b97 # v7.0.0
        with:
          python-version: "3.12"
      - name: Smoke tests
        env:
          REVOSHOP_URL: ${{ vars.APP_URL }}
          REVOSHOP_EXPECT_HTTPS: "1"
        run: |
          pip install pytest
          python -m pytest tests/smoke -v
```

`/opt/revoshop/deploy.sh` di server, dan setup SSH/OIDC, datang di Minggu 4. Karena langkah deploy hidup di satu file bisa dipakai ulang, pindah ke ECS nanti hanya ubah file ini — bukan seluruh pipeline.

### C5 · Pengaturan repository (45 menit)

Di repository pribadimu di GitHub:

1. **Settings → Rules → Rulesets → New branch ruleset** untuk `main`: wajib pull request (1 approval opsional saat solo — paling sedikit wajib PR), wajib cek status `lint`, `test`, `migrations`, `e2e`, `build`, blok force push dan penghapusan.
2. **Settings → Environments**: buat `staging` (deployment branch: `main`) dan `production` (deployment tags: `v*`; required reviewer kalau paket kamu boleh). Tambah variabel `STAGING_ENABLED=false` / `PRODUCTION_ENABLED=false` di level repository untuk sekarang.
3. **Settings → Code security**: aktifkan secret scanning dan push protection (gratis untuk repo publik; cek apa yang paket kamu tawarkan untuk private).
4. **`.github/dependabot.yml`** jadi SHA yang dikunci dan gambar dasar tidak basi:

```yaml
version: 2
updates:
  - package-ecosystem: github-actions
    directory: /
    schedule: { interval: weekly }
  - package-ecosystem: pip
    directory: /
    schedule: { interval: weekly }
  - package-ecosystem: docker
    directory: /
    schedule: { interval: weekly }
```

5. **Settings → Actions → General → Workflow permissions**: "Read repository contents and packages permissions" (workflow-mu tambah apa yang mereka butuh).

### C6 · Buktikan pipeline (45 menit)

- Buka PR `ci/pipeline` → semua cek hijau; unduh artifact `test-reports`.
- Rusak sesuatu sengaja di cabang throwaway (ubah tipe kolom migrasi, atau kembalikan `500` dari `/api/v1/health/live`) dan konfirmasi job yang *tepat* gagal. Pipeline yang belum pernah kamu lihat gagal adalah alarm asap yang belum pernah kamu uji.
- Merge → gambar `sha-…` muncul di bawah **Packages** di profile/repository-mu. Pull di laptop: `docker pull ghcr.io/<kamu>/revoshop@sha256:…` (login dengan PAT yang punya `read:packages` kalau paket private).
- Catat di `docs/pipeline.md`: durasi job, total waktu feedback PR, dan baseline DORA yang kamu tulis di materi 01.

## ✅ Selesai saat

- [ ] Suite test hijau di checkout bersih dan jalan dalam detik; bcrypt cost 12 masih dipaksa di luar tes
- [ ] `ci-cd.yml` + `deploy.yml` merge; PR check wajib di ruleset
- [ ] Migrasi diverifikasi upgrade → downgrade → upgrade di PostgreSQL 16
- [ ] Stack Compose production menyala di CI dan smoke test lulus
- [ ] Gambar di GHCR tagged `sha-*` dan `main`, dirujuk pakai digest di output job
- [ ] Environment `staging` dan `production` dibuat; job deploy dijaga sampai Minggu 4
- [ ] Dependabot, secret scanning, dan workflow permission least-privilege aktif

## 🧠 Kebijakan AI

🤖✅ AI boleh membantu dengan error syntax YAML dan navigasi pengaturan GitHub. 🚫🤖 Diagnosa dan perbaiki tes yang gagal sendiri, dan bisa jelaskan setiap job, kondisi, dan permission.

## ❓ Pertanyaan yang mungkin ditanya pewawancara

- Test-mu butuh 7.5 menit. Bagaimana kamu temukan sebabnya, dan bagaimana kamu pastikan production masih memakai bcrypt cost kuat?
- Empat test menharap `401` di endpoint publik. Bagaimana kamu putuskan apakah kode atau tes yang salah?
- Kenapa test migrasi terpisah di PostgreSQL saat suite sudah lulus di SQLite?
- Apa yang job `e2e` buktikan yang unit test tidak bisa?
- Kenapa job deploy terima gambar pakai **digest**, dan apa yang salah dengan `latest`?

## 📣 Bagikan

:::linkedin{type="weekly"}
⚙️ Module 5 · Minggu 2: RevoShop API-ku sekarang punya pipeline CI/CD sungguhan.

Bagian yang paling membanggakan: suite tes turun dari 7 menit 27 detik menjadi 9 detik. Penyebabnya bcrypt hash setiap user tes di production cost — sekarang tes memakai cost rendah, production masih pakai 12 (dan tes membuktikannya).

Juga:
- perbaiki 5 tes yang sudah gagal tidak diperhatikan (4 menharap 401 di endpoint yang sengaja publik)
- migrasi diuji upgrade → downgrade → upgrade di PostgreSQL 16
- stack production penuh (Caddy, gunicorn, PostgreSQL, Redis) boots di dalam CI dan smoke test memukul
- gambar push ke GHCR pakai digest, action dikunci ke commit SHA, rule cabang wajib cek hijau

Selanjutnya: AWS. ☁️

#GitHubActions #CICD #Python #DevOps #BelajarDiPublik
:::

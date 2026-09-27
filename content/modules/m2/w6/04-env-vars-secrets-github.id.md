---
title: "Keamanan: Variabel Lingkungan & GitHub"
summary: Pisahkan konfigurasi dari kode dan rahasia dari Git — setelan terukur dan fail-fast, file .env yang benar, pemindai rahasia, keamanan GitHub, dan apa yang harus dilakukan kalau rahasia bocor.
sourceHash: 660736f96b49
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- **Konfigurasi vs kode** (ide Twelve-Factor) dan kenapa variabel lingkungan
- `.env` / `.env.example` / `.gitignore` — cara yang benar
- Setelan **terukur, tervalidasi, fail-fast** daripada default yang senyap
- Di mana rahasia tinggal di **CI** dan **production** (GitHub Actions secrets, secret manager)
- **Pemindai rahasia** (gitleaks, GitHub push protection) dan pre-commit hook
- Dasar keamanan GitHub: 2FA, SSH key, token butir halus, branch protection, Dependabot
- **Playbook rahasia bocor**: rotate dulu, baru bersihkan

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Konfigurasi** | Setelan yang beda tiap lingkungan (URL, key) |
| **Variabel lingkungan** | Nilai yang diberikan ke aplikasi dari luar |
| **File `.env`** | Berkas lokal berisi nilai-nilai — jangan pernah di-commit |
| **`.env.example`** | Contoh berkas yang dicatat, isi tanpa nilai asli |
| **Fail fast** | Berhenti kalau setelan wajib tidak ada |
| **Pemindai rahasia** | Alat yang memblokir atau menemukan rahasia di repo |
| **Push protection** | GitHub menolak push yang berisi rahasia |
| **Rotasi** | Mengganti rahasia dengan yang baru |

## 🧠 Ide besarnya

Kodemu adalah **denah rumah** — kamu bisa tunjukkan ke siapa saja. Rahasia adalah **kunci rumah**. Kamu tidak menempel kunci ke denah, dan tentu tidak fotokopi denahnya (`git clone`) sambil bawa kunci.

Variabel lingkungan adalah **tempat kunci di tiap pintu**: denah yang sama jalan di rumah mana saja (laptopmu, CI, production), dan tiap rumah punya kunci-nya sendiri.

## ❓ Kenapa ini penting

- Kode yang sama jalan di development, test, staging dan production dengan **database, key, dan setelan berbeda**.
- Rahasia di Git **selamanya**: tiap clone, fork, CI cache, dan backup simpan mereka, bahkan kalau kamu hapus baris-nya.
- Bot pemindai publik GitHub terus-menerus; key cloud yang bocor disalahgunakan dalam **hitungan menit** (tagihan crypto-mining, pencurian data).
- Key AI dihitung per pakai, jadi key yang bocor bisa biaya sungguhan dengan cepat.

Kesalahan paling umum adalah default yang terlihat ramah:

```python
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-secret-key-change-in-production")
```

Seseorang lupa atur variabel di production. Aplikasi **menyala dengan senang** pakai secret yang publik di GitHub. Siapa saja sekarang bisa tanda tangani token dengan `"role": "admin"` — dan tidak ada alarm.

Kejadian lain: `.env` di-commit di commit pertama lalu "dihapus" di commit kedua (masih di history), dan `DEBUG=True` di production, yang biarkan pengunjung jalankan Python di server lewat debugger.

## 📖 Langkah demi langkah

### 1. Konfigurasi harus di lingkungan

| Masuk di **kode** | Masuk di **lingkungan** |
|---|---|
| Route API, aturan bisnis | `DATABASE_URL`, `REDIS_URL` |
| Ukuran halaman default, batas validasi | `JWT_SECRET_KEY`, `OPENAI_API_KEY` |
| Logika fitur | `APP_ENV`, `LOG_LEVEL`, `PORT` |
| | Asal CORS boleh, URL layanan eksternal |

Aturan jempol dari [The Twelve-Factor App](https://12factor.net/config): bisa kamu buka-kode repo **sekarang** tanpa bocor apa-apa? Kalau tidak, konfigurasi ada di kode.

### 2. File `.env` — hanya kemudahan lokal

```bash
# .env.example  ← COMMITTED: documents every variable, with placeholders
APP_ENV=development
DATABASE_URL=postgresql://fsse:fsse@localhost:5491/careerpilot
JWT_SECRET_KEY=change-me
OPENAI_API_KEY=
```

```bash
# .gitignore  ← ignore every real env file, keep the example
.env
.env.*
!.env.example
```

- `cp .env.example .env`, lalu isi dengan nilai asli lokal.
- `python-dotenv` (atau `uv run --env-file .env`) memuat **saat development**. Di production, platform (Docker, ECS, Render, GitHub Actions) suntik variabel lingkungan asli — tidak ada file `.env` di server.
- Cek: `git check-ignore -v .env` seharusnya cetak aturan `.gitignore` yang cocok.

### 3. Setelan terukur, tervalidasi, fail-fast

Rahasia yang tidak ada seharusnya hentikan aplikasi saat startup, keras. Rahasia yang salah tapi biarkan aplikasi jalan jauh lebih berbahaya daripada aplikasi yang tolak menyala.

Baca lingkungan **sekali**, saat startup, ke objek terukur — dan tolak menyala kalau ada yang salah:

```python
@dataclass(frozen=True)
class Settings:
    app_env: str
    database_url: str = field(repr=False)      # never shown in repr / logs
    jwt_secret_key: str = field(repr=False)
    debug: bool
    port: int


def load_settings(env: Mapping[str, str]) -> Settings:
    errors = []
    if env.get("APP_ENV") == "production" and len(env.get("JWT_SECRET_KEY", "")) < 32:
        errors.append("JWT_SECRET_KEY must be at least 32 characters in production")
    ...
    if errors:
        raise SettingsError(errors)      # report ALL problems at once
```

```python
def create_app(settings: Settings | None = None) -> Flask:
    settings = settings or load_settings(os.environ)   # crash at deploy time, not at 2 a.m.
```

- **Fail fast**: deploy yang rusak yang tidak menyala ketangkap oleh health check langsung; deploy yang jalan dengan rahasia salah adalah insiden yang senyap.
- Parse tipe (`"false"` adalah string yang benar di Python!).
- Ambil `env` sebagai parameter buat trivial testable — tidak perlu `monkeypatch`.
- Library: **pydantic-settings** lakukan ini deklaratif (kamu pakai di modul FastAPI).

:::fastapi
Proyek FastAPI biasanya pakai `pydantic-settings`: `class Settings(BaseSettings): jwt_secret_key: SecretStr = Field(min_length=32)`. `SecretStr` sembunyikan nilai di `repr` dan log; nilai yang hilang atau tidak sah naikkan validation error saat startup.
:::

### 4. Buat rahasia yang kuat

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Pakai rahasia beda tiap lingkungan. Tidak pernah pakai ulang rahasia dev di production.

### 5. Rahasia di CI dan production

```mermaid
flowchart LR
    Dev[".env di laptopmu<br/>(git-ignored)"] -.tidak pernah.-> Git[(GitHub repo)]
    GHS["GitHub Actions secrets<br/>${{ secrets.X }}"] --> CI[CI job env var]
    SM["Secret manager<br/>AWS Secrets Manager / SSM"] --> Prod[Container production<br/>env var saat start]
```

- **GitHub Actions**: *Settings → Secrets and variables → Actions*, dipakai sebagai `${{ secrets.OPENAI_API_KEY }}`; tersembunyi di log (materi 07).
- **Production**: secret manager (AWS Secrets Manager / SSM Parameter Store — Modul 5) atau setelan env terenkripsi platform-mu. Akses tercatat dan bisa di-rotate.
- Hak terkecil: key CI bisa jalankan test, bukan hapus production.

### 6. Pindai untuk rahasia

- **gitleaks** / **trufflehog**: pindai file dan **sejarah git penuh** untuk pola key; jalankan di pre-commit hook dan di CI.
- **GitHub secret scanning & push protection**: blokir push yang berisi format token dikenal. Gratis di repo publik; di repo privat bagian dari GitHub Secret Protection berbayar — jadi untuk repo privat-mu, jalankan gitleaks sendiri.

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.30.1   # pin a release tag (check for the latest)
    hooks:
      - id: gitleaks
```

Cara pemindai jalan (kamu akan buat mini): **format dikenal** (`AKIA…`, `ghp_…`, header key privat) plus **heuristik** (variabel bernama `*password*` diberi literal panjang), dengan **allowlist** untuk placeholder.

### 7. Amankan GitHub sendiri

- [ ] **2FA** di akun-mu (passkey atau authenticator app).
- [ ] Push dengan **SSH key** (atau credential manager), bukan password di URL.
- [ ] Pakai **token akses personal butir halus**: satu repo, izin minimum, tanggal habis.
- [ ] **Branch protection / ruleset** di `main`: perlu PR + CI lulus.
- [ ] **Alert Dependabot & security update** untuk dependensi rentan; `pip-audit` / `npm audit` lokal.
- [ ] Review GitHub App dan Action pihak ketiga yang kamu beri akses; kunci action ke versi.

### 8. Playbook rahasia bocor

Urutan penting: **rotate dulu**, lalu selidiki, lalu bersihkan history. Bersihkan history dulu tinggal key lama jalan sementara kamu rapihkan.

1. **Revoke / rotate rahasia langsung** — anggap sudah disalin. (Ubah Git history TIDAK un-leak-nya.)
2. Cek penyalahgunaan: log provider, tagihan, log akses.
3. Deploy rahasia baru lewat env/secret manager.
4. Hapus dari kode; kalau repo dibagikan, tulis ulang history dengan `git filter-repo` dan minta rekan clone ulang.
5. Tambah pemindai/pre-commit hook supaya tidak terjadi lagi; tulis catatan singkat tanpa menyalahkan.

### Pilih setupmu

Setiap pilihan di sini trade-off:

| Pilihan | ✅ | ❌ |
|---|---|---|
| Env var | universal, sederhana, twelve-factor | string datar, terlihat ke proses dan anak-nya, tidak ada audit trail |
| File `.env` lokal | onboarding mudah | mudah di-commit accident; tidak boleh sampai ke server |
| Secret manager | audit log, rotasi, kontrol akses halus | biaya, setup, ketergantungan jaringan saat startup |
| Default senyap | "langsung jalan" lokal | berbahaya di production |
| Validasi fail-fast | misconfig ketangkap saat deploy | sedikit lebih banyak kode; harus simpan default dev mudah |

- ✅ Apa saja yang beda tiap lingkungan atau sensitif → environment/secret manager.
- ✅ Validasi setelan saat startup di setiap service.
- 🚫 Tidak pernah masukkan konstanta yang tidak berubah tiap lingkungan ke env var — itu saja penghamburan konfigurasi.
- 🚫 Tidak pernah berikan rahasia sebagai argumen command-line (terlihat di `ps`) atau di URL/query string (tercatat).

## ⚠️ Kesalahan umum

- `os.getenv("KEY", "some-default-secret")`.
- `bool(os.getenv("DEBUG"))` → `"false"` adalah `True`.
- `.gitignore` punya `.env` tapi bukan `.env.docker` / `.env.production`.
- Tempel `.env` ke chat, isu, atau asisten AI untuk "debug".
- Hapus baris bocor dan pikir sudah diperbaiki.

:::revoshop
Buka `config/base.py` RevoShop: (1) `JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY', 'super-secret-key-change-in-production')` — persis default berbahaya dari materi ini. Apa terjadi kalau production lupa variabel? (2) `MIDTRANS_SERVER_KEY` default ke `''`: error apa yang lihat pengguna saat checkout, dan kapan kamu tahu? (3) `.gitignore` abaikan `.env` dengan `!.env.example` — file `.env.docker` diabaikan? Uji dengan `git check-ignore -v .env.docker`. (4) Jalankan `scan_directory` materi ini di folder RevoShop dan triage setiap temuan. (5) Sketsa `load_settings` untuk RevoShop yang fail-fast di production.
:::

## 🏆 Praktik terbaik

- [ ] Tidak ada rahasia di kode, commit, isu, screenshot, log atau chat AI.
- [ ] Catat `.env.example` dengan **setiap** variabel dan placeholder; abaikan `.env` dan `.env.*`.
- [ ] Muat setelan **sekali** ke objek terukur; **fail-fast** dengan semua error terdaftar; tidak ada default production tidak aman.
- [ ] Sembunyikan rahasia di `repr`/log (`field(repr=False)`, `SecretStr`); log **ringkasan aman** saja.
- [ ] Rahasia beda, kuat (`secrets.token_urlsafe`) tiap lingkungan; rotate berkala dan saat perubahan staff.
- [ ] Jalankan **gitleaks** di pre-commit hook dan CI; nyalakan push protection di mana ada.
- [ ] Simpan CI secret di **GitHub Actions secrets**, production secret di **secret manager**.
- [ ] 2FA, SSH key, token datar habis masa berlaku, branch protection, Dependabot.
- [ ] Kalau rahasia bocor: **rotate dulu**, lalu selidiki dan bersihkan history.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Rekan junior commit `.env` dengan Midtrans server key, lalu push commit baru menghapusnya, dan bilang "sudah aman". Jelaskan kenapa tidak, dan apa yang kamu lakukan di 30 menit berikutnya.

## 📐 Rancang

Rancang konfigurasi dan penanganan rahasia untuk CareerPilot di **lokal**, **CI** dan **production**: catat setiap variabel (DB, JWT, key OpenAI/Anthropic, email provider, CORS, log level), di mana nilai tiap satu tinggal di tiap lingkungan, siapa bisa akses, aturan validasi, dan rencana rotasi untuk key AI.

:::quiz
Lihat contoh rancangan

| Variabel | Lokal | CI | Production | Validasi |
|---|---|---|---|---|
| `APP_ENV` | `.env` = development | workflow env = test | task definition = production | enum |
| `DATABASE_URL` | `.env` (Docker Postgres 5491) | service container URL di workflow | Secrets Manager (RDS credentials) | wajib |
| `JWT_SECRET_KEY` | opsional (default dev tidak aman) | dibuat tiap run di workflow | Secrets Manager, 64 char | prod ≥ 32, bukan placeholder |
| `LLM_API_KEY` | key pribadi-mu, batas pengeluaran rendah | **tidak perlu** — test pakai klien LLM pura-pura | Secrets Manager, key project-scope dengan alert anggaran | wajib di prod |
| `EMAIL_API_KEY` | kosong → backend email console | backend pura-pura | Secrets Manager | wajib di prod |
| `CORS_ORIGINS` | `http://localhost:3091` | tidak ada | `https://careerpilot.id` | bukan `*` di prod |
| `LOG_LEVEL` | DEBUG | INFO | INFO | enum |

**Akses:** hanya role task production bisa baca secret production; developer tidak bisa baca langsung; CI hanya punya nilai test.
**Rotasi (key LLM):** buat key baru → simpan versi baru di Secrets Manager → rolling deploy → verifikasi → revoke key lama; tiap 90 hari dan langsung kalau curiga. Alert anggaran tangkap penyalahgunaan.
**Pembatas:** `.env.*` diabaikan, gitleaks pre-commit + CI job, `safe_summary()` dicatat saat startup.
:::

### 📝 Checklist review mandiri

- [ ] Setiap rahasia punya rumah tiap lingkungan — tidak ada di Git
- [ ] Test tidak perlu key pihak ketiga asli
- [ ] Production tolak menyala dengan rahasia hilang/lemah
- [ ] Rencana rotasi ada

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m2/w6/04-env-and-secrets" ai="no-ai" title="Setelan fail-fast dan pemindai rahasia mini"}
Bagian 1: `load_settings(env)` parse dan validasi variabel lingkungan, lapor **semua** masalah sekaligus tanpa bocor nilai, dan sembunyikan rahasia di `repr` dan ringkasan aman. Bagian 2: pemindai kecil yang temukan AWS key, GitHub token, key privat, penugasan secret hardcoded dan file `.env` yang di-commit — sambil abaikan placeholder dan kode yang baca konfigurasi.
:::

:::hints
- Bangun daftar `errors`; tambah daripada raise; raise sekali di akhir.
- `urllib.parse.urlsplit(url).password` beri kamu password untuk mask.
- Regex blok bangunan: `\bAKIA[0-9A-Z]{16}\b`, `(?i)` untuk case-insensitive, grup bernama `(?P<value>...)`.
- Untuk "bukan function call", cek apa langsung setelah nilai.
- `Path.rglob("*")` + `relative_to(root).parts` untuk lewati folder; tangkap `UnicodeDecodeError` untuk binary.
:::

### 🏆 Tujuan stretch

Pasang gitleaks (`brew install gitleaks`) dan jalankan `gitleaks git -v` di repo RevoShop-mu — ia pindai **seluruh history**. Bandingkan temuan-nya dengan pemindai-mu.

## ✅ Cek cepat

:::quiz
Kenapa `os.getenv("JWT_SECRET_KEY", "dev-secret")` berbahaya?

Kalau variabel hilang di production, aplikasi diam-diam jalan dengan rahasia dikenal publik — siapa saja bisa tanda tangani token asli. Production seharusnya tolak menyala.
:::

:::quiz
Rahasia push ke GitHub. Langkah pertama apa?

Revoke/rotate rahasia langsung. Tulis ulang history datang nanti dan tidak undo exposure.
:::

:::quiz
Apa masuk `.env.example`?

Setiap variabel yang aplikasi butuh, dengan placeholder atau default lokal aman dan komentar — tidak pernah rahasia asli.
:::


## 📚 Lanjut belajar

- [The Twelve-Factor App — Config](https://12factor.net/config)
- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [GitHub Docs — About secret scanning](https://docs.github.com/en/code-security/secret-scanning/introduction/about-secret-scanning)
- [gitleaks](https://github.com/gitleaks/gitleaks)

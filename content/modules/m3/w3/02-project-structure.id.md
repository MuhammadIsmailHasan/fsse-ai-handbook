---
title: "Project Structure for Real Apps"
summary: Kembangkan app FastAPI melewati satu file — router dengan APIRouter, schema vs model, lapisan service, settings dari environment, dan aturan impor yang mencegah circular import.
sourceHash: eb95c1c199a2
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Memecah app FastAPI jadi **router**, **schema**, **service**, **repository** dan **model**
- Memakai **`APIRouter`** dan `include_router` untuk mengelompokkan endpoint
- Membedakan **schema** (bentuk API) dari **model** (tabel database)
- Memuat **settings** dari environment di satu tempat
- Mengikuti **aturan impor** supaya tak pernah kena circular import

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Router** | Kelompok endpoint terkait dalam file sendiri |
| **Schema** | Bentuk data yang masuk atau keluar dari API |
| **Model** | Kelas yang dipetakan ke tabel database |
| **Service** | Aturan bisnis, tanpa HTTP di dalamnya |
| **Repository** | Satu-satunya kode yang bicara ke database |
| **Settings** | Konfigurasi yang dibaca dari environment variable |
| **Circular import** | Modul A butuh B dan B butuh A, sehingga Python gagal |

## 🧠 Ide besarnya

App yang bertumbuh itu seperti **dapur restoran**. Pelayan (router) menerima pesanan dan mengantar piring. Koki (service) menentukan cara memasak. Petugas gudang (repository) satu-satunya yang membuka gudang. Semua punya satu tugas dan hanya bicara dengan orang berikutnya dalam antrean. Pelayan tidak pernah masuk gudang, dan gudang tidak pernah berteriak ke pelanggan.

## ❓ Kenapa ini penting

Satu `main.py` cukup untuk demo. Di 500 baris kamu menggulir lama untuk menemukan apa pun, dua orang mengedit file yang sama dan bentrok, dan kamu tak bisa menguji aturan bisnis tanpa HTTP. Menaruh tiap tugas di tempatnya berarti satu perubahan menyentuh satu file, tiap bagian punya tes sendiri, dan anggota tim baru tahu harus mencari di mana. Kamu sudah melihat lapisan ini di RevoShop (Flask). FastAPI memakai ide yang sama dengan alatnya sendiri: `APIRouter` sebagai ganti Blueprint, dan schema Pydantic di samping model SQLAlchemy.

## 📖 Langkah demi langkah

### 1. Susunan folder

```text
app/
├── main.py            # creates the app, includes the routers
├── core/
│   ├── config.py      # settings from environment variables
│   └── deps.py        # shared dependencies (get_db, get_current_user)
├── routers/           # HTTP only: parse request, call a service, return
│   └── applications.py
├── schemas/           # Pydantic shapes for requests and responses
│   └── applications.py
├── services/          # business rules
│   └── applications.py
├── repositories/      # database queries
│   └── applications.py
├── models/            # SQLAlchemy tables
│   └── application.py
tests/
```

Kamu tak butuh semuanya di hari pertama. Mulai dengan `main.py`, tambah router saat topik kedua muncul, tambah service saat router mulai berisi aturan.

### 2. Router dengan `APIRouter`

Router adalah app mini. Kamu menulis endpoint di dalamnya, lalu memasangnya ke app utama.

```python
# app/routers/applications.py
from fastapi import APIRouter, Depends

from app.core.deps import get_current_user
from app.schemas.applications import ApplicationIn, ApplicationOut
from app.services import applications as service

router = APIRouter(prefix="/applications", tags=["applications"])

@router.post("", response_model=ApplicationOut, status_code=201)
def create_application(body: ApplicationIn, user=Depends(get_current_user)):
    return service.create(user.id, body)
```

```python
# app/main.py
from fastapi import FastAPI
from app.routers import applications

app = FastAPI(title="CareerPilot")
app.include_router(applications.router)
```

`prefix` dan `tags` diatur sekali. `tags` mengelompokkan endpoint di dokumen otomatis. Fungsi route tetap **tipis**: baca request, panggil service, kembalikan hasilnya.

### 3. Schema bukan model

Keduanya mirip, tapi tugasnya berbeda.

| | Schema (Pydantic) | Model (SQLAlchemy) |
|---|---|---|
| Menjelaskan | apa yang diterima dan dikembalikan API | tabel di database |
| Tinggal di | `schemas/` | `models/` |
| Contoh field | `ApplicationIn` tanpa `id` | `Application` punya `id`, `user_id`, `created_at` |
| Bahaya jika dicampur | API membocorkan kolom internal | database dibentuk oleh API |

Pisahkan keduanya. Maka kamu bisa menambah kolom database tanpa mengubah API, dan tak pernah mengembalikan `password_hash` secara tak sengaja.

### 4. Service dan repository

**Service** memegang aturan ("user tak boleh menyimpan pekerjaan yang sama dua kali"). **Repository** memegang query. Service tak pernah membuat SQL, dan repository tak pernah memutuskan aturan.

```python
# app/services/applications.py
def create(user_id: int, body: ApplicationIn):
    if repo.exists(user_id, body.company, body.title):
        raise DuplicateApplication()
    return repo.add(user_id, body)
```

Karena service tak tahu soal HTTP, kamu bisa mengujinya dengan Python biasa, dan job di latar belakang bisa memakainya ulang.

### 5. Settings di satu tempat

Baca environment variable **sekali**, validasi, lalu impor hasilnya. Jangan panggil `os.getenv` di mana-mana.

```python
# app/core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    jwt_secret: str
    access_token_minutes: int = 15

settings = Settings()   # fails at startup if a value is missing
```

`DATABASE_URL` yang hilang menghentikan app saat startup dengan error yang jelas, bukan gagal di request pertama di production. Ini aturan "konfigurasi dari environment" dari pendekatan 12-factor.

### 6. Aturan impor mencegah circular import

Data mengalir satu arah: `routers → services → repositories → models`. Schema, model dan `core` tidak mengimpor apa pun dari lapisan di atasnya. Kalau service mengimpor router, dan router mengimpor service itu, Python memunculkan error saat startup.

Saat tergoda mengimpor "ke atas", pindahkan bagian bersama itu **ke bawah** ke lapisan yang lebih rendah, atau kirim sebagai argumen fungsi. Skrip kecil yang mengecek aturan di CI (latihan di bawah) menjaga struktur tetap rapi saat tim membesar.

### Kapan pakai apa

| Situasi | Lakukan ini |
|---|---|
| Topik baru (users, jobs, applications) | file router baru |
| Fungsi route punya `if` soal aturan bisnis | pindahkan aturan ke service |
| Query yang sama muncul dua kali | taruh di fungsi repository |
| Nilai berasal dari environment | tambahkan ke `Settings` |
| Dua modul saling butuh | pindahkan kode bersama ke lapisan lebih bawah |
| App kecil dengan 3 endpoint | satu file cukup — jangan berlebihan |

## ⚠️ Kesalahan umum

- Menaruh SQL atau aturan bisnis di dalam fungsi route.
- Mengembalikan model SQLAlchemy langsung, sehingga kolom internal sampai ke klien.
- Membaca `os.environ` di banyak file, bukan satu kelas `Settings`.
- Satu "utils.py" yang diimpor semua dan mengimpor semua.
- Memecah jadi sepuluh folder untuk app tiga endpoint.

:::revoshop
Lihat bagaimana RevoShop disusun (blueprint, schema, service, repository). (1) Folder mana di FastAPI yang menjadi tempat tiap blueprint RevoShop? (2) Temukan satu route yang memegang aturan bisnis — fungsi service mana yang akan kamu ekstrak? (3) Di mana RevoShop membaca environment variable-nya, dan apakah di satu tempat?
:::

## 🏆 Praktik terbaik

- [ ] Satu file router per topik, dengan `prefix` dan `tags` diatur sekali.
- [ ] Jaga fungsi route tetap tipis: parse, panggil service, kembalikan.
- [ ] Pisahkan schema Pydantic dan model SQLAlchemy.
- [ ] Muat settings sekali dengan `pydantic-settings` dan gagal cepat saat startup.
- [ ] Impor mengalir satu arah: routers → services → repositories → models.
- [ ] Tambah struktur saat mulai terasa sakit, bukan sebelumnya.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Pakai analogi dapur restoran untuk menjelaskan router, service dan repository. Lalu katakan kenapa router tak boleh bicara langsung ke database.

## 📐 Rancang

Susun folder dan file untuk layanan AI CareerPilot: endpoint `/applications`, `/jobs` dan `/ai/cover-letter`. Katakan apa yang masuk tiap lapisan, di mana settings berada, dan impor mana yang kamu larang.

:::quiz
Tampilkan rancangan yang mungkin

- **`routers/`**: `applications.py`, `jobs.py`, `ai.py`, masing-masing dengan `prefix` dan `tags` sendiri.
- **`schemas/`**: `ApplicationIn/Out`, `JobOut`, `CoverLetterRequest/Response`.
- **`services/`**: `applications.py` (aturan duplikat, kepemilikan), `cover_letters.py` (menyusun prompt, memanggil klien AI).
- **`repositories/`**: `applications.py`, `jobs.py` — semua query.
- **`models/`**: `Application`, `Job`.
- **`core/`**: `config.py` (`Settings`: URL database, secret JWT, API key AI), `deps.py` (`get_db`, `get_current_user`).
- **Dilarang:** service mengimpor router, atau router mengimpor repository. Cek di CI menegakkannya.
- **Klien AI** ada di balik kelas kecil di `services/`, jadi tes bisa menggantinya dengan fake.

**Aturan yang ditunjukkan:** satu tugas per lapisan, satu arah impor, settings di satu tempat.
:::

### 📝 Daftar cek diri

- [ ] Tiap folder punya satu tugas yang jelas
- [ ] Route tipis; aturan ada di service
- [ ] Schema dan model terpisah
- [ ] Settings dimuat sekali dan divalidasi saat startup
- [ ] Tidak ada impor ke atas

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m3/w3/02-layout" ai="no-ai" title="Cek susunan proyek"}
Tulis pengecek kecil yang bisa dijalankan tim di CI. Di `layout_rules.py`, implementasikan `layer_of`, `find_violations` (impor yang melanggar aturan lapisan) dan `find_cycle` (satu jalur circular import, atau `None`). Tes mencakup susunan bersih, router→repository, service→router, impor pihak ketiga, hasil terurut, dan siklus dengan ekor.
:::

:::hints
- `layer_of("app.routers.users")` adalah bagian kedua dari `module.split(".")`.
- Untuk tiap importer, lewati impor yang tak diawali `app.`. Lapisan yang sama dan `core` selalu boleh; `app.main` boleh mengimpor apa saja.
- Bandingkan dengan `ALLOWED[src]`; kembalikan `sorted(found)` supaya hasilnya stabil.
- Untuk siklus, pakai penelusuran depth-first dengan list `visiting`. Kalau menemui node yang sudah ada di `visiting`, potong dari posisinya lalu tambahkan node itu lagi di akhir.
- Node "ekor" seperti `x → a` bukan bagian dari siklus: potong dari tempat siklus dimulai.
:::

## ✅ Cek cepat

:::quiz
Kenapa memisahkan schema Pydantic dan model SQLAlchemy?

Tugasnya berbeda. Schema adalah kontrak dengan klien API; model adalah bentuk tabel database. Kalau keduanya satu kelas, menambah kolom mengubah API-mu, dan field internal seperti `password_hash` bisa bocor ke response. Kelas terpisah membuat masing-masing berubah sendiri.
:::

:::quiz
Apa itu circular import, dan bagaimana memperbaikinya?

Modul A mengimpor B sementara B mengimpor A, sehingga Python tak bisa menyelesaikan pemuatan keduanya. Perbaiki dengan membuat impor mengalir satu arah (routers → services → repositories → models) dan memindahkan kode bersama ke lapisan lebih bawah, atau mengirim bagian yang dibutuhkan sebagai argumen.
:::

## 📚 Lanjut belajar

- [FastAPI: Bigger Applications — Multiple Files](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
- [pydantic-settings: Settings management](https://docs.pydantic.dev/latest/concepts/pydantic_settings/)
- [The Twelve-Factor App: Config](https://12factor.net/config)

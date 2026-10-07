---
title: "Testing with pytest & TestClient"
summary: Uji app FastAPI tanpa menjalankan server — panggil dengan TestClient, ganti database dengan fake baru lewat dependency_overrides, bagi persiapan dengan fixture, dan uji jalur error, bukan hanya jalur sukses.
sourceHash: bb431abafe0f
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Memanggil API dari tes dengan **`TestClient`** — tanpa server
- Mengganti dependency asli dengan yang palsu lewat **`dependency_overrides`**
- Berbagi persiapan antar tes dengan **fixture**
- Menjaga tes tetap **terisolasi** supaya satu tes tak mengubah tes lain
- Menguji **jalur error**, bukan hanya jalur sukses

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **TestClient** | Browser palsu yang memanggil app-mu langsung |
| **Fixture** | Persiapan yang bisa dipakai ulang, diberikan pytest ke tes |
| **Override** | Mengganti dependency asli dengan yang palsu untuk satu tes |
| **Fake** | Pengganti sederhana yang berperilaku seperti aslinya |
| **Isolasi** | Tiap tes mulai dari keadaan bersih |
| **Assertion** | Pengecekan yang harus benar agar tes lulus |
| **Happy path** | Kasus ketika semuanya berjalan benar |

## 🧠 Ide besarnya

Menguji API itu seperti **lintasan latihan di sekolah mengemudi**. Kamu tidak belajar di jalan raya dengan lalu lintas asli. Kamu pakai lintasan tertutup (`TestClient`), dengan kerucut yang bisa ditaruh di mana saja (`dependency_overrides`), dan kerucut direset sebelum tiap pelajaran (isolasi). Mobilnya asli. Jalannya aman.

## ❓ Kenapa ini penting

Tanpa tes, setiap perubahan adalah tebakan. Kamu mengubah satu endpoint dan diam-diam merusak yang lain, lalu tahu dari user. Dengan tes yang cepat, kamu mengubah kode dengan percaya diri. Tes yang berbagi state lebih buruk daripada tanpa tes: satu tes lulus hanya karena tes lain jalan lebih dulu, dan suite gagal secara acak. Tes API yang baik cepat, terisolasi, dan mencakup kegagalan juga, karena di situlah bug sungguhan bersembunyi.

## 📖 Langkah demi langkah

### 1. Panggil app dengan `TestClient`

`TestClient` menjalankan app-mu di proses yang sama. Tanpa port, tanpa `uvicorn`. Rasanya seperti `requests` atau `httpx`.

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
```

Cek **status code** dan **body**. Keduanya bagian dari janji API-mu.

### 2. Uji penulisan dan error

```python
def test_create_note():
    r = client.post("/notes", json={"text": "buy milk"})
    assert r.status_code == 201
    assert r.json()["text"] == "buy milk"

def test_missing_note_is_404():
    assert client.get("/notes/999").status_code == 404

def test_bad_body_is_422():
    assert client.post("/notes", json={}).status_code == 422
```

Tes terakhir hampir gratis: FastAPI memvalidasi body untukmu, kamu hanya memastikannya. Selalu uji minimal satu kegagalan untuk tiap endpoint.

### 3. Ganti database dengan `dependency_overrides`

Endpoint-mu meminta repository lewat `Depends(get_repo)`. Di tes kamu tidak mau yang asli. Gantilah:

```python
def test_with_fake_repo():
    fake = NoteRepo()
    app.dependency_overrides[get_repo] = lambda: fake
    try:
        client = TestClient(app)
        client.post("/notes", json={"text": "a"})
        assert fake.all() == [{"id": 1, "text": "a"}]
    finally:
        app.dependency_overrides.clear()   # always clean up
```

Inilah hasil dari dependency injection minggu lalu: app tidak tahu bahwa ia sedang diuji. `finally` itu penting. `dependency_overrides` bersifat **global** untuk app, jadi override yang tertinggal bocor ke tes berikutnya.

### 4. Taruh persiapan di fixture

Mengulang `try/finally` itu berisik. **Fixture** melakukannya sekali. Kode sebelum `yield` adalah persiapan, kode sesudahnya pembersihan, dan pytest menjalankan pembersihan walau tes gagal.

```python
import pytest

@pytest.fixture
def client():
    fake = NoteRepo()                              # fresh for every test
    app.dependency_overrides[get_repo] = lambda: fake
    yield TestClient(app)
    app.dependency_overrides.clear()

def test_create_note(client):                      # pytest injects it by name
    assert client.post("/notes", json={"text": "a"}).status_code == 201
```

Taruh fixture bersama di `conftest.py` dan pytest menemukannya di setiap file tes di sebelahnya.

### 5. Jaga tes tetap terisolasi

Setiap tes harus jalan **sendirian dan dalam urutan apa pun**. Fake baru per tes memberimu itu. Jebakannya adalah objek bersama yang hidup selama proses (list atau repository di level modul). Kalau tes A menambah catatan dan tes B berharap list kosong, B lulus hanya jika jalan lebih dulu.

Cek cepat: jalankan satu tes sendirian (`pytest -k nama_tes`) dan jalankan suite dalam urutan berbeda. Kalau hasilnya berubah, ada state bersama.

### 6. Uji database asli juga, tapi lebih sedikit

Fake itu cepat, tapi bisa berbeda dari database asli. Pakai keduanya:

| Jenis | Database | Kecepatan | Untuk |
|---|---|---|---|
| Tes unit/API | fake atau SQLite in-memory | sangat cepat | sebagian besar tes, aturan bisnis, jalur error |
| Tes integrasi | PostgreSQL asli (mis. di Docker) | lebih lambat | beberapa tes: query, constraint, transaksi |

Banyak tes di lapisan cepat, sedikit di yang asli. Ini disebut **test pyramid**.

### Kapan pakai apa

| Kebutuhan | Lakukan ini |
|---|---|
| Memanggil endpoint | `TestClient(app)` |
| Mengganti DB atau user yang login | `app.dependency_overrides[dep] = fake` |
| Memakai ulang persiapan | fixture, `yield` untuk pembersihan |
| Tes sama, banyak input | `@pytest.mark.parametrize` |
| Mengecek query atau constraint asli | beberapa tes integrasi di PostgreSQL asli |

## ⚠️ Kesalahan umum

- Lupa membersihkan `dependency_overrides`, sehingga satu tes mengubah tes berikutnya.
- Hanya menguji jalur sukses — tanpa 404, 401 atau 422.
- Repository bersama di level modul yang membuat tes bergantung pada urutan.
- Hanya mengecek status code dan tak pernah body.
- Terlalu banyak mock sampai tes mengecek mock-nya, bukan kodemu.

:::revoshop
Buka folder `tests/` RevoShop. (1) Bagaimana ia mendapatkan test client dan database bersih untuk tiap tes — fixture mana yang melakukannya? (2) Temukan satu tes untuk kasus gagal (401, 403 atau 404). (3) Bagaimana melakukan hal yang sama di FastAPI: apa pengganti test client Flask, dan apa pengganti mengganti konfigurasi database?
:::

## 🏆 Praktik terbaik

- [ ] Beri setiap tes state baru miliknya sendiri (fixture yang membuat fake atau database baru).
- [ ] Selalu bersihkan override, dengan `yield` di fixture atau `try/finally`.
- [ ] Uji kasus gagal: item tak ada, tanpa token, role salah, input buruk.
- [ ] Cek status code dan body response.
- [ ] Jaga sebagian besar tes tetap cepat (fake atau in-memory) dan beberapa di database asli.
- [ ] Beri nama tes seperti kalimat: `test_missing_note_is_404`.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan `TestClient`, `dependency_overrides` dan fixture dengan analogi lintasan sekolah mengemudi. Lalu katakan kenapa override yang tertinggal adalah bug.

## 📐 Rancang

Rencanakan tes untuk endpoint `POST /applications` milik CareerPilot (user menyimpan pekerjaan yang ia lamar). Daftar kasus tesnya, apa yang dicek tiap kasus, dependency mana yang kamu override, dan satu atau dua tes mana yang kamu jalankan di PostgreSQL asli.

:::quiz
Tampilkan rancangan yang mungkin

- **Jalur sukses:** body valid → `201`, body punya `id` dan field yang sama; repo palsu kini berisi satu lamaran.
- **Validasi:** `company` hilang → `422`; `title` kosong → `422`.
- **Auth:** tanpa token → `401`; token user lain tak bisa membaca lamaran ini → `404` atau `403`.
- **Duplikat:** pekerjaan sama disimpan dua kali → `409` (atau aturan pilihanmu).
- **Override:** `get_repo` → fake baru per tes; `get_current_user` → user palsu tetap, jadi sebagian besar tes tak butuh token asli.
- **PostgreSQL asli (integrasi):** satu tes untuk constraint unik dan satu untuk transaksi yang rollback saat error.
- **Isolasi:** semuanya di fixture dengan pembersihan `yield`.

**Aturan yang ditunjukkan:** banyak tes cepat dan terisolasi di fake; sedikit di database asli; selalu jalur gagal.
:::

### 📝 Daftar cek diri

- [ ] Tiap tes membuat state sendiri dan membersihkannya
- [ ] Kasus gagal diuji, bukan hanya sukses
- [ ] Status code dan body sama-sama dicek
- [ ] Hanya sedikit tes yang butuh database asli

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m3/w3/01-testclient" ai="no-ai" title="Test client dengan repository baru"}
`notes_app.py` adalah API catatan yang sudah jadi dan membaca catatan lewat dependency `get_repo` yang dipakai bersama. Tulis `client_with_fresh_repo` di `notes_testing.py`: context manager yang menimpa `get_repo` dengan `NoteRepo()` baru (atau yang kamu berikan), menghasilkan `TestClient`, dan **selalu** menghapus override setelahnya. Tes mengecek isolasi antar tes dan pembersihan, bahkan saat isi tes gagal.
:::

:::hints
- `@contextmanager` mengubah generator jadi blok `with`: kode sebelum `yield` adalah persiapan, sesudahnya pembersihan.
- `app.dependency_overrides[get_repo] = lambda: fake` — lambda mengembalikan `fake` yang sama tiap dipanggil.
- Taruh `yield` di dalam `try:` dan `app.dependency_overrides.clear()` di `finally:` supaya jalan walau tes error.
- Pakai `repo if repo is not None else NoteRepo()`, bukan `repo or NoteRepo()` — repo kosong tetap dianggap diberikan.
:::

## ✅ Cek cepat

:::quiz
Kenapa kamu harus membersihkan `app.dependency_overrides` setelah tes?

`dependency_overrides` milik objek app, yang hidup selama seluruh tes berjalan. Kalau override dibiarkan, tes berikutnya diam-diam ikut memakai fake itu, dan hasilnya bergantung pada urutan tes. Membersihkannya (di pembersihan fixture atau `finally`) menjaga tiap tes terisolasi.
:::

:::quiz
Kenapa menguji jalur sukses saja tidak cukup?

Kebanyakan bug nyata ada di kasus gagal: item tak ada, input buruk, belum login, role salah. Jalur ini juga yang sering tak sengaja diakses user. Satu tes untuk tiap kegagalan (404, 401, 422) membuktikan API menjawab dengan jelas, bukan crash.
:::

## 📚 Lanjut belajar

- [FastAPI: Testing](https://fastapi.tiangolo.com/tutorial/testing/)
- [FastAPI: Testing dependencies with overrides](https://fastapi.tiangolo.com/advanced/testing-dependencies/)
- [pytest: How to use fixtures](https://docs.pytest.org/en/stable/how-to/fixtures.html)

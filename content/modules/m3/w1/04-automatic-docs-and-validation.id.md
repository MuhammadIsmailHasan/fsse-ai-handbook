---
title: "Automatic Docs & Validation"
summary: Dari mana kekuatan gratis FastAPI berasal — skema OpenAPI dan /docs interaktif, response_model untuk membentuk dan menyaring output, status code yang benar, dan HTTPException untuk error bersih, semua dari tipemu.
sourceHash: dfe9c8c8aa7a
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Bagaimana FastAPI menghasilkan **OpenAPI** dan `/docs` interaktif
- Membentuk dan menyaring output dengan **`response_model`**
- Menetapkan **status code** yang benar (seperti `201 Created`)
- Mengembalikan error bersih dengan **`HTTPException`**
- Kenapa docs selalu benar (berasal dari kodemu)

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **OpenAPI** | Deskripsi mesin standar API-mu |
| **Swagger UI** | Halaman `/docs` interaktif |
| **response_model** | Model Pydantic yang membentuk output |
| **Status code** | Angka hasil HTTP (200, 201, 404…) |
| **HTTPException** | Cara FastAPI mengembalikan respons error |
| **Schema** | Bentuk request/response yang dideskripsikan |

## 🧠 Ide besarnya

`response_model` seperti **saringan di pintu keluar**. Handler-mu mungkin memegang objek user lengkap (termasuk hash password), tapi saringan keluar hanya meloloskan field yang kamu deklarasikan aman dikembalikan. Dan `/docs` seperti **menu langsung yang dicetak dapur sendiri** — karena dihasilkan dari kodemu, ia tak pernah bisa menampilkan hidangan yang tak lagi kamu sajikan.

## ❓ Kenapa ini penting

Dua risiko nyata: **membocorkan data** (tak sengaja mengembalikan hash password atau field internal) dan **docs usang** (docs tulisan tangan yang berbohong). FastAPI memperbaiki keduanya dari tipemu: `response_model` menjamin bentuk output dan menyembunyikan selainnya, dan OpenAPI/`/docs` dihasilkan dari kode jadi selalu akurat. Status code yang benar dan error bersih membuat API-mu bisa diprediksi frontend.

## 📖 Langkah demi langkah

### 1. Docs-nya otomatis

Tiap route + model Pydantic memberi makan skema **OpenAPI**, disajikan sebagai **Swagger UI** interaktif di `/docs` (dan ReDoc di `/redoc`). Tanpa setup, selalu sinkron dengan kode.

### 2. response_model membentuk dan menyaring output

Deklarasikan apa yang dikembalikan endpoint; FastAPI memvalidasi dan **menyaring** respons ke persis field itu:

```python
class UserIn(BaseModel):
    name: str
    email: str
    password: str

class UserOut(BaseModel):      # note: no password
    id: int
    name: str
    email: str

@app.post("/users", response_model=UserOut)
def create_user(user: UserIn):
    record = save_user(user)              # record has a password hash
    return record                          # response_model strips it to id/name/email
```

Meski `record` punya field ekstra, klien hanya melihat `UserOut`. Field sensitif tak bisa bocor.

### 3. Status code yang benar

Tetapkan kode yang tepat per aksi:

```python
from fastapi import status

@app.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(user: UserIn): ...
```

`201 Created` untuk pembuatan, `200 OK` untuk baca/update, `204 No Content` untuk delete tanpa body. (Kode REST yang sama dari Modul 2.)

### 4. Error bersih dengan HTTPException

Saat ada yang salah, raise `HTTPException` — FastAPI mengubahnya menjadi respons error yang benar dengan status dan pesanmu:

```python
from fastapi import HTTPException

@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    user = find_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

Klien mendapat `404` dengan `{"detail": "User not found"}` — bisa diprediksi dan terdokumentasi.

### 5. Poles tambahan (opsional)

- `tags=["users"]` mengelompokkan endpoint di `/docs`.
- `summary`/`description` menambah catatan manusia ke docs.
- `response_model_exclude_none=True` menyembunyikan field null.

### Pilih apa yang diekspos

| Kepedulian | Lakukan ini |
|---|---|
| Sembunyikan field sensitif | model `...Out` terpisah lewat `response_model` |
| Sinyalkan jenis sukses | `status_code` yang benar (201/200/204) |
| Laporkan not-found / state buruk | `raise HTTPException(...)` |
| Kelompokkan & jelaskan endpoint | `tags`, `summary` |

- ✅ Pakai model output khusus; jangan pernah kembalikan objek DB mentah.
- ✅ Tetapkan status code akurat dan raise `HTTPException` untuk error.
- 🚫 Jangan pakai ulang model input sebagai output (bisa mengekspos rahasia).

## ⚠️ Kesalahan umum

- Mengembalikan objek ORM/record langsung, membocorkan field internal atau sensitif.
- Memakai ulang satu model untuk input dan output, sehingga `password` menyelinap ke respons.
- Mengembalikan `200` untuk segalanya, bahkan pembuatan dan error.
- Mengembalikan dict error dengan `200` alih-alih raise `HTTPException` dengan kode yang benar.
- Menulis docs terpisah dengan tangan — ia usang; biarkan `/docs` jadi sumber kebenaran.

:::revoshop
RevoShop mengembalikan JSON dari route Flask. (1) Adakah endpoint yang bisa membocorkan field internal (hash password, flag internal)? `response_model`/skema output akan mencegahnya. (2) Pembuatan mana yang harus mengembalikan `201`, dan delete mana `204`? (3) Di mana RevoShop mengembalikan error — apakah `HTTPException` (atau abort flask-smorest) membuat status code dan pesan lebih bersih?
:::

## 🏆 Praktik terbaik

- [ ] Definisikan model input (`...In`) dan output (`...Out`) terpisah; ekspos hanya field aman.
- [ ] Pakai `response_model` supaya respons dibentuk dan disaring otomatis.
- [ ] Tetapkan status code akurat (`201` create, `204` delete, dll.).
- [ ] Raise `HTTPException` untuk kasus error dengan `detail` jelas.
- [ ] Perlakukan `/docs` sebagai kontrak hidup; kelompokkan dengan `tags` dan tambah summary.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan `response_model` dengan analogi saringan-di-pintu-keluar, dan `/docs` dengan analogi menu-langsung-dicetak-dapur. Lalu katakan kenapa ini mencegah kebocoran data dan docs usang.

## 📐 Rancang

Rancang `POST /users` (register) dan `GET /users/{id}` CareerPilot. User tersimpan punya `id, name, email, password_hash, is_admin`. Putuskan model input dan output, status code, dan error untuk user yang hilang — supaya tak ada field sensitif yang bocor.

:::quiz
Tampilkan satu rancangan yang mungkin

```python
class UserIn(BaseModel):
    name: str
    email: str
    password: str

class UserOut(BaseModel):          # no password_hash, no is_admin
    id: int
    name: str
    email: str

@app.post("/users", response_model=UserOut, status_code=201)
def register(user: UserIn):
    record = create_user(user)     # has password_hash, is_admin
    return record                   # filtered to UserOut

@app.get("/users/{user_id}", response_model=UserOut)
def get_user(user_id: int):
    user = find_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user
```

- **Input** `UserIn` menyertakan `password`; **output** `UserOut` mengecualikan `password_hash` dan `is_admin`, jadi keduanya tak bisa bocor meski record menyimpannya.
- **Status:** `201` saat register, `200` saat read.
- **Error:** user hilang → `HTTPException(404)` dengan detail jelas.

**Aturan yang ditunjukkan:** model In/Out terpisah + `response_model` menjamin output aman; status code benar dan `HTTPException` membuat API bisa diprediksi.
:::

### 📝 Checklist review mandiri

- [ ] Model input dan output terpisah; field sensitif dikecualikan dari output
- [ ] `response_model` dipakai di tiap endpoint yang mengembalikan
- [ ] Status code akurat
- [ ] Error lewat `HTTPException` dengan detail jelas

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m3/w1/04-response-model" ai="no-ai" title="Bentuk output dan tangani error"}
Bangun `POST /users` yang mengembalikan `201` dengan `UserOut` (tanpa password) meski record tersimpan berisi password, dan `GET /users/{id}` yang mengembalikan user atau raise `404`. Tes membuktikan password tak pernah muncul di respons dan user yang hilang memberi `404`.
:::

:::hints
- Dua model: `UserIn(name, email, password)` dan `UserOut(id, name, email)`.
- `@app.post("/users", response_model=UserOut, status_code=201)` — kembalikan dict/objek yang juga punya `password`; `response_model` membuangnya.
- Simpan `dict` level modul sebagai store palsu; `GET` raise `HTTPException(status_code=404, detail=...)` saat id tak ada.
:::

## ✅ Cek cepat

:::quiz
Bagaimana `response_model` mencegah kebocoran field sensitif?

FastAPI memvalidasi dan menyaring respons ke persis field yang dideklarasikan di `response_model`, membuang selainnya. Jadi meski handler-mu mengembalikan record lengkap dengan `password_hash`, klien hanya menerima field aman yang kamu daftar — kebocoran mustahil secara konstruksi.
:::

:::quiz
Kenapa `/docs` FastAPI tak pernah usang?

Karena dihasilkan dari route dan model Pydantic aktualmu (skema OpenAPI), bukan ditulis tangan. Kalau kamu mengubah endpoint atau model, docs berubah bersamanya otomatis, jadi ia tak bisa menyimpang dari perilaku nyata.
:::

## 📚 Lanjut belajar

- [FastAPI: response model](https://fastapi.tiangolo.com/tutorial/response-model/)
- [FastAPI: handling errors](https://fastapi.tiangolo.com/tutorial/handling-errors/)
- [FastAPI: metadata & docs URLs](https://fastapi.tiangolo.com/tutorial/metadata/)

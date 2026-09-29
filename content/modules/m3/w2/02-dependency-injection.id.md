---
title: "Dependency Injection"
summary: Sistem Depends FastAPI — deklarasikan apa yang dibutuhkan endpoint (session DB, user saat ini, settings) dan FastAPI membangunnya, menyuntikkannya, dan membersihkannya, menghapus setup berulang dan membuat handler mudah diuji.
sourceHash: a60c9bc7a3fd
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa itu **dependency injection** dan kenapa FastAPI bersandar padanya
- Memakai `Depends(...)` untuk menyediakan setup bersama ke endpoint
- Dependency dengan **`yield`** untuk setup + cleanup (seperti session DB)
- Membangun dependency **`get_current_user`** untuk auth
- Kenapa DI membuat handler kecil, dapat dipakai ulang, dan mudah diuji

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Dependency** | Sesuatu yang dibutuhkan endpoint untuk bekerja |
| **Injection** | Framework menyediakannya untukmu |
| **Depends** | Cara FastAPI mendeklarasikan dependency |
| **yield dependency** | Menjalankan setup, lalu cleanup setelah respons |
| **Reuse** | Satu dependency dipakai banyak endpoint |
| **Override** | Menukar dependency saat tes |

## 🧠 Ide besarnya

Dependency injection seperti **rantai pasok restoran**. Koki (endpoint-mu) tak menyetir ke pasar untuk bahan sebelum tiap hidangan — mereka cukup bilang "saya butuh sayuran segar" dan pemasok mengantarnya, lalu mengambil kembali petinya sesudahnya. Koki fokus memasak. Di FastAPI kamu mendeklarasikan "saya butuh session DB / user saat ini", dan framework membangunnya, menyerahkannya, dan membersihkannya.

## ❓ Kenapa ini penting

Tanpa DI, tiap handler mengulang setup yang sama: buka session DB, baca dan verifikasi token auth, muat settings — dan ingat menutup/membersihkan. Itu berulang, rawan salah, dan sulit diuji. `Depends` FastAPI memusatkan tiap kepedulian dalam satu fungsi, menyuntikkannya di mana pun dideklarasikan, dan (dengan `yield`) menjamin cleanup. Bonus: di tes kamu bisa **override** sebuah dependency untuk menyuntikkan fake, jadi handler diuji terisolasi.

## 📖 Langkah demi langkah

### 1. Dependency sederhana

Dependency hanyalah fungsi yang nilai kembalinya disuntikkan:

```python
from fastapi import Depends

def pagination(page: int = 1, limit: int = 20) -> dict:
    return {"page": page, "limit": limit}

@app.get("/items")
def list_items(pg: dict = Depends(pagination)):
    return pg     # FastAPI called pagination() and injected the result
```

Kini tiap endpoint daftar memakai ulang logika paging yang sama dengan mendeklarasikan `Depends(pagination)`.

### 2. Dependency dengan yield (setup + cleanup)

Untuk sumber daya yang harus dibuka dan ditutup — session database — pakai `yield`:

```python
def get_db():
    db = SessionLocal()
    try:
        yield db            # hand the session to the endpoint
    finally:
        db.close()          # always cleaned up, even on error

@app.get("/users/{id}")
def read_user(id: int, db = Depends(get_db)):
    return db.get(User, id)
```

FastAPI menjalankan kode sampai `yield` sebelum handler, dan kode setelah `yield` begitu respons terkirim — jadi kamu tak pernah membocorkan session.

### 3. Auth sebagai dependency: get_current_user

Penggunaan klasik — ubah token menjadi user saat ini, dan tolak kalau hilang/tak valid:

```python
from fastapi import Header, HTTPException

def get_current_user(authorization: str | None = Header(default=None)):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Not authenticated")
    token = authorization.removeprefix("Bearer ")
    user = verify_token(token)                # decode & look up
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user

@app.get("/me")
def me(user = Depends(get_current_user)):
    return {"id": user.id, "name": user.name}
```

Endpoint terproteksi mana pun cukup menambah `user = Depends(get_current_user)` — pengecekan auth tinggal di satu tempat.

### 4. Dependency bisa bergantung pada dependency

`get_current_user` bisa sendiri `Depends(get_db)`. FastAPI meresolusi seluruh rantai untukmu, berurutan, dan meng-cache hasil dependency dalam satu request.

### 5. Override saat tes

Di tes, ganti dependency asli dengan fake:

```python
app.dependency_overrides[get_current_user] = lambda: FakeUser(id=1)
```

Kini endpoint jalan dengan user fake — tanpa token atau DB asli. Inilah kenapa DI membuat kode sangat mudah diuji.

### Pilih kapan membuat dependency

| Kepedulian berulang | Jadikan dependency? |
|---|---|
| Session DB (buka/tutup) | ✅ ya (`yield`) |
| User terautentikasi saat ini | ✅ ya |
| Paginasi / query param umum | ✅ ya |
| Objek settings / config | ✅ ya |
| Logika sekali-pakai untuk satu endpoint | 🚫 biarkan inline |

- ✅ Ekstrak setup bersama (DB, auth, settings, paging) ke dependency.
- ✅ Pakai `yield` untuk apa pun yang butuh cleanup.
- ✅ Override dependency di tes untuk menyuntikkan fake.
- 🚫 Jangan jadikan logika sepele satu-endpoint dependency hanya demi gaya.

## ⚠️ Kesalahan umum

- Membuka session DB di dalam tiap handler alih-alih dependency `yield` (bocor, duplikasi).
- Mengulang pengecekan auth di tiap endpoint alih-alih satu `get_current_user`.
- Lupa `finally` (atau `try/finally`) sehingga cleanup tak jalan saat error.
- Tak memakai `dependency_overrides`, lalu butuh token/DB asli di tiap tes.
- Menaruh kerja berat di dependency yang jalan tiap request tanpa perlu.

:::revoshop
RevoShop (Flask) memakai decorator/before-request hook untuk auth dan session per request. (1) Setup berulang mana (session DB, user saat ini, cek RBAC) yang akan menjadi dependency FastAPI? (2) Sketsa `get_current_user` untuk RevoShop yang mengembalikan user login atau `401`. (3) Bagaimana `dependency_overrides` membuatmu bisa menguji endpoint terproteksi tanpa JWT asli?
:::

## 🏆 Praktik terbaik

- [ ] Pindahkan session DB, auth, settings, dan paging ke dependency dapat-dipakai-ulang.
- [ ] Pakai `yield` + `finally` untuk sumber daya yang harus dibersihkan.
- [ ] Bangun satu `get_current_user` dan pakai ulang di tiap route terproteksi.
- [ ] Override dependency di tes untuk menyuntikkan fake alih-alih layanan asli.
- [ ] Jaga dependency fokus; biarkan FastAPI meresolusi rantai dependency.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan dependency injection dengan analogi rantai-pasok-restoran. Lalu katakan apa yang dijamin dependency `yield` yang tak dijamin yang biasa.

## 📐 Rancang

Rancang dependency untuk API CareerPilot: session database, user saat ini dari token Bearer, dan penjaga "admin saja" untuk endpoint admin. Tunjukkan bagaimana endpoint biasa dan endpoint admin masing-masing mendeklarasikan yang dibutuhkan, dan bagaimana kamu menguji endpoint admin tanpa token asli.

:::quiz
Tampilkan satu rancangan yang mungkin

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_current_user(db = Depends(get_db), authorization: str | None = Header(default=None)):
    user = user_from_token(db, authorization)
    if user is None:
        raise HTTPException(401, "Not authenticated")
    return user

def require_admin(user = Depends(get_current_user)):
    if not user.is_admin:
        raise HTTPException(403, "Admin only")
    return user

@app.get("/me")
def me(user = Depends(get_current_user)):
    return {"id": user.id}

@app.get("/admin/stats")
def stats(admin = Depends(require_admin), db = Depends(get_db)):
    return compute_stats(db)
```

- `get_db` (yield) membuka/menutup session; `get_current_user` bergantung padanya dan header; `require_admin` dibangun di atas `get_current_user` dan menambah cek peran (`403` kalau bukan admin).
- **Menguji route admin:** `app.dependency_overrides[require_admin] = lambda: FakeAdmin()` — endpoint jalan dengan admin fake, tanpa token atau DB asli.

**Aturan yang ditunjukkan:** susun berlapis dependency (db → user saat ini → penjaga admin), deklarasikan hanya yang dibutuhkan tiap endpoint, dan override di tes untuk isolasi.
:::

### 📝 Checklist review mandiri

- [ ] Session DB adalah dependency `yield` dengan cleanup
- [ ] Cek auth dan peran adalah dependency, bukan kode berulang
- [ ] Endpoint mendeklarasikan hanya yang dibutuhkan
- [ ] Tes override dependency untuk menyuntikkan fake

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m3/w2/02-depends" ai="no-ai" title="Auth dan DB lewat Depends"}
Bangun dependency `get_current_user` yang membaca token `Bearer` dari header `Authorization` (menolak yang hilang/tak valid dengan `401`) dan `GET /me` terproteksi yang mengembalikan user. Tes mengenai `/me` tanpa token (`401`), token buruk (`401`), token baik (`200`), dan juga memakai `dependency_overrides` untuk menyuntikkan user fake.
:::

:::hints
- Peta token→user kecil, mis. `{"tok-ismail": {"id": 1, "name": "Ismail"}}`.
- `get_current_user(authorization: str | None = Header(default=None))`: wajibkan mulai dengan `"Bearer "`, cari tokennya, raise `HTTPException(401, ...)` kalau hilang/tak dikenal.
- `@app.get("/me")` dengan `user = Depends(get_current_user)` mengembalikan dict user.
- Satu tes menetapkan `app.dependency_overrides[get_current_user] = lambda: {"id": 99, "name": "Fake"}` lalu memanggil `/me`.
:::

## ✅ Cek cepat

:::quiz
Apa yang diberikan dependency `yield` yang tak diberikan dependency biasa (return)?

Cleanup terjamin: kode sebelum `yield` jalan sebagai setup, nilainya disuntikkan, dan kode setelah `yield` (dalam `finally`) jalan begitu respons terkirim — bahkan kalau handler error. Begitulah session DB dibuka dengan andal dan selalu ditutup.
:::

:::quiz
Kenapa dependency injection membuat endpoint mudah diuji?

Karena endpoint tak membangun session DB atau user-nya sendiri — ia mendeklarasikannya lewat `Depends`, jadi di tes kamu bisa `dependency_overrides` dengan fake. Handler jalan terisolasi tanpa database, token, atau jaringan asli.
:::

## 📚 Lanjut belajar

- [FastAPI: dependencies](https://fastapi.tiangolo.com/tutorial/dependencies/)
- [FastAPI: dependencies with yield](https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/)
- [FastAPI: testing with dependency overrides](https://fastapi.tiangolo.com/advanced/testing-dependencies/)

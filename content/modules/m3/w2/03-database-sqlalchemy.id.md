---
title: "Database with SQLAlchemy 2.0"
summary: Menyambungkan FastAPI ke database dengan cara modern — model berjenis SQLAlchemy 2.0, gaya query select(), Session sebagai unit of work, dan menyambungkan semuanya lewat dependency get_db (dengan catatan tentang SQLModel).
sourceHash: e499261d9bfb
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Mendefinisikan tabel sebagai **model berjenis** di SQLAlchemy 2.0
- Gaya query **`select()`** modern (bukan API `Query` lama)
- **`Session`** sebagai unit of work: add, commit, refresh
- Menyambungkan DB ke FastAPI lewat dependency **`get_db`**
- Apa itu **SQLModel** dan kapan berguna

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **ORM** | Memetakan objek Python ke baris database |
| **Model** | Kelas yang memetakan ke sebuah tabel |
| **Session** | Unit of work yang membundel perubahan DB |
| **select()** | Cara 2.0 membangun query |
| **scalars** | Ambil objek model dari sebuah hasil |
| **commit** | Menyimpan perubahan session |
| **SQLModel** | Gabungan Pydantic + SQLAlchemy |

## 🧠 Ide besarnya

ORM seperti **penerjemah antara dua bahasa**: kodemu berbahasa objek Python, database berbahasa baris dan SQL. SQLAlchemy menerjemahkan dua arah supaya kamu bekerja dengan objek `User` alih-alih menulis SQL mentah dengan tangan. **Session** seperti **notes penerjemah**: kamu mencatat perubahan (tambah user ini, update yang itu) dan, saat `commit`, ia mengirim semuanya ke database dalam satu transaksi.

## ❓ Kenapa ini penting

Kamu memakai SQLAlchemy dengan Flask di Modul 2. FastAPI memakai SQLAlchemy yang *sama*, tapi **gaya 2.0** modern lebih berjenis dan eksplisit (API `select()`), dan kamu menyambungkan session lewat **dependency** alih-alih `db` global Flask. Membuat pola ini benar memberimu akses data yang bersih, dapat diuji, dengan autocomplete dan pengecekan tipe — dan ini persis setup yang dipakai proyek FastAPI nyata.

## 📖 Langkah demi langkah

### 1. Model berjenis (gaya 2.0)

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    email: Mapped[str] = mapped_column(unique=True)
```

`Mapped[int]` / `mapped_column(...)` memberi kolom berjenis — editor-mu tahu `user.email` adalah `str`.

### 2. Engine dan Session

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

engine = create_engine("postgresql+psycopg://...")   # or sqlite:///./app.db
SessionLocal = sessionmaker(bind=engine)
```

**engine** mengelola connection pool; **`SessionLocal()`** membuat session (unit of work) per request.

### 3. Query dengan select()

Gaya 2.0 membangun statement dan mengeksekusinya:

```python
from sqlalchemy import select

# one by primary key
user = session.get(User, 7)

# a query
stmt = select(User).where(User.email == "i@x.com")
user = session.scalars(stmt).first()

# a list
users = session.scalars(select(User).order_by(User.name)).all()
```

`scalars(...)` mengembalikan objek model (bukan baris). Ini menggantikan API `session.query(User)` lama.

### 4. Menulis: add, commit, refresh

```python
user = User(name="Ismail", email="i@x.com")
session.add(user)
session.commit()          # sends the INSERT in a transaction
session.refresh(user)     # loads DB-generated fields (like id)
```

Semua di antara commit adalah satu transaksi — semua-atau-tidak, persis seperti di Modul 2.

### 5. Sambungkan ke FastAPI dengan get_db

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/users", response_model=UserOut, status_code=201)
def create_user(body: UserIn, db: Session = Depends(get_db)):
    user = User(name=body.name, email=body.email)
    db.add(user); db.commit(); db.refresh(user)
    return user
```

Dependency `yield` (pelajaran lalu) memberi tiap request session segar yang selalu ditutup.

### 6. SQLModel (opsional)

**SQLModel** (oleh pembuat FastAPI) menggabungkan Pydantic dan SQLAlchemy: satu kelas adalah *sekaligus* model tabelmu *dan* skema API-mu. Nyaman untuk aplikasi kecil, tapi untuk kasus kompleks banyak tim menjaga model SQLAlchemy dan skema Pydantic terpisah demi kejelasan. Ketahui ia ada; keduanya cukup baik.

### Pilih setup data-mu

| Situasi | Lakukan ini |
|---|---|
| Query lewat primary key | `session.get(Model, id)` |
| Query filter/sort | `select(Model).where(...).order_by(...)` + `scalars` |
| Session per-request | dependency yield `get_db` |
| Aplikasi kecil, ingin sedikit boilerplate | pertimbangkan SQLModel |
| Domain kompleks / lapisan jelas | model SQLAlchemy + skema Pydantic terpisah |

- ✅ Pakai gaya `select()` 2.0 dan kolom `Mapped` berjenis.
- ✅ Satu session per request lewat dependency `get_db`; commit di handler/service.
- 🚫 Jangan bagi satu session global antar request; jangan pakai API `Query` lama.

## ⚠️ Kesalahan umum

- Memakai API `session.query(...)` lama alih-alih `select()` (gaya 2.0).
- Membagi satu session antar request (menyebabkan bug threading dan data basi).
- Lupa `commit()`, sehingga perubahan diam-diam hilang.
- Tak menutup session (diperbaiki oleh dependency yield `get_db`).
- Mengembalikan objek ORM langsung tanpa `response_model`, membocorkan kolom.

:::revoshop
RevoShop memakai Flask-SQLAlchemy (pembungkus Flask). (1) Modelnya memetakan ke tabel yang sama — tulis ulang satu model dalam SQLAlchemy 2.0 polos (`Mapped`, `mapped_column`). (2) Konversi satu panggilan `Model.query.filter_by(...)` ke gaya `select(...).where(...)`. (3) Di FastAPI kamu akan mengganti `db.session` global Flask dengan dependency `get_db` — di mana itu mengubah kode route RevoShop?
:::

## 🏆 Praktik terbaik

- [ ] Definisikan model berjenis dengan `Mapped`/`mapped_column`; pakai `select()` untuk query.
- [ ] Beri tiap request session-nya sendiri lewat dependency yield `get_db`.
- [ ] Commit dengan sengaja; refresh untuk memuat field yang dihasilkan seperti id.
- [ ] Jaga transaksi jelas — satu use case adalah satu commit (seperti di Modul 2).
- [ ] Kembalikan lewat `response_model`, bukan objek ORM mentah.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ORM dengan analogi penerjemah dan Session dengan analogi notes. Lalu tunjukkan, satu baris masing-masing, cara mengambil user lewat id dan cara mengambil lewat email di SQLAlchemy 2.0.

## 📐 Rancang

Rancang lapisan data untuk model `Application` CareerPilot dan endpoint-nya: model berjenis (`id, user_id, company, role, status`), dependency `get_db`, endpoint create, dan endpoint "daftar lamaranku difilter status" memakai `select()`. Catat di mana batas transaksinya.

:::quiz
Tampilkan satu rancangan yang mungkin

```python
class Application(Base):
    __tablename__ = "applications"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(index=True)
    company: Mapped[str]
    role: Mapped[str]
    status: Mapped[str] = mapped_column(default="saved")

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

@app.post("/users/{user_id}/applications", response_model=ApplicationOut, status_code=201)
def create(user_id: int, body: ApplicationIn, db: Session = Depends(get_db)):
    app_row = Application(user_id=user_id, company=body.company, role=body.role, status=body.status)
    db.add(app_row); db.commit(); db.refresh(app_row)   # ← one transaction
    return app_row

@app.get("/users/{user_id}/applications", response_model=list[ApplicationOut])
def list_apps(user_id: int, status: str | None = None, db: Session = Depends(get_db)):
    stmt = select(Application).where(Application.user_id == user_id)
    if status:
        stmt = stmt.where(Application.status == status)
    return db.scalars(stmt.order_by(Application.id)).all()
```

- Model berjenis dengan index di `user_id` (kolom filter, sesuai indexing Stage F).
- `get_db` memberi session per-request; **batas transaksi** adalah `add`+`commit` pada create.
- List memakai `select().where()` dan membangun filter secara kondisional.

**Aturan yang ditunjukkan:** model berjenis 2.0 + `select()`, satu session per request lewat `get_db`, dan transaksi satu-commit yang jelas per tulis.
:::

### 📝 Checklist review mandiri

- [ ] Model memakai `Mapped`/`mapped_column`; kolom filter panas ter-index
- [ ] Dependency yield `get_db` untuk session
- [ ] Query memakai `select()` + `scalars`
- [ ] Batas transaksi (satu commit per use case) jelas

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m3/w2/03-sqlalchemy" ai="no-ai" title="CRUD SQLAlchemy 2.0 (SQLite)"}
Memakai SQLAlchemy 2.0 terhadap database SQLite dalam-memori (tanpa server), definisikan model `User` dan implementasikan `create_user`, `get_user`, dan `list_users_by_domain` (email berakhir dengan sebuah domain) memakai `session.add/commit`, `session.get`, dan `select().where()`. Tes membuat session, memasukkan user, dan memeriksa query.
:::

:::hints
- `Base(DeclarativeBase)`, `User` dengan `id` (pk), `name`, `email`.
- `create_user(session, name, email)`: bangun, `add`, `commit`, `refresh`, kembalikan.
- `get_user(session, user_id)`: `session.get(User, user_id)`.
- `list_users_by_domain(session, domain)`: `select(User).where(User.email.endswith(domain))` lalu `scalars(...).all()`.
:::

## ✅ Cek cepat

:::quiz
Di SQLAlchemy 2.0, bagaimana mengambil satu baris lewat primary key vs menjalankan query terfilter?

Lewat primary key: `session.get(Model, id)`. Untuk query terfilter, bangun statement dengan `select(Model).where(...)` dan eksekusi dengan `session.scalars(stmt).first()` (satu) atau `.all()` (banyak). Gaya 2.0 mengutamakan `select()` daripada `session.query(...)` lama.
:::

:::quiz
Kenapa memberi tiap request Session-nya sendiri lewat `get_db` alih-alih satu session global?

Session adalah objek per-unit-kerja dan tak aman dibagi antar request bersamaan — yang global menyebabkan masalah threading dan data basi. Dependency yield `get_db` membuat session segar per request dan selalu menutupnya, menjaga transaksi terisolasi dan bersih.
:::

## 📚 Lanjut belajar

- [SQLAlchemy 2.0: ORM quickstart](https://docs.sqlalchemy.org/en/20/orm/quickstart.html)
- [FastAPI: SQL databases](https://fastapi.tiangolo.com/tutorial/sql-databases/)
- [SQLModel documentation](https://sqlmodel.tiangolo.com/)

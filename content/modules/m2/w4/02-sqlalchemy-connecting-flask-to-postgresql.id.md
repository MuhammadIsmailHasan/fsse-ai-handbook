---
title: "SQLAlchemy: Menghubungkan Flask ke PostgreSQL"
summary: Cara ORM berbicara ke database — engine, connection pool, session dan transaksi, kueri select() SQLAlchemy 2.0, dan cara memasangnya ke aplikasi Flask dengan aman.
sourceHash: a765c432d42f
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa itu **ORM**, dan apa yang bisa dan tidak bisa disembunyikan ORM
- Lapisan SQLAlchemy: **engine**, **connection pool**, **session**
- **Unit of work**: `add`, `flush`, `commit`, `rollback`
- Kueri gaya SQLAlchemy **2.0** menggunakan `select()`, `scalars()`, `get()`
- Memasang **Flask-SQLAlchemy** ke application factory
- Lifetime session per request, dan melihat SQL yang dijalankan

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **ORM** | Penerjemah antara objek Python dan tabel database |
| **Engine** | Objek yang tahu cara berbicara ke database-mu |
| **Connection pool** | Sekumpulan koneksi siap pakai, bukan membuat baru tiap kali |
| **Session** | Ruang kerja untuk satu request: melacak perubahan dan menyimpannya bersama |
| **Unit of work** | Pola: kumpulkan perubahan, lalu simpan sekaligus sebagai satu transaksi |
| **`flush` vs `commit`** | Kirim SQL sekarang tapi tetap dalam transaksi / selesaikan transaksi |
| **`rollback`** | Batalkan semua perubahan dalam transaksi session ini |
| **`select()`** | Cara modern SQLAlchemy untuk menulis kueri |
| **N+1 query** | Satu kueri per baris dalam loop, bukan satu kueri untuk semuanya |

## 🧠 Ide besarnya

Bayangkan ORM seperti **penerjemah di pertemuan bisnis**: kamu berbicara Python (objek, daftar), database berbicara SQL (tabel, baris), dan ORM mengartikan keduanya bolak-balik. Kamu bilang "simpan objek `Application` ini", ORM menulis `INSERT`. Kamu tanya "ambil aplikasi user 7", ORM menulis `SELECT` dan kasih objek.

Penerjemah membuat percakapan mudah — tapi kamu tetap harus tahu apa yang dibicarakan. Developer ORM yang baik **membaca SQL** yang dibuatnya.

## ❓ Kenapa ini penting

Menulis SQL mentah untuk semuanya berarti: kode pemetaan berulang (baris → dict → objek), mengelola parameter dengan tangan, dan string SQL di mana-mana. ORM memberi kamu kelas Python untuk tabel (lesson 03), kueri yang bisa dibangun bertahap, **session** yang melacak perubahan dan commit sekali dalam satu transaksi, dan kode yang paling portabel.

Bahayanya: percaya ORM adalah keajaiban:

- Koneksi baru dibuka di **setiap request** tanpa pool → database mentok kehabisan koneksi saat banyak request.
- Lupa `commit()` → "terselamatkan di test tapi tidak di database".
- Exception di tengah request membuat session rusak → setiap request nanti gagal sampai restart.
- Loop yang diam-diam menjalankan ratusan kueri (N+1 problem, lesson 05).

## 📖 Langkah demi langkah

### 1. Lapisannya

```mermaid
flowchart LR
    Code[Kode kamu<br/>model & kueri] --> Session[Session<br/>unit of work, lacak objek]
    Session --> Engine[Engine<br/>dialect + pool koneksi]
    Engine --> Pool[(Pool koneksi<br/>database terbuka)]
    Pool --> PG[(PostgreSQL)]
```

| Lapisan | Tugasnya |
|---|---|
| **Engine** | tahu *cara* berbicara ke PostgreSQL (dialect + driver) dan mengelola **pool** koneksi |
| **Connection pool** | pakai kembali beberapa koneksi terbuka, bukan buka baru per kueri (buka itu lambat) |
| **Session** | ruang kerja kamu: muat objek, lacak perubahan, kirim dalam satu transaksi |

### 2. URL database

```text
postgresql+psycopg://careerpilot:secret@localhost:5491/careerpilot
└─ dialect ─┘└driver┘
```

`+psycopg` memilih driver psycopg 3 yang kamu pakai di Week 2. URL datang dari `DATABASE_URL`, bukan dari kode.

### 3. SQLAlchemy inti (tanpa Flask)

```python
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import Session

engine = create_engine(DATABASE_URL, pool_pre_ping=True)   # create ONCE per process

with Session(engine) as session:                            # short-lived
    total = session.scalar(text("SELECT count(*) FROM applications"))
```

`pool_pre_ping=True` cek apakah koneksi pool masih hidup sebelum dipakai (database dan proxy bisa putus koneksi idle).

### 4. Unit of work

Bayangkan troli belanja: `add` masukkan barang, `flush` tampilkan ke kasir, `commit` bayar. Sampai bayar, belum final — dan `rollback` kosongkan troli.

```python
with Session(engine) as session:
    company = Company(name="Kopi Data")
    session.add(company)          # pending: nothing sent yet
    session.flush()               # sends INSERT, company.id is now set — still inside the transaction
    session.add(Application(company_id=company.id, role_title="Analyst"))
    session.commit()              # COMMIT: both rows saved together
```

| Method | Yang terjadi |
|---|---|
| `add(obj)` | mulai lacak objek baru |
| `flush()` | kirim SQL pending ke database **dalam** transaksi sekarang |
| `commit()` | flush + COMMIT |
| `rollback()` | buang semuanya sejak commit terakhir |
| `close()` | kembalikan koneksi ke pool |

Kalau error: `rollback()`. Blok `with Session(...)` tutup session untuk kamu.

### 5. Kueri SQLAlchemy 2.0

```python
from sqlalchemy import select, func

# one object by primary key
application = session.get(Application, 42)            # None if missing

# many objects
stmt = (
    select(Application)
    .where(Application.user_id == user_id, Application.status == "interview")
    .order_by(Application.created_at.desc())
    .limit(20)
)
applications = session.scalars(stmt).all()

# one or none
company = session.scalars(select(Company).where(Company.name == "Kopi Data")).one_or_none()

# aggregates
counts = session.execute(
    select(Application.status, func.count()).where(Application.user_id == user_id).group_by(Application.status)
).all()                                               # list of (status, count) rows
```

- `scalars(...)` kembalikan kolom pertama setiap baris — sempurna saat pilih seluruh objek.
- `execute(...)` kembalikan baris dengan beberapa kolom.
- Nilai seperti `user_id` dikirim sebagai **bound parameter** — aman dari SQL injection.

:::note[Gaya lama yang kamu lihat di kode yang ada]
`Application.query.filter_by(user_id=7).all()` adalah legacy Flask-SQLAlchemy query API. Masih jalan, tapi kode baru dan docs pakai `db.session.scalars(select(...))`.
:::

### 6. Flask-SQLAlchemy di factory

```python
# extensions.py
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)          # created WITHOUT an app

# __init__.py
def create_app(config_object=DevelopmentConfig):
    app = Flask(__name__)
    app.config.from_object(config_object)   # includes SQLALCHEMY_DATABASE_URI
    db.init_app(app)                         # attach to THIS app
    ...
    return app
```

Flask-SQLAlchemy kasih `db.session`, **scoped session per request/app context**, dan **hapus di akhir setiap request** — jadi setiap request mulai bersih.

### 7. Session per request

```python
@applications_bp.post("")
def create_application():
    data = parse(request.get_json())
    application = Application(**data, user_id=current_user_id())
    db.session.add(application)
    db.session.commit()
    return {"data": serialize(application)}, 201
```

Kalau ada yang raise sebelum `commit()`, tidak ada yang tersimpan. Di service yang bikin beberapa langkah, commit **sekali** di akhir unit of work (lesson 06).

### 8. Lihat SQL-nya

Hidupin ini saat belajar. Setiap kejutan di ORM jadi jelas begitu kamu lihat kueri yang benar-benar dikirimnya.

```python
app.config["SQLALCHEMY_ECHO"] = True        # logs every SQL statement (development only!)
print(select(Application).where(Application.user_id == 7))   # shows the SQL of a statement
```

### 9. Pengaturan pool (preview production)

| Pengaturan | Artinya |
|---|---|
| `pool_size` | koneksi yang terbuka per proses (default 5) |
| `max_overflow` | koneksi sementara ekstra saat beban tinggi |
| `pool_pre_ping` | tes koneksi sebelum pakai |
| `pool_recycle` | buka ulang koneksi yang lebih tua dari N detik |

Gunicorn dengan 4 worker × (5 + 10 overflow) bisa buka sampai **60** koneksi — cek itu pas dengan `max_connections` database-mu (Week 6 / Module 5).

### Pilih setupmu

Setiap pilihan di sini ada trade-off:

| Pilihan | ✅ | ❌ |
|---|---|---|
| ORM | lebih sedikit boilerplate, objek, parameter aman, integrasi migrasi | kueri tersembunyi, kurva belajar, bisa bikin SQL tidak efisien |
| Raw SQL (psycopg) | kontrol penuh, mudah optimalkan | pemetaan manual, berulang, SQL di mana-mana |
| SQLAlchemy Core (`select`, table, bukan objek) | seperti SQL, composable | kurang nyaman dari objek |
| Hybrid: ORM + raw SQL untuk laporan susah | terbaik dari kedua dunia | dua gaya dalam satu codebase |
| Session lama | lebih sedikit objek yang dibuat | data lama, pertumbuhan memori, lock |

- ✅ ORM untuk CRUD dan logika bisnis biasa.
- ✅ `text()` atau Core untuk laporan kompleks, bulk operation, atau fitur khusus database.
- 🚫 Jangan buat engine per request.
- 🚫 Jangan bagikan satu session di thread atau taro session terbuka berminit-minit.

## ⚠️ Kesalahan umum

- Lupa commit.
- Tangkap exception tapi tidak rollback → `PendingRollbackError` di kueri nanti.
- Akses atribut objek sesudah session tutup (`DetachedInstanceError`).
- Biarkan `SQLALCHEMY_ECHO=True` di production (berisik, bisa log data sensitif).
- Campur legacy `.query` dan 2.0 `select()` gaya secara acak.

:::revoshop
`app/extensions.py` milik RevoShop bikin `db = SQLAlchemy()` tanpa app, dan `create_app()` panggil `db.init_app(flask_app)`. `config/base.py` baca `SQLALCHEMY_DATABASE_URI` dari `DATABASE_URL`, dan `config/development.py` atur `SQLALCHEMY_ECHO = True`. Buka satu repository (misalnya `app/repositories/product_repository.py`): apakah pakai legacy `Model.query` API atau gaya 2.0 `select()`? Di mana `commit()` dipanggil — di repository, service, atau route? Apakah ada path di mana exception sesudah `add()` bisa tinggalkan half-done unit of work yang commit?
:::

## 🏆 Praktik terbaik

- [ ] **Satu engine per proses** (Flask-SQLAlchemy tangani); URL koneksi dari `DATABASE_URL`.
- [ ] Pakai **session singkat umurnya** — satu per request atau unit of work.
- [ ] Commit **sekali per unit of work**; rollback saat error (Flask-SQLAlchemy bersihkan di akhir request).
- [ ] Pakai **gaya SQLAlchemy 2.0** (`select()`, `scalars()`, `session.get()`) di kode baru.
- [ ] Hidupin `SQLALCHEMY_ECHO` lokal dan **baca SQL-nya** untuk endpoint penting.
- [ ] Set `pool_pre_ping=True` (lewat `SQLALCHEMY_ENGINE_OPTIONS`) dan sizing pool sesuai limit koneksi database.
- [ ] Jangan bangun SQL dengan string formatting; pakai bound parameter (ekspresi ORM atau `text(":param")`).
- [ ] Jauhkan akses database dari fungsi route — pakai repository/service (lesson 06).

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan connection pool ke orang yang bukan programmer pakai analogi taxi yang mengantre di bandara versus panggil taxi baru untuk setiap penumpang. Lalu jelaskan `flush` vs `commit` dalam satu kalimat masing-masing.

## 📐 Rancang

Untuk CareerPilot, tulis statement SQLAlchemy 2.0 (Python, bukan SQL) untuk:
1. Ambil application 42 hanya kalau punya user 7
2. Daftar application user 7 dengan status `interview`/`offer`, terbaru duluan, halaman 2 (20 per halaman), plus total count
3. Hitung application per status untuk user 7
4. Buat company kalau tidak ada company dengan nama itu (case-insensitive), lalu buat application — dalam **satu** transaksi

:::quiz
Lihat kode yang mungkin

```python
# 1
application = db.session.scalars(
    select(Application).where(Application.id == 42, Application.user_id == 7)
).one_or_none()

# 2
base = select(Application).where(Application.user_id == 7, Application.status.in_(["interview", "offer"]))
items = db.session.scalars(base.order_by(Application.created_at.desc(), Application.id.desc()).limit(20).offset(20)).all()
total = db.session.scalar(select(func.count()).select_from(base.subquery()))

# 3
rows = db.session.execute(
    select(Application.status, func.count()).where(Application.user_id == 7).group_by(Application.status)
).all()

# 4
company = db.session.scalars(select(Company).where(func.lower(Company.name) == name.lower())).one_or_none()
if company is None:
    company = Company(name=name)
    db.session.add(company)
    db.session.flush()                      # get company.id without committing
db.session.add(Application(user_id=7, company_id=company.id, role_title=role))
db.session.commit()                         # both inserts, one transaction
```

Untuk #4 di bawah concurrency, jaga juga unique index pada `lower(name)` dan tangani `IntegrityError` (dua request bisa buat company yang sama di saat bersamaan).
:::

### 📝 Checklist review mandiri

- [ ] Filter ownership di #1
- [ ] Urutan stabil dan count terpisah di #2
- [ ] `flush` sebelum pakai id yang dibuat; satu `commit` di #4
- [ ] Saya pertimbangkan race di #4

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m2/w4/02-sqlalchemy" ai="no-ai" title="Kueri dan unit of work dengan SQLAlchemy 2.0"}
`models.py` (disediakan) mendefinisikan `Company` dan `Application` dengan Flask-SQLAlchemy. Implementasi fungsi di `repository.py` pakai kueri gaya **2.0** melawan PostgreSQL sungguhan: get-for-user, listing berhalaman dengan total, count per status, dan `create_application_with_company` yang buat kedua baris dalam **satu** transaksi dan rollback bersih saat gagal. Test juga hitung berapa banyak SQL statement fungsi-mu jalankan.
:::

:::hints
- `db.session.scalars(select(Model).where(...)).one_or_none()`
- Total count: `select(func.count()).select_from(stmt.subquery())`
- Pakai `flush()` dapat `company.id`, lalu `commit()` sekali.
- Saat `IntegrityError`, panggil `db.session.rollback()` sebelum re-raise error kamu sendiri.
:::

### 🏆 Stretch goal

Hidupin `SQLALCHEMY_ECHO` di test app dan baca SQL yang dibuat untuk `list_applications`. Apakah count query-nya efisien?

## ✅ Cek cepat

:::quiz
Apa bedanya engine dan session?

Engine dibuat sekali per proses dan mengelola cara koneksi (dialect, driver, connection pool). Session singkat umurnya: lacak objek dan jalankan unit of work dalam transaksi.
:::

:::quiz
Kenapa panggil `flush()` sebelum `commit()` kadang?

Untuk kirim insert pending sehingga database buat nilai (seperti primary key) yang kamu butuh untuk langkah nanti — tapi tetap dalam transaksi yang sama yang belum di-commit.
:::

:::quiz
Apa yang harus kamu lakukan sesudah tangkap error database di dalam session?

Panggil `session.rollback()`; kalau tidak, session tetap dalam status transaksi gagal dan kueri nanti gagal.
:::


## 📚 Lanjut belajar

- [SQLAlchemy 2.0 Unified Tutorial](https://docs.sqlalchemy.org/en/20/tutorial/)
- [SQLAlchemy: Session basics](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)
- [Flask-SQLAlchemy: Quick start](https://flask-sqlalchemy.readthedocs.io/en/stable/quickstart/)

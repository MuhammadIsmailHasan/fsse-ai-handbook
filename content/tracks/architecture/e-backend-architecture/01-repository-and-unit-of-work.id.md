---
title: "Repository & Unit of Work"
summary: Pisahkan logika bisnis dari penyimpanan data — repository sebagai antarmuka koleksi, unit of work sebagai batas transaksi, fake yang tepercaya lewat contract test, dan kapan session ORM sudah cukup.
sourceHash: 2b37cd476182
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Pola **Repository**: antarmuka mirip koleksi untuk mengakses penyimpanan
- Pola **Unit of Work**: satu aksi bisnis = satu transaksi atomik
- Pemetaan antara **objek domain** dan baris database
- Implementasi fake dan **contract test** yang menjaga fake tetap jujur
- Bagaimana `Session` SQLAlchemy sudah mengimplementasikan kedua pola — dan kapan menambah layer sendiri sebanding
- Lanjutan dari Modul 2 Minggu 4 (arsitektur berlapis) dan Minggu 2 (transaksi)

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Repository** | Objek yang menyimpan dan mengambil data, menyembunyikan SQL |
| **Unit of Work** | Satu aksi bisnis = satu transaksi, disimpan sekaligus |
| **Objek domain** | Objek biasa dengan aturan bisnis, tidak terikat tabel |
| **Pemetaan** | Mengubah baris database menjadi objek dan sebaliknya |
| **Fake** | Pengganti sederhana dalam memori yang dipakai di tes |
| **Contract test** | Satu suite tes dijalankan di implementasi asli dan fake |
| **Batas transaksi** | Di mana "semua atau tidak sama sekali" dimulai dan berakhir |
| **Session (SQLAlchemy)** | Unit of work bawaan SQLAlchemy |

## 🧠 Ide besarnya

**Repository** seperti **pustakawan**: kamu minta "kasih buku nomor 42" atau "simpan buku ini", dan kamu tidak peduli apakah buku itu di rak, di gudang, atau di arsip digital.

**Unit of Work** seperti **keranjang belanja saat bayar**: kamu masukkan beberapa barang, dan pembayaran terjadi **sekaligus** — atau semua terbeli atau tidak sama sekali. Kamu tidak akan pernah bayar sebagian keranjang.

## ❓ Kenapa ini penting

Di Minggu 4 kamu memindahkan panggilan `db.session` dari route ke repository. Dua masalah biasanya masih tersisa:

1. **Aturan bisnis terikat database** — setiap tes aturan butuh PostgreSQL berjalan, jadi suite tes crawl.
2. **Batas transaksi tidak jelas** — setengah operasi tersimpan, dan tidak ada yang tahu di mana commit terjadi.

Repository dan unit of work memperbaiki keduanya: pustakawan menyembunyikan di mana buku disimpan, dan checkout memastikan kamu tidak pernah bayar setengah keranjang.

Argumen jujur: SQLAlchemy's `Session` sudah *adalah* unit of work dengan query mirip repository. Tambahkan layer sendiri saat kamu butuh tes tanpa database atau berencana ganti penyimpanan — bukan secara otomatis.

## 📖 Langkah demi langkah

### 1. Antarmuka repository

```python
class ApplicationRepository(Protocol):
    def add(self, application: Application) -> int: ...
    def get(self, application_id: int) -> Application | None: ...
    def list_for_user(self, user_id: int) -> list[Application]: ...
    def update(self, application: Application) -> None: ...
    def remove(self, application_id: int) -> None: ...
```

Aturan desain:
- Gunakan **bahasa domain** (`list_for_user`, `find_due_follow_ups`), bukan SQL (`select_where`).
- Kembalikan **objek domain** atau `None`, jangan baris mentah atau query object ORM yang bocor penyimpanan.
- **Jangan commit di dalam method repository** — itu tugas unit of work.

### 2. Implementasi asli: pemetaan baris ↔ objek domain

```python
class SqlApplicationRepository:
    def __init__(self, connection):
        self._conn = connection

    def get(self, application_id):
        row = self._conn.execute(select(applications_table).where(applications_table.c.id == application_id)).first()
        return Application(user_id=row.user_id, company=row.company, role=row.role, status=row.status, id=row.id) if row else None
```

Di sini `Application` domain adalah dataclass biasa; repository melakukan pemetaannya. (Dengan ORM model SQLAlchemy kamu juga bisa pemetakan kelas langsung — lebih sederhana, tapi domain class tergantung SQLAlchemy.)

### 3. Unit of Work sebagai context manager

```python
class SqlUnitOfWork:
    def __init__(self, engine):
        self._engine = engine

    def __enter__(self):
        self._connection = self._engine.connect()
        self._transaction = self._connection.begin()
        self.applications = SqlApplicationRepository(self._connection)
        return self

    def commit(self):
        self._transaction.commit()
        self._transaction = self._connection.begin()

    def __exit__(self, *exc_info):
        if self._transaction.is_active:
            self._transaction.rollback()      # no commit or an exception → nothing saved
        self._connection.close()
```

```python
def withdraw_all(uow, user_id):
    with uow:
        for app in uow.applications.list_for_user(user_id):
            if app.is_active:
                app.status = "withdrawn"
                uow.applications.update(app)
        uow.commit()                          # one atomic change
    # send emails AFTER commit (or publish an event → worker)
```

**Commit eksplisit** adalah pilihan sengaja: lupa commit kehilangan perubahan dengan aman, daripada auto-commit setengah pekerjaan.

### 4. Fake

Fake repository adalah dictionary dengan method yang sama. Tiba-tiba aturan bisnis bisa ditest dalam milidetik, tanpa database sama sekali.

```python
class InMemoryUnitOfWork:
    def __enter__(self):
        self._working = copy.deepcopy(self._database)   # uncommitted changes live in a copy
        self.applications = InMemoryApplicationRepository(self._working)
        return self

    def commit(self):
        self._database.rows = copy.deepcopy(self._working.rows)
```

Tes service berjalan dalam milidetik dengan `InMemoryUnitOfWork` — ratusan tes aturan bisnis tanpa Docker.

### 5. Contract test: satu suite tes, dua implementasi

Inilah yang mencegah fake berbohong: tes yang sama dijalankan di repository asli dan fake, jadi "lulus dengan fake" berarti sesuatu.

```python
@pytest.fixture(params=["memory", "sql"])
def make_uow(request): ...

def test_without_commit_nothing_is_saved(make_uow):
    with make_uow() as uow:
        uow.applications.add(new_app())
    with make_uow() as uow:
        assert uow.applications.list_for_user(1) == []
```

Fake yang berperilaku beda dari production lebih buruk daripada tanpa fake. Menjalankan tes yang **sama** di kedua membukti mereka sepakat tentang kontrak (id, urutan, error "tidak ditemukan", rollback).

### 6. "Apa SQLAlchemy tidak sudah lakukan ini?"

Ya:
- `Session` **adalah** unit of work (lacak perubahan, flush, `commit()`/`rollback()`),
- `session.get(Application, id)` / `session.scalars(select(...))` mirip repository.

| Situasi | Rekomendasi |
|---|---|
| API CRUD kecil, logika kebanyakan di query | gunakan `Session` langsung di service (gaya Minggu 4), tes dengan PostgreSQL |
| Aturan bisnis kaya, banyak unit test, kemungkinan ganti penyimpanan | tambah antarmuka repository + UoW di atas SQLAlchemy |
| Beberapa sumber data dalam satu use case (DB + API eksternal + cache) | UoW yang mengkoordinasikan sangat berharga |

### Pilih setup-mu

Setiap pilihan di sini adalah trade-off:

| Pilihan | ✅ | ❌ |
|---|---|---|
| Antarmuka repository | logika teruji, detail persistence di satu tempat | layer ekstra; risiko reinvent ORM |
| Generic repository (`get/add/remove` untuk semua model) | sedikit kode | akhirnya bocor query; domain language lemah |
| Repository spesifik | ekspresif (`find_due_follow_ups`) | lebih banyak method yang dirawat |
| Explicit UoW commit | jelas, batas transaksi aman | harus ingat commit |
| Fake + contract test | tes cepat yang bisa dipercaya | contract test harus dirawat dengan antarmuka |
| Dataclass domain + pemetaan | domain independen ORM | kode pemetaan |

- ✅ Service dengan aturan bisnis bermakna yang ingin diunit test.
- ✅ Operasi yang menyentuh beberapa aggregate yang harus sukses atau gagal bersama.
- ✅ Saat penyimpanan mungkin berubah (SQL → document store, atau API eksternal sebagai sumber kebenaran).
- 🚫 Endpoint CRUD tipis tanpa logika — layer ekstra tidak menambah apa-apa.
- 🚫 Query laporan kompleks — gunakan query model baca khusus (SQL view, query service) daripada paksa melalui repository.

## ⚠️ Kesalahan umum

- `repository.save()` yang commit — komposisi dua save kehilangan atomicity.
- Kembalikan SQLAlchemy `Query` object dari repository sehingga pemanggil terus bangun SQL.
- Fake yang auto-assign id berbeda, abaikan rollback, atau kembalikan objek mutable bersama.
- Kirim email di dalam transaksi, sebelum commit.

:::revoshop
RevoShop punya `app/repositories/*`. (1) Buka `order_repository.py`: apakah `OrderRepository.create` panggil `db.session.commit()`? Apa yang terjadi jika kamu ingin create order **dan** record payment dalam satu aksi atomik dari service? (2) Apakah method repository kembalikan instance model, dict atau query? (3) Unit test mock repository (`tests/unit/test_order_service.py`) — apa yang akan catch contract test antara fake dan repository asli yang mock tidak bisa?
:::

## 🏆 Praktik terbaik

- [ ] Nama method repository dalam bahasa domain; kembalikan objek domain atau DTO, jangan query ORM.
- [ ] **Jangan pernah commit di dalam repository**; satu use case = satu unit of work = satu commit.
- [ ] Rollback otomatis pada exception atau commit hilang; selalu tutup koneksi.
- [ ] Picu side effect (email, event) **setelah** commit.
- [ ] Jaga fake di balik protocol yang sama dan jalankan **contract test** di implementasi fake dan asli.
- [ ] Jangan buat repository per tabel dengan reflex — kelompokkan by aggregate/use case.
- [ ] Gunakan session ORM langsung saat layer ekstra tidak sebanding — dan catat dalam design note.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan unit of work kepada non-programmer dengan analogi keranjang belanja, lalu katakan apa yang salah di sistem checkout yang "bayar tiap item terpisah" saat kartu ditolak di item ketiga.

## 📐 Rancang

Use case "Import from job board" di CareerPilot: ambil 50 job dari API partner, buat atau update row `Company`, buat row `Application` (status `saved`) untuk yang dipilih user, catat `ImportRun` (count, error), dan kirim satu notifikasi ringkasan. Rancang repository, batas unit-of-work, apa yang terjadi saat job ke-30 punya data salah, dan bagaimana kamu tes dengan cepat.

:::quiz
Lihat contoh rancangan

**Repository** (via satu UoW): `companies` (`get_by_normalized_name`, `add`), `applications` (`add`, `exists_for_job(user_id, external_job_id)`), `import_runs` (`add`, `update`).

**Alur**
1. **Di luar transaksi apa pun**: ambil 50 job dari API partner (panggilan jaringan tidak boleh tahan transaksi DB terbuka).
2. Validasi/normalisasi tiap job dalam memori → pisahkan jadi `valid` dan `rejected` (beserta alasan). Job yang salah #30 **ditolak, bukan fatal**.
3. **UoW #1** (`with uow:`): upsert company, tambah application untuk job valid terpilih (skip yang sudah diimport), tambah `ImportRun(count, alasan_ditolak)`, `commit()` — semua atau tidak sama sekali untuk database.
4. **Setelah commit**: publish `import_completed {run_id}` → worker kirim notifikasi ringkasan (retry independen dari import).

Jika exception tak terduga terjadi di dalam langkah 3 (misal database error), semua rollback dan `ImportRun` bisa dicatat sebagai gagal dalam **UoW kecil terpisah** sehingga user tahu apa yang terjadi.

**Tes**: tes service dengan `FakeUnitOfWork` + `FakeJobBoardClient` cover validasi, duplikat dan count dalam milidetik; contract test buktikan fake dan repository SQL setuju; satu tes integrasi jalankan UoW asli di PostgreSQL.
:::

### 📝 Checklist review mandiri

- [ ] Network I/O di luar transaksi
- [ ] Aturan jelas untuk partial data salah vs error fatal
- [ ] Notifikasi setelah commit
- [ ] Tes cepat dengan fake, plus cakupan contract/integrasi

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/architecture/e-backend-architecture/01-repository-unit-of-work" ai="no-ai" title="Repository dan unit of work — fake dan PostgreSQL"}
Implementasikan repository dalam-memori dan SQLAlchemy Core plus unit of work yang sesuai. Tes contract yang sama dijalankan di kedua: id, objek independen, error update/remove, no commit = tidak disimpan, rollback pada exception, dan tidak ada koneksi bocor.
:::

:::hints
- SQL add: `insert(table).values(...).returning(table.c.id)` lalu `.scalar_one()`.
- SQL update/remove: cek `result.rowcount == 0` untuk raise `LookupError`.
- `SqlUnitOfWork.__exit__`: rollback kalau `self._transaction.is_active`, lalu tutup di `finally`.
- Dalam-memori: `copy.deepcopy` database saat enter; copy object saat `get` sehingga pemanggil tidak bisa mutate baris tersimpan.
:::

## ✅ Cek cepat

:::quiz
Kenapa method repository tidak boleh commit?

Karena use case sering ubah beberapa hal yang harus sukses atau gagal bersama; commit di dalam repository memecah atomicity itu. Unit of work punya batas transaksi.
:::

:::quiz
Apa yang dilindungi contract test?

Implementasi fake drift dari yang asli, sehingga tes lulus dengan fake padahal production berperilaku beda.
:::


## 📚 Lanjut belajar

- [Cosmic Python — Repository pattern](https://www.cosmicpython.com/book/chapter_02_repository.html)
- [Cosmic Python — Unit of Work pattern](https://www.cosmicpython.com/book/chapter_06_uow.html)
- [SQLAlchemy docs: Session basics (unit of work ORM)](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)

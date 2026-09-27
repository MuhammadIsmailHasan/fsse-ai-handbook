---
title: "Models: Mendefinisikan Tabel Database sebagai Kelas Python"
summary: Tulis model SQLAlchemy 2.0 dengan tipe — kolom, nullable, default, constraint, index, timestamp, dan enum — sehingga Python dan PostgreSQL sepakat tentang aturannya.
sourceHash: 19cb827f52b8
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Model deklaratif dengan **`Mapped[...]`** dan **`mapped_column()`** (SQLAlchemy 2.0)
- Bagaimana tipe hint Python menentukan **nullable**
- Default sisi Python vs **default sisi server**; `created_at` / `updated_at`
- Constraint dan index di model: `unique`, `CheckConstraint`, `UniqueConstraint`, `Index`, **naming convention**
- Enum untuk status, kolom uang, dan `__repr__`
- Jaga model tetap fokus: apa yang ada di model dan apa yang tidak

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Model** | Kelas Python yang menggambarkan satu tabel |
| **`Mapped[...]` / `mapped_column()`** | Cara modern mendeklarasikan kolom dan tipenya |
| **Nullable** | Boleh kosong atau tidak |
| **Python default** | Nilai yang diisi kode saat membuat baris |
| **Server default** | Nilai yang diisi database (`now()`) |
| **Constraint** | Aturan yang dipaksakan database (`UNIQUE`, `CHECK`) |
| **Naming convention** | Pola penamaan yang dapat diprediksi |
| **Enum** | Kumpulan nilai yang diizinkan (status) |

## 🧠 Ide besarnya

Model adalah **kontrak yang ditulis dua kali sekaligus**: sekali di Python agar kode tahu bentuk data, sekali di database agar aturan benar-benar diterapkan. SQLAlchemy membiarkan kamu menulis sekali sebagai kelas dan menghasilkan tabel — dan nanti migration — darinya.

Tabel yang kamu tulis dengan tangan di SQL di Minggu 2 menjadi:

```python
class Application(db.Model):
    __tablename__ = "applications"

    id: Mapped[int] = mapped_column(primary_key=True)
    role_title: Mapped[str] = mapped_column(String(200))
    salary_expectation: Mapped[int | None]
```

## ❓ Kenapa ini penting

Aplikasimu butuh objek Python dengan atribut; database butuh tabel dengan kolom dan constraint. Menjaga keduanya tetap sejalan dengan tangan — lama-lama bergeser — dan model juga menjadi input untuk **migration** (materi 04), **relationship** (materi 05), dan type checking di service-mu.

Model yang tidak hati-hati menyebabkan kerusakan diam-diam:

```python
class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    status = db.Column(db.String)          # any text, nullable, no rule
    salary = db.Column(db.Float)           # money as float 😬
    created_at = db.Column(db.DateTime, default=datetime.now())   # evaluated ONCE at import time!
```

- `status` menerima `NULL` dan `"aplied"`.
- Uang dapat pembulatan yang salah.
- `default=datetime.now()` — dengan tanda kurung — membeku waktu saat aplikasi dimulai, jadi setiap baris dapat timestamp yang sama.
- Constraint tanpa nama menghasilkan migration dan pesan error yang sulit dibaca.

## 📖 Langkah demi langkah

### 1. Basis dan model pertama

```python
from datetime import datetime
from sqlalchemy import MetaData, String, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from flask_sqlalchemy import SQLAlchemy

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)

db = SQLAlchemy(model_class=Base)
```

**Naming convention** memberi setiap constraint nama yang dapat diprediksi — penting untuk migration yang nanti menghapus atau mengubah constraint.

### 2. Kolom bertipe

```python
class Company(db.Model):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    website: Mapped[str | None] = mapped_column(String(500))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
```

| Anotasi Python | Database |
|---|---|
| `Mapped[str]` | `NOT NULL` |
| `Mapped[str \| None]` | nullable |
| `Mapped[int]` | `INTEGER NOT NULL` (gunakan `BigInteger` eksplisit untuk id/jumlah sangat besar) |
| `Mapped[bool]` | `BOOLEAN NOT NULL` |
| `Mapped[datetime]` | `TIMESTAMP NOT NULL` — tambahkan `DateTime(timezone=True)` untuk `timestamptz` |
| `Mapped[Decimal]` | `NUMERIC` — sebutkan presisi: `Numeric(12, 2)` |

Tipe hint adalah **sumber kebenaran tunggal** untuk nullable — dan type checker-mu juga mengerti.

### 3. Default: sisi Python vs sisi server

Ingat bedanya dengan siapa isi formulir: Python default diisi aplikasimu sebelum mengirimkan; server default diisi database saat baris tiba — termasuk untuk baris yang dimasukkan script atau layanan lain.

```python
from sqlalchemy import DateTime, func

class Application(db.Model):
    status: Mapped[str] = mapped_column(String(30), default="applied", server_default="applied")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
```

| Opsi | Siapa atur nilai | Berlaku untuk |
|---|---|---|
| `default=` | SQLAlchemy, saat insert melalui ORM | hanya insert ORM |
| `server_default=` | **database** (`DEFAULT` di tabel) | setiap insert, termasuk SQL mentah dan aplikasi lain |
| `onupdate=` | SQLAlchemy pada update ORM | hanya update ORM |

Kirim **fungsi**, bukan hasil: `default=datetime.now` atau `func.now()` — jangan `datetime.now()`.

### 4. Constraint dan index

```python
from sqlalchemy import CheckConstraint, Index, UniqueConstraint

class Application(db.Model):
    __tablename__ = "applications"
    __table_args__ = (
        CheckConstraint("salary_expectation >= 0", name="salary_non_negative"),
        CheckConstraint("length(trim(role_title)) > 0", name="role_title_not_blank"),
        UniqueConstraint("user_id", "company_id", "role_title", name="uq_applications_user_company_role"),
        Index("ix_applications_user_created", "user_id", "created_at"),
    )
```

Aturan Minggu 2 berpindah ke model: check, keunikan gabungan, index gabungan (materi 06 Minggu 2).

### 5. Enum untuk status

```python
import enum
from sqlalchemy import Enum

class ApplicationStatus(enum.StrEnum):
    WISHLIST = "wishlist"
    APPLIED = "applied"
    INTERVIEW = "interview"
    OFFER = "offer"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"

status: Mapped[ApplicationStatus] = mapped_column(
    Enum(
        ApplicationStatus,
        native_enum=False,          # store as VARCHAR instead of a PostgreSQL ENUM type
        create_constraint=True,     # add a CHECK constraint with the allowed values
        length=30,
        values_callable=lambda e: [m.value for m in e],
    ),
    default=ApplicationStatus.APPLIED,
)
```

`native_enum=False` menyimpan `VARCHAR`, lebih mudah diubah nanti daripada tipe PostgreSQL `ENUM`. `values_callable` menyimpan **nilai** huruf kecil bukan nama anggota.

:::warning[Constraint CHECK adalah opt-in]
Sejak SQLAlchemy 1.4, non-native `Enum` **tidak** membuat constraint `CHECK` kecuali kamu kirim `create_constraint=True`. Tanpanya, Python validasi nilai, tapi database terima teks apa saja — SQL mentah, script dan layanan lain dapat memasukkan `'hired'`. Selalu verifikasi dengan insert tidak sah.
:::

### 6. `__repr__` dan metode domain kecil

```python
    def __repr__(self) -> str:
        return f"<Application id={self.id} {self.role_title!r} status={self.status}>"

    @property
    def is_active(self) -> bool:
        return self.status in {ApplicationStatus.APPLIED, ApplicationStatus.INTERVIEW}
```

### 7. Apa yang ada di model?

Jaga model dekat tabel: field, aturan dan pembantu kecil. Proses bisnis yang sentuh beberapa tabel ada di service (materi 06), atau model menjadi aplikasi kedua yang tersembunyi.

| ✅ Di model | ❌ Bukan di model |
|---|---|
| kolom, constraint, relationship | penanganan HTTP request/response |
| properti turunan sederhana (`is_active`) | kirim email, panggil API eksternal |
| invarian kecil tentang field sendiri | query lintas banyak tabel (→ repository) |
| | serialisasi JSON untuk endpoint spesifik (→ schema) |

Model yang tumbuh `to_dict_for_admin_page()`, `send_welcome_email()` dan 30 pembantu query jadi sulit diubah.

### Pilih setup-mu

Setiap opsi di sini adalah trade-off:

| Pilihan | ✅ | ❌ |
|---|---|---|
| Gaya `Mapped[...]` bertipe | type checking, nullable jelas, dokumentasi modern | beda dari tutorial lama (`db.Column`) |
| Legacy `db.Column(...)` | umum di kode ada | nullable default (mudah lupa `nullable=False`), tanpa tipe |
| `server_default` | diterapkan untuk setiap penulis | nilai tidak terlihat di objek Python sampai refresh |
| Python `default` | langsung di Python | insert SQL mentah lewati |
| Non-native enum (VARCHAR + CHECK via `create_constraint=True`) | mudah berkembang | penyimpanan sedikit lebih besar; ingat flag opt-in |
| Native PostgreSQL ENUM | ringkas | ubah nilai butuh migration khusus |

- ✅ Deklarasikan **setiap** aturan yang harus selalu ada di model/tabel (nullable, uniqueness, check).
- ✅ Gunakan `server_default` untuk timestamp dan default penting.
- 🚫 Jangan pakai `db.create_all()` untuk kelola schema production — gunakan migration (materi 04).
- 🚫 Jangan taruh alur kerja bisnis atau logika presentasi di model.

## ⚠️ Kesalahan umum

- `default=datetime.now()` (dievaluasi sekali).
- Lupa timestamp sadar zona.
- `Float` untuk uang.
- Hilang `nullable=False` di gaya legacy `db.Column`.
- Constraint tanpa nama yang migration tidak bisa rujuk.

:::revoshop
Buka `app/models/products.py` di RevoShop. Ia gunakan gaya legacy `db.Column`: `price = db.Column(db.Numeric(11, 2), nullable=False)` (bagus — Numeric untuk uang), constraint check **bernama** `ck_products_price_non_negative`, foreign key dengan `ondelete='SET NULL'` dan `index=True`, `is_active` untuk soft delete, dan `created_at = db.Column(db.DateTime, default=utcnow)`. Jawab: (1) `created_at` sadar zona? (2) Kolom mana nullable hanya karena `nullable=False` hilang? (3) Tulis ulang model di gaya `Mapped` bertipe — apa yang berubah? (4) `to_dict()` ada di model: pro dan kontra dibanding schema marshmallow?
:::

## 🏆 Praktik terbaik

- [ ] Gunakan **model SQLAlchemy 2.0 bertipe** (`Mapped`, `mapped_column`) untuk kode baru.
- [ ] Atur **naming convention** di metadata sebelum migration pertama.
- [ ] Biarkan `Mapped[X | None]` tentukan nullable — dan izinkan `None` hanya saat bermakna.
- [ ] Timestamp: `DateTime(timezone=True)` dengan `server_default=func.now()`; `updated_at` dengan `onupdate`.
- [ ] Uang: `Numeric(precision, scale)` atau integer unit terkecil — jangan pernah `Float`.
- [ ] Status sebagai `StrEnum` (non-native **dengan `create_constraint=True`**) atau `CHECK` eksplisit — bukan teks bebas.
- [ ] Tambah constraint `__table_args__` dan index gabungan yang cocok query sungguhan.
- [ ] Beri model `__repr__` berguna; jaga tetap kecil.
- [ ] Kirim callable ke default (`func.now()`, `datetime.now`), bukan nilai dievaluasi.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke orang non-programmer kenapa aturan database (misalnya "gaji tidak bisa negatif") harus ada di model Python dan tabel database sekaligus, walaupun terasa seperti menulis dua kali.

## 📐 Rancang

Tulis model SQLAlchemy bertipe (field, tipe, nullable, default, constraint, index) untuk CareerPilot **`Interview`**: milik application; tipe (`hr`, `technical`, `system_design`, `final`); jadwal mulai dan selesai (sadar zona; selesai sesudah mulai); URL meeting opsional; hasil (`pending`, `passed`, `failed`) default pending; catatan opsional; timestamp. Query sering: "interview akan datang untuk application pengguna, urut waktu mulai".

:::quiz
Lihat contoh model

```python
class InterviewType(enum.StrEnum):
    HR = "hr"; TECHNICAL = "technical"; SYSTEM_DESIGN = "system_design"; FINAL = "final"

class InterviewOutcome(enum.StrEnum):
    PENDING = "pending"; PASSED = "passed"; FAILED = "failed"

def str_enum(e):
    return Enum(e, native_enum=False, create_constraint=True, length=30, values_callable=lambda m: [x.value for x in m])

class Interview(db.Model):
    __tablename__ = "interviews"
    __table_args__ = (
        CheckConstraint("ends_at > starts_at", name="ends_after_starts"),
        Index("ix_interviews_application_starts", "application_id", "starts_at"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    application_id: Mapped[int] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"))
    type: Mapped[InterviewType] = mapped_column(str_enum(InterviewType))
    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    meeting_url: Mapped[str | None] = mapped_column(String(500))
    outcome: Mapped[InterviewOutcome] = mapped_column(
        str_enum(InterviewOutcome), default=InterviewOutcome.PENDING, server_default="pending"
    )
    notes: Mapped[str | None]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```

Index gabungan `(application_id, starts_at)` layani "interview dari application ini urut waktu".
:::

### 📝 Checklist review mandiri

- [ ] Nullable sesuai requirement persis
- [ ] Timestamp sadar zona dengan default server
- [ ] Enum/check batasi status dan jendela waktu
- [ ] Index cocok query sering

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m2/w4/03-models" ai="no-ai" title="Model bertipe yang paksakan aturan"}
Tulis `models.py` dengan naming convention, model `User`, `Company` dan `Application` di gaya SQLAlchemy 2.0 bertipe. Test buat tabel di schema PostgreSQL segar, **inspeksi** kolom dan constraint sungguhan, dan coba masukkan data tidak sah — jadi aturan harus ada di database, bukan hanya Python.
:::

:::hints
- Nullable = `Mapped[X | None]`; sisanya `NOT NULL`.
- Sadar zona: `mapped_column(DateTime(timezone=True), server_default=func.now())`.
- Email unik case-insensitive: `Index("ix_users_email_lower", func.lower(email), unique=True)` dalam `__table_args__` (rujuk kolom setelah didefinisikan, atau gunakan `text("lower(email)")`).
- Untuk enum status, gunakan `native_enum=False`, `create_constraint=True` dan `values_callable` — lalu cek insert `'hired'` benar-benar gagal.
:::

### 🏆 Target lanjut

Tambah metode `to_summary()` … lalu pindahkan ke `serializers.py` terpisah dan jelaskan di catatan kenapa itu rumah lebih baik.

## ✅ Cek cepat

:::quiz
Bagaimana SQLAlchemy 2.0 tentukan kolom nullable?

Dari anotasi `Mapped[...]`: `Mapped[str]` adalah `NOT NULL`, `Mapped[str | None]` nullable (kecuali override dengan `nullable=`).
:::

:::quiz
Ada yang salah dengan `default=datetime.now()`?

Fungsi dipanggil sekali saat modul muat, jadi setiap baris dapat timestamp tetap itu. Kirim callable (`datetime.now`) atau gunakan `server_default=func.now()`.
:::

:::quiz
Kenapa atur naming convention untuk constraint?

Supaya setiap constraint dan index dapat nama dapat diprediksi, yang migration butuh ubah atau hapus, dan yang buat error terbaca.
:::


## 📚 Lanjut belajar

- [SQLAlchemy: Declarative mapping with mapped_column](https://docs.sqlalchemy.org/en/20/orm/declarative_tables.html)
- [SQLAlchemy: Configuring constraint naming conventions](https://docs.sqlalchemy.org/en/20/core/constraints.html#configuring-constraint-naming-conventions)
- [Flask-SQLAlchemy: Models and tables](https://flask-sqlalchemy.readthedocs.io/en/stable/models/)

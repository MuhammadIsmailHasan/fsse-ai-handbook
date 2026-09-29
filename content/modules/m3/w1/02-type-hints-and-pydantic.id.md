---
title: "Type Hints & Pydantic v2"
summary: Mesin di balik FastAPI — type hint Python plus model Pydantic v2 yang memvalidasi, mengoersi, dan mendokumentasikan datamu, dengan batasan Field dan validator buatan yang menolak input buruk sebelum mencapai logikamu.
sourceHash: ca0ebc76fa05
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Bagaimana **type hint** Python menggambarkan bentuk data
- Apa itu model **Pydantic** dan bagaimana ia memvalidasi dan **mengoersi** data
- Menambah aturan dengan **`Field`** (min/max, panjang, default)
- Menulis **validator buatan** untuk aturan yang tak bisa diungkap tipe
- Kenapa validasi di tepi menjaga logika inti tetap bersih

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Type hint** | Mendeklarasikan tipe nilai (`age: int`) |
| **Pydantic** | Pustaka yang memvalidasi data terhadap model |
| **Model** | Kelas yang menggambarkan field dan tipe yang diharapkan |
| **Coerce** | Mengubah input yang kompatibel ke tipe yang tepat |
| **Field** | Pembantu untuk menambah aturan ke field model |
| **Validator** | Kode buatan yang mengecek/membersihkan nilai |
| **ValidationError** | Error yang dilempar Pydantic saat data buruk |

## 🧠 Ide besarnya

Model Pydantic seperti **formulir dengan aturan di meja depan**. Sebelum pengunjung (data masuk) mencapai kantor (logikamu), meja mengecek formulir: nama terisi? umur angka betulan? email tampak valid? Formulir buruk ditolak di sana dengan catatan jelas, jadi kantormu hanya berurusan dengan data bersih dan benar.

## ❓ Kenapa ini penting

Data tak tepercaya — dari user, layanan lain, berkas — tempat bug dan lubang keamanan mulai. Kalau kamu memvalidasi tersebar di seluruh kode, kamu akan melewatkan kasus dan mengulang diri. Pydantic membuatmu mendeklarasikan aturannya **sekali** sebagai model; ia memvalidasi dan **mengoersi** di batas dan menyerahkan objek yang dijamin benar ke logikamu. FastAPI memakai persis ini untuk tiap request, jadi belajar Pydantic adalah belajar mesinnya.

## 📖 Langkah demi langkah

### 1. Type hint: kosakatanya

```python
name: str
age: int
price: float
tags: list[str]
nickname: str | None = None      # optional, defaults to None
```

Ini menggambarkan *maksud*. Sendirian, Python tak menegakkannya saat runtime — itu yang ditambahkan Pydantic.

### 2. Model Pydantic memvalidasi dan mengoersi

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
    is_active: bool = True

User(name="Ismail", age="30")     # age "30" is coerced to int 30 ✅
User(name="Ismail", age="old")    # raises ValidationError ❌
```

- **Validasi**: `age="old"` tak bisa jadi int → `ValidationError` dengan pesan jelas.
- **Coercion**: `age="30"` (string angka) jadi `30`. Pydantic membantu dengan lunak pada input yang jelas kompatibel.

### 3. Field: aturan melampaui tipe

`Field` menambah batasan yang tak bisa diungkap tipe telanjang:

```python
from pydantic import BaseModel, Field

class Product(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    price: float = Field(gt=0)                 # must be > 0
    stock: int = Field(default=0, ge=0)        # >= 0, defaults to 0
```

Kini `price=-5` ditolak otomatis — aturan yang kalau tidak harus kamu tulis tangan di mana-mana.

### 4. Validator buatan untuk aturan nyata

Sebagian aturan butuh logika. Pakai field validator:

```python
from pydantic import BaseModel, field_validator

class Signup(BaseModel):
    email: str
    password: str

    @field_validator("email")
    @classmethod
    def email_has_at(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("email must contain @")
        return v.lower()          # you can also clean/normalize
```

Validator bisa **menolak** (raise `ValueError`) dan **membersihkan** (mengembalikan nilai yang diperbaiki, seperti lowercasing).

### 5. Membaca error-nya

`ValidationError` memberitahumu persis apa yang gagal — field, aturan, dan nilai — yang diubah FastAPI menjadi body respons `422`. Kamu dapat error yang presisi dan terbaca-mesin secara gratis.

### Pilih apa yang divalidasi

| Aturan | Pakai |
|---|---|
| "harus int / str / list" | type hint |
| "harus > 0", "panjang 1–100" | batasan `Field(...)` |
| "email punya @", "tanggal akhir setelah awal" | validator buatan |
| Membersihkan (trim, lowercase) | kembalikan nilai diperbaiki dari validator |

- ✅ Modelkan tiap input eksternal; validasi di batas, bukan jauh di logika.
- ✅ Utamakan batasan `Field` dan validator daripada cek `if` yang tersebar.
- 🚫 Jangan percaya data masuk; jangan validasi ulang hal sama di sepuluh tempat.

## ⚠️ Kesalahan umum

- Melewatkan model dan mengoper dict mentah — celah validasi dan tanpa autocomplete.
- Mengecek ulang nilai dengan tangan *setelah* Pydantic sudah menjaminnya.
- Menaruh aturan bisnis yang butuh database di dalam validator (simpan itu di service).
- Lupa Pydantic **mengoersi** — `"30"` jadi `30` adalah fitur, tapi ketahui itu terjadi.
- Memakai pola Pydantic v1 (`@validator`) — v2 memakai `@field_validator` dan `model_config`.

:::revoshop
RevoShop (Flask) memakai skema Marshmallow untuk validasi. (1) Temukan sebuah skema dan tulis ulang sebagai model Pydantic dengan batasan `Field` (mis. `price > 0`, panjang nama). (2) Di mana RevoShop memvalidasi yang akan menjadi validator buatan (mis. email atau enum status)? (3) Pembersihan apa (trim, lowercase) yang bisa dipusatkan validator alih-alih diulang di route?
:::

## 🏆 Praktik terbaik

- [ ] Definisikan model Pydantic untuk tiap bentuk input dan output eksternal.
- [ ] Ungkap aturan sederhana dengan `Field`; pakai `field_validator` untuk logika dan pembersihan.
- [ ] Validasi sekali di batas; biarkan sisa kode mempercayai model.
- [ ] Kembalikan nilai ternormalisasi (trim/lowercase) dari validator agar data konsisten.
- [ ] Pakai idiom Pydantic v2 (`field_validator`, `model_config`), bukan v1.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan model Pydantic dengan analogi formulir-dan-meja-depan. Lalu beri satu contoh masing-masing aturan yang ditangani tipe, oleh `Field`, dan oleh validator buatan.

## 📐 Rancang

Rancang model Pydantic untuk input "buat lamaran" CareerPilot: `company` (tak kosong, ≤120 karakter), `role` (tak kosong), `salary_expectation` (opsional, kalau ada harus ≥ 0), `status` (salah satu dari `saved`, `applied`, `interviewing`), dan `contact_email` (harus punya `@`, disimpan lowercase). Putuskan aturan mana yang dipakai tiap field dan tulis modelnya.

:::quiz
Tampilkan satu rancangan yang mungkin

```python
from pydantic import BaseModel, Field, field_validator

class ApplicationIn(BaseModel):
    company: str = Field(min_length=1, max_length=120)
    role: str = Field(min_length=1)
    salary_expectation: float | None = Field(default=None, ge=0)
    status: str
    contact_email: str

    @field_validator("status")
    @classmethod
    def valid_status(cls, v: str) -> str:
        allowed = {"saved", "applied", "interviewing"}
        if v not in allowed:
            raise ValueError(f"status must be one of {allowed}")
        return v

    @field_validator("contact_email")
    @classmethod
    def email_ok(cls, v: str) -> str:
        if "@" not in v:
            raise ValueError("email must contain @")
        return v.lower()
```

- Tipe menangani `company`/`role`/`salary` menjadi jenis nilai yang benar.
- `Field` menangani panjang dan `ge=0` (dan default opsional).
- Validator menangani enum `status` dan aturan email + lowercasing.

**Aturan yang ditunjukkan:** cocokkan tiap aturan dengan alat paling sederhana — tipe, lalu `Field`, lalu validator — dan normalisasi di validator supaya kode hilir mendapat data bersih.
:::

### 📝 Checklist review mandiri

- [ ] Tiap field memakai aturan paling sederhana yang cocok (tipe → Field → validator)
- [ ] Field opsional punya default masuk akal
- [ ] Aturan enum/format ditangani validator
- [ ] Nilai dinormalisasi (lowercase/trim) di mana berguna

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m3/w1/02-pydantic-models" ai="no-ai" title="Validasi dan bersihkan dengan Pydantic v2"}
Bangun model `Product` dengan batasan `Field` (panjang nama, price > 0, stock ≥ 0) dan model `Signup` dengan validator buatan yang mewajibkan `@` di email dan menyimpannya lowercase. Tes mem-parse data valid (termasuk coercion string angka) dan meng-assert `ValidationError` pada tiap aturan yang rusak.
:::

:::hints
- `from pydantic import BaseModel, Field, field_validator, ValidationError`.
- `price: float = Field(gt=0)`, `name: str = Field(min_length=1, max_length=50)`, `stock: int = Field(ge=0)`.
- Validator email: `if "@" not in v: raise ValueError(...)` lalu `return v.lower()`.
- Di tes, pakai `with pytest.raises(ValidationError):` untuk kasus yang gagal.
:::

## ✅ Cek cepat

:::quiz
Apa beda validasi dan coercion di Pydantic?

Validasi menolak data yang tak bisa masuk ke model (melempar `ValidationError`), sementara coercion mengubah input yang jelas kompatibel ke tipe yang dideklarasikan — mis. string angka `"30"` jadi int `30`. Coercion itu kemudahan; validasi itu jaminan.
:::

:::quiz
Kapan kamu butuh `field_validator` buatan alih-alih batasan `Field`?

Saat aturannya butuh logika yang tak bisa diungkap batasan — mengecek email punya `@`, memastikan tanggal akhir setelah tanggal awal, atau menormalkan nilai (trim, lowercase). `Field` mencakup batas sederhana (min/max, panjang, ≥/≤); validator mencakup selainnya.
:::

## 📚 Lanjut belajar

- [Pydantic v2: models](https://docs.pydantic.dev/latest/concepts/models/)
- [Pydantic v2: fields & constraints](https://docs.pydantic.dev/latest/concepts/fields/)
- [Pydantic v2: validators](https://docs.pydantic.dev/latest/concepts/validators/)

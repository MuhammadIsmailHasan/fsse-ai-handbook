---
title: "Type Hints & Pemeriksaan Tipe Statis"
summary: Jelaskan tipe data yang fungsi terima dan kembalikan, biarkan mypy/pyright tangkap bug sebelum jalan, dan pakai alat type yang framework modern andalkan.
sourceHash: f6da8e380d73
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Memberi anotasi pada variabel, fungsi, koleksi, dan nilai yang bisa kosong
- Union type (`X | None`), `Literal`, `TypedDict`, `Protocol`, `Callable`
- Dasar generics: `list[T]`, `TypeVar` / sintaks baru `def first[T](...)` di Python 3.12
- Menjalankan **static type checker** (mypy atau pyright) di lokal dan di CI
- Kenapa FastAPI dan Pydantic (Module 3) mengubah type hint menjadi validasi saat jalan

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Type hint** | Catatan yang menjelaskan jenis nilai apa yang masuk dan keluar |
| **Static type checker** | Alat (mypy, pyright) yang membaca catatan itu dan menemukan ketidakcocokan tanpa menjalankan kode |
| **Dynamic typing** | Python hanya cek tipe saat kode jalan |
| **`X \| None`** | "Bisa X atau kosong" — harus ditangani dengan hati-hati |
| **`Literal`** | Hanya nilai-nilai tertentu yang dibolehkan (misalnya `"applied"`, `"offer"`) |
| **`TypedDict`** | Dict yang punya kunci dan tipe nilai yang sudah diketahui |
| **`Protocol`** | "Asal punya metode-metode ini, kamu cocok" |
| **Generic (`list[T]`)** | Wadah yang dijelaskan bersama dengan isi-nya |
| **Type alias** | Nama pendek untuk type yang panjang |

## 🧠 Ide besarnya

:term[Type hints]{bahasa="petunjuk tipe — anotasi yang menjelaskan jenis data yang diterima dan dikembalikan fungsi"} itu seperti **label di pipa gedung**: "air panas", "gas", "saluran keluar".

Air tidak peduli — Python tetap jalan tanpa cek — tapi tukang ledeng (editor dan type checker-mu) bisa langsung lihat kalau ada yang salah koneksi, misalnya pipa gas disambung ke wastafel.

## ❓ Kenapa ini penting

Python cuma cek tipe saat kode jalan, jadi kesalahan seperti kirim `None` ketika yang diharap string hanya ketahuan kalau baris itu benar-benar dijalankan — mungkin di production, jam 2 pagi. Type hint membiarkan alat menangkap seluruh kelas bug ini **sebelum** jalan, berdayakan autocomplete editor, dan dokumentasikan apa yang fungsi harapkan tepat di tempat kamu baca.

Tanpa type hint:

```python
def find_user(email):
    ...                       # returns a User — or None if not found

def greeting(email):
    user = find_user(email)
    return "Hi " + user.name   # 💥 AttributeError: 'NoneType' has no attribute 'name' — only for unknown emails
```

Dengan type hint, checker tahu langsung:

```python
def find_user(email: str) -> User | None: ...

def greeting(email: str) -> str:
    user = find_user(email)
    return "Hi " + user.name   # error: Item "None" of "User | None" has no attribute "name"
```

## 📖 Langkah demi langkah

### 1. Dasarnya

```python
count: int = 0
names: list[str] = []
prices: dict[str, int] = {}
point: tuple[float, float] = (-6.2, 106.8)
ids: set[int] = set()

def apply_discount(price: int, percent: int = 10) -> int:
    return price * (100 - percent) // 100

def log(message: str) -> None:     # returns nothing
    print(message)
```

Built-in generic (`list[str]`, `dict[str, int]`) sudah jalan langsung di Python modern — tidak perlu `from typing import List`.

### 2. Nilai yang bisa kosong dan union

`User | None` adalah tipe yang berkata "kotak ini mungkin kosong — buka dengan hati-hati". Satu hint ini cegah kebanyakan crash `NoneType`.

```python
def parse_salary(text: str) -> int | None:
    text = text.strip()
    return int(text) if text else None

salary = parse_salary(raw)
if salary is not None:        # "narrowing": after this check, the checker knows salary is int
    print(salary + 1)
```

`int | None` berarti "int atau None". Checker paksa kamu tangani kasus `None` — itu yang penting.

### 3. Tipe yang lebih presisi

```python
from typing import Literal, TypedDict, Protocol, Callable, Final

Status = Literal["applied", "interview", "offer", "rejected"]      # only these strings

class JobDict(TypedDict):          # a dict with known keys (e.g. JSON payloads)
    title: str
    salary_max: int | None

class Notifier(Protocol):          # any object with this method fits ("duck typing" for checkers)
    def send(self, recipient: str, message: str) -> None: ...

Handler = Callable[[dict], str]    # a function taking a dict, returning a str

MAX_RETRIES: Final = 3             # must not be reassigned
```

`Protocol` adalah cara kamu type **dependency injection** tanpa warisan: `ReminderService(notifier: Notifier)` terima kelas apa pun dengan metode yang cocok.

### 4. Generics

```python
def first[T](items: list[T]) -> T | None:        # Python 3.12 syntax
    return items[0] if items else None

first([1, 2, 3])        # checker knows: int | None
first(["a"])            # str | None
```

(Cara lama: `T = TypeVar("T")` lalu `def first(items: list[T]) -> T | None`.)

### 5. Type alias

```python
type UserId = int                               # Python 3.12
type SkillCounts = dict[str, int]

def top_skills(counts: SkillCounts, n: int) -> list[tuple[str, int]]: ...
```

### 6. Menjalankan type checker

```bash
uv add --dev mypy          # or: pyright / basedpyright
uv run mypy src/           # check a folder
```

```toml
# pyproject.toml
[tool.mypy]
python_version = "3.12"
strict = true              # start strict on new projects; relax per module for legacy code
```

VS Code's Pylance (pyright) tunjukkan tipe error yang sama dengan yang mypy lapor.

### 7. Hint jadi validasi (preview)

Di Module 3, FastAPI dan Pydantic baca label yang sama ini dan pakai untuk cek request saat jalan — label pipa jadi inspector sungguhan di pintu masuk.

Type hint **tidak ada efek saat jalan** di plain Python:

```python
apply_discount("100", "abc")   # runs, then crashes inside — hints didn't stop it
```

Library seperti **Pydantic** dan **FastAPI** baca hint kamu dan **validasi** data masuk saat jalan:

```python
class ApplicationIn(BaseModel):
    company_id: int
    status: Literal["applied", "interview"] = "applied"
# {"company_id": "abc"} → automatic 422 error with a clear message
```

### Pilih setup-mu

Setiap pilihan ini ada trade-off:

| Pilihan | ✅ | ❌ |
|---|---|---|
| Type hint + checker | tangkap bug awal, autocomplete, dokumentasi sendiri | sintaks tambah; kadang berantem dengan kode dinamis |
| Tidak ada hint | cepat untuk skrip kecil | bug ketemu saat jalan; refactor lebih susah |
| Mode `strict` | keamanan maksimal | berisik untuk kode lama |
| `Any` | jalur keluar | matiin checker untuk nilai itu |
| `TypedDict` | tipe untuk dict bentuk JSON | tidak ada validasi saat jalan |
| Model Pydantic | validasi saat jalan | dependency, sedikit overhead |

- ✅ Type **semua** function signature di kode aplikasi; jalankan checker di CI.
- ✅ `X | None` untuk apa saja yang bisa hilang — dan tangani.
- ✅ `Protocol` untuk dependency yang disuntik; `Literal` untuk set string tetap.
- 🚫 Jangan tabur `Any` atau `# type: ignore` untuk diamkan masalah sungguhan.
- 🚫 Jangan anggap type hint sebagai validasi input di batas API — tetap validasi saat jalan.

## ⚠️ Kesalahan umum

- Lupa `| None` untuk fungsi yang bisa return tidak ada apa-apa.
- Pakai `list` tanpa tipe item (`list` bukan `list[Job]`).
- Percaya hint validasi data saat jalan.
- `def f(items: list = [])` — masih default mutable, meski ada hint.
- Diam-diamkan error dengan `Any` bukan perbaiki desain.

:::revoshop
Pilih tiga fungsi di `app/services/` RevoShop. Apakah mereka punya type hint untuk semua parameter dan return value? Tambah hint ke satu service di branch dan jalankan `uv run mypy app/services/<file>.py` (install mypy sementara). Apa yang di-report? Lihat khusus tempat repository bisa return `None` (misalnya "produk tidak ketemu") dan service pakai hasil tanpa cek.
:::

## 🏆 Praktik terbaik

- [ ] Anotasi **setiap function signature** (parameter dan return type), termasuk `-> None`.
- [ ] Pakai sintaks modern: `list[str]`, `X | None`, `type` alias (3.12+).
- [ ] Jalankan **mypy atau pyright di CI**; pakai `strict` untuk kode baru.
- [ ] Sempit nilai optional dengan cek eksplisit (`if x is None: …`) bukan asumsi.
- [ ] Lebih suka tipe presisi (`Literal`, `TypedDict`, dataclass, Protocol) daripada `dict`/`Any`.
- [ ] Simpan `# type: ignore[code]` jarang, spesifik, dan berikan alasan di komentar.
- [ ] Validasi input eksternal saat jalan (Pydantic/marshmallow); andalkan tipe di dalam.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan kepada non-programmer kenapa labeli input dan output fungsi bantu tim, meskipun Python abaikan label saat jalan.

## 📐 Rancang

Tulis full type signature (tanpa body) untuk application service CareerPilot:

- buat aplikasi (user id, company id, role, salary expectation opsional) → aplikasi baru
- cari by id untuk user → aplikasi atau tidak ada
- ubah status → aplikasi yang diperbarui; status harus salah satu nilai yang dibolehkan
- list untuk user dengan opsional filter status dan pagination → halaman object dengan items dan total
- service terima repository dan clock (disuntik)

:::quiz
Lihat kemungkinan signature

```python
from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Protocol, Callable

type Status = Literal["wishlist", "applied", "interview", "offer", "rejected", "withdrawn"]

@dataclass(frozen=True, slots=True)
class Page[T]:
    items: list[T]
    total: int

class ApplicationRepository(Protocol):
    def add(self, application: "Application") -> "Application": ...
    def get_for_user(self, application_id: int, user_id: int) -> "Application | None": ...
    def list_for_user(self, user_id: int, status: Status | None, limit: int, offset: int) -> Page["Application"]: ...

class ApplicationService:
    def __init__(self, repository: ApplicationRepository, clock: Callable[[], datetime]) -> None: ...
    def create(self, user_id: int, company_id: int, role_title: str, salary_expectation: int | None = None) -> "Application": ...
    def get(self, user_id: int, application_id: int) -> "Application | None": ...
    def change_status(self, user_id: int, application_id: int, status: Status) -> "Application": ...
    def list(self, user_id: int, *, status: Status | None = None, page: int = 1, per_page: int = 20) -> Page["Application"]: ...
```
:::

### 📝 Checklist review mandiri

- [ ] Return yang "mungkin tidak ada" adalah `X | None`
- [ ] Status pakai `Literal` (atau Enum)
- [ ] Dependency di-type dengan `Protocol`/`Callable`
- [ ] Opsi adalah keyword-only

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m2/w3/07-type-hints" ai="no-ai" title="Type, lalu biarkan mypy judge"}
`service.py` jalan saat runtime tapi **tidak punya** type hint dan dua bug `None` tersembunyi. Tambah hint lengkap dan presisi (`Literal`, `TypedDict`, `Protocol`, `X | None`, generics) dan perbaiki bug yang checker ketahui. Test jalankan kode-mu **dan** jalankan `mypy --strict` pada file-mu.
:::

:::hints
- Jalankan `uv run mypy --strict m2/w3/07-type-hints/service.py` dari `exercises/` dan baca error pertama.
- `dict.get()` return `X | None` — mypy akan paksa kamu tangani.
- `Protocol` untuk repository biarkan fake repository di test type-check.
:::

## ✅ Cek cepat

:::quiz
Apakah type hint cegah `apply_discount("100")` dari jalan?

Tidak. Python abaikan hint saat jalan. Type checker lapor kesalahan sebelum jalan; library validasi saat jalan (Pydantic) bisa paksa tipe pada data masuk.
:::

:::quiz
Apa yang `Protocol` biarkan kamu lakukan?

Jelaskan metode yang harus dimiliki objek, jadi kelas apa saja dengan metode yang cocok diterima type checker — tanpa warisi dari base class.
:::


## 📚 Lanjut belajar

- [Dokumentasi Python: typing](https://docs.python.org/3/library/typing.html)
- [mypy: Getting started](https://mypy.readthedocs.io/en/stable/getting_started.html)
- [Pydantic: Why use Pydantic](https://pydantic.dev/latest/why/)

---
title: "Komposisi daripada Warisan"
summary: Bangun perilaku dengan menggabung objek kecil, bukan pohon kelas dalam — kapan warisan cocok, kenapa itu patah, dan cara komposisi membuat kode Python fleksibel.
sourceHash: 893dcd86598b
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- **Is-a** (warisan) vs **has-a** (komposisi)
- Masalah hirarki dalam: ledakan kelas, kelas induk rapuh, coupling ketat
- Pola komposisi di Python: delegation, strategy object, kumpulan kemampuan
- Kapan warisan adalah alat yang tepat (dan cara memakainya dengan aman)
- Mixin dan warisan ganda — dengan hati-hati

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Inheritance** (warisan) | Kelas yang didasarkan pada kelas lain |
| **Composition** (komposisi) | Kelas yang tersusun dari objek lain yang ia miliki |
| **Delegation** (delegasi) | Melimpahkan pekerjaan ke objek yang kamu miliki |
| **Class explosion** | Terlalu banyak subkelas karena setiap kombinasi membuat satu kelas baru |
| **Fragile base class** | Perubahan di induk menciptakan masalah di anak tanpa terlihat |
| **Strategy object** | Objek perilaku yang bisa ditukar dengan yang lain |
| **Mixin** | Kelas kecil yang menambah satu kemampuan fokus |

## 🧠 Ide besarnya

Warisan itu seperti **genetika**: anak mewarisi segalanya dari orang tua, selamanya, dan tidak bisa pilih-pilih. Komposisi itu seperti **LEGO**: kamu bangun sesuatu dari balok, dan bisa tukar roda dengan baling-baling kapan saja.

Kalau kombinasi fitur bertambah (role × plan × region…), genetika menghasilkan pohon keluarga yang tidak terkontrol. LEGO tinggal tambah balok.

## ❓ Kenapa ini penting

Pelajaran awal tentang OOP mendorong warisan sebagai cara memakai ulang kode. Puluhan tahun pengalaman — buku *Design Patterns* sudah bilang "favor object composition over class inheritance" tahun 1994 — menunjukkan bahwa warisan mengikat subkelas erat ke bagian dalam induk, sedangkan variasi sebenarnya lebih baik digambar sebagai **bagian yang bisa kamu gabung dan tukar**.

Saat fitur mulai bertambah (role × plan × region), genetika memberimu pohon keluarga yang tidak bisa dikelola, dan LEGO tinggal tambah balok lagi.

## 📖 Langkah demi langkah

### 1. Is-a vs has-a

Tanya: **apakah ini hubungan tetap, benar-benar "is-a" yang punya kontrak lengkap?** Atau objek **punya** kemampuan yang bisa berubah atau berganti?

| Hubungan | Model yang lebih baik |
|---|---|
| `Account` **punya** role, **punya** plan | komposisi |
| `Notifier` **punya** retry policy | komposisi |
| `ValidationError` **adalah** `ValueError` | warisan ✅ |
| `PostgresRepository` **adalah** implementasi `Repository` | protocol (struktural) atau ABC |

### 2. Komposisi dengan mengumpul kemampuan

```python
@dataclass(frozen=True)
class Role:
    name: str
    permissions: frozenset[str]

class Account:
    def __init__(self, email, roles=(), plan=FREE):
        self.roles = set(roles)
        self.plan = plan

    def can(self, permission):
        return any(permission in role.permissions for role in self.roles)
```

Kombinasi role baru adalah **data**. Mengganti plan adalah `account.plan = PRO`. Tidak perlu kelas baru.

### 3. Komposisi dengan delegasi

```python
class ReportService:
    def __init__(self, repository, renderer, clock):
        self._repository = repository      # has-a
        self._renderer = renderer          # has-a
        self._clock = clock

    def monthly(self, user_id):
        apps = self._repository.list_for_user(user_id)
        return self._renderer.render(apps, generated_at=self._clock())
```

Tukar renderer (PDF → HTML) atau repository (Postgres → fake) tanpa subclass `ReportService`.

### 4. Kenapa warisan mengikat begitu ketat

Subkelas bisa bergantung pada **bagaimana** induk melakukan sesuatu, bukan hanya apa yang dijanjikannya. Lalu perubahan kecil di induk merusak anak yang penulis tidak pernah lihat.

```python
class BaseImporter:
    def run(self):
        for row in self.rows():
            self.save(row)

class CsvImporter(BaseImporter):
    def save(self, row):
        self.count += 1          # relies on base class calling save once per row
        super().save(row)
```

Kalau base class kemudian batch save (`save_many`), `CsvImporter` diam-diam patah: subkelas bergantung pada **bagaimana** induk bekerja, bukan hanya **apa** yang dijanjikannya. Itu masalah fragile base class.

### 5. Kapan warisan bagus saja

Warisan tepat saat hubungan benar-benar "jenis dari", induk stabil, dan hirarki tetap datar — contohnya kelas exception milikmu sendiri.

- **Exception hierarchies**: `class InvalidTransition(DomainError)` — pemanggil tangkap keluarga error.
- **Framework extension point** yang didesain untuk subclass: `flask.views.MethodView`, Django class-based view, `unittest.TestCase`, SQLAlchemy `DeclarativeBase`.
- **Template Method** dengan base kecil, stabil (Stage D).
- Datar (1 level), dengan kontrak lengkap dihormati (Liskov).

### 6. Mixin — warisan kecil, fokus

```python
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

class Application(TimestampMixin, db.Model): ...
```

Berguna untuk **menambah** fitur independen, agak tak berbentuk. Jaga mixin tetap kecil, jangan biarkan saling bergantung, dan hindari hirarki berlian.

### 7. Protocol mengganti paling banyak "interface inheritance" di Python

```python
class Renderer(Protocol):
    def render(self, applications, generated_at) -> str: ...
```

Kelas apa pun dengan `render` bekerja — tidak perlu base class untuk diwariskan, jadi tidak ada yang jadi rapuh.

### Memilih setup-mu

Setiap pilihan di sini adalah trade-off:

| Pilihan | ✅ | ❌ |
|---|---|---|
| Warisan | kode sedikit, natural untuk is-a dan framework yang sebenarnya | coupling ketat, ledakan kelas, tidak bisa berubah saat runtime |
| Komposisi | fleksibel, perubahan saat runtime, mudah diuji | lebih banyak wiring, objek agak lebih banyak dibaca |
| Mixin | memakai ulang perilaku kecil | kompleksitas MRO kalau berlebihan |
| Protocol | tidak ada coupling ke base class | tidak ada implementasi dibagikan (pakai helper function/komposisi untuk itu) |

- ✅ Komposisi: variasi yang bergabung (role × plan), perilaku yang berubah saat runtime, apa pun yang ingin kamu palsukan di tes.
- ✅ Warisan: exception, hook framework, hubungan is-a yang benar-benar stabil.
- 🚫 Warisan hanya untuk memakai ulang beberapa method — ekstrak function atau objek helper.
- 🚫 Hirarki dalam (lebih dari 2 level) di kode aplikasi.

## ⚠️ Kesalahan umum

- `class Admin(User)` untuk role yang bisa berubah.
- Override method induk untuk tidak melakukan apa-apa atau lempar exception — tanda subkelas tidak benar-benar subtype.
- Panggil `super()` dengan urutan rapuh di banyak mixin.
- Komposisi di mana-mana untuk kode trivial, ciptakan indirection tidak perlu.

:::revoshop
RevoShop punya pembeli, penjual, dan admin. (1) Lihat `app/models/users.py`: apakah role adalah kolom (data) atau kelas? (2) Apa yang diperlukan agar satu orang bisa jadi pembeli dan penjual? (3) Cari `app/services/` untuk `if role ==` — berapa banyak tempat yang berubah kalau kamu tambah role "support"? Sketsa model `Role` + permission dan fungsi `can(user, permission)` tunggal.
:::

## 🏆 Praktik terbaik

- [ ] Default ke komposisi; pembenaran warisan dengan is-a yang sebenarnya dan kontrak stabil.
- [ ] Hirarki tetap **datar**; prefer protocol untuk polymorphism.
- [ ] Model role, plan, permission dan pengaturan sebagai **data** (frozen dataclass, enum), bukan subkelas.
- [ ] Inject kolaborator lewat constructor; jangan buat di dalam method.
- [ ] Kalau kamu subclass kelas framework, override hanya documented hook.
- [ ] Pakai mixin jarang, untuk fitur independen, tanpa konflik state.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke developer junior kenapa `class ProRecruiter(Recruiter)` jadi masalah saat produk tambah plan "Enterprise" dan biarkan recruiter juga cari pekerjaan. Pakai analogi LEGO vs genetika.

## 📐 Rancang

Importer pekerjaan CareerPilot menarik listing dari board berbeda. Setiap board perlu **fetch** metode berbeda (REST API, RSS, CSV upload), **parser** berbeda, optional **rate limiting**, dan optional **deduplication**. Rancang dengan komposisi: objek apa yang ada, apa yang dipegang importer, dan cara bikin "RSS + dedupe, tanpa rate limit" dan "API + rate limit + dedupe" tanpa subkelas baru.

:::quiz
Lihat contoh rancangan

```python
class Fetcher(Protocol):   def fetch(self) -> Iterable[bytes]: ...
class Parser(Protocol):    def parse(self, raw: bytes) -> list[JobPosting]: ...
class Filter(Protocol):    def apply(self, jobs: list[JobPosting]) -> list[JobPosting]: ...

class ApiFetcher: ...          # uses an injected HTTP client
class RssFetcher: ...
class RateLimitedFetcher:      # wraps any Fetcher (composition/decorator)
    def __init__(self, inner: Fetcher, limiter): ...
class DedupeFilter: ...        # uses a seen-key store

class JobImporter:
    def __init__(self, fetcher: Fetcher, parser: Parser, filters: list[Filter], repository):
        ...
    def run(self) -> ImportReport:
        jobs = [job for raw in self.fetcher.fetch() for job in self.parser.parse(raw)]
        for f in self.filters:
            jobs = f.apply(jobs)
        self.repository.add_many(jobs)
```

Konfigurasi hanya assembli berbeda:
- `JobImporter(RssFetcher(url), RssParser(), [DedupeFilter(store)], repo)`
- `JobImporter(RateLimitedFetcher(ApiFetcher(client), limiter), KalibrrJsonParser(), [DedupeFilter(store)], repo)`

Board baru = pasangan fetcher/parser baru, filter memakai ulang. Fitur opsional = objek ada atau tidak ada, bukan kombinasi subkelas. (Stage D beri nama polanya: Strategy, Decorator, Pipeline.)
:::

### 📝 Checklist review mandiri

- [ ] Titik variasi adalah objek terpisah
- [ ] Perilaku opsional tidak perlu subkelas baru
- [ ] Setiap bagian bisa dipalsukan di tes

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/architecture/c-oop-design/02-composition-accounts" ai="no-ai" title="Ganti ledakan kelas dengan role dan plan"}
Ubah hirarki `JobSeeker`/`Recruiter`/`ProRecruiter` jadi `Account` yang **punya** role dan plan. Role dan plan berubah saat runtime di objek yang sama, permission dukung wildcard, dan tes periksa tidak ada kelas yang diwariskan dari yang lain.
:::

:::hints
- Role dan plan adalah frozen dataclass — nilai, bukan kelas berat perilaku.
- `can()`: bangun himpunan `{permission, "*", f"{resource}:*"}` dan periksa terhadap permission setiap role.
- `limit()`: `self.plan.limits.get(name, 0)`.
:::

## ✅ Cek cepat

:::quiz
Apa itu masalah "fragile base class"?

Subkelas bergantung pada detail implementasi induknya, jadi perubahan tampak aman di base class merusak subkelas dengan cara tak terduga.
:::

:::quiz
Beri satu kegunaan warisan yang bagus di Python.

Hirarki exception (contoh `class InvalidTransition(DomainError)`), atau documented framework extension point seperti `MethodView`.
:::


## 📚 Lanjut belajar

- [Dokumentasi Python: dataclass](https://docs.python.org/3/library/dataclasses.html)
- [Real Python: Inheritance and Composition — A Python OOP Guide](https://realpython.com/inheritance-composition-python/)

## 📣 Stage C selesai — bagikan

:::linkedin{type="concept"}
💡 "Favor composition over inheritance" akhirnya jelas untuk saya.

Saya model user sebagai JobSeeker → ProJobSeeker → RecruiterWhoIsAlsoJobSeeker… dan setiap plan baru double kelas. Upgrade user berarti ganti objek.

Perbaikannya: Account yang *punya* role dan *punya* plan. Kombinasi baru adalah data, bukan kelas — dan perubahan plan adalah satu assignment.

Rule of thumb yang saya pakai sekarang: warisan untuk is-a yang benar, stabil (seperti tipe exception); komposisi untuk apa pun yang berubah atau berganti saat runtime.

Warisan dalam pernah gigit kamu? 👇

#SoftwareDesign #OOP #Python #LearningInPublic
:::

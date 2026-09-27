---
title: "Pola Kreasi: Factory, Builder, Singleton"
summary: Kontrol cara objek dibuat — factory dan registry untuk memilih implementasi, builder untuk objek kompleks yang valid, dan kenapa Singleton biasanya jebakan (serta apa yang harus dilakukan).
sourceHash: d50ba934195f
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa itu :term[design pattern]{bahasa="pola desain — solusi umum yang sudah terbukti untuk masalah desain yang berulang"} — dan apa yang bukan
- **Factory** (factory sederhana, factory method, registry) untuk memilih implementasi
- **Builder** untuk objek dengan banyak bagian opsional dan aturan validasi
- **Singleton**: kenapa instance global merusak testing, dan alternatif Pythonic
- Bagaimana fitur Python (class first-class, decorator, module, `functools.cache`) menyederhanakan pola-pola ini

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Design pattern** | Solusi bernama yang sudah terbukti untuk masalah yang terus terulang |
| **Factory** | Satu tempat yang memutuskan class mana yang dibuat |
| **Registry** | Daftar yang memetakan nama ke class yang menanganinya |
| **Builder** | Membangun objek kompleks langkah demi langkah, divalidasi di akhir |
| **Singleton** | Tepat satu instance bersama untuk seluruh program |
| **Global state** | Data bersama yang bisa diakses siapa saja — sulit di-test |
| **`functools.cache`** | Cara Python yang sederhana untuk menyimpan satu objek yang sudah dibuat |

## 🧠 Ide besarnya

Pola desain itu **nama untuk solusi yang terus kamu reinvent**. Mengatakan "pakai factory dengan registry" di code review mengkomunikasikan satu desain utuh dalam lima kata — seperti dokter mengatakan "patah" daripada menjelaskan foto X-ray.

Pola kreasi menjawab satu pertanyaan: **siapa yang memutuskan object mana yang dibuat, dan bagaimana?**

## ❓ Kenapa ini penting

Membuat object terlihat mudah — `CsvExporter()` — sampai:

- class yang dibuat bergantung pada **konfigurasi atau input pengguna** (`format=xlsx`),
- object punya **sepuluh setting opsional** dan harus selalu **valid**,
- semua orang butuh **satu hal bersama yang sama** (setting, engine database, klien HTTP).

Lalu kode pembuatan menyebar: `if format == "csv" … elif …` di enam file, object setengah jadi, dan shared instance yang tidak bisa diganti di test.

Pola juga **nama untuk solusi yang terus kamu reinvent**: mengatakan "pakai factory dengan registry" di review mengkomunikasikan satu desain utuh dalam lima kata, seperti dokter mengatakan "patah" daripada menjelaskan X-ray.

## 📖 Langkah demi langkah

### 1. Factory: sentralisasi "class mana?"

```python
def create_exporter(name: str, **options):
    if name == "csv":
        return CsvExporter(**options)
    if name == "json":
        return JsonExporter(**options)
    raise ValueError(f"unknown exporter {name!r}")
```

Satu tempat untuk berubah; caller bergantung pada "exporter", bukan class konkret (SOLID's D).

### 2. Registry: factory yang terbuka untuk extension

Registry adalah versi phone directory dari factory: menambah exporter baru berarti menambah satu baris ke directory, bukan edit chain `if` yang juga orang lain edit.

Di Python, class adalah object — simpan di dict dan daftar dengan decorator:

```python
EXPORTERS: dict[str, type] = {}

def register_exporter(name):
    def decorator(cls):
        if name in EXPORTERS:
            raise ValueError(f"exporter {name!r} is already registered")
        EXPORTERS[name] = cls
        return cls
    return decorator

@register_exporter("csv")
class CsvLinesExporter: ...

def create_exporter(name, **options):
    try:
        return EXPORTERS[name](**options)
    except KeyError:
        raise ValueError(f"unknown exporter {name!r} (available: {', '.join(sorted(EXPORTERS))})") from None
```

Format baru mendaftar diri sendiri; factory tidak pernah berubah. Flask's `app.route`, plugin pytest dan admin Django pakai ide yang sama.

:::note[Factory Method vs Abstract Factory]
Di buku OOP klasik, **Factory Method** adalah method yang subclass override untuk memilih apa yang dibuat, dan **Abstract Factory** membuat *keluarga* object terkait (misalnya `AwsFactory` → storage S3 + antrian SQS; `LocalFactory` → folder storage + antrian in-memory). Di Python, function atau dict callable biasanya cukup.
:::

### 3. Builder: konstruksi langkah demi langkah dengan validasi di akhir

```python
posting = (
    JobPostingBuilder()
    .titled("Backend Engineer")
    .at("Kopi Data")
    .in_city("Jakarta")
    .salary(9_000_000, 14_000_000)
    .requires("Python", "SQL")
    .build()                       # validates everything, returns a frozen object
)
```

- Terbaca: setiap call menamai apa yang diset.
- Mengumpul bagian secara bertahap (skill ditambah dari beberapa tempat, dinormal sekali).
- `build()` menegakkan **aturan lintas-field** (kota *atau* remote; min ≤ max) dan return result **immutable**.

**Alternatif Pythonic**: untuk kasus sederhana, keyword argument + dataclass dengan validasi `__post_init__` sudah cukup. Ambil builder saat konstruksi multi-step, kondisional, atau dipakai ulang (test data builder, query builder seperti SQLAlchemy's `select().where().order_by()`).

### 4. Singleton: satu instance — dan jebakan

Jebakan adalah satu global instance yang dibagi test juga, jadi perubahan satu test bocor ke test berikutnya. Di Python kamu jarang perlu pola: module-level object atau cached factory function cukup dan tetap replaceable.

Singleton klasik menjamin class punya satu instance dengan akses global:

```python
class Settings:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

Kenapa biasanya jebakan:
- **Hidden global state**: kode mana saja bisa baca atau ubah; dependency tidak terlihat di signature function.
- **Sulit di-test**: test berbagi state dan bocor satu ke yang lain; kamu tidak bisa gampang pakai setting berbeda per test.
- **Import-time side effect**: membuat di import baca env var/koneksi service sebelum app dikonfigurasi.

Opsi lebih baik di Python:

| Butuh | Lakukan ini |
|---|---|
| Satu object bersama, dibuat lazy | function dengan `@functools.cache` (resettable via `.cache_clear()`) |
| Config untuk app | build di `create_app()` dan pass / simpan di `app.config` |
| Satu engine DB / klien HTTP per process | buat di app factory atau composition root, inject ke mana yang butuh |
| "Module-level singleton" | module sudah singleton — tapi jaga bebas side effect di import |

```python
@cache
def get_settings() -> Settings:
    return load_settings(os.environ)     # load_settings(env) stays pure and testable
```

### Memilih setup-mu

Setiap opsi di sini adalah trade-off:

| Pola | ✅ | ❌ |
|---|---|---|
| Simple factory | satu tempat untuk logika kreasi | tumbuh menjadi chain `if` |
| Registry | extensible tanpa edit factory | pendaftaran terjadi di import — module harus di-import; name clash |
| Builder | terbaca, divalidasi, result immutable | lebih banyak kode daripada constructor untuk object sederhana |
| Singleton class | jamin single instance | global state, testing pain, concurrency surprise |
| Cached getter / DI | explicit, resettable | ada yang harus wire (composition root) |

- ✅ Factory/registry: memilih implementasi dari config atau input (exporter, payment gateway, LLM provider).
- ✅ Builder: banyak bagian opsional + invariant; test data builder.
- ✅ Shared instance: klien mahal (engine DB, session HTTP) — dibuat sekali di app factory dan di-inject.
- 🚫 Factory untuk class dengan satu implementasi dan tanpa konfigurasi.
- 🚫 Builder untuk object 3-field — pakai dataclass.
- 🚫 Singleton untuk hal yang test butuh berbeda-beda (setting, clock, repository).

## ⚠️ Kesalahan umum

- Pola sebagai dekorasi: `AbstractExporterFactoryManager` untuk dua class.
- Registry yang diam-diam overwrite nama yang ada.
- Builder yang izinkan `build()` return object tidak valid.
- Module-level `settings = Settings()` baca production env var saat test.

:::revoshop
(1) `config/__init__.py` RevoShop punya `config_by_name = {"development": DevelopmentConfig, "production": ProductionConfig}` — itu **registry**. Apa yang terjadi dengan nilai `FLASK_ENV` yang tidak dikenal, dan bagaimana kamu buat error-nya membantu? (2) `create_app()` adalah application **factory** ✅ — tapi `config/base.py` panggil `load_dotenv()` dan baca env var **saat import**. Kenapa itu bisa kejutan test? (3) Cari seeder-nya: apakah `ProductBuilder` buat test data lebih jelas daripada constructor call yang panjang?
:::

## 🏆 Praktik terbaik

- [ ] Simpan logika kreasi di **satu** tempat (factory function, registry atau composition root).
- [ ] Buat error "opsi tidak dikenal" membantu: list pilihan yang valid.
- [ ] Builder return object **immutable** dan validasi di `build()`.
- [ ] Prefer keyword argument + dataclass validation sebelum invent builder.
- [ ] Tidak ada side effect di import time: tidak koneksi, tidak baca env ke global.
- [ ] Ganti singleton dengan **cached factory function** atau **dependency injection**; buat cache resettable untuk test.
- [ ] Nama pola di code review hanya kalau tambah clarity — jangan paksa pola.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke developer junior kenapa "bikin Settings jadi Singleton" membuat test flaky, dan apa yang `@functools.cache` + `cache_clear()` kasih kamu sebaliknya.

## 📐 Rancang

Fitur AI CareerPilot (Phase 3) harus support beberapa LLM provider: Anthropic (default), OpenAI, dan local Ollama model untuk development offline — plus fake untuk test. Provider dan model datang dari setting; setiap provider client mahal dibuat. Rancang bagaimana client yang tepat dibuat, dibagikan dan ditukar di test.

:::quiz
Lihat contoh rancangan yang mungkin

```python
class LLMClient(Protocol):
    def complete(self, messages: list[Message], *, max_tokens: int) -> Completion: ...

LLM_PROVIDERS: dict[str, Callable[[Settings], LLMClient]] = {}

def register_provider(name):                    # registry decorator
    def decorator(factory): LLM_PROVIDERS[name] = factory; return factory
    return decorator

@register_provider("anthropic")
def _anthropic(settings): return AnthropicClient(api_key=settings.llm_api_key, model=settings.llm_model)

@register_provider("ollama")
def _ollama(settings): return OllamaClient(base_url=settings.ollama_url, model=settings.llm_model)

def create_llm_client(settings: Settings) -> LLMClient:   # factory with a helpful error
    try: return LLM_PROVIDERS[settings.llm_provider](settings)
    except KeyError: raise ValueError(f"unknown provider {settings.llm_provider!r} (available: ...)") from None
```

- **Shared**: `create_app()` (composition root) panggil `create_llm_client(settings)` **sekali** dan simpan di service container / `app.extensions`; service terima via constructor. Tidak ada singleton global.
- **Test**: construct service dengan `FakeLLMClient(responses=[...])` langsung — tidak env var, tidak network.
- **Swap**: ubah `LLM_PROVIDER=ollama` di `.env` untuk development offline; production pakai Anthropic.
- **Extend**: tambah provider = satu registered factory function.
:::

### 📝 Checklist review mandiri

- [ ] Satu creation point, didrive oleh setting
- [ ] Klien mahal dibuat sekali tanpa global singleton
- [ ] Test inject fake tanpa patch global
- [ ] Provider baru tidak ubah kode yang ada

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/architecture/d-design-patterns/01-creational" ai="no-ai" title="Registry factory, builder yang validasi dan singleton yang bisa di-test"}
Bangun exporter registry dengan decorator dan error yang membantu, fluent `JobPostingBuilder` yang validasi aturan lintas-field dan return posting yang di-freeze, dan cached `get_settings()` yang test bisa reset — dengan apa pun tidak dibuat di import time.
:::

:::hints
- Registry decorator adalah function yang return function yang terima class.
- Di builder, simpan bagian di private attribute; hanya `build()` yang buat dataclass.
- `raise ValueError(...) from None` sembunyikan internal `KeyError` dari error message chain.
- `@cache` di function no-argument ubah menjadi shared value yang dibuat lazy.
:::

## ✅ Cek cepat

:::quiz
Masalah apa yang registry selesaikan yang factory `if/elif` tidak?

Implementasi baru bisa ditambah dengan daftar mereka, tanpa ubah factory function (open/closed).
:::

:::quiz
Sebutkan dua alasan Singleton klasik membuat testing lebih sulit.

Itu global state tersembunyi yang dibagi test, dan sulit diganti atau di-reset dengan nilai spesifik test (sering dibuat di import time).
:::


## 📚 Lanjut belajar

- [Refactoring.Guru — Creational patterns](https://refactoring.guru/design-patterns/creational-patterns)
- [Python docs: functools.cache](https://docs.python.org/3/library/functools.html#functools.cache)
- [Flask docs: Application Factories](https://flask.palletsprojects.com/en/stable/patterns/appfactories/)

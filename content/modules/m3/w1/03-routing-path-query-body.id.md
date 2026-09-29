---
title: "Routing, Path, Query & Body"
summary: Bagaimana FastAPI membaca request — path parameter dari URL, query parameter dari string setelah ?, dan body Pydantic berjenis dari JSON, masing-masing divalidasi otomatis supaya handler-mu menerima nilai bersih dan berjenis.
sourceHash: 7b41616265b4
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Mendeklarasikan route dengan method HTTP (`@app.get`, `@app.post`, …)
- **Path parameter** — nilai di dalam jalur URL
- **Query parameter** — nilai setelah `?`, dengan default dan opsional
- **Request body** — JSON berjenis lewat model Pydantic
- Bagaimana FastAPI memutuskan yang mana, dan memvalidasi masing-masing

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Route** | URL + method yang dipetakan ke fungsi |
| **Path param** | Nilai di dalam jalur URL (`/items/42`) |
| **Query param** | Nilai setelah `?` (`?q=phone&page=2`) |
| **Request body** | Data JSON yang dikirim bersama request |
| **Default** | Nilai yang dipakai saat param dihilangkan |
| **Optional** | Param yang boleh tak ada (`| None`) |

## 🧠 Ide besarnya

Request seperti **memesan di konter**. **Path** adalah *hidangan mana* di papan menu (`/coffee/latte`). **Query** adalah *penyesuaianmu* (`?size=large&sugar=0`). **Body** adalah *formulir pesanan tertulis* untuk sesuatu yang detail (kue kustom utuh). FastAPI membaca ketiganya dari tempat yang tepat dan mengecek masing-masing terisi benar sebelum dapur mulai.

## ❓ Kenapa ini penting

Tiap endpoint membaca input dari suatu tempat: URL, query string, atau body. Mencampuradukkan ini — atau lupa memvalidasinya — adalah sumber bug klasik dan error `500`. FastAPI mengikat tiap input ke argumen fungsi berjenis dan memvalidasinya, jadi handler-mu selalu menerima nilai bersih dan berjenis benar. Tahu input mana ke mana adalah desain REST inti (dari Modul 2), kini ditegakkan oleh tipe.

## 📖 Langkah demi langkah

### 1. Route dan method

```python
@app.get("/items")          # list
@app.get("/items/{id}")     # read one
@app.post("/items")         # create
@app.put("/items/{id}")     # replace
@app.delete("/items/{id}")  # delete
```

Method REST yang sama yang kamu pakai di Flask — FastAPI hanya mengikatnya ke fungsi berjenis.

### 2. Path parameter

`{name}` di path menjadi argumen berjenis:

```python
@app.get("/items/{item_id}")
def read_item(item_id: int):        # "/items/42" → item_id = 42 (int)
    return {"item_id": item_id}
```

`item_id: int` berarti `/items/abc` ditolak dengan `422` otomatis — nilainya divalidasi dan dikonversi sebelum kodemu jalan.

### 3. Query parameter

Argumen fungsi yang **tidak** di path datang dari query string:

```python
@app.get("/items")
def list_items(q: str | None = None, page: int = 1, limit: int = 20):
    # GET /items?q=phone&page=2  →  q="phone", page=2, limit=20 (default)
    ...
```

- Sebuah **default** (`page: int = 1`) membuat param opsional dengan nilai itu.
- `str | None = None` membuatnya benar-benar opsional (boleh tak ada).
- Tipe divalidasi: `?page=abc` → `422`.

### 4. Request body (Pydantic)

Untuk create/update, ambil model Pydantic — FastAPI membaca dan memvalidasi body JSON:

```python
class ItemIn(BaseModel):
    name: str
    price: float

@app.post("/items")
def create_item(item: ItemIn):      # JSON body → validated ItemIn
    return {"name": item.name, "price": item.price}
```

### 5. Menggabungkan ketiganya

```python
@app.put("/users/{user_id}/items/{item_id}")
def update(user_id: int, item_id: int, item: ItemIn, notify: bool = False):
    # user_id, item_id ← path ; item ← body ; notify ← query (?notify=true)
    ...
```

Aturan FastAPI: **di path → path param; model Pydantic → body; selainnya → query param.** Masing-masing divalidasi oleh tipenya.

### Pilih di mana input berada

| Input | Taruh di |
|---|---|
| Sumber daya mana (sebuah id) | **path** (`/items/{id}`) |
| Filter / paging / opsi | **query** (`?q=&page=`) |
| Data yang dibuat/diperbarui | **body** (model Pydantic) |
| Rahasia/token | header (bukan path/query) |

- ✅ Identifikasi sumber daya dengan path param; filter/page dengan query param.
- ✅ Kirim data create/update sebagai body berjenis, jangan di query string.
- 🚫 Jangan taruh data besar atau sensitif di URL (ia di-log dan di-cache).

## ⚠️ Kesalahan umum

- Mengoper data create di query string alih-alih body JSON.
- Lupa default, membuat query param tak sengaja wajib.
- Menaruh id di body padahal miliknya di path.
- Memakai `POST` untuk mengambil data yang seharusnya dikembalikan `GET` dengan query param.
- Mengirim rahasia di URL, tempat ia bocor ke log dan riwayat.

:::revoshop
Petakan endpoint RevoShop ke tipe param FastAPI. (1) "Ambil produk 42" → path param; tulis signature-nya. (2) "Cari produk, halaman 2, category=books" → query param dengan default; tulis. (3) "Buat order" → body Pydantic; field apa saja, dan kenapa harus di body bukan query?
:::

## 🏆 Praktik terbaik

- [ ] Pakai path param untuk identitas sumber daya, query param untuk filter/paging/opsi.
- [ ] Beri query param opsional default masuk akal; pakai `| None` untuk yang benar-benar opsional.
- [ ] Modelkan data create/update sebagai body Pydantic berjenis.
- [ ] Jaga rahasia dan payload besar keluar dari URL.
- [ ] Ikuti konvensi REST Modul 2 — method dan status code tak berubah.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan path vs query vs body dengan analogi memesan-di-konter (hidangan di papan, penyesuaian, formulir tertulis). Lalu nyatakan aturan FastAPI untuk memutuskan argumen mana yang mana.

## 📐 Rancang

Rancang endpoint lamaran CareerPilot: (a) ambil satu lamaran lewat id, (b) daftar lamaran user difilter status dengan paging, (c) buat lamaran. Untuk masing-masing, putuskan path/query/body dan tulis signature FastAPI-nya.

:::quiz
Tampilkan satu rancangan yang mungkin

```python
# (a) read one — id in the path
@app.get("/applications/{application_id}")
def get_application(application_id: int): ...

# (b) list with filter + paging — query params with defaults
@app.get("/users/{user_id}/applications")
def list_applications(user_id: int, status: str | None = None, page: int = 1, limit: int = 20): ...

# (c) create — typed body
class ApplicationIn(BaseModel):
    company: str
    role: str
    status: str = "saved"

@app.post("/users/{user_id}/applications")
def create_application(user_id: int, body: ApplicationIn): ...
```

- `application_id`, `user_id` mengidentifikasi sumber daya → **path**.
- `status`, `page`, `limit` memfilter/paginasi → **query** dengan default.
- Data lamaran baru → **body** (model Pydantic), karena ia data terstruktur yang dibuat, bukan filter.

**Aturan yang ditunjukkan:** id di path, filter/paging di query, data create/update di body berjenis — masing-masing divalidasi oleh tipenya.
:::

### 📝 Checklist review mandiri

- [ ] Id sumber daya di path
- [ ] Filter/paging di query param dengan default
- [ ] Data create/update di body berjenis
- [ ] Tak ada rahasia atau data massal di URL

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m3/w1/03-params" ai="no-ai" title="Path, query, dan body dalam satu API"}
Bangun aplikasi FastAPI kecil dengan tiga endpoint: baca satu item lewat id path, daftar item dengan filter query + paging (default), dan buat item dari body Pydantic. Tes memeriksa routing yang benar, default, `422` pada tipe path yang salah, dan validasi body.
:::

:::hints
- `@app.get("/items/{item_id}")` dengan `item_id: int`; kembalikan `{"item_id": item_id}`.
- `@app.get("/items")` dengan `q: str | None = None, page: int = 1` — kembalikan nilai yang diterima supaya tes bisa cek default.
- `@app.post("/items")` dengan `body: ItemIn` (model Pydantic `name: str, price: float`).
- Meminta `/items/abc` seharusnya mengembalikan `422` otomatis.
:::

## ✅ Cek cepat

:::quiz
FastAPI melihat argumen fungsi yang tak di path dan bukan model Pydantic. Dari mana ia mendapat nilainya?

Dari **query string** — ia menjadi query parameter (mis. `?page=2`). Aturan FastAPI: nama di path adalah path param, model Pydantic adalah request body, dan selainnya adalah query parameter, masing-masing divalidasi oleh tipenya.
:::

:::quiz
Kenapa data untuk membuat sumber daya harus di request body, bukan query string?

Karena ia data terstruktur, berpotensi besar atau sensitif, dan URL di-log, di-cache, dan dibatasi panjang. Body JSON berjenis menjaganya divalidasi model Pydantic dan keluar dari log, sementara query param ditujukan untuk filter, paging, dan opsi kecil.
:::

## 📚 Lanjut belajar

- [FastAPI: path parameters](https://fastapi.tiangolo.com/tutorial/path-params/)
- [FastAPI: query parameters](https://fastapi.tiangolo.com/tutorial/query-params/)
- [FastAPI: request body](https://fastapi.tiangolo.com/tutorial/body/)

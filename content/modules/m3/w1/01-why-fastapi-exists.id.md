---
title: "Why FastAPI Exists"
summary: Kenapa belajar FastAPI setelah Flask? Ia mengubah type hint Python menjadi validasi otomatis dan docs interaktif, dan mendukung async bawaan — jadi kamu menulis lebih sedikit kode perekat dan menangkap request buruk secara gratis.
sourceHash: d68919aeab22
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa itu FastAPI dan bagaimana ia dibandingkan dengan Flask yang kamu tahu
- Bagaimana **type hint** Python menjadi validasi dan docs otomatis
- Apa yang diberikan dukungan `async` (dan kapan penting)
- Kenapa "lebih sedikit kode perekat" berarti lebih sedikit bug
- Kapan FastAPI sepadan — dan kapan Flask sudah cukup

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **FastAPI** | Framework web Python yang dibangun di sekitar type hint |
| **Type hint** | Menyebut tipe sebuah nilai di kode (`item_id: int`) |
| **Validasi** | Memeriksa data masuk berbentuk benar |
| **OpenAPI** | Deskripsi standar seluruh API-mu |
| **Swagger UI** | Halaman `/docs` interaktif |
| **async** | Mengerjakan hal lain saat menunggu I/O |
| **Kode perekat** | Boilerplate yang kamu tulis untuk menyambung |

## 🧠 Ide besarnya

Flask seperti **dapur polos**: ia memberimu kompor dan membiarkanmu memasak sesukamu — kamu menulis pengecekan pesanan dan kartu menu sendiri. FastAPI seperti **dapur dengan layar pesanan pintar**: kamu mendeskripsikan tiap hidangan sekali (dengan tipe), dan ia otomatis mengecek pesanan dari kesalahan dan mencetak menu untuk pelanggan. Memasak sama, lebih sedikit administrasi.

## ❓ Kenapa ini penting

Di RevoShop (Flask) kamu menulis validasi dengan tangan — memeriksa `price` adalah angka, mengembalikan `400` saat input buruk — dan kamu menjaga docs API tetap sinkron secara manual (atau dengan flask-smorest). Kode perekat tulisan tangan itu tempat bug bersembunyi dan waktu terkuras.

FastAPI membaca **type hint** yang toh akan kamu tulis dan melakukan pekerjaan itu untukmu: ia memvalidasi tiap request terhadap tipemu dan menghasilkan docs interaktif yang selalu benar. Lebih sedikit kode ditulis, lebih sedikit kesalahan, dan halaman `/docs` langsung yang benar-benar bisa dipakai rekan tim.

## 📖 Langkah demi langkah

### 1. Endpoint yang sama, dua framework

Flask (yang kamu tahu):

```python
@app.post("/items")
def create_item():
    data = request.get_json()
    if not isinstance(data.get("price"), (int, float)):   # manual check
        return {"error": "price must be a number"}, 400
    ...
```

FastAPI:

```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float          # the type IS the validation

@app.post("/items")
def create_item(item: Item):
    return {"name": item.name, "price": item.price}
```

Versi FastAPI **tanpa validasi manual**: mendeklarasikan `price: float` membuat FastAPI menolak `"price": "abc"` dengan `422` yang jelas secara otomatis.

### 2. Type hint bekerja ganda

Tipe yang kamu tulis demi keterbacaan kini juga menggerakkan:
- **Validasi** — tipe salah masuk → `422` otomatis dengan pesan membantu.
- **Docs** — tiap field muncul di skema OpenAPI dan `/docs`.
- **Bantuan editor** — autocomplete dan pengecekan tipe pada `item.price`.

Satu deklarasi, tiga manfaat. Itu ide inti FastAPI.

### 3. Docs interaktif otomatis

Jalankan aplikasi dan buka `/docs`: FastAPI menampilkan **Swagger UI** interaktif yang mendaftar tiap endpoint, input dan output-nya, dengan tombol "Try it out". Ia dihasilkan dari kodemu, jadi tak bisa usang. Rekan frontend memakainya untuk melihat persis apa yang harus dikirim.

### 4. Dukungan async, bawaan

FastAPI membuatmu bisa menulis handler `async def`. Saat endpoint kebanyakan **menunggu** I/O (memanggil API lain, database, model AI), `async` membuat server menangani request lain selama menunggu alih-alih memblokir. Untuk layanan berat-I/O atau konkurensi tinggi ini kemenangan throughput nyata. (Kamu akan mendalaminya di Minggu 2.)

```python
@app.get("/weather")
async def weather():
    data = await call_external_api()   # server serves others while waiting
    return data
```

### 5. Jadi haruskah kamu tinggalkan Flask?

Tidak — keduanya bagus. Pilih per proyek:

| Situasi | Pilih |
|---|---|
| Ingin validasi + docs otomatis dari tipe | **FastAPI** |
| Banyak I/O async (API eksternal, panggilan AI) | **FastAPI** |
| Aplikasi Flask yang ada / tim tahu Flask | **Flask** cukup |
| Aplikasi sederhana, sedikit endpoint | Keduanya; pakai yang kamu tahu |

- ✅ Pakai FastAPI saat validasi, docs, dan async berbuah.
- ✅ Terus pakai Flask di tempat yang sudah bekerja — konsepnya transfer.
- 🚫 Jangan tulis ulang aplikasi Flask yang bekerja "cuma karena" FastAPI lebih baru.

## ⚠️ Kesalahan umum

- Mengira FastAPI adalah "Flask dengan runtime lebih cepat" — kemenangan sebenarnya tipe → validasi + docs, bukan kecepatan mentah.
- Menulis validasi manual toh, menduplikasi yang sudah dilakukan Pydantic.
- Memakai `async def` untuk kerja berat-CPU (tak membantu di sana; async untuk menunggu I/O).
- Mengira kamu harus meninggalkan Flask — pengetahuan HTTP/REST dari Modul 2 langsung terbawa.

:::revoshop
API RevoShop adalah Flask + flask-smorest (yang menambah validasi skema dan docs di atas Flask). (1) Temukan di mana RevoShop memvalidasi input dan menghasilkan docs — FastAPI akan melipat keduanya ke type hint. (2) Pilih satu endpoint RevoShop dan sketsa versi FastAPI-nya dengan model Pydantic. (3) Panggilan RevoShop mana yang terikat-I/O (Midtrans, DB) dan bisa diuntungkan `async`?
:::

## 🏆 Praktik terbaik

- [ ] Biarkan type hint + Pydantic melakukan validasi; jangan tulis tangan cek yang disediakan FastAPI.
- [ ] Jaga `/docs` sebagai kontrak API hidup untuk rekan frontend.
- [ ] Pakai `async def` untuk handler terikat-I/O; `def` biasa cukup untuk kerja sederhana/CPU.
- [ ] Pakai ulang pengetahuan REST Modul 2 — status code, method, dan desain identik.
- [ ] Pilih framework per kebutuhan proyek, bukan karena kebaruan.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke developer Flask, pakai analogi dapur-polos vs layar-pesanan-pintar, apa yang diotomasi FastAPI. Lalu sebutkan tiga hal yang diberikan satu type hint di FastAPI.

## 📐 Rancang

Kamu memulai "layanan AI" baru CareerPilot sebagai API segar yang kebanyakan memanggil LLM eksternal dan database. Putuskan apakah FastAPI atau Flask lebih cocok dan benarkan (pikirkan validasi, docs, dan I/O async). Lalu sketsa satu endpoint `POST /suggestions` dengan model request/response Pydantic-nya.

:::quiz
Tampilkan satu rancangan yang mungkin

**Framework:** **FastAPI** cocok di sini — layanan ini terikat-I/O (panggilan LLM + DB), jadi `async` meningkatkan throughput; dan model request/response berjenis memberi validasi otomatis plus `/docs` yang bisa dipakai tim.

**Sketsa endpoint:**
```python
class SuggestionRequest(BaseModel):
    profile_id: int
    job_text: str

class SuggestionResponse(BaseModel):
    summary: str
    score: float

@app.post("/suggestions", response_model=SuggestionResponse)
async def suggest(req: SuggestionRequest):
    result = await call_llm(req.profile_id, req.job_text)
    return SuggestionResponse(summary=result.summary, score=result.score)
```

FastAPI memvalidasi JSON masuk terhadap `SuggestionRequest`, membentuk output dengan `SuggestionResponse`, dan mendokumentasikan keduanya di `/docs` — tanpa kode validasi atau docs manual.

**Aturan yang ditunjukkan:** pilih FastAPI saat validasi berjenis, docs otomatis, dan I/O async semuanya berbuah; desain endpoint (method, status code) adalah REST yang sama yang kamu pelajari di Modul 2.
:::

### 📝 Checklist review mandiri

- [ ] Pilihan dibenarkan oleh validasi/docs/async, bukan hype
- [ ] Request dan response dimodelkan dengan Pydantic
- [ ] Async dipakai karena kerjanya terikat-I/O
- [ ] Desain REST konsisten dengan Modul 2

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m3/w1/01-first-fastapi" ai="no-ai" title="Aplikasi FastAPI pertamamu"}
Bangun aplikasi FastAPI minimal: `GET /health` mengembalikan `{"status": "ok"}` dan `POST /greet` yang mengambil body berjenis `{"name": str}` dan mengembalikan salam. Tes memakai `TestClient` FastAPI dan membuktikan body yang hilang/tak valid ditolak dengan `422` otomatis — tanpa validasi manual.
:::

:::hints
- `app = FastAPI()`; sebuah Pydantic `class GreetIn(BaseModel): name: str`.
- `@app.get("/health")` mengembalikan dict; `@app.post("/greet")` mengambil `body: GreetIn`.
- Tes mengimpor `app` dan memakai `TestClient(app)`; mengirim `{}` ke `/greet` seharusnya memberi status `422` secara gratis.
:::

## ✅ Cek cepat

:::quiz
Di FastAPI, tiga hal apa yang diberikan satu type hint seperti `price: float`?

Validasi otomatis (bukan-angka ditolak dengan `422`), dokumentasi (field muncul di skema OpenAPI dan `/docs`), dan dukungan editor (autocomplete dan pengecekan tipe). Satu deklarasi, tiga manfaat — itu poin FastAPI.
:::

:::quiz
Kapan `async def` benar-benar membantu endpoint FastAPI?

Saat handler kebanyakan **menunggu I/O** — memanggil API lain, database, atau model AI — karena server bisa menangani request lain selama menunggu. Ia tak membantu kerja terikat-CPU, di mana kode sibuk menghitung alih-alih menunggu.
:::

## 📚 Lanjut belajar

- [FastAPI: first steps](https://fastapi.tiangolo.com/tutorial/first-steps/)
- [FastAPI: features](https://fastapi.tiangolo.com/features/)
- [Flask vs FastAPI (official FAQ perspective)](https://fastapi.tiangolo.com/alternatives/)

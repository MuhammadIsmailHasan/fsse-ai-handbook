---
title: "Dokumentasi API dengan OpenAPI (flask-smorest)"
summary: Buat dokumentasi API yang akurat dan interaktif langsung dari kode — spec OpenAPI, Swagger UI, skema dengan penjelasan, error, dan security — sehingga dokumentasi tidak akan ketinggalan dari kode asli.
sourceHash: 34999564b7f4
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa itu **OpenAPI** dan apa yang bisa dilakukannya (dokumentasi, generate klien, testing, mock server)
- **Code-first** vs **design-first** documentation
- Mendokumentasikan API Flask dengan **flask-smorest**: `@blp.arguments`, `@blp.response`, `@blp.alt_response`, docstring, tag
- Menjelaskan **security** (Bearer JWT), **error**, dan **contoh**
- Menjaga dokumentasi tetap akurat: test spec di CI

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **OpenAPI** | Standar file yang menjelaskan setiap endpoint dari sebuah API |
| **Spec** | Berkas deskripsi itu sendiri (JSON atau YAML) |
| **Swagger UI** | Halaman web yang membaca spec supaya orang bisa coba API-nya |
| **Code-first** | Spec dihasilkan dari kode dan skema kamu |
| **Design-first** | Spec ditulis dulu, baru kode menyusul |
| **flask-smorest** | Pustaka Flask yang menghasilkan spec dari route dan skema kamu |
| **Tag** | Pengelompokan endpoint di dokumentasi (jobs, auth) |
| **Security scheme** | Cara autentikasi dijelaskan di dokumentasi (Bearer JWT) |
| **Contract** | Kesepakatan antara backend dan klien tentang request dan response |

## 🧠 Ide besarnya

:term[OpenAPI]{bahasa="OpenAPI — standar format (JSON/YAML) untuk mendeskripsikan endpoint, parameter, dan respons sebuah API"} adalah **menu yang bisa dibaca mesin** untuk API kamu: setiap hidangan (endpoint), bahan-bahannya (parameter dan body), apa yang sampai ke meja (response), dan peringatannya (error, autentikasi).

Orang membacanya lewat tools seperti **Swagger UI**; mesin memakainya untuk generate kode klien, mock server, dan test.

Menu terbaik **dicetak dari resep asli dapur**, jadi tidak bisa advertise hidangan yang sudah tidak dibuat lagi. Itu dokumentasi code-first.

## ❓ Kenapa ini penting

Tim frontend, mobile, dan partner perlu tahu persis cara memanggil API kamu. Dokumentasi yang ditulis tangan di wiki akan ketinggalan dalam hitungan minggu. Spec yang dihasilkan dari skema yang sama yang sudah validate request tetap selalu akurat, dan tools bisa memakainya otomatis.

Tanpa ini (atau dengan dokumentasi yang ditulis tangan):

- README bilang `POST /jobs` butuh `name`; kode mengharap `title` → frontend debug berjam-jam.
- Tidak ada yang tahu error apa saja yang bisa dikembalikan endpoint, jadi klien tunjukkan "Ada yang salah" untuk semuanya.
- Developer baru baca kode controller untuk cari tahu parameternya.
- Recruiter yang buka portfolio API kamu tidak ada cara untuk mencobanya.

## 📖 Langkah demi langkah

### 1. Bagian utama spec

```yaml
openapi: 3.0.3
info: { title: CareerPilot API, version: v1 }
paths:
  /api/v1/companies:
    post:
      tags: [companies]
      summary: Create a company
      security: [{ BearerAuth: [] }]
      requestBody:
        content:
          application/json:
            schema: { $ref: '#/components/schemas/CompanyCreate' }
      responses:
        '201': { description: Created, content: { application/json: { schema: { $ref: '#/components/schemas/Company' } } } }
        '409': { description: A company with this name already exists }
components:
  schemas: { CompanyCreate: {…}, Company: {…} }
  securitySchemes:
    BearerAuth: { type: http, scheme: bearer, bearerFormat: JWT }
```

### 2. Code-first vs design-first

| Pendekatan | Caranya | Terbaik untuk |
|---|---|---|
| **Code-first** | generate spec dari kode (flask-smorest, FastAPI) | tim kecil/menengah, iterasi cepat — materi ini |
| **Design-first** | tulis spec dulu, review, baru implement (dan generate stub) | API publik, banyak pengguna, kontrak terpisah |

### 3. Setup flask-smorest

```python
from flask_smorest import Api

app.config.update(
    API_TITLE="CareerPilot API",
    API_VERSION="v1",
    OPENAPI_VERSION="3.0.3",
    OPENAPI_URL_PREFIX="/docs",
    OPENAPI_JSON_PATH="openapi.json",
    OPENAPI_SWAGGER_UI_PATH="/swagger-ui",
    OPENAPI_SWAGGER_UI_URL="https://cdn.jsdelivr.net/npm/swagger-ui-dist/",
)
api = Api(app)
api.spec.components.security_scheme("BearerAuth", {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"})
```

Buka `http://localhost:5091/docs/swagger-ui` untuk coba endpoint di browser.

### 4. Dokumentasi endpoint dengan skema yang sudah ada

Ini adalah hadiah dari materi 03: skema yang validate request juga menjelaskannya di dokumentasi, jadi dua-duanya tidak pernah bisa berbeda.

```python
from flask.views import MethodView
from flask_smorest import Blueprint, abort

blp = Blueprint("companies", __name__, url_prefix="/api/v1/companies", description="Companies you apply to")

@blp.route("")
class Companies(MethodView):
    @blp.arguments(CompanyQuerySchema, location="query")
    @blp.response(200, CompanySchema(many=True))
    def get(self, query):
        """List companies

        Sorted by name. Use `q` to search by name (case-insensitive).
        """
        return company_service().list(query)

    @blp.arguments(CompanyCreateSchema)
    @blp.response(201, CompanySchema)
    @blp.alt_response(409, schema=ErrorSchema, description="A company with this name already exists")
    @blp.doc(security=[{"BearerAuth": []}])
    def post(self, data):
        """Create a company"""
        return company_service().create(data)
```

- `@blp.arguments` **validate** input dan **dokumentasi**-nya — satu sumber kebenaran.
- `@blp.response` **serialize** output dengan skema dan dokumentasi-nya.
- Baris pertama docstring menjadi `summary`; sisanya menjadi `description`.
- `@blp.alt_response` dokumentasikan hasil lain (error).

### 5. Deskripsi dan contoh di skema

```python
class CompanyCreateSchema(Schema):
    name = fields.String(
        required=True,
        validate=validate.Length(min=1, max=200),
        metadata={"description": "Company name, unique (case-insensitive)", "example": "Kopi Data"},
    )
```

Contoh yang bagus adalah cara tercepat bagi developer frontend untuk pahami sebuah field.

### 6. Error dalam format kamu sendiri

Default validation error flask-smorest terlihat seperti `{"code": 422, "errors": {"json": {...}}, "status": "..."}`. Daftar handler untuk tetap dengan **envelope kamu**, dan dokumentasikan `ErrorSchema` untuknya:

```python
@app.errorhandler(422)
def validation_error(error):
    messages = getattr(error, "data", {}).get("messages", {})     # {"json": {"name": ["…"]}, "query": {...}}
    fields = {f"{location}.{name}": msgs[0] for location, errs in messages.items() for name, msgs in errs.items()}
    return {"error": {"code": "validation_failed", "message": "Some fields are invalid", "fields": fields}}, 422
```

### 7. Test spec-nya

Test yang gagal saat spec berubah mengubah dokumentasi jadi sesuatu yang pipeline lindungi, bukan sesuatu yang orang ingat untuk update.

```python
def test_openapi_spec(client):
    spec = client.get("/docs/openapi.json").get_json()
    post = spec["paths"]["/api/v1/companies"]["post"]
    assert {"201", "409", "422"} <= set(post["responses"])
    assert post["security"] == [{"BearerAuth": []}]
```

Jalankan juga **spec linter** (misalnya Spectral, Redocly) di CI, dan pertimbangkan **contract test** (misalnya Schemathesis generate request dari spec kamu dan cek response cocok).

### 8. Apa yang bisa spec buka

| Kegunaan | Contoh tool |
|---|---|
| Dokumentasi interaktif | Swagger UI, Redoc, Scalar |
| Generate klien bertipe | `openapi-typescript` untuk aplikasi Next.js kamu (Modul 4), openapi-generator |
| Mock server sebelum backend ada | Prism |
| Contract / fuzz testing | Schemathesis |
| Import ke API klien | Postman, Bruno, Insomnia |
| AI tools | agent dan LLM "tool" definition bisa dihasilkan dari OpenAPI (Modul 7) |

### Pilih setup kamu

Setiap pilihan di sini adalah trade-off:

| Pilihan | ✅ | ❌ |
|---|---|---|
| Generate code-first | tidak pernah ketinggalan; usaha rendah | kualitas spec bergantung anotasi kode |
| Design-first | kontrak disepakati sebelum coding; kerjakan parallel | harus jaga kode tetap sinkron (codegen/contract test) |
| Dokumentasi markdown ditulis tangan | fleksibel narasi | selalu ketinggalan |
| Swagger UI publik di production | mudah explore | buka permukaan attack — lindungi atau matikan untuk API internal |
| Contoh kaya | onboarding lebih cepat | harus jaga tetap realistis |

- ✅ Setiap HTTP API yang punya lebih dari satu pengguna (termasuk "kamu di masa depan" dan frontend kamu).
- ✅ Tambahkan docstring, contoh, response error, dan security ke setiap endpoint.
- 🚫 Jangan expose dokumentasi endpoint admin internal secara publik.
- 🚫 Jangan dokumentasi field atau error yang kode tidak benar-benar return.

## ⚠️ Kesalahan umum

- Hanya dokumentasi happy path.
- Dokumentasi skema yang beda dari apa yang endpoint return (bypass `@blp.response`).
- Security declaration hilang → "Try it out" gagal dengan membingungkan.
- Biarkan default placeholder untuk judul/versi.
- Expose endpoint admin internal lewat dokumentasi secara publik.

:::revoshop
RevoShop sudah serve dokumentasi: `config/base.py` atur `OPENAPI_URL_PREFIX = '/docs'` dan Swagger UI, dan `create_app()` tambahkan security scheme `BearerAuth` dengan deskripsi *"Paste the access_token returned by /api/v1/auth/login"*. Jalankan aplikasi dan buka `/docs/swagger-ui`: (1) Apakah **semua** endpoint tunjukkan response error mereka (`404`, `409`, `422`), atau hanya success? (2) Apakah endpoint terlindungi tunjukkan ikon lock? (3) Apakah skema punya deskripsi field dan contoh? (4) Apakah format error yang didokumentasikan cocok dengan apa yang `app/errors.py` kamu benar-benar return? Pilih tiga endpoint terlemah dan improve dokumentasinya — lalu tambahkan test yang check spec-nya.
:::

## 🏆 Praktik terbaik

- [ ] Generate spec dari **skema yang sama** yang validate dan serialize (code-first) — atau enforce design-first dengan contract test.
- [ ] Setiap operasi: **summary**, **description**, **tag**, skema request, response **success** dan **error**.
- [ ] Tambahkan **deskripsi dan contoh** ke field skema.
- [ ] Deklarasikan **security scheme** dan tandai operasi yang terlindungi.
- [ ] Jaga satu **error schema** dan dokumentasikan di setiap endpoint yang bisa gagal.
- [ ] **Test spec** di CI (structure test, linter, optional contract test).
- [ ] Versi API (`/api/v1`) dan publikasikan changelog untuk breaking change.
- [ ] Lindungi atau matikan Swagger UI di production untuk non-public API.
- [ ] Generate klien bertipe dari spec untuk frontend kamu.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke non-programmer apa itu OpenAPI spec dan kenapa generate dokumentasi dari kode lebih baik daripada tulis di Google Doc.

## 📐 Rancang

Untuk `POST /api/v1/applications/{id}/status` dari CareerPilot, tulis dokumentasi yang kamu inginkan: summary, description, tag, path parameter, request body (dengan contoh), semua response (dengan deskripsi dan skema apa), dan security. Lalu daftar automated check apa yang bisa tangkap dokumentasi ketinggalan dari kode.

:::quiz
Lihat contoh rencana dokumentasi

- **Summary:** Change an application's status
- **Description:** Moves the application through its pipeline. Allowed transitions: applied → interview/rejected/withdrawn; interview → interview/offer/rejected/withdrawn; offer → accepted/declined. Records a history entry.
- **Tag:** applications · **Security:** BearerAuth
- **Path param:** `id` (integer, the application id)
- **Body:** `StatusChangeSchema` — `status` (enum of allowed values, example `"interview"`), optional `note` (≤ 500 chars, example `"Technical round scheduled"`)
- **Response:** `200` `ApplicationSchema` · `401` `ErrorSchema` (missing/expired token) · `404` `ErrorSchema` (not found or not yours) · `409` `ErrorSchema` (`invalid_transition`) · `422` `ErrorSchema` (`validation_failed`)

**Cek untuk ketinggalan:** pytest yang load `/docs/openapi.json` dan assert response dan security ini; Schemathesis jalankan terhadap spec di CI; TypeScript generate tipe di frontend gagal compile saat field berubah.
:::

### 📝 Checklist review mandiri

- [ ] Response error didokumentasikan, bukan hanya 200
- [ ] Business rule (allowed transition) ada di description
- [ ] Field request punya contoh
- [ ] Ada automated drift check

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m2/w5/07-openapi-docs" ai="no-ai" title="A self-documenting companies API"}
Build a small companies API with **flask-smorest** (in memory, no database): documented query and body schemas with descriptions and examples, success and error responses, a Bearer security scheme on protected operations, tags, docstring summaries, and a custom `422` handler that keeps the handbook's error envelope. The tests read your `/docs/openapi.json` and check it matches what the endpoints really do.
:::

:::hints
- `api.spec.components.security_scheme("BearerAuth", {...})` right after creating `Api(app)`.
- `@blp.alt_response(404, schema=ErrorSchema, description="...")` for each error.
- `metadata={"description": "...", "example": ...}` on schema fields.
- The `422` handler receives an exception whose `.data["messages"]` holds `{location: {field: [messages]}}`.
:::

### 🏆 Tantangan lebih jauh

Jalankan [Schemathesis](https://schemathesis.readthedocs.io/) terhadap aplikasi yang jalan (`uvx schemathesis run http://localhost:5091/docs/openapi.json`) dan fix apa yang ditemukan.

## ✅ Cek cepat

:::quiz
Keuntungan utama generate OpenAPI dari kode apa?

Dokumentasi berasal dari skema dan dekorator yang sama yang validate dan serialize request sungguhan, jadi tidak bisa diam-diam ketinggalan dari implementasi.
:::

:::quiz
Sebutkan tiga hal yang OpenAPI spec buka selain dokumentasi yang bisa dibaca manusia.

Generate klien bertipe, mock server, contract/fuzz testing, import ke klien API atau gateway, dan generate AI tool definition.
:::


## 📚 Lanjut belajar

- [OpenAPI Specification](https://spec.openapis.org/oas/latest.html)
- [flask-smorest documentation](https://flask-smorest.readthedocs.io/)
- [Schemathesis — property-based API testing](https://schemathesis.readthedocs.io/)

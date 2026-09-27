---
title: "Konsep REST & Endpoint GET"
summary: Rancang API berbasis resource dengan URL yang jelas, bangun endpoint GET dengan filter, sorting, dan pagination yang aman — dengan balasan konsisten yang disukai klien.
sourceHash: 0580fdbe4915
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- **REST** dalam praktik: resource, representasi, method, dan statelessness
- Merancang **URL** dan konvensi penamaan
- Method **aman** dan **idempotent**
- Endpoint GET untuk **kumpulan item** dan **satu resource**
- **Filter**, **sorting** (dengan daftar izin), **pagination** (offset dan keyset), dan **envelope** balasan
- Dasar versioning dan caching

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **REST** | Gaya desain API: data adalah resource dengan URL, dimanipulasi dengan method HTTP standar |
| **Resource** | Satu objek yang disediakan API (pekerjaan, pengguna) |
| **Endpoint** | Satu URL + method yang API jawab |
| **Safe method** | Permintaan yang tidak mengubah data (`GET`) |
| **Idempotent** | Diulang beberapa kali punya hasil yang sama seperti sekali (`PUT`, `DELETE`) |
| **Stateless** | Server tidak mengingat hal apapun antar permintaan; setiap permintaan membawa apa yang ia butuhkan |
| **Envelope** | Bentuk tetap yang setiap balasan pakai (`data`, `meta`, `error`) |
| **Pagination** | Membagi hasil menjadi halaman-halaman |
| **Keyset pagination** | Pagination dengan "mulai dari item ini" daripada "lewati 5.000 baris" |
| **Whitelist** | Daftar tetap nilai yang boleh dipakai (field untuk sorting) |

## 🧠 Ide besarnya

:term[REST]{bahasa="REST — gaya desain API yang memodelkan data sebagai resource dengan URL, dimanipulasi lewat method HTTP standar"} mengobati API seperti **katalog perpustakaan**:

- Setiap hal — buku, anggota — adalah **resource** dengan alamat: `/books/42`.
- Kamu bekerja dengan alamat itu memakai sedikit **kata kerja standar**: baca (`GET`), tambah (`POST`), ganti sepenuhnya (`PUT`), ubah sebagian (`PATCH`), hapus (`DELETE`).
- Siapa pun yang tahu HTTP bisa menebak cara pakai API-mu **tanpa baca kode**.

## ❓ Kenapa ini penting

Frontend, aplikasi mobile, partner, dan service lain semua bicara ke backend-mu. Desain yang diprediksi berarti bug lebih sedikit, dokumentasi lebih sedikit ditulis, caching lebih mudah, dan klien bisa dibangun bersamaan dengan backend.

Desain yang tidak konsisten terlihat seperti ini:

```text
GET  /getJobs?cityName=Jakarta
POST /job/create
GET  /api/job_detail?jobid=42
POST /deleteJobById
GET  /jobs/list?page=1&pageSize=100000
```

Sekarang setiap endpoint perlu dokumentasinya sendiri, klien menebak salah, permintaan `GET` mengubah data — dan browser senang cache atau pre-fetch itu — dan ada yang minta 100.000 baris sekaligus.

## 📖 Cara kerjanya, langkah demi langkah

### 1. Resource dan URL

| Aturan | ✅ | ❌ |
|---|---|---|
| Kata benda, bukan kerja | `/api/v1/applications` | `/api/v1/getApplications` |
| Kumpulan jamak | `/applications`, `/applications/42` | `/application/42` |
| Sarang hanya untuk milik | `/applications/42/interviews` | `/users/7/applications/42/interviews/3/notes` |
| Huruf kecil, tanda hubung | `/job-listings` | `/JobListings`, `/job_listings` |
| Versi di jalan (atau header) | `/api/v1/...` | ubah besar tanpa versi |
| Aksi yang tidak cocok CRUD | `POST /applications/42/status` atau `POST /payments/9/refund` | `GET /refund?id=9` |

### 2. Method: aman dan idempotent

Dua janji ini biar jaringan bisa coba ulang dengan aman: tombol lift yang bisa ditekan dua kali tanpa panggil dua lift.

| Method | Pakai untuk | Aman (tidak ubah)? | Idempotent (efek sama kalau diulang)? |
|---|---|---|---|
| `GET` | baca | ✅ | ✅ |
| `POST` | buat / aksi | ❌ | ❌ (kecuali kamu pakai idempotency keys) |
| `PUT` | ganti sepenuhnya | ❌ | ✅ |
| `PATCH` | ubah sebagian | ❌ | biasanya ✅ dalam praktik |
| `DELETE` | hapus | ❌ | ✅ |

Method **aman** tidak boleh ubah data: crawlers, browsers dan caches panggil `GET` bebas. Method **idempotent** boleh dicoba ulang setelah timeout jaringan tanpa ubah dua kali.

### 3. Statelessness

Setiap permintaan bawa semua yang dibutuhkan (token auth, parameter). Server tidak ingat "halaman sebelumnya kamu lihat" — makanya parameter pagination dan token dikirim setiap kali (dan kenapa scaling horizontal jalan — Architecture Stage B).

### 4. Response envelope

Pilih satu bentuk dan pakai di mana-mana:

```json
{
  "data": [ { "id": 42, "title": "Backend Engineer" } ],
  "meta": { "page": 2, "per_page": 20, "total": 134, "total_pages": 7 },
  "links": { "self": "/api/v1/jobs?page=2", "next": "/api/v1/jobs?page=3", "prev": "/api/v1/jobs?page=1" }
}
```

```json
{ "data": { "id": 42, "title": "Backend Engineer" } }
```

```json
{ "error": { "code": "job_not_found", "message": "Job 42 not found" } }
```

Klien bisa tulis **satu** handler generic untuk sukses, pagination dan error.

### 5. Filtering

```text
GET /api/v1/jobs?city=jakarta&remote=true&min_salary=10000000&q=engineer
```

- Validasi dan **konversi** setiap parameter (`remote` harus `true`/`false`; `min_salary` integer ≥ 0).
- Nilai tidak dikenal atau tidak valid → `422` dengan pesan jelas (jangan diam-diam abaikan typo seperti `?reomte=true`).
- Terjemah filter ke kondisi query **parameterized** di repository.

### 6. Sorting dengan whitelist

```text
GET /api/v1/jobs?sort=-salary_max,title
```

`-` berarti menurun. **Jangan pernah** lewat input pengguna langsung ke `ORDER BY`:

```python
SORTABLE = {"posted_on": Job.posted_on, "salary_max": Job.salary_max, "title": Job.title}

def order_by_clauses(sort: str):
    clauses = []
    for part in sort.split(","):
        descending = part.startswith("-")
        column = SORTABLE.get(part.lstrip("-"))
        if column is None:
            raise ValidationFailed({"sort": f"unknown field {part!r}"})
        clauses.append(column.desc() if descending else column.asc())
    clauses.append(Job.id.desc())           # always a unique tie-breaker for stable pages
    return clauses
```

### 7. Offset pagination

```python
per_page = min(max(per_page, 1), 100)       # enforce limits
stmt = base.order_by(*clauses).limit(per_page).offset((page - 1) * per_page)
total = db.session.scalar(select(func.count()).select_from(base.subquery()))
```

- ✅ sederhana; "lompat ke halaman 7"; hitung total
- ❌ `OFFSET 100000` lambat (database tetap jalan lewat baris itu); baris bergeser kalau data baru datang

### 8. Keyset (cursor) pagination

Offset paging seperti minta petugas perpustakaan hitung lewat 5.000 buku setiap kali; keyset paging seperti bilang "lanjut dari buku ini" — jauh lebih cepat, dan tidak ada yang terlewat kalau baris baru datang.

```text
GET /api/v1/jobs?limit=20                      → ..., "next_cursor": "eyJwIjoiMjAyNi0wOS0xMCIsImkiOjQyfQ"
GET /api/v1/jobs?limit=20&cursor=eyJwIjoiMjAy…
```

```python
# cursor decodes to (last_posted_on, last_id)
stmt = (
    select(Job)
    .where(tuple_(Job.posted_on, Job.id) < (last_posted_on, last_id))
    .order_by(Job.posted_on.desc(), Job.id.desc())
    .limit(limit)
)
```

- ✅ cepat di kedalaman apa pun (pakai index `(posted_on, id)`), stabil dengan penyisipan
- ❌ tidak ada "lompat ke halaman 37", tidak ada hitung total murah
- Enkrip cursor (missal base64 JSON) supaya klien anggap **opaque**

Feed infinite scroll dan export besar pakai keyset; tabel admin dengan nomor halaman sering pakai offset.

### 9. Satu resource

```python
@jobs_bp.get("/<int:job_id>")
def get_job(job_id: int):
    job = job_service().get(job_id)            # raises JobNotFound → 404 via the error handler
    return {"data": JobSchema().dump(job)}
```

### 10. Caching headers (pratinjau)

Balasan `GET` bisa masukkan `Cache-Control` dan `ETag` supaya klien dan CDN hindari download ulang data tidak berubah (`304 Not Modified`). Jangan cache balasan pribadi per-pengguna secara public.

### Pilih setup-mu

Setiap pilihan adalah trade-off:

| Pilihan | ✅ | ❌ |
|---|---|---|
| REST (resource + method) | diprediksi, bisa cache, alat bagus | tidak nyaman untuk aksi kompleks atau baca sarang dalam |
| GraphQL (Architecture Stage F) | klien pilih field, lebih sedikit roundtrip | cache dan otorisasi lebih keras; risiko N+1 |
| RPC style (`POST /doSomething`) | sederhana untuk aksi | tidak konsisten, cache jelek |
| Offset pagination | nomor halaman, total | halaman dalam lambat, tidak stabil |
| Keyset pagination | cepat, stabil | tidak ada akses halaman acak |
| Envelope (`data/meta/error`) | klien konsisten | payload sedikit lebih besar |

- ✅ REST untuk kebanyakan API gaya CRUD bisnis.
- ✅ Keyset pagination untuk kumpulan besar atau yang banyak tambah (feed, log, listing).
- 🚫 Jangan kembalikan kumpulan tanpa batas — selalu pagination.
- 🚫 Jangan pakai `GET` untuk apa pun yang ubah state.
- 🚫 Jangan buka nama kolom database atau id internal yang mungkin ingin kamu ubah tanpa versioning.

## ⚠️ Kesalahan umum

- Kata kerja di URL; singular/plural campur.
- `ORDER BY` dibangun dari string query mentah (SQL injection + crash).
- Tidak ada maximum `per_page`.
- Pagination tanpa kolom unik tie-breaker → baris terulang atau hilang antar halaman.
- Kembalikan `200` dengan `{"error": ...}`.

:::revoshop
Di `app/routes/products.py` RevoShop, endpoint list baca parameter query `ProductQuerySchema` (`name`, `category_id`, `seller_id`, `min_price`, `max_price`, `sort_by`, `order`, `page`, `limit`) dan kembalikan `make_response(..., pagination=paginate_meta(paginated))`. Buka `app/schemas/product_schema.py` dan `app/utils/http.py`: (1) `sort_by` dibatasi ke whitelist (missal `validate.OneOf`)? (2) `limit` ada cap? (3) Apa metadata pagination-mu? (4) Ada unik tie-breaker di ordering? Bandingkan envelope-mu (`make_response`) dengan pelajaran ini — developer frontend nemuin itu konsisten di setiap endpoint?
:::

## 🏆 Praktik terbaik

- [ ] Kata benda **jamak**, jalan lowercase-hyphen, `/api/v1` versioning.
- [ ] `GET` **aman**; desain tulis menjadi **idempotent** kalau bisa.
- [ ] Satu **envelope konsisten** untuk data, metadata pagination dan error.
- [ ] **Validasi dan konversi** semua parameter query; tidak dikenal/tidak valid → `422`.
- [ ] **Whitelist** field yang bisa sort/filter; selalu tambah unik **tie-breaker** ke ordering.
- [ ] Paksa **maximum page size** (missal 100) dan default masuk akal (missal 20).
- [ ] Pakai **keyset pagination** untuk kumpulan besar atau yang tumbuh cepat; cursor opaque.
- [ ] Index kolom di filter dan sort order (pelajaran Week 2 lesson 06).
- [ ] Kembalikan **404** untuk resource yang tidak ada **atau** tidak terlihat ke pemanggil.
- [ ] Dokumentasikan parameter dan balasan dengan OpenAPI (pelajaran 07).

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke teman developer frontend kenapa endpoint list pekerjaan kamu hanya kembalikan paling banyak 100 item per permintaan, dan perbedaan antara pagination nomor halaman dan pagination cursor "load lebih banyak".

## 📐 Rancang

Rancang `GET /api/v1/applications` untuk CareerPilot: filter (status — boleh banyak, perusahaan, rentang tanggal aplikasi, cari teks di role), opsi sorting, gaya pagination, envelope balasan, error validasi, dan index database yang diperlukan query. Tunjukkan satu contoh permintaan dan balasan.

:::quiz
Tunjukkan rancangan yang mungkin

**Permintaan:** `GET /api/v1/applications?status=applied,interview&company_id=12&applied_from=2026-08-01&applied_to=2026-09-13&q=engineer&sort=-applied_on&limit=20&cursor=…`

**Aturan:** nilai `status` dari set yang boleh; tanggal ISO format dengan `applied_from <= applied_to`; `q` ≥ 2 karakter; `sort` di {`applied_on`, `-applied_on`, `company`, `status`} dengan tie-breaker `id`; `limit` 1–100 (default 20); keyset cursor untuk sort default (offset boleh untuk sort lain di tampilan admin).

**Balasan:**
```json
{
  "data": [{"id": 88, "company": {"id": 12, "name": "Kopi Data"}, "role_title": "Analytics Engineer", "status": "interview", "applied_on": "2026-09-02"}],
  "meta": {"limit": 20, "next_cursor": "eyJkIjoiMjAyNi0wOS0wMiIsImkiOjg4fQ"}
}
```

**Error:** `422 {"error": {"code": "invalid_query", "fields": {"status": "unknown value 'hired'"}}}`

**Index:** `(user_id, applied_on DESC, id DESC)` untuk listing default; `(user_id, status)`; trigram index pada `role_title` kalau cari menjadi lambat.
:::

### 📝 Checklist review mandiri

- [ ] Setiap parameter divalidasi dengan error jelas
- [ ] Sorting di-whitelist dengan tie-breaker
- [ ] Ukuran halaman terbatas; gaya pagination cocok dengan use case
- [ ] Index cocok dengan query default

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m2/w5/01-rest-get" ai="no-ai" title="Filter, sort dan paginate daftar pekerjaan"}
Implementasikan `GET /api/v1/jobs` dan `GET /api/v1/jobs/<id>` di PostgreSQL nyata: filter tervalidasi, multi-field sorting di-whitelist dengan tie-breaker, offset pagination dengan `meta` dan `links`, dan **keyset** pagination dengan cursor opaque. Test bandingkan halaman dengan data seed dan coba parameter sort gaya injection.
:::

:::hints
- Parse dan validasi parameter query ke dict biasa dulu; bangun query kedua.
- `tuple_(Job.posted_on, Job.id) < (posted_on, job_id)` untuk keyset "lebih lama dari".
- Enkrip cursor dengan `base64.urlsafe_b64encode(json.dumps(...).encode())`; tolak cursor yang tidak dekode.
- Tie-breaker untuk setiap sort adalah `id` dalam **arah yang sama seperti field sort terakhir**.
:::

### 🏆 Tujuan tantangan

Tambahkan header `ETag` (hash dari isi balasan) dan kembalikan `304 Not Modified` kalau `If-None-Match` permintaan cocok.

## ✅ Cek cepat

:::quiz
Apa perbedaan antara aman dan idempotent?

Method aman tidak ubah state server (GET). Method idempotent mungkin ubah state, tapi ulangi punya efek yang sama seperti sekali (PUT, DELETE).
:::

:::quiz
Kenapa pagination order harus sertakan kolom unik seperti `id`?

Tanpa unik tie-breaker, baris dengan nilai sort sama bisa muncul dalam urutan apa pun, jadi mereka mungkin terulang atau terlewat antar halaman.
:::

:::quiz
Kenapa whitelist field sort daripada lewatkan `?sort=` ke query?

Input pengguna di `ORDER BY` buka SQL injection atau crash, dan buka kolom (atau sort tidak-indexed) yang tidak pernah ingin kamu dukung.
:::


## 📚 Lanjut belajar

- [MDN: HTTP request methods](https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods)
- [Microsoft REST API Guidelines](https://github.com/microsoft/api-guidelines)
- [Use The Index, Luke: Paging through results (keyset)](https://use-the-index-luke.com/no-offset)

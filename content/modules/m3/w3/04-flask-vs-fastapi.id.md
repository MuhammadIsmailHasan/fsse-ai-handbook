---
title: "Flask vs FastAPI Decision Guide"
summary: Pilih antara Flask dan FastAPI dengan alasan, bukan tren — apa kelebihan masing-masing, biaya nyata menulis ulang, cara pindah satu endpoint demi satu, dan cara menjelaskan pilihanmu di wawancara.
sourceHash: 2b5764d3ba4c
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa yang dikerjakan baik oleh Flask dan FastAPI
- Pertanyaan yang menentukan pilihan
- Kenapa "FastAPI lebih cepat" biasanya alasan yang salah
- Cara pindah dari Flask ke FastAPI **satu endpoint demi satu**
- Cara menjelaskan pilihan itu di wawancara

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **WSGI** | Standar web Python lama: satu request, satu worker dalam satu waktu |
| **ASGI** | Standar lebih baru yang mendukung `async` dan streaming |
| **Batteries included** | Banyak fitur sudah ada bersama framework |
| **Micro-framework** | Inti kecil; sisanya kamu tambah sendiri |
| **Biaya migrasi** | Waktu, bug dan risiko pindah ke sesuatu yang baru |
| **Strangler pattern** | Mengganti sistem lama sepotong demi sepotong, bukan sekaligus |
| **Trade-off** | Kamu mendapat satu hal dan melepas hal lain |

## 🧠 Ide besarnya

Memilih framework itu seperti memilih **kendaraan**. Motor (Flask) ringan, kamu sudah mahir, dan muat di gang kecil. Mobil boks (FastAPI) punya ruang muat lebih besar dan GPS bawaan (validasi dan dokumen). Tak ada yang "lebih baik". Yang tepat bergantung pada jalan dan muatannya. Dan kalau motormu sudah cukup untuk rutemu, membeli mobil boks "karena mobil boks itu modern" hanya pemborosan.

## ❓ Kenapa ini penting

Tim kehilangan berbulan-bulan untuk penulisan ulang yang sebenarnya tak perlu, dan juga merilis kode lambat dan menyakitkan karena bertahan dengan alat yang sudah tak cocok. Engineer yang baik bisa mengatakan **kenapa** sebuah alat cocok, dan berapa harganya. Ini juga muncul di wawancara dan di pekerjaan nyata: kamu akan membaca kode Flask di kantor, dan kamu akan diminta memulai layanan FastAPI. Kamu perlu berpindah di antara keduanya tanpa drama.

## 📖 Langkah demi langkah

### 1. Endpoint yang sama di keduanya

Flask (kamu menulis ini di RevoShop):

```python
@app.post("/notes")
def create_note():
    data = request.get_json()
    if not data or "text" not in data:
        return {"error": "text is required"}, 400
    note = repo.add(data["text"])
    return note, 201
```

FastAPI (yang kamu tulis di module ini):

```python
class NoteIn(BaseModel):
    text: str

@app.post("/notes", status_code=201)
def create_note(body: NoteIn, repo: NoteRepo = Depends(get_repo)):
    return repo.add(body.text)
```

Di FastAPI, type hint melakukan validasi, mengembalikan `422` yang jelas untuk input buruk, dan mengisi dokumen otomatis. Di Flask kamu menambahkannya sendiri, biasanya dengan Marshmallow atau library sejenis.

### 2. Kelebihan masing-masing

| | Flask | FastAPI |
|---|---|---|
| Gaya | inti kecil, tambah yang perlu | validasi, dokumen dan DI bawaan |
| Validasi | library tambahan (Marshmallow, Pydantic) | Pydantic bawaan |
| Dokumen API | library tambahan (flask-smorest, apispec) | OpenAPI otomatis di `/docs` |
| `async` | bisa, tapi bukan desain utama | kelas satu (ASGI) |
| Streaming (AI) | bisa, butuh lebih hati-hati | sederhana dengan `StreamingResponse` |
| Halaman HTML (Jinja) | kuat, matang | bisa, bukan fokusnya |
| Ekosistem | sangat besar, ekstensi bertahun-tahun | lebih baru, tumbuh cepat |
| Usia di codebase nyata | di mana-mana | umum di layanan baru, terutama AI |

### 3. "FastAPI lebih cepat" adalah alasan yang lemah

Benchmark "hello world" menunjukkan selisih. App nyatamu menghabiskan waktu **menunggu database dan layanan lain**, bukan di framework. Satu query SQL lambat berharga seribu kali lipat dibanding pilihan framework. `async` hanya membantu bila kamu banyak menunggu secara paralel (kamu sudah melihatnya di lesson async). Pilih FastAPI untuk validasi, dokumen dan I/O async, bukan demi angka benchmark.

### 4. Pertanyaan yang menentukan

Tanyakan berurutan:

1. **Apakah kamu me-render halaman HTML di server?** Flask (atau Django) lebih cocok.
2. **Apakah sudah ada app Flask yang jalan?** Maka kamu butuh alasan nyata untuk pindah. Penulisan ulang ada biayanya dan tak memberi user sesuatu yang baru.
3. **Apakah layanan menunggu banyak panggilan lambat, atau men-stream token AI?** FastAPI membantu.
4. **Apakah banyak klien butuh kontrak dan dokumen yang jelas?** OpenAPI otomatis FastAPI menghemat kerja.
5. **Apa yang sudah dikuasai tim?** Tim mahir Flask mengalahkan tim baru yang bergulat dengan FastAPI.

### 5. Migrasi satu endpoint demi satu (strangler)

Jangan pernah menghentikan dunia untuk menulis ulang. Jalankan keduanya berdampingan.

```text
            ┌───────────────┐   /api/ai/*  ──►  new FastAPI service
 client ──► │ gateway/proxy │
            └───────────────┘   everything else ─► existing Flask app
```

1. Pasang gateway (nginx, API Gateway) di depan.
2. Bangun fitur **baru** di FastAPI. Arahkan hanya path-nya ke FastAPI.
3. Pindahkan endpoint lama nanti, satu per satu, saat memang perlu perubahan besar.
4. Bagi database dengan hati-hati, atau beri layanan baru database sendiri.
5. Saat Flask tak punya apa-apa lagi, hapus.

Begitulah tim sungguhan tetap merilis sambil memodernisasi.

### 6. Pilihanmu di handbook ini

- **RevoShop** tetap Flask. Ia jalan, dan mengajarkan dasar-dasarnya.
- **Layanan AI CareerPilot** memakai FastAPI. Ia men-stream, menunggu model AI, dan membuka API yang jelas.
- Di pekerjaan, harapkan keduanya. Menguasai Flask *dan* FastAPI adalah nilai tambah untuk peran remote, karena banyak perusahaan menjalankan layanan Flask lama di samping layanan FastAPI baru.

### Memilih

| Situasi | Pilih |
|---|---|
| Halaman dirender di server | Flask (atau Django) |
| App Flask ada, tak ada yang memaksa berubah | tetap Flask |
| API baru dengan streaming AI atau banyak menunggu I/O | FastAPI |
| API baru, tim kecil yang mahir Flask | Flask tak masalah |
| App Flask lama + satu fitur AI baru | tambah layanan FastAPI di sampingnya |

## ⚠️ Kesalahan umum

- Menulis ulang app yang jalan hanya karena FastAPI sedang tren.
- Memilih berdasarkan angka benchmark, bukan hambatan sebenarnya (database).
- Mencampur Flask dan FastAPI di satu proses tanpa rencana.
- Meremehkan biaya migrasi: tes, auth, deployment dan monitoring semua berubah.
- Mengatakan "X lebih baik" di wawancara, tanpa alasan dan tanpa trade-off.

:::revoshop
Bayangkan menambah fitur "deskripsi produk pintar" ke RevoShop yang men-stream teks dari model AI. (1) Apakah kamu menulis ulang RevoShop di FastAPI, atau menambah layanan FastAPI terpisah? Kenapa? (2) Apa yang diarahkan gateway ke masing-masing? (3) Sebutkan dua hal yang harus berubah jika kamu menulis ulang semuanya (petunjuk: auth, tes, deployment).
:::

## 🏆 Praktik terbaik

- [ ] Putuskan dengan alasan dan trade-off tertulis, bukan selera.
- [ ] Jangan menulis ulang app yang jalan tanpa alasan bisnis.
- [ ] Pindah bertahap: gateway di depan, satu endpoint atau layanan sekali jalan.
- [ ] Jaga kontrak (URL, bentuk JSON) tetap sama selama pindah.
- [ ] Ukur hambatan nyata sebelum menyalahkan framework.
- [ ] Pelajari keduanya; keterampilannya berpindah (routing, validasi, auth, testing).

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Dalam dua menit, jelaskan ke rekan tim kenapa sebuah tim bisa mempertahankan Flask untuk layanan lama tapi memilih FastAPI untuk layanan AI baru. Pakai gambaran motor dan mobil boks, dan sebut satu trade-off untuk tiap sisi.

## 📐 Rancang

Sebuah perusahaan punya monolit Flask dengan 80 endpoint. Tim produk ingin asisten AI dengan jawaban streaming. Rencanakan pendekatannya: apa yang kamu bangun, di framework apa, bagaimana lalu lintas sampai ke tiap bagian, apa yang kamu biarkan, dan apa yang bisa salah.

:::quiz
Tampilkan rancangan yang mungkin

- **Bangun asisten sebagai layanan FastAPI baru.** Ia men-stream token (SSE) dan menunggu model AI, hal yang dikerjakan baik oleh FastAPI.
- **Biarkan 80 endpoint Flask.** Mereka jalan; tak ada yang memaksa penulisan ulang.
- **Gateway di depan:** arahkan `/api/assistant/*` ke FastAPI dan sisanya ke Flask. Browser melihat satu domain.
- **Auth:** bagi secret JWT yang sama atau layanan auth, supaya satu login berlaku di keduanya. Uji bahwa token diterima keduanya.
- **Data:** layanan baru membaca lewat API yang ada, atau punya tabel sendiri. Hindari dua layanan menulis tabel yang sama.
- **Observability:** satu format log dan header request-id di keduanya, supaya trace mengikuti request.
- **Risiko:** dua deployment untuk dijalankan, logika auth ganda, buffering proxy yang merusak streaming. Redam dengan library bersama, tes di staging dan pengaturan gateway untuk streaming.
- **Nanti:** pindahkan endpoint Flask hanya saat ia memang butuh perubahan besar.

**Aturan yang ditunjukkan:** tambah kemampuan baru di samping sistem lama; migrasikan bagian lama hanya bila ada alasan.
:::

### 📝 Daftar cek diri

- [ ] Pilihan disertai alasan dan trade-off yang disebut
- [ ] Rencana menghindari penulisan ulang big-bang
- [ ] Auth dan logging bekerja di kedua layanan
- [ ] Risikonya disebutkan

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m3/w3/04-decision" ai="no-ai" title="Tulis panduan keputusan sebagai kode"}
Di `framework_choice.py`, implementasikan `choose_framework(...)`. Ia mengembalikan `"flask"`, `"keep-flask"` atau `"fastapi"` dengan tiga aturan: halaman dirender server → Flask; app Flask yang ada tanpa alasan pindah → pertahankan; selain itu skor (I/O async +2, streaming AI +2, dokumen otomatis +1, tim mahir FastAPI +1, kurangi 2 jika migrasi) yang butuh 3 untuk memilih FastAPI.
:::

:::hints
- Cek dua aturan return awal lebih dulu, sesuai urutan.
- Boolean dihitung 0 atau 1, jadi `2 * needs_async_io` bisa dipakai.
- Kurangi 2 hanya bila `existing_flask_app` bernilai true.
- Di akhir: `score >= 3` → `"fastapi"`; selain itu `"keep-flask"` bila ada app lama, kalau tidak `"flask"`.
:::

## ✅ Cek cepat

:::quiz
Kenapa "FastAPI lebih cepat" biasanya alasan yang lemah untuk menulis ulang app Flask?

App nyata menghabiskan waktu menunggu database dan layanan lain, bukan di framework. Query lambat atau indeks yang hilang jauh lebih mahal daripada selisih framework mana pun, dan penulisan ulang menambah risiko dan biaya. Perbaiki hambatan sebenarnya dulu; pilih FastAPI untuk validasi, dokumen atau I/O async saat kamu benar-benar membutuhkannya.
:::

:::quiz
Apa itu pendekatan strangler untuk pindah dari Flask ke FastAPI?

Pasang gateway di depan keduanya, bangun fitur baru di FastAPI dan arahkan hanya path-nya ke sana, lalu pindahkan endpoint lama satu per satu bila masuk akal. App tetap berjalan sepanjang waktu, dan kamu menghapus Flask hanya saat tak ada lagi yang tersisa di dalamnya.
:::

## 📚 Lanjut belajar

- [FastAPI: Alternatives, Inspiration and Comparisons](https://fastapi.tiangolo.com/alternatives/)
- [Flask documentation](https://flask.palletsprojects.com/)
- [Martin Fowler: Strangler Fig](https://martinfowler.com/bliki/StranglerFigApplication.html)

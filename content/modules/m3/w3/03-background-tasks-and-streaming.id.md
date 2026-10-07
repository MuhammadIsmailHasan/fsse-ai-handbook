---
title: "Background Tasks & Streaming Responses"
summary: Kerjakan pekerjaan lambat setelah response dengan BackgroundTasks (dan tahu kapan perlu antrean job sungguhan), lalu kirim jawaban besar atau lambat sedikit demi sedikit dengan StreamingResponse dan Server-Sent Events — pola di balik endpoint chat AI.
sourceHash: f87da8a5fe1e
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Menjalankan pekerjaan **setelah** response dengan **`BackgroundTasks`**
- Tahu batasnya: kapan background task adalah alat yang salah
- Mengirim response **sedikit demi sedikit** dengan **`StreamingResponse`**
- Memakai **Server-Sent Events (SSE)** untuk mendorong teks ke browser
- Kenapa endpoint AI memakai streaming, dan apa yang bisa salah

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Background task** | Fungsi yang berjalan setelah response dikirim |
| **Job queue** | Sistem terpisah yang menyimpan job dan menjalankannya dengan andal |
| **Streaming** | Mengirim isi dalam potongan kecil begitu siap |
| **Generator** | Fungsi yang memberi nilai satu per satu dengan `yield` |
| **SSE** | Format teks sederhana agar server mendorong event ke browser |
| **Token** | Potongan kecil teks yang dihasilkan model AI |
| **Time to first byte** | Berapa lama user menunggu sebelum ada yang muncul |

## 🧠 Ide besarnya

Background task itu seperti **kasir yang menyerahkan struk lebih dulu**, lalu membungkus belanjaanmu sementara kamu berjalan pergi. Kamu tak menunggu pembungkusan. Streaming response itu seperti **ban berjalan sushi**: piring datang satu per satu selagi koki masih memasak, bukan kamu menunggu seluruh hidangan di meja.

## ❓ Kenapa ini penting

Sebagian pekerjaan lambat dan user tak butuh hasilnya sekarang: kirim email, ubah ukuran gambar, tulis audit log. Mengerjakannya di dalam request membuat user menunggu tanpa guna. Pekerjaan lain lambat *dan* user ingin melihatnya tumbuh: jawaban AI butuh sepuluh detik, tapi kata pertama bisa muncul dalam setengah detik. Streaming membuat app terasa cepat walau pekerjaannya tidak. Keduanya alat harian di layanan AI, jadi kamu perlu tahu apa yang bisa dan tak bisa mereka janjikan.

## 📖 Langkah demi langkah

### 1. `BackgroundTasks`: pekerjaan setelah response

Tambahkan parameter `BackgroundTasks` dan panggil `add_task` dengan fungsi dan argumennya. FastAPI mengirim response dulu, lalu menjalankan fungsinya.

```python
from fastapi import BackgroundTasks, FastAPI

app = FastAPI()

def send_welcome(email: str) -> None:
    ...   # slow: talk to an email service

@app.post("/signup", status_code=201)
def signup(body: SignupIn, background: BackgroundTasks):
    user = create_user(body)                    # the part the user needs
    background.add_task(send_welcome, body.email)
    return {"email": body.email}                # returns right away
```

User menerima `201` dalam milidetik. Emailnya keluar sesaat kemudian.

### 2. Apa yang *tidak* dijanjikan background task

Background task berjalan **di dalam proses web-mu**. Itu ada harganya:

- Kalau server restart atau crash, tugasnya **hilang**. Tak ada yang mengingatnya.
- Kalau gagal, klien sudah menerima sukses. Tak ada yang mengulang.
- Ia memakai CPU dan memori yang sama dengan API-mu, jadi pekerjaan berat memperlambat semua request.
- Tak ada cara bertanya "sudah selesai belum?"

Pakai untuk pekerjaan kecil yang **bagus kalau ada**: satu baris log, pemanasan cache, email selamat datang yang boleh terlewat.

### 3. Kapan butuh antrean job sungguhan

Kalau pekerjaan penting, lambat, atau harus diulang saat gagal, taruh job di **antrean** dan biarkan **worker** terpisah menjalankannya.

| Kebutuhan | Pakai |
|---|---|
| Kecil, boleh hilang, cepat | `BackgroundTasks` |
| Harus selamat dari restart, ulang, jadwal | antrean: Celery, ARQ atau RQ dengan Redis, atau AWS SQS |
| Jalan sesuai jam | scheduler (cron, EventBridge) |
| CPU berat (video, ML) | proses worker atau layanan sendiri |

Kamu sudah bertemu antrean Redis dan SQS di Module 5. API hanya **menambah job** ke antrean lalu kembali; worker mengerjakan sisanya.

### 4. Streaming dengan `StreamingResponse`

Berikan **generator** ke `StreamingResponse`. Ia mengirim tiap potongan yang di-yield begitu potongan itu ada.

```python
from fastapi.responses import StreamingResponse

def word_events(text: str):
    for word in text.split():
        yield f"data: {word}\n\n"
    yield "data: [DONE]\n\n"

@app.get("/stream")
def stream(text: str):
    return StreamingResponse(word_events(text), media_type="text/event-stream")
```

Tak ada yang dibangun dulu di memori. Ide yang sama bekerja untuk ekspor CSV raksasa: yield baris demi baris, dan server tak pernah memegang seluruh file.

### 5. Server-Sent Events (SSE)

SSE adalah format teks biasa. Tiap pesan adalah baris yang diawali `data:` dan diakhiri **baris kosong** (`\n\n`). Browser membacanya dengan `EventSource`.

```javascript
const source = new EventSource("/stream?text=hello big world");
source.onmessage = (event) => {
  if (event.data === "[DONE]") return source.close();
  output.textContent += event.data + " ";
};
```

SSE satu arah (server ke browser), berjalan di HTTP biasa, dan menyambung ulang sendiri. Untuk chat dua arah kamu pakai WebSocket, tapi untuk "tampilkan jawaban AI saat ditulis" SSE lebih sederhana.

### 6. Kenapa endpoint AI memakai streaming

Model bahasa menulis **token demi token**. Jawaban penuh bisa butuh 10 detik. Kalau kamu menunggu semuanya, user menatap layar kosong. Kalau di-stream, kata pertama muncul dalam kurang dari satu detik. Total waktunya sama; **time to first byte**-nya jauh lebih baik.

```python
async def answer_events(question: str):
    async for token in ai_client.stream(question):   # your AI client
        yield f"data: {token}\n\n"
    yield "data: [DONE]\n\n"
```

Generator `async` adalah bentuk yang tepat di sini, karena menunggu token berikutnya adalah I/O (kamu sudah melihat alasannya di lesson async).

### 7. Apa yang bisa salah

- **Proxy melakukan buffer.** nginx atau CDN bisa menahan potongan dan mengirimnya sekaligus. Matikan buffering untuk route itu (di nginx, header `X-Accel-Buffering: no`).
- **Error di tengah stream.** Status `200` sudah terkirim. Kirim event error (`data: {"error": ...}`) agar klien bisa menampilkannya.
- **Klien pergi.** User menutup tab. Hentikan pekerjaannya, atau kamu membayar token yang tak dibaca siapa pun.
- **Auth.** `EventSource` tak bisa mengatur header `Authorization`. Pakai cookie, atau `fetch` dengan pembaca stream.

### Kapan pakai apa

| Situasi | Lakukan ini |
|---|---|
| Kirim email selamat datang, tulis log | `BackgroundTasks` |
| Struk pembayaran, laporan, apa pun yang tak boleh hilang | antrean job plus worker |
| Tampilkan jawaban AI saat ditulis | `StreamingResponse` + SSE |
| Ekspor file besar | stream baris demi baris |
| Chat langsung dua arah | WebSocket |

## ⚠️ Kesalahan umum

- Memakai `BackgroundTasks` untuk pekerjaan penting dan kehilangannya saat restart.
- Pekerjaan CPU berat di background task yang memperlambat seluruh API.
- Membangun jawaban penuh dulu, baru "men-stream"-nya (tak ada untungnya).
- Lupa baris kosong (`\n\n`) setelah tiap pesan SSE.
- Proxy yang mem-buffer stream, sehingga user tak melihat apa-apa sampai akhir.
- Mengabaikan error setelah byte pertama, karena status code sudah `200`.

:::revoshop
RevoShop mengirim email pesanan dan menulis audit log. (1) Temukan satu hal yang seharusnya terjadi *setelah* response. Apakah hari ini dikerjakan di dalam request? (2) Mana yang boleh hilang saat restart (pakai `BackgroundTasks`), dan mana yang tidak (pakai antrean)? (3) Adakah daftar panjang atau ekspor yang akan terbantu streaming?
:::

## 🏆 Praktik terbaik

- [ ] Pakai `BackgroundTasks` hanya untuk pekerjaan kecil yang boleh hilang.
- [ ] Taruh pekerjaan penting atau lambat di antrean dengan worker, retry dan monitoring.
- [ ] Buat tugas **idempoten** (aman dijalankan dua kali), karena retry pasti terjadi.
- [ ] Stream jawaban AI; kirim event `[DONE]` di akhir dan event error saat gagal.
- [ ] Matikan buffering proxy untuk route streaming dan uji lewat proxy sungguhan.
- [ ] Hentikan pekerjaan hulu saat klien putus.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan `BackgroundTasks` dengan kasir yang memberi struk lebih dulu, dan streaming dengan ban berjalan sushi. Lalu katakan kapan kamu tidak memakai background task.

## 📐 Rancang

Endpoint `POST /ai/cover-letter` milik CareerPilot memanggil model AI yang butuh sekitar 12 detik. Rancang alurnya: apa yang dilihat user, apakah kamu stream, apa yang berjalan di latar belakang (menyimpan hasil, mengirim email), apa yang butuh antrean, dan bagaimana menangani error di tengah jalan.

:::quiz
Tampilkan rancangan yang mungkin

- **Stream jawabannya:** `GET`/`POST` mengembalikan `StreamingResponse` dengan SSE; token muncul dalam kurang dari satu detik. Event `[DONE]` di akhir menutup stream.
- **Simpan hasilnya:** setelah token terakhir, simpan surat ke database. Background task kecil boleh jika kehilangannya bisa diterima (user masih punya teksnya di layar); kalau tidak, simpan sebelum mengirim `[DONE]`.
- **Email salinan:** ini "bagus kalau ada", jadi `BackgroundTasks` cukup. Kalau tak boleh hilang, taruh job di antrean.
- **Penagihan pemakaian atau audit:** tak boleh hilang → tulis ke antrean atau database dalam transaksi yang sama, bukan background task.
- **Error di tengah jalan:** status sudah `200`, jadi kirim `data: {"error": "..."}`, lalu tutup. Klien menampilkan tombol coba lagi.
- **Putus koneksi:** cek koneksi yang tertutup dan batalkan panggilan AI supaya tak membayar token yang tak terbaca.
- **Proxy:** matikan buffering untuk route ini.

**Aturan yang ditunjukkan:** stream apa yang ditonton user; latar belakangkan apa yang tak ia butuhkan; antrekan apa yang tak boleh hilang.
:::

### 📝 Daftar cek diri

- [ ] Pekerjaan lambat yang ditunggu user untuk dilihat di-stream
- [ ] Hanya pekerjaan yang boleh hilang memakai `BackgroundTasks`
- [ ] Pekerjaan penting lewat antrean
- [ ] Error setelah byte pertama dikirim sebagai event
- [ ] Buffering proxy dan klien yang putus sudah ditangani

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m3/w3/03-background-stream" ai="no-ai" title="Email selamat datang di latar belakang dan endpoint streaming"}
Di `signup_stream_app.py`, selesaikan `POST /signup` (tolak email buruk dengan `400` dan jadwalkan apa pun; selain itu kembalikan `201` seketika dan kirim email selamat datang dengan `BackgroundTasks`) dan `GET /stream` (stream satu event SSE per kata, lalu `data: [DONE]`). `word_events` harus berupa generator.
:::

:::hints
- `background.add_task(send_welcome, body.email)` — berikan fungsi dan argumennya, jangan memanggilnya.
- Munculkan `HTTPException(status_code=400, ...)` **sebelum** `add_task` agar email buruk tak menjadwalkan apa pun.
- `word_events`: `for word in text.split(): yield f"data: {word}\n\n"`, lalu `yield "data: [DONE]\n\n"`.
- `return StreamingResponse(word_events(text), media_type="text/event-stream")`.
:::

## ✅ Cek cepat

:::quiz
Kenapa `BackgroundTasks` adalah alat yang salah untuk mengirim struk pembayaran yang penting?

Tugasnya berjalan di dalam proses web. Kalau server restart atau crash sebelum tugas jalan, tugasnya hilang, dan tak ada yang mengulang atau melaporkan kegagalan. Pekerjaan penting butuh antrean job dan worker terpisah, yang menyimpan job secara tahan lama dan mengulangnya.
:::

:::quiz
Kenapa men-stream jawaban AI memperbaiki pengalaman user walau total waktunya sama?

Model menulis token demi token, jadi kata pertama siap dalam jauh kurang dari satu detik. Streaming menampilkannya seketika, bukan setelah seluruh jawaban. User melihat kemajuan langsung (time to first byte lebih baik) dan bisa mulai membaca selagi sisanya masih ditulis.
:::

## 📚 Lanjut belajar

- [FastAPI: Background Tasks](https://fastapi.tiangolo.com/tutorial/background-tasks/)
- [FastAPI: Custom Response — StreamingResponse](https://fastapi.tiangolo.com/advanced/custom-response/#streamingresponse)
- [MDN: Using server-sent events](https://developer.mozilla.org/en-US/docs/Web/API/Server-sent_events/Using_server-sent_events)

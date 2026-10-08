---
title: "Chat API & Streaming"
summary: "Panggil model chat dari Python — pesan dan peran, system prompt, max_tokens dan stop_reason, usage, error dan retry — lalu stream jawaban token demi token dan teruskan ke browser dengan aman."
sourceHash: 8aeff698a8ac
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Bentuk **request chat**: model, system prompt, pesan, `max_tokens`
- Kenapa API itu **stateless** dan apa artinya untuk kodemu
- Membaca **response**: blok teks, `stop_reason`, `usage`
- **Streaming**: event, `text_stream`, dan arti tiap event
- Mengirim stream ke browser dengan **FastAPI + SSE**
- **Error dan retry** yang dibutuhkan kode produksi

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Messages API** | Cara standar mengobrol dengan model: daftar pesan masuk, satu pesan keluar |
| **Role** | Siapa yang menulis pesan: `user` atau `assistant` |
| **System prompt** | Instruksi tetap untuk seluruh chat |
| **Stateless** | Server tidak mengingat apa pun antar panggilan |
| **Stop reason** | Kenapa model berhenti menulis |
| **Stream** | Jawaban datang dalam potongan kecil saat ditulis |
| **SSE** | Server-Sent Events: format teks sederhana untuk mendorong stream ke browser |
| **Rate limit** | Batas request atau token per menit |

## 🧠 Ide besarnya

Chat API itu seperti **ahli yang sangat pelupa di telepon**. Setiap kali menelepon, kamu harus membacakan *seluruh* percakapan sejauh ini, lalu mengajukan pertanyaan barumu. Si ahli menjawab dan melupakan semuanya saat telepon ditutup. Kamu yang memegang buku catatan.

Streaming adalah si ahli **berbicara sambil berpikir**, bukan diam sepuluh detik lalu membacakan satu halaman penuh. Total waktunya sama, tapi orang di telepon mendengar kata-kata pertama hampir seketika.

## ❓ Kenapa ini penting

Ini lapisan dasar di bawah setiap fitur AI: chatbot, ringkasan, ekstraksi, agen. Kalau kamu menguasainya, kamu mendapat:

- **produk yang terasa cepat** (kata pertama dalam kurang dari satu detik),
- **yang stabil** (retry, timeout, error yang jelas),
- **yang aman** (API key tak pernah sampai ke browser; jawaban terpotong terdeteksi),
- **yang murah** (kamu mencatat `usage` dan memangkas apa yang dikirim).

## 📖 Langkah demi langkah

### 1. Pasang dan buat klien

```python
# pip install anthropic     # the provider's official SDK
import anthropic

client = anthropic.Anthropic()    # reads the API key from the environment (ANTHROPIC_API_KEY)
```

**Jangan pernah menaruh key di kode, di git, atau di JavaScript front-end.** Simpan di environment variable atau secret manager. *Backend*-mu yang memanggil model; browser memanggil backend-mu.

### 2. Satu request

```python
response = client.messages.create(
    model=settings.llm_model,          # from config, see the last lesson
    max_tokens=1000,                   # the most the model may write in this call
    system="You are a polite help-desk assistant for Warung Kita Online.",
    messages=[
        {"role": "user", "content": "How long does delivery take?"},
    ],
)

for block in response.content:         # a list of blocks: check the type first
    if block.type == "text":
        print(block.text)
print(response.stop_reason, response.usage.input_tokens, response.usage.output_tokens)
```

Hal yang perlu diperhatikan:

- **`messages`** adalah list `{"role", "content"}` dengan peran `user` dan `assistant`. Yang pertama harus `user`.
- **System prompt adalah field terpisah**, bukan pesan di dalam list.
- **`max_tokens` wajib.** Atur dengan sengaja (lihat lesson 1).
- **`response.content` adalah list blok**, bukan string. Jawaban normal punya blok `text`. Jenis lain (pemanggilan tool, thinking) muncul di minggu berikutnya, jadi selalu cek `block.type`.
- Baca **`stop_reason`**: `end_turn` (selesai), `max_tokens` (terpotong!), `tool_use` (meminta tool), `refusal` (menolak demi keamanan), dan beberapa lainnya.
- Baca **`usage`** dan catat.

### 3. API stateless: kamu yang memegang riwayat

```python
from chat_stream import Conversation        # the exercise for this lesson

chat = Conversation(system="You are a polite help-desk assistant.")
chat.add_user("Hi, I need help with an order.")
reply = client.messages.create(**chat.to_request(settings.llm_model, 1000))
chat.add_assistant(reply.content[0].text)
chat.add_user("It is order 1234.")
reply = client.messages.create(**chat.to_request(settings.llm_model, 1000))
```

Tiap panggilan mengirim seluruh list. App-mu (atau database) menyimpan riwayat per user. Ingat lesson 1: list tumbuh, jadi pangkas atau ringkas.

Peran harus **bergantian** (user, assistant, user, ...), dan chat harus **dimulai dengan pesan user**. Kelas `Conversation` kecil yang menegakkan ini menyelamatkanmu dari error 400 yang membingungkan.

### 4. Streaming

Tanpa streaming, user menunggu seluruh jawaban. Dengan streaming kamu mendapat event saat model menulis. Helper SDK menyembunyikan detailnya:

```python
with client.messages.stream(
    model=settings.llm_model,
    max_tokens=1000,
    messages=[{"role": "user", "content": "Explain what a token is."}],
) as stream:
    for text in stream.text_stream:          # just the new text, piece by piece
        print(text, end="", flush=True)
    final = stream.get_final_message()       # the complete message, with usage and stop_reason
print(final.stop_reason, final.usage.output_tokens)
```

Pakai streaming untuk apa pun yang ditonton manusia, dan juga untuk **keluaran panjang** (`max_tokens` besar) karena request panjang tanpa streaming bisa timeout.

Di balik helper ada rangkaian event kecil:

```text
message_start         → starts; input token count
content_block_start   → a text block begins
content_block_delta   → "Hel"   then "lo"   (the pieces)
content_block_stop    → the block ends
message_delta         → stop_reason and output token count
message_stop          → done
ping                  → keep-alive, ignore
error                 → something broke
```

Pembaca stream yang baik melakukan empat hal: **menggabungkan** delta teks, **mengabaikan** jenis event yang tak dikenal (penyedia menambah yang baru, seperti delta thinking), **memperlakukan event error sebagai error**, dan memperlakukan stream yang berakhir **tanpa `message_stop`** sebagai kegagalan, bukan jawaban pendek.

### 5. Teruskan stream ke browser (FastAPI + SSE)

Kamu sudah bertemu `StreamingResponse` dan SSE di Module 3. Sekarang sambungkan keduanya. Browser tidak boleh melihat key-mu, jadi browser memanggil endpoint **-mu**, dan endpoint-mu memanggil model:

```python
import json
import anthropic
from fastapi import Depends
from fastapi.responses import StreamingResponse

@app.post("/v1/chat")
def chat(body: ChatIn, user: str = Depends(current_user)):
    def events():
        try:
            with client.messages.stream(
                model=settings.llm_model,
                max_tokens=1000,
                system=SYSTEM_PROMPT,
                messages=body.messages,
            ) as stream:
                for text in stream.text_stream:
                    yield f"data: {json.dumps({'token': text})}\n\n"
                final = stream.get_final_message()
            if final.stop_reason == "max_tokens":
                yield f"data: {json.dumps({'truncated': True})}\n\n"
            log_usage(user, final.usage)
            yield "data: [DONE]\n\n"
        except anthropic.APIError as error:
            yield f"data: {json.dumps({'error': type(error).__name__})}\n\n"

    return StreamingResponse(events(), media_type="text/event-stream",
                             headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})
```

Hal yang dikerjakan dengan benar di sini:

- tiap token adalah **JSON**, sehingga token dengan baris kosong tak merusak format SSE,
- jawaban yang **terpotong** diberi tanda,
- **error setelah byte pertama** menjadi event error (status HTTP sudah 200),
- **usage dicatat** dan user diautentikasi,
- buffering proxy dimatikan.

Validasi `messages` yang masuk (peran, panjang, ukuran) sebelum meneruskannya. Jangan pernah percaya klien mengirim system prompt yang aman: simpan system prompt di server.

### 6. Error dan retry

Hal buruk terjadi karena alasan biasa: server sibuk, rate limit, jaringan putus, request buruk.

| Status | Artinya | Yang dilakukan |
|---|---|---|
| 400 | requestmu tidak valid | perbaiki kode; jangan retry |
| 401 / 403 | key hilang atau tidak diizinkan | perbaiki konfigurasi |
| 404 | model atau resource tak dikenal | perbaiki nama model |
| 413 | request terlalu besar | pangkas masukan |
| 429 | rate limit | tunggu dan retry (back off) |
| 500 / 503 / 529 | masalah server atau kelebihan beban | retry nanti, mungkin fallback ke model lain |

SDK sudah **me-retry** error koneksi, 408, 409, 429 dan 5xx beberapa kali dengan backoff. Atur **timeout** yang masuk akal. Tangkap exception yang **paling spesifik** lebih dulu:

```python
try:
    response = client.messages.create(...)
except anthropic.RateLimitError:
    ...                                   # tell the user to retry soon, or queue the job
except anthropic.APIStatusError as error:
    log.error("model error %s", error.status_code)
    ...                                   # 4xx: a bug of ours; 5xx: temporary
except anthropic.APIConnectionError:
    ...                                   # the network failed
```

Jangan pernah menampilkan error mentah penyedia ke user. Beri pesan singkat dan tenang, dan catat detailnya (dengan request id) untuk dirimu.

### 7. Menguji tanpa membayar

Kodemu yang membaca event, membuat request dan meneruskan SSE adalah Python biasa. Ujilah dengan **event palsu** (latihan melakukannya) dan dengan klien palsu yang kamu injeksi, persis seperti `dependency_overrides` di Module 3. Simpan hanya beberapa "smoke test" yang memanggil API sungguhan, dan jalankan jarang.

### Memilih caranya

| Situasi | Lakukan ini |
|---|---|
| Jawaban pendek, di latar belakang | `messages.create`, baca `response.content` |
| Manusia menonton | `messages.stream` + SSE |
| Keluaran sangat panjang | stream (menghindari timeout) |
| Chat | simpan riwayat sendiri; peran bergantian; pangkas |
| Browser butuh jawabannya | backend men-stream ke browser; key tetap di server |
| Kena rate limit | back off dan retry; antrekan kerja; pakai batch API untuk pekerjaan tak mendesak |
| Pengujian | event palsu dan klien yang diinjeksi |

- ✅ Catat `usage`, `stop_reason` dan request id.
- ✅ Perlakukan `max_tokens` dan `refusal` sebagai hasil normal yang harus ditangani.
- 🚫 API key di kode front-end.
- 🚫 Menampilkan stack trace mentah atau error penyedia ke user.

## ⚠️ Kesalahan umum

- Memakai `response.content[0].text` tanpa mengecek jenis blok itu.
- Lupa bahwa API stateless dan hanya mengirim pesan terakhir.
- Dua pesan `user` berturut-turut, atau memulai dengan pesan `assistant`.
- Menaruh system prompt di list pesan.
- Tak menangani `stop_reason == "max_tokens"`.
- Menangkap satu `Exception` luas dan me-retry semuanya, termasuk request buruk.
- Mengirim teks model mentah di SSE (baris kosong di teks merusak stream).
- Tidak mematikan buffering proxy, sehingga streaming terlihat seperti menunggu.
- Membiarkan klien memilih model atau system prompt.

:::revoshop
Rancang request yang dikirim endpoint "tanya tentang pesananku" RevoShop. (1) Apa isi system prompt, dan apa isi `messages`? (2) Ke mana data pesanan masuk, dan siapa yang boleh membacanya (pikirkan JWT dari Module 2)? (3) Apa yang harus dilakukan endpoint saat penyedia mengembalikan 429?
:::

## 🏆 Praktik terbaik

- [ ] Simpan API key dan system prompt di server.
- [ ] Atur `max_tokens` dan timeout dengan sengaja; tangani `max_tokens` dan `refusal`.
- [ ] Stream apa pun yang ditonton manusia; kirim token sebagai JSON di SSE.
- [ ] Tangkap error paling spesifik dulu; retry hanya yang layak di-retry.
- [ ] Catat `usage`, `stop_reason`, model dan request id untuk setiap panggilan.
- [ ] Bungkus penyedia dengan antarmuka kecilmu sendiri dan uji dengan fake.
- [ ] Validasi dan batasi ukuran pesan user sebelum meneruskannya.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan "stateless" dengan gambaran ahli yang pelupa. Lalu katakan kenapa jawaban yang di-stream terasa lebih cepat padahal total waktunya sama.

## 📐 Rancang

Endpoint chat SupportDesk AI harus (1) mengautentikasi user, (2) men-stream jawaban, (3) bertahan saat penyedia mati beberapa menit, (4) tidak pernah membuka system prompt atau key, dan (5) berbiaya tidak lebih dari 2 sen per giliran chat rata-rata. Rancang alur request dan penanganan kegagalannya.

:::quiz
Tampilkan rancangan yang mungkin

- **Alur:** browser → `POST /v1/chat` (JWT) → validasi dan batasi ukuran pesan → tambahkan system prompt sisi server dan konteks hasil retrieval → panggil model dengan streaming → teruskan token sebagai SSE JSON → catat usage → `[DONE]`.
- **Auth dan penyalahgunaan:** verifikasi JWT, rate-limit per user, batasi jumlah dan ukuran pesan, dan jangan pernah menerima system prompt atau nama model dari klien.
- **Error:** SDK me-retry masalah singkat. Untuk 429/5xx setelah retry, kirim event error dan pesan ramah "coba lagi". Untuk gangguan lebih lama, **fallback** ke penyedia kedua atau model lebih kecil di balik antarmuka yang sama, atau beralih ke "kami akan email kamu" dengan pertanyaan diantrekan.
- **Gagal di tengah stream:** status sudah 200, jadi kirim `{"error": ...}`, tandai giliran itu gagal di database, dan biarkan user mencoba lagi.
- **Jawaban terpotong:** deteksi `max_tokens` dan tawarkan "lanjutkan".
- **Biaya:** catat `usage` per giliran, perkirakan dengan rumus dari lesson 1, pangkas pesan lama, cache system prompt yang stabil, pakai model lebih kecil untuk giliran mudah, dan beri alarm saat rata-rata giliran melewati 2 sen.
- **Secret:** key di secret manager atau environment variable; system prompt disimpan di server; log tidak pernah berisi key atau pesan pelanggan lengkap.
- **Klien putus:** hentikan panggilan model saat browser pergi.

**Aturan yang ditunjukkan:** backend memegang key, prompt dan batas; browser hanya mendapat stream token yang aman.
:::

### 📝 Daftar cek diri

- [ ] Key dan system prompt tak pernah meninggalkan server
- [ ] Error streaming dan pemotongan dilaporkan ke klien
- [ ] Kegagalan punya rencana retry atau fallback
- [ ] Usage dicatat dan biaya diperkirakan

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m7/w1/03-chat-stream" ai="no-ai" title="Conversation dan pembaca stream"}
Bangun `Conversation` (peran bergantian, system prompt terpisah, dict request yang berupa salinan), `collect_stream` (gabungkan delta teks, abaikan thinking dan event tak dikenal, baca stop reason dan token, raise pada event error atau akhir dini) dan `to_sse` (baris SSE lazy sebagai JSON, flag `truncated`, event error tanpa `[DONE]`). Tes memakai bentuk event yang asli, jadi tak perlu API key.
:::

:::hints
- `Conversation._add(role, text)`: tolak pesan pertama `assistant` dan dua peran sama berturut-turut.
- `to_request`: salin pesan (`[dict(m) for m in ...]`) dan tambahkan `"system"` hanya bila diberikan.
- `collect_stream`: loop event menurut `event["type"]`; untuk `content_block_delta` cek `delta["type"] == "text_delta"`.
- Setelah loop, tanpa `message_stop` berarti `StreamError("stream ended early")`.
- `to_sse`: `yield f"data: {json.dumps({'token': text})}\n\n"`; pada event error `yield` errornya lalu `return` (tanpa `[DONE]`).
:::

## ✅ Cek cepat

:::quiz
Jawaban model berhenti di tengah kalimat. Apa yang kamu cek pertama?

Cek `stop_reason`. Jika `"max_tokens"`, jawaban mencapai batas keluaran. Naikkan `max_tokens`, minta jawaban lebih pendek, atau tampilkan opsi "lanjutkan". Cek juga bahwa prompt menyisakan ruang di context window.
:::

:::quiz
Kenapa kita mengirim token sebagai JSON di dalam SSE, bukan teks mentah?

SSE memisahkan pesan dengan baris kosong. Jika model menulis baris kosong di dalam token, teks mentah akan memecah pesan dan merusak stream. JSON meng-escape baris baru, sehingga tiap pesan tetap satu baris yang aman.
:::

:::quiz
Kenapa browser harus memanggil backend-mu dan bukan penyedia model langsung?

Key di kode browser terlihat oleh semua orang, yang lalu bisa menghabiskan uangmu. Backend-mu menyimpan key dan system prompt secara rahasia, memeriksa siapa user-nya, memvalidasi dan membatasi masukan, dan mencatat usage.
:::

## 📚 Lanjut belajar

- [Anthropic docs: Messages API](https://platform.claude.com/docs/en/api/messages)
- [Anthropic docs: Streaming messages](https://platform.claude.com/docs/en/build-with-claude/streaming)
- [Anthropic docs: Errors](https://platform.claude.com/docs/en/api/errors)

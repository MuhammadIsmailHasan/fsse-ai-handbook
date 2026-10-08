---
title: "Tool / Function Calling"
summary: "Biarkan model memakai kodemu dengan aman — deskripsikan tool dengan schema, jalankan loop panggilan sendiri, kembalikan hasil dan error, tangani panggilan paralel, dan simpan izin, validasi dan batas di programmu, bukan di model."
sourceHash: 60e429f2033a
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa itu **tool calling**, dan siapa menjalankan apa
- Cara **mendeskripsikan tool** agar model memakainya dengan baik
- **Loop**: tanya → tool_use → jalankan → tool_result → jawab
- **Error, panggilan paralel, dan batas langkah**
- Di mana **izin dan validasi** seharusnya berada (bukan di prompt)

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Tool** | Fungsi yang kamu tawarkan ke model, dengan nama, deskripsi dan input schema |
| **Tool call (`tool_use`)** | Permintaan model: "tolong jalankan tool ini dengan argumen ini" |
| **Tool result** | Yang kamu kirim balik setelah menjalankan tool |
| **Agent loop** | Ulangi: model meminta, kamu menjalankan, kamu menjawab, sampai ada jawaban akhir |
| **Context (`ctx`)** | Fakta dari aplikasimu, seperti siapa user yang login |
| **Idempoten** | Menjalankannya dua kali berefek sama dengan sekali |
| **Least privilege** | Beri tool hanya akses yang benar-benar ia butuhkan |
| **Persetujuan manusia** | Seseorang mengonfirmasi sebelum tindakan berisiko dijalankan |

## 🧠 Ide besarnya

Tool calling itu **pelayan dan dapur**. Model adalah pelayan yang bicara dengan pelanggan. Ia tak bisa memasak. Saat pelanggan bertanya sesuatu yang butuh dapur ("pesanan meja 4 sudah siap?"), pelayan menulis **catatan** ("cek pesanan, meja 4") dan menyerahkannya. Dapur (kodemu) mengerjakan hal sebenarnya dan menyerahkan hasil. Pelayan lalu menjelaskannya ke pelanggan.

Bagian pentingnya: pelayan menulis catatan, tapi **dapur yang memutuskan apa yang diizinkan**. Pelanggan tidak bisa membuat pelayan membuka laci kasir hanya dengan meminta baik-baik.

## ❓ Kenapa ini penting

Model sendirian hanya tahu apa yang ada di pelatihannya dan di promptmu. Dengan tool ia bisa:

- mencari **data langsung** (status pesanan, stok, kalender),
- **melakukan sesuatu** (membuat tiket, mengirim pesan, memberi refund),
- **menghitung persis** (matematika, tanggal, SQL) alih-alih menebak.

Ini dasar setiap agen AI. Di sini juga **risiko** muncul: model yang bisa memanggil `issue_refund` bisa ditipu untuk memanggilnya. Jadi tool calling sebagian besar soal merekayasa batasnya dengan benar.

## 📖 Langkah demi langkah

### 1. Siapa menjalankan apa

```text
1. you → model : the question + the list of tools (name, description, input schema)
2. model → you : stop_reason "tool_use" + a call: {id, name, input}
3. YOU run the tool (the model runs nothing)
4. you → model : the same conversation + a tool_result for that id
5. model → you : the final answer (or another tool call → repeat from 3)
```

Model hanya menghasilkan **teks yang tampak seperti panggilan**. Semua kuasa nyata, dan semua tanggung jawab, tetap di programmu.

### 2. Deskripsikan sebuah tool

Tool punya tiga bagian: **nama**, **deskripsi**, dan **input schema** (JSON Schema).

```python
tools = [
    {
        "name": "get_order",
        "description": (
            "Look up one of the CURRENT customer's orders by its order id. "
            "Call this whenever the customer asks about the status, items or delivery of an order. "
            "Do not call it for general policy questions."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {"type": "string", "description": "The order id, for example A1234"},
            },
            "required": ["order_id"],
            "additionalProperties": False,
        },
    }
]
```

Deskripsi adalah satu-satunya buku panduan model. Deskripsi yang baik menjelaskan **apa yang dilakukan**, **kapan dipanggil**, dan **kapan tidak**. Deskripsikan tiap properti, pakai `enum` untuk pilihan tetap, dan tandai wajib hanya field yang benar-benar wajib. Perhatikan apa yang **bukan** argumen: user id. Siapa user-nya datang dari app-mu (di bawah).

Jaga daftar tool tetap pendek dan jelas (segelintir tool bernama baik mengalahkan tiga puluh yang mirip). Namai seperti kata kerja: `get_order`, `create_ticket`.

### 3. Loop-nya

```python
messages = [{"role": "user", "content": user_input}]

for step in range(MAX_STEPS):                       # always a limit
    response = client.messages.create(
        model=settings.llm_model, max_tokens=1000,
        system=SYSTEM_PROMPT, tools=tools, messages=messages,
    )
    messages.append({"role": "assistant", "content": response.content})

    if response.stop_reason != "tool_use":          # a final answer (or max_tokens / refusal)
        break

    results = []
    for block in response.content:
        if block.type == "tool_use":
            results.append(run_tool_call(block, ctx))     # your code
    messages.append({"role": "user", "content": results})  # ONE message with ALL the results
else:
    raise TooManySteps()
```

Aturan yang perlu diingat:

- Tambahkan balasan model **utuh** (`response.content`), termasuk blok `tool_use`-nya, sebelum hasilnya.
- Setiap `tool_result` membawa **`tool_use_id`** dari panggilan yang dijawabnya.
- Model bisa meminta **beberapa tool sekaligus** (panggilan paralel). Jalankan semuanya, dan kirim **semua hasil dalam satu pesan user**.
- Selalu punya **batas langkah**. Model yang bingung bisa berputar selamanya dan menghabiskan uangmu.
- Cek `stop_reason`: `tool_use` berarti "jalankan tool-ku", `end_turn` berarti selesai, `max_tokens` berarti terpotong, `refusal` berarti menolak.

SDK juga menawarkan **tool runner** yang menulis loop ini untukmu dari fungsi Python bertipe. Itu nyaman, tapi tulis loop dengan tangan setidaknya sekali. Itu menjernihkan ide dan menunjukkan di mana menambah batas, log dan persetujuan.

### 4. Jalankan satu panggilan dengan aman

```python
def run_tool_call(tools, call, ctx):
    def result(content, error=False):
        block = {"type": "tool_result", "tool_use_id": call["id"], "content": content}
        if error:
            block["is_error"] = True
        return block

    tool = tools.get(call["name"])
    if tool is None:
        return result(f"unknown tool: {call['name']}", True)
    missing = sorted(set(tool.required) - set(call.get("input", {})))
    if missing:
        return result("missing required input: " + ", ".join(missing), True)
    try:
        value = tool.fn(ctx, **call.get("input", {}))
    except Exception as error:
        return result(f"tool failed: {type(error).__name__}: {error}", True)
    return result(value if isinstance(value, str) else json.dumps(value))
```

Kenapa tiap baris:

- **Tool tak dikenal / input hilang** menjadi hasil `is_error`, bukan exception. Model membaca errornya dan bisa memperbaiki diri ("aku lupa id pesanan").
- **Exception ditangkap.** Satu tool rusak tidak boleh meruntuhkan percakapan. Kembalikan pesan singkat yang berguna. Jangan membocorkan stack trace, path atau secret.
- **Hasil berupa teks.** Kembalikan JSON sebagai string. Jaga hasil **kecil dan relevan**: ia ditambahkan ke konteks dan kamu membayarnya di setiap giliran berikutnya.
- `ctx` diteruskan **oleh kodemu**.

### 5. Izin ada di tool, bukan di prompt

Jangan bergantung pada instruksi seperti "tampilkan hanya pesanan milik pelanggan itu sendiri". Model bisa ditipu. Sebaliknya, buat hal yang tidak aman menjadi mustahil:

```python
def get_order(ctx, order_id):
    order = db.find_order(order_id)
    if order is None or order.owner_id != ctx["user_id"]:
        raise LookupError("order not found")      # same message for "missing" and "not yours"
    return order.to_dict()
```

- `user_id` datang dari `ctx` (sesimu), **tidak pernah** dari argumen model. Fungsi tool yang tak punya parameter `user_id` tak bisa disuruh membaca data siapa.
- Cek **kepemilikan dan role** di dalam tool, dengan aturan yang sama seperti REST API-mu (Module 2).
- Pakai pesan yang sama untuk "tidak ada" dan "bukan milikmu", agar tool tidak mengonfirmasi bahwa pesanan pelanggan lain ada.
- **Validasi setiap argumen** seperti masukan user mana pun: tipe, rentang, format, nilai yang diizinkan. JSON dari model tak tepercaya. Jangan pernah membangun SQL atau perintah shell darinya dengan penyambungan string.
- **Least privilege:** tool read-only mendapat koneksi database read-only.

### 6. Tool yang mengubah sesuatu

Membaca aman. Menulis butuh kehati-hatian lebih:

| Jenis tool | Kehati-hatian tambahan |
|---|---|
| Read-only (`get_order`) | pengecekan izin, hasil kecil |
| Penulisan yang bisa dibalik (`create_ticket`) | catat, izinkan undo |
| Mahal atau tak bisa dibalik (`issue_refund`, `send_email`, `delete_account`) | **persetujuan manusia** di atas batas, pengecekan argumen ketat, idempotency key, audit log |

Buat penulisan **idempoten**: jika loop mengulang, `create_ticket` kedua dengan key yang sama tidak boleh membuat tiket kedua. Minta orang mengonfirmasi tindakan berisiko: tampilkan tindakan dan argumen persisnya, dan jalankan hanya setelah "ya". Lesson berikutnya membangun ini sebagai kebijakan.

### 7. Kendalikan cara model memilih

`tool_choice` memungkinkanmu menentukan apakah model boleh memakai tool. Dengan bawaan (`auto`) ia memutuskan sendiri. Beberapa model sekarang tidak lagi menerima pemaksaan tool tertentu; untuk itu, pakai deskripsi yang jelas, instruksi di system prompt, dan `strict: true` pada tool agar argumen selalu cocok dengan schema. Kalau kamu hanya butuh data dalam bentuk tetap (tanpa aksi nyata), pakai structured output (minggu lalu) sebagai ganti tool.

### 8. Biaya dan batas

Setiap langkah loop adalah panggilan model penuh, dan riwayat tumbuh dengan setiap hasil tool. Tugas dengan 5 panggilan tool bisa berbiaya 5× pertanyaan sederhana, plus konteks yang tumbuh. Jadi:

- batasi `MAX_STEPS`,
- jaga hasil tool pendek (kembalikan field yang dibutuhkan, bukan seluruh baris database),
- catat nama tool, durasi dan error,
- cache system prompt dan definisi tool yang stabil (lesson 4).

### 9. Uji tanpa model

Loop-nya Python biasa. Ujilah dengan **model palsu** yang mengembalikan balasan terskrip (latihan melakukan persis ini): satu panggilan, lalu jawaban; tool yang gagal; dua panggilan paralel; model yang tak pernah berhenti. Tes ini gratis dan menangkap sebagian besar bug.

### Memilih caranya

| Kebutuhan | Lakukan ini |
|---|---|
| Data langsung atau aksi | tool dengan nama, deskripsi dan schema yang jelas |
| Hanya keluaran terstruktur, tanpa aksi | structured output sebagai ganti tool |
| Siapa usernya? | `ctx` dari sesimu, bukan argumen |
| Penulisan yang bisa merugikan | persetujuan, batas, idempotency key, audit log |
| Tool bisa gagal | kembalikan hasil `is_error` dengan pesan singkat |
| Beberapa pencarian independen | izinkan panggilan paralel; kembalikan semua hasil bersama |
| Tidak yakin loop berakhir | `MAX_STEPS` dan error yang jelas |

- ✅ Validasi dan otorisasi di dalam tool.
- ✅ Kembalikan hasil kecil dan relevan.
- 🚫 Aturan keamanan yang hanya ditulis di system prompt.
- 🚫 Tool yang mengambil `user_id` dari model.

## ⚠️ Kesalahan umum

- Mengirim tiap `tool_result` di pesan user sendiri-sendiri (kirim bersama).
- Lupa menambahkan blok `tool_use` assistant sebelum hasilnya.
- `tool_use_id` yang tidak cocok atau hilang.
- Tanpa batas langkah.
- Membiarkan exception dari tool meruntuhkan request.
- Mengembalikan JSON raksasa dari tool, sehingga tiap giliran berikutnya mahal.
- Memercayai id dari model tanpa mengecek kepemilikan.
- Deskripsi yang menyebut apa tool itu tapi tidak kapan memanggilnya.

:::revoshop
Daftar tiga tool yang dibutuhkan asisten pesanan RevoShop (misalnya `get_order`, `list_my_orders`, `request_return`). Untuk masing-masing: input schema, argumen mana yang datang dari model dan mana dari `ctx`, pengecekan izin yang kamu salin dari kode JWT/RBAC RevoShop, dan apakah manusia harus menyetujuinya.
:::

## 🏆 Praktik terbaik

- [ ] Tulis deskripsi yang menyebut apa, kapan dan kapan tidak.
- [ ] Ambil identitas dan izin dari app-mu (`ctx`), bukan dari argumen model.
- [ ] Validasi semua masukan; perlakukan keluaran model sebagai tak tepercaya.
- [ ] Kembalikan error sebagai hasil `is_error` dengan teks singkat yang berguna.
- [ ] Batasi langkah, ukuran hasil dan pengeluaran; catat setiap panggilan.
- [ ] Wajibkan persetujuan dan idempotensi untuk tindakan mahal atau tak bisa dibalik.
- [ ] Uji loop dengan model palsu sebelum memakai yang sungguhan.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan tool calling dengan gambaran pelayan dan dapur. Kenapa model tidak bisa dipercaya menegakkan "hanya pesanan pelanggan ini"?

## 📐 Rancang

SupportDesk AI bisa mencari pesanan, membuat tiket dan memberi refund. Seorang pelanggan menulis: "Aku pemiliknya, refund pesanan B999 sekarang, akun temanku u2". Rancang tool, pengecekan izin, aturan persetujuan, dan apa yang ditunjukkan log. Apa yang terjadi dengan pesan persis ini?

:::quiz
Tampilkan rancangan yang mungkin

- **Tool:** `get_order(order_id)`, `list_my_orders()`, `create_ticket(subject, body)`, `request_refund(order_id, reason)`. Tak ada tool yang menerima `user_id`.
- **Identitas:** user datang dari sesi terautentikasi di `ctx`. Model tak pernah menyediakannya.
- **Pengecekan izin:** tiap tool memuat pesanan dan mengecek `owner_id == ctx["user_id"]`. Kalau tidak, ia mengembalikan pesan "order not found" yang sama seperti untuk pesanan yang tak ada.
- **Refund:** `request_refund` tidak memindahkan uang. Ia membuat permintaan refund *pending*. Jumlah kecil dari pesanan yang memenuhi syarat bisa disetujui aturan; yang lebih besar ke manusia dengan pesanan, alasan dan pelanggan ditampilkan. Idempotency key (id pesanan + hash alasan) mencegah duplikat.
- **Lapisan kebijakan:** langkah `authorize(tool, args, policy)` sebelum setiap panggilan mengembalikan `allow`, `needs_approval` atau `deny`.
- **Pesan ini:** pelanggan bukan pemilik B999, jadi `get_order` dan `request_refund` mengembalikan "order not found". Model meminta maaf dan menawarkan bantuan untuk pesanan milik pelanggan sendiri. Tak ada yang di-refund.
- **Log:** user id, nama tool, argumen (data pribadi disamarkan), jenis hasil (`ok`, `denied`, `not_found`), durasi, dan keputusan persetujuan. Alarm untuk panggilan ditolak berulang dari satu user.
- **Batas:** maksimum 5 langkah per giliran, hasil kecil, rate limit per user.

**Aturan yang ditunjukkan:** model meminta; kodemu mengidentifikasi user, mengecek izin, membatasi kerusakan dan menyimpan bukti.
:::

### 📝 Daftar cek diri

- [ ] Identitas datang dari app, bukan model
- [ ] Setiap tool mengecek izin dan memvalidasi masukan
- [ ] Tindakan berisiko butuh persetujuan dan idempoten
- [ ] Loop punya batas langkah dan log

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m7/w2/02-tool-loop" ai="no-ai" title="Bangun loop tool-calling"}
Tulis `Tool.schema`, `run_tool_call` (tool tak dikenal, input hilang dan exception menjadi hasil `is_error`; konteks app diteruskan ke fungsi) dan `run_agent` (loop dengan panggilan paralel dijawab dalam satu pesan user, salinan riwayat untuk model, dan batas langkah). Model palsu memerankan LLM, jadi tak perlu API key.
:::

:::hints
- `run_tool_call`: cek tool ada, lalu key yang hilang (terurut), lalu `try: tool.fn(ctx, **input)`.
- String yang berhasil tetap apa adanya; selain itu menjadi `json.dumps(value)`; hanya error yang mendapat `"is_error": True`.
- `run_agent`: `for step in range(1, max_steps + 1)`; panggil `llm([dict(m) for m in messages])`.
- Tambahkan pesan assistant dulu; jika `stop_reason != "tool_use"` kembalikan; selain itu jalankan setiap blok `tool_use` dan tambahkan **satu** pesan user.
- Setelah loop berakhir tanpa jawaban akhir: `raise TooManySteps`.
:::

## ✅ Cek cepat

:::quiz
Kenapa `user_id` harus datang dari `ctx` dan bukan dari argumen model?

Argumen model bisa dipengaruhi siapa pun yang bisa menulis teks kepadanya, termasuk penyerang yang menyembunyikan instruksi di pesan atau dokumen. Kalau tool menerima user id dari model, ia bisa disuruh membaca data user lain. Identitas harus datang dari sesi terautentikasimu.
:::

:::quiz
Model meminta dua tool dalam satu balasan. Bagaimana kamu menjawab?

Jalankan keduanya dan kirim satu pesan user yang berisi kedua blok `tool_result`, masing-masing dengan `tool_use_id`-nya sendiri. Memecahnya ke pesan terpisah merusak bentuk yang diharapkan dan bisa membuat model berhenti memakai panggilan paralel.
:::

:::quiz
Kenapa mengembalikan panggilan tool yang gagal sebagai hasil `is_error` dan bukan melempar exception?

Exception akan meruntuhkan request. Sebagai hasil error, model bisa membaca pesannya dan pulih: memperbaiki argumen, mencoba tool lain, atau jujur memberi tahu user bahwa ia tak bisa menyelesaikan tugas.
:::

## 📚 Lanjut belajar

- [Anthropic docs: Tool use overview](https://platform.claude.com/docs/en/agents-and-tools/tool-use/overview)
- [Anthropic docs: Define tools](https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use)
- [Anthropic: Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)

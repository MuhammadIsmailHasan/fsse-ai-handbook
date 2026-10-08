---
title: "Running Local Models with Ollama"
summary: "Jalankan model open-weight di komputermu sendiri dengan Ollama — apa untung dan ruginya, berapa memori yang dibutuhkan, cara memanggil HTTP API-nya dari Python, dan cara membungkusnya dengan cadangan cloud."
sourceHash: 77f1e28f7b50
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa itu **model open-weight**, dan apa yang dilakukan **Ollama**
- Kapan **model lokal** adalah ide bagus, dan kapan bukan
- Berapa **memori** yang dibutuhkan sebuah model (kuantisasi)
- Memanggil **HTTP API** Ollama dan membaca jawaban yang di-stream
- **Klien fallback** supaya app-mu bertahan saat model lokal mati

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Model open-weight** | Model yang bobotnya (angka hasil belajarnya) bisa diunduh |
| **Ollama** | Alat yang mengunduh dan menjalankan model terbuka di komputermu |
| **Parameter** | Angka hasil belajar dalam model; "7B" berarti 7 miliar |
| **Kuantisasi** | Menyimpan angka dengan lebih sedikit bit supaya model lebih kecil |
| **VRAM** | Memori di kartu grafis; cepat untuk model |
| **NDJSON** | Satu objek JSON per baris: cara Ollama men-stream |
| **Fallback** | Pilihan kedua yang dipakai saat yang pertama gagal |
| **Lisensi** | Aturan bagaimana kamu boleh memakai model |

## 🧠 Ide besarnya

Memakai model cloud itu seperti **memesan makanan antar**: tak ada dapur untuk dijalankan, pilihan beragam, dan kamu bayar per pesanan. Menjalankan model lokal itu seperti **masak di rumah**: bahan ada di rakmu, tak ada yang melihat apa yang kamu makan, dan piring kedua hampir gratis — tapi kamu butuh dapur, kamu yang mencuci, dan kamu mungkin tak bisa memasak sehebat restoran top.

Ollama adalah **alat dapur** yang membuat masak di rumah mudah: satu perintah untuk mengambil resep (mengunduh model), satu perintah untuk memasak (menjalankannya), dan API web kecil agar programmu bisa memesan.

## ❓ Kenapa ini penting

Model lokal memberimu hal yang tak bisa diberikan cloud:

- **Privasi:** teks privat tidak pernah meninggalkan mesinmu (berguna untuk kesehatan, hukum, dokumen internal, atau sekadar latihan dengan data nyata).
- **Bentuk biaya:** setelah punya perangkat keras, tiap request tambahan gratis. Bagus untuk belajar, uji coba dan pekerjaan massal.
- **Offline:** bekerja di pesawat atau jaringan tertutup.
- **Kendali:** kamu memilih file model yang tepat dan ia tak berubah di bawahmu.

Dan ada batas nyata: model kecil biasanya lebih lemah, bisa lambat tanpa GPU yang baik, dan kamu harus menjalankan serta memperbaruinya. Engineer yang baik tahu kedua sisi dan bisa **membangun app yang memakai salah satunya**.

## 📖 Langkah demi langkah

### 1. Pasang dan jalankan

Ikuti halaman instalasi di situs Ollama untuk sistemmu (macOS, Windows atau Linux). Lalu, di terminal:

```bash
ollama pull llama3.2        # download a model once (example name; pick a size your computer can run)
ollama run llama3.2         # chat in the terminal; type /bye to leave
ollama list                 # see what you have downloaded
```

Ollama juga menjalankan server kecil di mesinmu, **port 11434 secara bawaan**. Kalau port itu terpakai, atau kamu suka port tak biasa, atur `OLLAMA_HOST` (misalnya `127.0.0.1:11491`) sebelum menjalankannya. Biarkan terikat ke `127.0.0.1`: server lokal **tanpa login**, jadi jangan pernah membukanya ke internet.

### 2. Model sebesar apa yang bisa dijalankan komputermu?

Model adalah daftar angka yang sangat panjang. Memori yang dibutuhkan kira-kira:

```text
memory ≈ number of parameters × bytes per parameter   (+ room for the conversation)

7 billion parameters, 16-bit  → about 14 GB
7 billion parameters, 4-bit   → about 4–5 GB     ← "quantized": the usual way to run locally
70 billion parameters, 4-bit  → about 40 GB
```

**Kuantisasi** menyimpan tiap angka dengan lebih sedikit bit. File menyusut banyak, dan kualitas turun hanya sedikit untuk versi 4–8 bit. Model sering dipublikasikan dalam beberapa ukuran dan kuantisasi, dan halaman model menunjukkan kebutuhan masing-masing.

Patokan kasar:

- Jika muat di **memori GPU** (atau memori bersama Apple Silicon), ia cepat.
- Jika meluber ke RAM biasa, ia tetap jalan, tapi **jauh lebih lambat**.
- Jika sama sekali tak muat, pilih model lebih kecil.
- Percakapan (*konteks*) juga memakai memori. Bawaan ukuran konteks kecil, jadi atur ukuran konteks dengan sengaja bila promptmu panjang, atau awal promptmu bisa terbuang tanpa error.

Kecepatan diukur dalam **token per detik**. Baris terakhir response berisi hitungan dan waktu, jadi kamu bisa mengukur mesinmu sendiri.

### 3. HTTP API Ollama

Kodemu bicara dengan server lokal lewat HTTP biasa:

```text
POST http://localhost:11434/api/chat
{"model": "llama3.2",
 "messages": [{"role": "user", "content": "Hi"}],
 "stream": true,
 "options": {"temperature": 0.2}}
```

Jawaban datang sebagai **NDJSON**: satu objek JSON per baris.

```text
{"message": {"role": "assistant", "content": "Hel"}, "done": false}
{"message": {"role": "assistant", "content": "lo"},  "done": false}
{"message": {"role": "assistant", "content": ""},    "done": true, "done_reason": "stop", "prompt_eval_count": 14, "eval_count": 6}
```

Gabungkan `content` tiap baris. Baris terakhir punya `"done": true`, alasan berhenti, dan jumlah token (`prompt_eval_count` masukan, `eval_count` keluaran). Error datang sebagai `{"error": "..."}`.

```python
import json

def collect_ollama_stream(lines):
    text, done = [], None
    for line in lines:
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            raise LocalModelError("bad line from the model server") from None
        if "error" in obj:
            raise LocalModelError(obj["error"])
        text.append(obj.get("message", {}).get("content", ""))
        if obj.get("done"):
            done = obj
            break
    if done is None:
        raise LocalModelError("stream ended early")
    return {
        "text": "".join(text),
        "done_reason": done.get("done_reason", ""),
        "prompt_tokens": done.get("prompt_eval_count", 0),
        "completion_tokens": done.get("eval_count", 0),
    }
```

Ide yang sama dengan stream cloud: gabungkan potongan, perlakukan baris error sebagai error, dan perlakukan stream tanpa baris `done` akhir sebagai kegagalan.

Ollama juga menawarkan endpoint **kompatibel OpenAI** dan library Python resmi. Itu nyaman, tapi mengetahui bentuk HTTP polos membantumu men-debug apa pun.

### 4. Taruh antarmuka kecil di depannya

App-mu tidak perlu peduli dari mana jawaban datang. Definisikan satu antarmuka kecil dan tulis dua implementasi:

```python
class OllamaClient:
    def __init__(self, model, post, host="http://localhost:11434", options=None):
        self.model, self.post, self.host, self.options = model, post, host.rstrip("/"), options

    def complete(self, messages):
        payload = build_chat_payload(self.model, messages, options=self.options)
        try:
            lines = self.post(self.host + "/api/chat", payload)
            return collect_ollama_stream(lines)["text"]
        except ConnectionError:
            raise LocalModelError("local model server is not running") from None
```

Memasukkan `post` dari luar (bukan mengimpor library HTTP di dalam) adalah **dependency injection** lagi: tes memberinya fake dan tak butuh Ollama.

### 5. Fallback ke cloud

Model lokal bisa mati, sibuk, atau terlalu lemah untuk satu request. Bungkus dua klien:

```python
class FallbackClient:
    def __init__(self, primary, secondary):
        self.primary, self.secondary, self.last_used = primary, secondary, None

    def complete(self, messages):
        try:
            answer = self.primary.complete(messages)
            self.last_used = "primary"
            return answer
        except (LocalModelError, ConnectionError):
            answer = self.secondary.complete(messages)
            self.last_used = "secondary"
            return answer
```

Perhatikan apa yang ditangkapnya: hanya error yang berarti "server lokal tidak tersedia". `ValueError` dari bug-mu sendiri **tidak boleh** disembunyikan. Catat juga `last_used`, supaya kamu bisa melihat seberapa sering fallback terjadi dan berapa biayanya.

Putuskan aturan fallback dengan **aturan datamu** di kepala. Kalau alasan memakai model lokal adalah privasi, diam-diam mengirim teks privat yang sama ke penyedia cloud melanggar janji itu. Buat fallback eksplisit (pengaturan, baris log, atau "tanya user dulu").

### 6. Di mana model lokal cocok

| Cocok | Tidak cocok |
|---|---|
| Belajar, eksperimen, demo tanpa tagihan | penalaran sulit saat kualitas segalanya |
| Teks privat (dengan perangkat keras yang tepat) | lalu lintas tinggi dari banyak user di server kecil |
| Pekerjaan massal berulang (tagging, draf kasar) | tugas yang butuh kemampuan model besar terbaru |
| Alat offline, perangkat edge | saat kamu tak bisa menjalankan dan memperbarui server |
| Model embedding dan klasifikasi kecil | loop agen yang panjang dan kompleks |

Cek **lisensi** model apa pun sebelum memakainya di produk. Sebagian bebas untuk semua pemakaian, sebagian punya batas (ukuran perusahaan, bidang pemakaian, aturan penamaan).

### Memilih caranya

| Situasi | Lakukan ini |
|---|---|
| Latihan tanpa mengeluarkan uang | Ollama + model kecil |
| Data privat, aturan ketat | model lokal, diuji pada contoh nyatamu; eksplisit soal fallback |
| Produksi dengan banyak user | API cloud (atau self-hosting serius dengan GPU dan monitoring) |
| Tidak yakin cukup bagus | jalankan set uji 30 barismu di model lokal dulu |
| Model lokal mungkin mati | `FallbackClient`, dan catat siapa yang menjawab |
| Tugas berbeda, kebutuhan berbeda | rutekan: mudah → lokal, sulit → cloud |

- ✅ Jaga server di `127.0.0.1`; pakai port tak bawaan bila suka.
- ✅ Ukur token per detik dan kualitas pada contoh **-mu**.
- 🚫 Membuka Ollama ke internet.
- 🚫 Fallback cloud diam-diam untuk data yang harus tetap privat.

## ⚠️ Kesalahan umum

- Memilih model terlalu besar untuk mesin, lalu heran kenapa merangkak.
- Membiarkan ukuran konteks kecil, sehingga prompt panjang kehilangan awalnya.
- Menganggap "modelnya lokal" sebagai "app-nya aman".
- Menangkap semua exception di fallback (menyembunyikan bug sungguhan).
- Tidak mengecek lisensi.
- Membandingkan model lokal kecil dengan model cloud besar dan berharap kualitas setara.
- Hardcode `localhost:11434` di mana-mana, bukan satu pengaturan.

:::revoshop
RevoShop punya alamat dan nomor telepon pelanggan. Pilih satu tugas AI (misalnya menandai pesan support) dan putuskan: model lokal, model cloud, atau keduanya dengan fallback? Tulis aturan data yang menentukannya, perangkat keras yang kamu butuhkan, dan apa yang harus dilakukan fallback saat model lokal mati.
:::

## 🏆 Praktik terbaik

- [ ] Sembunyikan model di balik satu antarmuka kecil (`complete(messages) -> text`).
- [ ] Taruh host, port, nama model dan opsi di konfigurasi.
- [ ] Ikat server lokal ke `127.0.0.1`; jangan buka tanpa autentikasi.
- [ ] Ukur kecepatan dan kualitas pada contohmu sendiri sebelum memilih.
- [ ] Buat fallback eksplisit, tercatat, dan menghormati aturan data.
- [ ] Tangkap hanya error "server tidak tersedia" di fallback; biarkan bug muncul.
- [ ] Cek lisensi model dan pin nama serta versi model.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan gambaran pesan-antar versus masak di rumah ke seorang manajer. Beri satu alasan memilih opsi lokal dan satu alasan menolaknya.

## 📐 Rancang

Sebuah firma hukum ingin asisten yang meringkas dokumen klien. Dokumen **tidak boleh pernah meninggalkan jaringan firma**. Firma punya satu server kantor dengan satu GPU. Rancang susunannya: jenis model apa, bagaimana app berbicara dengannya, apa yang terjadi saat lambat atau mati, bagaimana kamu mengukur kualitas, dan apa yang kamu tolak lakukan.

:::quiz
Tampilkan rancangan yang mungkin

- **Model:** model open-weight, dikuantisasi agar muat di memori GPU, dilayani Ollama (atau server serupa) **di dalam jaringan kantor**, terikat ke alamat internal dengan autentikasi di depannya (reverse proxy dengan login), tidak terbuka ke internet.
- **App:** backend kecil dengan antarmuka `complete(messages)` yang sama; browser tidak pernah bicara langsung dengan model.
- **Kualitas:** set uji ~30 dokumen nyata (dianonimkan atau disetujui) dengan poin harapan berbentuk daftar cek; bandingkan dua atau tiga ukuran untuk kualitas dan token per detik; terima model lebih besar dan lebih lambat jika ringkasan tidak mendesak waktu.
- **Dokumen lambat:** proses file panjang per potongan (ringkasan map-reduce), pakai antrean agar satu pekerjaan besar tak menghalangi yang lain, dan tampilkan progres.
- **Mati atau kelebihan beban:** **tanpa fallback cloud**, karena aturan data. Sebagai gantinya: antrekan pekerjaan, ulangi, dan beri tahu user "siap dalam N menit". Beri alarm ke administrator.
- **Ukuran konteks:** atur dengan sengaja agar dokumen panjang tidak terpotong diam-diam.
- **Privasi:** catat hanya metadata (waktu, jumlah token), jangan pernah teks dokumen; enkripsi disk; batasi siapa yang bisa memanggil layanan.
- **Lisensi:** pastikan lisensi model mengizinkan pemakaian komersial untuk firma seperti ini.
- **Tolak:** mengirim teks dokumen apa pun ke API luar, bahkan "hanya untuk kasus sulit", kecuali firma dan klien menyetujui secara eksplisit.

**Aturan yang ditunjukkan:** aturan data menentukan arsitektur; fallback tidak boleh melanggarnya.
:::

### 📝 Daftar cek diri

- [ ] Aturan data tertulis dan dihormati
- [ ] Ukuran model sesuai perangkat keras
- [ ] Kasus lambat dan mati punya rencana
- [ ] Kualitas diukur pada contoh nyata

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m7/w1/05-local-llm" ai="no-ai" title="Klien model lokal dengan cadangan cloud"}
Bangun `build_chat_payload`, `collect_ollama_stream` (baca baris NDJSON, tangani baris kosong, baris error, baris rusak dan akhir dini), `OllamaClient` (panggilan HTTP dimasukkan sebagai `post`) dan `FallbackClient` (fallback hanya pada error server lokal; catat klien mana yang menjawab). Tak perlu Ollama: tes memakai baris palsu dan klien palsu.
:::

:::hints
- `build_chat_payload`: salin pesan dengan `[dict(m) for m in messages]`; tambahkan `"options"` hanya bila tidak kosong.
- `collect_ollama_stream`: `json.loads` tiap baris non-kosong; key `"error"` memunculkan `LocalModelError`; berhenti pada baris dengan `"done": true`.
- `OllamaClient.complete`: URL-nya `host.rstrip("/") + "/api/chat"`; ubah `ConnectionError` menjadi `LocalModelError("local model server is not running")`.
- `FallbackClient`: hanya `except (LocalModelError, ConnectionError)`; atur `last_used` setelah tiap keberhasilan.
:::

## ✅ Cek cepat

:::quiz
Apa itu kuantisasi, dan kenapa penting untuk model lokal?

Kuantisasi menyimpan angka-angka model dengan lebih sedikit bit (misalnya 4-bit, bukan 16-bit). File dan memori yang dibutuhkan menyusut banyak, sementara kualitas turun hanya sedikit. Inilah yang membuat model dengan miliaran parameter muat di komputer biasa.
:::

:::quiz
Kenapa fallback hanya boleh menangkap error "server tidak tersedia"?

Jika ia menangkap semua exception, bug sungguhan di kodemu (seperti `ValueError`) akan tersembunyi oleh peralihan diam-diam ke cloud, dan kamu tak akan pernah menyadari atau memperbaikinya. Tangkap hanya error yang berarti layanan lokal tak bisa menjawab.
:::

:::quiz
Kapan fallback cloud bisa menjadi pilihan yang salah?

Saat alasan memilih model lokal adalah privasi atau aturan hukum. Fallback diam-diam akan mengirim teks privat ke penyedia luar dan melanggar janji itu. Dalam kasus itu antrekan pekerjaan, ulangi, atau minta persetujuan.
:::

## 📚 Lanjut belajar

- [Ollama: documentation](https://github.com/ollama/ollama/tree/main/docs)
- [Ollama: API reference](https://github.com/ollama/ollama/blob/main/docs/api.md)
- [Hugging Face: Quantization overview](https://huggingface.co/docs/transformers/main/en/quantization/overview)

---
title: "Tokens, Context Window & Temperature"
summary: "Lihat bagaimana model bahasa sebenarnya bekerja — ia membaca dan menulis token, punya jendela konteks terbatas, memprediksi token berikutnya dengan sedikit keacakan — dan belajar menghitung token, memperkirakan biaya, memangkas riwayat chat, dan memilih temperature."
sourceHash: 27c4533fb260
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa itu **token**, dan kenapa token (bukan kata) menentukan **biaya** dan **batas**-mu
- Apa itu **context window**, dan kenapa chat panjang harus dipangkas
- Kenapa model **memprediksi** token berikutnya, dan apa artinya untuk fakta
- Apa yang dilakukan **temperature**, dan kapan mengubahnya
- Cara **menghitung token** dan **memperkirakan harga** sebuah panggilan

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **LLM** | Model yang dilatih dengan banyak teks untuk memprediksi apa yang datang berikutnya |
| **Token** | Potongan kecil teks: satu kata, bagian kata, atau simbol |
| **Context window** | Jumlah token terbanyak yang bisa dibaca dan ditulis model dalam satu panggilan |
| **Prompt** | Teks yang kamu kirim ke model |
| **Completion** | Teks yang dikirim balik model |
| **Temperature** | Kenop untuk seberapa acak pemilihan token berikutnya |
| **Logits** | Skor mentah yang diberikan model ke setiap token berikutnya yang mungkin |
| **Halusinasi** | Jawaban yang lancar tapi tidak benar |

## 🧠 Ide besarnya

Model bahasa itu **autocomplete super cepat dengan ingatan raksasa tentang bentuk teks**. Kamu memberinya teks. Ia memilih potongan berikutnya yang paling mungkin, menambahkannya, dan mengulang sampai berhenti. Ia tidak "mencari" fakta. Ia menulis apa yang cocok.

Tiga gambaran membantu:

- **Token adalah keping Lego.** Model tidak melihat huruf atau kata. Ia melihat keping kecil. Kamu membayar per keping, dan kotaknya punya batas ukuran.
- **Context window adalah meja kerja.** Semua yang bisa dipikirkan model harus muat di meja: pertanyaanmu, chat sejauh ini, dokumen yang kamu tempel, **dan ruang untuk jawabannya**. Saat meja penuh, sesuatu harus disingkirkan.
- **Temperature adalah kenop** antara penguji ujian yang ketat (selalu kata paling aman) dan pemain improvisasi (lebih banyak kejutan).

## ❓ Kenapa ini penting

Setiap fitur AI nyata menabrak tiga hal ini:

- **Biaya.** Kamu ditagih per token, masukan dan keluaran. Chat yang mengirim ulang 40 pesan tiap giliran cepat menjadi mahal.
- **Batas.** Kalau prompt ditambah jawaban tidak muat di jendela, panggilan gagal atau jawaban terpotong.
- **Keandalan.** Kalau kamu lupa bahwa model *memprediksi*, kamu memercayai fakta karangan. Kalau keacakan dibiarkan tinggi untuk tugas ekstraksi, masukan yang sama memberi hasil berbeda.

Engineer yang paham ini bisa memperkirakan tagihan sebelum rilis, menjaga chat tetap di dalam batas, dan menjelaskan jawaban yang salah.

## 📖 Langkah demi langkah

### 1. Teks menjadi token

Model memecah teks menjadi token dengan kosakata tetap (sebuah *tokenizer*). Kata umum satu token. Kata langka, nama dan kode terpecah jadi beberapa potongan.

```text
"Hello world"            → 2 tokens
"unbelievably"           → maybe 3 tokens:  "un" "believ" "ably"
"Terima kasih banyak"    → often MORE tokens than the English "Thank you very much"
```

Patokan kasar untuk bahasa Inggris: **1 token ≈ 4 karakter ≈ ¾ kata**. Bahasa lain, kode, dan angka biasanya butuh **lebih banyak** token untuk makna yang sama. Teks Indonesia agak lebih mahal daripada bahasa Inggris untuk ide yang sama, jadi ukur dengan teksmu sendiri.

Keluarga model berbeda memakai tokenizer berbeda. Perkiraanmu hanya tebakan. Untuk angka sebenarnya, tanyakan ke penyedia:

```python
count = client.messages.count_tokens(
    model=MODEL,
    messages=[{"role": "user", "content": "Explain recursion in one sentence."}],
)
print(count.input_tokens)
```

Dan setelah setiap panggilan, response memberi tahu apa yang ditagihkan:

```python
response = client.messages.create(model=MODEL, max_tokens=500, messages=messages)
print(response.usage.input_tokens, response.usage.output_tokens)
```

Catat kedua angka ini untuk **setiap** request. Keduanya dasar dari setiap penyelidikan biaya dan kecepatan.

### 2. Context window dipakai bersama

Jendela menghitung **semuanya**: system prompt, semua pesan sebelumnya, pesan barumu, hasil tool, **dan jawaban yang akan ditulis model**.

```text
context window  =  system prompt + chat history + new message + [room for the answer]
```

Dua batas yang berbeda:

| Batas | Artinya |
|---|---|
| **Context window** | masukan + keluaran bersama |
| **`max_tokens`** | paling banyak yang boleh *ditulis* model dalam panggilan ini |

Kalau jawaban mencapai `max_tokens`, ia berhenti di tengah kalimat dan `stop_reason` bernilai `"max_tokens"`. Periksa nilai ini. Jawaban yang terpotong diam-diam adalah bug yang umum.

Jendela sudah menjadi sangat besar (ratusan ribu sampai sejuta token pada beberapa model sekarang), tapi jendela besar tidak gratis:

- kamu **membayar** setiap token masukan di **setiap** panggilan,
- prompt panjang **lebih lambat**,
- model bisa melewatkan detail yang terkubur di tengah masukan yang sangat panjang.

Jadi tujuannya bukan "memenuhi jendela". Tujuannya "memasukkan token yang *tepat*".

### 3. Jaga chat tetap di dalam jendela

API tidak mengingat apa pun. Kamu mengirim ulang seluruh percakapan tiap giliran, jadi ia hanya tumbuh. Strategi sederhana dan jujur:

1. Simpan **system prompt** selalu.
2. Simpan **pesan terbaru**.
3. Buang giliran **tertua** lebih dulu (atau ganti dengan ringkasan pendek).
4. Sisakan ruang untuk jawaban.

```python
MESSAGE_OVERHEAD = 4

def total(messages):
    return sum(estimate_tokens(m["content"]) + MESSAGE_OVERHEAD for m in messages)

def fit_history(messages, max_context, reserve_for_output):
    budget = max_context - reserve_for_output
    system = [messages[0]] if messages and messages[0]["role"] == "system" else []
    rest = list(messages[len(system):])
    while len(rest) > 1 and (total(system + rest) > budget or rest[0]["role"] == "assistant"):
        rest.pop(0)                      # oldest first; the chat must start with a user message
    return system + rest
```

Pilihan lebih baik untuk chat panjang: **ringkas** giliran lama jadi satu pesan pendek, simpan fakta di **memori** yang dikendalikan app, atau **ambil** hanya pesan lama yang relevan (minggu berikutnya). Fitur penyedia seperti prompt caching membuat awalan yang panjang dan stabil menjadi lebih murah.

### 4. Model memprediksi; ia tidak mencari fakta

Untuk setiap posisi berikutnya, model memberi skor (sebuah *logit*) ke **setiap token dalam kosakatanya**. Fungsi bernama *softmax* mengubah skor menjadi probabilitas. Lalu satu token dipilih.

```text
after "The capital of France is" →  " Paris" 96%   " a" 1%   " the" 1% ...
```

Saat model sudah sering melihat sebuah fakta, jawaban yang benar menang. Saat belum, jawaban yang lancar tapi salah bisa menang. Itulah **halusinasi**. Model tak punya alarm bawaan untuk "aku tidak tahu".

Yang membantu (semuanya di module ini nanti): taruh sumber asli di prompt (RAG), minta kutipan, validasi keluaran, biarkan model memanggil tool, dan tulis eval.

### 5. Temperature: seberapa berani pemilihannya?

Sebelum softmax, skor dibagi dengan **temperature**:

```python
import math

def apply_temperature(logits, temperature):
    if temperature == 0:                       # always the best token
        best = max(logits, key=lambda k: logits[k])
        return {k: (1.0 if k == best else 0.0) for k in logits}
    top = max(logits.values())                 # subtract the max so exp() cannot overflow
    weights = {k: math.exp((v - top) / temperature) for k, v in logits.items()}
    total = sum(weights.values())
    return {k: w / total for k, w in weights.items()}
```

```text
scores  a=2.0  b=1.0  c=0.0
T = 0.3 → a 0.96  b 0.03  c 0.00     sharp: almost always "a"
T = 1.0 → a 0.67  b 0.24  c 0.09
T = 3.0 → a 0.45  b 0.32  c 0.23     flat: more surprises
```

| Tugas | Temperature |
|---|---|
| Ekstraksi, klasifikasi, JSON, kode, SQL | rendah (0 – 0,3) |
| Tanya jawab atas dokumen | rendah |
| Menulis, brainstorming, nama, variasi | sedang sampai tinggi |

Dua peringatan jujur:

1. **Bahkan pada 0 keluaran tidak dijamin identik.** Server menghitung secara paralel dan urutan penjumlahan kecil bisa berubah. Jangan membangun logika yang butuh teks identik sampai ke byte.
2. **Beberapa model sekarang tidak membiarkanmu mengaturnya.** Beberapa model baru menolak pengaturan sampling seperti `temperature` dan `top_p`, dan memberi kontrol lain (misalnya pengaturan *effort*). Baca dokumentasi model yang kamu pakai. Prompt dan validasimu lebih penting daripada kenop ini.

(`top_p` adalah kerabatnya: ia hanya mempertimbangkan kelompok token terkecil yang probabilitasnya berjumlah *p*. Ubah salah satu dari dua kenop itu, jangan keduanya.)

### 6. Biaya: rumus kecil

Penyedia mempublikasikan harga **per juta token**, dan **token keluaran lebih mahal daripada token masukan** (beberapa kali lipat itu umum).

```python
def request_cost(input_tokens, output_tokens, input_price_per_m, output_price_per_m):
    return input_tokens * input_price_per_m / 1_000_000 + output_tokens * output_price_per_m / 1_000_000
```

Sebuah ilustrasi (bukan daftar harga sungguhan): masukan $3 per juta, keluaran $15 per juta. Panggilan dengan 2.000 token masuk dan 500 keluar berbiaya 0,006 + 0,0075 = **$0,0135**. Pada 10.000 panggilan sehari itu **$135 sehari**. Kalikan sebelum rilis, bukan sesudahnya.

Cara memangkas biaya tanpa kehilangan kualitas: prompt lebih pendek, model lebih kecil untuk tugas mudah (lesson berikutnya), prompt caching untuk awalan berulang, `max_tokens` lebih rendah, dan tidak mengirim ulang apa yang tak dibutuhkan model.

Harga dan nama model sering berubah. Lihat halaman harga penyedia saat membangun, dan simpan harga di config, bukan di kode.

### Memilih caranya

| Situasi | Lakukan ini |
|---|---|
| Butuh jumlah token pasti | endpoint hitung dari penyedia, atau `usage` di response |
| Perkiraan cepat | sekitar 4 karakter per token (Inggris) — dan tambahkan margin aman |
| Chat makin panjang | buang giliran tertua, ringkas, atau ambil yang relevan |
| Keluaran terpotong di tengah kalimat | cek `stop_reason`; naikkan `max_tokens`; pendekkan jawaban |
| Masukan sama harus memberi hasil stabil | temperature rendah, plus validasi (bukan keterulangan persis) |
| Variasi kreatif | temperature lebih tinggi, atau minta beberapa pilihan |

- ✅ Catat `input_tokens` dan `output_tokens` untuk setiap panggilan.
- ✅ Sisakan ruang untuk jawaban sebelum memangkas riwayat.
- 🚫 Memercayai jawaban lancar sebagai fakta.
- 🚫 Mengirim ulang riwayat 200 pesan karena "jendelanya besar".

## ⚠️ Kesalahan umum

- Menghitung kata atau karakter lalu menyebutnya token, kemudian kaget dengan tagihan.
- Lupa bahwa **keluaran** juga masuk hitungan jendela.
- Tidak mengecek `stop_reason == "max_tokens"`.
- Membuang system prompt saat memangkas, atau memulai chat dengan pesan assistant.
- Memakai temperature tinggi untuk ekstraksi atau JSON.
- Mengira temperature 0 berarti keluaran selalu identik.
- Menaruh harga sebagai angka di dalam kode, bukan di config.

:::revoshop
Bayangkan asisten "tanya tentang pesanan ini" untuk RevoShop. (1) Apa yang masuk ke tiap panggilan: system prompt, JSON pesanan, riwayat chat? Perkirakan token tiap bagian (4 karakter ≈ 1 token). (2) Jika 1.000 pelanggan mengirim masing-masing 5 pertanyaan sehari, berapa jumlah token masukan dan keluaran per hari? (3) Bagian mana yang pertama kamu kecilkan untuk menghemat uang, dan bagian mana yang tak boleh dipangkas?
:::

## 🏆 Praktik terbaik

- [ ] Catat pemakaian token dan biaya per request, per fitur.
- [ ] Perkirakan biaya sebuah fitur di kertas sebelum membangunnya.
- [ ] Sisakan ruang keluaran, dan tangani `stop_reason == "max_tokens"` secara eksplisit.
- [ ] Pangkas riwayat dari yang tertua, simpan system prompt dan giliran terbaru.
- [ ] Pakai keacakan rendah untuk tugas terstruktur dan faktual, dan tetap validasi keluarannya.
- [ ] Simpan harga dan nama model di konfigurasi; cek ulang secara berkala.
- [ ] Perlakukan setiap jawaban model sebagai **klaim yang harus diverifikasi**, bukan fakta.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke rekan non-teknis kenapa AI "lupa" apa yang dikatakan pelanggan 30 pesan lalu, dengan gambaran meja kerja. Apa dua perbaikannya?

## 📐 Rancang

SupportDesk AI menyimpan chat panjang dengan tiap pelanggan. Percakapan bisa mencapai 60 pesan. Tiap panggilan menyertakan system prompt 1.500 token dan potongan artikel bantuan sekitar 3.000 token. Rancang bagaimana menjaga tiap panggilan di bawah anggaran, mencegah jawaban terpotong, dan menjaga biaya bulanan tetap bisa diprediksi.

:::quiz
Tampilkan rancangan yang mungkin

- **Anggaran per panggilan:** tentukan batas (misalnya 8.000 token masukan) dan sisakan sekitar 1.000 untuk jawaban. Hitung dengan `count_tokens` atau pakai `usage` dari panggilan sebelumnya.
- **Selalu simpan:** system prompt dan pesan user terbaru.
- **Pangkas:** buang giliran tertua lebih dulu; jaga chat dimulai dengan pesan user. Untuk chat sangat panjang, ganti giliran lama dengan **ringkasan berjalan yang pendek** (diperbarui tiap N giliran) dan simpan 6–10 pesan terakhir apa adanya.
- **Ambil, jangan tempel:** sertakan hanya 2–3 potongan artikel bantuan yang paling relevan untuk pertanyaan *ini*, bukan seluruh basis pengetahuan.
- **Cache awalan yang stabil:** system prompt dan instruksi tetap sama di tiap panggilan, jadi pakai prompt caching jika penyedia mendukung.
- **Jangan potong jawaban:** atur `max_tokens` cukup tinggi; jika `stop_reason == "max_tokens"`, tampilkan "lanjutkan" atau ulangi dengan instruksi jawaban lebih pendek.
- **Kendali biaya:** catat token per percakapan, tetapkan batas per percakapan dan alarm untuk total harian, dan pakai model lebih kecil untuk langkah klasifikasi yang mudah.
- **Temperature rendah** untuk jawaban yang harus mengikuti kebijakan.

**Aturan yang ditunjukkan:** jendela adalah meja kerja bersama yang berbayar — putuskan apa yang layak mendapat tempat di atasnya.
:::

### 📝 Daftar cek diri

- [ ] Aku menyisakan ruang untuk jawaban
- [ ] System prompt dan giliran terbaru tidak pernah dibuang
- [ ] Riwayat panjang diringkas atau diambil, bukan sekadar dikirim ulang
- [ ] Pemakaian token dicatat dan biaya bulanan diperkirakan

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m7/w1/01-token-budget" ai="no-ai" title="Anggaran token, biaya dan temperature"}
Tulis empat alat kecil: `estimate_tokens` (sekitar 4 karakter per token), `request_cost`, `fit_history` (pangkas pesan tertua, simpan pesan system dan pesan terakhir, mulai dengan pesan user) dan `apply_temperature` (softmax dengan temperature, termasuk temperature 0 dan tanpa overflow). Tak perlu API key.
:::

:::hints
- `estimate_tokens`: `math.ceil(len(text) / 4)`.
- `request_cost`: token × harga ÷ 1.000.000 untuk masukan dan untuk keluaran.
- `fit_history`: anggaran = `max_context - reserve_for_output`; pop pesan non-system **pertama** selama total melebihi anggaran atau pesan pertama berasal dari assistant; simpan setidaknya pesan terakhir.
- Satu pesan berbiaya `estimate_tokens(content) + MESSAGE_OVERHEAD`.
- `apply_temperature`: tangani `0` lebih dulu (one-hot); selain itu kurangi logit terbesar sebelum `math.exp`.
:::

## ✅ Cek cepat

:::quiz
Kenapa jawaban termasuk dalam anggaran context window?

Jendela membatasi masukan dan keluaran bersama. Model menulis jawabannya ke jendela yang sama, jadi kalau prompt sudah memenuhi sebagian besar jendela, ruang tersisa sedikit, dan jawaban terpotong di batas (`stop_reason: "max_tokens"`). Selalu sisakan ruang untuk keluaran.
:::

:::quiz
Apa yang dilakukan penurunan temperature?

Ia membuat distribusi probabilitas lebih tajam: token berskor tertinggi menjadi makin mungkin, sehingga keluaran lebih mudah diprediksi. Pada 0 model selalu memilih token teratas. Ini membantu untuk ekstraksi dan keluaran terstruktur, tapi tidak menjamin hasil identik atau fakta yang benar.
:::

:::quiz
Model memberi jawaban yakin yang salah. Kenapa ini bisa terjadi?

Model memprediksi kelanjutan teks yang mungkin; ia tidak memeriksa fakta. Jika jawaban yang benar langka dalam pelatihan atau tidak ada di prompt, kelanjutan yang lancar tapi salah bisa berprobabilitas tertinggi. Perbaiki dengan memberi sumber (RAG), meminta kutipan, memvalidasi keluaran dan memakai eval.
:::

## 📚 Lanjut belajar

- [Anthropic docs: Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting)
- [Anthropic docs: Context windows](https://platform.claude.com/docs/en/build-with-claude/context-windows)
- [Anthropic docs: Pricing](https://platform.claude.com/docs/en/about-claude/pricing)

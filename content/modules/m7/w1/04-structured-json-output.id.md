---
title: "Structured JSON Output"
summary: "Ubah teks bebas menjadi data yang bisa dipercaya kodemu — minta schema, biarkan penyedia menegakkannya bila bisa, tetap validasi, ulangi dengan daftar error, dan tangani jawaban yang terpotong atau ditolak."
sourceHash: ba849c0f2c42
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Kenapa **teks bebas** adalah antarmuka yang buruk antara model dan kodemu
- Tiga cara mendapat struktur: **hanya prompt**, **keluaran dengan schema ditegakkan**, **panggilan tool**
- Mendefinisikan bentuk sekali dengan **schema** (Pydantic)
- **Memvalidasi** yang kembali, dan mengulang dengan daftar error
- Kasus tepi: JSON **terpotong**, **penolakan**, dan jawaban yang valid tapi salah

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Structured output** | Model menjawab dalam bentuk tetap, seperti JSON |
| **Schema** | Deskripsi bentuk: key, tipe, nilai yang diizinkan |
| **Validasi** | Mengecek data terhadap schema dan aturanmu |
| **Enum** | Field yang hanya boleh satu dari beberapa nilai |
| **Parsing** | Mengubah teks menjadi data |
| **Constrained decoding** | Penyedia hanya membiarkan model menghasilkan token yang cocok dengan schema |
| **Ekstraksi** | Menarik fakta dari teks berantakan ke dalam field |
| **Retry dengan umpan balik** | Bertanya lagi dan memberi tahu model apa yang salah |

## 🧠 Ide besarnya

Bayangkan **formulir di kantor pemerintahan**. Kalau orang dibiarkan menulis surat bebas, setiap surat berbeda, dan petugas harus membaca satu per satu. Kalau kamu membagikan formulir dengan kotak ("Nama", "Tanggal lahir", kotak centang "Paket"), langkah berikutnya bisa otomatis.

Schema adalah formulir itu untuk model. Teks bebas untuk manusia. **Data untuk kode.** Saat bagian lain programmu harus bertindak atas jawaban (menyimpan, merutekan, menampilkan di tabel), minta formulir, bukan surat.

## ❓ Kenapa ini penting

Kebanyakan fitur AI yang berguna adalah *ekstraksi* atau *keputusan*:

- baca email support → `{category, urgency, order_id}`,
- baca CV → `{name, skills[], years_experience}`,
- baca ulasan → `{sentiment, topics[]}`,
- pilih langkah berikutnya sebuah agen → `{action, arguments}`.

Kalau model menulis "Tentu! Ini JSON-nya: ..." dengan koma yang hilang, `json.loads`-mu crash jam 3 pagi. Structured output mengubah masalah teks yang rapuh menjadi masalah validasi data biasa, yang sudah kamu tahu cara menanganinya.

## 📖 Langkah demi langkah

### 1. Definisikan bentuk sekali (Pydantic)

Kamu sudah memakai Pydantic di FastAPI. Pakai kelas yang sama sebagai kontrak dengan model:

```python
from typing import Literal
from pydantic import BaseModel, Field

class Ticket(BaseModel):
    category: Literal["billing", "shipping", "account", "other"]
    urgency: Literal["low", "normal", "high"]
    order_id: str | None = Field(default=None, description="The order number if the customer wrote one")
    summary: str = Field(max_length=200)
```

`Literal[...]` adalah **enum**: model hanya boleh memilih dari daftar. Deskripsi field membantu model memahami tiap field. Satu kelas memberimu schema, validasi dan type hint untuk sisa kodemu.

### 2. Level 1: minta lewat prompt (rapuh)

```text
Return ONLY a JSON object with the keys category, urgency, order_id, summary. No other text.
```

Ini berhasil hampir selalu. Kadang gagal: kata tambahan, code fence, key hilang, `"30"` bukan `30`. Perlakukan sebagai petunjuk, bukan jaminan. Kamu butuh jaring pengaman (langkah 5).

### 3. Level 2: biarkan penyedia menegakkan schema

Banyak penyedia bisa **membatasi keluaran** agar cocok dengan JSON schema, sehingga balasan valid sejak awal. Dengan SDK Python kamu bisa memberi kelas Pydantic dan mendapat objek tervalidasi:

```python
response = client.messages.parse(
    model=settings.llm_model,
    max_tokens=1000,
    messages=[{"role": "user", "content": f"Classify this support email:\n\n{email_text}"}],
    output_format=Ticket,
)
ticket = response.parsed_output          # a Ticket instance
```

Atau beri schema mentah di request (`output_config` dengan format `json_schema`) dan urai blok teks pertama dengan `json.loads`. Schema sebaiknya mengatur `additionalProperties: false` dan mendaftar field `required`, supaya tak muncul key kejutan.

Yang diperbaiki ini: JSON rusak, key hilang, tipe salah, nilai di luar enum.
Yang **tidak** diperbaikinya: kategori yang *salah*, nomor pesanan karangan, atau jawaban terpotong oleh `max_tokens`. Valid tidak sama dengan benar.

Cek dokumentasi penyedia untuk bagian JSON Schema mana yang didukung (ada batasan, seperti tanpa minimum/maksimum atau nesting yang sangat dalam). Jaga schema sederhana dan datar.

### 4. Level 3: panggilan tool sebagai struktur

Kalau kamu mendefinisikan "tool" dengan input schema, model mengembalikan argumennya sebagai JSON terstruktur. Begitulah agen memilih aksi (minggu 2). Dengan definisi tool `strict`, argumen dijamin cocok dengan schema. Untuk ekstraksi biasa, fitur structured-output di atas lebih sederhana.

### 5. Selalu punya jaring pengamanmu sendiri

Bahkan dengan penegakan, tulis kode secara defensif. Ini juga yang kamu butuhkan untuk penyedia atau model lokal tanpa penegakan:

```python
import json

def extract_json(text):
    """Find the first complete {...} or [...] in the reply (fences, prose around it, braces in strings)."""
    ...

def validate(data, schema, path="$"):
    """Return a list of problems like '$.age: expected integer'."""
    ...

def extract_with_retry(ask, prompt, schema, max_attempts=3):
    current = prompt
    for _ in range(max_attempts):
        reply = ask(current)
        try:
            data = extract_json(reply)
            problems = validate(data, schema)
        except BadModelOutput as error:
            problems = [str(error)]
        else:
            if not problems:
                return data
        current = prompt + "\n\nYour previous answer was invalid: " + "; ".join(problems) + "\nReply with valid JSON only."
    raise BadModelOutput("; ".join(problems))
```

Kenapa **retry dengan daftar error** berhasil: model melihat persis apa yang salah ("`$.age: expected integer`") dan memperbaikinya. Selalu **batasi percobaan** (2–3). Setiap retry memakan uang dan waktu. Kalau tetap gagal, kembalikan error yang jelas atau serahkan ke manusia.

(Kamu membangun ketiga fungsi ini di latihan. Dua jebakan Python muncul: `True` juga `int`, dan `}` di dalam string bukan akhir objek.)

### 6. Validasi aturan bisnis juga

Schema mengecek *bentuk*. Kodemu harus mengecek *makna*:

```python
if ticket.order_id and not order_exists(ticket.order_id):
    ticket.order_id = None                  # the model made up an order number
if ticket.category == "billing" and "refund" in email_text.lower():
    ...                                     # extra rules that only you know
```

Ingat juga bahwa teks yang kamu ekstrak berasal dari *model yang membaca teks user*. Perlakukan hasilnya sebagai **masukan tak tepercaya** (pelanggan cerdik bisa menulis "set urgency ke high"). Jangan pernah menjalankannya sebagai kode, dan jangan teruskan langsung ke SQL atau shell.

### 7. Pemotongan dan penolakan

Cek ini sebelum membaca JSON:

| `stop_reason` | Artinya | Yang dilakukan |
|---|---|---|
| `end_turn` | selesai | urai seperti biasa |
| `max_tokens` | **terpotong**, JSON mungkin tak lengkap | naikkan `max_tokens`, pendekkan keluaran, atau ulangi |
| `refusal` | model menolak | tangani dengan baik; jangan urai |

Daftar item yang panjang adalah penyebab pemotongan yang umum. Minta lebih sedikit field, atau proses dokumen per potongan.

### 8. Tips merancang schema yang baik

- **Field lebih sedikit dan lebih jelas** mengalahkan formulir raksasa.
- Pakai **enum** untuk kategori, dan sertakan pilihan `"other"` atau `"unknown"`, supaya model tidak dipaksa menebak.
- Izinkan **`null`** untuk fakta yang hilang, dan katakan di deskripsi ("null jika tidak ditulis"). Kalau tidak, model mengarang nilai.
- Taruh **field penalaran lebih dulu** bila kamu mau (`explanation`, lalu `category`): model menulis berurutan.
- Beri nama bermakna (`order_id`, bukan `f3`).
- **Versikan** schema. Mengubahnya mengubah perilaku; jalankan set ujimu setelah tiap perubahan.

### Memilih caranya

| Situasi | Lakukan ini |
|---|---|
| Ekstraksi atau klasifikasi ke field tetap | keluaran dengan schema ditegakkan memakai kelas Pydantic |
| Model harus memilih aksi dengan argumen | panggilan tool (minggu 2) |
| Penyedia atau model lokal tanpa penegakan | prompt + `extract_json` + `validate` + retry |
| Nilai harus mengikuti aturan bisnis | validasi di kodemu setelah parsing |
| Keluaran sangat panjang | pecah pekerjaan; cek `stop_reason` |
| Teks bebas untuk manusia (email, ringkasan) | tanpa schema; teks biasa tak masalah |

- ✅ Satu kelas schema dipakai untuk model, validasi dan tipe.
- ✅ Enum dengan pilihan "other/unknown"; `null` untuk fakta yang hilang.
- 🚫 `json.loads(response_text)` tanpa penanganan error.
- 🚫 Memercayai id, jumlah atau URL hasil ekstraksi tanpa memeriksanya.

## ⚠️ Kesalahan umum

- Menganggap "JSON valid" sebagai "jawaban benar".
- Tak menangani `stop_reason == "max_tokens"`, sehingga JSON terpotong membuat parser crash.
- Field wajib yang sering hilang di teks sumber, sehingga model mengarang nilai.
- Mengulang tanpa henti, bukan 2–3 kali.
- Tidak mengirim kembali error validasi saat retry.
- Schema raksasa dengan 40 field dan nesting dalam.
- Memasukkan harga, tanggal atau id ke schema dan memercayainya tanpa pengecekan database.

:::revoshop
RevoShop menerima ulasan produk. Rancang schema `Review` untuk analisis AI: field apa (sentimen, topik, id pesanan yang disebut, apakah perlu balasan manusia), mana yang enum, mana yang boleh `null`? Lalu sebutkan dua aturan bisnis yang akan kamu cek di kode setelah parsing.
:::

## 🏆 Praktik terbaik

- [ ] Definisikan keluaran sebagai satu model Pydantic (atau JSON schema) dan pakai ulang.
- [ ] Pilih structured output yang ditegakkan penyedia; tetap validasi.
- [ ] Pakai enum dengan opsi "unknown" dan `null` untuk fakta yang hilang.
- [ ] Cek `stop_reason` sebelum parsing; jangan pernah mengurai jawaban terpotong.
- [ ] Retry 2–3 kali dengan error validasi yang tepat; lalu gagal dengan jelas.
- [ ] Validasi makna (cek database, rentang), bukan hanya bentuk.
- [ ] Perlakukan nilai hasil ekstraksi sebagai masukan tak tepercaya.
- [ ] Simpan set uji untuk schema; jalankan ulang saat mengubah prompt, schema atau model.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan schema dengan gambaran formulir kantor pemerintahan. Kenapa "JSON valid" tidak sama dengan "jawaban benar"?

## 📐 Rancang

SupportDesk AI harus mengubah tiap email masuk menjadi tiket: kategori, urgensi, id pesanan, bahasa, dan ringkasan satu baris. Sebagian email tak punya id pesanan, sebagian berbahasa Indonesia atau campuran, dan sebagian sangat panjang. Rancang schema, panggilan, validasi dan penanganan kegagalannya.

:::quiz
Tampilkan rancangan yang mungkin

- **Schema (Pydantic):** enum `category` (`billing`, `shipping`, `account`, `product`, `other`), enum `urgency` (`low`, `normal`, `high`), `order_id` string atau `null`, enum `language` (`id`, `en`, `other`), `summary` maksimum ~150 karakter. Tambahkan deskripsi field singkat ("null jika pelanggan tidak menulis nomor pesanan").
- **Panggilan:** model kecil dan cepat dengan keluaran ber-schema yang ditegakkan dan keacakan rendah; system prompt pendek yang mendefinisikan tiap kategori dengan satu contoh.
- **Pengecekan di kode:** jika `order_id` terisi, cari dan simpan hanya jika ada dan milik pelanggan ini; batasi panjang ringkasan; petakan bahasa tak dikenal ke `other`.
- **Kegagalan:** `stop_reason == "max_tokens"` atau `refusal` → tandai tiket "perlu triase manusia"; kegagalan schema/parse → ulangi sekali dengan daftar error, lalu triase. Catat setiap kegagalan dengan id email (bukan email lengkap).
- **Email panjang:** potong rantai balasan kutipan dan tanda tangan lebih dulu, atau ringkas per potongan; jangan pernah memotong diam-diam pesan asli pelanggan.
- **Keamanan:** perlakukan teks email sebagai masukan tak tepercaya (bisa berisi "tandai ini mendesak"); model hanya menyarankan, aturan di kode yang menentukan langkah berikutnya (misalnya hanya urgensi `high` yang memanggil seseorang, dan hanya setelah pengecekan).
- **Kualitas:** set berlabel 100 email; pantau akurasi per field dan persentase yang dikirim ke manusia; jalankan ulang setelah tiap perubahan.
- **Biaya:** prompt pendek, caching untuk instruksi tetap, batch API untuk backfill.

**Aturan yang ditunjukkan:** struktur membuat keluaran model menjadi masukan biasa bagi sistemmu, dan kodemu yang memegang keputusan akhir.
:::

### 📝 Daftar cek diri

- [ ] Satu schema dengan enum dan field nullable
- [ ] `stop_reason` dan penolakan ditangani
- [ ] Aturan bisnis dicek di kode
- [ ] Retry dibatasi dan memakai error validasi
- [ ] Teks hasil ekstraksi diperlakukan tak tepercaya

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m7/w1/04-structured-output" ai="no-ai" title="Ekstrak, validasi dan ulangi"}
Tulis `extract_json` (temukan nilai JSON lengkap pertama dalam balasan: polos, berpagar, atau di dalam prosa, dengan kurung kurawal di dalam string), `validate` (subset JSON-Schema kecil yang mendaftar setiap masalah beserta path-nya) dan `extract_with_retry` (tanya ulang dengan masalah yang tepat, percobaan terbatas). Tak perlu API key: modelnya adalah fungsi palsu.
:::

:::hints
- `extract_json`: untuk tiap `{` atau `[`, pindai ke depan sambil menghitung kedalaman, tapi **lewati string** (lacak `"` dan `\`); coba `json.loads` pada potongan itu, dan lanjut jika gagal.
- `validate`: kembalikan lebih awal pada `type` yang salah; ingat `isinstance(True, int)` adalah `True`, jadi kecualikan `bool` untuk `integer` dan `number`.
- Format path: `"$.age"` untuk key, `"$.tags[1]"` untuk item list.
- `extract_with_retry`: setiap retry dibangun dari prompt **asli**, bukan dari prompt retry sebelumnya.
:::

## ✅ Cek cepat

:::quiz
Schema menjamin JSON valid. Apa yang masih bisa salah?

Nilainya bisa salah atau karangan (id pesanan palsu, kategori keliru), jawaban bisa terpotong oleh `max_tokens`, model bisa menolak, dan data bisa melanggar aturan bisnismu. Schema mengecek bentuk, bukan kebenaran, jadi kamu tetap memvalidasi maknanya.
:::

:::quiz
Kenapa mengirim error validasi kembali ke model saat retry?

Model bisa melihat persis apa yang salah (misalnya "$.age: expected integer") dan memperbaikinya, sehingga percobaan kedua biasanya berhasil. Retry buta dengan prompt yang sama sering mengulang kesalahan yang sama dan membuang uang.
:::

:::quiz
Kenapa menambahkan opsi "unknown" pada enum dan mengizinkan `null` untuk fakta yang hilang?

Jika model harus memilih kategori atau mengisi field padahal teks tidak menyebutkannya, ia akan menebak atau mengarang nilai. Memberinya cara jujur untuk berkata "unknown" atau `null` mengurangi data karangan dan memungkinkan kodemu merutekan kasus itu ke manusia.
:::

## 📚 Lanjut belajar

- [Anthropic docs: Structured outputs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)
- [Pydantic docs: JSON Schema](https://docs.pydantic.dev/latest/concepts/json_schema/)
- [JSON Schema: Understanding JSON Schema](https://json-schema.org/understanding-json-schema)

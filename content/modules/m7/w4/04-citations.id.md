---
title: "Citations"
summary: "Buat jawaban RAG bisa diperiksa — sumber bernomor, fitur sitasi bawaan penyedia, validasi nomor sitasi dan kutipan di kode, daftar sumber yang rapi, dan tahu apa yang bisa dan tak bisa dibuktikan pengecekan sitasi."
sourceHash: 65d2e91a6dcb
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Kenapa **sitasi** membangun kepercayaan dan membuat kesalahan terlihat
- Dua cara mendapatkannya: **sumber bernomor buatanmu sendiri** dan **fitur sitasi penyedia**
- Cara **memvalidasi** sitasi di kode: nomor tak dikenal, kalimat tanpa sitasi, kutipan palsu
- Cara **menampilkan sumber** dengan jelas ke user
- Apa yang **dibuktikan** sitasi, dan apa yang tidak

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Sitasi** | Penunjuk dari sebuah klaim ke sumber yang mendukungnya |
| **Nomor sumber** | Label `[1]`, `[2]` sebuah sumber di prompt |
| **Jawaban berpijak** | Jawaban yang klaimnya didukung sumber yang diberikan |
| **Kutipan langsung** | Kata-kata persis yang disalin dari sumber |
| **Sitasi palsu** | Sitasi ke sumber yang tak ada, atau tidak berkata demikian |
| **Cited text** | Bagian persis yang menurut penyedia mendukung sebuah klaim |
| **Faithfulness** | Seberapa baik jawaban tetap pada sumber |
| **Atribusi** | Memberi kredit dan tautan ke asal informasi |

## 🧠 Ide besarnya

Sitasi itu seperti **catatan kaki di makalah penelitian**. Klaim tanpa catatan kaki adalah "percayalah padaku". Klaim dengan catatan kaki adalah "periksa aku". Pembaca (dan timmu sendiri) bisa mengikuti catatan kaki, melihat sumber, dan memutuskan.

Tapi catatan kaki bisa salah. Murid ceroboh bisa menulis "[7]" padahal hanya ada tiga buku, mengutip buku yang berkata sebaliknya, atau menaruh tanda kutip di sekitar kata yang tak ditulis siapa pun. Jadi sistem yang baik melakukan yang dilakukan guru yang baik: ia **memeriksa catatan kaki**.

## ❓ Kenapa ini penting

- **Kepercayaan.** User memercayai jawaban lebih, dengan benar, saat bisa mengeklik sumbernya.
- **Debugging.** Saat jawaban salah, sitasi menunjukkan chunk mana yang menyesatkan model, atau bahwa tak ada.
- **Keamanan dan hukum.** Di setting support, kesehatan, keuangan atau hukum kamu perlu menunjukkan dari mana jawaban berasal.
- **Mendeteksi halusinasi.** Jawaban yang tidak mengutip apa pun, atau mengutip sesuatu yang tak ada, adalah bendera merah yang bisa kamu tangkap otomatis.

Dan murah: kebanyakan pengecekan adalah penanganan string biasa, tanpa panggilan model tambahan.

## 📖 Langkah demi langkah

### 1. Buat sitasi sendiri: sumber bernomor

Kamu sudah membangun ini di lesson arsitektur: taruh sumber di prompt dengan nomor, dan suruh model mengutipnya.

```text
Answer the question using ONLY the sources below. Cite them like [1], [2].
If the sources do not contain the answer, say you do not know.

<sources>
[1] (refund.md)
Refunds are paid back in 7 days after we receive the item.

[2] (shipping.md)
Shipping is free for orders above Rp 200.000.
</sources>

Question: How long does a refund take?
```

Jawaban yang baik: `Refunds are paid back in 7 days after we receive the item [1].`

Simpan tabel yang memetakan `[n]` ke chunk asli (id, judul, URL, halaman). Nomor di teks harus selalu bisa dipetakan balik ke sesuatu yang bisa kamu tampilkan.

### 2. Pakai fitur sitasi penyedia (bila tersedia)

Sebagian API model dapat menghasilkan sitasi untukmu. Kamu mengirim dokumen sebagai **blok dokumen** khusus dengan sitasi diaktifkan, dan response kembali terpecah menjadi potongan teks, masing-masing dengan bagian persis yang mendukungnya:

```python
response = client.messages.create(
    model=settings.llm_model,
    max_tokens=1000,
    messages=[{
        "role": "user",
        "content": [
            {
                "type": "document",
                "source": {"type": "text", "media_type": "text/plain", "data": REFUND_POLICY_TEXT},
                "title": "Refund policy",
                "citations": {"enabled": True},          # turn on citations for this document
            },
            {"type": "text", "text": "How long does a refund take?"},
        ],
    }],
)

for block in response.content:
    if block.type == "text":
        print(block.text)
        for citation in getattr(block, "citations", None) or []:
            print("  from:", citation.document_title, "|", citation.cited_text)
```

Yang kamu dapat: `cited_text` (kata-kata persis), `document_index` dan `document_title` (dokumen mana), dan **lokasi** (rentang karakter untuk teks polos, rentang halaman untuk PDF). Sifat bagusnya: teks yang dikutip **dijamin berasal dari dokumen yang kamu kirim**, jadi kutipan tak bisa dikarang, dan kamu tak perlu meminta model memformat penanda `[n]`.

Hal yang perlu diketahui (cek dokumentasi terbaru penyediamu):

- sitasi diaktifkan **per dokumen**, untuk semua atau tak satu pun dokumenmu dalam satu request,
- ia bisa bentrok dengan fitur lain, seperti memaksa format keluaran JSON ketat,
- kamu membayar token dokumen seperti masukan lain,
- pengecekanmu sendiri soal "apakah klaim cocok dengan bagian itu" tetap penting.

Pendekatan sumber bernomor buatanmu sendiri bekerja dengan model dan penyedia apa pun. Fitur bawaan adalah pilihan bagus saat tersedia.

### 3. Validasi nomornya

Jangan pernah percaya bahwa `[n]` valid. Cek di kode:

```python
import re

_BRACKET = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")

def extract_citations(answer):
    seen, out = set(), []
    for match in _BRACKET.finditer(answer):
        for number in re.split(r"\s*,\s*", match.group(1)):
            n = int(number)
            if n not in seen:
                seen.add(n)
                out.append(n)
    return out                               # source numbers in order of first use
```

```python
def _sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]

def validate_citations(answer, source_count):
    problems = []
    cited = extract_citations(answer)
    for n in cited:
        if not 1 <= n <= source_count:
            problems.append(f"unknown source [{n}]")
    sentences = _sentences(answer)
    if not cited:
        if sentences and source_count > 0:
            problems.append("no citations")
        return problems
    for sentence in sentences:
        if sentence.startswith(("I do not know", "I don't know", "I could not find")):
            continue                          # an honest refusal does not need a source
        if not _BRACKET.search(sentence):
            problems.append(f"uncited sentence: {sentence}")
    return problems
```

Tiga masalah yang ditangkapnya: **nomor yang tak ada**, jawaban **tanpa sitasi sama sekali**, dan **kalimat tanpa sitasi**. Saat menemukan masalah kamu bisa mengulang sekali ("setiap klaim butuh sitasi"), menampilkan peringatan, atau kembali ke "Saya tidak menemukan ini".

Hati-hati dengan ketatnya: tidak setiap kalimat butuh sumber (sapaan, "Ini yang saya temukan:"). Putuskan aturan untuk produkmu dan uji.

### 4. Validasi kutipan

Model kadang menaruh kata dalam tanda kutip yang tidak ada di sumber. Cek kutipan terhadap sumber, mengabaikan huruf besar-kecil, spasi dan tanda kutip:

```python
def normalize(text):
    text = re.sub(r"[\"'“”‘’]", "", text.lower())
    return re.sub(r"\s+", " ", text).strip()

def quote_supported(quote, source_text):
    q = normalize(quote)
    return bool(q) and q in normalize(source_text)

def find_fake_quotes(answer, sources):
    fake = []
    for quote in re.findall(r'"([^"]+)"', answer):
        if len(normalize(quote).split()) < 3:
            continue                          # very short quoted words are not claims
        if not any(quote_supported(quote, s) for s in sources):
            fake.append(quote)
    return fake
```

Jika kutipan ada di tidak satu sumber pun, hapus tanda kutipnya (itu parafrase), buat ulang, atau tandai jawabannya.

### 5. Tampilkan sumber ke user

Tampilan yang baik hanya menunjukkan sumber yang **benar-benar dikutip**, dalam urutan kemunculannya, dengan judul dan tautan:

```python
def render_sources(answer, sources):
    lines = []
    for n in extract_citations(answer):
        if 1 <= n <= len(sources):
            s = sources[n - 1]
            lines.append(f"[{n}] {s['title']} - {s['url']}")
    if not lines:
        return answer
    return answer + "\n\nSources:\n" + "\n".join(lines)
```

Tips rancangan:

- Jadikan `[1]` penanda yang **bisa diklik** dan membuka sumber, menggulir ke bagian yang dikutip bila bisa.
- Tampilkan **judul dan tanggal**, agar user bisa menilai kesegaran.
- Tampilkan **kutipan** (`cited_text`) saat hover atau di panel, untuk pengecekan cepat.
- Jangan daftar sumber yang terambil tapi tidak dikutip seolah mendukung jawaban.
- Ingat izin user: hanya tautkan dokumen yang boleh mereka buka.

### 6. Apa yang dibuktikan pengecekan sitasi, dan apa yang tidak

| Kodemu bisa mengecek | Kodemu tidak bisa sepenuhnya mengecek |
|---|---|
| nomor yang dikutip ada | apakah sumber **benar-benar mendukung** klaim |
| setiap kalimat punya sitasi | apakah klaim **lengkap** atau melewatkan pengecualian |
| kata yang dikutip muncul di sumber | apakah sumber **benar dan terkini** |
| sumber ada di prompt | apakah model **menggabungkan** dua sumber dengan salah |

Untuk kolom kanan kamu memakai **juri**: tinjauan manusia atas sampel, atau model kedua yang diberi klaim dan bagian yang dikutip dan menjawab "didukung / tidak didukung / sebagian" (minggu 5 membahas ini dengan cermat). Ambil sampel dan ukur; jangan menjalankannya membabi buta pada semuanya.

Catat juga kegagalan: jawaban dengan sitasi tidak valid adalah kasus uji yang berharga.

### Memilih caranya

| Situasi | Lakukan ini |
|---|---|
| Penyedia mana pun, kendali penuh | sumber bernomor `[n]` buatanmu sendiri + validasi di kode |
| Penyedia menawarkan sitasi dokumen | coba fitur bawaan; tetap validasi dan tampilkan sumber |
| Jawaban harus mengutip persis | cek kutipan terhadap sumber |
| Domain berisiko tinggi | tambahkan langkah juri dan tinjauan manusia atas sampel |
| Tampilan untuk user | penanda yang bisa diklik, judul, tanggal, kutipan saat hover |
| "Aku tidak tahu" yang jujur | izinkan tanpa sitasi |

- ✅ Simpan peta dari `[n]` ke chunk asli.
- ✅ Validasi nomor, klaim tanpa sitasi dan kutipan di kode.
- 🚫 Mendaftar setiap dokumen yang terambil sebagai "sumber".
- 🚫 Menganggap sitasi sebagai bukti bahwa klaim benar.

## ⚠️ Kesalahan umum

- Memercayai `[n]` tanpa mengecek ia ada.
- Menampilkan dokumen terambil yang tak pernah dipakai jawaban.
- Menomori sumber berbeda di prompt dan di UI.
- Membiarkan model mengarang URL atau judul: selalu render ini dari datamu sendiri.
- Mewajibkan sitasi di setiap kalimat, termasuk sapaan.
- Lupa meng-escape teks model sebelum menaruhnya di HTML.
- Percaya bahwa sitasi yang tampak benar berarti klaim yang benar.
- Tidak mencatat sitasi yang tidak valid.

:::revoshop
Tulis jawaban yang harus diberikan asisten RevoShop untuk "boleh retur sepatu yang sudah dipakai?" memakai dua sumber (kebijakan retur dan aturan higiene). Tambahkan penanda sitasi, daftar apa yang akan dicek validatormu (nomor, kalimat tanpa sitasi, kutipan), dan katakan apa yang tak bisa ditangkap validator.
:::

## 🏆 Praktik terbaik

- [ ] Beri nomor sumber di prompt dan simpan peta balik ke id chunk, judul, URL dan halaman.
- [ ] Render judul dan tautan sumber dari datamu sendiri, jangan dari teks model.
- [ ] Validasi nomor sitasi, kalimat tanpa sitasi dan teks kutipan di kode.
- [ ] Izinkan penolakan jujur tanpa sitasi.
- [ ] Tampilkan hanya sumber yang benar-benar dikutip, dengan penanda yang bisa diklik dan bagian yang dikutip.
- [ ] Pakai juri (sampel manusia atau model) untuk mengecek bahwa sumber mendukung klaim.
- [ ] Catat dan tinjau jawaban dengan sitasi tidak valid atau hilang.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan sitasi dengan gambaran catatan kaki. Kenapa "sitasinya ada" berbeda dari "klaimnya benar"?

## 📐 Rancang

Jawaban SupportDesk AI ke pelanggan harus menyertakan sumber. Minggu lalu seorang pelanggan mendapat "Refund butuh 3 hari [4]" padahal prompt hanya punya tiga sumber, dan kebijakan sebenarnya 7 hari. Rancang validasi, tampilan, penanganan kegagalan, dan pemantauan agar ini tak bisa sampai ke pelanggan lagi.

:::quiz
Tampilkan rancangan yang mungkin

- **Validasi di kode sebelum mengirim:** `extract_citations` menemukan `[4]`; `validate_citations(answer, 3)` melaporkan `unknown source [4]`. Cek juga kalimat tanpa sitasi dan kutipan terhadap tiga sumber.
- **Penanganan kegagalan:** pada masalah apa pun, ulangi sekali dengan memberi tahu model apa yang salah ("sumber 4 tidak ada; kutip hanya sumber 1–3"), validasi ulang; jika tetap gagal, kembalikan pesan aman ("Saya tidak bisa memverifikasi ini; ini artikel terkait" dengan tautan) dan serahkan ke manusia bila pelanggan meminta.
- **Cek klaim pendukung:** untuk angka (hari, harga) ekstrak angka dari jawaban dan konfirmasi angka yang sama muncul di chunk sumber yang dikutip (penjaga murah terhadap "3 hari" vs "7 hari"). Untuk topik berisiko tinggi, tambahkan panggilan juri kecil ("apakah bagian ini mendukung kalimat ini?").
- **Tampilan:** hanya sumber yang benar-benar dikutip, dirender dari databasemu dengan judul, tanggal pembaruan terakhir dan tautan; penanda membuka bagian itu.
- **Prompt:** sumber bernomor, "kutip seperti [1]", "kutip hanya nomor yang ada", dan "jika sumber tidak memuat jawabannya, katakan tidak tahu".
- **Pemantauan:** catat setiap kegagalan validasi dengan pertanyaan, id terambil dan jawaban; lacak persentase jawaban dengan sitasi tidak valid (alarm di atas 1%); tambahkan tiap kegagalan ke set uji.
- **Evaluasi:** set pertanyaan yang angka benarnya diketahui; ukur seberapa sering jawaban punya angka yang benar *dan* sitasi valid.
- **Akar masalah:** lihat juga retrieval: chunk kebijakan yang tepat (7 hari) mungkin tidak ada di prompt, itulah kenapa model mengarang angka.

**Aturan yang ditunjukkan:** biarkan kode memeriksa semua yang bisa (nomor, klaim tanpa sitasi, kutipan, angka), dan pakai juri untuk sisanya.
:::

### 📝 Daftar cek diri

- [ ] Nomor sitasi divalidasi terhadap jumlah sumber sebenarnya
- [ ] Judul dan tautan sumber datang dari datamu
- [ ] Ada fallback saat validasi gagal
- [ ] Kegagalan dicatat dan menjadi kasus uji

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m7/w4/04-citations" ai="no-ai" title="Sitasi yang bisa diperiksa"}
Tulis `extract_citations` (termasuk `[1, 3]`), `validate_citations` (nomor tak dikenal, tanpa sitasi, kalimat tanpa sitasi, penolakan jujur diizinkan), `normalize`, `quote_supported`, `find_fake_quotes` (kutipan minimal 3 kata yang ditemukan di tidak satu sumber pun) dan `render_sources` (hanya sumber yang benar-benar dikutip, berurutan). Tak perlu API key.
:::

:::hints
- Regex kurung: `\[(\d+(?:\s*,\s*\d+)*)\]`; pecah isinya pada koma.
- Jaga urutan kemunculan pertama dengan set `seen`.
- `validate_citations`: jangan laporkan "uncited sentence" saat "no citations" sudah dilaporkan.
- Kalimat: `re.split(r"(?<=[.!?])\s+", text.strip())`; lewati penolakan yang diawali "I do not know", "I don't know" atau "I could not find".
- `normalize`: huruf kecil, buang tanda kutip, ratakan spasi, strip.
- `render_sources`: lewati nomor di luar `1..len(sources)`; jika tak ada baris valid, kembalikan jawaban tanpa perubahan.
:::

## ✅ Cek cepat

:::quiz
Jawaban mengutip [5] tapi hanya ada 3 sumber di prompt. Apa yang kamu lakukan?

Perlakukan sebagai jawaban tidak valid: jangan tampilkan apa adanya. Ulangi sekali dengan koreksi yang menyuruh model mengutip hanya sumber yang diberikan, dan jika tetap gagal, tampilkan fallback aman. Catat kegagalan sebagai kasus uji.
:::

:::quiz
Pengecekan sitasi lolos. Apakah jawabannya benar?

Belum tentu. Pengecekan membuktikan nomor dan kutipan konsisten dengan sumber, bukan bahwa sumber benar-benar mendukung klaim, lengkap, atau terkini. Pakai juri (sampel manusia atau model) dan retrieval yang baik untuk itu.
:::

:::quiz
Kenapa merender judul dan URL sumber dari datamu sendiri, bukan dari teks model?

Model bisa mengarang judul atau tautan yang masuk akal. Kalau kodemu mencari nomor yang dikutip di tabel sumbernya sendiri, user hanya pernah melihat dokumen nyata yang diizinkan.
:::

## 📚 Lanjut belajar

- [Anthropic docs: Citations](https://platform.claude.com/docs/en/build-with-claude/citations)
- [Anthropic docs: Reduce hallucinations](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations)
- [Gao et al.: Enabling LLMs to Generate Text with Citations (paper)](https://arxiv.org/abs/2305.14627)

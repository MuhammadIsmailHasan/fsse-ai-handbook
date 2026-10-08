---
title: "RAG Architecture"
summary: "Pahami RAG dari ujung ke ujung: kenapa bukan fine-tuning atau prompt raksasa, dua alurnya, prompt berpijak dengan anggaran token, jalur jujur 'aku tidak tahu', dan titik biaya, kecepatan dan keamanan rancangannya."
sourceHash: 7f1978d00542
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa itu **RAG** dan kapan ia mengalahkan fine-tuning atau prompt yang sangat panjang
- **Komponen** dan alur satu request
- Cara **menyusun prompt yang berpijak**, dengan anggaran token
- Kenapa kamu butuh **jalur "tidak ada jawaban"**, dan cara membangunnya
- Titik **biaya, latency dan keamanan** sistem RAG
- **Varian** yang umum: naif, dengan penulisan ulang, hybrid, agentik

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **RAG** | Temukan teks relevan dulu, lalu biarkan model menjawab memakainya |
| **Retriever** | Bagian yang menemukan chunk relevan |
| **Generator** | Model bahasa yang menulis jawaban |
| **Grounding** | Membuat jawaban bertumpu pada sumber yang diberikan, bukan ingatan |
| **Context** | Teks yang kamu taruh di prompt untuk dipakai model |
| **Knowledge cutoff** | Tanggal setelah itu model tidak melihat apa pun |
| **Jalur penolakan** | Jawaban saat sumber tidak memuat jawabannya |
| **Agentic RAG** | Model memutuskan kapan dan apa yang dicari, memakai tool |

## 🧠 Ide besarnya

RAG adalah **ujian buka buku**. Model biasa mengerjakan ujian dari ingatan: mungkin ingat dengan baik, mungkin salah ingat, dan tak tahu apa pun yang lebih baru dari belajarnya. Dengan RAG kamu membiarkan murid membawa **halaman yang tepat** dari buku ke ruang ujian. Murid tetap harus membaca dengan baik, tapi kini jawabannya ada di meja, dan bisa bilang "lihat halaman 12".

Dua aturan membuat ujian buka buku itu adil: **halaman yang tepat harus ada di meja** (retrieval), dan murid harus **menjawab dari halaman itu**, bukan dari imajinasi, dan berkata "tidak ada di halaman ini" bila memang tidak ada (grounding).

## ❓ Kenapa ini penting

Model punya tiga batas yang diperbaiki RAG:

1. **Mereka tidak tahu data privatmu**: artikel bantuan, kontrak, katalog produk, tiket.
2. **Mereka menjadi usang**: apa pun setelah cutoff pelatihan, dan apa pun yang kamu ubah kemarin.
3. **Mereka mengarang**: saat ragu pun mereka tetap menulis jawaban lancar.

RAG membawa **fakta privat dan segar yang tepat** saat pertanyaan datang, memungkinkanmu menampilkan **sumber**, dan memungkinkanmu memperbarui pengetahuan dengan **mengubah dokumen** alih-alih melatih ulang model. Itulah kenapa kebanyakan asisten AI perusahaan adalah sistem RAG.

## 📖 Langkah demi langkah

### 1. RAG, fine-tuning, atau prompt sangat panjang?

| Pendekatan | Bagus untuk | Lemah di |
|---|---|---|
| **RAG** | fakta yang berubah, dokumen privat, kutipan, koleksi besar | tugas yang butuh membaca semuanya sekaligus; butuh retriever yang baik |
| **Prompt panjang** (tempel semuanya) | beberapa dokumen yang muat di jendela; prototipe | biaya dan kecepatan di setiap panggilan; "jarum" bisa hilang; tanpa kontrol akses |
| **Fine-tuning** | gaya, format, keahlian atau kosakata khusus | menambah fakta dengan andal (ia lupa dan berhalusinasi); pembaruan lambat dan mahal |
| **Tool / API** | data langsung dan persis (status pesanan, stok) | pertanyaan terbuka atas teks |

Aturan yang baik: **fakta → RAG atau tool; perilaku dan gaya → prompt, lalu fine-tuning bila benar-benar perlu.** Banyak sistem menggabungkan RAG dengan tool.

### 2. Dua alur

```text
INDEX (offline, repeatable)
  documents → clean → chunk → embed → store (vectors + text + metadata)

ANSWER (online, per question)
  question → [rewrite] → retrieve (vector + keyword, with filters) → [re-rank] → select chunks within a budget
           → build prompt (rules + numbered sources + question) → model → answer + citations → [check]
```

Perlakukan keduanya sebagai bagian terpisah yang bisa diuji sendiri: **retriever** (apakah menemukan chunk yang tepat?) dan **generator** (diberi chunk yang tepat, apakah menjawab dengan benar?). Minggu 3 dan 5 membahas pengukuran masing-masing.

### 3. Susun prompt

Prompt punya tiga bagian: aturan, sumber, pertanyaan.

```python
def build_prompt(question, chunks, max_context_tokens):
    used, total = [], 0
    for chunk in chunks:
        cost = estimate_tokens(chunk["text"])
        if total + cost > max_context_tokens:
            break                                           # stop at the first chunk that does not fit
        used.append(chunk)
        total += cost
    blocks = [f"[{i}] ({c['source']})\n{c['text']}" for i, c in enumerate(used, start=1)]
    sources = "<sources>\n" + ("\n\n".join(blocks) + "\n" if blocks else "") + "</sources>"
    prompt = (
        "Answer the question using ONLY the sources below. Cite them like [1], [2].\n"
        "If the sources do not contain the answer, say you do not know.\n\n"
        f"{sources}\n\n"
        f"Question: {question}"
    )
    return prompt, used
```

Kenapa bentuknya begini:

- **"ONLY the sources"** dan **"say you do not know"** menetapkan aturan grounding.
- **Sumber bernomor dengan asalnya** memungkinkan sitasi (lesson 4).
- **Tag** memisahkan data dari instruksi (minggu 2). Dokumen adalah *teks tak tepercaya*: ia juga bisa berisi instruksi ("abaikan semua aturan"), jadi prompt memperlakukannya sebagai data.
- **Anggaran token** menjaga panggilan di dalam jendela dan di bawah target biayamu. Putuskan berapa token konteks yang kamu izinkan, bukan hanya berapa chunk.
- Taruh **bagian stabil dulu** (aturan), dan **bagian berubah terakhir** (sumber, pertanyaan), yang juga membantu prompt caching.

### 4. Jalur "tidak ada jawaban"

Sistem RAG yang selalu menjawab kadang akan menjawab dari ketiadaan. Bangun kejujuran:

```python
NO_ANSWER = "I could not find this in the documents I have."

def answer(question, retriever, llm, *, k=5, min_score=0.0, max_context_tokens=1000):
    chunks = [c for c in retriever(question, k) if c["score"] >= min_score]
    if chunks:
        prompt, used = build_prompt(question, chunks, max_context_tokens)
        if used:
            text = llm(prompt)
            return {
                "answer": text,
                "sources": [{"n": i, "id": c["id"], "source": c["source"]} for i, c in enumerate(used, start=1)],
                "used_llm": True,
            }
    return {"answer": NO_ANSWER, "sources": [], "used_llm": False}
```

Yang dilakukannya untukmu:

- Kalau retrieval **tidak menemukan yang bagus**, model **tidak dipanggil**. Itu lebih murah, lebih cepat dan lebih aman daripada membiarkannya berimprovisasi.
- **Sumber yang kamu laporkan** persis chunk yang masuk ke prompt, tidak lebih.
- **Skor minimum** adalah pengaman yang bisa disetel (pilih dari contoh nyata). Jadikan "tidak ada jawaban" hasil normal yang diuji dan beri user langkah berikutnya ("hubungi support", "tanya dengan cara lain").

### 5. Ke mana waktu dan uang pergi

| Langkah | Biaya / waktu | Cara memperbaiki |
|---|---|---|
| Meng-embed pertanyaan | kecil | cache pertanyaan identik |
| Pencarian vektor + kata kunci | milidetik sampai puluhan ms | indeks, filter, batasi kandidat |
| Re-ranking | puluhan sampai ratusan ms | re-rank hanya 20–50 teratas |
| **Panggilan model dengan konteks** | **bagian terbesar**: token masukan × harga, plus tunggu token pertama | chunk lebih sedikit dan lebih baik; prompt caching untuk awalan stabil; model lebih kecil untuk pertanyaan mudah; stream jawaban |
| Pengecekan (sitasi, keamanan) | kecil | jalankan di kode, bukan dengan model lain |

Stream jawaban agar user melihat kata dalam sekitar satu detik. Catat waktu tiap langkah, dan token yang dipakai.

### 6. Keamanan dan izin

- **Penyaringan izin ada di retrieval.** User hanya boleh mendapat chunk yang boleh ia baca. Taruh tenant/role di filter pencarian; jangan pernah mengandalkan prompt untuk menyembunyikan yang sudah terambil.
- **Dokumen tak tepercaya.** Halaman web, PDF, atau unggahan user bisa berisi instruksi tersembunyi (indirect prompt injection). Tandai sebagai data, jangan beri model **tool yang kuat** di langkah yang sama, dan cek keluaran (minggu 2).
- **Privasi.** Apa pun yang kamu ambil dikirim ke penyedia model. Samarkan yang tak dibutuhkan model; cek ketentuan data penyedia.
- **Kualitas sumber.** Dokumen lama, draf atau bertentangan menghasilkan jawaban buruk. Indeks hanya konten yang disetujui, simpan tanggal, dan utamakan sumber segar.

### 7. Varian yang akan kamu temui

| Varian | Yang ditambahkan | Kapan |
|---|---|---|
| **RAG naif** | embed → top-k → prompt | versi pertama; bagus untuk demo |
| **+ penulisan ulang kueri** | model mengubah pertanyaan bertele-tele menjadi kueri pencarian yang baik (memakai riwayat chat) | chat multi-giliran ("yang merah bagaimana?") |
| **+ hybrid search + re-ranking** | kata kunci + vektor, lalu re-ranker | produk nyata dengan kode dan nama |
| **+ sitasi dan pengecekan** | sumber bernomor, validasi | jawaban apa pun yang dilihat user |
| **Agentic RAG** | model mendapat tool `search` dan memutuskan apakah, kapan dan berapa kali mencari, dan bisa mencoba lagi | pertanyaan sulit multi-langkah (minggu 6) |
| **Multi-hop / graph RAG** | mengikuti tautan antar dokumen atau entitas | pertanyaan yang menggabungkan fakta dari beberapa tempat |

Mulai dengan RAG naif **plus set uji**. Tambahkan satu perbaikan sekali, dan simpan hanya jika angkanya naik.

### 8. Daftar cek minimal untuk versi RAG pertama

1. Korpus kecil dokumen yang disetujui dan **set uji** 30+ pertanyaan nyata (sebagian tak bisa dijawab).
2. Job pengindeksan: chunk, embed, simpan dengan metadata.
3. Retrieval dengan filter, top-k, dan batas skor.
4. Prompt dengan sumber bernomor, aturan grounding dan aturan "tidak tahu".
5. Jalur "tidak ada jawaban" yang melewati model.
6. Sitasi ditampilkan, dan divalidasi di kode.
7. Log: pertanyaan, id dan skor terambil, id di prompt, jawaban, token, waktu.
8. Skrip evaluasi yang bisa dijalankan setelah tiap perubahan.

### Memilih caranya

| Situasi | Lakukan ini |
|---|---|
| Pengetahuan berubah atau privat | RAG |
| Hanya beberapa dokumen pendek | tempel ke prompt dulu; tambah RAG saat tumbuh |
| Data langsung (pesanan, stok) | panggilan tool, bukan RAG |
| Pertanyaan chat multi-giliran | tambahkan penulisan ulang kueri |
| Kode, nama, jargon | hybrid search |
| User harus memercayai jawaban | sitasi + validasi + jalur penolakan |
| Data beberapa pelanggan | filter izin di pencarian |

- ✅ Uji retrieval dan generasi secara terpisah.
- ✅ Jadikan "aku tidak tahu" hasil kelas satu.
- 🚫 Membiarkan model menjawab saat retrieval tak menemukan apa pun.
- 🚫 Menyaring izin di prompt.

## ⚠️ Kesalahan umum

- Menganggap RAG sebagai "tambahkan database vektor" dan melewatkan evaluasi.
- Selalu menjawab, bahkan dengan konteks kosong atau tidak relevan.
- Melaporkan sumber yang tidak ada di prompt.
- Menjejalkan 30 chunk ke prompt "biar aman" (biaya naik, kualitas sering turun).
- Mengindeks draf, duplikat dan halaman usang.
- Memakai prompt yang sama untuk pertanyaan berat-retrieval dan pertanyaan obrolan.
- Lupa bahwa teks hasil retrieval bisa membawa prompt injection.
- Tanpa log apa yang terambil, sehingga kegagalan tak bisa didiagnosis.

:::revoshop
Gambarkan asisten RAG untuk help center dan kebijakan retur RevoShop. Daftar dokumen yang kamu indeks, metadatanya, apa yang harus berupa tool (status pesanan), pesan "tidak ada jawaban", dan aturan izin bila penjual dan pembeli melihat dokumen berbeda.
:::

## 🏆 Praktik terbaik

- [ ] Pisahkan dan uji retriever dan generator.
- [ ] Beri nomor sumber, beri label asalnya, dan nyatakan aturan grounding di prompt.
- [ ] Anggarkan konteks dalam token; simpan hanya chunk terbaik.
- [ ] Lewati panggilan model dan jawab "tidak ditemukan" saat retrieval kosong atau lemah.
- [ ] Taruh filter izin dan tenant di retrieval.
- [ ] Perlakukan dokumen hasil retrieval sebagai data tak tepercaya.
- [ ] Catat id terambil, skor, isi prompt, token dan waktu.
- [ ] Evaluasi pada set uji tetap setelah setiap perubahan.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan RAG dengan ujian buka buku. Apa dua aturan yang membuatnya adil?

## 📐 Rancang

SupportDesk AI harus menjawab pertanyaan pelanggan dari 3.000 artikel bantuan dan kebijakan, untuk beberapa perusahaan klien. Jawaban harus mengutip sumber, tak boleh membuka dokumen perusahaan lain, menangani "aku tidak tahu", dan merespons dalam 3 detik sampai kata pertama. Rancang arsitekturnya: komponen, alur request, prompt, jalur penolakan, keamanan, dan apa yang dicatat.

:::quiz
Tampilkan rancangan yang mungkin

- **Komponen:** job pengindeksan (chunk, embed, simpan dengan `tenant_id`, bahasa, status), layanan retrieval (hybrid search dengan filter), pembangun prompt, panggilan model, validator sitasi, dan lapisan log/evaluasi.
- **Alur request:** autentikasi user dan temukan tenant → (opsional) tulis ulang pertanyaan memakai riwayat chat → hybrid search dengan filter `tenant_id`, `status = published` dan bahasa, 20 teratas → re-rank ke 5 teratas → buang chunk di bawah batas skor → bangun prompt dalam anggaran token → stream jawaban model → validasi sitasi dan kutipan → kembalikan teks + sumber.
- **Prompt:** aturan (jawab hanya dari sumber, kutip sebagai [n], katakan tidak tahu, balas dalam bahasa pelanggan), blok `<sources>` bernomor, dan pertanyaan; aturan stabil dulu untuk caching.
- **Jalur penolakan:** jika tak ada yang lolos batas skor, lewati model dan kembalikan pesan standar dengan langkah berikutnya ("bicara dengan agen"); jika model bilang tidak tahu, perlakukan sebagai jawaban sah dan tawarkan handoff.
- **Keamanan:** filter tenant dan izin di SQL untuk setiap retrieval; dokumen ditandai sebagai data; tanpa tool kuat di langkah ini; cek keluaran untuk data pribadi bocor; hanya artikel yang disetujui diindeks.
- **Latency (3 dtk sampai kata pertama):** panggilan embedding kecil, pencarian terindeks puluhan ms, re-rank hanya 20 kandidat, prompt caching pada aturan, dan **streaming** agar kata pertama muncul sementara sisanya ditulis.
- **Pencatatan:** pertanyaan, kueri hasil tulis ulang, id dan skor terambil, id di prompt, jawaban, validitas sitasi, token, waktu, dan tenant. Dipakai untuk debugging dan membangun set uji.
- **Evaluasi:** 200 pertanyaan berlabel (termasuk yang tak bisa dijawab) dicek untuk recall retrieval dan kebenaran jawaban secara terpisah, setelah tiap perubahan.

**Aturan yang ditunjukkan:** RAG adalah alur bagian-bagian kecil yang bisa diuji di sekitar satu panggilan model; kejujuran dan izin dirancang sejak awal, bukan ditambahkan belakangan.
:::

### 📝 Daftar cek diri

- [ ] Retrieval dan generasi bisa diuji terpisah
- [ ] Prompt membuat model berpijak dan menomori sumber
- [ ] Retrieval kosong atau lemah melewati model
- [ ] Izin ditegakkan di retrieval
- [ ] Semua yang dibutuhkan untuk debugging jawaban buruk dicatat

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m7/w4/01-rag-pipeline" ai="no-ai" title="Alur RAG"}
Tulis `estimate_tokens`, `build_prompt` (tata letak persis, sumber bernomor, berhenti di anggaran token) dan `answer` (retrieve, buang skor rendah, lewati model bila tak ada yang tersisa, laporkan persis sumber yang masuk ke prompt). Retriever dan model adalah fungsi palsu, jadi tak perlu API key.
:::

:::hints
- Tambahkan chunk berurutan selama total berjalan `estimate_tokens(text)` tetap `<= max_context_tokens`; `break` di chunk pertama yang tak muat.
- Beri nomor sumber dengan `enumerate(used, start=1)`.
- Blok sumber kosong persis `"<sources>\n</sources>"`.
- Di `answer`, filter dengan `score >= min_score` sebelum membangun prompt; jika `used` kosong, kembalikan hasil tanpa jawaban tanpa memanggil `llm`.
:::

## ✅ Cek cepat

:::quiz
Kapan sistem RAG tidak boleh memanggil model bahasa sama sekali?

Saat retrieval tidak mengembalikan yang relevan: tanpa chunk, semuanya di bawah batas skor, atau tak ada yang muat anggaran. Memanggil model tanpa sumber mengundang jawaban karangan. Kembalikan "tidak ditemukan" yang jelas dengan langkah berikutnya; lebih murah, lebih cepat dan jujur.
:::

:::quiz
Kenapa pengecekan izin harus bagian retrieval dan bukan prompt?

Prompt hanyalah teks yang bisa diabaikan atau ditipu model, dan setelah chunk ada di prompt, user bisa mengekstraknya. Kalau retrieval menyaring menurut hak user, chunk terlarang tak pernah sampai ke model.
:::

:::quiz
Kenapa menjaga retriever dan generator bisa diuji terpisah?

Saat jawaban salah kamu harus tahu bagian mana yang gagal. Jika chunk yang tepat tak pernah terambil, perbaiki retrieval; jika ada di prompt dan jawaban tetap salah, perbaiki prompt atau model. Mengukur keduanya bersama menyembunyikan penyebabnya.
:::

## 📚 Lanjut belajar

- [Anthropic docs: Search and retrieval (RAG)](https://platform.claude.com/docs/en/build-with-claude/search-results)
- [Lewis et al.: Retrieval-Augmented Generation (original paper)](https://arxiv.org/abs/2005.11401)
- [Anthropic: Introducing Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval)

---
title: "Why RAG Fails and How to Fix It"
summary: "Diagnosis jawaban RAG yang buruk langkah demi langkah — ada di data, terambil, bertahan di prompt, dipakai, dan didukung? — namai kegagalannya, pilih perbaikan yang tepat, dan ubah kegagalan menjadi rencana berprioritas dan set uji yang tumbuh."
sourceHash: 0952b15f8eb7
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- **Empat pertanyaan** yang menemukan lokasi kegagalan RAG
- **Taksonomi** kegagalan dan **perbaikan** untuk masing-masing
- Cara merekam **trace** untuk setiap request
- Cara **mengklasifikasi** kegagalan di kode dan membangun **rencana perbaikan**
- Kegagalan yang bersembunyi di luar alur: **data usang, konflik, injeksi**
- Cara mengubah setiap kegagalan menjadi **kasus uji**

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Trace** | Catatan tersimpan dari semua yang terjadi untuk satu request |
| **Retrieval miss** | Chunk yang tepat tak pernah ditemukan |
| **Faithfulness** | Jawaban hanya mengatakan hal yang didukung sumber |
| **Halusinasi** | Jawaban lancar yang tidak didukung apa pun |
| **Pertanyaan yang bisa dijawab** | Dokumen benar-benar memuat jawabannya |
| **Failure mode** | Cara khas sistem menjadi salah |
| **Akar masalah** | Langkah pertama yang salah |
| **Tes regresi** | Kasus tersimpan yang harus terus lulus |

## 🧠 Ide besarnya

Saat paket tidak sampai, kamu tidak berteriak ke "perusahaan pengiriman". Kamu **mengikuti pelacakan**: apakah dikemas? apakah keluar gudang? apakah sampai kota? apakah diantar ke pintu yang salah? Tiap pertanyaan menunjuk orang berbeda yang bisa memperbaikinya.

Jawaban RAG punya rantai yang sama: **Apakah faktanya ada di data? Apakah terambil? Apakah sampai ke prompt? Apakah model memakainya dengan benar?** Tanpa trace, kamu hanya melihat jawaban buruk dan mulai mengubah hal acak. Dengan trace, kamu tahu mata rantai mana yang putus, dan perbaikannya biasanya jelas.

## ❓ Kenapa ini penting

"AI memberi jawaban salah" bukan laporan bug. Tim yang tak bisa menemukan lokasi kegagalan menghabiskan berminggu-minggu berganti model, menulis ulang prompt dan chunk ulang tanpa perbaikan. Tim yang **melacak dan mengklasifikasi** menemukan bahwa dua atau tiga penyebab menjelaskan sebagian besar kegagalan, memperbaikinya, dan melihat lompatan besar. Ini juga melindungimu dari memperbaiki satu pertanyaan dan diam-diam merusak sepuluh lainnya.

## 📖 Langkah demi langkah

### 1. Empat pertanyaan

Untuk satu pertanyaan yang gagal, tanyakan berurutan:

```text
1. Is the answer in the corpus at all?          no → the right outcome is "I do not know" (content gap)
2. Was a right chunk RETRIEVED (in the pool)?   no → retrieval miss
3. Did it reach the PROMPT (after k / budget / re-ranking)?   no → dropped before the prompt
4. Was the answer correct and GROUNDED?         no → generation problem (not used / ungrounded / wrong refusal)
```

"Tidak" pertama adalah **akar masalah**. Perbaiki mata rantai itu dulu: mata rantai berikutnya tak bisa memperbaiki yang sebelumnya.

### 2. Taksonomi yang bisa dikodekan

| Kategori | Artinya | Perbaikan khas |
|---|---|---|
| `ok` | benar dan berpijak | tidak ada |
| `correct_refusal` | tak ada jawaban di korpus, dan sistem mengatakannya | tidak ada (ini sukses) |
| `hallucinated_answer` | tak ada jawaban di korpus, tapi sistem menjawab | jalur penolakan: batas skor, aturan "aku tidak tahu", cek bisa-tidaknya dijawab |
| `retrieval_miss` | chunk yang tepat tak pernah ditemukan | chunking, hybrid search, model embedding, penulisan ulang kueri, filter |
| `dropped_before_prompt` | ditemukan, tapi terpotong oleh `k`, anggaran token atau peringkat | naikkan `k` atau anggaran, tambah atau perbaiki re-ranker |
| `not_used` | chunk yang tepat ada di prompt, jawaban tetap salah | kata-kata prompt, kurangi noise, urutan chunk, model lebih kuat |
| `ungrounded` | benar tapi tidak didukung sumber | wajibkan sitasi, cek kutipan, aturan grounding lebih ketat |
| `wrong_refusal` | model berkata "aku tidak tahu" padahal punya jawabannya | longgarkan aturan penolakan, perjelas izin menjawab |

### 3. Rekam trace untuk setiap request

Kamu hanya bisa mendiagnosis apa yang kamu catat. Simpan satu catatan per request:

```python
trace = {
    "question": question,
    "rewritten_query": rewritten,          # if you rewrite
    "filters": filters,                    # tenant, language, status
    "retrieved": [{"id": ..., "score": ...}, ...],          # the pool, best first
    "reranked": [...],                                       # after re-ranking
    "prompt_ids": [...],                                     # exactly what went into the prompt, in order
    "prompt_tokens": ..., "output_tokens": ..., "model": ..., "prompt_version": ...,
    "answer": answer,
    "citations_valid": True,
    "timings_ms": {"retrieve": ..., "rerank": ..., "llm": ...},
}
```

Hati-hati dengan data pribadi di trace: samarkan, atur masa retensi, dan batasi siapa yang boleh membacanya.

Untuk **set ujimu**, setiap pertanyaan juga butuh kebenaran dasar: `relevant_ids` (chunk yang memuat jawaban; list kosong berarti tak bisa dijawab), dan penilaian apakah jawaban benar dan berpijak (oleh manusia, atau model juri yang sudah kamu cek terhadap manusia).

### 4. Klasifikasi di kode

```python
def diagnose(trace):
    relevant = set(trace["relevant_ids"])
    if not relevant:                                        # nothing in the corpus can answer this
        return "correct_refusal" if trace["refused"] else "hallucinated_answer"
    if not relevant & set(trace["retrieved_ids"]):
        return "retrieval_miss"
    if not relevant & set(trace["prompt_ids"]):
        return "dropped_before_prompt"
    if trace["refused"]:
        return "wrong_refusal"
    if trace["answer_is_correct"] and trace["answer_is_grounded"]:
        return "ok"
    if trace["answer_is_correct"]:
        return "ungrounded"
    return "not_used"
```

Aturannya berurutan seperti rantai pertanyaan, jadi **mata rantai putus pertama** yang menang. Lalu hitung di seluruh set uji dan buat rencana:

```python
def summarize(traces):
    counts = {c: 0 for c in CATEGORIES}
    answerable = hit = 0
    for t in traces:
        counts[diagnose(t)] += 1
        if t["relevant_ids"]:
            answerable += 1
            if set(t["relevant_ids"]) & set(t["retrieved_ids"]):
                hit += 1
    failures = [c for c in CATEGORIES if c not in ("ok", "correct_refusal")]
    worst = max(failures, key=lambda c: counts[c]) if any(counts[c] for c in failures) else None
    return {"total": len(traces), "counts": counts,
            "retrieval_recall": hit / answerable if answerable else 1.0, "worst": worst}
```

```python
def plan(traces):
    counts = summarize(traces)["counts"]
    rows = [(c, counts[c]) for c in CATEGORIES if c not in ("ok", "correct_refusal") and counts[c] > 0]
    rows.sort(key=lambda r: -r[1])                                  # biggest problem first
    return [f"{c} ({n}): {FIXES[c]}" for c, n in rows]
```

Keluaran khas:

```text
retrieval_miss (12): improve retrieval: chunking, query rewriting, hybrid search, embedding model, filters
dropped_before_prompt (5): raise k or the context budget, or fix the ranking / re-ranker so the right chunk is kept
hallucinated_answer (3): add a refusal path: a minimum score, an 'I do not know' instruction, an answerability check
```

Sekarang tim tahu apa yang dikerjakan lebih dulu. Perbaiki kategori terbesar, jalankan ulang set uji yang sama, dan bandingkan.

### 5. Penyebab lebih dalam di balik tiap kategori

**Retrieval miss.** Lihat pertanyaan yang meleset dan chunk yang seharusnya cocok.
- Kata-kata berbeda dari dokumen (sinonim, slang, bahasa lain) → embedding multibahasa, penulisan ulang kueri, multi-kueri.
- Memuat kode atau nama persis → hybrid search.
- Chunk kehilangan konteks (heading, nama produk) → jalur heading, chunk berkonteks.
- Filter mengecualikannya (tenant, bahasa, status salah) → cek logika filter.
- Dokumen tak pernah diindeks atau usang → cek ingestion dan kesegaran.

**Dropped before the prompt.** Cetak kolam dengan skor. Jika chunk yang tepat peringkat 12 dan kamu menyimpan 5, naikkan kolam untuk re-ranking atau perbaiki peringkat. Jika anggaran token yang memotongnya, pendekkan chunk, pakai parent-child, atau kompres.

**Not used.** Chunk yang tepat ada di prompt tapi jawaban salah. Lihat prompt: terlalu banyak chunk (noise)? chunk saling bertentangan? kalimat kunci di tengah? konflik instruksi? Coba chunk lebih sedikit, urutan lebih baik, instruksi lebih jelas ("jika dua sumber bertentangan, utamakan yang terbaru"), atau model lebih kuat.

**Hallucinated atau ungrounded.** Model mengisi celah dengan pengetahuannya sendiri. Perkuat aturan grounding, wajibkan sitasi dan validasi (lesson sebelumnya), tambahkan batas skor, dan uji dengan pertanyaan tak terjawab dengan sengaja.

**Wrong refusal.** Aturan penolakan terlalu bersemangat atau sumber sulit dibaca. Lunakkan instruksi ("jawab bila sumber memuat jawabannya, bahkan sebagian; katakan apa yang kurang"), dan cek kualitas chunk.

### 6. Kegagalan yang bukan di alur

| Masalah | Gejala | Perbaikan |
|---|---|---|
| **Data usang** | sitasi benar, fakta kedaluwarsa | metadata kesegaran, re-index terjadwal, utamakan sumber lebih baru, tampilkan tanggal |
| **Sumber bertentangan** | dua chunk tidak sepakat | selesaikan di sumber; beri tahu model aturannya (yang terbaru menang); tampilkan keduanya |
| **Pertanyaan multi-hop** | jawaban butuh fakta dari dua dokumen | retrieval per sub-pertanyaan (dekomposisi kueri), agentic RAG |
| **Pertanyaan ambigu** | user bermaksud hal lain | ajukan pertanyaan klarifikasi alih-alih menebak |
| **Prompt injection di dokumen** | jawaban mengikuti instruksi tersembunyi di chunk | tandai dokumen sebagai data, batasi tool, cek keluaran (minggu 2) |
| **Kebocoran izin** | jawaban menyebut dokumen yang tak boleh dilihat user | filter di retrieval; uji dengan dua user |
| **Angka dan tabel** | angka salah dari tabel | chunk sadar-tabel; hitung dengan tool, jangan membaca |
| **Ketidakcocokan bahasa** | pertanyaan bahasa Indonesia, dokumen bahasa Inggris | embedding multibahasa; jawab dalam bahasa user |

### 7. Ubah setiap kegagalan menjadi tes

Set uji terbaik tumbuh dari kegagalan nyata. Untuk setiap kegagalan:

1. Tambahkan pertanyaan, `relevant_ids` (atau "tidak ada"), dan fakta kunci yang diharapkan ke set uji.
2. Perbaiki penyebabnya.
3. Jalankan **seluruh** set (bukan hanya kasus baru) untuk memastikan tak ada yang lain rusak.
4. Simpan changelog singkat: "Menambah jalur heading → retrieval_miss 12 → 6".

Ambil juga sampel **keberhasilan** sesekali: jawaban benar dengan sitasi salah adalah kegagalan tersembunyi.

### 8. Ritme kerja

- **Harian/mingguan:** baca 20 trace acak dan 20 yang ditandai (jempol-bawah, tanpa jawaban, sitasi tidak valid).
- **Sebelum tiap rilis:** jalankan set uji penuh; bandingkan hitungan kategori dengan rilis lalu; blokir rilis bila ada regresi.
- **Dashboard:** persentase `retrieval_miss`, recall kolam, tingkat "tidak ada jawaban", validitas sitasi, token per jawaban, latency p95.
- **Satu perubahan sekali**, dengan angka dicatat.

### Memilih caranya

| Gejala | Lihat dulu |
|---|---|
| Dokumen yang tepat ada, jawaban salah | empat pertanyaan: terambil? di prompt? |
| Jawaban dengan fakta salah yang yakin | aturan grounding, batas skor, validasi sitasi |
| Banyak "aku tidak tahu" untuk pertanyaan yang bisa dijawab | recall retrieval, aturan penolakan |
| Bagus untuk pertanyaan pendek, buruk untuk lanjutan chat | penulisan ulang kueri |
| Bagus untuk prosa, buruk untuk tabel atau kode | chunk sadar-tabel, hybrid search |
| Kualitas turun setelah pembaruan konten | pengindeksan, duplikat, chunk usang |

- ✅ Temukan mata rantai putus pertama sebelum mengubah apa pun.
- ✅ Catat kolam, chunk prompt, skor dan versi.
- 🚫 Mengganti model sebelum melihat satu trace pun.
- 🚫 Memperbaiki kegagalan tanpa menambahkannya ke set uji.

## ⚠️ Kesalahan umum

- Menilai sistem hanya dari jawaban akhirnya.
- Mengubah beberapa hal sekaligus, sehingga penyebab peningkatan tak diketahui.
- Set uji tanpa pertanyaan tak terjawab (halusinasi tetap tak terlihat).
- Menyalahkan model untuk apa yang sebenarnya retrieval miss.
- Hanya mencatat jawaban, bukan id dan skor yang terambil.
- Lupa bahwa dokumen "yang benar" berubah saat korpus berubah.
- Memperbaiki keluhan yang paling nyaring, bukan kategori terbesar.
- Tanpa menjalankan regresi setelah perbaikan.

:::revoshop
Bayangkan asisten RevoShop-mu menjawab "Pengiriman ke Papua gratis" padahal kebijakan sebenarnya "Rp 50.000". Jalani empat pertanyaan: apa yang kamu cek di tiap langkah, field trace apa yang kamu butuhkan, dan kategori serta perbaikan mana yang paling mungkin jika chunk kebijakan yang tepat berperingkat 8?
:::

## 🏆 Praktik terbaik

- [ ] Catat trace penuh untuk setiap request (data pribadi disamarkan).
- [ ] Diagnosis berurutan: korpus → terambil → di prompt → benar dan berpijak.
- [ ] Simpan pertanyaan tak terjawab di set ujimu.
- [ ] Hitung kategori kegagalan dan perbaiki yang terbesar dulu.
- [ ] Ubah satu hal sekali dan jalankan ulang seluruh set uji.
- [ ] Ubah setiap kegagalan nyata menjadi tes regresi.
- [ ] Lacak recall kolam, validitas sitasi dan tingkat "tidak ada jawaban" dari waktu ke waktu.
- [ ] Tinjau juga keberhasilan acak, bukan hanya kegagalan.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan debugging RAG dengan gambaran pelacakan paket. Kenapa mata rantai putus pertama yang harus diperbaiki?

## 📐 Rancang

Bulan lalu skor kualitas SupportDesk AI turun dari 82% ke 74% setelah tim konten mengunggah 400 artikel baru. Pelanggan mengeluh soal jawaban usang dan soal "Saya tidak menemukan ini" untuk hal yang ada. Rancang penyelidikannya: apa yang dilihat, dalam urutan apa, penyebab yang mungkin, dan cara mencegah terulang.

:::quiz
Tampilkan rancangan yang mungkin

- **Mulai dari data, bukan tebakan:** jalankan set uji 200 pertanyaan dan klasifikasikan tiap hasil dengan `diagnose`; bandingkan hitungan dengan bulan lalu. Harapkan kenaikan `retrieval_miss`, `dropped_before_prompt` dan mungkin `not_used`.
- **Kemungkinan penyebab 1: duplikat dan versi lama.** 400 artikel baru mungkin menduplikasi atau menggantikan yang lama. Cek berapa banyak hampir-duplikat; 5 teratas mungkin kini berisi dua salinan dan versi lama → deduplikasi, utamakan yang terbaru menurut `updated_at`, dan arsipkan artikel yang digantikan.
- **Kemungkinan penyebab 2: kolam sesak.** Lebih banyak dokumen berarti lebih banyak kecocokan mirip; chunk yang tepat turun ke peringkat 6–12 → perbesar kolam, tambah atau setel re-ranker.
- **Kemungkinan penyebab 3: metadata hilang.** Jika artikel baru tak punya `product`, `language` atau `status`, filter mengecualikannya atau membiarkan draf masuk → validasi metadata saat ingestion; tolak artikel tanpa field wajib.
- **Kemungkinan penyebab 4: chunking berubah.** Apakah job ingestion memakai chunker atau pengaturan berbeda untuk file baru? Cek `chunker_version` dan `embedding_model` pada chunk baru.
- **Jawaban usang:** temukan jawaban yang chunk kutipannya lama padahal ada artikel lebih baru; tambahkan kesegaran ke peringkat dan tampilkan tanggal.
- **"Saya tidak menemukan ini":** lihat daftar `retrieval_miss` dan buka misses dengan tangan: ketidakcocokan kata, filter, atau dokumen hilang/tak terindeks.
- **Pencegahan:** daftar cek ingestion dan pengecekan otomatis (metadata wajib, duplikat, jumlah chunk, model embedding), evaluasi di CI pada setiap impor konten, alarm saat `retrieval_recall` atau campuran kategori bergeser, dan tiap kegagalan ditambahkan ke set uji.
- **Komunikasi:** laporkan akar masalah dengan angka, perbaikannya, dan hasil uji sebelum/sesudah.

**Aturan yang ditunjukkan:** klasifikasikan dulu, perbaiki penyebab terbesar, buktikan dengan set uji yang sama, dan otomatiskan pengecekan agar tak pernah mengejutkanmu lagi.
:::

### 📝 Daftar cek diri

- [ ] Penyelidikan dimulai dari trace dan set uji
- [ ] Kegagalan diklasifikasi menurut mata rantai putus pertama
- [ ] Perbaikan diurutkan menurut dampak dan diverifikasi dengan menjalankan ulang set
- [ ] Ada otomatisasi untuk menangkap regresi berikutnya

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m7/w4/05-rag-diagnosis" ai="no-ai" title="Diagnosis kegagalan RAG"}
Tulis `diagnose` (aturan berurutan: tak bisa dijawab, retrieval miss, dropped before the prompt, wrong refusal, ok, ungrounded, not used), `summarize` (hitungan untuk setiap kategori, recall retrieval pada pertanyaan yang bisa dijawab, kategori terburuk) dan `plan` (daftar kerja terurut menurut besarnya). Tiap trace adalah dict biasa, jadi tak perlu API key.
:::

:::hints
- Cek `relevant_ids` dulu: kosong berarti pertanyaan tak bisa dijawab (`correct_refusal` atau `hallucinated_answer`).
- Lalu bandingkan himpunan: `relevant & retrieved_ids`, lalu `relevant & prompt_ids`.
- Setelah dua itu, `refused` berarti `wrong_refusal`; selain itu gabungkan `answer_is_correct` dan `answer_is_grounded`.
- `summarize`: mulai hitungan dari `{c: 0 for c in CATEGORIES}`; penyebut recall hanya menghitung trace dengan `relevant_ids` tidak kosong.
- `worst`: abaikan `ok` dan `correct_refusal`; dengan `max` pada urutan `CATEGORIES`, seri dimenangkan kategori lebih awal.
- `plan`: `sort(key=lambda r: -r[1])` yang stabil menjaga urutan kategori saat seri.
:::

## ✅ Cek cepat

:::quiz
Chunk yang tepat berperingkat 9 di kolam, dan prompt menyimpan 5 chunk. Kategori apa itu, dan apa perbaikannya?

`dropped_before_prompt`. Retrieval menemukannya, tapi peringkat dan `k`/anggaran memotongnya. Perbaiki peringkat (re-ranker, hybrid search), atau naikkan jumlah chunk atau anggaran, sambil mengawasi biaya token.
:::

:::quiz
Kenapa set uji harus menyertakan pertanyaan yang tak bisa dijawab dokumen?

Tanpanya, halusinasi tak terlihat: sistem tak mendapat penalti karena menjawab dari imajinasi. Pertanyaan tak terjawab memungkinkanmu mengukur apakah sistem dengan benar berkata "aku tidak tahu", dan menyetel batas skor serta aturan penolakan.
:::

:::quiz
Kualitas turun setelah unggahan konten besar. Apa yang kamu cek pertama?

Klasifikasikan hasil set uji dan bandingkan hitungan kategori dengan sebelumnya. Temuan khas adalah duplikat dan versi lama yang memenuhi hasil teratas, metadata hilang yang merusak filter, atau chunker atau model embedding berbeda dipakai untuk file baru.
:::

## 📚 Lanjut belajar

- [Anthropic docs: Reduce hallucinations](https://platform.claude.com/docs/en/test-and-evaluate/strengthen-guardrails/reduce-hallucinations)
- [Barnett et al.: Seven Failure Points When Engineering a RAG System (paper)](https://arxiv.org/abs/2401.05856)
- [Ragas documentation](https://docs.ragas.io/)

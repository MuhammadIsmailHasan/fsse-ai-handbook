---
title: "Retrieval & Reranking"
summary: "Ubah pencarian pertama yang kasar menjadi konteks yang bersih — tulis ulang kueri, ambil luas lalu persempit, buang duplikat, tambah variasi dengan MMR, re-rank dengan penilai yang lebih pintar, dan urutkan chunk agar model benar-benar memakainya."
sourceHash: 15ef70977048
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Ide **dua tahap**: ambil luas (recall), lalu persempit (precision)
- **Penulisan ulang kueri** dan pencarian multi-kueri
- **Keragaman** dengan MMR dan membuang **hampir-duplikat**
- **Re-ranking** dengan penilai yang lebih pintar dan lebih lambat
- Kenapa **urutan** di prompt penting ("lost in the middle")
- Cara **mengevaluasi dan menyetel** tiap tahap

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Retrieval tahap pertama** | Pencarian cepat yang menemukan banyak kandidat |
| **Re-ranker** | Model lebih lambat yang membaca kueri + kandidat dan menilai kecocokannya |
| **Cross-encoder** | Re-ranker yang membaca kueri dan teks bersama |
| **Penulisan ulang kueri** | Mengubah kata-kata user menjadi kueri pencarian yang lebih baik |
| **MMR** | Maximal Marginal Relevance: relevan tapi tidak berulang |
| **Hampir-duplikat** | Dua chunk yang mengatakan hampir hal yang sama |
| **Anggaran jendela konteks** | Berapa token sumber yang kamu izinkan di prompt |
| **Lost in the middle** | Model memakai awal dan akhir prompt panjang lebih baik daripada tengahnya |

## 🧠 Ide besarnya

Perekrutan adalah gambaran yang bagus. Pertama kamu **menyaring CV dengan cepat**: filter cepat yang menyisakan 50 orang dari 5.000. Murah, dan boleh agak kasar, selama orang-orang baik *ada* di 50 itu. Lalu kamu **mewawancarai** beberapa: lambat, cermat, mahal, dan hanya untuk daftar pendek. Akhirnya kamu menaruh kandidat terbaik **di panel** dalam urutan yang masuk akal.

Retrieval bekerja sama: pencarian cepat menemukan 50 kandidat (jaring dilebarkan, agar recall tinggi), re-ranker yang cermat mengurutkannya (precision), kamu membersihkan daftar pendek (tanpa duplikat, dengan sedikit variasi), dan hanya 3 sampai 6 terbaik masuk ke prompt.

## ❓ Kenapa ini penting

Model hanya bisa memakai apa yang kamu taruh di depannya. Prompt biasanya hanya punya ruang untuk segelintir chunk, jadi **segelintir yang mana** menentukan jawaban. Pencarian pertama yang bagus tapi mengembalikan 5 chunk hampir identik memberi model satu fakta lima kali. Urutan yang buruk bisa mengubur kalimat kunci di tengah. Konteks besar penuh noise memakan uang dan membuat model lebih buruk, bukan lebih baik.

Tahap ini sering memberi **peningkatan kualitas terbesar per jam kerja** setelah chunking.

## 📖 Langkah demi langkah

### 1. Dua tahap: luas, lalu sempit

```text
question ─► first search: top 50 (fast, high recall)
        ─► clean: drop duplicates, apply MMR for variety   (cheap, in code)
        ─► re-rank: score top 20–50 with a smarter model   (slower)
        ─► keep the best 3–6 within the token budget
        ─► order them well and build the prompt
```

Ukur tiap tahap dengan set uji dari minggu 3:

| Tahap | Metrik yang diawasi |
|---|---|
| Pencarian pertama | **recall@50**: apakah chunk yang tepat ada di kolam sama sekali? |
| Setelah re-ranking | **precision@5 / MRR**: apakah ada di puncak? |
| Ujung ke ujung | kebenaran jawaban |

Kalau recall@50 rendah, re-ranker mana pun tak bisa membantu: perbaiki chunking, embedding atau hybrid search. Kalau recall@50 tinggi tapi precision@5 rendah, re-ranker adalah alat yang tepat.

### 2. Tulis ulang kueri

User menulis pertanyaan pendek, bertele-tele atau tidak lengkap. Dalam chat, pesan bisa bergantung pada giliran sebelumnya: "kalau yang merah?".

Pilihan:

- **Penulisan ulang mandiri:** model kecil mengubah riwayat chat + pesan terakhir menjadi satu kueri pencarian lengkap ("kebijakan retur untuk sepatu lari merah").
- **Multi-kueri:** hasilkan 2–4 varian (sinonim, kata berbeda, bahasa lain), cari masing-masing, dan **gabungkan** hasilnya (reciprocal rank fusion, minggu lalu).
- **Ekstraksi kata kunci:** simpan kode, nama dan angka sebagai istilah persis untuk pencarian kata kunci.
- **HyDE (jawaban hipotetis):** minta model menulis *jawaban palsu* singkat, embed itu, dan cari dengannya. Bisa menemukan chunk yang tampak seperti jawaban. Cerdik tapi bisa melenceng, jadi uji.
- **Filter dari kueri:** "dalam bahasa Indonesia", "untuk penjual", "setelah 2025" bisa menjadi filter metadata.

Penulisan ulang memakan satu panggilan model dan sedikit latency, jadi pakai model kecil dan cepat dan ukur manfaatnya. Untuk versi pertama, langkah penulisan ulang hanya untuk chat multi-giliran sering sudah cukup.

### 3. Buang hampir-duplikat

Teks yang sama sering ada di beberapa tempat (FAQ dan salinannya di manual, dua versi kebijakan). Duplikat menyia-nyiakan prompt. Metode sederhana yang efektif membandingkan himpunan kata dengan **kemiripan Jaccard**:

```python
import re

def jaccard(a, b):
    wa, wb = set(re.findall(r"[a-z0-9]+", a.lower())), set(re.findall(r"[a-z0-9]+", b.lower()))
    if not wa and not wb:
        return 1.0
    return len(wa & wb) / len(wa | wb)

def drop_near_duplicates(chunks, threshold=0.8):
    kept = []
    for chunk in chunks:
        if all(jaccard(chunk["text"], k["text"]) < threshold for k in kept):
            kept.append(chunk)             # keep the first (the better-ranked) copy
    return kept
```

Lakukan ini pada daftar berperingkat agar kamu menyimpan salinan yang peringkatnya lebih baik. Utamakan juga versi **segar**: jika dua hampir-duplikat berbeda tanggal, simpan yang lebih baru, atau saring yang lama lewat metadata saat pencarian.

### 4. Tambah variasi dengan MMR

Lima chunk tentang kalimat yang sama kurang berguna daripada tiga chunk tentang tiga aspek. **Maximal Marginal Relevance** memilih chunk berikutnya dengan menyeimbangkan relevansi terhadap pertanyaan dengan kemiripan terhadap yang sudah dipilih:

```python
def mmr(query_vector, candidates, k, lambda_=0.7):
    remaining = list(candidates)
    chosen = []
    while remaining and len(chosen) < k:
        best, best_value = None, None
        for c in remaining:
            redundancy = max((cosine(c["vector"], s["vector"]) for s in chosen), default=0.0)
            value = lambda_ * cosine(query_vector, c["vector"]) - (1 - lambda_) * redundancy
            if best_value is None or value > best_value:
                best, best_value = c, value
        chosen.append(best)
        remaining.remove(best)
    return chosen
```

`lambda_ = 1` adalah relevansi murni. Nilai lebih rendah mendorong variasi. Mulai sekitar 0,7 dan setel pada set ujimu. Pakai MMR saat pertanyaan luas ("ceritakan proses refund kami"); hindari untuk pertanyaan tepat ("berapa batas waktu refund?") yang mungkin butuh beberapa chunk berdekatan.

### 5. Re-rank dengan penilai yang lebih pintar

Pencarian pertama membandingkan pertanyaan dan tiap chunk **secara terpisah** (dua vektor). **Cross-encoder** membaca pertanyaan dan chunk **bersama**, sehingga bisa menangkap detail. Ia lebih lambat, jadi hanya dijalankan pada 20–50 teratas.

```python
def rerank(query, candidates, scorer, top_n):
    scored = [dict(c, rerank_score=scorer(query, c["text"])) for c in candidates]
    scored.sort(key=lambda c: -c["rerank_score"])          # sort is stable: ties keep their order
    return scored[:top_n]
```

Dari mana `scorer` datang?

| Opsi | Catatan |
|---|---|
| **API rerank terhosting** dari penyedia model | paling sederhana; satu panggilan dengan kueri dan teks-teks; bayar per panggilan |
| **Cross-encoder terbuka** yang kamu jalankan sendiri | gratis per panggilan, butuh perangkat keras dan pembaruan |
| **Model bahasa sebagai juri** ("beri skor 0–10 seberapa baik bagian ini menjawab pertanyaan") | fleksibel, tapi lebih lambat dan mahal; jaga prompt pendek dan hasil terstruktur |

Aturan: panggil scorer **sekali per kandidat**, re-rank hanya daftar pendek, dan ukur `precision@5` dan latency sebelum dan sesudah. Cache skor untuk kueri populer.

### 6. Urutkan chunk untuk model

Model cenderung memakai **awal dan akhir** prompt panjang lebih baik daripada tengahnya. Kalau kamu punya 5 chunk berperingkat 1 sampai 5, taruh yang terbaik di kedua ujung:

```python
def lost_in_the_middle_order(chunks):
    return chunks[0::2] + chunks[1::2][::-1]
# [1st, 2nd, 3rd, 4th, 5th]  ->  [1st, 3rd, 5th, 4th, 2nd]
```

Manfaatnya bergantung pada model dan panjang konteks, dan kecil untuk konteks pendek, jadi anggap ini eksperimen murah. Juga:

- **Kelompokkan chunk dari dokumen yang sama** dan jaga dalam urutan aslinya (chunk 3 sebelum chunk 4), karena itu terbaca natural.
- Tandai setiap chunk dengan nomor sumber agar model bisa mengutipnya (lesson berikutnya).

### 7. Muat dalam anggaran dan kompres

Hitung token. Jika chunk terbaik melebihi anggaran:

- simpan lebih sedikit chunk (kualitas di atas kuantitas),
- pakai **parent-child** untuk mengirim child pendek alih-alih parent panjang saat pertanyaan sempit,
- **kompres**: minta model kecil mengekstrak hanya kalimat yang relevan dengan pertanyaan dari tiap chunk (menambah satu panggilan, menghemat token, bisa membuang konteks, jadi uji),
- buang bagian yang jelas tak relevan (header boilerplate).

Lebih banyak konteks tidak lebih baik. Prompt dengan 20 chunk yang kebanyakan tak relevan membuat model lebih sulit menemukan fakta, lebih mahal, dan menambah peluang mencampur sumber.

### 8. Setel dengan set uji

Setel satu kenop sekali:

| Kenop | Rentang khas | Awasi |
|---|---|---|
| `k` tahap pertama | 20–100 | recall@k |
| `top_n` re-rank | 3–8 | precision@5, kualitas jawaban, token |
| `lambda_` MMR | 0,5–1,0 | variasi vs recall untuk pertanyaan tepat |
| Ambang duplikat | 0,7–0,9 | varian berguna yang hilang |
| Batas skor | disetel dari contoh nyata | tingkat "tidak ada jawaban" |
| Penulisan ulang kueri | on/off, per chat vs selalu | manfaat vs latency |

Simpan tabel kecil eksperimen dengan angkanya. Kalau suatu langkah tidak memperbaiki angka, buang: setiap tahap menambah latency dan tempat bug.

### Memilih caranya

| Situasi | Lakukan ini |
|---|---|
| Chunk yang tepat ada di kolam tapi tidak di puncak | tambahkan re-ranker |
| Chunk yang tepat tidak ada di kolam | perbaiki chunking / embedding / hybrid search dulu |
| Hasil teratas saling menyalin | buang hampir-duplikat; coba MMR |
| Pertanyaan lanjutan chat | penulisan ulang kueri mandiri |
| Banyak cara mengatakan hal yang sama | multi-kueri + fusi |
| Prompt panjang, fakta kunci terlewat | chunk lebih sedikit, urutan lebih baik, kompresi |
| Latency terlalu tinggi | re-rank lebih sedikit kandidat, cache, reranker lebih kecil |

- ✅ Ambil luas, lalu persempit.
- ✅ Ukur recall@k-besar dan precision@k-kecil secara terpisah.
- 🚫 Mengirim 20 chunk "jaga-jaga".
- 🚫 Me-re-rank saat chunk yang tepat tak pernah terambil.

## ⚠️ Kesalahan umum

- Mengatur `k` sama dengan jumlah chunk yang muat, sehingga tak ada ruang untuk re-rank.
- Memakai MMR pada pertanyaan tepat yang butuh beberapa chunk berdekatan.
- Memanggil re-ranker pada ratusan kandidat (lambat, mahal).
- Ambang dedupe yang membuang versi yang sah berbeda (kebijakan 2024 vs 2025).
- Menulis ulang setiap kueri dengan model besar, menambah detik latency.
- Mengubah tiga hal sekaligus dan tak tahu mana yang membantu.
- Mengabaikan urutan chunk dan anggaran token.
- Menyembunyikan kegagalan: tak ada log kolam, daftar hasil re-rank dan chunk akhir.

:::revoshop
Seorang pelanggan RevoShop bertanya "kalau yang merah?" setelah membicarakan sepatu lari. Tulis kueri pencarian mandiri yang harus dihasilkan langkah penulisan ulang, dua varian multi-kueri (satu dalam bahasa Inggris), dan katakan chunk mana yang kamu harapkan di kolam tahap pertama versus tiga akhir.
:::

## 🏆 Praktik terbaik

- [ ] Pisahkan recall (tahap pertama) dari precision (re-rank), dan ukur keduanya.
- [ ] Ambil 20–100 kandidat; re-rank turun ke 3–8 dalam anggaran token.
- [ ] Buang hampir-duplikat, dan utamakan versi segar.
- [ ] Pakai penulisan ulang kueri untuk lanjutan chat, dan multi-kueri hanya saat membantu di set uji.
- [ ] Terapkan MMR untuk pertanyaan luas, bukan yang tepat.
- [ ] Re-rank hanya daftar pendek, sekali per kandidat, dan awasi latency.
- [ ] Urutkan chunk dengan sengaja dan beri label nomor sumber.
- [ ] Catat kolam kandidat, daftar hasil re-rank dan chunk akhir di prompt.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan retrieval dua tahap dengan gambaran penyaringan CV dan wawancara. Kenapa re-ranker tidak bisa memperbaiki retrieval miss?

## 📐 Rancang

Versi pertama SupportDesk AI mengembalikan 5 chunk teratas menurut kemiripan vektor. Evaluasi pada 200 pertanyaan menunjukkan recall@5 = 0,68, recall@50 = 0,93, dan banyak jawaban mengutip paragraf yang sama yang berulang dari dua artikel. Anggaran latency retrieval 400 ms. Rancang tahap retrieval yang diperbaiki dan katakan bagaimana kamu tahu itu berhasil.

:::quiz
Tampilkan rancangan yang mungkin

- **Diagnosis:** recall@50 tinggi (0,93), recall@5 rendah (0,68): chunk yang tepat ada di kolam tapi tidak di dekat puncak, dan duplikat menyia-nyiakan slot. Ini masalah peringkat dan pembersihan, bukan cakupan.
- **Alur:** tahap pertama hybrid top 50 → buang hampir-duplikat (Jaccard ≥ 0,8, simpan yang terbaru) → re-rank 30 teratas dengan API rerank terhosting atau cross-encoder → simpan 5 terbaik dalam anggaran token → urutkan dengan chunk terbaik di kedua ujung → bangun prompt.
- **Latency:** tahap pertama ~50 ms (terindeks), dedupe ~1 ms, re-rank 30 chunk pendek 100–250 ms (batch dalam satu panggilan), sisanya di kode: dalam 400 ms. Cache hasil rerank untuk kueri yang sering.
- **Penulisan ulang kueri:** hanya untuk chat multi-giliran, dengan model kecil cepat dan timeout 1 detik; lewati untuk pesan pertama percakapan.
- **MMR:** coba hanya pada pertanyaan luas; verifikasi dengan set uji bahwa pertanyaan tepat tidak kehilangan recall.
- **Cara tahu berhasil:** jalankan ulang 200 pertanyaan dan bandingkan precision@5, MRR, recall@5 dan kebenaran jawaban ujung ke ujung sebelum dan sesudah; cek 0,68 → target (katakan ≥ 0,85); bandingkan juga rata-rata token per prompt dan latency p95; baca misses yang tersisa.
- **Pengaman:** pertahankan batas skor dan jalur "tidak ada jawaban"; catat id kolam, id hasil re-rank dan id akhir untuk tiap request guna mendiagnosis regresi.

**Aturan yang ditunjukkan:** saat recall di k besar tinggi, habiskan upayamu untuk pembersihan dan re-ranking, dan buktikan peningkatannya dengan set uji yang sama.
:::

### 📝 Daftar cek diri

- [ ] Recall dan precision diukur pada batas berbeda
- [ ] Re-ranker hanya melihat daftar pendek
- [ ] Duplikat dibuang
- [ ] Urutan prompt dan anggaran token dikendalikan
- [ ] Tiap tahap punya manfaat terukur

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m7/w4/03-retrieval-tools" ai="no-ai" title="Bersihkan kandidat"}
Tulis `cosine`, `mmr` (relevansi dikurangi redundansi), `jaccard`, `drop_near_duplicates`, `lost_in_the_middle_order` (terbaik di kedua ujung) dan `rerank` (satu panggilan scorer per kandidat, seri stabil, input tidak diubah). Tak perlu API key.
:::

:::hints
- `mmr`: `redundancy = max(cosine(c, s) for s in chosen)` dengan `default=0.0` selama belum ada yang dipilih.
- Seri di `mmr` untuk kandidat lebih awal: ganti yang terbaik hanya bila nilai baru benar-benar lebih besar.
- `jaccard`: himpunan kata `[a-z0-9]+`; dua teks kosong memberi `1.0`.
- `drop_near_duplicates`: simpan chunk hanya jika Jaccard-nya dengan setiap chunk tersimpan `< threshold`.
- `lost_in_the_middle_order`: `chunks[0::2] + chunks[1::2][::-1]`.
- `rerank`: buat salinan dengan `dict(c, rerank_score=...)`, lalu `sort` (stabil) menurun menurut skor dan potong `[:top_n]`.
:::

## ✅ Cek cepat

:::quiz
Kenapa mengambil 50 kandidat lalu hanya menyimpan 5?

Pencarian pertama cepat tapi kasar, jadi kamu melebarkan jaring agar yakin chunk yang tepat ada di antara kandidat (recall tinggi). Langkah yang lebih lambat dan cermat lalu memilih beberapa terbaik (precision tinggi). Menyimpan hanya beberapa chunk di prompt juga menghemat token dan mengurangi noise.
:::

:::quiz
Kapan MMR bisa merugikan?

Untuk pertanyaan tepat yang jawabannya butuh beberapa chunk yang sangat mirip (misalnya syarat berbeda dari aturan yang sama). MMR mendorong variasi dan mungkin melewatkan chunk dekat kedua yang kamu butuhkan. Pakai untuk pertanyaan luas dan uji pada kedua jenis.
:::

:::quiz
recall@50 adalah 0,45. Haruskah kamu menambah re-ranker?

Tidak. Chunk yang tepat tak ada di kolam untuk lebih dari separuh pertanyaan, dan re-ranker hanya bisa mengurutkan ulang yang terambil. Perbaiki chunking, model embedding, hybrid search atau filter dulu.
:::

## 📚 Lanjut belajar

- [Sentence-Transformers: Cross-Encoders](https://www.sbert.net/examples/applications/cross-encoder/README.html)
- [Liu et al.: Lost in the Middle (paper)](https://arxiv.org/abs/2307.03172)
- [Carbonell & Goldstein: MMR (paper)](https://www.cs.cmu.edu/~jgc/publication/The_Use_MMR_Diversity_Based_LTMIR_1998.pdf)

---
title: "Evals Libraries: Ragas & DeepEval"
summary: "Pakai pustaka evaluasi dengan bijak — apa yang sebenarnya diukur faithfulness, context precision, context recall dan answer relevancy, bagaimana pustaka menghitungnya dengan model juri, jebakan biaya dan noise, dan cara memasangnya di pytest dan CI."
sourceHash: "90dfab8b6467"
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Untuk apa **Ragas** dan **DeepEval**, dan kapan pustaka membantu
- **Metrik RAG**: faithfulness, context precision, context recall, answer relevancy
- Bagaimana metrik ini **dihitung** (agar kamu bisa memercayai atau meragukannya)
- **Biaya dan jebakan**: panggilan juri, noise, bahasa, kotak hitam
- Cara menjalankan eval di **pytest dan CI**
- **Alur kerja** yang masuk akal: pengecekanmu sendiri dulu, pustaka untuk sisanya

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Ragas** | Pustaka open-source berisi metrik untuk sistem RAG |
| **DeepEval** | Kerangka uji open-source untuk aplikasi LLM, bergaya pytest |
| **Faithfulness** | Apakah klaim jawaban didukung konteks yang terambil? |
| **Context precision** | Apakah chunk relevan berperingkat dekat puncak? |
| **Context recall** | Apakah konteks memuat apa yang dibutuhkan untuk menjawab? |
| **Answer relevancy** | Apakah jawaban menjawab pertanyaan yang diajukan? |
| **Ambang metrik** | Skor di atas mana sebuah tes lulus |
| **Model juri** | LLM yang dipanggil pustaka untuk membuat tiap penilaian |

## 🧠 Ide besarnya

Membangun setiap pengecekan sendiri itu seperti **membuat meteran sendiri**. Cara hebat untuk belajar apa itu sentimeter. Tapi untuk kerja nyata kamu membeli meteran yang bagus. Pustaka evaluasi adalah meteran untuk RAG: metrik siap pakai dengan nama yang dipakai semua orang ("faithfulness 0,82"), pelari tes, dan laporan.

Pengrajin yang baik juga **tahu bagaimana meteran itu dibuat**, sesekali mengeceknya terhadap panjang yang diketahui, dan tidak memakai meteran untuk sesuatu yang butuh timbangan. Di lesson ini kamu belajar apa isi meteran itu.

## ❓ Kenapa ini penting

- **Kosakata bersama.** "Faithfulness" dan "context recall" adalah kata standar untuk kualitas RAG. Pewawancara dan rekan tahu.
- **Kecepatan.** Kamu tak perlu menulis ekstraksi klaim, prompt juri dan agregasi dari nol.
- **Integrasi.** Mereka terpasang ke pytest, CI dan dashboard.

Tapi pustaka bisa menipumu. Mereka membuat banyak panggilan juri (uang dan waktu), berisik, prompt bawaannya mungkin tak cocok untuk bahasa Indonesia atau domainmu, dan angka seperti 0,82 tak berarti banyak jika kamu tak tahu bagaimana angka itu dihasilkan. Mengetahui ide di balik tiap metrik membuatmu bisa memercayainya untuk pekerjaan yang tepat.

## 📖 Langkah demi langkah

### 1. Apa yang ditanyakan metrik

Semua metrik RAG standar adalah jawaban untuk pertanyaan sederhana tentang satu kasus uji: sebuah **pertanyaan**, **konteks terambil**, **jawaban**, dan (kadang) **jawaban acuan** atau fakta yang dibutuhkan.

| Metrik | Pertanyaan | Butuh acuan? | Nilai rendah berarti |
|---|---|---|---|
| **Faithfulness** | Apakah klaim jawaban didukung konteks? | tidak | jawaban menambah hal yang tidak dikatakan sumber |
| **Context precision** | Apakah chunk relevan berperingkat di puncak? | ya (mana yang relevan) | retrieval berisik atau peringkat buruk |
| **Context recall** | Apakah konteks terambil memuat fakta yang dibutuhkan? | ya (fakta yang dibutuhkan) | retrieval melewatkan informasi |
| **Answer relevancy** | Apakah jawaban menjawab pertanyaan? | tidak | jawaban di luar topik atau mengelak |
| **Answer correctness** | Apakah jawaban cocok dengan jawaban acuan? | ya | jawaban salah atau tidak lengkap |

Perhatikan bagaimana mereka menunjuk tahap berbeda: **recall dan precision** menilai **retrieval**; **faithfulness** menilai **generasi vs konteks**; **relevancy dan correctness** menilai **jawaban akhir**. Itu persis rantai diagnosis dari minggu 4.

### 2. Bangun versi sederhana, untuk memahami

Pustaka nyata memakai model juri. Untuk melihat idenya, bangun versi pencocokan kata yang kasar.

**Faithfulness:** pecah jawaban menjadi klaim, cek tiap klaim terhadap konteks.

```python
import re

STOPWORDS = {"a", "an", "the", "is", "are", "was", "were", "be", "been", "to", "of", "in", "on", "at", "for",
             "and", "or", "it", "its", "this", "that", "with", "as", "by", "from", "we", "you", "your", "our",
             "can", "will", "after"}

def split_claims(answer):
    text = re.sub(r"\s*\[\s*\d+(?:\s*,\s*\d+)*\s*\]", "", answer)         # remove [1] markers
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s.strip()]

def content_words(text):
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS}

def claim_supported(claim, contexts, threshold=0.8):
    words = content_words(claim)
    if not words:
        return True
    available = set()
    for context in contexts:
        available |= content_words(context)
    return len(words & available) / len(words) >= threshold

def faithfulness(answer, contexts, threshold=0.8):
    claims = split_claims(answer)
    if not claims:
        return 1.0
    return sum(claim_supported(c, contexts, threshold) for c in claims) / len(claims)
```

Pustaka nyata meminta model untuk (1) memecah jawaban menjadi klaim dan (2) menilai untuk tiap klaim apakah konteks mendukungnya. Bentuk yang sama, penilaian jauh lebih pintar.

**Context precision** adalah average precision atas peringkat:

```python
def context_precision(relevance_flags):
    total, relevant_so_far = 0.0, 0
    for k, flag in enumerate(relevance_flags, start=1):
        if flag:
            relevant_so_far += 1
            total += relevant_so_far / k              # precision at this rank
    return total / relevant_so_far if relevant_so_far else 0.0
```

```text
[True, False, True]  → (1/1 + 2/3) / 2 = 0.83      the relevant chunks are near the top
[False, False, True] → (1/3) / 1       = 0.33      the relevant chunk is buried
```

**Context recall** mengecek fakta yang dibutuhkan:

```python
def _share(facts, text):
    if not facts:
        return 1.0
    lowered = text.lower()
    return sum(f.lower() in lowered for f in facts) / len(facts)

def context_recall(required_facts, contexts):
    return _share(required_facts, " ".join(contexts))
```

Di pustaka nyata, "fakta yang dibutuhkan" biasanya pernyataan dalam jawaban acuan, dan model mengecek apakah masing-masing bisa ditemukan di konteks.

### 3. Bagaimana pustaka biasanya dipakai

API persisnya berubah antar versi, jadi baca dokumentasi terbaru, tapi bentuknya stabil:

```python
# Pseudocode — check the library's documentation for the exact names in your version
from some_eval_library import evaluate, FaithfulnessMetric, ContextRecallMetric

test_cases = [
    {
        "question": "How long do refunds take?",
        "answer": "Refunds take 7 days [1].",
        "contexts": ["Refunds are paid back within 7 days after we receive the item."],
        "reference": "7 days",
    },
    # ... one dict per case, taken from your test set + your system's actual outputs
]

result = evaluate(test_cases, metrics=[FaithfulnessMetric(threshold=0.8), ContextRecallMetric(threshold=0.7)],
                  judge_model="<a model you choose>")
print(result)          # scores per case and averages
```

DeepEval dibangun di sekitar **pytest**: tiap kasus uji menjadi tes, metrik punya ambang, dan skor gagal menggagalkan tes. Ragas dibangun di sekitar **dataset dan metrik** yang kamu evaluasi secara massal. Keduanya bisa memakai model juri dan datamu sendiri. Yang lain ada (promptfoo, Inspect, TruLens, evaluator Langfuse): idenya terbawa.

Alur kerjanya:

1. Jalankan sistem RAG-mu pada set uji dan **simpan** pertanyaan, konteks, jawaban, sitasi dan waktu (trace-mu, lesson lalu).
2. Berikan catatan itu ke pustaka.
3. Baca skor per kasus, urutkan dari yang terburuk, dan buka trace-nya.
4. Simpan hasil bersama versi sistem, prompt dan juri.

### 4. Biaya dan jebakan

| Jebakan | Kenapa penting | Yang dilakukan |
|---|---|---|
| **Banyak panggilan juri** | tiap metrik pada tiap kasus memanggil model beberapa kali | mulai dengan 50–100 kasus; pakai juri lebih murah untuk metrik mudah; cache hasil; jalankan set penuh tiap malam, set kecil per commit |
| **Noise** | juri adalah model: skor bergoyang antar run | tetapkan temperature rendah; rata-ratakan ulangan; bandingkan pada kasus yang sama; abaikan selisih kecil |
| **Kualitas juri** | juri lemah memberi skor tak bermakna | pilih model kuat; kalibrasi terhadap label manusia pada sampel (lesson lalu) |
| **Bahasa** | prompt bawaan berbahasa Inggris; teks Indonesia atau campuran mungkin dinilai lebih buruk | uji metrik pada bahasamu; terjemahkan atau sesuaikan prompt bila pustaka mengizinkan |
| **Kotak hitam** | kamu tak bisa menjelaskan kenapa 0,76 | baca putusan dan alasan per klaim; simpan pengecekan sederhanamu sendiri di sampingnya |
| **Metrik ≠ tujuan** | faithfulness tinggi dengan jawaban tak berguna ("aku tidak tahu" untuk semuanya) | selalu baca beberapa metrik bersama plus metrik tingkat tugas |
| **Pergeseran versi** | pembaruan pustaka mengubah prompt dan skor | pin versi; baseline ulang saat upgrade |
| **Kebocoran data** | menyetel sistem sampai pustaka memberi skor tinggi pada kasus ujimu | simpan set tertahan; pakai pustaka sebagai sinyal, bukan target |

Aturan yang baik: **pengecekan murah dan deterministik dulu** (sitasi valid, fakta wajib ada, frasa terlarang tidak ada, recall retrieval dari id berlabel), lalu pustaka untuk faithfulness dan relevancy, lalu manusia untuk sampel.

### 5. Jalankan di pytest dan CI

Jadikan eval sebagai tes yang gagal saat kualitas turun:

```python
# tests/test_rag_quality.py
import json
import pytest

CASES = json.load(open("evals/dev_cases.json"))

@pytest.mark.parametrize("case", CASES, ids=lambda c: c["id"])
def test_case(case, rag_run):                       # rag_run: a fixture that runs your system and caches the output
    output = rag_run(case["input"])
    assert faithfulness(output["answer"], output["contexts"]) >= 0.8
    assert context_recall(case["required_facts"], output["contexts"]) >= 0.7
```

Lebih baik untuk set besar: jalankan seluruh evaluasi sebagai satu job, simpan laporan JSON, lalu **bandingkan dengan laporan terakhir yang diterima** memakai gate (dari lesson 1): tak boleh ada kasus penting yang mundur, dan skor agregat harus di atas batas. Unggah laporan sebagai artefak CI agar reviewer bisa membacanya. Jalankan subset kecil di setiap pull request, dan set penuh sebelum rilis.

### 6. Baca hasil seperti engineer

- Urutkan kasus menurut **faithfulness terendah**, dan baca jawaban di samping konteksnya: apakah halusinasi sungguhan, atau parafrase yang terlewat metrik?
- Urutkan menurut **context recall terendah**: ini masalah retrieval; buka trace-nya.
- Cek bahwa **perubahan skor setelah edit prompt** lebih besar daripada noise antar run (jalankan versi yang sama dua kali untuk mengukurnya).
- Lihat **sebaran skor**, bukan hanya rata-rata: beberapa kasus bencana bersembunyi di balik rata-rata yang bagus.
- Lacak **biaya dan latency** bersama skor.

### Memilih caranya

| Situasi | Lakukan ini |
|---|---|
| Proyek kecil, belajar | pengecekanmu sendiri (latihan minggu ini) + beberapa metrik juri |
| Butuh angka RAG standar cepat | Ragas atau DeepEval dengan juri kuat, pada 50–100 kasus |
| Sudah memakai pytest dan CI | tes ala DeepEval, atau pembungkus pytest-mu sendiri |
| Bahasa Indonesia atau campuran | uji metrik pada datamu; sesuaikan prompt; sampel dicek manusia |
| Skor bergoyang | tetapkan pengaturan juri; ulangi run; pakai set lebih besar |
| Upgrade pustaka | pin versi; baseline ulang |

- ✅ Pahami apa yang diukur tiap metrik sebelum memercayainya.
- ✅ Simpan trace agar kasus berskor rendah bisa dibuka.
- 🚫 Mengoptimalkan prompt sampai angka pustaka tinggi.
- 🚫 Melaporkan skor pustaka tanpa model juri dan versinya.

## ⚠️ Kesalahan umum

- Menganggap "faithfulness 0,9" sebagai "jawabannya benar" (itu hanya berarti: konsisten dengan konteks yang terambil, apa pun isi konteksnya).
- Memakai model yang sama sebagai juri dan sebagai sistem.
- Menjalankan pustaka pada tiga kasus dan menarik kesimpulan.
- Mengabaikan biaya: run eval besar bisa lebih mahal daripada lalu lintas sehari.
- Tidak mem-pin versi, lalu heran kenapa skor melonjak.
- Melewatkan pengecekan sampel manusia.
- Tak ada tautan dari skor buruk kembali ke trace.
- Mengganti semua pengecekan sederhana dengan pustaka.

:::revoshop
Pilih dua metrik (dari faithfulness, context recall, context precision, answer relevancy) yang paling cocok untuk asisten retur RevoShop, dan jelaskan kenapa. Untuk satu metrik, tulis data trace persis yang perlu kamu catat agar pustaka bisa menghitungnya nanti.
:::

## 🏆 Praktik terbaik

- [ ] Ketahui apa yang diukur tiap metrik dan tahap mana yang ditunjuknya.
- [ ] Mulai dengan pengecekan murah deterministik; tambahkan metrik pustaka untuk faithfulness dan relevancy.
- [ ] Pilih model juri kuat, atur keacakan rendah, dan pin versi pustaka dan juri.
- [ ] Kalibrasi metrik yang dinilai juri terhadap label manusia pada sampel.
- [ ] Simpan trace (pertanyaan, konteks, jawaban, sitasi) agar setiap skor bisa diperiksa.
- [ ] Gerbangi pada regresi terhadap laporan tersimpan; jalankan subset kecil per pull request.
- [ ] Baca kasus terburuk, bukan hanya rata-rata.
- [ ] Lacak biaya dan latency di samping kualitas.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan pustaka evaluasi dengan gambaran meteran. Kenapa tetap penting tahu bagaimana meteran itu dibuat?

## 📐 Rancang

SupportDesk AI ingin melaporkan kualitas RAG di CI. Set uji punya 150 kasus berbahasa Indonesia dan Inggris. Satu run penuh dengan pustaka berbiaya sekitar 6 USD dan butuh 15 menit; pull request terjadi 20 kali sehari. Rancang apa yang berjalan kapan, metrik mana yang dipakai, bagaimana mengendalikan biaya dan noise, dan bagaimana reviewer membaca hasilnya.

:::quiz
Tampilkan rancangan yang mungkin

- **Tiga lapisan.** (1) Di setiap commit: hanya pengecekan deterministik (sitasi valid, fakta wajib ada, frasa terlarang tidak ada, recall retrieval dari id chunk berlabel, schema, panjang): detik, gratis. (2) Di setiap pull request yang menyentuh prompt, retrieval atau model: **subset 50 kasus** dengan metrik faithfulness dan context-recall pustaka, juri lebih murah untuk metrik konteks, hasil di-cache menurut (kasus, versi sistem) sehingga kasus tak berubah tidak dinilai ulang. (3) Tiap malam dan sebelum rilis: **150 kasus penuh**, 3 ulangan untuk metrik juri, plus pengecekan sampel manusia mingguan atas 20 putusan juri.
- **Metrik:** retrieval — context recall dan recall@k dari id berlabel; generasi — faithfulness; ujung ke ujung — kebenaran jawaban terhadap fakta acuan, tingkat penolakan pada kasus tak terjawab; operasi — token, biaya dan latency p95 per jawaban.
- **Kendali biaya:** subset plus caching menurunkan run PR menjadi sekitar 1 USD; juri lebih kuat hanya untuk faithfulness; batch API untuk run malam; alarm anggaran untuk pengeluaran eval.
- **Noise:** temperature juri rendah; ulangi run penuh 3×, laporkan rata-rata dan sebaran; gerbangi hanya pada selisih di atas noise terukur (misalnya lebih dari 3 poin) dan pada regresi apa pun di kasus `critical`.
- **Bahasa:** bandingkan putusan juri dengan label manusia pada kasus Indonesia (kappa) sebelum memercayainya; jika lemah, sesuaikan prompt atau pakai model juri lain.
- **Membaca hasil:** job CI memposting tabel singkat (skor vs baseline, kasus fixed/broken, biaya, latency) dan menautkan laporan dengan 10 kasus terburuk yang menampilkan pertanyaan, konteks, jawaban dan alasan juri.
- **Tata kelola:** pin versi pustaka dan juri; perubahan salah satunya memicu baseline ulang dan catatan di changelog.

**Aturan yang ditunjukkan:** lapiskan pengecekan deterministik murah, metrik pustaka yang tertarget dan pengecekan sampel manusia, dan buat hasilnya terbaca, terbatas biayanya, dan terhubung ke trace.
:::

### 📝 Daftar cek diri

- [ ] Tiap metrik terikat pada satu tahap dan satu perbaikan
- [ ] Pengecekan murah jalan dulu; metrik pustaka tertarget
- [ ] Biaya, noise dan kualitas juri dikendalikan
- [ ] Versi di-pin dan trace disimpan
- [ ] Keluaran CI terbaca dan menggerbangi regresi

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m7/w5/04-rag-metrics" ai="no-ai" title="Metrik RAG sederhana"}
Tulis `split_claims` (buang penanda `[n]` dan spasi sebelumnya, lalu pecah kalimat), `content_words`, `claim_supported`, `faithfulness`, `context_precision` (average precision), `context_recall` dan `answer_coverage`. Semuanya pengganti pencocokan kata untuk apa yang diminta Ragas dan DeepEval diputuskan oleh model juri. Tak perlu API key.
:::

:::hints
- `split_claims`: `re.sub(r"\s*\[\s*\d+(?:\s*,\s*\d+)*\s*\]", "", answer)` lalu pecah pada `(?<=[.!?])\s+`.
- `content_words`: token `[a-z0-9]+` huruf kecil, dikurangi `STOPWORDS`.
- `claim_supported`: gabungan kata isi konteks; rasio kata klaim yang ditemukan; tanpa kata isi berarti didukung.
- `context_precision`: tambahkan `relevant_so_far / k` di setiap peringkat relevan, bagi dengan jumlah chunk relevan.
- `context_recall` dan `answer_coverage`: pengecekan substring tak peka huruf; tanpa fakta berarti `1.0`.
:::

## ✅ Cek cepat

:::quiz
Faithfulness 0,95 tetapi user bilang jawabannya salah. Apa yang bisa menjelaskannya?

Faithfulness hanya mengukur konsistensi dengan konteks yang terambil. Jika retrieval membawa chunk yang salah, usang atau tidak lengkap (context recall rendah), jawaban yang setia pun bisa salah. Cek context recall dan trace.
:::

:::quiz
Kenapa membandingkan skor juri pustaka dengan label manusia setidaknya sekali?

Angka pustaka berasal dari model juri dengan biasnya sendiri dan promptnya sendiri, yang mungkin menangani bahasa atau domainmu dengan buruk. Membandingkan dengan label manusia (kesepakatan dan kappa) memberi tahu seberapa jauh skor bisa dipercaya.
:::

:::quiz
Kenapa tetap menyimpan pengecekan deterministik sederhana walau memakai pustaka?

Mereka gratis, cepat dan persis bisa direproduksi, jadi menangkap banyak kegagalan (sitasi tidak valid, frasa terlarang, fakta hilang) di setiap commit. Metrik berbasis juri pustaka lebih lambat, lebih mahal dan lebih berisik, jadi melengkapi pengecekan murah, bukan menggantikannya.
:::

## 📚 Lanjut belajar

- [Ragas documentation](https://docs.ragas.io/)
- [DeepEval documentation](https://deepeval.com/docs/getting-started)
- [Anthropic docs: Test and evaluate](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)

---
title: "Chunking Strategies"
summary: "Potong dokumen agar retrieval bekerja — pecah menurut heading dan paragraf, kelompokkan kalimat utuh, cari kecil dan jawab dengan induk yang besar, simpan jalur heading, dan perlakukan tabel, kode dan PDF dengan hati-hati."
sourceHash: 27d3daa8b464
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Kenapa **chunking** adalah tuas tersembunyi terbesar dalam kualitas RAG
- Chunking **berbasis struktur** (heading, paragraf) dengan **jalur heading**
- Chunking **berbasis kalimat** dengan overlap
- Retrieval **parent-child (kecil-ke-besar)**
- Cara menangani **tabel, kode, daftar dan PDF**
- Cara **memilih** strategi dengan bukti

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Chunk** | Unit yang kamu embed, cari dan taruh di prompt |
| **Jalur heading** | Rantai heading di atas sebuah chunk: `Returns > Refunds` |
| **Overlap** | Teks yang diulang di tepi chunk bertetangga |
| **Parent chunk** | Potongan besar (satu bagian) yang memberi konteks |
| **Child chunk** | Potongan kecil di dalam parent, dipakai untuk pencarian presisi |
| **Small-to-big** | Cari potongan kecil, kembalikan parent besar |
| **Semantic chunking** | Memotong di tempat topik berubah, ditemukan dengan embedding |
| **Chunk berkonteks** | Chunk dengan catatan singkat asalnya ditambahkan di depan |

## 🧠 Ide besarnya

Bayangkan memotong **kue lapis panjang**. Kamu bisa memotong tiap 3 cm dengan penggaris dan mengabaikan lapisan: sebagian irisan penuh krim, sebagian berisi setengah stroberi. Atau kamu memotong **mengikuti lapisan** sehingga tiap irisan satu rasa. Pencarian bekerja sama: irisan yang *satu ide* mendapat "rasa" (embedding) yang jelas dan bisa ditemukan; irisan dengan setengah satu ide dan setengah ide lain itu keruh.

Lalu ada pertanyaan apa yang **disajikan**: untuk menemukan irisan yang tepat kamu ingin potongan kecil dan presisi. Agar model menjawab dengan baik kamu mungkin ingin **seluruh lapisan** asal irisan itu. Retrieval parent-child melakukan keduanya.

## ❓ Kenapa ini penting

Chunking terjadi **sebelum** hal lain. Kalau jawaban terpotong dua di antara dua chunk, atau terkubur di chunk tentang tiga hal lain, tak ada model embedding atau re-ranker yang bisa memperbaikinya sepenuhnya. Dalam praktik:

- chunk buruk → teks yang tepat tak pernah terambil (retrieval miss),
- chunk tanpa heading-nya → model melihat "7 hari" dan tak bisa tahu apakah tentang refund atau pengiriman,
- chunk raksasa → prompt penuh noise dan lebih mahal,
- chunk mungil → tanpa konteks, dan jawaban tersebar di banyak potongan.

Tim yang memperbaiki chunking sering mendapat lebih banyak daripada tim yang berganti ke model lebih besar.

## 📖 Langkah demi langkah

### 1. Mulai dari struktur

Dokumen sudah punya struktur: heading, paragraf, daftar, tabel. Pakai itu dulu, dan terapkan batas ukuran kedua.

```text
# Returns                      path: "Returns"
You can return items within 14 days.

## Refunds                     path: "Returns > Refunds"
Refunds are paid back in 7 days.
Shipping costs are not refunded.

## Exchanges                   path: "Returns > Exchanges"
Exchanges depend on stock.
```

Aturan untuk chunker markdown yang baik:

- **Heading memulai bagian baru**; simpan **jalur heading** (`A > B`). Heading baru dengan level sama atau lebih tinggi mengembalikan jalur.
- Bagian yang muat di `max_words` adalah **satu chunk**.
- Bagian yang lebih panjang dipotong **di antara paragraf** dulu; hanya satu paragraf raksasa yang dipotong per kata.
- Tiap chunk menyimpan **path** dan **index**-nya, sehingga kamu bisa menunjukkan asalnya dan mengambil tetangganya.

```python
import re

_HEADING = re.compile(r"^(#{1,6}) (.*)$")

def split_markdown(text, max_words):
    sections, path, body, current_path = [], [], [], ""

    def flush():
        if "".join(body).strip():
            sections.append((current_path, "\n".join(body)))

    for line in text.split("\n"):
        m = _HEADING.match(line)
        if m:
            flush()
            body = []
            level = len(m.group(1))
            path = path[: level - 1] + [m.group(2).strip()]       # a level-2 heading keeps the level-1 parent
            current_path = " > ".join(path)
        else:
            body.append(line)
    flush()
    ...   # then cut each long section between paragraphs, up to max_words
```

### 2. Taruh jalur heading ke dalam teks yang di-embed

Kalimat "Refunds are paid back in 7 days." sendirian sedikit artinya. Embed dengan path-nya:

```text
Returns > Refunds
Refunds are paid back in 7 days.
Shipping costs are not refunded.
```

Path memberi embedding (dan model berikutnya) konteks yang hilang. Simpan path juga sebagai **metadata**, untuk tampilan dan filter. Ini salah satu perbaikan termurah yang bisa kamu buat.

Versi lebih kuat dari ide yang sama adalah **chunk berkonteks**: untuk tiap chunk, tambahkan satu atau dua kalimat yang menempatkannya dalam seluruh dokumen ("Chunk ini dari kebijakan refund 2025 Warung Kita, bagian biaya pengiriman"). Model bisa menulis catatan ini saat kamu mengindeks. Berbiaya token saat pengindeksan, tapi membantu saat chunk ambigu sendirian. Uji pada pertanyaanmu sebelum membayarnya dalam skala besar.

### 3. Chunking berbasis kalimat

Untuk teks polos tanpa heading (email, transkrip, paragraf panjang), kelompokkan **kalimat utuh**:

```python
def split_sentences(text):
    parts = re.split(r"(?<=[.!?])(?!\d)\s+", text.strip())          # "3.5" or "10.000" is not a sentence end
    return [p.strip() for p in parts if p.strip()]

def sentence_chunks(text, max_words, overlap_sentences=0):
    sentences = split_sentences(text)
    chunks, current = [], []
    words = lambda sents: sum(len(s.split()) for s in sents)
    for sentence in sentences:
        n = len(sentence.split())
        if current and words(current) + n > max_words:
            chunks.append(" ".join(current))
            carry = current[-overlap_sentences:] if overlap_sentences else []
            current = carry if carry and words(carry) + n <= max_words else []
        current.append(sentence)
    if current:
        chunks.append(" ".join(current))
    return chunks
```

Overlap satu kalimat berarti pikiran di batas muncul utuh di setidaknya satu chunk. Singkatan ("Dr.", "e.g.") bisa menipu regex sederhana; untuk teks penting pakai library pemecah kalimat yang layak.

### 4. Parent-child: cari kecil, jawab besar

Chunk kecil cocok persis dengan pertanyaan. Chunk besar memberi model cukup konteks untuk menjawab. Lakukan keduanya: embed **child**, kembalikan **parent**.

```python
def parent_child(parents, child_words):
    children, parent_of = [], {}
    for parent in parents:
        words = parent["text"].split()
        for n, start in enumerate(range(0, len(words), child_words)):
            child_id = f"{parent['id']}#{n}"
            children.append({"id": child_id, "text": " ".join(words[start : start + child_words])})
            parent_of[child_id] = parent["id"]
    return children, parent_of

def expand_to_parents(hit_ids, parent_of, parents):
    out, seen = [], set()
    for hit in hit_ids:
        pid = parent_of.get(hit)
        if pid is None or pid in seen:
            continue                                  # skip unknown ids and parents we already added
        seen.add(pid)
        out.append({"id": pid, "text": parents[pid]})
    return out
```

```text
search the CHILD "paid back in 7 days"  ──►  hit: refunds#2
return the PARENT: the whole "Refunds" section  ──►  into the prompt (each parent only once)
```

Parent biasanya satu bagian atau satu halaman. Harganya prompt lebih besar, jadi jaga jumlah parent kecil (3–4 teratas) dan awasi anggaran tokenmu.

Trik terkait adalah mengembalikan sebuah hit **plus tetangganya** (chunk sebelum dan sesudah), memakai `index` yang kamu simpan.

### 5. Tabel, kode, daftar dan PDF

| Konten | Kehati-hatian |
|---|---|
| **Tabel** | jaga tabel dalam satu chunk, dan ulangi header kolom; untuk tabel besar, satu chunk per kelompok baris dengan header di atas; atau ubah baris menjadi kalimat ("Produk A berharga Rp 50.000 dan dikirim 2 hari") |
| **Kode** | potong di batas fungsi/kelas, jangan di tengah blok; simpan path file dan bahasa sebagai metadata |
| **Daftar** | jaga daftar bersama pengantarnya ("Untuk mengatur ulang password:") dan jangan pecah langkah bernomor |
| **PDF** | ekstraksi teks bisa mengacak kolom, header, footer, tanda hubung. Periksa teks hasil ekstraksi dengan mata. Buang header/footer berulang dan nomor halaman; halaman pindaian butuh OCR |
| **Halaman HTML** | buang menu, banner cookie dan footer; simpan heading dan konten utama |
| **Log chat, tiket** | chunk per percakapan atau per topik, dengan nama pembicara dan tanggal sebagai metadata |
| **Slide** | satu slide (judul + catatan) adalah chunk alami |

Sampah masuk, sampah keluar: **lihat chunk-mu**. Cetak dua puluh chunk acak dan bacalah seperti user.

### 6. Ukuran dan overlap: pilih dengan bukti

Tak ada ukuran terbaik universal. Titik awal khas: **150–300 kata** dengan **overlap 10–20%** untuk prosa; potongan berbasis struktur untuk dokumen dengan heading. Lalu uji:

| Pengaturan | recall@5 | MRR |
|---|---|---|
| 100 kata | ukur | ukur |
| 250 kata | ukur | ukur |
| 250 kata + jalur heading | ukur | ukur |
| berbasis kalimat, overlap 1 | ukur | ukur |
| parent-child (child 60, parent = bagian) | ukur | ukur |

Pakai set uji dari minggu 3. Ubah **satu** hal, simpan pemenangnya, ulangi. Dan bandingkan juga kualitas jawaban **ujung ke ujung**: pengaturan dengan recall bagus bisa menghasilkan prompt yang terlalu panjang.

### 7. Metadata yang harus dibawa setiap chunk

```text
doc_id, chunk_index, path (heading path), title, source URL, language,
tenant / access level, product / version, updated_at, content_hash, parent_id
```

Child mewarisi metadata parent (tenant, bahasa, akses). Jangan pernah biarkan child kehilangan field akses: child yang bocor adalah dokumen yang bocor.

### 8. Chunk ulang nanti

Mengganti chunker berarti meng-embed ulang semuanya. Jaga kode chunking-mu **berversi** (simpan `chunker_version` di metadata), indeks ke koleksi **baru**, jalankan set uji, lalu alihkan. Hindari mencampur chunker dalam satu indeks.

### Memilih caranya

| Konten | Mulai dengan |
|---|---|
| Artikel bantuan, dokumen dengan heading | chunker markdown/heading dengan jalur heading, ~200 kata |
| Email, transkrip, prosa polos | chunk kalimat ~150 kata, overlap 1 kalimat |
| Manual panjang yang konteksnya penting | parent-child (child ~60–100 kata, parent = bagian) |
| Tabel dan daftar harga | chunk sadar-tabel dengan header diulang |
| Kode | potong di fungsi/kelas |
| PDF berantakan | bersihkan ekstraksi dulu, baru chunk |
| Chunk ambigu | tambahkan catatan konteks atau jalur heading |

- ✅ Cetak dan baca chunk nyata.
- ✅ Simpan jalur heading, index dan metadata akses.
- 🚫 Memotong per karakter tetap menembus kalimat dan tabel.
- 🚫 Mengganti chunker tanpa menjalankan ulang set uji.

## ⚠️ Kesalahan umum

- Chunk karakter berukuran tetap yang memotong kalimat, tabel dan kode.
- Membuang heading, sehingga chunk kehilangan topiknya.
- Satu chunk raksasa per dokumen ("embedding akan mengerti sendiri").
- Menduplikasi teks antar chunk tanpa batas (overlap besar sekali).
- Lupa metadata akses pada chunk child.
- Memercayai ekstraksi teks PDF tanpa melihatnya.
- Mencampur chunker lama dan baru dalam satu indeks.
- Mengoptimalkan ukuran chunk pada tiga contoh.

:::revoshop
Ambil satu halaman bantuan RevoShop (pengiriman atau retur). Tandai di mana kamu memotongnya dengan chunker markdown, tulis jalur heading tiap chunk, dan katakan bagian mana yang jadi parent dan mana yang child. Sebut satu tempat di mana potongan naif 200 kata akan memecah jawaban.
:::

## 🏆 Praktik terbaik

- [ ] Chunk menurut struktur dulu (heading, paragraf), baru menurut ukuran.
- [ ] Simpan jalur heading di teks yang di-embed dan di metadata.
- [ ] Pakai overlap secukupnya (10–20%) dan jangan pernah memecah kalimat, baris tabel atau blok kode.
- [ ] Pertimbangkan retrieval parent-child saat jawaban butuh konteks sekitar.
- [ ] Periksa chunk acak dengan mata setelah setiap perubahan pada alur.
- [ ] Bawa metadata tenant, bahasa dan akses pada setiap chunk.
- [ ] Versikan chunker dan indeks ulang ke koleksi baru saat berubah.
- [ ] Pilih pengaturan dengan set uji, bukan intuisi.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan chunking dengan gambaran kue lapis. Kenapa "cari kecil, kembalikan parent" lebih baik dari kedua ekstrem?

## 📐 Rancang

SupportDesk AI mengindeks: artikel bantuan markdown, manual PDF 40 halaman dengan tabel, dan thread email hasil ekspor. Rancang chunking untuk tiap jenis sumber, metadata, cara menjaga jawaban yang melintasi satu bagian tetap utuh, dan cara memutuskan ukuran.

:::quiz
Tampilkan rancangan yang mungkin

- **Artikel bantuan (markdown):** chunker berbasis heading dengan jalur heading, `max_words` sekitar 200, potong di antara paragraf; awali teks yang di-embed dengan path; metadata: id artikel, path, URL, bahasa, produk, status, tanggal pembaruan, hash.
- **Manual PDF:** bersihkan ekstraksi dulu (buang header, footer, nomor halaman, perbaiki tanda hubung; OCR jika dipindai). Pecah menurut heading yang terdeteksi; tabel menjadi chunk sendiri dengan header kolom diulang (dan, untuk tabel kunci, versi satu-baris-per-kalimat). Metadata menambah versi manual dan nomor halaman agar sitasi bisa berkata "halaman 12".
- **Thread email:** buang balasan terkutip dan tanda tangan; chunk per pesan atau per topik; metadata: id thread, peran pengirim (pelanggan/agen), tanggal. Jangan indeks data pribadi yang tak perlu.
- **Parent-child untuk manual:** child ~80 kata dicari; parent (bagian) dikembalikan ke model, dibatasi 3 parent teratas dan anggaran token.
- **Perluasan tetangga:** untuk prosedur langkah demi langkah, ambil juga chunk sebelum dan sesudah hit memakai `chunk_index`.
- **Metadata akses:** tenant, bahasa dan visibilitas disalin ke setiap chunk child dan parent.
- **Memilih ukuran:** set uji 200 pertanyaan; coba pengaturan 120/200/300 kata, dengan dan tanpa jalur heading, dan dengan parent-child; bandingkan recall@5, MRR dan kebenaran jawaban ujung ke ujung plus token per jawaban; pilih kompromi terbaik.
- **Operasional:** `chunker_version` di metadata; membangun ulang ke koleksi baru saat chunker berubah; tinjauan sampel mingguan 30 chunk acak.

**Aturan yang ditunjukkan:** tiap jenis sumber mendapat chunker yang menghormati strukturnya, dan bukti (bukan selera) memilih ukurannya.
:::

### 📝 Daftar cek diri

- [ ] Tiap jenis konten punya strategi chunking yang cocok
- [ ] Jalur heading, index dan metadata akses disimpan
- [ ] Tabel, kode dan PDF ditangani dengan sengaja
- [ ] Chunker berversi dan pengaturan dipilih dengan set uji

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m7/w4/02-chunkers" ai="no-ai" title="Chunker sadar-struktur"}
Tulis `split_markdown` (jalur heading, potongan sadar-paragraf, index), `split_sentences` (bukan di dalam `3.5`), `sentence_chunks` (kalimat utuh dengan overlap opsional), `parent_child` (child kecil dipetakan ke parent) dan `expand_to_parents` (tiap parent sekali, terbaik dulu). Tak perlu API key.
:::

:::hints
- Lacak list `path`: untuk heading level `n`, `path = path[: n - 1] + [title]`.
- Bagian tanpa teks isi tidak membuat chunk; `index` menghitung chunk di seluruh dokumen.
- Untuk memotong bagian panjang: kelompokkan paragraf utuh sampai menambah berikutnya melewati `max_words`; satu paragraf yang lebih panjang dari `max_words` dipotong per kata.
- Regex pemecah kalimat: `re.split(r"(?<=[.!?])(?!\d)\s+", text.strip())`.
- Overlap `sentence_chunks`: saat memulai chunk baru, bawa N kalimat terakhir hanya jika masih menyisakan ruang untuk kalimat berikutnya.
- `expand_to_parents`: simpan set `seen`; lewati id hit yang tak ada di `parent_of`.
:::

## ✅ Cek cepat

:::quiz
Kenapa menambahkan jalur heading ke teks tiap chunk?

Chunk seperti "Refunds are paid in 7 days" bisa kehilangan topiknya saat dipotong dari dokumen. Path ("Returns > Refunds") memberi embedding dan model berikutnya konteks yang hilang, sehingga chunk dicocokkan dan dipahami dengan benar. Murah dan biasanya meningkatkan hasil.
:::

:::quiz
Masalah apa yang diselesaikan retrieval parent-child?

Chunk kecil memberi kecocokan presisi tapi terlalu sedikit konteks untuk menjawab; chunk besar memberi konteks tapi mengaburkan kecocokan. Parent-child mencari chunk child kecil dan mengembalikan parent yang lebih besar, sehingga kamu mendapat presisi saat menemukan dan konteks saat menjawab.
:::

:::quiz
Kamu pindah ke chunker baru. Apa yang harus kamu lakukan sebelum mengirim lalu lintas ke sana?

Indeks ke koleksi baru dengan chunk dan embedding baru, jalankan set ujimu terhadap kedua versi, bandingkan metrik retrieval dan ujung ke ujung, baru kemudian alihkan. Jangan pernah mencampur dua chunker dalam satu indeks.
:::

## 📚 Lanjut belajar

- [Anthropic: Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval)
- [LlamaIndex: Node parsers and chunking](https://docs.llamaindex.ai/en/stable/module_guides/loading/node_parsers/)
- [Pinecone: Chunking strategies](https://www.pinecone.io/learn/chunking-strategies/)

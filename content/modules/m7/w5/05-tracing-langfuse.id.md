---
title: "Tracing with Langfuse"
summary: "Lihat ke dalam setiap request AI — trace dan span, apa yang dicatat (prompt, token, biaya, latency, error), skor dan umpan balik, sesi, privasi dan sampling, dan bagaimana alat seperti Langfuse mengubah trace menjadi debugging dan eval."
sourceHash: "dc3f7d5b6610"
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa arti **observability** untuk fitur AI
- **Trace** dan **span**: bentuk satu request
- Apa yang **dicatat** di tiap span (dan apa yang tidak)
- **Skor dan umpan balik** yang ditempel ke trace
- Bagaimana **Langfuse** (dan alat serupa) memakai ide ini
- **Privasi, sampling dan biaya** tracing itu sendiri
- Bagaimana trace menyuplai **debugging, eval dan pemantauan**

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Observability** | Mampu melihat apa yang dilakukan sistemmu, dari luar |
| **Trace** | Catatan lengkap satu request, dari awal sampai akhir |
| **Span** | Satu langkah di dalam trace, dengan awal, akhir dan rincian |
| **Generation** | Span untuk satu panggilan model (prompt, keluaran, token, biaya) |
| **Session** | Beberapa trace dari percakapan atau kunjungan user yang sama |
| **Skor** | Angka yang ditempel ke trace atau span: jempol, hasil eval |
| **Langfuse** | Platform open-source untuk tracing, penilaian dan pengelolaan aplikasi LLM |
| **Sampling** | Hanya mencatat sebagian request |

## 🧠 Ide besarnya

Saat paket bermasalah, perusahaan pengiriman menunjukkan **halaman pelacakan**: diambil 09.02, disortir 11.40, keluar gudang 14.10, diantar 16.55. Tiap baris adalah langkah dengan waktu. Kamu bisa melihat di mana ia tersangkut.

Request AI adalah paket dengan banyak langkah: tulis ulang pertanyaan, cari, re-rank, bangun prompt, panggil model, cek sitasi, kirim jawaban. **Trace** adalah halaman pelacakannya, dan tiap **span** adalah satu barisnya. Tanpanya, "bot lambat dan salah kemarin" adalah misteri. Dengannya, kamu membuka trace, melihat bahwa pencarian butuh 1,8 detik dan tak mengembalikan apa pun yang berguna, dan kamu tahu di mana harus bekerja.

## ❓ Kenapa ini penting

Sistem AI gagal dengan cara baru: model lambat, loop retry, tagihan token mengejutkan, retrieval meleset, prompt yang tumbuh terlalu panjang. Log biasa ("200 OK dalam 3,2 dtk") tak bisa memberi tahu langkah mana penyebabnya atau apa yang sebenarnya dilihat model.

Tracing memberimu:

- **Debugging:** prompt, konteks, keluaran dan waktu persis dari request yang gagal.
- **Kendali biaya:** token dan biaya per request, per fitur, per user.
- **Kerja latency:** langkah mana yang lambat.
- **Putaran kualitas:** skor dan umpan balik user menempel pada request yang mereka bicarakan, siap menjadi kasus eval.
- **Akuntabilitas:** versi prompt dan model mana yang menghasilkan jawaban.

## 📖 Langkah demi langkah

### 1. Trace dan span

```text
trace "rag-answer"  (one request)                          120 ms
 ├─ span "rewrite"                                          15 ms
 ├─ span "retrieve"     chunks=20                           30 ms
 ├─ span "rerank"       top_n=5                             10 ms
 ├─ generation "llm"    model=…  input_tokens=1200           80 ms ← model call
 │                      output_tokens=150  cost=0.004
 └─ span "validate-citations"   ok=true                      2 ms
```

**Trace** adalah seluruh request. **Span** adalah satu langkah. Span **bersarang**: satu langkah mungkin berisi langkah lebih kecil (panggilan tool di dalam langkah agen). Span yang berupa panggilan model sering disebut **generation** dan membawa prompt, keluaran dan pemakaian token.

### 2. Tracer mini, untuk memahami mekanismenya

Alat nyata melakukannya dengan jam nyata dan mengirim data ke server. Intinya kecil:

```python
import itertools, time
from contextlib import contextmanager

class Span:
    def __init__(self, span_id):
        self.id = span_id
        self.attrs = {}

    def set(self, **attrs):
        self.attrs.update(attrs)

class Tracer:
    def __init__(self, clock=time.perf_counter, ids=None):
        self.clock = clock
        counter = itertools.count(1)
        self.ids = ids or (lambda: str(next(counter)))
        self.traces, self._stack, self._current = [], [], None

    @contextmanager
    def span(self, name, **attrs):
        if not self._stack:                                         # no open span → a NEW trace starts
            self._current = {"trace_id": self.ids(), "spans": []}
        parent = self._stack[-1] if self._stack else None
        handle = Span(self.ids())
        handle.attrs.update(attrs)
        record = {"id": handle.id, "trace_id": self._current["trace_id"],
                  "parent_id": parent["id"] if parent else None, "name": name,
                  "start": self.clock(), "end": None, "duration": None,
                  "attrs": handle.attrs, "status": "ok", "error": None}
        self._current["spans"].append(record)
        self._stack.append(record)
        try:
            yield handle
        except BaseException as exc:
            record["status"] = "error"
            record["error"] = f"{type(exc).__name__}: {exc}"
            raise                                                   # recording an error must not hide it
        finally:
            record["end"] = self.clock()
            record["duration"] = record["end"] - record["start"]
            self._stack.pop()
            if not self._stack:
                self.traces.append(self._current)
                self._current = None
```

Pemakaiannya tampak seperti ini:

```python
with tracer.span("rag", user="u1"):
    with tracer.span("retrieve") as s:
        s.set(chunks=5)
    with tracer.span("llm", model="m") as s:
        s.set(input_tokens=1200, output_tokens=150, cost=0.004)
```

Tiga detail yang patut diperhatikan: span tanpa induk terbuka **memulai trace baru**; exception **menandai span sebagai error dan di-raise ulang** (tracer mengamati, tidak menelan); dan jam serta pembangkit id bisa diinjeksi, jadi tes memakai waktu palsu.

### 3. Membaca trace

Dengan data di tangan, tiga pertanyaan menjawab sebagian besar masalah:

```python
def slowest_span(trace, include_root=False):
    best = None
    for span in trace["spans"]:
        if span["parent_id"] is None and not include_root:
            continue
        if best is None or span["duration"] > best["duration"]:
            best = span
    return best

def total(trace, key):                    # sum tokens or cost over the steps
    value = 0
    for span in trace["spans"]:
        v = span["attrs"].get(key)
        if isinstance(v, (int, float)) and not isinstance(v, bool):
            value += v
    return value

def render_tree(trace):
    depth, lines = {}, []
    for span in trace["spans"]:
        level = 0 if span["parent_id"] is None else depth[span["parent_id"]] + 1
        depth[span["id"]] = level
        suffix = " ERROR" if span["status"] == "error" else ""
        lines.append(f"{'  ' * level}{span['name']} ({round(span['duration'] * 1000)} ms){suffix}")
    return lines
```

- *Ke mana waktu pergi?* `slowest_span`.
- *Berapa biayanya?* `total(trace, "cost")`.
- *Apa yang terjadi, berurutan?* `render_tree`.

### 4. Apa yang dicatat

| Pada setiap panggilan model | Kenapa |
|---|---|
| nama dan versi model, parameter kunci | untuk membandingkan model dan mereproduksi |
| prompt (atau **nama, versi dan fingerprint**-nya) dan pesan | untuk melihat apa yang dilihat model |
| keluaran dan **stop reason** | terpotong? penolakan? |
| **token masukan dan keluaran**, token cache read/write | biaya dan kesehatan cache |
| latency, dan **time to first token** untuk jawaban yang di-stream | kecepatan seperti yang dirasakan user |
| error, retry, fallback yang dipakai | keandalan |

| Pada request | Kenapa |
|---|---|
| id user (atau id ter-hash), tenant, id sesi | biaya per-user, support, permintaan privasi |
| nama fitur dan versi app | pengirisan |
| id dan skor terambil, filter, kueri hasil tulis ulang | debugging RAG |
| panggilan tool: nama, argumen (disamarkan), jenis hasil, durasi | debugging agen |
| hasil validasi: sitasi valid, guardrail terpicu | kualitas dan keamanan |

Tambahkan **atribut** (key-value) alih-alih menaruh semuanya di nama span. Jaga nama stabil (`retrieve`, `llm`), agar bisa dikelompokkan.

### 5. Skor dan umpan balik

**Skor** adalah angka yang ditempel ke trace (atau span) sesudahnya:

- **Umpan balik user:** jempol atas/bawah, "apakah ini membantu?", handoff ke manusia.
- **Pengecekan otomatis:** validitas sitasi, guardrail terpicu, format valid.
- **Hasil eval:** skor faithfulness dari juri untuk trace ini.
- **Sinyal bisnis:** tiket terselesaikan, user tidak bertanya lagi.

Karena skor ada di trace, satu klik membawamu dari "jawaban ini dapat jempol-bawah" ke prompt, konteks dan token persisnya. Dan trace jempol-bawah adalah **kasus uji baru** terbaik untuk eval minggu depan.

### 6. Sesi, user, dan tag

Kelompokkan trace dari satu percakapan dalam **sesi**, agar kamu bisa membaca seluruh chat. Beri tag pada trace dengan user, tenant, environment (`prod`, `staging`), rilis dan fitur, agar bisa memfilter ("tampilkan kegagalan untuk tenant 7 sejak rilis 2.3"). Versikan prompt-mu dan catat versinya di trace: lalu "apakah prompt 1.4 membuat biaya naik?" menjadi grafik.

### 7. Langfuse dan alat serupa

**Langfuse** adalah platform open-source untuk observability LLM. Kamu bisa memakai cloud mereka atau **self-host** (berguna untuk data privat). Kira-kira ia menyediakan:

- **Tracing** dengan trace, span, generation, sesi dan user, plus UI untuk menjelajah, mencari dan memfilternya.
- Dashboard **biaya dan latency** dari pemakaian token yang kamu catat.
- **Skor** (dari kode, user atau evaluator) dan antrean anotasi untuk tinjauan manusia.
- **Dataset dan eksperimen** untuk menjalankan kasus evalmu dan membandingkan versi.
- **Manajemen prompt** dengan versi.

Kamu mengintegrasikan dengan menambah SDK: biasanya dekorator atau context manager di sekitar fungsimu, plus integrasi untuk framework dan SDK model umum. Nama API berubah antar versi, jadi ikuti panduan quick-start terbaru. Bentuknya persis tracer mini di atas:

```python
# Pseudocode: the real decorator/context-manager names differ per SDK version
@observe(name="rag-answer")
def answer(question, user_id):
    with span("retrieve") as s:
        chunks = search(question)
        s.update(metadata={"chunks": len(chunks)})
    with generation("llm", model=MODEL, input=prompt) as g:
        text = call_model(prompt)
        g.update(output=text, usage={"input": 1200, "output": 150})
    return text
```

Alat lain melakukan pekerjaan yang sama (Arize Phoenix, LangSmith, Helicone, susunan berbasis OpenTelemetry). **OpenTelemetry** adalah standar netral-vendor untuk trace dan span, dan banyak alat LLM bisa mengirim atau menerimanya. Pilih menurut kebutuhan hosting, privasi, biaya dan kebiasaan tim, bukan merek.

### 8. Privasi, sampling dan biaya tracing

Trace berisi prompt, dan prompt berisi data user.

- **Samarkan atau buang** data pribadi sebelum meninggalkan app-mu (email, telepon, nomor kartu, secret): redaksi yang sama yang kamu tulis untuk guardrail.
- **Jangan pernah mencatat secret** (API key, token, password) di prompt atau atribut.
- **Retensi:** simpan trace hanya selama perlu (misalnya 30 hari), dan dukung permintaan penghapusan.
- **Akses:** batasi siapa yang boleh membaca trace produksi.
- **Self-host atau pilih penyedia dengan ketentuan data yang tepat** untuk data sensitif.
- **Sampling:** pada lalu lintas tinggi, simpan semua error dan request lambat, dan sampel (katakan 10%) sisanya. Selalu simpan trace dengan umpan balik user.
- **Overhead:** kirim trace **secara asinkron** (antrean latar belakang), jangan pernah memblokir request user pada server tracing, dan pastikan kegagalan tracing tak pernah merusak app.

### 9. Trace menggerakkan putaran kualitas

```text
production traffic ─► traces ─► scores & thumbs-down ─► review ─► new eval cases ─► eval/gate ─► better release
                         ▲                                                                       │
                         └───────────────────────── monitoring ◄─────────────────────────────────┘
```

Pasang beberapa **alarm**: tingkat error, latency p95, biaya per hari, persentase "tidak ada jawaban", tingkat validitas sitasi, tingkat jempol-bawah. Beri alarm pada perubahan setelah rilis, dan pakai tautan trace di alarm untuk memulai penyelidikan.

### Memilih caranya

| Situasi | Lakukan ini |
|---|---|
| Baru mulai | trace setiap request: retrieval, panggilan model, validasi; catat token, biaya, latency, versi |
| Data privat | samarkan sebelum mengirim; self-host atau pilih ketentuan data ketat |
| Lalu lintas tinggi | sampel request normal; simpan semua error, yang lambat dan yang berumpan balik |
| Perlu menemukan "kenapa lambat" | span dengan durasi, dan `slowest_span` atau tampilan flame di UI |
| Perlu menemukan "kenapa mahal" | token dan biaya per span, per fitur, per user |
| Ingin putaran kualitas | tempel skor dan umpan balik ke trace; ubah kegagalan menjadi kasus eval |
| Banyak layanan | teruskan trace id (OpenTelemetry) lintas layanan |

- ✅ Trace setiap panggilan model dengan usage dan versi prompt.
- ✅ Samarkan data pribadi sebelum mencatat.
- 🚫 Memblokir request user pada backend tracing.
- 🚫 Menyimpan secret atau data pribadi mentah di trace.

## ⚠️ Kesalahan umum

- Hanya mencatat jawaban akhir, bukan langkah-langkahnya.
- Tanpa atribut token atau biaya, sehingga tagihan mengejutkan.
- Merekam data user mentah dan secret.
- Kode tracing yang bisa menjatuhkan request.
- Span tanpa nama stabil, sehingga tak ada yang bisa dikelompokkan.
- Tak ada tautan dari umpan balik user ke trace.
- Menyimpan setiap trace selamanya.
- Tidak pernah melihat trace sampai ada yang rusak.

:::revoshop
Gambarkan span untuk request "tanya soal pesananku" RevoShop: daftar tiap langkah, atribut yang kamu catat di masing-masing, field yang kamu samarkan, dan satu alarm yang kamu pasang.
:::

## 🏆 Praktik terbaik

- [ ] Bungkus setiap request dalam trace, dan setiap langkah (retrieve, rerank, model, tool, validasi) dalam span.
- [ ] Catat model, parameter, versi prompt, token, biaya, latency dan stop reason di setiap generation.
- [ ] Tempel umpan balik dan skor otomatis ke trace; ubah kegagalan menjadi kasus eval.
- [ ] Samarkan data pribadi dan secret; atur retensi; batasi akses.
- [ ] Kirim trace secara asinkron dan buat kegagalan tracing tidak berbahaya.
- [ ] Sampel lalu lintas volume tinggi tapi simpan error, request lambat dan umpan balik.
- [ ] Tambahkan dashboard dan alarm untuk error, latency, biaya dan sinyal kualitas.
- [ ] Pakai nama span stabil dan atribut konsisten.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan trace dan span dengan gambaran pelacakan paket. Kenapa error tracing tak boleh merusak request user?

## 📐 Rancang

SupportDesk AI: sebagian pelanggan menunggu 12+ detik untuk sebuah jawaban, tagihan model bulanan 40% di atas perkiraan, dan kepala support berkata "bot salah hari Selasa" tanpa rincian. Rancang tracing-nya: span, atribut, skor, aturan privasi, sampling, dashboard dan alarm, dan bagaimana kamu memakainya untuk menemukan masing-masing dari tiga masalah itu.

:::quiz
Tampilkan rancangan yang mungkin

- **Span per request:** `chat-request` (root) → `auth`, `rewrite-query`, `retrieve` (vektor + kata kunci), `rerank`, `build-prompt`, `llm` (generation), `validate-output` (sitasi, guardrail), `stream-to-client`. Panggilan tool menjadi span anak.
- **Atribut:** di root — tenant, id user ter-hash, id sesi, fitur, versi app dan prompt, environment; di `retrieve` — filter, ukuran kolam, ringkasan skor, id terambil; di `llm` — model, parameter, token masukan/keluaran, token cache read/write, biaya, stop reason, time to first token, retry dan fallback; di `validate-output` — validitas sitasi, guardrail terpicu.
- **Skor:** jempol atas/bawah dan klik "bicara dengan manusia" ditempel ke trace; skor otomatis (sitasi valid, tanpa jawaban, guardrail terpicu); skor juri malam untuk faithfulness pada sampel.
- **Privasi:** samarkan email, telepon dan nomor kartu sebelum ekspor; jangan pernah menyertakan secret; simpan prompt dan keluaran 30 hari; batasi trace produksi untuk tim AI; hapus menurut id user bila diminta.
- **Sampling:** simpan 100% error, trace lambat (di atas 8 dtk), trace dengan umpan balik atau handoff, dan 10% sisanya; kirim asinkron dengan antrean terbatas.
- **Jawaban lambat:** filter trace di atas 12 dtk dan bandingkan durasi span: jika `retrieve` atau `rerank` mendominasi, perbaiki pencarian; jika time to first token `llm` mendominasi, pendekkan prompt, aktifkan caching, atau pilih model lebih cepat; jika ada retry, perbaiki error penyedia atau timeout.
- **Tagihan melebihi anggaran:** kelompokkan biaya menurut fitur, tenant, versi prompt dan hari; cari prompt panjang (terlalu banyak chunk), cache hit hilang, loop retry, atau satu tenant mengirim masukan raksasa; atur batas per-tenant dan alarm biaya harian.
- **"Salah hari Selasa":** cari trace menurut tanggal dan jempol-bawah; buka id terambil, versi prompt dan jawaban; klasifikasikan dengan kategori diagnosis (retrieval miss, dropped, not used) dan tambahkan masing-masing ke set eval.
- **Alarm:** latency p95, tingkat error, biaya per hari, tingkat jempol-bawah, tingkat tanpa-jawaban dan tingkat sitasi-tidak-valid, masing-masing dibandingkan dengan rilis terakhir.

**Aturan yang ditunjukkan:** satu trace yang teratribusi dengan baik per request menjawab "apa yang terjadi, berapa lama, berapa biaya, dan apakah bagus", dan menyuplai putaran eval.
:::

### 📝 Daftar cek diri

- [ ] Setiap langkah request adalah span bernama
- [ ] Token, biaya, latency dan versi dicatat
- [ ] Skor dan umpan balik ditempel ke trace
- [ ] Data pribadi dan secret disamarkan; retensi diatur
- [ ] Tracing asinkron dan aman dari kegagalan

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m7/w5/05-tracer" ai="no-ai" title="Tracer mini: trace dan span"}
Tulis `Span`, `Tracer.span` (context manager: span tanpa induk terbuka memulai trace baru, anak bersarang, error dicatat dan di-raise ulang, trace selesai disimpan saat span terluar menutup), `slowest_span`, `total` dan `render_tree`. Jam dan pembangkit id diinjeksi sehingga tes memakai waktu palsu. Tak perlu API key.
:::

:::hints
- Simpan tumpukan catatan span terbuka; trace id diambil **pertama** (hanya untuk trace baru), lalu span id.
- Tambahkan setiap catatan ke `current["spans"]` saat span **dimulai**, agar urutannya urutan mulai.
- Di `except BaseException`: atur `status` dan `error`, lalu `raise`. Taruh waktu akhir di `finally`.
- Saat tumpukan kosong setelah pop, tambahkan trace selesai ke `self.traces`.
- `total`: abaikan bool (`isinstance(True, int)` adalah `True`).
- `render_tree`: ingat kedalaman tiap span menurut id; anak memakai `depth[parent] + 1`.
:::

## ✅ Cek cepat

:::quiz
Di mana trace dimulai dan berakhir?

Trace dimulai saat span pertama (terluar) terbuka, tanpa induk, dan berakhir saat span terluar itu menutup. Span yang dibuka di dalamnya menjadi anaknya. Jadi satu request biasanya sama dengan satu trace.
:::

:::quiz
Kenapa mencatat versi prompt dan pemakaian token di setiap panggilan model?

Versi memungkinkanmu mengikat hasil baik atau buruk ke prompt persis, membandingkan versi dan rollback. Pemakaian token memberi biaya dan menunjukkan prompt panjang atau cache hit yang hilang. Tanpanya, kamu tak bisa menjelaskan tagihan atau perubahan kualitas.
:::

:::quiz
Bagaimana tracing sendiri bisa merugikan, dan bagaimana menghindarinya?

Ia bisa membocorkan data pribadi atau secret ke log, memperlambat request jika memblokir server tracing, atau menjatuhkan app jika melempar error. Samarkan data sebelum ekspor, atur retensi dan aturan akses, kirim trace secara asinkron, dan tangkap error tracing agar tak pernah memengaruhi user.
:::

## 📚 Lanjut belajar

- [Langfuse documentation](https://langfuse.com/docs)
- [OpenTelemetry: Traces concepts](https://opentelemetry.io/docs/concepts/signals/traces/)
- [OpenTelemetry: GenAI semantic conventions](https://opentelemetry.io/docs/specs/semconv/gen-ai/)

---
title: "Prompt Caching"
summary: "Bayar jauh lebih murah untuk bagian prompt yang dikirim berulang — cara kerja prefix caching, di mana menaruh breakpoint, apa yang diam-diam merusaknya, berapa lama ia hidup, dan cara memastikan ia benar-benar kena."
sourceHash: 849925d32992
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa itu **prompt caching** dan kenapa ia menghemat uang **dan** waktu
- Kenapa ia **prefix match**, dan apa artinya untuk urutan promptmu
- Di mana menaruh **breakpoint**
- Aturan biaya: **write**, **read**, **TTL**, **panjang minimum**
- **Perusak diam-diam** yang memberimu nol hit
- Cara **memverifikasi** bahwa caching benar-benar bekerja

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Prompt caching** | Penyedia mengingat awal promptmu sehingga kamu tak membayar penuh untuk mengirimnya lagi |
| **Prefix** | Awal prompt, sampai suatu titik |
| **Breakpoint** | Penanda (`cache_control`) yang berkata "cache semuanya sampai sini" |
| **Cache write** | Pertama kali prefix disimpan (sedikit lebih mahal) |
| **Cache read** | Memakai ulang prefix tersimpan (jauh lebih murah) |
| **TTL** | Berapa lama prefix tersimpan hidup tanpa dipakai |
| **Invalidasi** | Perubahan yang membuat prefix tersimpan tak berguna |
| **Cache hit rate** | Porsi token masukan yang dibaca dari cache |

## 🧠 Ide besarnya

Bayangkan guru yang memberi **handout 20 halaman yang sama** ke setiap murid, lalu bertanya pertanyaan berbeda ke masing-masing. Tanpa caching, guru membacakan ulang semua 20 halaman untuk tiap pertanyaan. Dengan caching, guru berkata, "Kamu ingat handout tadi; ini hanya pertanyaan barunya." Membaca handout sekali berbiaya sedikit ekstra. Setiap pertanyaan berikutnya murah dan mulai lebih cepat.

Tapi ada syaratnya: guru hanya mengenali handout jika **sama persis kata demi kata, dari halaman pertama**. Kalau seseorang mengubah baris pertama (misalnya cap tanggal), guru tak bisa tahu itu handout yang sama, dan mulai dari awal.

## ❓ Kenapa ini penting

Banyak app AI mengirim **awalan besar yang berulang** di setiap panggilan:

- system prompt panjang dengan aturan dan contoh,
- definisi tool,
- dokumen kebijakan atau buku panduan produk,
- bagian awal percakapan panjang.

Kamu membayar token masukan itu setiap kali, dan menunggu pemrosesannya. Caching biasanya membuat bagian berulang **sekitar sepuluh kali lebih murah** dan **lebih cepat sampai token pertama**. Untuk bot support dengan prompt tetap 6.000 token dan 20.000 request sehari, itu bagian besar dari tagihan.

Tak berbiaya apa pun selain rancangan prompt yang hati-hati, yang memang harus kamu lakukan.

## 📖 Langkah demi langkah

### 1. Prefix match

Kunci cache adalah **teks persis dari awal prompt sampai breakpoint**. Perubahan di mana pun dalam rentang itu berarti miss untuk semua mulai titik tersebut.

```text
prompt order:   [ tools ] [ system prompt ] [ messages... ]
                └── the provider builds the prefix in this order ──┘

example:        [ tools ][ rules + examples ][ policy document ][ the user's question ]
                └────────────── stable: cache it ──────────────┘└─ changes: not cached ─┘
                                                  ▲
                                          breakpoint here
```

Aturan rancangan: **hal stabil dulu, hal berubah terakhir.** Urutkan bagian prompt-mu menurut seberapa sering berubah.

| Berubah... | Contoh | Di mana |
|---|---|---|
| tak pernah | definisi tool, aturan dasar | pertama |
| per deployment atau per hari | dokumen kebijakan, ringkasan katalog produk | setelah itu |
| per sesi | profil user, percakapan sejauh ini | lebih akhir |
| per request | pertanyaan, timestamp, request id | **terakhir** (atau tinggalkan) |

### 2. Nyalakan

Cara paling sederhana adalah satu penanda tingkat-atas. Penyedia meng-cache sampai blok terakhir yang bisa di-cache:

```python
response = client.messages.create(
    model=settings.llm_model,
    max_tokens=1000,
    cache_control={"type": "ephemeral"},        # automatic: cache the stable prefix
    system=LONG_SYSTEM_PROMPT,
    messages=[{"role": "user", "content": question}],
)
```

Atau taruh penanda sendiri pada blok, untuk kendali halus:

```python
response = client.messages.create(
    model=settings.llm_model,
    max_tokens=1000,
    system=[
        {
            "type": "text",
            "text": LONG_SYSTEM_PROMPT,
            "cache_control": {"type": "ephemeral"},     # cache everything up to and including this block
        }
    ],
    messages=[{"role": "user", "content": question}],
)
```

Untuk dokumen bersama dengan pertanyaan yang berubah, taruh penanda di **dokumen**, bukan di pertanyaan:

```python
messages=[{
    "role": "user",
    "content": [
        {"type": "text", "text": POLICY_DOCUMENT, "cache_control": {"type": "ephemeral"}},
        {"type": "text", "text": question},                  # no marker: different every time
    ],
}]
```

Kalau kamu menaruh penanda setelah pertanyaan, setiap request menulis entri cache **baru** (prefix mencakup pertanyaan) dan tak ada yang pernah dibaca. Itu kesalahan pemula yang paling umum.

Untuk **chat panjang**, taruh breakpoint di blok terakhir giliran terbaru. Setiap request baru lalu memakai ulang seluruh percakapan sebelumnya.

(Ada batas jumlah penanda per request; beberapa sudah cukup.)

### 3. Aturan uang

| Peristiwa | Biaya dibanding token masukan normal |
|---|---|
| Masukan tanpa cache | 1× |
| **Cache write** (pertama kali, umur 5 menit) | sekitar **1,25×** (ekstra kecil) |
| **Cache write**, umur 1 jam | sekitar **2×** |
| **Cache read** | sekitar **0,1×** (beberapa model baru lebih murah lagi) |

Angka persisnya berbeda per model dan berubah seiring waktu, jadi cek halaman harga. Titik impas dengan umur 5 menit: **dua request** cukup (1,25 + 0,1 = 1,35 lawan 2,0 tanpa cache). Prompt yang hanya dipakai sekali rugi sedikit.

```python
def prompt_cost(usage, input_price_per_m, read_multiplier=0.1, write_multiplier=1.25):
    weighted = usage["read"] * read_multiplier + usage["write"] * write_multiplier + usage["uncached"]
    return weighted * input_price_per_m / 1_000_000
```

Aturan lain:

- **TTL (time to live):** secara bawaan prefix tersimpan hidup sekitar **5 menit**, dan **setiap read menyegarkan timer**. Lalu lintas stabil menjaganya hidup. Umur **1 jam** opsional lebih mahal untuk ditulis; hanya sepadan bila request tersebar, dengan jeda lebih dari 5 menit.
- **Panjang minimum:** prefix yang lebih pendek dari minimum khusus-model **tidak di-cache, dan kamu tak mendapat error**. Minimumnya berbeda per model (dari sekitar 500 sampai beberapa ribu token), jadi baca dokumen untuk modelmu.
- **Per model:** cache milik satu model. Berganti model mulai dari nol.
- **Isolasi:** entri cache privat untuk organisasi/workspace-mu; pelanggan lain tidak pernah membaca punyamu.

### 4. Simulasikan, untuk memahami

Latihan membangun simulator kecil. Aturan intinya:

```python
def simulate_cache(requests, ttl_s=300, min_tokens=1024):
    store = {}
    results = []
    for request in requests:
        t, blocks, bp = request["t"], request["blocks"], request["breakpoint"]
        tokens = [block_tokens(b) for b in blocks]
        if bp is None:
            results.append({"read": 0, "write": 0, "uncached": sum(tokens)})
            continue
        key = tuple(blocks[: bp + 1])                    # the prefix, exactly
        prefix_tokens = sum(tokens[: bp + 1])
        after = sum(tokens[bp + 1 :])
        last = store.get(key)
        if last is not None and t - last <= ttl_s:       # hit: also refreshes the timer
            store[key] = t
            results.append({"read": prefix_tokens, "write": 0, "uncached": after})
        elif prefix_tokens >= min_tokens:                # miss, long enough: write
            store[key] = t
            results.append({"read": 0, "write": prefix_tokens, "uncached": after})
        else:                                            # too short: no caching at all
            results.append({"read": 0, "write": 0, "uncached": after + prefix_tokens})
    return results
```

Mainkan dan kamu akan melihat aturannya: cap tanggal di atas berarti tak ada hit; breakpoint setelah pertanyaan yang berubah tidak meng-cache apa pun yang berguna; jeda di atas TTL berarti membayar write lagi.

### 5. Perusak diam-diam

Ini membuat caching diam-diam berhenti bekerja. API tidak memberi peringatan, kamu hanya tidak menghemat:

| Biang | Contoh | Perbaikan |
|---|---|---|
| Timestamp atau tanggal di atas | `f"Today is {now}"` di system prompt | pindahkan ke akhir, atau buang |
| Request id atau id acak di prefix | trace id di system prompt | teruskan lewat header/metadata, bukan di prompt |
| Urutan tak stabil | tool atau key JSON dalam urutan berbeda tiap kali (`set`, dict tak terurut) | urutkan; bangun list dengan cara sama setiap kali |
| Mengubah system prompt per user | nama user di dalam system prompt | jaga system prompt tetap; taruh detail user setelah breakpoint |
| Mengedit pesan sebelumnya | memangkas atau menulis ulang giliran lama | hanya tambah; ringkas pada saat terkendali |
| Set tool berbeda per request | tool ditambah atau dihapus | jaga satu daftar stabil |
| Prefix di bawah minimum | system prompt pendek | taruh breakpoint lebih akhir di prompt, atau terima tanpa caching |
| Mengubah pengaturan yang bagian dari prefix | perubahan thinking atau effort yang mereset cache | jaga pengaturan itu stabil dalam satu sesi |

`first_difference(prev, current)` di latihan menemukan blok pertama yang berubah antar dua request: di situlah perusakmu.

### 6. Verifikasi dengan angka nyata

Jangan pernah berasumsi. Baca angka usage dari response:

```python
usage = response.usage
print(usage.cache_creation_input_tokens)   # tokens written this time (costs a little extra)
print(usage.cache_read_input_tokens)       # tokens read from cache (cheap)
print(usage.input_tokens)                  # tokens processed normally (after the last breakpoint)
```

Kirim request yang sama dua kali dalam beberapa menit. Panggilan kedua harus menunjukkan `cache_read_input_tokens` yang besar. **Kalau tetap 0**, cari perusak diam-diam dari bagian 5, lalu cek panjang minimum. Catat tiga angka ini untuk setiap request, dan buat grafik **hit rate** = reads ÷ (reads + writes + uncached).

### 7. Kapan caching sepadan

| Situasi | Sepadan? |
|---|---|
| System prompt tetap panjang, banyak request | ya, kasus klasik |
| Satu dokumen besar ditanyai banyak pertanyaan | ya |
| Percakapan panjang | ya (cache prefix yang tumbuh) |
| Sedikit request dengan jeda panjang (lebih dari TTL) | mungkin pakai umur 1 jam, atau lewati |
| Prompt pendek, di bawah minimum | tak berefek |
| Tiap request punya dokumen panjang berbeda | tidak, tak ada yang berulang |

### Memilih caranya

| Situasi | Lakukan ini |
|---|---|
| System prompt dan tool tetap | breakpoint setelah system prompt |
| Satu dokumen, banyak pertanyaan | breakpoint di dokumen, pertanyaan setelahnya |
| Chat panjang | breakpoint di blok terakhir giliran terbaru |
| Lalu lintas tipis | pertimbangkan umur 1 jam, atau jadwalkan panggilan "jaga hangat" |
| Hit rate 0 | cari perusak diam-diam; cek panjang minimum |
| Prompt punya bagian dinamis | urutkan stabil → berubah; data dinamis terakhir |

- ✅ Urutkan prompt menurut seberapa sering tiap bagian berubah.
- ✅ Catat token cache read/write dan lacak hit rate.
- 🚫 Timestamp atau request id di bagian atas prompt.
- 🚫 Breakpoint setelah bagian yang berubah.

## ⚠️ Kesalahan umum

- Menaruh penanda setelah pertanyaan yang berubah.
- Tanggal, jam, nama user atau trace id di dalam system prompt.
- Tool atau key JSON dalam urutan tak deterministik.
- Mengubah pesan sebelumnya alih-alih hanya menambah.
- Mengharapkan caching pada prompt yang lebih pendek dari minimum.
- Tidak pernah mengecek `cache_read_input_tokens`.
- Lupa bahwa cache hanya hidup beberapa menit tanpa lalu lintas.
- Berganti model di tengah sesi dan heran kenapa cache dingin.

:::revoshop
Asisten "tanya tentang pesanan ini" RevoShop punya system prompt 3.000 token berisi aturan, plus JSON pesanan dan pertanyaan. Tulis urutan prompt (dari stabil ke berubah), katakan di mana breakpoint ditaruh, dan sebutkan satu hal di rancangan sekarang yang akan diam-diam merusak caching.
:::

## 🏆 Praktik terbaik

- [ ] Taruh konten stabil dulu, konten berubah terakhir; taruh breakpoint di batasnya.
- [ ] Jaga prefix identik sampai ke byte antar request (tool terurut, tanpa timestamp).
- [ ] Jangan pernah mengubah pesan sebelumnya; tambahkan saja.
- [ ] Catat `cache_creation_input_tokens`, `cache_read_input_tokens` dan `input_tokens` untuk setiap panggilan.
- [ ] Lacak hit rate dan beri alarm saat turun.
- [ ] Cek panjang minimum dan TTL untuk modelmu; pilih 5 menit atau 1 jam menurut pola lalu lintas.
- [ ] Hitung caching dalam perkiraan biayamu (lihat lesson 2 minggu 1).

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan caching dengan gambaran handout. Kenapa cap tanggal di baris pertama merusaknya?

## 📐 Rancang

SupportDesk AI punya: definisi tool (2.000 token), system prompt (3.000), ringkasan help-center yang berubah sekali sehari (8.000), percakapan sejauh ini, dan pesan pelanggan baru. Lalu lintas 10.000 percakapan sehari, ramai jam 9 sampai 17 dan sepi di malam hari. Versi pertama menaruh "Current time: ..." dan nama pelanggan di atas system prompt, dan cache hit rate 0%. Rancang ulang urutan prompt, breakpoint, pilihan TTL, dan cara mengukur keberhasilan.

:::quiz
Tampilkan rancangan yang mungkin

- **Urutan (stabil → berubah):** definisi tool → system prompt tetap (aturan, contoh) → ringkasan help-center (berubah harian) → percakapan sejauh ini → pesan pelanggan baru. Waktu dan nama pelanggan pindah ke **akhir**, di pesan terbaru atau blok akhir kecil.
- **Breakpoint:** satu setelah blok system prompt (mencakup tool + system, sama untuk semua pelanggan), satu setelah ringkasan help-center (dibagi semua orang selama sehari), dan satu di blok terakhir giliran terbaru agar percakapan yang tumbuh dipakai ulang. Itu tiga penanda, dalam batas lazim.
- **TTL:** di siang hari, lalu lintas ramai terus menyegarkan entri 5 menit, jadi pakai umur bawaan. Jeda malam panjang, jadi terima awal yang dingin di pagi hari, atau kirim satu request pemanasan sebelum jam buka. Pakai umur 1 jam hanya untuk prefix dengan jeda 5–60 menit.
- **Perubahan harian:** saat ringkasan help-center berubah di malam hari, ringkasan dan blok sesudahnya miss sekali; blok sebelumnya tetap hit, karena urutan menaruh bagian yang berubah harian setelah bagian tetap.
- **Panjang minimum:** kumpulan blok pertama 5.000+ token, di atas minimum model mana pun.
- **Ukur:** catat `cache_read_input_tokens`, `cache_creation_input_tokens` dan `input_tokens` per request; hit rate = reads ÷ (reads + writes + uncached); target di atas 80% di siang hari; alarm jika di bawah 50%.
- **Cek biaya:** hitung tagihan sebelum dan sesudah dengan rumus biaya; konfirmasi penghematan dengan laporan usage penyedia.
- **Tes:** tes otomatis membangun dua request untuk dua pelanggan berbeda dan menegaskan N blok pertama identik.

**Aturan yang ditunjukkan:** caching adalah masalah urutan prompt; perbaiki urutannya, lalu verifikasi dengan angka usage.
:::

### 📝 Daftar cek diri

- [ ] Bagian stabil lebih dulu; bagian dinamis terakhir
- [ ] Breakpoint ada di batas stabilitas
- [ ] TTL sesuai pola lalu lintas
- [ ] Ada pengukuran dan alarm

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m7/w2/04-cache-planner" ai="no-ai" title="Simulasikan prompt caching"}
Tulis `block_tokens`, `simulate_cache` (hit prefix persis, TTL yang disegarkan oleh read, panjang minimum, tanpa breakpoint = tanpa caching), `first_difference` (di mana perusak diam-diam bersembunyi), `prompt_cost` (read ×0,1, write ×1,25) dan `cache_savings`. Tes menunjukkan timestamp merusak cache, breakpoint di tempat salah, dan satu request yang rugi uang. Tak perlu API key.
:::

:::hints
- Kunci store dengan `tuple(blocks[: bp + 1])` dan ingat kapan terakhir dipakai.
- Hit butuh `t - last <= ttl_s`; saat hit atur `store[key] = t` (read menyegarkan).
- Bukan hit dan `prefix_tokens >= min_tokens` → write; selain itu hitung prefix sebagai uncached.
- `uncached` juga mencakup blok setelah breakpoint.
- `first_difference`: loop sampai panjang yang lebih besar; blok yang hilang dianggap berbeda; `None` bila sama.
- `cache_savings`: semua token dengan harga penuh, dikurangi jumlah `prompt_cost` dari simulasi.
:::

## ✅ Cek cepat

:::quiz
Kenapa timestamp di atas system prompt memberi hit rate 0%?

Cache mencocokkan prompt dari karakter pertama. Timestamp mengubah blok pertama di setiap request, sehingga prefix tersimpan tak pernah sama dengan yang baru, dan semua sesudahnya juga miss. Pindahkan timestamp ke akhir atau buang.
:::

:::quiz
Di mana breakpoint ditaruh saat banyak request berbagi dokumen dan bertanya berbeda-beda?

Di dokumen (blok stabil terakhir), bukan di pertanyaan. Prefix yang di-cache lalu hanya berisi teks yang berulang. Kalau di setelah pertanyaan, setiap request menyimpan entri baru yang tak pernah dipakai ulang.
:::

:::quiz
`cache_read_input_tokens` 0 di setiap panggilan. Apa yang kamu cek?

Pertama, apakah ada sesuatu di prefix yang berubah tiap kali (timestamp, id, nama user, tool tak terurut, pesan sebelumnya diedit). Kedua, apakah prefix lebih pendek dari panjang minimum yang bisa di-cache model. Ketiga, apakah request berjarak lebih jauh dari umur cache, atau model atau pengaturan berubah.
:::

## 📚 Lanjut belajar

- [Anthropic docs: Prompt caching](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
- [Anthropic docs: Pricing](https://platform.claude.com/docs/en/about-claude/pricing)
- [Anthropic docs: Token counting](https://platform.claude.com/docs/en/build-with-claude/token-counting)

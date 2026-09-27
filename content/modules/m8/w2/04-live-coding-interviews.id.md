---
title: "Wawancara Live Coding"
summary: Selesaikan masalah saat diawasi — alur clarify-to-test, menjelaskan sambil berpikir, DSA pattern di bawah tekanan waktu, menerima bantuan, sesi API dan React praktis, dan cara berlatih.
sourceHash: 3ebe417ffe88
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa saja yang dinilai pewawancara di live coding (bukan hanya "jawaban benar")
- Alur **7-langkah yang bisa diulang**: clarify → contoh → pendekatan → kompleksitas → kode → uji → perbaiki
- **Menjelaskan sambil berpikir** tanpa berlebihan
- Memetakan masalah ke **pola-pola** dari track DSA
- Cara **keluar dari kebuntuan** dan menerima petunjuk dengan baik
- Sesi **praktis**: bangun endpoint kecil, perbaiki bug, tulis component React
- Rencana latihan dengan mock berjangka waktu

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Live coding** | Menulis kode sambil diamati pewawancara |
| **Rubric** | Daftar hal-hal yang dinilai petugas wawancara |
| **Clarify** | Bertanya detail soalnya sebelum coding |
| **Think out loud** | Menjelaskan apa yang sedang kamu pikirkan saat memikirkannya |
| **Pattern** | Pendekatan yang sudah dikenal (dua pointer, hash map) cocok untuk soal |
| **Complexity** | Big-O dari pendekatan yang kamu pilih |
| **Hint** | Bantuan dari pewawancara — menerimanya dengan baik nilainya plus |
| **Practical round** | Membangun endpoint atau component kecil, bukan puzzle |

## 🧠 Ide besarnya

Live coding itu seperti **memasak di acara TV**. Hakim peduli dengan hasil masakannya, tapi mereka juga lihat bagaimana kamu merencanakan, menjaga meja rapi, mencoba rasanya sambil memasak, dan gimana kamu keluar dari bencana saat masakan gagal. Kalau kamu menjelaskan saat memasak, hakim bisa kasih nilai bahkan kalau soufflé tidak sempurna.

## ❓ Kenapa ini penting

Pewawancara tidak bisa baca pikiran kamu, dan daftar penilaian punya lebih dari satu baris: "jawaban benar" hanyalah salah satunya. Mereka juga nilai cara kamu mengerti soal, merencanakan, menguji, dan gimana reaksi kamu saat tersendat.

Di wawancara jarak jauh ada lapisan praktis juga: ruangan sepi, koneksi stabil, dan bilang "izinkan saya bagi layarku" dengan lancar—semuanya tanpa biaya dan menghilangkan gangguan dari penilaian sebenarnya.

## 📖 Langkah demi langkah

### 1. Apa saja yang dinilai (rubric khas)

| Sinyal | Caranya terlihat |
|---|---|
| Memahami masalah | bertanya untuk klarifikasi, identifikasi edge case |
| Menyelesaikan masalah | pertimbang pendekatan, pilih dengan alasan |
| Coding | nama jelas, fungsi kecil, pakai bahasa pemrograman dengan benar |
| Verifikasi | telusuri contoh, uji edge case, perbaiki bug dengan tenang |
| Komunikasi | jelaskan pemikiran, dengarkan petunjuk |

### 2. Alur 7-langkah (45 menit)

Ikuti meski kamu pikir tahu jawabannya. Langsung ke kode adalah cara paling umum kandidat kuat kehilangan nilai.

| Langkah | Menit | Bilang |
|---|---|---|
| 1. **Clarify** | 3 | "Daftar bisa kosong? Nilai unik? Apa kembalian jika tidak cocok?" |
| 2. **Contoh** | 3 | tulis 2 contoh normal + 1–2 edge dengan output yang diharapkan |
| 3. **Pendekatan** | 5 | brute force dulu ("O(n²) dengan cek semua pasangan"), lalu tingkat ("hash map beri O(n)") |
| 4. **Kompleksitas** | 1 | waktu dan ruang dari pendekatan pilihan |
| 5. **Kode** | 15–20 | jelaskan niat setiap blok, bukan setiap keystroke |
| 6. **Uji** | 5 | telusuri contoh baris demi baris; jalankan edge case |
| 7. **Perbaiki** | sisa | diskusi trade-off, pertanyaan lanjutan |

### 3. Contoh yang sudah dikerjakan

> "Diberi daftar lamaran kerja `(perusahaan, status)`, kembalikan perusahaan dengan wawancara terbanyak. Seri → yang pertama abjad."

```python
def top_interview_company(applications: list[tuple[str, str]]) -> str | None:
    # Clarified: statuses are lowercase strings; empty input → None; ties → alphabetical.
    counts: dict[str, int] = {}
    for company, status in applications:
        if status == "interview":
            counts[company] = counts.get(company, 0) + 1
    if not counts:
        return None
    # max by (count desc, name asc)
    return min(counts, key=lambda company: (-counts[company], company))


assert top_interview_company([]) is None
assert top_interview_company([("Kopi Data", "applied")]) is None
assert top_interview_company([("B", "interview"), ("A", "interview")]) == "A"
assert top_interview_company([("B", "interview"), ("B", "interview"), ("A", "interview")]) == "B"
```

Contoh narasi: *"Aku akan hitung wawancara per perusahaan pakai dictionary — satu lintasan, O(n). Untuk tie-break aku pakai `min` dengan kunci negatif count lalu nama, jadi count tertinggi menang dan nama break tie secara abjad."*

### 4. Pola-pola yang sudah kamu tahu (track DSA)

| Petunjuk di soal | Coba |
|---|---|
| "pasangan yang jumlahnya", "sudah pernah lihat", penghitungan | hash map / set |
| array terurut, "cari posisi/pertama ≥" | binary search |
| subarray berderet / substring dengan kondisi | sliding window |
| penjumlahan range | prefix sum |
| input terurut, pasangan dari kedua ujung | two pointer |
| bracket cocok, "paling baru" | stack |
| level, jalur tercepat di graph tak berbobot | BFS |
| top K | heap |

### 5. Saat kamu tersendat

Bilang apa yang kamu tahu, bilang apa yang sudah kamu abaikan, dan tanya pertanyaan spesifik. Diam adalah satu-satunya jawaban yang nilainya nol.

1. Bilang: "Aku tersendat di cara handle duplikat; aku coba contoh yang lebih kecil."
2. Selesaikan dengan tangan di input mini; jelaskan apa yang *kamu* lakukan — itulah algoritmanya.
3. Kembali ke brute force dan optimalkan bagian lambatnya.
4. Terima hint sebagai kolaborasi: "Itu membantu — jadi set biar cek O(1)…".

### 6. Sesi praktis

| Sesi | Tip |
|---|---|
| **Bangun endpoint** (Flask/FastAPI) | clarify input/output dan error; validasi input; kembalikan status code yang sesuai; tulis satu tes |
| **Perbaiki bug** di kode asing | reproduce dulu, baca pesan error, buat tes yang gagal, perbaiki minimal, jalankan lagi |
| **Component React** (misalnya daftar pencarian, tab, form) | mulai markup statis, lalu state, lalu event; aksesibilitas (label, button); handle state kosong/loading |
| **Query SQL** | clarify schema, mulai `SELECT … FROM … JOIN`, lalu filter, grouping, ordering; pikir tentang index |

### 7. Lingkungan dan AI

- Latih di tool yang mereka pakai (editor seperti CoderPad, IDE bersama, bagikan layar).
- Kecuali diizinkan terang-terangan, **jangan pakai AI assistant atau copilot** di wawancara live — kalau diizinkan, jelaskan cara kamu verifikasi output-nya.
- Siapkan: ruangan sepi, internet stabil, ukuran font zoom, air.

### Memilih setup kamu

Setiap pilihan punya trade-off:

| Metode latihan | ✅ | ❌ |
|---|---|---|
| Selesaikan sendiri di situs LeetCode | volume, pola | tidak latih komunikasi |
| Mock wawancara berjangka waktu dengan teman | tekanan realistis, feedback | jadwal rumit |
| Jelaskan solusi tulis/post | pemahaman mendalam | lebih lambat |
| Hafal solusi | recall cepat | gagal pada variasi |

## ⚠️ Kesalahan umum

- Coding sebelum paham; tidak tanya edge case.
- Optimalkan prematur dan tidak pernah selesai.
- Diam saat tersendat; perdebatan dengan hint.
- Tidak uji; nyatakan kemenangan di happy path.

## 🏆 Praktik terbaik

- [ ] Ikuti alur 7-langkah setiap kali — bahkan soal mudah.
- [ ] Clarify dan tulis contoh sebelum coding.
- [ ] Nyatakan brute force, lalu optimalkan; kasih kompleksitas.
- [ ] Jelaskan niat; dengarkan hint.
- [ ] Uji dengan contoh dan edge case sebelum bilang "selesai".
- [ ] Latih pola setiap minggu (review DSA track spaced) dan lakukan mock berjangka waktu bersuara.
- [ ] Siapkan sesi praktis juga: API kecil, perbaikan bug, component React.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan analogi acara TV memasak dan kenapa menjelaskan pendekatanmu bisa beri nilai bahkan saat solusi tidak sempurna.

## 📐 Rancang

Untuk soal *"Diberi hitungan lamaran harian selama N hari dan integer K, kembalikan jumlah maksimal lamaran dikirim di mana saja K hari berturut-turut"*, tulis pertanyaan clarifying-mu, contoh, pendekatan brute-force dan yang dioptimalkan dengan kompleksitas, dan narasi yang akan kamu pakai.

:::quiz
Lihat jawaban contoh

- **Clarify:** K bisa lebih besar dari N? (→ kembalikan jumlah semua atau raise? tanya) · Apakah hitungan non-negatif? · Daftar kosong? · Kembalikan jumlah saja, atau index mulai juga?
- **Contoh:** `[1, 3, 2, 5, 1], K=2` → `7` (2+5) · `[4], K=1` → `4` · `[], K=1` → `0` (sepakat)
- **Brute force:** jumlah setiap window K → O(N·K) waktu, O(1) ruang.
- **Dioptimalkan:** sliding window — jumlah K pertama, lalu tambah hari baru dan kurang hari yang pergi → O(N) waktu, O(1) ruang.
- **Narasi:** "Window bertumpang tindih, jadi hitung ulang setiap jumlah sia-siakan pekerjaan. Aku akan jaga jumlah berjalan: saat window geser ke kanan satu, tambah hari masuk dan kurang hari keluar, dan lacak maksimal."
- **Uji:** K = N, K = 1, semua nol, K > N sesuai aturan yang di-clarify.
:::

### 📝 Checklist review mandiri

- [ ] Pertanyaan clarifying cover edge case
- [ ] Kompleksitas nyatakan untuk kedua pendekatan
- [ ] Uji rencanakan sebelum "selesai"

::ai-review{task="explain"}

::part[Latihan Kecil]{n="3"}

## 🛠️ Lakukan

1. Lakukan 3 soal berjangka waktu (45 menit) **bersuara**, catat layar dan suara; review rekaman dengan rubric.
2. Lakukan satu sesi praktis: bangun `GET /jobs?q=` dengan validasi dan tes dalam 45 menit.
3. Lakukan satu mock dengan teman di editor bersama; tukar peran pewawancara/kandidat.

## ✅ Selesai saat

- [ ] 3 mock solo terekam di-review dengan rubric
- [ ] 1 sesi praktis selesai
- [ ] 1 mock teman selesai; 2 perbaikan top ditulis

## 📖 Kamus

| Istilah | Bahasa Indonesia |
|---|---|
| Live coding | Menulis kode secara langsung saat wawancara |
| Clarifying question | Pertanyaan klarifikasi |
| Edge case | Kasus batas/tepi |
| Brute force | Solusi coba semua kemungkinan |
| Time complexity | Kompleksitas waktu |

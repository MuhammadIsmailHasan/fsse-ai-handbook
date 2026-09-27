---
title: "Wawancara Perilaku (STAR)"
summary: Jawab pertanyaan "ceritakan pengalaman saat..." dengan kisah jujur dan jelas — metode STAR, kumpulan cerita dari bootcamp dan proyek, pertanyaan umum, dan tanda merah yang harus dihindari.
sourceHash: e29d9a51661b
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa yang dinilai dalam wawancara perilaku dan kenapa perusahaan menggunakannya
- Metode **STAR** (Situation, Task, Action, Result) + Reflection
- Membangun **story bank** 8–10 cerita yang mencakup sebagian besar pertanyaan
- Pertanyaan umum dan sinyal apa yang sebenarnya dinilai
- Cara menceritakan **career switch** dan pengalaman bootcamp sebagai kekuatan
- Cara menyampaikan: durasi, "I" vs "we", jujur tentang kegagalan

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Wawancara perilaku** | Pertanyaan tentang apa yang kamu benar-benar lakukan sebelumnya |
| **STAR** | Situation, Task, Action, Result — kerangka untuk menjawab |
| **Reflection** | Pelajaran yang diambil, ditambahkan di akhir |
| **Story bank** | 8–10 cerita siap pakai yang mencakup pertanyaan paling umum |
| **Signal** | Hal yang sebenarnya dinilai interviewer |
| **"I" vs "we"** | Menunjukkan peranmu sendiri dalam kerja tim |
| **Red flag** | Jawaban yang membuat interviewer khawatir (contoh: menyalahkan orang lain) |

## 🧠 Ide besarnya

Perilaku di masa lalu adalah prediksi terbaik untuk perilaku masa depan. Interviewer tidak bisa menonton kamu bekerja selama sebulan, jadi mereka minta **dokumenter pendek** tentang momen-momen yang sudah terjadi. STAR adalah storyboard yang membuat dokumenter kamu tetap di bawah dua menit dan fokus pada *apa yang kamu lakukan*.

## ❓ Kenapa ini penting

Apa yang kamu lakukan sebelumnya adalah tebakan terbaik tentang apa yang akan kamu lakukan nanti. Interviewer tidak bisa menonton kamu bekerja selama sebulan, jadi mereka minta **dokumenter pendek** dari momen-momen nyata.

Putaran ini sering memutuskan antara calon yang serupa dari segi teknis, dan hiring manager mencari risiko: menyalahkan orang lain, menyerah, komunikasi buruk. Untuk career switcher ini kesempatan terbaik untuk mengubah pekerjaan sebelumnya menjadi keuntungan.

Di hiring remote, hal ini bahkan lebih penting, karena tim tidak bisa mengamati kamu setiap hari — jadi cara kamu menjelaskan masalah di masa lalu *adalah* sampel komunikasi kamu.

## 📖 Langkah demi langkah

### 1. STAR (+R)

| Bagian | Apa yang dibagikan | Waktu |
|---|---|---|
| **S**ituation | konteks dalam 1–2 kalimat | 15 s |
| **T**ask | tanggung jawab atau tujuanmu | 10 s |
| **A**ction | apa **kamu** lakukan, langkah demi langkah, dengan alasan | 60 s |
| **R**esult | hasil dengan angka kalau ada | 15 s |
| **R**eflection | apa yang kamu pelajari / akan lakukan berbeda | 15 s |

### 2. Contoh

**Pertanyaan:** "Ceritakan pengalaman saat kamu harus belajar sesuatu dengan cepat."

- **S:** "Di modul backend bootcamp saya, proyek e-commerce tim saya butuh integrasi pembayaran dengan Midtrans, dan tidak ada yang pernah pakai webhook sebelumnya. Kami punya satu minggu."
- **T:** "Saya yang menangani payment flow: membuat transaksi dan menangani notifikasi Midtrans dengan handal."
- **A:** "Saya baca dokumentasi Midtrans dan buat script sandbox kecil dulu untuk lihat payload notifikasi sungguhan. Saya pelajari bahwa notifikasi bisa datang lebih dari sekali, jadi saya buat handler idempotent dengan cek status order sebelum update, dan verifikasi kunci signature. Saya tulis test dengan payload rekaman dan dokumentasikan flow di README supaya teman setim bisa debug-nya."
- **R:** "Payment flow berhasil di demo, termasuk test case notifikasi duplikat, dan menjadi bagian yang mentor minta kelompok lain untuk lihat."
- **Reflection:** "Saya pelajari bahwa eksplorasi API baru dimulai dengan spike kecil sebelum tulis kode production — saya lakukan hal sama nanti dengan jose untuk enkripsi session."

### 3. Bangun story bank

Delapan cerita mencakup hampir setiap pertanyaan, karena sebagian besar pertanyaan adalah variasi dari konflik, kegagalan, ownership, pembelajaran, dan tekanan. Siapkan sekali, pakai di mana-mana.

Kumpulkan 8–10 cerita dari proyek bootcamp, CareerPilot, RevoShop, pekerjaan sebelumnya, volunteer. Tag setiap cerita dengan tema yang dicakupinya:

| Cerita | Tema |
|---|---|
| Webhook Midtrans dalam seminggu | belajar cepat, ownership, kedalaman teknis |
| Merge teman merusak main sebelum demo | konflik/kolaborasi, tenang di tekanan, perbaikan proses (CI) |
| N+1 query ditemukan di load test | problem solving, keputusan berbasis data |
| Tinggalkan pekerjaan sebelumnya untuk switch karir | motivasi, risiko, ketekunan |
| Kesalahan: commit secret key | akuntabilitas, pembelajaran, pencegahan (secret scanning) |
| Jelaskan API ke kolega non-teknis | komunikasi |
| Tidak setuju dengan mentor soal arsitektur | disagreement, kerendahan hati, trade-off |
| Lewatkan estimasi deadline | prioritisasi, komunikasi |

### 4. Pertanyaan umum → sinyal apa yang dinilai

| Pertanyaan | Sinyal |
|---|---|
| Ceritakan tentang dirimu | kejelasan, relevansi (pakai pitch-mu) |
| Waktu kamu gagal / buat kesalahan | akuntabilitas, pembelajaran |
| Konflik dengan teman kerja | empati, kolaborasi, resolusi |
| Tidak setuju dengan senior/manager | critical pushback yang hormat, keterbukaan |
| Deadline ketat | prioritisasi, komunikasi |
| Sesuatu yang kamu bangga | ownership, kedalaman |
| Terima feedback kritis | coachability |
| Kenapa kamu pindah ke software? | motivasi, komitmen |
| Kenapa kami harus hire kamu (junior)? | self-awareness, kecepatan belajar, bukti |

### 5. Cerita career-switcher

Frame-nya sebagai **keputusan deliberat dengan bukti**: apa yang menarik kamu (satu momen), apa yang kamu lakukan tentangnya (bootcamp, berbulan-bulan proyek), apa yang kamu bawa dari sebelumnya (domain knowledge, komunikasi, reliability), dan bukti kamu terus berkembang (proyek, post, test).

### 6. Tips penyampaian

Dua menit, first person, dan hasil nyata. "Kami improve berbagai hal" tidak beri tahu interviewer tentang kamu.

- Target **~2 menit**; tawarkan untuk explain lebih dalam ("senang menjelaskan cara idempotency check bekerja").
- Bilang **"I"** untuk aksi kamu, **"we"** untuk hasil tim.
- Kegagalan: pilih yang nyata tapi tidak bencana; habiskan waktu paling banyak untuk apa yang kamu ubah.
- Pause sebelum jawab; tidak apa-apa bilang "biar saya pikir contoh yang bagus".
- Di konteks Indonesia dan remote sama-sama: sopan dan rendah hati tapi **spesifik tentang kontribusi kamu** — kerendahan hati jangan sembunyikan kerja kamu.

### Pilih setup-mu

Setiap pilihan di sini adalah trade-off:

| | ✅ | ❌ |
|---|---|---|
| Script hafal | percaya diri | terdengar robot; rusak kalau ada follow-up |
| Story bank bullet-point | fleksibel, alami | butuh latihan keras |
| Cerita yang berat teknis | tunjukkan skill | mungkin miss sinyal people/process |

## ⚠️ Kesalahan umum

- Tidak ada result, atau result "dan kemudian proyek selesai".
- Pilih cerita konflik di mana kamu jelas benar dan orang lain villain.
- Pakai satu cerita untuk semuanya.
- Bilang negatif tentang bootcamp atau manager sebelumnya.

## 🏆 Praktik terbaik

- [ ] 8–10 cerita nyata, tag berdasarkan tema, tulis sebagai STAR bullet (bukan script).
- [ ] Setiap cerita punya aksi personal yang jelas dan result (angka kalau jujur).
- [ ] Sertakan reflection — apa yang kamu pelajari atau akan ubah.
- [ ] Latihan keras; rekam dan hitung waktu; buat mock interview dengan peer.
- [ ] Siap untuk follow-up: "apa yang kamu lakukan berbeda?", "apa pendapat teman kamu?".
- [ ] Tidak pernah bikin atau lebih-lebihkan; jangan salahkan orang lain.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan kenapa interviewer minta contoh nyata dari masa lalu daripada "apa yang kamu lakukan kalau...", pakai analogi dokumenter.

## 📐 Rancang

Tulis STAR bullet untuk 3 cerita: kegagalan/kesalahan, konflik atau disagreement, dan waktu kamu belajar sesuatu dengan cepat. Tambah satu baris reflection ke setiap cerita.

:::quiz
Tunjukkan cerita kegagalan yang berhasil

- **S:** Saat build CareerPilot saya push commit yang include `.env` saya dengan API key sungguhan untuk email service.
- **T:** Saya harus batasi kerusakan dan pastikan tidak bisa terjadi lagi.
- **A:** Dalam hitungan menit saya revoke dan rotate key-nya (hapus file saja tidak cukup — ada di history), cek log provider untuk misuse, hapus secret dari history, tambah `.env` ke `.gitignore`, aktifkan GitHub push protection dan tambah step `gitleaks` ke CI.
- **R:** Tidak ada misuse; CI sekarang block secret; saya tulis post pendek tentangnya yang dapat komentar dari dua engineer.
- **Reflection:** Handling secret perlu automation, bukan memory — sekarang setiap proyek mulai dengan `.env.example`, secret scanner, dan push protection.
:::

### 📝 Checklist review mandiri

- [ ] Setiap cerita ≤ 2 menit kalau diucapkan
- [ ] Aksi "I" yang jelas
- [ ] Reflection jujur

::ai-review{task="explain"}

::part[Latihan Kecil]{n="3"}

## 🛠️ Lakukan

1. Tulis story bank-mu (8–10 cerita) di *My notes*, tag berdasarkan tema.
2. Rekam jawaban untuk 5 pertanyaan umum; review untuk durasi dan filler word.
3. Buat satu mock behavioral interview dengan peer; tukar peran.

## ✅ Selesai saat

- [ ] Story bank mencakup kegagalan, konflik, pembelajaran, ownership, feedback, motivasi
- [ ] 5 rekaman jawaban di bawah 2 menit masing-masing
- [ ] Satu mock interview selesai dengan catatan feedback

## 📖 Kamus (glosarium)

| Istilah | Bahasa Indonesia |
|---|---|
| Behavioral interview | Wawancara perilaku |
| STAR method | Metode STAR (Situasi, Tugas, Aksi, Hasil) |
| Story bank | Kumpulan cerita pengalaman |
| Ownership | Rasa kepemilikan/tanggung jawab |
| Coachability | Kemampuan menerima masukan |

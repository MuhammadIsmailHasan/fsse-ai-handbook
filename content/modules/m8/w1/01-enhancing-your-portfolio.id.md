---
title: "Tingkatkan Portfolio Software Engineering Kamu"
summary: Ubah proyek jadi bukti untuk interview — apa yang dicari reviewer, pilih 2–3 proyek unggulan, README yang meyakinkan, demo dan live link, tunjukkan test dan keputusan, dan jelaskan bantuan AI dengan jujur.
sourceHash: dd1a57054c49
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Bagaimana portfolio benar-benar dibaca: **30 detik** oleh recruiter, **10 menit** oleh engineer
- Memilih **2–3 proyek unggulan** daripada 15 tutorial
- Anatomi **README proyek** yang menjawab pertanyaan reviewer
- Sinyal bukti: deployed link, screenshot/video demo, test dan CI badge, diagram arsitektur, alasan keputusan
- Mempresentasikan **CareerPilot**, **RevoShop**, dan bootcamp work secara jujur — termasuk bantuan AI
- Checklist portfolio yang bisa kamu pakai lagi untuk setiap proyek di masa depan

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Portfolio** | Beberapa proyek yang kamu tunjukkan sebagai bukti kemampuan |
| **Proyek unggulan** | Proyek terbaikmu, dipresentasikan dengan baik |
| **README** | Halaman pertama repo: apa itu, cara menjalankannya |
| **Sinyal bukti** | Sesuatu yang menunjukkan pekerjaan sungguhan (live link, test, CI) |
| **Demo** | Video atau GIF singkat menunjukkan aplikasi bekerja |
| **Diagram arsitektur** | Gambar bagian-bagian dan cara menghubungkannya |
| **Decision log** | Catatan singkat kenapa pilih X daripada Y |
| **Dibantu AI** | Pekerjaan di mana AI membantu, dinyatakan dengan jujur |

## 🧠 Ide besarnya

Portfolio adalah **iklan properti**, bukan gudang. Pembeli tidak ingin lihat setiap kotak yang kamu punya — mereka ingin 3 foto bagus, denah, lokasi, dan bukti pipa bekerja. Untuk junior developer, itu berarti: beberapa proyek, masing-masing dengan **apa**, **bagaimana**, **bukti**, dan **kenapa** yang jelas.

## ❓ Kenapa ini penting

Junior bersaing dengan banyak pelamar yang semua bilang "React, Node, Python". Portfolio adalah cara termurah untuk tim hiring menurunkan risiko: *apakah orang ini benar-benar bisa membangun sesuatu, menyelesaikannya, mengujinya, di-deploy, dan menjelaskannya?*

Itu penting di Indonesia, di mana banyak perusahaan — terutama startup — lihat GitHub dan deployed link sebelum gelar. Lebih penting lagi untuk **remote role di luar**, terutama perusahaan US: mereka tidak bisa bertemu kamu, jadi repo, README, dan working link adalah hampir semua yang mereka punya untuk menilai.

Tanpa itu, kamu minta orang asing percaya kata-kata kamu — dan mereka punya dua puluh aplikasi lain terbuka.

## 📖 Langkah demi langkah

### 1. Bagaimana reviewer membaca

| Reviewer | Waktu | Lihat |
|---|---|---|
| Recruiter / HR | ~30 d | nama proyek, deskripsi satu baris, live link, screenshot, keyword teknologi yang cocok dengan lowongan |
| Engineer / hiring manager | 5–15 m | kejernihan README, arsitektur, test dan CI, riwayat commit, kode di 2–3 file penting, cara handle error dan security |
| Interviewer | saat interview | *penjelasanmu*: keputusan, trade-off, apa yang break, apa yang akan diubah |

Rancang untuk ketiga-tiganya: top yang bisa dipindai, middle yang detail, dan cerita yang bisa kamu jelaskan.

### 2. Pilih proyek unggulan

| Jadikan unggulan | Arsipkan atau sembunyikan |
|---|---|
| Selesaikan masalah realistis dengan data sungguhan | ikuti tutorial |
| Punya auth, persistence, error handling, test, deploy | eksperimen setengah jadi |
| Cocok dengan role yang kamu lamar | proyek yang tidak bisa dijelaskan |
| Bisa cerita tentangnya 10 menit | fork tanpa perubahan |

Untuk kamu sekarang: **CareerPilot** (Phase 1, 2, 4 → cerita full-stack), **RevoShop** (backend dengan payment — setelah kerja *Defend Your RevoShop*), dan opsional satu proyek kecil yang tunjukkan skill berbeda (DSA/CLI tool atau UI component library). **Pin** ini di GitHub.

### 3. README yang meyakinkan

Asumsikan reader punya 30 detik dan tanpa konteks. Apa itu, screenshot, cara menjalankannya, dan apa yang menarik secara teknis — dalam urutan itu.

```markdown
# CareerPilot — AI job-hunt assistant

Track job applications through a hiring pipeline, with a Flask API and a Next.js web app.

**Live:** https://careerpilot.example.com · **Demo video (90 s):** link · **API docs:** /docs

![Dashboard screenshot](docs/dashboard.png)

## Features
- Applications pipeline with valid transitions, history and notes
- Secure sessions (httpOnly encrypted cookie), per-user data isolation
- URL-based filters and pagination

## Architecture
(mermaid diagram: browser → Next.js → Flask → PostgreSQL)

## Tech stack
Next.js 16 · React 19 · TypeScript · Flask · SQLAlchemy · PostgreSQL · Docker · GitHub Actions · Playwright

## Run locally
1. `cp .env.example .env` …  2. `docker compose up` …  3. open http://localhost:3091

## Tests
`uv run pytest` (113 acceptance + unit) · `npx playwright test` (23 E2E) · CI badge

## Decisions & trade-offs
- Sessions over localStorage tokens because …
- Offset pagination now; keyset planned because …

## What I'd improve next
- Refresh-token rotation · Kanban board with optimistic updates
```

Urutan penting: **apa + bukti dulu** (live link, screenshot), detail nanti.

### 4. Sinyal bukti, berdasarkan urutan

1. **Deployed link yang bekerja** (dengan demo account — jangan data pribadi kamu).
2. **Screenshot atau 60–90 s demo video/GIF** di atas.
3. **Test + CI badge** — hijau, dan berarti (bilang apa yang dicakup).
4. **Diagram arsitektur** dan bagian **keputusan** singkat.
5. **Riwayat commit** dengan pesan jelas sepanjang minggu (bukan satu "initial commit" besar).
6. **Issue/PR** di repo sendiri (bahkan solo) yang tunjukkan kebiasaan plan dan review.

### 5. Jujur tentang AI dan bootcamp work

Bilang "AI bikin draft pertama; aku redesign payment flow dan tulis test" lebih kuat daripada pura-pura. Perusahaan tahun 2026 harap pakai AI; mereka cek apakah kamu mengerti hasilnya.

- Pakai AI tool itu normal. Bilang bagaimana: *"Aku pakai AI agent untuk scaffold Docker dan CI config dan review setiap baris; pipeline rule, session handling, dan test adalah punyaku."*
- Proyek bootcamp baik-baik saja; jadiin punyamu: improve sesuatu yang terukur (tambah test, fix N+1 query, tambah rate limiting) dan dokumentasi perubahannya.
- Jangan bilang kerja tim sebagai kerja solo. Tulis "tim 4 orang — aku bangun webhook payment dan order service".

### Pilih setup-mu

Setiap opsi di sini ada trade-off:

| Pilihan | ✅ | ❌ |
|---|---|---|
| Beberapa proyek dalam | tunjukkan menyelesaikan, kedalaman, cerita | breadth lebih sedikit di atas kertas |
| Banyak proyek kecil | breadth, keyword | terlihat tidak selesai, tidak ada yang didiskusikan dalam |
| Personal site | branding, kontrol | waktu bangun/maintain; GitHub + LinkedIn biasanya cukup untuk junior |
| Deploy di free tier | bukti sungguhan | sleep/limit; bilang cold start atau simpan demo video |

## ⚠️ Kesalahan umum

- Screenshot halaman Next.js default; README placeholder.
- Live link break, demo credential tidak bekerja.
- Daftar tech-stack tanpa bilang apa aplikasinya.
- Commit `.env` file atau API key.
- Sembunyikan fakta bahwa proyek adalah tim atau tutorial project.

## 🏆 Praktik terbaik

- [ ] 2–3 proyek unggulan pinned yang cocok dengan target role-mu.
- [ ] Setiap flagship README: satu-baris pitch, live link, screenshot/GIF, feature, arsitektur, tech stack, cara jalankan, test, keputusan, langkah berikutnya.
- [ ] Demo bekerja dengan **demo account**; cek link setiap bulan.
- [ ] CI hijau dan ringkasan test; tidak ada secret di repo (jalankan secret scanner).
- [ ] Riwayat commit jelas dan lisensi; `.env.example` diberikan.
- [ ] Jelaskan role dan bantuan AI dengan jujur.
- [ ] Kamu bisa jelaskan file apa pun di proyek unggulan selama 2 menit.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ide "iklan properti, bukan gudang" ke teman sekelas yang ingin tunjukkan 25 exercise bootcamp mereka.

## 📐 Rancang

Rancang portfolio kamu: daftar setiap proyek yang kamu punya, tandai **unggulan / pendukung / arsip**, dan untuk setiap unggulan tulis one-line pitch, 3 sinyal bukti terkuat yang dimiliki, dan 2 gap terbesar yang perlu diperbaiki sebelum apply.

:::quiz
Lihat contoh rancangan

| Proyek | Status | Pitch | Bukti yang punya | Gap untuk diperbaiki |
|---|---|---|---|---|
| CareerPilot | unggulan | Job-hunt tracker: Flask API + Next.js app dengan hiring pipeline | 113 API test + 23 E2E, Docker, CI | live URL + demo video; bagian keputusan |
| RevoShop | unggulan | E-commerce backend dengan Midtrans payment, JWT + RBAC | test, Locust report, layered architecture | README jelaskan peran aku dan pakai AI; fix race condition oversell dan dokumentasi |
| Job listings CLI (Phase 1) | pendukung | CLI yang analisis job posting | test, README jelas | tidak ada — simpan, jangan pin |
| todo-app, learn-react | arsip | — | — | arsip repo |
:::

### 📝 Checklist self-review

- [ ] Paling banyak 3 unggulan
- [ ] Setiap unggulan punya live link atau demo video terencana
- [ ] Gap konkret dan bisa diselesaikan dalam seminggu

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

## 🛠️ Lakukan

1. Arsipkan atau buat private repo yang tidak membantu.
2. Pin 2–3 unggulan; tulis ulang setiap README dengan template di atas.
3. Rekam demo 60–90 s (screen recording dengan suara atau caption) untuk CareerPilot.
4. Cek setiap link dan demo account dari incognito window.
5. Minta satu developer teman (atau mentor) review README selama 5 menit dan bilang apa yang tidak jelas.

## ✅ Selesai kalau

- [ ] 2–3 pinned repo dengan README lengkap, screenshot, dan working link
- [ ] Setiap README punya bagian keputusan dan catatan role/AI jujur
- [ ] Bisa pitch setiap unggulan di bawah 2 menit (pakai D-T-C dari *Defend Your RevoShop*)

## 📖 Kamus

| Istilah | Bahasa Indonesia |
|---|---|
| Portfolio | Portofolio (kumpulan karya) |
| Flagship project | Proyek unggulan |
| Demo account | Akun contoh untuk mencoba aplikasi |
| Proof signal | Bukti kemampuan |
| Pitch | Penjelasan singkat yang meyakinkan |

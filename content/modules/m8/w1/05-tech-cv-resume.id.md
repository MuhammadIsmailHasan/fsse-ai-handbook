---
title: "Tech CV / Resume"
summary: Tulis CV satu halaman yang lolos filter ATS dan yakinkan engineer — struktur, impact bullet dengan rumus XYZ, proyek untuk career switcher, skill yang cocok lowongan, tailoring per aplikasi, dan konvensi CV Indonesia.
sourceHash: a84309f3b3a3
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Cara CV disaring: filter keyword **ATS**, recruiter, hiring manager
- Struktur **satu halaman** yang bersih untuk junior developer dan career switcher
- **Impact bullet** dengan rumus "Accomplished X, measured by Y, by doing Z"
- Cara menampilkan **project**, bootcamp dan pengalaman non-tech
- **Tailoring** CV untuk setiap lowongan dalam 15 menit
- Konvensi CV Indonesia: foto, data pribadi, bahasa, format file

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **CV / resume** | Dokumen satu halaman yang membawamu mendapat wawancara |
| **ATS** | Software yang membaca CV dan mengurutkannya sesuai lowongan |
| **Keyword match** | Pakai kata-kata yang sama dengan deskripsi lowongan |
| **Impact bullet** | Satu baris yang menunjukkan hasil, ukuran, dan cara kerjanya |
| **XYZ formula** | "Accomplished X, measured by Y, by doing Z" |
| **Tailoring** | Menyesuaikan CV untuk setiap lowongan |
| **One-pager** | Semua di halaman satu saja — standar untuk junior |
| **Parseable format** | Tata letak yang bisa dibaca software (tanpa kolom atau gambar) |

## 🧠 Ide besarnya

CV itu **trailer film**, bukan filmnya. Dalam 30 detik harus tunjukkan adegan terbaik (project dan hasil), genre-nya (target peran), dan buat penonton pengin nonton lebih (ajak ke wawancara). Apa pun yang tidak melayani tujuan itu, potong.

## ❓ Kenapa ini penting

Posisi junior populer dapat ratusan lamaran. Recruiter melintir cepat, dan banyak perusahaan pakai software (ATS) yang membaca CV-mu dan mengurutkannya menurut deskripsi lowongan. CV yang tidak terbaca, atau tidak pakai kata-kata lowongan, mungkin tidak pernah sampai ke manusia.

Untuk remote di perusahaan US, dua aturan ekstra berlaku: tetap **satu halaman dalam English**, dan buang foto, tanggal lahir, status perkawinan, dan alamat lengkap yang normal di CV Indonesia — recruiter US mengharapkan mereka tidak ada, dan beberapa sistem tandai itu.

Pikirkan sebagai **trailer film**, bukan filmnya: adegan terbaik, genre yang tepat, dan alasan untuk nonton lebih.

## 📖 Langkah demi langkah

### 1. Struktur (satu halaman untuk junior)

```text
MUHAMMAD ISMAIL
Full-Stack Developer · Jakarta, Indonesia (open to remote)
you@example.com · linkedin.com/in/<you> · github.com/<you> · portfolio link

SUMMARY (2 lines)
Full-stack developer (Python, TypeScript) who builds and deploys tested web apps. Built CareerPilot (Flask API + Next.js, 130+ automated tests) and an e-commerce API with payments.

SKILLS
Languages: Python, TypeScript, SQL · Backend: Flask, FastAPI, SQLAlchemy, REST · Frontend: React, Next.js, Tailwind · Data: PostgreSQL, Redis · Tools: Docker, GitHub Actions, Playwright, pytest

PROJECTS
CareerPilot — job-hunt tracker (github link · live link)                                   2026
• Built a Flask REST API with JWT auth, a hiring-pipeline state machine and per-user isolation, verified by 113 acceptance tests on PostgreSQL in CI
• Developed a Next.js frontend with Server Actions and encrypted httpOnly sessions; 23 Playwright E2E tests run against production builds
• Cut the list endpoint from 21 to 2 SQL queries by fixing an N+1 query (p95 180 → 35 ms under Locust load)

RevoShop — e-commerce backend (github link)                                                2026
• Implemented order and payment flows with Midtrans webhooks and role-based access for admins and customers
• …

EXPERIENCE
[Previous role], [Company] — [City]                                                       2022–2025
• Automated weekly sales reporting with spreadsheets and scripts, saving ~4 hours per week for a team of 6
• …

EDUCATION & TRAINING
the bootcamp — Full-Stack Software Engineering program                                           2026
[Degree], [University]                                                                    2021
```

Untuk career switcher, **Project duluan sebelum Experience**. Simpan pekerjaan sebelumnya tapi tulis ulang bullet-nya sekitar skill yang bisa dipindah (automation, data, communication, ownership).

### 2. Impact bullet

"Reduced the applications page from 21 queries to 2, cutting p95 latency from 1.8 s to 240 ms" lebih bagus dari "Worked on backend performance" — kerja yang sama, tapi yang satu ada buktinya.

Rumus (dari "XYZ" Google): **Accomplished [X] as measured by [Y], by doing [Z]**.

| ❌ Lemah | ✅ Kuat |
|---|---|
| Worked on the backend API | Built 25 REST endpoints in Flask with validation and ownership checks, covered by 113 acceptance tests |
| Made the website faster | Improved job page LCP from 3.9 s to 2.1 s by moving markdown rendering to Server Components and preloading the hero image |
| Used Docker | Containerized API and web app with multi-stage non-root images; one-command local setup with Docker Compose |

Mulai dengan kata kerja kuat (Built, Designed, Reduced, Automated, Migrated), sertakan angka kalau jujur, dan sebutkan teknologi dalam konteks.

### 3. Format ramah ATS

- Satu kolom, heading standar (Summary, Skills, Projects, Experience, Education).
- Text asli (bukan gambar), font standar, tanpa tabel/kotak teks untuk konten utama, tanpa skill bar.
- Ekspor **PDF** kecuali portal minta DOCX. Nama file: `Muhammad-Ismail-Full-Stack-Developer-CV.pdf`.
- Pakai wording persis dari lowongan kalau benar ("REST APIs", "PostgreSQL", "Next.js").

### 4. Tailoring dalam 15 menit

1. Garis bawahi skill yang wajib dan kata-kata berulang di lowongan.
2. Atur ulang Skills supaya yang cocok duluan.
3. Pilih 2 project bullet paling relevan ke peran (peran backend → API, database, performance; peran frontend → UI, accessibility, Web Vitals).
4. Sesuaikan summary 2 baris dengan judul peran.
5. Simpan salinan per aplikasi dan catat di job tracker-mu (CareerPilot!).

### 5. Konvensi CV Indonesia

Buat dua versi: yang lokal dengan konvensi yang diharapkan perusahaan Indonesia, dan yang internasional untuk remote dan aplikasi US. Konten sama, packaging beda.

- **Foto, tanggal lahir, status perkawinan**: masih normal di CV Indonesia, tapi tidak wajib untuk kebanyakan tech company; banyak startup dan multinasional lebih suka **tanpa foto**. Untuk peran remote/internasional, buang.
- **Bahasa**: CV dalam English standar untuk peran tech di Jakarta startup dan multinasional; gunakan Bahasa Indonesia kalau lowongan dalam Bahasa dan perusahaannya lokal.
- **Data pribadi**: kota cukup — tanpa alamat lengkap, nomor KTP, atau NPWP di CV.
- **Gaji yang diharapkan**: jangan tulis di CV; jawab kalau ditanya (ada materi tentang negosiasi).

### Pilih setup-mu

Tiap pilihan di sini ada trade-off:

| | ✅ | ❌ |
|---|---|---|
| Satu halaman | paksa fokus, cepat dibaca | susah muat segalanya — bagus! |
| Template berdesain | mudah diingat manusia | risiko parsing ATS |
| Master CV + salinan yang di-tailor | cocok per peran | versi yang harus dikelola |
| Daftar setiap teknologi | lebih banyak keyword | dangkal, interview akan gali lebih |

## ⚠️ Kesalahan umum

- Statement objective ("seeking a challenging position to grow…").
- Daftar tugas, bukan hasil.
- Typo di nama teknologi (Postgre, Nextjs, Javascript).
- Konten CV berbeda dengan apa yang bisa kamu jelaskan di wawancara.

## 🏆 Praktik terbaik

- [ ] Satu halaman, satu kolom, heading standar, PDF.
- [ ] Link: GitHub, LinkedIn, live project — semua aktif.
- [ ] 2–3 project dengan impact bullet (kata kerja + apa + cara + hasil/angka).
- [ ] Skill dikelompok dan cocok untuk target peran; tanpa skill bar atau rating.
- [ ] Tailor summary, urutan skill, dan bullet untuk setiap aplikasi.
- [ ] Tanggal dan judul konsisten dengan LinkedIn.
- [ ] Proofreading; minta satu engineer dan satu non-engineer baca dalam 30 detik dan bilang apa yang kamu lakukan.
- [ ] Jangan lebih-lebihkan — setiap bullet jadi pertanyaan interview.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan analogi trailer film ke teman yang ingin sertakan setiap sertifikat kursus dan pencapaian sekolah.

## 📐 Rancang

Tulis 3 impact bullet untuk CareerPilot dan 2 untuk pekerjaan non-tech sebelumnya, lalu tailor skill section-mu untuk dua lowongan berbeda (satu backend, satu frontend) — tunjukkan kedua urutan.

:::quiz
Tunjukkan rubrik review

- Tiap bullet mulai dengan kata kerja past-tense kuat dan sebutkan **apa** yang kamu buat.
- Minimal satu angka per project (tes, query, latency, endpoint, user) — cuma kalau benar.
- Bullet non-tech tunjukkan skill yang bisa dipindah dengan hasil (waktu hemat, error berkurang, customer terlayani).
- Tailoring backend bawa Python, Flask/FastAPI, PostgreSQL, Docker duluan; tailoring frontend bawa TypeScript, React/Next.js, accessibility, testing duluan.
- Tidak ada bullet yang tidak bisa kamu jelaskan 2 menit.
:::

### 📝 Checklist review mandiri

- [ ] Format aman ATS
- [ ] Impact bullet dengan bukti
- [ ] Tailoring cepat dan bisa diulangi

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

## 🛠️ Lakukan

1. Buat master CV-mu di plain document editor (Google Docs/Word) pakai struktur di atas.
2. Buat dua versi yang di-tailor: backend dan full-stack/frontend.
3. Paste teks PDF ke plain text editor — kalau urutan berantakan, sederhanakan tata letak.
4. Minta feedback dari satu engineer (mentor, alumni, komunitas).

## ✅ Selesai saat

- [ ] Master CV + 2 PDF yang di-tailor
- [ ] Setiap link aktif; setiap bullet bisa dipertahankan
- [ ] Feedback diterapkan

## 📖 Kamus

| Istilah | Bahasa Indonesia |
|---|---|
| CV / Resume | Daftar riwayat hidup |
| ATS (Applicant Tracking System) | Sistem pelacak pelamar |
| Impact bullet | Poin pencapaian berdampak |
| Tailoring | Menyesuaikan CV untuk tiap lowongan |
| Transferable skills | Keterampilan yang bisa dipakai lintas bidang |

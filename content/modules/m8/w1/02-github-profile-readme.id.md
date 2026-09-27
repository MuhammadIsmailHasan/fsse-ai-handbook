---
title: "GitHub Profile README"
summary: Buat profil GitHub-mu bekerja untukmu — profile README, repo disematkan, cerita kontribusi bersih, kerapian repo, pesan commit, dan yang harus dihindari (stat card berisik, aktivitas palsu, secret bocor).
sourceHash: 74382ca7eccd
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa yang dilihat recruiter dan engineer di `github.com/<kamu>` dalam 10 detik pertama
- Menulis **profile README** (repo khusus `<username>/<username>`)
- **Repo yang disematkan**, deskripsi repo, topic, dan link website
- Kerapian repo: README, license, `.gitignore`, tidak ada secret, release/tag
- Pesan commit dan history yang menceritakan kisah
- **Kontribusi open source** kecil dan nyata untuk junior

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Profile README** | Halaman perkenalan di profil GitHub-mu (repo `<kamu>/<kamu>`) |
| **Repo yang disematkan** | Hingga 6 proyek yang kamu pilih untuk ditampilkan pertama |
| **Kerapian repo** | Dasar-dasar: README, license, `.gitignore`, tidak ada secret |
| **Topic** | Label yang membuat repo mudah ditemukan |
| **Pesan commit** | Catatan yang menjelaskan satu perubahan |
| **Grafik kontribusi** | Kotak-kotak yang menunjukkan aktivitasmu sepanjang waktu |
| **Kontribusi open source** | Perubahan yang kamu buat ke proyek orang lain |

## 🧠 Ide besarnya

Profil GitHub-mu adalah **etalase toko**. Orang yang lewat memutuskan dalam hitungan detik apakah mereka masuk. Etalase yang bersih dengan tiga produk yang bagus (repo disematkan) dan papan kecil yang bilang apa yang kamu jual (profile README) lebih bagus daripada etalase yang penuh semua barang di gudang.

## ❓ Kenapa ini penting

CV dan LinkedIn-mu berdua link ke GitHub. Untuk orang tanpa pengalaman bertahun-tahun, GitHub adalah tempat klaim berubah menjadi bukti: kode nyata, test nyata, kebiasaan commit, dan cara kamu menulis dokumentasi.

Untuk aplikasi remote ini lebih penting lagi — perusahaan AS yang merekrut di zona waktu berbeda sering buka GitHub-mu sebelum CV, karena itu cara tercepat untuk lihat bagaimana kamu bekerja sungguhan.

Perbandingan etalase toko adalah seluruh pelajaran ini: tiga produk yang bagus lebih baik daripada etalase yang penuh semua barang.

## 📖 Langkah demi langkah

### 1. Profile README

Buat repo publik dengan nama persis seperti username-mu; `README.md`-nya muncul di profilmu.

```markdown
# Hi, I'm Muhammad Ismail 👋

Full-stack developer (Python · TypeScript) based in Indonesia, building products end to end — APIs, web apps and AI features.

🔭 **Currently building:** [CareerPilot](https://github.com/<you>/careerpilot) — a job-hunt assistant (Flask API + Next.js, 130+ tests, Docker, CI)
🛒 **Backend project:** [RevoShop](https://github.com/<you>/revoshop) — e-commerce API with Midtrans payments and RBAC
🌱 **Learning:** system design, RAG and LLM evaluation

**Stack:** Python, Flask, FastAPI, PostgreSQL, TypeScript, React, Next.js, Docker, GitHub Actions

📫 [LinkedIn](https://linkedin.com/in/<you>) · [Email](mailto:you@example.com) · Open to junior backend/full-stack roles (Jakarta or remote)
```

Jaga tetap singkat: siapa kamu, apa yang kamu buat, 2–3 link, cara menghubungimu. Satu stat card kecil boleh; dinding badge tidak.

### 2. Pin, deskripsi, topic

- Pin hingga 6 repo — tampilkan 2–3 flagship terlebih dahulu.
- Setiap repo: satu baris **deskripsi**, **topic** (`nextjs`, `flask`, `postgresql`), dan field **website** dengan URL live.
- Arsip repo yang tidak kamu maintenance lagi (tetap terlihat tapi read-only), atau jadikan private.

### 3. Checklist kerapian repo

Jalankan daftar ini di setiap repo yang kamu pin. Satu `.env` yang bocor atau README yang cuma bilang `# project` membatalkan semua kerja lainnya.

| File / pengaturan | Alasan |
|---|---|
| `README.md` | apa, kenapa, cara menjalankan dan test |
| `LICENSE` (misal MIT) | bilang orang lain boleh pakai apa |
| `.gitignore` | tidak ada `node_modules`, `.env`, `__pycache__` |
| `.env.example` | tunjukkan konfigurasi tanpa secret |
| CI workflow + badge | bukti test berjalan |
| Tag/release (`phase-2`, `v1.0.0`) | milestone dan changelog |
| Secret scanning / push protection | GitHub bisa blokir push yang punya format secret dikenal — biarkan nyala |

Kalau pernah commit secret: **rotate dulu** (revoke key-nya), baru hapus dari history. Menghapus file di commit baru tidak hapus dari history.

### 4. Commit yang menceritakan kisah

Reviewer skim history-mu untuk lihat cara kamu bekerja. Commit kecil dengan pesan jelas bilang "orang ini bisa kerja tim" lebih meyakinkan daripada satu baris di CV.

```text
feat(api): add status transition rules with history
fix(web): keep typed values after server validation errors
test(api): cover invalid transitions and ownership 404s
docs: add architecture diagram and decisions to README
```

- Commit kecil dengan prefix gaya **Conventional Commits** (`feat`, `fix`, `test`, `docs`, `refactor`, `chore`).
- Kerja di branch dan merge lewat pull request bahkan kalau solo — reviewer bisa lihat bagaimana kamu membagi pekerjaan.
- Jangan palsukan aktivitas (script yang commit setiap hari). Engineer perhatian, dan itu signal nilai yang salah.

### 5. Open source untuk junior

Kontribusi pertama yang realistis: perbaiki typo atau langkah yang tidak jelas di docs yang kamu pakai, tambah test yang hilang, duplikasi bug dengan contoh minimal, terjemahkan docs ke Bahasa Indonesia. Cari label `good first issue`, baca `CONTRIBUTING.md`, dan jaga PR tetap kecil.

### Pilih setupmu

Setiap pilihan di sini punya trade-off:

| | ✅ | ❌ |
|---|---|---|
| Profile README minimal | cepat dibaca, profesional | kurang "kepribadian" |
| Stat card/badge banyak | colorful | lambat, ribut, bilang sedikit tentang ability |
| Semua repo public | transparan | tunjukkan kerja tidak selesai/malu; arsip saja |
| Fokus pada grafik kontribusi | tunjukkan konsistensi | gampang dimanipulasi; bukan signal hire sendiri |

## ⚠️ Kesalahan umum

- Profile README lebih panjang daripada project README apa pun.
- Fork repo populer di-pin seakan itu kerja kamu.
- Repo flagship private sementara CV bilang "lihat GitHub-ku".
- Nomor HP pribadi dan alamat rumah di README publik.

## 🏆 Praktik terbaik

- [ ] Profile README: intro satu paragraph, flagship sekarang, stack, kontak, availability.
- [ ] 2–3 repo flagship di-pin, masing-masing dengan deskripsi, topic dan link live.
- [ ] Setiap repo publik punya README; yang tidak di-maintain di-arsip.
- [ ] Tidak ada secret di repo atau history mana pun; push protection nyala; `.env.example` sebagai gantinya.
- [ ] Pesan commit jelas; PR untuk fitur; tag untuk milestone.
- [ ] Nama sama, foto, dan headline seperti LinkedIn untuk dikenali.
- [ ] Pakai email profesional untuk commit (atau GitHub noreply address untuk privacy).

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ide etalase toko dan kenapa "30 badge" tidak membantu recruiter memutuskan untuk meneleponmu.

## 📐 Rancang

Buat draf profile README-mu (≤ 15 baris) dan daftar: 3 repo apa yang akan kamu pin dan urutan mana, deskripsi satu baris mereka dan topic, dan repo mana yang akan kamu arsip.

:::quiz
Lihat standar kualitas

- **Intro** menyebut target peran dan preferensi lokasi/remote dalam satu kalimat.
- **Link** ke proyek yang berjalan, bukan "coming soon".
- **Pin:** CareerPilot (cerita full-stack) → RevoShop (kedalaman backend) → satu proyek dukung. Deskripsi mulai dengan *apa yang dilakukan*, bukan stack: "Job-hunt tracker dengan hiring pipeline — Flask API + Next.js, 130+ test".
- **Topic:** 5–8 akurat per repo.
- **Arsip:** tutorial, fork tanpa perubahan, eksperimen ditinggal.
:::

### 📝 Checklist review mandiri

- [ ] Bisa dibaca dalam 10 detik
- [ ] Setiap link berjalan
- [ ] Tidak ada yang private atau secret terbuka

::ai-review{task="explain"}

::part[Latihan Kecil]{n="3"}

## 🛠️ Lakukannya

1. Buat `<username>/<username>` dan publish profile README-mu.
2. Update pin, deskripsi, topic, dan field website.
3. Jalankan secret scan di repo flagship-mu (misal `gitleaks detect`) dan nyalakan push protection.
4. Tambah `LICENSE`, `.env.example`, dan CI badge di tempat yang kurang.

## ✅ Selesai kalau

- [ ] Profile README live dan di-link dari LinkedIn
- [ ] Flagship di-pin dengan deskripsi, topic, dan link live
- [ ] Secret scan bersih di semua repo publik

## 📖 Kamus (glosarium)

| Istilah | Bahasa Indonesia |
|---|---|
| Profile README | README profil GitHub |
| Pinned repository | Repositori yang disematkan |
| Push protection | Perlindungan saat push (blokir secret) |
| Conventional Commits | Format standar pesan commit |
| Good first issue | Isu yang cocok untuk kontributor pemula |

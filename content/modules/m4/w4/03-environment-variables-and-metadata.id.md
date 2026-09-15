---
title: "Environment Variable & Metadata"
summary: Atur Next.js dengan aman — variabel khusus server vs NEXT_PUBLIC_, file .env, mengecek pengaturan saat aplikasi mulai — dan buat halaman tampil bagus saat dibagikan atau dicari, dengan judul halaman dan pratinjau link.
sourceHash: a59babefbd5c
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- File `.env`: jenis-jenisnya dan mana yang boleh di-commit
- Variabel khusus server vs variabel `NEXT_PUBLIC_`
- Menjauhkan rahasia dari browser
- Mengecek pengaturan saat aplikasi mulai
- Judul dan deskripsi halaman dengan Metadata API
- Pratinjau link (Open Graph), sitemap, dan robots

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Environment variable** | Pengaturan di luar kodemu, seperti `API_URL`, yang berbeda di setiap komputer atau server |
| **File `.env`** | File teks yang menyimpan environment variable |
| **Secret** | Nilai yang harus tetap rahasia: token, password, key |
| **`NEXT_PUBLIC_`** | Awalan yang menyalin variabel ke kode browser — jadi publik! |
| **Build time** | Saat `next build` membuat file-file aplikasi |
| **Metadata** | Informasi tentang halaman: judul, deskripsi, gambar pratinjau |
| **Open Graph** | Tag yang mengatur pratinjau link di WhatsApp, LinkedIn… |
| **BFF (Backend for Frontend)** | Server Next.js-mu memanggil API untuk browser dan menambahkan rahasianya |

## 🧠 Ide besarnya

Environment variable ada dua jenis:
- **Kunci rumah** — token API, URL database. Tetap di dalam rumah (server).
- **Nomor rumah** — URL situs publik, id analytics. Dicat di pagar untuk semua orang.

Awalan `NEXT_PUBLIC_` itu seperti **mengecat sebuah nilai di pagar**: begitu aplikasi di-build, setiap pengunjung bisa membacanya.

Metadata adalah **papan nama toko dan kartu nama**-mu: judul di tab browser, kartu pratinjau di WhatsApp dan LinkedIn, dan apa yang ditampilkan Google.

## ❓ Kenapa ini penting

- Aplikasi yang sama berjalan di laptopmu (Flask di `localhost:5091`), di server staging, dan di production — dengan URL dan key yang berbeda.
- Link lowongan yang dibagikan tanpa tag Open Graph tampil sebagai kartu kosong di LinkedIn, jadi tidak ada yang mengekliknya.

Kesalahan yang berbahaya:

```ts
// app/applications/client-list.tsx ("use client")
fetch(`${process.env.NEXT_PUBLIC_API_URL}/applications`, {
  headers: { Authorization: `Bearer ${process.env.NEXT_PUBLIC_API_TOKEN}` },   // 🚨 token inlined into public JS
});
```

Siapa pun bisa membuka DevTools → Sources dan membaca token itu. Dan kalau `API_URL` tidak ada di production, request diam-diam dikirim ke `"undefined/api/v1/..."`.

## 📖 Langkah demi langkah

### 1. File-file `.env`

| File | Di-commit? | Dipakai saat |
|---|---|---|
| `.env` | biasanya tidak (hanya default yang bukan rahasia) | selalu |
| `.env.local` | **tidak pernah** | selalu (menimpa `.env`); tidak saat tes |
| `.env.development` / `.env.production` | hanya default yang bukan rahasia | `next dev` / `next build` + `next start` |
| `.env.example` | **ya** — daftar variabel dengan nilai palsu | tidak pernah dimuat |

- Variabel sungguhan yang diatur di server (pengaturan Vercel, Docker `-e`, secret CI) menang atas file.
- `create-next-app` mengabaikan `.env*` di git. Tambahkan `!.env.example` ke `.gitignore` agar file contohnya ter-commit — itu **lembar petunjuk** untuk rekan tim.

### 2. Server vs publik

```bash
# .env.local
API_URL=http://localhost:5091           # server only
API_TOKEN=change-me                     # server only — secret
NEXT_PUBLIC_API_URL=http://localhost:5091   # inlined into browser JS at build time
```

- Tanpa awalan, variabel **hanya ada di server** (Server Component, Route Handler, Server Action).
- Dengan `NEXT_PUBLIC_`, nilainya **disalin ke file JavaScript saat `next build`** — seperti dicetak ke dalam buku. Mau diubah nanti → harus build ulang (cetak ulang).
- Hati-hati: image Docker yang di-build sekali untuk staging lalu dipindah ke production tetap berisi nilai **staging** yang sudah tercetak.
- Hanya referensi langsung yang disalin: `process.env.NEXT_PUBLIC_API_URL` ✅, `process.env[name]` ❌.

### 3. Simpan rahasia di server

```ts
// lib/data.ts
import "server-only";                  // importing this from a Client Component → build error

export async function getApplications(token: string) {
  return fetch(`${process.env.API_URL}/api/v1/applications`, { headers: { Authorization: `Bearer ${token}` } });
}
```

- `import "server-only"` adalah gembok: kalau Client Component meng-import file ini, build gagal.
- Saat kode browser butuh data yang dilindungi, ia bertanya ke **server Next.js-mu** (Route Handler atau Server Action). Server menambahkan rahasianya lalu memanggil Flask. Inilah pola **BFF** — seperti teller bank yang memakai kunci brankas untukmu, bukan memberikan kuncinya kepadamu.

### 4. Cek pengaturan saat mulai

```ts
export function readServerEnv(env = process.env) {
  const problems: string[] = [];
  if (!/^https?:\/\//.test(env.API_URL ?? "")) problems.push("API_URL must be an http(s) URL");
  if ((env.API_TOKEN ?? "").length < 20) problems.push("API_TOKEN must be at least 20 characters");
  if (problems.length) throw new Error(`Invalid environment:\n- ${problems.join("\n- ")}`);
  return { apiUrl: env.API_URL!.replace(/\/+$/, ""), apiToken: env.API_TOKEN! };
}
```

- Berhenti langsung dengan pesan yang jelas saat pengaturan hilang atau salah — seperti pengecekan pilot sebelum terbang.
- Tampilkan **nama, jangan pernah nilainya** (rahasia di log error adalah kebocoran).
- Ide yang sama dengan Modul 2 Minggu 6, sekarang dengan TypeScript. (Zod membuatnya lebih singkat — Minggu 5.)

### 5. Judul halaman

```tsx
// app/layout.tsx
import type { Metadata } from "next";

export const metadata: Metadata = {
  metadataBase: new URL("https://careerpilot.id"),   // makes relative URLs absolute
  title: { default: "CareerPilot", template: "%s · CareerPilot" },
  description: "Track job applications and prepare for interviews with AI.",
  openGraph: { siteName: "CareerPilot", locale: "id_ID", type: "website" },
};
```

- `title.template`: halaman dengan `title: "Applications"` menampilkan `Applications · CareerPilot` di tab.
- `title.default`: dipakai saat halaman tidak mengatur judul.
- `metadataBase`: mengubah URL relatif (seperti `/jobs/1`) menjadi URL lengkap untuk pratinjau.

### 6. Judul dari data: `generateMetadata`

```tsx
// app/jobs/[id]/page.tsx
export async function generateMetadata({ params }: { params: Promise<{ id: string }> }): Promise<Metadata> {
  const { id } = await params;
  const job = await getJob(Number(id));
  if (!job) return { title: "Job not found", robots: { index: false } };
  const description = `${job.title} at ${job.company} in ${job.city}`;
  return {
    title: job.title,
    description,
    alternates: { canonical: `/jobs/${id}` },
    openGraph: { title: job.title, description, url: `/jobs/${id}` },
  };
}
```

- Setiap halaman lowongan mendapat judul dan pratinjaunya sendiri — seperti label nama untuk setiap produk di rak.
- `canonical` = "ini alamat utama halaman ini" (membantu Google).
- `robots: { index: false }` = "jangan tampilkan halaman ini di Google".
- Metadata hanya berfungsi di **Server Component**.

### 7. File metadata khusus

| File di `app/` | Menghasilkan |
|---|---|
| `favicon.ico`, `icon.png`, `apple-icon.png` | ikon situs |
| `opengraph-image.png` atau `opengraph-image.tsx` | gambar pratinjau link |
| `sitemap.ts` | `/sitemap.xml` (daftar halaman untuk Google) |
| `robots.ts` | `/robots.txt` (halaman mana yang boleh dikunjungi Google) |

Halaman privat (dashboard) sebaiknya tidak diindeks. Halaman lowongan publik sebaiknya ada di sitemap.

## ⚠️ Kesalahan umum

- `NEXT_PUBLIC_API_KEY=sk-live-…` — rahasia yang dijadikan publik.
- Mengubah nilai `NEXT_PUBLIC_` dan berharap berlaku tanpa build ulang.
- Menaruh file `.env` di dalam `src/` (Next.js membacanya dari root proyek).
- Meng-commit `.env.local`.
- URL gambar pratinjau relatif tanpa `metadataBase`.
- Membiarkan Google mengindeks halaman privat atau kosong.

## 🏆 Praktik terbaik

- [ ] Commit `.env.example`; jangan pernah commit `.env.local` atau rahasia sungguhan.
- [ ] Pakai rahasia hanya di kode server; tambahkan `import "server-only"` ke file data.
- [ ] Cek environment variable saat aplikasi mulai, dengan nama tapi tanpa nilai di pesan error.
- [ ] Ingat nilai `NEXT_PUBLIC_` terkunci saat build — rencanakan build per environment.
- [ ] `metadata` di root dengan `metadataBase`, template judul, dan deskripsi; `generateMetadata` untuk halaman dinamis.
- [ ] Tambahkan gambar pratinjau, `sitemap.ts`, dan `robots.ts`; `noindex` untuk halaman privat dan not-found.
- [ ] Tes pratinjau link dengan Post Inspector LinkedIn sebelum rilis.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Dengan ide kunci rumah vs nomor rumah, jelaskan ke rekan tim kenapa `NEXT_PUBLIC_API_TOKEN` adalah masalah keamanan walaupun "harus login dulu", dan apa yang diubah oleh pola BFF.

## 📐 Rancang

Frontend CareerPilot di-build sekali sebagai image Docker lalu dipindahkan dari staging ke production. Ia butuh: URL situs publik, URL Flask API, id analytics, token rahasia untuk API service, dan feature flag "AI match aktif". Tentukan variabel apa saja yang ada, awalannya, bagaimana browser mendapat nilai yang berbeda per environment **tanpa build ulang**, dan cara mengeceknya.

:::quiz
Tampilkan contoh desainnya

| Variabel | Jenis | Kenapa |
|---|---|---|
| `SITE_URL` | server | dipakai di `metadataBase`, sitemap, email |
| `API_URL` | server | Server Component / Route Handler memanggil Flask |
| `API_SERVICE_TOKEN` | server, rahasia | panggilan antar server; tidak pernah ke browser |
| `ANALYTICS_ID` | server → diberikan ke browser saat runtime | berbeda per environment; image di-build sekali |
| `FEATURE_AI_MATCH` | server → diberikan ke browser saat runtime | flag berbeda per environment |

- **Tanpa variabel `NEXT_PUBLIC_`**, karena image yang sama dipindah ke production: nilai yang tercetak saat build akan menyimpan nilai staging selamanya.
- **Cara browser mendapatkannya**: root layout (Server Component) membaca `ANALYTICS_ID` dan `FEATURE_AI_MATCH` lalu mengirimnya sebagai props ke `ConfigProvider` kecil di client. Atau Route Handler `GET /api/config` mengembalikan nilai-nilai publiknya saja.
- **Request data dari browser** melewati Route Handler (BFF), yang menambahkan sesi pengguna dan memanggil `API_URL`.
- **Pengecekan** di `lib/env.ts` (server-only), dijalankan saat mulai: URL harus http(s), token minimal 32 karakter di production, flag harus `"true"` atau `"false"`. Error hanya menyebut nama. `.env.example` mendokumentasikan semuanya dengan nilai palsu.
:::

### 📝 Checklist self-review

- [ ] Rahasia tidak pernah sampai ke browser
- [ ] "Build sekali, deploy ke banyak environment" sudah ditangani
- [ ] Pengecekan tanpa membocorkan nilai

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/web/m4/w4/03-env-metadata" ai="no-ai" title="Konfigurasi env yang divalidasi dan metadata halaman"}
Tulis pembaca env server yang berhenti lebih awal dengan error yang jelas, `publicEnv` yang aman untuk browser dengan referensi `NEXT_PUBLIC_` langsung, dokumentasikan variabelnya di `.env.example`, dan tambahkan metadata root dengan template judul plus `generateMetadata` untuk halaman lowongan dinamis (termasuk versi not-found dengan `noindex`).
:::

:::hints
- Kumpulkan masalah di sebuah array; lempar error sekali, dengan hanya nama di pesannya.
- `metadataBase: new URL("https://careerpilot.id")`.
- `generateMetadata` menerima Promise `params` yang sama dengan halamannya.
:::

## ✅ Cek cepat

:::quiz
Kapan nilai `process.env.NEXT_PUBLIC_API_URL` ditetapkan untuk kode browser?

Saat build (`next build`) — diganti dengan teks sebenarnya di dalam file JavaScript.
:::

:::quiz
Apa fungsi `title.template` di root layout?

Memformat judul halaman-halaman di dalamnya. `"%s · CareerPilot"` mengubah judul halaman "Jobs" menjadi "Jobs · CareerPilot". `title.default` dipakai saat halaman tidak mengatur judul.
:::

## 📚 Lanjut belajar

- Dokumentasi Next.js (tersedia di dalam proyek): panduan Environment Variables; Metadata and OG images; referensi `generateMetadata`
- [Open Graph protocol](https://ogp.me/)

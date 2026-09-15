---
title: "Setup Next.js & Component React"
summary: Buat aplikasi Next.js 16 di port non-default, pahami folder-foldernya, dan pelajari ide utama React — component yang mengubah data menjadi tampilan dengan JSX — plus gambaran awal Server dan Client Component.
sourceHash: ad306eef01fa
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa itu React dan Next.js
- Membuat proyek Next.js 16 dan menjalankannya di port 3091
- Folder dan file utamanya
- JSX: menulis kode mirip HTML di dalam JavaScript
- Component, `children`, dan list dengan `key`
- Server Component vs Client Component (`"use client"`) — ide dasarnya
- Tools: React DevTools dan tampilan error Next.js

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **React** | Library untuk membangun tampilan dari component |
| **Next.js** | Framework di atas React yang menambahkan halaman, routing, dan render di server |
| **Component** | Function yang mengembalikan sepotong tampilan, seperti `JobCard` |
| **JSX** | Sintaks mirip HTML di dalam JavaScript: `<h1>{title}</h1>` |
| **Props** | Input yang kamu berikan ke component: `<JobCard job={job} />` |
| **Render** | React mengubah component-mu menjadi apa yang tampil di layar |
| **Server Component** | Berjalan di server; hanya mengirim HTML, tanpa JavaScript |
| **Client Component** | Berjalan di browser; bisa memakai klik dan state (`"use client"`) |

## 🧠 Ide besarnya

Di Minggu 1 kamu mengubah halaman langkah demi langkah: "cari list-nya, kosongkan, buat `li`, tambahkan…". React membalik cara ini: kamu **menjelaskan seperti apa tampilan untuk data saat ini**, dan React yang mencari tahu perubahannya.

Component itu seperti **resep**: `JobCard(job) → kartu di layar`. Bahan (data) berbeda → hidangan (kartu) berbeda. Resep-resep kecil digabung menjadi resep yang lebih besar — sebuah halaman hanyalah component yang tersusun dari component lain, seperti sepiring nasi campur yang terdiri dari lauk-lauk kecil.

## ❓ Kenapa ini penting

- Mengubah DOM secara manual jadi tidak terkendali saat aplikasi membesar: setiap perubahan harus ingat semua tempat yang perlu diperbarui.
- React adalah library frontend yang paling banyak dipakai. **Next.js** adalah framework React paling populer: menambahkan halaman, render di server, dan banyak optimasi.
- Tanpa component, memperbaiki satu kartu berarti memperbaikinya di 12 salinan.
- React + Next.js adalah stack yang paling sering muncul di lowongan frontend dan full-stack, termasuk posisi remote.

## 📖 Langkah demi langkah

### 1. Buat aplikasinya

```bash
npx create-next-app@latest careerpilot-web --yes   # TypeScript, Tailwind, ESLint, App Router, Turbopack
cd careerpilot-web
npm run dev -- --port 3091                          # the handbook's frontend port (3000 is often taken)
```

Simpan port-nya di `package.json`, agar semua orang di tim memakai port yang sama:

```json
{
  "scripts": {
    "dev": "next dev --port 3091",
    "build": "next build",
    "start": "next start --port 3091",
    "lint": "eslint"
  }
}
```

- Next.js 16 butuh Node.js 20.9 atau lebih baru.
- Proyek baru menyertakan file `AGENTS.md` yang memberi tahu tool AI coding untuk membaca dokumentasi Next.js yang sesuai versimu (di dalam `node_modules/next/dist/docs`). Next.js berubah cepat, jadi ini berguna.

### 2. Folder-foldernya

```text
careerpilot-web/
├── app/                    ← App Router: folders = URLs
│   ├── layout.tsx          ← root layout: <html>, <body>, shared UI (required)
│   ├── page.tsx            ← the "/" route
│   ├── globals.css         ← @import "tailwindcss"
│   └── jobs/
│       └── page.tsx        ← the "/jobs" route (Week 4)
├── public/                 ← static files served at "/" (logo.svg → /logo.svg)
├── next.config.ts
├── tsconfig.json           ← includes the "@/*" import alias
├── eslint.config.mjs
└── package.json
```

Folder `app/` bekerja seperti **papan petunjuk gedung**: setiap folder adalah satu lantai (sebuah URL), dan `page.tsx` adalah ruangan yang dikunjungi orang.

```tsx
// app/layout.tsx
import "./globals.css";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
```

```tsx
// app/page.tsx
export default function Page() {
  return <h1 className="text-3xl font-bold">Hello, CareerPilot!</h1>;
}
```

- `layout.tsx` = bingkai yang dipakai bersama oleh semua halaman.
- `page.tsx` = isi dari satu halaman. `{children}` di layout adalah tempat halaman itu muncul.

### 3. JSX

JSX terlihat seperti HTML, tapi sebenarnya JavaScript:

```tsx
const job = { title: "Backend Engineer", company: "Kopi Data", remote: false };

<article className="rounded-xl p-4">            {/* class → className */}
  <h2>{job.title}</h2>                           {/* { } embeds any JS expression */}
  <p>{job.company.toUpperCase()}</p>
  <label htmlFor="note">Note</label>             {/* for → htmlFor */}
  <input id="note" disabled={!job.remote} />      {/* attributes can be expressions */}
  <img src="/logo.png" alt="" />                  {/* every tag must close */}
</article>
```

- `{ }` menaruh nilai JavaScript di dalam markup.
- `class` menjadi `className`, `for` menjadi `htmlFor`, nama event memakai camelCase (`onClick`).
- Setiap tag harus ditutup (`<img />`).
- Kembalikan satu elemen terluar, atau bungkus elemen bersebelahan dengan `<>…</>` (fragment).
- Teks **otomatis di-escape**: `{job.title}` tidak pernah bisa menyisipkan HTML. Masalah XSS dari Minggu 1 terselesaikan secara default.

### 4. Component

```tsx
type Job = { id: number; title: string; company: string; city: string };

export function JobCard({ job }: { job: Job }) {
  return (
    <article>
      <h2>{job.title}</h2>
      <p>{job.company} · {job.city}</p>
    </article>
  );
}
```

- Component adalah function yang mengembalikan JSX.
- Namanya diawali **huruf kapital**: `<JobCard />` adalah component, `<article>` adalah tag HTML.
- Component sebaiknya **pure**: props sama → hasil sama, dan tanpa efek samping (seperti panggilan API) saat menggambar. Seperti kalkulator: 2 + 2 selalu menampilkan 4.

### 5. `children`: menaruh sesuatu di dalam component

```tsx
export function Card({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="rounded-xl border p-4">
      <h2>{title}</h2>
      {children}
    </section>
  );
}

<Card title="Notes">
  <p>Recruiter called on Monday</p>
</Card>
```

`children` adalah apa pun yang kamu taruh di antara tag pembuka dan penutup — seperti **kotak kado**: kotaknya selalu sama, hadiah di dalamnya yang berganti. Layout, popup, dan pembungkus semuanya memakai ini.

### 6. List dan key

```tsx
<ul>
  {jobs.map((job) => (
    <li key={job.id}>
      <JobCard job={job} />
    </li>
  ))}
</ul>
```

`key` itu seperti **name tag** untuk setiap item, agar React tahu item mana yang mana setelah list berubah. Pakai id yang stabil dari datamu. Jangan pernah `Math.random()`, dan hindari index array kalau item bisa ditambah, dihapus, atau diurutkan ulang (materi 06 menunjukkan bug-nya).

### 7. Server Component dan Client Component

Di Next.js, **setiap component adalah Server Component secara default**. Ia berjalan di server, bisa memuat data langsung, menyimpan rahasia di sana, dan **tidak mengirim JavaScript** untuk dirinya ke browser — seperti dapur restoran yang mengirim hidangan jadi, bukan kompornya.

Saat sebuah component butuh **state, handler klik, effect, atau fitur browser**, tulis `"use client"` di bagian paling atas file-nya:

```tsx
// app/jobs/save-button.tsx
"use client";

import { useState } from "react";

export function SaveButton() {
  const [saved, setSaved] = useState(false);
  return <button onClick={() => setSaved(!saved)}>{saved ? "Saved" : "Save"}</button>;
}
```

```tsx
// app/jobs/page.tsx — Server Component using a Client Component
import { SaveButton } from "./save-button";

export default function JobsPage() {
  return (
    <main>
      <h1>Jobs</h1>
      <SaveButton />
    </main>
  );
}
```

`"use client"` menarik sebuah **garis**: file itu dan semua yang di-import-nya dikirim ke browser. Buat bagian ini sekecil mungkin. Minggu 4 membahasnya secara mendalam. Untuk sekarang ingat: **interaktif → client**.

### 8. Tools

- **React Developer Tools** (extension browser): lihat pohon component, props, dan state.
- **Tampilan error Next.js**: error muncul di browser beserta file dan barisnya.
- `console.log` di Server Component tercetak di **terminal**; di Client Component, di console **browser**.

## ⚠️ Kesalahan umum

- `class` bukan `className`; lupa menutup tag.
- Nama component berhuruf kecil (`<jobCard />` dianggap tag HTML yang tidak dikenal).
- Memakai `useState` atau `onClick` di file tanpa `"use client"`.
- Menambahkan `"use client"` ke `layout.tsx` "biar error-nya hilang" — akibatnya seluruh aplikasi berjalan di browser.
- Menyalin-tempel markup alih-alih membuat component.

## 🏆 Praktik terbaik

- [ ] Buat proyek dengan TypeScript dan ESLint; set port dev non-default di `package.json`.
- [ ] Satu tugas per component; props ber-type.
- [ ] Jaga component tetap pure — tanpa efek samping saat render.
- [ ] `key` yang stabil dan unik dari id data.
- [ ] Server Component sebagai default; `"use client"` hanya untuk bagian kecil yang interaktif.
- [ ] Pakai alias import `@/` alih-alih path panjang `../../..`.
- [ ] Install React DevTools sejak hari pertama.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke rekan tim beda kode DOM di Minggu 1 ("cari list-nya, tambahkan item") dengan React ("jelaskan tampilan untuk data ini"). Pakai analogi resep.

## 📐 Rancang

Pecah **halaman dashboard** CareerPilot menjadi component: header dengan menu pengguna, kartu statistik, daftar "lamaran terbaru" dengan badge status, panel "lowongan tersimpan" dengan tombol simpan/batal simpan, dan tampilan kosong. Tulis props setiap component, dan tandai mana yang harus menjadi Client Component.

:::quiz
Tampilkan contoh pohonnya

```text
app/dashboard/page.tsx            (Server) — loads data, composes the page
├── <SiteHeader user>             (Server)
│   └── <UserMenu user>           (Client: open/close state, click outside)
├── <StatsGrid stats>             (Server)
│   └── <StatCard label value trend?>   (Server)
├── <RecentApplications applications>   (Server)
│   ├── <ApplicationRow application>    (Server)
│   │   └── <StatusBadge status>        (Server)
│   └── <EmptyState message action?>    (Server)
└── <SavedJobsPanel initialJobs>        (Client: saving/unsaving updates the list)
    └── <SavedJobItem job onUnsave>     (Client, inside the client boundary)
        └── <SaveButton saved onToggle jobTitle>
```

- Props berupa data sederhana (`stats`, `applications`) yang bisa dikirim dari server ke browser.
- Hanya `UserMenu` dan panel lowongan tersimpan yang mengirim JavaScript ke browser; sisanya HTML biasa dari server.
- `StatusBadge` dan `EmptyState` adalah potongan kecil yang bisa dipakai ulang di banyak halaman.
:::

### 📝 Checklist self-review

- [ ] Setiap component punya satu tugas yang jelas dan props ber-type
- [ ] Hanya bagian interaktif yang menjadi Client Component
- [ ] Potongan yang bisa dipakai ulang sudah diidentifikasi

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/web/m4/w3/01-components" ai="no-ai" title="Component presentasional pertamamu"}
Bangun `PageHeader`, `JobCard`, `EmptyState`, `JobList`, dan `JobsPage` sebagai function component ber-type: subjudul dan gaji yang opsional, list dengan key yang stabil, dan `children`. Tes me-render-nya dengan Testing Library, gagal kalau ada peringatan key dari React, dan melakukan type-check pada file-nya.
:::

:::hints
- `{subtitle && <p>{subtitle}</p>}` hanya menampilkan paragraf kalau ada subjudul (aman untuk string; untuk angka pakai `> 0`).
- `JobList` bisa langsung mengembalikan `<EmptyState … />` saat array-nya kosong.
- Bungkus dua elemen tingkat atas dengan fragment `<>…</>`.
:::

:::sandpack{template="react-ts" title="Coba JSX di browser"}
```tsx App.tsx
type Job = { id: number; title: string; company: string };

const jobs: Job[] = [
  { id: 1, title: "Backend Engineer", company: "Kopi Data" },
  { id: 2, title: "AI Engineer", company: "Lintas AI" },
];

function JobCard({ job }: { job: Job }) {
  return (
    <article style={{ border: "1px solid #ddd", borderRadius: 12, padding: 12, marginBottom: 8 }}>
      <h2 style={{ margin: 0 }}>{job.title}</h2>
      <p style={{ margin: 0, color: "#64748b" }}>{job.company}</p>
    </article>
  );
}

export default function App() {
  return (
    <main style={{ fontFamily: "system-ui", padding: 16 }}>
      <h1>Jobs for you</h1>
      {jobs.map((job) => (
        <JobCard key={job.id} job={job} />
      ))}
    </main>
  );
}
```
:::

## ✅ Cek cepat

:::quiz
Kenapa nama component harus diawali huruf kapital?

JSX menganggap tag berhuruf kecil sebagai elemen HTML (`<article>`) dan yang berhuruf kapital sebagai component (`<JobCard />`).
:::

:::quiz
Kapan sebuah component butuh `"use client"`?

Saat memakai state, effect, handler klik, custom hook, atau fitur yang hanya ada di browser.
:::

## 📚 Lanjut belajar

- [React docs: Your First Component](https://react.dev/learn/your-first-component)
- [React docs: Writing Markup with JSX](https://react.dev/learn/writing-markup-with-jsx)
- Dokumentasi Next.js (juga tersedia di `node_modules/next/dist/docs`): Installation, Project Structure, Server and Client Components

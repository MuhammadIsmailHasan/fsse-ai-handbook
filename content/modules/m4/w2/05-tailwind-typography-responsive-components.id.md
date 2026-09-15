---
title: "Tailwind: Tipografi, Desain Responsif & Component"
summary: Bangun tampilan sungguhan dengan utility class — ukuran teks, jarak, warna, state hover dan fokus, prefix mobile-first, dark mode, dan mengubah daftar class yang berulang menjadi component.
sourceHash: fe6340a85b5b
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Class Tailwind yang paling sering dipakai: jarak, ukuran, teks, warna, border
- Class untuk state: `hover:`, `focus-visible:`, `disabled:`, `group-hover:`, `aria-*`
- Prefix mobile-first (`sm:`, `md:`, `lg:`) dan container query
- Dark mode dengan `dark:`
- Styling artikel panjang dengan `prose`
- Membuat component alih-alih menyalin daftar class yang panjang

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Scale** | Daftar ukuran tetap dari Tailwind: `p-1`, `p-2`, `p-4`… |
| **Variant / prefix** | Kondisi sebelum class: `hover:bg-blue-500` hanya berlaku saat hover |
| **Responsive prefix** | `md:` = "mulai layar sedang **dan lebih besar**" |
| **`group`** | Tandai parent agar child bisa bereaksi saat parent di-hover: `group-hover:` |
| **`sr-only`** | Tersembunyi di layar, tapi dibacakan screen reader |
| **Arbitrary value** | Nilai sekali pakai dalam kurung siku: `mt-[13px]` |

## 🧠 Ide besarnya

Class Tailwind itu seperti **belajar kosakata bahasa baru**. Hari-hari pertama kamu mencari arti setiap kata. Setelah seminggu kamu "berbicara layout": `flex items-center justify-between gap-4` terbaca seperti kalimat — "taruh dalam satu baris, tengahkan secara vertikal, sebar, beri jarak". Pengetahuan CSS-mu dari Minggu 1 tetap berlaku: setiap class adalah satu rule CSS dengan nilai dari skala desain.

## ❓ Kenapa ini penting

Kebanyakan pekerjaan UI adalah menggabungkan beberapa property yang sama dengan nilai yang konsisten. Tailwind memungkinkanmu melakukannya tepat di samping elemennya, dan prefix seperti `md:`, `hover:`, dan `dark:` menangani ukuran layar dan state di tempat yang sama.

Kalau dipakai sembarangan, jadi sulit dirawat:

```html
<div class="mt-[13px] ml-[7px] text-[15px] text-[#4b5563] w-[437px]">…</div>
<button class="bg-indigo-600 text-white">Save</button>   <!-- no hover, focus or disabled states -->
```

- Nilai acak merusak tampilan yang konsisten dan tidak menyesuaikan layar.
- Tanpa style hover atau fokus: pengguna keyboard tidak tahu posisinya di mana.
- Tombol berisi 40 class yang disalin ke 30 tempat = 30 kali edit untuk satu perubahan desain.

## 📖 Langkah demi langkah

### 1. Class yang sering dipakai

| Kelompok | Contoh | Fungsinya |
|---|---|---|
| Jarak (kelipatan 0.25rem) | `p-4`, `px-2`, `mt-6`, `gap-3`, `space-y-2` | padding, margin, jarak |
| Ukuran | `w-full`, `max-w-5xl`, `h-12`, `size-10`, `min-h-dvh` | lebar dan tinggi |
| Teks | `text-sm`, `text-2xl`, `font-semibold`, `leading-relaxed`, `tracking-tight`, `line-clamp-2`, `truncate` | ukuran, ketebalan, baris |
| Warna | `bg-white`, `text-slate-600`, `border-slate-200`, `bg-indigo-600/90` | warna (`/90` = opacity 90%) |
| Border & bayangan | `border`, `rounded-xl`, `ring-1`, `shadow-sm`, `outline-2` | tepi dan kedalaman |
| Layout | `flex`, `grid`, `grid-cols-3`, `items-center`, `justify-between`, `hidden`, `sr-only` | menata posisi |

- `truncate` memotong teks panjang dengan "…" dalam satu baris; `line-clamp-2` membolehkan 2 baris.
- `sr-only` menyembunyikan teks secara visual tapi tetap dibacakan screen reader — cocok untuk tombol yang hanya berisi ikon.

### 2. State

```html
<button class="rounded-lg bg-indigo-600 px-4 py-2 text-white
               hover:bg-indigo-500
               focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-600
               disabled:cursor-not-allowed disabled:opacity-50">
  Save
</button>

<a class="group flex items-center gap-2">
  <span class="group-hover:underline">View job</span>
  <svg class="transition group-hover:translate-x-1" aria-hidden="true">…</svg>
</a>

<button aria-pressed="true" class="aria-pressed:bg-indigo-50 aria-pressed:text-indigo-700">Saved</button>
<div data-state="open" class="data-[state=open]:block hidden">…</div>
```

- `hover:` — saat mouse di atasnya. `focus-visible:` — saat dijangkau dengan keyboard. `disabled:` — saat tombol nonaktif.
- `group` + `group-hover:` — meng-hover **parent** mengubah **child**, seperti satu saklar yang mengendalikan beberapa lampu.
- `aria-pressed:` — style dari state aksesibilitas. Tampilan dan maknanya selalu cocok, karena berasal dari atribut yang sama.

### 3. Mobile first

```html
<ul class="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">…</ul>
<h1 class="text-2xl sm:text-3xl lg:text-4xl">Jobs for you</h1>
<aside class="hidden md:block">Filters</aside>
```

| Prefix | Mulai lebar |
|---|---|
| `sm:` | 40rem (640px) |
| `md:` | 48rem (768px) |
| `lg:` | 64rem (1024px) |
| `xl:` | 80rem (1280px) |
| `2xl:` | 96rem (1536px) |

Class **tanpa** prefix berlaku untuk semua layar. Prefix berarti "**mulai lebar ini dan lebih besar**" — seperti aturan film "17+": bukan berarti "hanya umur 17". Pakai `max-md:` kalau kamu butuh "lebih kecil dari md".

Container query sudah tersedia, jadi kartu bisa menyesuaikan dengan kotak tempatnya berada:

```html
<div class="@container">
  <article class="flex flex-col @md:flex-row">…</article>
</div>
```

### 4. Dark mode

```html
<article class="bg-white text-slate-900 dark:bg-slate-900 dark:text-slate-100">…</article>
```

Class `dark:` berlaku di dark mode. Secara default ini mengikuti pengaturan HP atau komputer; dengan custom variant dari materi 04, ini mengikuti class `.dark` yang kamu nyalakan.

### 5. Artikel panjang: `prose`

Untuk konten Markdown atau blog, plugin Typography men-styling semuanya dengan satu class:

```css
@plugin "@tailwindcss/typography";
```

```html
<article class="prose dark:prose-invert max-w-none">…rendered markdown…</article>
```

(Handbook ini memakai `prose` untuk materinya.)

### 6. Component, bukan copy-paste

Saat daftar class panjang yang sama muncul berulang kali, buat **component** (React, Minggu 3) — seperti menyimpan resep daripada mengingat bahannya setiap kali:

```tsx
function Badge({ children }: { children: React.ReactNode }) {
  return <span className="inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium">{children}</span>;
}
```

`@apply` di CSS juga ada, tapi memakainya di mana-mana membawa kembali masalah penamaan yang sudah diselesaikan Tailwind. Pakai hanya untuk HTML yang tidak bisa kamu tambahi class (dari library pihak ketiga).

### 7. Membaca daftar class yang panjang

Baca per kelompok: **layout → kotak → teks → warna → state → ukuran layar**. Plugin Prettier untuk Tailwind otomatis mengurutkan class dengan urutan seperti ini.

## ⚠️ Kesalahan umum

- Mengira `md:` berarti "hanya layar sedang" (artinya sedang **dan lebih besar**).
- Lupa `min-w-0` pada child flex, sehingga `truncate` tidak berfungsi dan teks panjang meluber.
- Tidak ada style `focus-visible:` di tombol dan link.
- Nilai acak seperti `mt-[13px]` alih-alih memakai skala.
- Menyalin tombol berisi 30 class alih-alih membuat component.
- Menunjukkan state hanya dengan warna.

## 🏆 Praktik terbaik

- [ ] Mobile first: class dasar untuk ponsel, prefix untuk layar yang lebih besar.
- [ ] Setiap elemen interaktif punya style `hover:`, `focus-visible:`, dan `disabled:`.
- [ ] Tombol yang hanya berisi ikon punya label `sr-only`; styling dari state `aria-*`.
- [ ] Tetap di skala; tambahkan nilai yang kurang ke `@theme`, bukan `[…]`.
- [ ] Ubah kelompok class yang berulang menjadi component.
- [ ] Urutkan class dengan Prettier.
- [ ] Tes dark mode dan zoom 200%.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan prefix mobile-first ke seorang desainer: apa yang ditampilkan `grid-cols-1 md:grid-cols-2 xl:grid-cols-4` di ponsel 375px, tablet 800px, dan laptop 1440px?

## 📐 Rancang

Tulis class Tailwind untuk **kartu lamaran** CareerPilot di papan: logo perusahaan, judul lowongan (satu baris, dipotong dengan "…"), perusahaan + lokasi (abu-abu), badge status, "diperbarui 2 hari lalu", tombol ikon menu yang aksesibel, bayangan saat hover, cincin fokus saat link kartu difokuskan, dan layout ringkas di kolom sempit dengan container query.

:::quiz
Tampilkan contoh markup-nya

```html
<li class="@container">
  <article class="group relative flex gap-3 rounded-xl border border-slate-200 bg-white p-3 shadow-sm transition
                  hover:shadow-md focus-within:ring-2 focus-within:ring-indigo-600
                  dark:border-slate-800 dark:bg-slate-900">
    <img src="…" alt="" class="size-10 shrink-0 rounded-lg object-cover" />
    <div class="min-w-0 flex-1">
      <h3 class="truncate text-sm font-semibold text-slate-900 dark:text-white">
        <a href="/applications/12" class="outline-none after:absolute after:inset-0">Senior Backend Engineer</a>
      </h3>
      <p class="truncate text-xs text-slate-500 dark:text-slate-400">Kopi Data · Jakarta</p>
      <div class="mt-2 flex flex-col gap-1 @xs:flex-row @xs:items-center @xs:justify-between">
        <span class="inline-flex w-fit items-center rounded-full bg-amber-50 px-2 py-0.5 text-xs font-medium text-amber-800">Interview</span>
        <time datetime="2026-09-12" class="text-xs text-slate-500">Updated 2 days ago</time>
      </div>
    </div>
    <button type="button" class="relative z-10 self-start rounded-md p-1 text-slate-500 hover:bg-slate-100 focus-visible:outline-2 focus-visible:outline-indigo-600">
      <span class="sr-only">Actions for Senior Backend Engineer</span>
      <svg aria-hidden="true" class="size-4">…</svg>
    </button>
  </article>
</li>
```

- `min-w-0` membuat `truncate` berfungsi di dalam flex.
- `after:absolute after:inset-0` pada link merentangkan area kliknya ke seluruh kartu, sambil tetap hanya ada satu link untuk difokuskan.
- Tombol menu berada di atas area itu dengan `relative z-10`.
- `alt=""` karena nama perusahaan sudah tertulis sebagai teks.
- `sr-only` memberi tombol ikon nama yang spesifik.
:::

### 📝 Checklist self-review

- [ ] Teks panjang terpotong dengan benar (`min-w-0`)
- [ ] Satu link yang jelas, dan tombol ikon yang aksesibel
- [ ] Fokus terlihat, dark mode ditangani
- [ ] Tetap rapi di kolom sempit

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/web/m4/w2/05-tailwind-components" ai="no-ai" title="Kartu lowongan responsif hanya dengan utility"}
Styling halaman daftar lowongan hanya dengan class Tailwind: container, heading dan grid yang responsif, kartu dengan dark mode, deskripsi yang dibatasi beberapa baris, badge, dan tombol dengan state hover, focus-visible, dan disabled. Tes mengecek class-mu, melarang nilai sembarang dan inline style, dan mem-build Tailwind untuk menangkap salah ketik.
:::

:::hints
- `flex flex-col` pada kartu + `mt-auto` pada tombol mendorong tombol ke bawah.
- `w-fit` mencegah badge melebar di kolom flex.
- Kalau sebuah class "tidak ada", cek ejaannya di dokumentasi Tailwind (misalnya `grid-cols-2`, bukan `grid-col-2`).
:::

## ✅ Cek cepat

:::quiz
Apa yang dilakukan `md:hidden`?

Menyembunyikan elemen mulai lebar `md` (48rem) dan lebih besar. Di layar yang lebih kecil, elemen tetap terlihat.
:::

:::quiz
Kenapa styling dengan `aria-pressed:` dan bukan class "active" terpisah?

Tampilannya otomatis mengikuti state aksesibilitas, jadi keduanya tidak pernah berbeda.
:::

## 📚 Lanjut belajar

- [Tailwind CSS docs: Responsive design](https://tailwindcss.com/docs/responsive-design)
- [Tailwind CSS docs: Hover, focus, and other states](https://tailwindcss.com/docs/hover-focus-and-other-states)
- [Tailwind CSS docs: Dark mode](https://tailwindcss.com/docs/dark-mode)

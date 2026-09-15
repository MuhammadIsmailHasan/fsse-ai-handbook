---
title: "Navigasi: Link, Penanda Halaman Aktif & Routing dari Kode"
summary: Berpindah halaman dengan cara Next.js — Link untuk perpindahan yang cepat, menandai link halaman saat ini, breadcrumb, menyimpan filter di URL, dan useRouter untuk berpindah setelah sebuah aksi.
sourceHash: b1be5d57a2b6
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- `<Link>`: berpindah halaman tanpa reload penuh
- Menandai link halaman yang sedang dibuka
- Breadcrumb yang dibangun dari URL
- **URL sebagai state**: filter, nomor halaman, dan tab di `?status=…`
- Berpindah halaman dari kode dengan `useRouter` dan `redirect()`
- Menunjukkan bahwa halaman sedang dimuat

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **`<Link>`** | Link milik Next.js: mengganti halaman tanpa me-reload semuanya |
| **Prefetch** | Memuat halaman di latar belakang sebelum kamu mengekliknya |
| **Client-side transition** | Hanya bagian yang berubah yang ditukar; sisanya tetap |
| **`usePathname`** | Hook yang memberi path saat ini, seperti `/applications` |
| **Search params** | Bagian `?key=value` dari URL |
| **`router.push` / `replace`** | Pergi ke sebuah URL (dengan / tanpa menambah langkah Back) |
| **Breadcrumb** | Jejak "Home › Applications › Detail" |
| **Open redirect** | Celah keamanan: mengirim pengguna ke situs mana pun yang dipilih penyerang |

## 🧠 Ide besarnya

URL adalah **alamat sekaligus bookmark** dari apa yang sedang dilihat pengguna. Kalau "lamaran difilter Interview, halaman 2" hanya ada di `useState`, reload akan menghilangkannya dan tidak ada yang bisa membagikannya. Taruh di URL, dan tampilan itu bisa dibagikan, di-reload, dan dinavigasi dengan tombol Back — gratis. Seperti **link Google Maps**: kirim ke teman, dan dia melihat tempat yang persis sama.

## ❓ Kenapa ini penting

Reload halaman penuh setiap kali klik itu lambat dan membuang apa yang ada di layar. `<Link>` membuat perpindahan halaman terasa instan.

Kesalahan yang umum:

```tsx
<a href="/applications">Applications</a>                    // full reload: layout state lost, slower
<div onClick={() => (window.location.href = "/jobs")}>Jobs</div>   // not a link: no middle-click, no keyboard, no prefetch
const [status, setStatus] = useState("all");                // refresh → filter gone; can't share the filtered view
router.push(`/applications?status=${status}`)               // clicking filters fills history; Back cycles through filters
```

- `<a>` biasa untuk halaman internal me-reload semuanya.
- `div` yang bisa diklik bukan link sungguhan: tanpa keyboard, tanpa "buka di tab baru".
- Filter di `useState` hilang saat reload.
- `push` untuk setiap klik filter memenuhi riwayat Back dengan filter.

## 📖 Langkah demi langkah

### 1. `<Link>`

```tsx
import Link from "next/link";

<Link href="/applications">Applications</Link>
<Link href={`/applications/${application.id}`}>{application.role}</Link>
<Link href={{ pathname: "/applications", query: { status: "offer" } }}>Offers</Link>
```

- Ia menghasilkan `<a href>` sungguhan: keyboard, screen reader, dan "buka di tab baru" semuanya berfungsi.
- Ia **prefetch** halaman saat link muncul di layar, jadi klik terasa instan — seperti pelayan yang menyiapkan menu sebelum kamu duduk.
- Ia hanya menukar bagian yang berubah; layout bersama tetap.
- Pakai `<a>` biasa untuk situs lain dan unduhan file.

### 2. Tandai link saat ini

```tsx
"use client";
import { usePathname } from "next/navigation";

export function NavLinks({ links }: { links: { href: string; label: string }[] }) {
  const pathname = usePathname();
  return (
    <nav aria-label="Main">
      {links.map(({ href, label }) => {
        const active = href === "/" ? pathname === "/" : pathname === href || pathname.startsWith(`${href}/`);
        return (
          <Link key={href} href={href} aria-current={active ? "page" : undefined} className={cn("px-3 py-2", active && "font-semibold text-indigo-600")}>
            {label}
          </Link>
        );
      })}
    </nav>
  );
}
```

- `usePathname()` memberikan path saat ini.
- `aria-current="page"` memberi tahu screen reader "kamu di sini" — seperti titik merah di peta mal.
- Pencocokan harus teliti: `/jobsearch` **tidak boleh** menandai `/jobs`. Itulah kenapa kodenya mengecek `startsWith(href + "/")`.

### 3. Breadcrumb

Pecah path menjadi bagian-bagian, buat link untuk setiap langkah, dan tampilkan yang terakhir sebagai teks biasa dengan `aria-current="page"`, di dalam `<nav aria-label="Breadcrumb"><ol>`. Pakai tabel label kecil untuk bagian seperti id ("12" → "Backend Engineer").

### 4. Filter di URL

```tsx
"use client";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

export function StatusFilter() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();            // read-only URLSearchParams

  function setStatus(value: string) {
    const params = new URLSearchParams(searchParams.toString());
    value ? params.set("status", value) : params.delete("status");
    params.delete("page");                           // new filter → back to page 1
    const query = params.toString();
    router.replace(query ? `${pathname}?${query}` : pathname, { scroll: false });
  }

  return <select value={searchParams.get("status") ?? ""} onChange={(e) => setStatus(e.target.value)}>…</select>;
}
```

- `useSearchParams()` hanya bisa dibaca, jadi buat salinan dengan `new URLSearchParams(...)`.
- Pertahankan param lain (seperti `q`), tapi reset `page` saat filter berubah.
- `replace` untuk filter dan urutan (tanpa langkah Back tambahan). `push` untuk perpindahan halaman sungguhan yang mungkin ingin di-Back pengguna.
- Halaman Server Component membaca nilai yang sama dari `searchParams`-nya dan memuat data yang sudah difilter. URL menghubungkan kontrol di browser dengan data di server.
- Untuk kotak pencarian, tunggu sampai pengguna berhenti mengetik (debounce, Minggu 1).

### 5. Berpindah halaman dari kode

```tsx
const router = useRouter();
router.push(`/applications/${id}`);   // navigate after a successful save
router.back();                         // Cancel button
router.refresh();                      // re-render Server Components with fresh data (keeps client state)
```

Di server (Server Component, Server Action, Route Handler):

```tsx
import { redirect, notFound } from "next/navigation";
if (!session) redirect("/login?next=/applications");
```

- Pindah halaman hanya **setelah** aksinya berhasil. Kalau gagal, tetap di halaman dan tampilkan error.
- `router.refresh()` memuat ulang data server tapi mempertahankan yang sudah diketik di browser.
- `redirect()` seperti resepsionis yang bilang "silakan ke meja login dulu".

### 6. Menunjukkan loading

- `loading.tsx` langsung tampil untuk halaman yang lambat.
- `useLinkStatus()` (di component yang berada di dalam `<Link>`) memberikan `pending`, untuk spinner kecil di jaringan lambat.

### 7. Scroll dan fokus

Next.js scroll ke atas saat halaman berganti. Pastikan setiap halaman punya `<h1>` yang jelas, agar pengguna screen reader tahu halamannya sudah berganti.

## ⚠️ Kesalahan umum

- Mengubah `useSearchParams()` secara langsung (hanya bisa dibaca) — salin ke `new URLSearchParams`.
- Kehilangan param lain saat mengubah satu param.
- **Open redirect**: `redirect(searchParams.next)` dengan URL lengkap yang diberikan penyerang. Hanya izinkan path relatif seperti `/applications`.
- `window.location` untuk halaman internal.
- Data sensitif (email, token) di URL — URL tercatat di log dan dibagikan.
- `router.push` di dalam `div` alih-alih `<Link>` sungguhan.

## 🏆 Praktik terbaik

- [ ] Link internal dengan `next/link`; link eksternal dengan `<a>` dan `rel="noopener noreferrer"` saat `target="_blank"`.
- [ ] Tandai link saat ini dengan `aria-current="page"`; cocokkan halaman bersarang dengan teliti.
- [ ] Taruh state tampilan yang bisa dibagikan di URL; cek di server.
- [ ] `replace` + `scroll: false` untuk filter; reset nomor halaman saat filter berubah.
- [ ] Pindah halaman hanya setelah berhasil.
- [ ] `redirect()` untuk pengecekan login di server, dengan path `next` yang divalidasi.
- [ ] Tambahkan `loading.tsx` ke halaman dinamis.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Dengan ide link Google Maps, jelaskan ke product manager kenapa filter lamaran sebaiknya disimpan di URL — misalnya saat mengirim link yang sudah difilter ke mentor.

## 📐 Rancang

Rancang URL dan navigasi untuk **daftar lamaran** CareerPilot: filter status, pencarian teks, filter perusahaan, urutan, pagination, dan drawer pratinjau yang terbuka di atas list. Tentukan apa yang masuk ke path vs bagian `?`, kapan memakai push vs replace, dan bagaimana perilaku tombol Back.

:::quiz
Tampilkan contoh desainnya

- **List**: `/applications?status=interview&q=backend&company=3&sort=-updated&page=2`
  - Nilai default tidak ditulis di URL (`sort=-updated`, `page=1`).
  - Mengubah `status`, `company`, atau `sort` → `router.replace`, dan reset `page`.
  - `q` (teks pencarian) → `replace` setelah 300 ms tanpa ketikan.
  - Pagination → `push` (orang berharap Back kembali ke halaman 1) — pengecualian yang masuk akal.
- **Halaman detail**: `/applications/12` — halaman penuh yang bisa dibagikan.
- **Drawer pratinjau**: `/applications?…&preview=12` → `push`, jadi Back menutup drawer. List tetap tampil. Membuka link itu secara langsung juga membuka drawer-nya. ("Intercepting routes" di Next.js juga bisa menampilkan `/applications/12` sebagai modal — lebih lanjut.)
- **Server**: halaman list mengecek setiap param (status tidak dikenal → abaikan; page bukan bilangan bulat positif → 1) sebelum memanggil Flask API.
- **Setelah mengubah status** di drawer: tetap di halaman, tampilkan pesan kecil, dan panggil `router.refresh()` agar list dimuat ulang.
:::

### 📝 Checklist self-review

- [ ] State tampilan yang bisa dibagikan ada di URL, default tidak ditulis
- [ ] push vs replace dipilih dengan sengaja
- [ ] Tombol Back berperilaku sesuai harapan pengguna
- [ ] Server mengecek param-nya

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/web/m4/w4/02-navigation" ai="no-ai" title="Link aktif, breadcrumb, dan filter di URL"}
Bangun `NavLinks` dengan pencocokan link saat ini yang benar, `Breadcrumbs` yang dibangun dari path, `StatusFilter` yang mempertahankan param URL lain dan mereset pagination dengan `router.replace`, serta `SaveAndOpen` yang hanya berpindah halaman setelah penyimpanan berhasil. Tes memalsukan `next/navigation` untuk mengendalikan URL.
:::

:::hints
- `new URLSearchParams(searchParams.toString())` membuat salinan yang bisa diubah.
- Link breadcrumb: `"/" + segments.slice(0, index + 1).join("/")`.
- Di `SaveAndOpen`: `try { const { id } = await onSave(); router.push(...) } catch { … }`.
:::

## ✅ Cek cepat

:::quiz
Kapan memakai `router.replace` alih-alih `router.push`?

Saat perubahan tidak boleh menambah langkah Back — biasanya filter, urutan, atau teks pencarian — agar Back kembali ke halaman sebelumnya, bukan melewati setiap filter.
:::

:::quiz
Kenapa `<Link>` lebih baik daripada `div` dengan `onClick` + `router.push`?

`<Link>` adalah link sungguhan (keyboard, screen reader, buka di tab baru, salin link), ia prefetch halamannya, dan tetap berpindah halaman tanpa reload penuh.
:::

## 📚 Lanjut belajar

- Dokumentasi Next.js (tersedia di dalam proyek): Linking and Navigating; referensi `useRouter`, `usePathname`, `useSearchParams`, `useLinkStatus`
- [WAI-ARIA: aria-current](https://www.w3.org/TR/wai-aria-1.2/#aria-current)

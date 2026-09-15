---
title: "🔥 shadcn/ui: Komponen Aksesibel Milikmu Sendiri"
summary: Cara shadcn/ui menyalin komponen aksesibel berbasis Radix ke proyekmu — variant dengan cva, helper cn, tema lewat CSS variable, konfirmasi hapus yang aman, dan merawat kode yang kamu miliki.
sourceHash: dc910ab72a97
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa itu shadcn/ui — dan apa yang bukan: ia menyalin kode ke proyekmu, bukan library komponen dari npm
- `npx shadcn@latest init` / `add`, dan ke mana file-nya disimpan
- **Radix primitive**: aksesibilitas yang sudah tertanam (fokus, keyboard, ARIA)
- Variant dengan **cva** dan helper **`cn()`** (sudah kamu kenal di Week 2)
- Tema dengan CSS variable
- **Konfirmasi hapus** dengan AlertDialog dan status "Menghapus…"
- Memiliki dan memperbarui komponen salinan dengan bertanggung jawab

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **shadcn/ui** | Alat yang menyalin komponen siap pakai dan aksesibel ke dalam kodemu |
| **Radix** | Library komponen tanpa gaya yang mengurus keyboard, fokus, dan ARIA |
| **Headless component** | Hanya perilaku, tanpa tampilan — kamu yang menambahkan gayanya |
| **Primitive** | Balok dasar seperti Dialog, Menu, Tabs |
| **Focus trap** | Menjaga fokus keyboard tetap di dalam dialog selama terbuka |
| **AlertDialog** | Dialog untuk aksi berbahaya; klik di luar tidak menutupnya |
| **`asChild`** | Memberikan gaya komponen ke elemen anaknya (misalnya link asli) |
| **Design token** | Nilai desain (warna, radius) yang disimpan sebagai CSS variable |

## 🧠 Ide besarnya

Kebanyakan library UI itu seperti **menyewa furnitur**: datang sudah jadi, warnanya dipilih dari katalog, tapi kamu tidak boleh memotong kakinya. shadcn/ui seperti **rakitan IKEA plus bahan berkualitas**: kamu dapat potongan yang dirancang dengan baik (dengan "engsel" aksesibel dari Radix) yang dikirim **ke rumahmu sendiri** (proyekmu). Semuanya milikmu — boleh diubah apa saja.

## ❓ Kenapa ini penting

Membuat komponen aksesibel sendiri itu sulit. Dialog popup yang benar butuh: fokus tetap di dalam, fokus kembali saat ditutup, `Escape` untuk menutup, halaman di belakang tidak ikut scroll, judul dan deskripsi yang terhubung, serta diuji dengan screen reader. Library tradisional (MUI, Ant Design) sudah menyelesaikan ini, tapi membawa sistem gaya sendiri yang bentrok dengan Tailwind.

shadcn/ui menggabungkan **perilaku yang aksesibel** (Radix) dengan **gaya Tailwind yang kamu miliki**.

"Modal" buatan tangan biasanya rusak:

```tsx
// ❌ a hand-rolled "modal"
{open && (
  <div className="fixed inset-0 bg-black/50" onClick={() => setOpen(false)}>
    <div className="bg-white p-6">
      <p>Delete this application?</p>
      <div onClick={handleDelete}>Delete</div>          {/* not a button: no keyboard, no role */}
    </div>
  </div>
)}
```

- Pengguna keyboard bisa Tab ke elemen **di belakang** modal.
- Screen reader tidak mengumumkannya; `Escape` tidak berfungsi.
- Fokus hilang setelah modal ditutup.
- Salah klik di latar gelap membatalkan aksi berbahaya di tengah jalan.

## 📖 Langkah demi langkah

### 1. Setup

```bash
npx shadcn@latest init            # detects Next.js + Tailwind v4, writes components.json, lib/utils.ts, theme CSS variables
npx shadcn@latest add button alert-dialog badge form
```

```text
components/
  ui/
    button.tsx          ← copied source, edit freely
    alert-dialog.tsx
    badge.tsx
lib/
  utils.ts              ← cn()
components.json         ← aliases, style, base color, icon library
```

- `init` menyiapkan proyek; `add` menyalin komponen ke `components/ui`.
- Komponennya memakai paket `radix-ui` untuk perilaku dan `lucide-react` untuk ikon.

### 2. `cn()` — menggabungkan class dengan aman

```ts
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

cn("px-4 bg-red-600", isActive && "ring-2", "bg-purple-600");   // → "px-4 ring-2 bg-purple-600"
```

Helper yang sama dengan Week 2 lesson 06: `clsx` menambahkan class berdasarkan kondisi, `tailwind-merge` membuang class yang bentrok sehingga prop `className` bisa **menimpa** gaya bawaan.

### 3. Variant dengan `cva`

```tsx
import { cva, type VariantProps } from "class-variance-authority";

export const badgeVariants = cva("inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium", {
  variants: {
    tone: {
      neutral: "bg-slate-100 text-slate-700",
      info: "bg-blue-100 text-blue-800",
      warning: "bg-amber-100 text-amber-800",
      success: "bg-green-100 text-green-800",
      danger: "bg-red-100 text-red-800",
    },
  },
  defaultVariants: { tone: "neutral" },
});

export function Badge({ tone, className, ...props }: React.ComponentProps<"span"> & VariantProps<typeof badgeVariants>) {
  return <span data-slot="badge" className={cn(badgeVariants({ tone }), className)} {...props} />;
}
```

Lalu hubungkan nilai **bisnis** ke variant **desain** di satu tempat:

```tsx
const STATUS_BADGE = {
  applied: { tone: "info", label: "Applied" },
  interview: { tone: "warning", label: "Interview" },
  offer: { tone: "success", label: "Offer 🎉" },
  rejected: { tone: "danger", label: "Rejected" },
} as const;
```

`Badge` yang generik hanya tahu warna ("tone"). Tabel kecil ini yang bilang "interview → warning". Dengan begitu desainnya tetap bisa dipakai ulang, dan istilah bisnis tetap berada di kode aplikasimu.

### 4. `asChild`

```tsx
<Button asChild variant="outline">
  <Link href="/applications/new">New application</Link>
</Button>
```

`asChild` artinya "jangan buat `<button>` sendiri — pasang gayamu ke anak saya". Hasilnya link asli (`<a>`) yang tampil seperti tombol, tanpa susunan `<button><a/></button>` yang tidak valid. Seperti memakaikan seragam ke karyawan yang sudah ada, bukan membuat orang baru.

### 5. AlertDialog untuk aksi berbahaya

| Komponen | Tertutup saat klik di luar? | Role | Dipakai untuk |
|---|---|---|---|
| `Dialog` | ya | `dialog` | form, detail |
| `AlertDialog` | **tidak** | `alertdialog` | konfirmasi aksi berbahaya atau permanen |

```tsx
export function DeleteApplicationDialog({ role, onConfirm }: Props) {
  const [open, setOpen] = useState(false);
  const [pending, setPending] = useState(false);
  const [failed, setFailed] = useState(false);

  async function handleConfirm(event: React.MouseEvent<HTMLButtonElement>) {
    event.preventDefault();                 // don't auto-close; wait for the result
    setPending(true);
    setFailed(false);
    try {
      await onConfirm();
      setOpen(false);
    } catch {
      setFailed(true);
    } finally {
      setPending(false);
    }
  }

  return (
    <AlertDialog open={open} onOpenChange={(next) => !pending && setOpen(next)}>
      <AlertDialogTrigger asChild><Button variant="destructive">Delete</Button></AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{`Delete "${role}"?`}</AlertDialogTitle>
          <AlertDialogDescription>This removes the application and its notes. This can't be undone.</AlertDialogDescription>
        </AlertDialogHeader>
        {failed && <p role="alert">Couldn't delete. Try again.</p>}
        <AlertDialogFooter>
          <AlertDialogCancel disabled={pending}>Cancel</AlertDialogCancel>
          <AlertDialogAction disabled={pending} onClick={handleConfirm}>{pending ? "Deleting…" : "Delete application"}</AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}
```

- `event.preventDefault()` mencegah dialog langsung tertutup; dialog baru tertutup **setelah** penghapusan berhasil.
- Selama menghapus, `Escape` dan klik di luar diabaikan (`!pending && setOpen(next)`).
- Kalau gagal, pesan error tampil **di dalam** dialog.
- Sisanya diurus Radix: fokus pindah ke **Cancel** (pilihan aman), Tab tetap di dalam, `Escape` menutup, fokus kembali ke tombol Delete, dan judul serta deskripsi terhubung untuk screen reader.

Seperti ATM yang bertanya "Yakin mau transfer?" — ia menunggu jawaban bank dulu sebelum mencetak struk.

### 6. Tema

`init` menambahkan CSS variable (`--background`, `--primary`, `--destructive`, `--radius`…) dan menghubungkannya ke class Tailwind (`bg-primary`, `text-destructive`). Ganti warna brand dengan mengubah variable-nya; tambahkan dark mode dengan class `.dark` — tanpa menyentuh komponennya.

## ⚠️ Kesalahan umum

- Menaruh `<Link>` di dalam `<Button>` alih-alih memakai `asChild`.
- Tidak memakai `cn`, sehingga `className="bg-purple-600"` tidak menimpa `bg-red-600`.
- Langsung menutup dialog konfirmasi, lalu gagal tanpa kabar.
- Memakai `Dialog` untuk "Hapus akun", sehingga klik nyasar di luar membatalkannya.
- Lupa `"use client"` di komponen yang memakai state Radix.
- Menyalin komponen tanpa pernah membacanya — bug-nya juga jadi milikmu.
- Memakai shadcn/ui padahal perusahaan sudah punya paket design system sendiri.

## 🏆 Praktik terbaik

- [ ] Perlakukan `components/ui` sebagai kode **milikmu**: baca, uji perilaku penting, dan review perubahan saat menambahkannya lagi.
- [ ] Kustomisasi lewat variant dan CSS variable sebelum mengubah isi komponen.
- [ ] Simpan pemetaan bisnis (status → tone) di luar komponen `ui/`.
- [ ] Pakai `AlertDialog` untuk aksi berbahaya; biarkan terbuka sampai aksinya selesai; tampilkan error di dalamnya.
- [ ] Pakai `asChild` untuk link yang tampil seperti tombol.
- [ ] Selalu beri dialog judul (boleh disembunyikan secara visual) dan deskripsi.
- [ ] Uji setiap jenis komponen dengan keyboard dan screen reader minimal sekali.
- [ ] Kunci versi `radix-ui`, `cva`, dan `tailwind-merge`; update dengan sengaja.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ide "menyewa furnitur vs rakitan IKEA dengan bahan berkualitas", dan satu kekurangan nyata dari memiliki kode komponen sendiri.

## 📐 Rancang

Rencanakan **design system CareerPilot** kecil di atas shadcn/ui: komponen apa yang ditambahkan dulu untuk papan lamaran, variant apa yang dibutuhkan masing-masing (misalnya `Button`: default/outline/ghost/destructive, dengan beberapa ukuran), komponen khusus aplikasi apa yang membungkusnya (`StatusBadge`, `ApplicationCard`), dan bagaimana mendokumentasikan serta mengujinya.

:::quiz
Lihat contoh rencana

- **Komponen dasar (`components/ui`)**: Button (default, secondary, outline, ghost, destructive × sm/default/icon), Badge (tone), Card, Input, Textarea, Select, Form (React Hook Form), Dialog, AlertDialog, DropdownMenu, Tabs, Tooltip, Skeleton, Sonner/Toast.
- **Komponen aplikasi (`components/careerpilot`)**: `StatusBadge` (status → tone), `ApplicationCard` (Card + StatusBadge + aksi DropdownMenu), `MoveStatusMenu`, `DeleteApplicationDialog`, `SalaryRange`, `EmptyState`.
- **Token**: warna brand dan radius sebagai CSS variable; dark mode dengan `.dark`.
- **Dokumentasi**: story Storybook untuk setiap variant, dengan add-on aksesibilitas, plus `components/README.md` singkat tentang "komponen mana dipakai kapan".
- **Tes**: Vitest + Testing Library untuk perilaku (dialog saat menyimpan/error, navigasi keyboard di menu); screenshot state penting (Storybook atau Playwright); cek axe di CI.
- **Update**: setiap beberapa bulan, bandingkan salinanmu dengan versi shadcn/ui terbaru dan terapkan perubahan lewat pull request yang direview.
:::

### 📝 Checklist review mandiri

- [ ] Komponen dasar tetap generik; logika bisnis ada di pembungkus
- [ ] Aksi berbahaya memakai AlertDialog
- [ ] Aksesibilitas diuji, bukan diasumsikan

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/web/m4/w5/08-shadcn-ui" ai="ai-allowed" title="Variant badge dan konfirmasi hapus"}
Dengan `Button` dan `AlertDialog` gaya shadcn yang sudah disediakan, buat badge `cva` dengan beberapa tone, pemetaan `StatusBadge`, dan `DeleteApplicationDialog` yang tetap terbuka selama menghapus, mengabaikan Escape selama request berjalan, dan menampilkan error di dalam dialog.
:::

:::hints
- `cn(badgeVariants({ tone }), className)` membuat `className` bisa menimpa warna latar dari tone.
- Panggil `event.preventDefault()` di `onClick` tombol aksi supaya Radix tidak menutup dialog.
- Abaikan `onOpenChange(false)` selama pending.
:::

## ✅ Cek cepat

:::quiz
Kenapa shadcn/ui memakai `tailwind-merge` di dalam `cn()`?

Class Tailwind tidak saling menimpa berdasarkan urutan di atribut `class` — urutan di file CSS yang menentukan. `tailwind-merge` membuang class yang bentrok (`bg-red-600` vs `bg-purple-600`) supaya class yang kamu maksud yang menang.
:::

:::quiz
shadcn/ui merilis perbaikan untuk komponen button. Bagaimana cara mendapatkannya?

Tidak otomatis — kodenya milikmu. Jalankan `add` lagi (dan review perubahannya sebelum menimpa kustomisasimu), atau terapkan perbaikannya secara manual.
:::

## 📚 Lanjut belajar

- [Dokumentasi shadcn/ui](https://ui.shadcn.com/docs) — Installation (Next.js), Theming, AlertDialog, Form
- [Radix Primitives: Alert Dialog](https://www.radix-ui.com/primitives/docs/components/alert-dialog)
- [Dokumentasi cva](https://cva.style/docs)

---
title: "TypeScript + Tailwind: Pola Integrasi"
summary: Gabungkan type dan class Tailwind menjadi balok penyusun yang bisa dipakai ulang — helper cn(), tabel variant ber-type, class-variance-authority (CVA), menimpa class dengan aman, dan tempat menyimpan file-file ini.
sourceHash: 8a9119e51c14
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Menambahkan class hanya saat sebuah kondisi benar (`clsx`)
- Membuat class **terakhir** yang menang saat dua class bentrok (`tailwind-merge`)
- Helper `cn()` yang menggabungkan keduanya
- **Variant** ber-type seperti `variant: "primary" | "danger"`
- CVA, library yang dipakai shadcn/ui untuk ide yang sama
- Di mana menaruh token, helper, dan component

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Variant** | Pilihan gaya bernama dari sebuah component: primary, danger, small… |
| **`clsx`** | Helper yang menggabungkan nama class dan melewati yang bernilai false |
| **`tailwind-merge`** | Helper yang membuang class Tailwind yang bentrok; yang terakhir menang |
| **`cn()`** | Helper kecilmu = `clsx` + `tailwind-merge` |
| **Override** | Pemanggil mengganti style default (`px-8` menggantikan `px-4`) |
| **Design system** | Kumpulan component dan style bersama yang dipakai seluruh tim |

## 🧠 Ide besarnya

Design system itu seperti **menu restoran, bukan prasmanan**. Daripada setiap developer mencampur class sesukanya, component menawarkan menu kecil — `variant: "primary" | "danger"`, `size: "sm" | "md"` — dan TypeScript menolak pesanan yang tidak ada di menu. Tailwind menyediakan bahan-bahannya; TypeScript menjaga menunya.

## ❓ Kenapa ini penting

Setelah beberapa minggu memakai Tailwind, setiap proyek menanyakan hal yang sama:
- "Bagaimana menambahkan class hanya saat tombolnya disabled?"
- "Kenapa `px-8`-ku tidak menggantikan `px-4` milik component?"
- "Bagaimana mencegah orang memakai `size='xl'` yang tidak ada?"

Cara sederhana gagal:

```ts
const classes = "px-4 py-2 bg-indigo-600 " + (danger ? "bg-red-600 " : "") + props.className;
// "px-4 py-2 bg-indigo-600 bg-red-600 px-8" — which bg and px win? Depends on CSS order, not class order!
```

`bg-indigo-600` dan `bg-red-600` sama-sama ada di daftar class. Mana yang menang bergantung pada urutannya **di dalam file CSS yang dihasilkan**, bukan urutan di string-mu (ingat "rule mana yang menang" dari Minggu 1). Jadi tombol danger bisa tetap berwarna indigo. Dan salah ketik seperti `variant="dagner"` lolos diam-diam.

## 📖 Langkah demi langkah

### 1. `clsx`: tambahkan class berdasarkan kondisi

```ts
clsx("px-4", isActive && "bg-indigo-50", { "opacity-50": disabled }, ["mt-2", null])
// "px-4 bg-indigo-50 opacity-50 mt-2" (falsy values dropped)
```

Seperti mengisi tas dengan checklist: "payung — hanya kalau hujan". Item yang false dilewati.

### 2. `tailwind-merge`: yang terakhir menang

```ts
twMerge("px-4 py-2 bg-indigo-600", "px-8 bg-red-600")
// "py-2 px-8 bg-red-600"
```

Ia tahu class Tailwind mana yang melakukan tugas yang sama (padding, warna background…) dan hanya menyimpan yang **terakhir** — seperti memperbarui alamat pengiriman: alamat terbaru menggantikan yang lama.

### 3. `cn()` = keduanya sekaligus

```ts
import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}
```

Helper kecil ini ada di hampir setiap proyek React + Tailwind modern.

### 4. Tabel variant ber-type

```ts
export type ButtonVariant = "primary" | "secondary" | "danger" | "ghost";
export type ButtonSize = "sm" | "md" | "lg";

const VARIANTS = {
  primary: "bg-indigo-600 text-white hover:bg-indigo-500",
  secondary: "bg-white text-slate-900 ring-1 ring-slate-300 hover:bg-slate-50",
  danger: "bg-red-600 text-white hover:bg-red-500",
  ghost: "bg-transparent text-slate-700 hover:bg-slate-100",
} satisfies Record<ButtonVariant, string>;

const SIZES = { sm: "px-2.5 py-1.5 text-sm", md: "px-4 py-2 text-sm", lg: "px-5 py-3 text-base" } satisfies Record<ButtonSize, string>;

export function buttonClasses({ variant = "primary", size = "md", fullWidth = false, className }: {
  variant?: ButtonVariant; size?: ButtonSize; fullWidth?: boolean; className?: string;
} = {}) {
  return cn(BASE, VARIANTS[variant], SIZES[size], fullWidth && "w-full", className);
}
```

- Tabelnya berisi nama class **lengkap**, jadi Tailwind bisa menemukannya.
- `satisfies` mengecek setiap variant punya style. Tambahkan `"warning"` ke type tapi lupa style-nya → error.
- `className` ditaruh **terakhir**, jadi class dari pemanggil yang menang (`buttonClasses({ className: "px-8" })`).

### 5. CVA: ide yang sama dalam bentuk library

```ts
import { cva, type VariantProps } from "class-variance-authority";

export const button = cva("inline-flex items-center justify-center rounded-lg font-semibold", {
  variants: {
    variant: { primary: "bg-indigo-600 text-white", danger: "bg-red-600 text-white" },
    size: { sm: "px-2.5 py-1.5 text-sm", md: "px-4 py-2 text-sm" },
  },
  compoundVariants: [{ variant: "danger", size: "sm", class: "font-bold" }],
  defaultVariants: { variant: "primary", size: "md" },
});

export type ButtonProps = VariantProps<typeof button>;   // { variant?: "primary" | "danger" | null; size?: … }
// usage: cn(button({ variant: "danger" }), className)
```

- `variants` — menunya.
- `compoundVariants` — style tambahan untuk kombinasi tertentu ("danger **dan** small").
- `defaultVariants` — yang kamu dapat kalau tidak memilih.
- `VariantProps` — membangun type props dari menu, jadi tidak perlu ditulis dua kali.

shadcn/ui (Minggu 5) membangun component-nya persis seperti ini. Karena kamu sudah menulis versi manualnya lebih dulu, CVA tidak akan terasa seperti sihir.

### 6. Tempat file-file

```text
src/
├── app.css                     ← @import "tailwindcss" + @theme tokens
├── lib/utils.ts                ← cn()
└── components/ui/
    ├── button.tsx              ← variants + component
    ├── badge.tsx               ← STATUS_BADGE satisfies Record<Status, string>
    └── card.tsx
```

Type `Status` berasal dari file model API-mu. Kalau backend menambahkan status, tabel badge gagal di-compile sampai kamu memberinya style.

## ⚠️ Kesalahan umum

- Menyambung string dan berharap class terakhir menang — tanpa `twMerge`, urutan di file CSS yang menentukan.
- Lupa `satisfies`, sehingga variant baru diam-diam tampil tanpa style.
- Menaruh `className` di awal, sehingga default component mengalahkan pemanggil.
- Menyusun nama class dari string (`` `bg-${color}` ``) yang tidak pernah dibuat Tailwind.
- Membuat sistem variant untuk layout sekali pakai — cukup tulis class-nya.

## 🏆 Praktik terbaik

- [ ] Satu helper `cn()`, dipakai di mana-mana.
- [ ] Variant berupa union ber-type dengan tabel lengkap (`satisfies Record<…>`).
- [ ] Taruh `className` **terakhir** agar class pemanggil yang menang.
- [ ] Bangun type props dari variant (`VariantProps`), bukan menulisnya dua kali.
- [ ] Taruh style fokus dan disabled di class dasar, agar setiap variant mendapatkannya.
- [ ] Hubungkan union domain (seperti `Status`) ke tabel style, agar nilai baru tidak terlupa.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan kenapa `"px-4 px-8"` tidak selalu menghasilkan `px-8` tanpa `tailwind-merge`. Pakai yang kamu pelajari tentang "rule mana yang menang" di Minggu 1.

## 📐 Rancang

Rancang API variant ber-type untuk component **`Alert`** CareerPilot: tone success, info, warning, dan error; ukuran `default` atau `compact`; opsional bisa ditutup; ikon untuk setiap tone. Sertakan type, tabel, dan catatan tentang role untuk screen reader.

:::quiz
Tampilkan contoh desainnya

```ts
export type AlertTone = "success" | "info" | "warning" | "error";
export type AlertDensity = "default" | "compact";

const TONE = {
  success: "border-green-200 bg-green-50 text-green-900",
  info: "border-blue-200 bg-blue-50 text-blue-900",
  warning: "border-amber-200 bg-amber-50 text-amber-900",
  error: "border-red-200 bg-red-50 text-red-900",
} satisfies Record<AlertTone, string>;

const DENSITY = { default: "gap-3 p-4 text-sm", compact: "gap-2 px-3 py-2 text-xs" } satisfies Record<AlertDensity, string>;

const ICON = { success: CheckCircleIcon, info: InfoIcon, warning: TriangleIcon, error: XCircleIcon } satisfies Record<AlertTone, IconComponent>;

// errors interrupt (assertive); others are polite status messages
const ROLE = { success: "status", info: "status", warning: "status", error: "alert" } as const satisfies Record<AlertTone, "status" | "alert">;

export interface AlertProps {
  tone?: AlertTone;
  density?: AlertDensity;
  title: string;
  children?: React.ReactNode;
  onDismiss?: () => void;          // dismissible iff provided — no separate boolean that can disagree
  className?: string;
}

export const alertClasses = ({ tone = "info", density = "default", className }: Pick<AlertProps, "tone" | "density" | "className">) =>
  cn("flex items-start rounded-lg border", TONE[tone], DENSITY[density], className);
```

- Error memakai `role="alert"` (langsung dibacakan); yang lain memakai `role="status"` (dibacakan dengan sopan).
- Ikon memakai `aria-hidden`; judul yang membawa makna, jadi warna bukan satu-satunya penanda.
- Tombol tutup punya nama yang jelas ("Dismiss error: Couldn't save").
- Kalau `onDismiss` diberikan, alert bisa ditutup. Tidak ada flag `dismissible` terpisah yang bisa bertentangan.
:::

### 📝 Checklist self-review

- [ ] Union ber-type dengan tabel yang lengkap
- [ ] Pemanggil bisa menimpa dengan `cn(…, className)`
- [ ] Role dan penanda selain warna sudah dipertimbangkan

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/web/m4/w2/06-integration-patterns" ai="no-ai" title="Variant button dan badge ber-type"}
Tulis `cn()` dengan clsx + tailwind-merge, tabel variant dan ukuran ber-type yang lengkap dengan `satisfies`, serta helper `buttonClasses` / `badgeClasses` di mana class pemanggil menimpa default. Tes mengecek output yang persis, penanganan bentrok, dan bahwa variant yang tidak dikenal tidak bisa di-compile.
:::

:::hints
- `twMerge(clsx(inputs))` — oper array-nya ke clsx.
- Urutan di `buttonClasses`: base, variant, size, `fullWidth && "w-full"`, `className`.
- `satisfies Record<ButtonVariant, string>` ditaruh setelah object-nya.
:::

## ✅ Cek cepat

:::quiz
Apa yang dilakukan `tailwind-merge` yang tidak dilakukan `clsx`?

Membuang class Tailwind yang bentrok sehingga yang terakhir menang (`px-4 px-8` → `px-8`). `clsx` hanya menggabungkan class dan melewati yang false.
:::

:::quiz
Kenapa tabel variant harus berisi nama class lengkap?

Tailwind hanya membuat CSS untuk nama class yang ditulis lengkap di file-filemu.
:::

## 📚 Lanjut belajar

- [tailwind-merge docs](https://github.com/dcastil/tailwind-merge)
- [class-variance-authority docs](https://cva.style/docs)
- [shadcn/ui: Installation (see the cn() helper)](https://ui.shadcn.com/docs/installation)

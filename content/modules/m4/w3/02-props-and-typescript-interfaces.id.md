---
title: "Props & Interface TypeScript"
summary: Rancang cara component dipakai — props ber-type, nilai default, children dan slot, menerima atribut HTML biasa, callback props, dan aturan sederhana agar component mudah dipakai.
sourceHash: e7f5cbcf662e
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Memberi type pada props, props opsional, dan nilai default
- `children` dan "slot" untuk konten yang fleksibel
- Membuat `Button`-mu menerima semua atribut `<button>` biasa
- Callback props seperti `onToggle`
- `useId` untuk menghubungkan label dan input
- Aturan props yang mudah dipakai dan sulit disalahgunakan

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Props** | Input yang diterima component dari parent-nya |
| **Default value** | Nilai yang dipakai kalau parent tidak mengirim sebuah prop |
| **`ReactNode`** | Type untuk "apa pun yang bisa ditampilkan React": teks, elemen, list, `null` |
| **Slot** | Prop yang menerima konten, seperti `actions={<Button />}` |
| **Rest / spread (`...rest`)** | Kumpulkan props sisanya lalu teruskan |
| **Callback prop** | Prop berupa function yang dipanggil child: `onToggle` |
| **`useId`** | Hook React yang membuat id unik untuk label dan input |

## 🧠 Ide besarnya

Props adalah **kontrak** sebuah component, seperti menu dan kertas pesanan di kedai kopi: daftar apa yang bisa kamu pesan (ukuran, tingkat gula) dan menolak pesanan aneh ("extra large tapi small"). TypeScript membuat editor mengecek kontrak ini setiap kali ada yang memakai component-nya.

## ❓ Kenapa ini penting

Component dipakai banyak orang di banyak tempat. Tanpa props ber-type, kesalahan baru ketahuan di browser:

```tsx
function Button(props: any) {
  return <button className={props.big ? "text-lg" : ""} onClick={props.click}>{props.text}</button>;
}
<Button text="Save" onClick={save} />         // onClick ignored (prop is called click) — silent bug
<Button text="Delete" big small danger />     // contradictory booleans
<Button text="Submit" type="submit" />        // type isn't forwarded → the form never submits
```

- `onClick` diam-diam diabaikan (nama prop-nya `click`).
- `big small danger` bersamaan tidak masuk akal, tapi diizinkan.
- `type="submit"` dibuang, jadi form tidak pernah ter-submit.

Dengan props ber-type, autocomplete menampilkan pilihannya dan kesalahan ini jadi garis merah.

## 📖 Langkah demi langkah

### 1. Props ber-type dan default

```tsx
interface StatusBadgeProps {
  status: Status;                    // required
  size?: "sm" | "md";                // optional
}

export function StatusBadge({ status, size = "md" }: StatusBadgeProps) {
  return <span data-status={status} className={size === "sm" ? "text-xs" : "text-sm"}>{STATUS_LABELS[status]}</span>;
}
```

- `status` wajib; `size?` opsional.
- `size = "md"` memberi nilai default tepat di tempat props dibongkar.

### 2. `children` dan slot

```tsx
interface CardProps {
  title: string;
  actions?: React.ReactNode;         // a "slot": any renderable content
  children: React.ReactNode;
}

export function Card({ title, actions, children }: CardProps) {
  const titleId = useId();           // unique, stable, SSR-safe id
  return (
    <section aria-labelledby={titleId}>
      <header className="flex justify-between">
        <h2 id={titleId}>{title}</h2>
        {actions}
      </header>
      {children}
    </section>
  );
}

<Card title="Notes" actions={<Button>Add note</Button>}>…</Card>
```

- **Slot** adalah tempat bernama untuk konten, seperti tempat foto di template sertifikat.
- `useId()` membuat id yang unik walaupun kartu muncul 10 kali di satu halaman. Di sini id itu menghubungkan section dengan heading-nya untuk screen reader.

### 3. Menerima atribut HTML biasa

`Button`-mu sebaiknya bekerja seperti `<button>` asli, plus tambahanmu — seperti **casing HP**: HP-nya tetap punya semua tombol, casing hanya menambah perlindungan dan gaya.

```tsx
import type { ComponentPropsWithoutRef } from "react";

interface ButtonProps extends ComponentPropsWithoutRef<"button"> {
  variant?: "primary" | "secondary" | "danger";
  loading?: boolean;
}

export function Button({ variant = "primary", loading = false, type = "button", disabled, className, children, ...rest }: ButtonProps) {
  return (
    <button
      {...rest}                                  // onClick, aria-*, data-*, form, name… all work
      type={type}                                // safe default: not "submit"
      disabled={disabled || loading}
      aria-busy={loading || undefined}
      className={cn(buttonClasses({ variant }), className)}
    >
      {loading ? "Loading…" : children}
    </button>
  );
}
```

- `ComponentPropsWithoutRef<"button">` = "semua props yang diterima button biasa".
- `...rest` mengumpulkan semua yang tidak kamu bongkar (onClick, aria-label…) dan meneruskannya ke button asli.
- `{...rest}` ditaruh **duluan**, baru props yang kamu kendalikan, agar pemanggil tidak merusaknya tanpa sengaja.
- `type = "button"` sebagai default, karena button di dalam form akan men-submit form kalau tidak diberi tahu sebaliknya.

### 4. Callback props

```tsx
interface SaveButtonProps {
  saved: boolean;
  onToggle: () => void;              // "on" + event, called by the child
  jobTitle: string;
}
```

Parent memberikan function; child memanggilnya saat sesuatu terjadi — seperti memberi nomor HP ke pelayan: "telepon aku kalau mejanya sudah siap". Kebiasaan penamaan: props bernama `onSomething`, function di parent bernama `handleSomething`. Untuk mengirim data balik, pakai argumen: `onSelect: (id: number) => void`.

### 5. Aturan props yang baik

| Daripada | Lebih baik | Kenapa |
|---|---|---|
| boolean `primary secondary danger` | `variant: "primary" \| "secondary" \| "danger"` | kombinasi aneh jadi mustahil |
| `titleText`, `titleColor`, `titleSize` | satu slot `title: ReactNode` | props lebih sedikit, lebih fleksibel |
| 15 props opsional | component kecil yang dipakai bersama | lebih mudah dibaca |
| `data={job}` padahal hanya dua field yang dipakai | `title`, `company` | lebih jelas, lebih mudah dipakai ulang |
| nama campur aduk seperti `isOpen` + `setIsOpen` | `open` + `onOpenChange` | gaya yang sama dengan library populer |

### 6. `ref` adalah prop biasa

**Ref** memberi akses langsung ke elemen DOM asli (misalnya untuk memfokuskan input). Di React 19 kamu mengirimnya seperti prop lain:

```tsx
function TextField({ label, ref, ...props }: { label: string; ref?: React.Ref<HTMLInputElement> } & ComponentPropsWithoutRef<"input">) {
  const id = useId();
  return (
    <>
      <label htmlFor={id}>{label}</label>
      <input id={id} ref={ref} {...props} />
    </>
  );
}
```

### 7. Props dari Server ke Client harus berupa data sederhana

Saat Server Component memakai Client Component, props-nya dikirim lewat jaringan — seperti mengirim paket lewat kurir. String, angka, boolean, object dan array biasa bisa dikemas. **Function tidak bisa** dikirim (kecuali Server Action — Minggu 5). Jadi callback seperti `onToggle` dibuat di dalam kode client.

## ⚠️ Kesalahan umum

- `props: any` atau props tanpa type.
- Tidak meneruskan `className` dan `aria-*`, sehingga orang lain tidak bisa men-styling atau memberi label pada component.
- Button di dalam form tanpa `type="button"` yang men-submit tanpa sengaja.
- Id yang ditulis langsung di component yang bisa dipakai ulang, sehingga dua salinan di satu halaman punya id yang sama.
- Menambah prop baru untuk setiap permintaan desain alih-alih menyusun component yang lebih kecil.

## 🏆 Praktik terbaik

- [ ] Beri type pada props setiap component; export type props untuk component yang dipakai ulang.
- [ ] Taruh default di tempat props dibongkar; button default-nya `type="button"`.
- [ ] Untuk pembungkus elemen HTML, extend `ComponentPropsWithoutRef<"element">` dan teruskan `...rest`.
- [ ] Pakai union untuk variant, bukan banyak boolean.
- [ ] Beri nama callback `onX`; kirim hanya data yang dibutuhkan.
- [ ] Pakai `useId` untuk id label dan deskripsi.
- [ ] Jaga props tetap data sederhana saat melintas dari Server ke Client Component.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Dengan ide kertas pesanan kedai kopi, jelaskan kenapa `<Button primary danger small large />` adalah desain yang lebih buruk daripada `<Button variant="danger" size="sm" />`.

## 📐 Rancang

Rancang props untuk **`TextField`** CareerPilot yang dipakai di semua form: label, teks petunjuk, pesan error, penanda wajib, prefix opsional (seperti "Rp"), dan tetap menerima semua atribut input biasa (type, name, autoComplete, onChange…). Tulis interface-nya dan jelaskan atribut aksesibilitasnya.

:::quiz
Tampilkan contoh desainnya

```tsx
interface TextFieldProps extends Omit<ComponentPropsWithoutRef<"input">, "id" | "prefix"> {
  label: string;
  hint?: string;
  error?: string;              // presence = invalid
  prefix?: React.ReactNode;     // e.g. "Rp"
  ref?: React.Ref<HTMLInputElement>;
}

export function TextField({ label, hint, error, prefix, required, ref, className, ...inputProps }: TextFieldProps) {
  const id = useId();
  const hintId = hint ? `${id}-hint` : undefined;
  const errorId = error ? `${id}-error` : undefined;
  return (
    <div className={className}>
      <label htmlFor={id}>
        {label} {required && <span aria-hidden="true">*</span>}
      </label>
      {hint && <p id={hintId}>{hint}</p>}
      <div className="flex">
        {prefix && <span aria-hidden="true">{prefix}</span>}
        <input
          {...inputProps}
          id={id}
          ref={ref}
          required={required}
          aria-invalid={error ? true : undefined}
          aria-describedby={[hintId, errorId].filter(Boolean).join(" ") || undefined}
        />
      </div>
      {error && <p id={errorId}>{error}</p>}
    </div>
  );
}
```

- Props input biasa langsung diteruskan (`name`, `type`, `autoComplete`, `onChange`, `value`).
- `id` dibuat dengan `useId` (dan dihapus dari props), jadi label selalu terhubung, walaupun ada banyak field.
- `aria-describedby` menghubungkan petunjuk dan error ke input; `aria-invalid` menandai keadaan error.
- "Rp" yang terlihat diberi `aria-hidden`, jadi tulis juga mata uangnya di label ("Gaji maksimum (Rp)").
:::

### 📝 Checklist self-review

- [ ] Props input biasa tetap berfungsi
- [ ] Label, petunjuk, dan error terhubung dengan id
- [ ] Keadaan error tersedia untuk screen reader

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/web/m4/w3/02-props-typescript" ai="no-ai" title="UI kit kecil ber-type"}
Bangun `Button` (menerima props button biasa, default `type` yang aman, state loading), `Avatar` (gambar atau inisial), `StatusBadge`, dan `Card` berlabel dengan actions opsional memakai `useId`. Tes mengecek perilaku dan penerusan props; tes type membuat variant, status yang tidak dikenal, dan children yang hilang gagal di-compile.
:::

:::hints
- Bongkar yang kamu kendalikan dan kumpulkan sisanya: `({ variant = "primary", loading = false, type = "button", disabled, children, ...rest })`.
- `aria-busy={loading || undefined}` menghilangkan atribut saat tidak loading.
- Inisial: `name.trim().split(/\s+/).slice(0, 2).map((w) => w[0]?.toUpperCase() ?? "").join("")`.
:::

## ✅ Cek cepat

:::quiz
Kenapa extend `ComponentPropsWithoutRef<"button">` untuk component Button?

Agar menerima semua props button biasa (onClick, aria-*, form, name…) dengan type yang benar, dan kamu bisa meneruskannya ke `<button>` asli.
:::

:::quiz
Kenapa Server Component tidak bisa mengirim function `onClick` ke Client Component?

Props yang dikirim dari server ke browser harus berupa data sederhana. Function biasa tidak bisa dikirim lewat jaringan.
:::

## 📚 Lanjut belajar

- [React docs: Passing Props to a Component](https://react.dev/learn/passing-props-to-a-component)
- [React docs: useId](https://react.dev/reference/react/useId)
- [React TypeScript Cheatsheet](https://react-typescript-cheatsheet.netlify.app/)

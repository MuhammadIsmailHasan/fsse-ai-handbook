---
title: "Controlled Input & Form"
summary: Bangun form yang bisa dikelola React — controlled input untuk semua jenis, satu object state per form, validasi yang mudah ditemukan pengguna, mengubah teks input menjadi data bersih, ref untuk fokus, dan kapan uncontrolled input lebih baik.
sourceHash: 340a9af5b8a7
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Controlled vs uncontrolled input
- Mengendalikan text, number, select, checkbox, radio, dan textarea
- Satu object state untuk seluruh form
- Mengubah teks form menjadi data bersih untuk API-mu (angka, `null`)
- Validasi dengan pesan error yang aksesibel
- `useRef` untuk memindahkan fokus
- Submit dengan aman (tanpa kiriman ganda)

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Controlled input** | Input yang nilainya berasal dari state React |
| **Uncontrolled input** | Input yang menyimpan nilainya sendiri di browser; kamu membacanya saat submit |
| **`onChange`** | Event yang terjadi setiap ada perubahan (setiap tekan tombol) |
| **Payload** | Data bersih yang kamu kirim ke API |
| **Validation** | Mengecek nilainya benar sebelum dikirim |
| **Ref (`useRef`)** | Kotak yang menyimpan sesuatu (seperti elemen DOM) tanpa menggambar ulang |
| **`FormData`** | Object browser yang membaca semua nilai form sekaligus |

## 🧠 Ide besarnya

Controlled input itu seperti **etalase toko yang hanya ditata oleh pemilik toko**: yang terlihat di kotak selalu persis sama dengan isi state React, dan setiap tekan tombol melewati kodemu dulu. Karena kebenarannya ada di satu tempat, validasi, format, dan "tampilkan field ini hanya kalau…" jadi sederhana.

## ❓ Kenapa ini penting

Form adalah tempat pengguna memberikan data ke API-mu. Kamu sering butuh penghitung karakter live, field yang muncul tergantung field lain, pengecekan sebelum memanggil Flask, dan data yang bersih dan ber-type.

Masalah umum kalau form dibuat sembarangan:

```tsx
<input type="number" onChange={(e) => setSalary(e.target.value)} />   // salary is "9000000" (a string!)
<input value={role} />                                                 // read-only: no onChange → can't type
<input value={maybeUndefined} onChange={…} />                          // "changing an uncontrolled input to be controlled" warning
```

- Bahkan input number memberimu **teks**.
- `value` tanpa `onChange` membuat input yang tidak bisa diketik.
- Memulai dengan `undefined` memicu peringatan React.

Dan mengirim `{ salary_min: "", salary_max: "9000000" }` membuat Flask API-mu mengembalikan 422 — atau menyimpan data yang salah.

## 📖 Langkah demi langkah

### 1. Controlled input

```tsx
const [role, setRole] = useState("");
<input id="role" value={role} onChange={(e) => setRole(e.target.value)} />
```

Siklusnya: kamu mengetik → `onChange` → `setRole` → React menggambar ulang → kotak menampilkan `role` yang baru.

| Input | Atur nilainya dengan | Baca nilai barunya dari |
|---|---|---|
| text, email, search, textarea | `value={string}` | `e.target.value` |
| number | `value={string}` (simpan sebagai teks saat mengetik) | `e.target.value` → ubah saat submit |
| select | `value={string}` pada `<select>` | `e.target.value` |
| checkbox | `checked={boolean}` | `e.target.checked` |
| grup radio | `checked={value === option}` | `e.target.value` |

Mulai dengan `""` atau `false`, jangan pernah `undefined`.

### 2. Satu object state untuk form

```tsx
type Values = { companyId: string; role: string; salaryMin: string; salaryMax: string; remote: boolean; notes: string };
const EMPTY: Values = { companyId: "", role: "", salaryMin: "", salaryMax: "", remote: false, notes: "" };

const [values, setValues] = useState<Values>(EMPTY);
const set = <K extends keyof Values>(key: K, value: Values[K]) => setValues((prev) => ({ ...prev, [key]: value }));

<input value={values.role} onChange={(e) => set("role", e.target.value)} />
<input type="checkbox" checked={values.remote} onChange={(e) => set("remote", e.target.checked)} />
```

Seperti satu **formulir pendaftaran** yang berisi semua field, bukan catatan-catatan lepas. Helper kecil `set` memakai generic (Minggu 2), jadi `set("remote", "yes")` menjadi error type.

### 3. Dari nilai form ke data bersih

Simpan dua bentuk terpisah — seperti **draf** yang masih kamu tulis dan **surat final** yang kamu kirim:
- **Nilai form**: teks, persis seperti yang diketik.
- **Payload**: data yang sudah dibersihkan dengan angka sungguhan dan `null`.

```tsx
const toNumber = (value: string) => (value.trim() === "" ? null : Number(value));

const payload: ApplicationPayload = {
  companyId: Number(values.companyId),
  role: values.role.trim(),
  salaryMin: toNumber(values.salaryMin),
  salaryMax: toNumber(values.salaryMax),
  remote: values.remote,
  notes: values.notes,
};
```

`toNumber` mengubah field kosong menjadi `null`, bukan `0` (`Number("")` bernilai `0`!).

### 4. Validasi dengan error yang aksesibel

```tsx
function validate(values: Values): Partial<Record<"company" | "role" | "salaryMax", string>> {
  const errors: Partial<Record<…>> = {};
  if (values.companyId === "") errors.company = "Choose a company";
  if (values.role.trim() === "") errors.role = "Role is required";
  const min = toNumber(values.salaryMin), max = toNumber(values.salaryMax);
  if (min !== null && max !== null && min > max) errors.salaryMax = "Maximum must be at least the minimum";
  return errors;
}
```

```tsx
<input
  id="role"
  aria-invalid={errors.role ? true : undefined}
  aria-describedby={errors.role ? "role-error" : undefined}
  …
/>
{errors.role && <p id="role-error">{errors.role}</p>}
```

- Cek **saat pengguna men-submit** dulu. Jangan tampilkan error saat mereka baru mengetik huruf pertama.
- Setelah error ditampilkan, kamu bisa mengecek ulang field itu selagi mereka memperbaikinya.
- Pengecekan di frontend untuk **pengalaman yang nyaman**. Pengecekan di Flask API untuk **keamanan**. Pertahankan keduanya — seperti petugas yang membantumu mengisi formulir, dan teller bank yang mengeceknya lagi.

### 5. Ref dan fokus

```tsx
const roleRef = useRef<HTMLInputElement>(null);
<input ref={roleRef} … />
roleRef.current?.focus();       // after validation fails
```

Ref itu seperti **pembatas buku** ke sebuah elemen asli: kamu bisa melompat ke sana (memfokuskannya) tanpa menggambar ulang halaman. Jangan baca atau ubah `ref.current` saat render — hanya di event handler atau effect.

### 6. Submit

```tsx
async function handleSubmit(event: FormEvent<HTMLFormElement>) {
  event.preventDefault();
  const found = validate(values);
  setErrors(found);
  if (Object.keys(found).length > 0) return focusFirstError(found);
  setSubmitting(true);
  try {
    await onSubmit(toPayload(values));
    setValues(EMPTY);
  } catch (error) {
    setServerError(messageFor(error));    // map API 422 field errors back to fields (Week 5)
  } finally {
    setSubmitting(false);
  }
}

<button type="submit" disabled={submitting}>{submitting ? "Saving…" : "Save application"}</button>
```

- Nonaktifkan tombol selama menyimpan, agar orang tidak men-submit dua kali (seperti menekan "Bayar" dua kali).
- Kosongkan form hanya setelah **berhasil**. Kalau API gagal, pertahankan yang sudah diketik pengguna.
- Tambahkan `noValidate` ke `<form>` kalau kamu menampilkan pesanmu sendiri, tapi tetap pakai `type="email"`, `required`, dan `min` untuk keyboard ponsel.

### 7. Uncontrolled input (kadang lebih sederhana)

```tsx
<form onSubmit={(e) => { e.preventDefault(); const data = new FormData(e.currentTarget); … }}>
  <input name="role" defaultValue="" />
</form>
```

Browser menyimpan nilainya, dan kamu membaca semuanya sekaligus saat submit dengan `FormData`. Cocok untuk form sederhana tanpa perilaku live. **Form action** di React 19 dibangun di atas ini — Minggu 5 membahasnya bersama React Hook Form + Zod.

## ⚠️ Kesalahan umum

- `value` tanpa `onChange` (tidak bisa mengetik).
- Membaca `"on"` dari checkbox alih-alih memakai `checked`.
- `Number("")` → `0`, diam-diam mengubah gaji kosong menjadi nol.
- Mengubah input number di setiap tekan tombol (nilai kosong dan setengah jadi rusak) — ubah saat submit.
- Mengosongkan form saat API mengembalikan error.
- Tanpa label, atau error yang tidak terhubung ke field-nya.

## 🏆 Praktik terbaik

- [ ] Setiap input punya label; error memakai `aria-describedby` + `aria-invalid`; fokus ke error pertama.
- [ ] Mulai nilai controlled dengan `""` / `false`, jangan pernah `undefined`.
- [ ] Pisahkan nilai form (teks) dari payload; trim dan ubah saat submit.
- [ ] Validasi saat submit dulu; validasi di server tetap pengecekan terakhir.
- [ ] Nonaktifkan submit dan tampilkan progres selama menyimpan.
- [ ] Reset setelah berhasil; pertahankan nilai setelah gagal.
- [ ] Pakai `type` input dan `autoComplete` yang tepat.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Dengan ide petugas formulir dan teller bank, jelaskan ke rekan tim backend kenapa frontend mengecek rentang gaji padahal Flask API sudah melakukannya — dan kenapa API tetap harus mengeceknya.

## 📐 Rancang

Rancang form **"Tambah catatan dengan pengingat"**: teks catatan (wajib, maksimal 1000 karakter), toggle "ingatkan aku" yang memunculkan field tanggal-waktu (wajib saat toggle aktif, harus di masa depan), dan pilihan prioritas (low / normal / high, default normal). Jelaskan type nilai form, type payload, pengecekannya, dan atribut aksesibilitasnya.

:::quiz
Tampilkan contoh desainnya

```ts
type NoteValues = { text: string; remind: boolean; remindAt: string; priority: "low" | "normal" | "high" };  // remindAt: "2026-09-20T09:00" from datetime-local
type NotePayload = { text: string; priority: NoteValues["priority"]; remindAt: string | null };                // ISO string in UTC or null

function validate(v: NoteValues, now: Date) {
  const errors: Partial<Record<"text" | "remindAt", string>> = {};
  if (v.text.trim() === "") errors.text = "Write a note";
  else if (v.text.length > 1000) errors.text = "Keep it under 1000 characters";
  if (v.remind) {
    if (v.remindAt === "") errors.remindAt = "Pick a reminder time";
    else if (new Date(v.remindAt) <= now) errors.remindAt = "Reminder must be in the future";
  }
  return errors;
}

const toPayload = (v: NoteValues): NotePayload => ({
  text: v.text.trim(),
  priority: v.priority,
  remindAt: v.remind ? new Date(v.remindAt).toISOString() : null,   // hidden field ignored when toggle is off
});
```

- Catatan: `<textarea id="note" maxLength={1000} aria-describedby="note-count note-error">` dengan penghitung live `<p id="note-count">120/1000</p>`.
- Toggle: `<input type="checkbox" id="remind" aria-controls="reminder-fields">`. Field tanggal hanya muncul saat toggle aktif (dan error-nya dihapus saat toggle dimatikan).
- Tanggal: `<input type="datetime-local" id="remindAt" min={nowLocalString}>`, dengan `aria-invalid` dan `aria-describedby` saat ada error.
- Prioritas: `<fieldset><legend>Priority</legend>` dengan tiga radio button biasa.
- `validate` menerima `now` sebagai parameter, jadi tes tidak perlu memalsukan jam.
:::

### 📝 Checklist self-review

- [ ] Nilai form dan payload adalah type yang terpisah
- [ ] Field tambahan hanya dicek saat ditampilkan
- [ ] Pengecekan waktu bisa dites (`now` dioper masuk)
- [ ] Radio dikelompokkan dan error terhubung

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/web/m4/w3/05-controlled-inputs" ai="no-ai" title="Form lamaran yang controlled"}
Bangun form yang sepenuhnya controlled dengan input select, text, number, checkbox, dan textarea, penghitung karakter live, validasi aksesibel yang memfokuskan error pertama, payload ber-type dengan konversi angka, dan reset setelah berhasil — plus kotak pencarian controlled yang tombol Clear-nya mengembalikan fokus ke input memakai ref.
:::

:::hints
- Satu object `values` + helper `set(key, value)` membuat handler tetap kecil.
- Simpan ref dalam object berdasarkan nama field, agar kamu bisa memfokuskan `refs[firstInvalid]`.
- Value `<option>` selalu berupa teks — ubah dengan `Number()` di payload.
:::

## ✅ Cek cepat

:::quiz
Apa yang membuat input disebut "controlled"?

Nilainya berasal dari state React lewat `value` (atau `checked`), dan hanya berubah lewat handler `onChange` yang memperbarui state itu.
:::

:::quiz
Kenapa input number disimpan sebagai teks di state form?

Selagi mengetik, field bisa kosong atau setengah jadi. Mengubahnya di setiap tekan tombol membuat kosong menjadi 0 atau NaN. Ubah sekali saja, saat submit.
:::

## 📚 Lanjut belajar

- [React docs: Reacting to Input with State](https://react.dev/learn/reacting-to-input-with-state)
- [React docs: `<input>` (controlled inputs)](https://react.dev/reference/react-dom/components/input)
- [React docs: Manipulating the DOM with Refs](https://react.dev/learn/manipulating-the-dom-with-refs)

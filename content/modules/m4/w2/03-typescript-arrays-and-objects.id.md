---
title: "Array & Object di TypeScript"
summary: Beri type yang tepat pada list dan tabel lookup — array readonly, tuple, `as const`, `keyof`, `Record`, `satisfies`, dan memperbarui data tanpa mengubah aslinya, semua dicek oleh TypeScript.
sourceHash: 6be650d680dc
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Memberi type pada array, array readonly, dan tuple
- `as const`: membuat type **mengikuti datamu**
- `keyof` dan `Type["field"]`
- `Record` untuk tabel lookup, dan kenapa key yang hilang itu berbahaya
- `satisfies`: mengecek sebuah tabel sudah lengkap
- Memperbarui array dan object tanpa mengubah aslinya

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Array `readonly`** | Array yang dijanjikan kodemu tidak akan diubah |
| **Tuple** | Array dengan panjang tetap dan type untuk setiap posisi: `[min, max]` |
| **`as const`** | "Anggap nilai-nilai ini pasti dan tidak bisa diubah" |
| **`typeof` (di type)** | Mengambil type dari nilai yang sudah ada |
| **`keyof`** | Daftar nama field sebuah type: `"id" \| "title"` |
| **`Record<K, V>`** | Type object dengan key K dan value V |
| **`satisfies`** | "Cek nilai ini cocok dengan sebuah type, tapi pertahankan type pastinya" |

## 🧠 Ide besarnya

Sering kali kamu sudah **punya** datanya — daftar status, tabel label. Daripada menulis daftar yang sama dua kali (sekali sebagai data, sekali sebagai type), biarkan type **mengikuti data**. Seperti **daftar harga induk** di toko: ubah harga di satu tempat, dan setiap struk otomatis memakai harga baru.

## ❓ Kenapa ini penting

Frontend penuh dengan tabel konfigurasi kecil: label per status, warna per status, opsi dropdown. Kalau ada key yang hilang, halaman menampilkan badge kosong — dan tidak ada yang sadar sampai pengguna menemukannya.

```ts
const STATUSES = ["saved", "applied", "interview"];      // string[]
type Status = "saved" | "applied" | "interview";          // typed again by hand → drifts
const LABELS: Record<string, string> = { saved: "Saved", aplied: "Applied" };  // typo compiles
LABELS["interview"].toUpperCase();                        // 💥 undefined at runtime
```

- Daftar dan type ditulis dua kali, jadi lama-lama tidak sama.
- Salah ketik `aplied` tetap lolos compile.
- Key yang hilang baru crash saat aplikasi berjalan.

## 📖 Langkah demi langkah

### 1. Array dan tuple

```ts
const skills: string[] = ["python", "sql"];
function render(items: readonly string[]) { ... }      // accepts mutable AND readonly arrays; can't push
const range: [min: number, max: number] = [9, 14];      // fixed length, typed positions
```

- Untuk input function, utamakan `readonly string[]`: artinya "aku hanya membacanya", seperti meminjam buku perpustakaan — dibaca, bukan dicoret-coret.
- **Tuple** punya posisi yang tetap, seperti tanggal yang ditulis `[hari, bulan, tahun]`.

### 2. `as const` — type mengikuti data

```ts
const STATUSES = ["saved", "applied", "interview", "offer", "rejected"] as const;
// type: readonly ["saved", "applied", "interview", "offer", "rejected"]

type Status = (typeof STATUSES)[number];
// "saved" | "applied" | "interview" | "offer" | "rejected"
```

Baca baris terakhir seperti ini:
- `typeof STATUSES` — "type dari array ini",
- `[number]` — "type dari item mana pun di dalamnya".

Sekarang daftar yang sama dipakai untuk opsi dropdown **dan** type `Status`. Tambahkan status ke daftar → type-nya ikut berubah.

### 3. `keyof` dan `Type["field"]`

```ts
interface Job { id: number; title: string; salaryMax: number | null }
type JobKey = keyof Job;                    // "id" | "title" | "salaryMax"
type Salary = Job["salaryMax"];             // number | null

function sortBy(jobs: readonly Job[], key: "id" | "title") { ... }   // or K extends keyof Job (generics lesson)
```

- `keyof Job` = nama semua field, seperti judul kolom di spreadsheet.
- `Job["salaryMax"]` = type dari satu field.

### 4. `Record` dan key yang hilang

```ts
const counts: Record<Status, number> = { saved: 0, applied: 2, interview: 0, offer: 1, rejected: 0 };   // every key required
const cache: { [jobId: string]: Job } = {};                                                             // any string key
```

- `Record<Status, number>` = satu entri untuk **setiap** status. Lupa satu → error.
- `{ [jobId: string]: Job }` = string apa pun bisa jadi key, jadi key-nya mungkin tidak ada. Dengan pengaturan `noUncheckedIndexedAccess`, `cache["42"]` punya type `Job | undefined`, yang mengingatkanmu untuk menangani "tidak ditemukan".

### 5. `satisfies` — cek tabel sudah lengkap

```ts
const STATUS_LABELS = {
  saved: "Saved",
  applied: "Applied",
  interview: "Interview",
  offer: "Offer",
  rejected: "Rejected",
} satisfies Record<Status, string>;
```

`satisfies` itu seperti **guru yang memeriksa PR-mu** tanpa menulis ulang jawabanmu: ia melaporkan key yang hilang atau salah ketik, tapi nilai-nilaimu tetap mempertahankan type pastinya. (Menulis `: Record<Status, string>` juga mengecek, tapi mengganti type pasti dengan type yang umum.)

Pakai untuk tabel konfigurasi, peta route, dan pengaturan tema.

### 6. Memperbarui tanpa mengubah aslinya

```ts
function moveItem(items: readonly BoardItem[], id: number, status: Status): BoardItem[] {
  return items.map((item) => (item.id === id ? { ...item, status } : item));
}
```

- `map` membuat array baru; item yang berubah menjadi object baru (`{ ...item, status }`).
- Item yang tidak berubah tetap **object yang persis sama**. React memakai ini untuk melewati penggambaran ulang (Minggu 3).
- `readonly` hanya dicek saat menulis kode. `Object.freeze` memblokir perubahan saat aplikasi berjalan.

### 7. Mengecek string dari luar

```ts
function isStatus(value: unknown): value is Status {
  return typeof value === "string" && (STATUSES as readonly string[]).includes(value);
}
const fromUrl = new URLSearchParams(location.search).get("status");
const status: Status = isStatus(fromUrl) ? fromUrl : "saved";
```

Nilai dari URL, localStorage, atau API bisa berupa apa saja. Cek dulu sebelum menganggapnya `Status` — seperti mengecek tiket sebelum mengizinkan orang masuk. (`as readonly string[]` dibutuhkan agar `includes` menerima string apa pun.)

## ⚠️ Kesalahan umum

- Menulis daftar nilai dua kali (array + type) — lama-lama tidak sama.
- Memberi type yang terlalu longgar pada object konfigurasi (`Record<string, string>`), sehingga salah ketik tetap lolos.
- Menganggap `obj[key]` pasti ada pada `Record<string, T>`.
- Mengubah array props atau state secara langsung (`sort`, `push`).
- Memakai nilai dari URL atau storage sebagai `Status` tanpa mengeceknya.

## 🏆 Praktik terbaik

- [ ] Bangun union dari array `as const`, bukan menulis ulang type-nya.
- [ ] Pakai `satisfies Record<Union, V>` untuk tabel lookup yang harus lengkap.
- [ ] Nyalakan `noUncheckedIndexedAccess`; tangani "tidak ditemukan".
- [ ] Terima `readonly T[]` di function; kembalikan array dan object baru.
- [ ] Cek nilai dari URL, storage, dan API dengan type guard sebelum dipakai.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Dengan analogi guru memeriksa PR, jelaskan beda `const LABELS: Record<Status, string> = …` dan `const LABELS = { … } satisfies Record<Status, string>`.

## 📐 Rancang

Rancang pengaturan ber-type untuk **bar filter** CareerPilot: opsi status dengan label dan warna, opsi urutan (`newest`, `oldest`, `company A–Z`) yang dipetakan ke parameter query API, serta membaca dan menulisnya di URL dengan aman.

:::quiz
Tampilkan contoh desainnya

```ts
export const STATUSES = ["saved", "applied", "interview", "offer", "rejected"] as const;
export type Status = (typeof STATUSES)[number];

export const STATUS_META = {
  saved: { label: "Saved", badge: "bg-slate-100 text-slate-700" },
  applied: { label: "Applied", badge: "bg-blue-50 text-blue-700" },
  interview: { label: "Interview", badge: "bg-amber-50 text-amber-800" },
  offer: { label: "Offer", badge: "bg-green-50 text-green-700" },
  rejected: { label: "Rejected", badge: "bg-red-50 text-red-700" },
} satisfies Record<Status, { label: string; badge: string }>;

export const SORTS = {
  newest: { label: "Newest", query: { order_by: "created_at", direction: "desc" } },
  oldest: { label: "Oldest", query: { order_by: "created_at", direction: "asc" } },
  company: { label: "Company A–Z", query: { order_by: "company", direction: "asc" } },
} as const satisfies Record<string, { label: string; query: { order_by: string; direction: "asc" | "desc" } }>;
export type SortKey = keyof typeof SORTS;

export interface Filters { status: Status | null; sort: SortKey; q: string }

const isStatus = (v: unknown): v is Status => typeof v === "string" && (STATUSES as readonly string[]).includes(v);
const isSort = (v: unknown): v is SortKey => typeof v === "string" && Object.hasOwn(SORTS, v);

export function readFilters(params: URLSearchParams): Filters {
  const status = params.get("status");
  const sort = params.get("sort");
  return { status: isStatus(status) ? status : null, sort: isSort(sort) ? sort : "newest", q: params.get("q") ?? "" };
}

export function writeFilters(filters: Filters): URLSearchParams {
  const params = new URLSearchParams();
  if (filters.status) params.set("status", filters.status);
  if (filters.sort !== "newest") params.set("sort", filters.sort);
  if (filters.q.trim()) params.set("q", filters.q.trim());
  return params;
}
```

- Daftar status dan tabel urutan adalah satu-satunya sumber kebenaran.
- `satisfies` menjamin setiap status punya label dan warna.
- Nilai dari URL dicek dengan guard sebelum dipakai.
- Nilai default tidak ditulis ke URL, jadi link tetap pendek.
:::

### 📝 Checklist self-review

- [ ] Satu sumber kebenaran untuk status dan urutan
- [ ] Tabel dicek agar tidak ada key yang hilang
- [ ] Nilai URL dicek sebelum dipakai

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/web/m4/w2/03-arrays-objects" ai="no-ai" title="Papan lamaran ber-type"}
Bangun union `Status` dari array `as const`, buat tabel label yang lengkap dengan `satisfies`, dan tulis function papan yang tidak pernah mengubah input-nya — jumlah yang termasuk nol, memindahkan item, menambah tag, dan mengurutkan — dengan menerima array readonly. Tes type mengecek field readonly, status yang salah, dan key yang salah.
:::

:::hints
- `Object.fromEntries(STATUSES.map((s) => [s, 0])) as Record<Status, number>` memulai semua hitungan dari nol (satu assertion yang bisa dipertanggungjawabkan).
- `items.map((item) => (item.id === id ? { ...item, status } : item))` membuat item yang tidak berubah tetap sama.
- Untuk urutan status: `STATUSES.indexOf(a.status) - STATUSES.indexOf(b.status)`.
:::

## ✅ Cek cepat

:::quiz
Bagaimana cara mendapatkan union dari nilai-nilai di `const X = ["a", "b"] as const`?

`type T = (typeof X)[number]` → `"a" | "b"`.
:::

:::quiz
Apa yang diubah oleh `noUncheckedIndexedAccess`?

Membaca `arr[0]` atau `record[key]` (dengan key dinamis) menyertakan `undefined` di type-nya, jadi kamu harus menangani "tidak ditemukan".
:::

## 📚 Lanjut belajar

- [TypeScript Handbook: Indexed Access Types](https://www.typescriptlang.org/docs/handbook/2/indexed-access-types.html)
- [TypeScript 4.9 release notes: the satisfies operator](https://www.typescriptlang.org/docs/handbook/release-notes/typescript-4-9.html)

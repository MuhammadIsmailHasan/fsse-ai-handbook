---
title: "🔥 Generic di TypeScript"
summary: Tulis function dan type yang bekerja dengan data apa pun sambil tetap menjaga type pastinya — type parameter, constraint, keyof, response API dan store yang generic, serta kapan generic justru memperburuk kode.
sourceHash: 14c423d80aa3
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa itu type parameter (`T`), dan bagaimana TypeScript mengisinya
- Membatasi `T` dengan `extends`, dan mengakses field dengan aman memakai `keyof`
- Type generic seperti `Result<T>` dan `Paginated<T>`
- Store generic (ide di balik state React)
- Kapan generic jadi berlebihan

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Generic** | Function atau type yang bekerja dengan banyak type tapi tetap menjaga type pastinya |
| **Type parameter (`T`)** | Pengganti sebuah type, diisi saat function-nya dipakai |
| **Inference** | TypeScript mencari tahu `T` itu apa dari argumenmu |
| **Constraint (`extends`)** | Aturan `T` boleh berupa apa: `T extends { length: number }` |
| **`keyof T`** | Nama-nama field dari `T` |
| **Wrapper type** | Type yang membungkus data lain: `ApiResponse<Job>` |

## 🧠 Ide besarnya

Generic itu seperti **toples berlabel di warung**: toplesnya bertuliskan "isi: T". Masukkan kerupuk, dan kamu tahu yang keluar kerupuk — tanpa harus membuat "toples kerupuk", "toples kacang", dan "toples permen" terpisah. Tanpa generic, kamu menyalin kode yang sama untuk setiap type, atau memakai `any` dan kehilangan labelnya sama sekali.

## ❓ Kenapa ini penting

Helper seperti `groupBy` atau `paginate`, pembungkus response API, store, dan React hook semuanya bekerja dengan data **apa pun**. Generic menjaga hubungan antara yang masuk dan yang keluar: `paginate(jobs)` mengembalikan `Paginated<Job>`, jadi autocomplete berfungsi di `result.data[0].title`.

Tanpa generic:

```ts
function first(items: any[]): any { return items[0]; }
const job = first(jobs);
job.titel.toUpperCase();          // compiles 😬 crashes at runtime

function firstJob(items: Job[]): Job | undefined { ... }
function firstCompany(items: Company[]): Company | undefined { ... }   // duplication forever
```

## 📖 Langkah demi langkah

### 1. Type parameter

```ts
function firstOrNull<T>(items: readonly T[]): T | null {
  return items.length > 0 ? items[0]! : null;
}

const job = firstOrNull(jobs);       // T inferred as Job → Job | null
const n = firstOrNull([1, 2, 3]);    // number | null
```

- `<T>` mendeklarasikan penggantinya.
- Saat kamu memanggil `firstOrNull(jobs)`, TypeScript melihat array berisi `Job` dan mengisi `T = Job`.
- Kamu hampir tidak pernah menulis `firstOrNull<Job>(…)` sendiri.

### 2. Constraint: aturan untuk `T`

```ts
function longest<T extends { length: number }>(a: T, b: T): T {
  return a.length >= b.length ? a : b;
}

function pick<T extends object, K extends keyof T>(obj: T, keys: readonly K[]): Pick<T, K> { ... }
pick(job, ["title", "salaryMax"]);   // Pick<Job, "title" | "salaryMax">
pick(job, ["company"]);              // ❌ "company" is not a key of Job
```

- `T extends { length: number }` = "T boleh apa saja **yang punya panjang**" (string, array). Seperti tempat parkir yang muat kendaraan apa pun — asal panjangnya kurang dari 5 meter.
- `K extends keyof T` = "K harus salah satu nama field milik T". Kamu tidak bisa meminta field yang tidak ada.

### 3. Callback menjaga type tetap mengalir

```ts
function groupBy<T, K extends PropertyKey>(items: readonly T[], keyOf: (item: T) => K): Partial<Record<K, T[]>> { ... }

groupBy(applications, (app) => app.status);   // Partial<Record<Status, Application[]>>
```

TypeScript tahu `app` adalah `Application` (dari array-nya) dan key-nya adalah `Status` (dari yang dikembalikan callback-mu). Tidak ada type yang ditulis manual.

### 4. Type generic

```ts
type Result<T, E = Error> = { ok: true; value: T } | { ok: false; error: E };

type Paginated<T> = {
  data: T[];
  meta: { page: number; perPage: number; total: number; totalPages: number };
};

type ApiResponse<T> = { data: T };                       // matches your Flask envelope
type ApiList<T> = ApiResponse<T[]> & { meta: Paginated<T>["meta"] };

async function getJson<T>(url: string): Promise<T> { ... }
const page = await getJson<ApiList<Application>>("/api/v1/applications");
```

- `Result<T, E = Error>` — sukses dengan sebuah nilai, atau gagal dengan sebuah error. `E = Error` adalah **nilai default**.
- `Paginated<T>` — satu bentuk "halaman" untuk list apa pun: lowongan, perusahaan, catatan.

:::warning[Generic tidak memvalidasi]
`getJson<ApiList<Application>>()` hanyalah label di toples — tidak ada yang mengecek isinya. Response-nya tidak dicek. Di Minggu 5, gabungkan dengan schema saat runtime (`schema.parse(json)`) supaya type-nya benar-benar terbukti.
:::

### 5. Store generic (pratinjau state React)

```ts
function createStore<T>(initial: T) {
  let value = initial;
  const listeners = new Set<(value: T) => void>();
  return {
    get: () => value,
    set(next: T | ((previous: T) => T)) { ... },
    subscribe(listener: (value: T) => void) { listeners.add(listener); return () => listeners.delete(listener); },
  };
}

const filters = createStore({ status: null as Status | null, q: "" });
filters.set((prev) => ({ ...prev, q: "python" }));
```

Store menyimpan satu nilai dan memberi tahu listener saat nilainya berubah — seperti grup WhatsApp yang memberi notifikasi ke semua anggota saat ada yang posting. `useState<T>` di React dan `create<T>()` di Zustand memakai pola persis seperti ini.

### 6. Lebih jauh (sekadar mencicipi)

```ts
type Nullable<T> = { [K in keyof T]: T[K] | null };        // mapped type
type ElementType<T> = T extends readonly (infer U)[] ? U : never;   // conditional type with infer
```

Library banyak memakai type tingkat lanjut ini. Di kode aplikasi, kamu jarang butuh lebih dari `Partial`, `Pick`, `Omit`, dan sejenisnya.

## ⚠️ Kesalahan umum

- `function f<T>(x: any): T` — mengembalikan `T` yang tidak dicek siapa pun itu berbohong.
- Type parameter yang hanya dipakai sekali (`function f<T>(x: T): void`) — pakai `unknown` saja.
- Membatasi terlalu ketat (`T extends Job` padahal object apa pun bisa) atau terlalu longgar (jadi tidak bisa mengakses field).
- Teka-teki type yang rumit di kode aplikasi yang tidak bisa dibaca siapa pun di tim.
- Memakai generic untuk "pura-pura" data dari luar sudah divalidasi.

## 🏆 Praktik terbaik

- [ ] Biarkan TypeScript mengisi type parameter; tulis sendiri hanya kalau ia tidak bisa.
- [ ] Pakai nama yang jelas kalau ada beberapa (`TData`, `TError`, `K`).
- [ ] Batasi `T` dengan `extends` sesuai yang benar-benar dibutuhkan function.
- [ ] Pakai `keyof` untuk helper yang bekerja dengan nama field.
- [ ] Beri default yang berguna (`Result<T, E = Error>`).
- [ ] Pakai generic saat type output bergantung pada type input — kalau tidak, buat tetap sederhana.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan generic dengan analogi toples berlabel, lalu tunjukkan bagaimana `paginate(jobs, 1, 20)` "tahu" bahwa `result.data` berisi lowongan.

## 📐 Rancang

Rancang pemuat data generic dengan TypeScript biasa (belum pakai React) untuk CareerPilot. Ia memuat data dengan `fetcher`, punya state `idle / loading / success / error` berupa discriminated union, mendukung `reload()`, dan membiarkan pemanggil mengubah data dengan function `select`. Tulis type-nya.

:::quiz
Tampilkan contoh desainnya

```ts
type ResourceState<TData, TError = Error> =
  | { status: "idle" }
  | { status: "loading"; previous?: TData }
  | { status: "success"; data: TData; loadedAt: number }
  | { status: "error"; error: TError; previous?: TData };

interface ResourceOptions<TRaw, TData = TRaw> {
  fetcher: (signal: AbortSignal) => Promise<TRaw>;
  select?: (raw: TRaw) => TData;          // e.g. envelope → data, sort, filter
  clock?: () => number;
}

interface Resource<TData> {
  getState(): ResourceState<TData>;
  load(): Promise<void>;                  // aborts an in-flight load first
  reload(): Promise<void>;
  subscribe(listener: (state: ResourceState<TData>) => void): () => void;
}

declare function createResource<TRaw, TData = TRaw>(options: ResourceOptions<TRaw, TData>): Resource<TData>;

// usage — TData inferred from select:
const applications = createResource({
  fetcher: (signal) => api.get<ApiList<Application>>("/api/v1/applications", { signal }),
  select: (res) => res.data.toSorted((a, b) => b.updatedAt.localeCompare(a.updatedAt)),
});
// Resource<Application[]>
```

- Dua type parameter: `TRaw` (yang dikembalikan jaringan) dan `TData` (yang diinginkan halaman).
- `TData` terisi otomatis dari yang dikembalikan `select`.
- `previous` menjaga data lama tetap tampil saat reload atau setelah error, jadi halaman tidak berkedip kosong.
- Ini versi kecil dari `useQuery` milik TanStack Query (Minggu 4).
:::

### 📝 Checklist self-review

- [ ] Type output otomatis berasal dari `select`
- [ ] State berupa discriminated union
- [ ] Pembatalan dan subscribe sudah ber-type

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/web/m4/w2/07-generics" ai="no-ai" title="Utility generic: groupBy, pick, Result, paginate, dan store"}
Ganti helper yang ber-type `unknown` dengan generic, agar type mengalir dari input ke output: `groupBy`, `pick` dengan `keyof`, type `Result` dengan `tryCatch`, `paginate`, store yang bisa di-subscribe, dan `firstOrNull`. Tes type mengecek type persis yang disimpulkan TypeScript.
:::

:::hints
- `(groups[key] ??= []).push(item)` membangun kelompok dalam satu baris.
- Di `pick`, mulai dengan `const result = {} as Pick<T, K>` lalu salin setiap key.
- `typeof next === "function"` membedakan function updater dari nilai biasa (cast sekali saja).
:::

## ✅ Cek cepat

:::quiz
Apa yang dijamin oleh `K extends keyof T`?

Bahwa `K` adalah salah satu nama field milik `T`, jadi `obj[key]` valid dan ber-type `T[K]`.
:::

:::quiz
Kapan type parameter tidak diperlukan?

Saat hanya muncul sekali dan tidak menghubungkan input dengan output. Pakai `unknown` atau type yang konkret.
:::

## 📚 Lanjut belajar

- [TypeScript Handbook: Generics](https://www.typescriptlang.org/docs/handbook/2/generics.html)
- [TypeScript Handbook: Keyof Type Operator](https://www.typescriptlang.org/docs/handbook/2/keyof-types.html)

## 📣 Akhir Minggu 2 — bagikan progresmu

:::linkedin{type="weekly"}
🔷 Minggu 2: TypeScript + Tailwind CSS.

- Memodelkan lamaran kerja dengan discriminated union — "offer tanpa nominal" sekarang gagal di-compile
- Belajar bahwa type TypeScript hilang saat aplikasi berjalan (jadi data API tetap perlu divalidasi)
- Setup Tailwind CSS v4 dengan design token di CSS, dan membuat kartu responsif dengan utility
- Menulis variant tombol ber-type dengan cn(), tailwind-merge, dan satisfies — pola di balik shadcn/ui

Yang paling "klik" buatku: [jawabanmu].

Berikutnya: React dengan Next.js. 🚀

#TypeScript #TailwindCSS #Frontend #LearningInPublic
:::

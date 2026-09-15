---
title: "Interface, Type Alias & Union Type"
summary: Jelaskan data sungguhan dengan tepat — type object, field opsional dan readonly, union di mana setiap keadaan hanya punya datanya sendiri, type guard, switch yang mencakup semua kasus, dan membangun type baru dari type yang sudah ada.
sourceHash: 565d11f291ff
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Menjelaskan object dengan `interface` dan `type`
- Field opsional (`?`) dan `readonly`
- **Discriminated union**: bentuk terpisah untuk setiap keadaan
- Mengecek semua kasus di dalam `switch`
- Type guard: mengajari TypeScript pengecekan buatanmu sendiri
- Membangun type baru dari type yang sudah ada (`Pick`, `Omit`, `Partial`…)

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Interface** | Penjelasan bernama tentang bentuk sebuah object |
| **Type alias** | Nama untuk type apa pun: `type Status = "saved" \| "applied"` |
| **Optional field (`?`)** | Field yang boleh tidak ada |
| **Discriminated union** | Beberapa bentuk yang dibedakan oleh satu field seperti `status` |
| **Type guard** | Function yang memberi tahu TypeScript "kalau ini mengembalikan true, nilainya type X" |
| **`never`** | Type yang tidak punya nilai sama sekali — dipakai untuk menangkap kasus yang terlupa |
| **Utility type** | Helper bawaan yang membuat type dari type lain (`Partial`, `Pick`…) |

## 🧠 Ide besarnya

Type yang baik itu seperti **formulir yang punya field tepat untuk setiap urusan**. Formulir akta nikah punya field untuk dua pasangan; akta kelahiran punya field untuk orang tua. Satu formulir raksasa dengan semua field "opsional" akan membuat orang mengisi hal yang tidak masuk akal.

Sama di kode: lamaran dengan status **offer** selalu punya nominal; lamaran **saved** tidak pernah punya tanggal interview. Kalau type-nya menyatakan ini, kombinasi yang mustahil bahkan tidak bisa ditulis.

## ❓ Kenapa ini penting

Banyak bug frontend adalah **keadaan yang mustahil**: spinner dan pesan error tampil bersamaan, "offer" tanpa nominal, membaca `interviewAt` pada lamaran yang ditolak.

Type yang semua field-nya opsional mengizinkan semua itu:

```ts
interface Application {
  status: string;
  appliedOn?: string;
  interviewAt?: string;
  offerAmount?: number;
  isLoading?: boolean;
  error?: string;
}
```

Setiap tempat yang memakainya harus menebak: "`offerAmount` ada tidak? Status apa saja yang ada? Bolehkah `isLoading` dan `error` sama-sama true?" TypeScript tidak bisa membantu, karena type-nya mengizinkan apa saja.

## 📖 Langkah demi langkah

### 1. Type object

```ts
interface Company {
  id: number;
  name: string;
  website?: string;                 // optional: string | undefined
}

type JobPosting = {
  readonly id: number;              // can't be reassigned
  title: string;
  company: Company;
  readonly skills: readonly string[];
};
```

- `website?` = field-nya boleh tidak ada.
- `readonly` = nilainya tidak bisa diubah setelah dibuat.

### 2. `interface` atau `type`?

Keduanya menjelaskan object. Bedanya kecil:

| | `interface` | `type` |
|---|---|---|
| Bentuk object | ✅ | ✅ |
| Union, tuple, type sederhana | ❌ | ✅ |
| Memperluas yang lain | ✅ `interface B extends A` | dengan `&` |

Kebiasaan tim yang umum: `interface` untuk bentuk object (props, data API), `type` untuk union. Yang paling penting adalah konsisten.

### 3. Discriminated union: satu bentuk per keadaan

```ts
interface ApplicationBase { id: number; job: JobPosting; updatedAt: string }

type Application =
  | (ApplicationBase & { status: "saved" })
  | (ApplicationBase & { status: "applied"; appliedOn: string })
  | (ApplicationBase & { status: "interview"; appliedOn: string; interviewAt: string })
  | (ApplicationBase & { status: "offer"; appliedOn: string; offerAmount: number })
  | (ApplicationBase & { status: "rejected"; reason?: string });
```

- `|` berarti "salah satu dari bentuk ini".
- `&` berarti "gabungkan": field dasar yang sama **plus** field untuk keadaan itu.
- `status` adalah **label** yang membedakan bentuk-bentuknya — seperti warna karcis parkir yang memberi tahu petugas tarif mana yang berlaku.

Saat kamu mengecek labelnya, TypeScript tahu bentuk pastinya:

```ts
if (app.status === "offer") {
  app.offerAmount;     // ✅ number
}
app.interviewAt;       // ❌ doesn't exist on all members
```

Ide yang sama berlaku untuk memuat data:

```ts
type Remote<T> =
  | { state: "idle" }
  | { state: "loading" }
  | { state: "error"; error: string }
  | { state: "success"; data: T };
```

Sekarang "loading **dan** error bersamaan" mustahil ditulis.

### 4. `switch` yang mencakup semua kasus

```ts
function assertNever(value: never): never {
  throw new Error(`Unhandled: ${JSON.stringify(value)}`);
}

function statusSummary(app: Application): string {
  switch (app.status) {
    case "saved": return "Saved";
    case "applied": return `Applied on ${app.appliedOn}`;
    case "interview": return `Interview at ${app.interviewAt}`;
    case "offer": return `Offer: Rp ${app.offerAmount}`;
    case "rejected": return app.reason ? `Rejected: ${app.reason}` : "Rejected";
    default: return assertNever(app);   // add "withdrawn" to the union → compile error here
  }
}
```

`never` berarti "ini tidak mungkin terjadi". Kalau semua kasus sudah ditangani, tidak ada yang tersisa untuk `default`. Saat seseorang menambahkan status baru seperti `"withdrawn"`, TypeScript menampilkan error **di setiap switch yang melupakannya** — seperti checklist yang tidak mau di-submit sebelum semua kotak dicentang.

### 5. Type guard

```ts
function isRemote(job: JobPosting): job is JobPosting & { location: { kind: "remote" } } {
  return job.location.kind === "remote";
}

const remoteJobs = jobs.filter(isRemote);   // typed as remote jobs
```

Return type `job is …` adalah janji ke TypeScript: "kalau aku mengembalikan `true`, lowongan ini remote". Setelah `filter(isRemote)`, TypeScript tahu setiap item-nya remote. Hati-hati: kalau pengecekanmu salah, TypeScript akan memercayai hal yang salah.

### 6. Membangun type dari type lain

Daripada menyalin field (dan lupa memperbarui salinannya), bangun type baru dari type utama — seperti membuat berbagai formulir dari satu template induk.

```ts
type Status = Application["status"];                     // indexed access
type ApplicationUpdate = Partial<Pick<JobPosting, "title" | "salaryMax">>;
type NewCompany = Omit<Company, "id">;                   // for create forms
type ById = Record<number, Company>;
type Loader = ReturnType<typeof createLoader>;
```

| Helper | Fungsinya |
|---|---|
| `Partial<T>` | membuat semua field opsional (cocok untuk update PATCH) |
| `Required<T>` | membuat semua field wajib |
| `Pick<T, K>` / `Omit<T, K>` | ambil sebagian field saja / buang sebagian field |
| `Record<K, V>` | object dengan key bertipe K dan value bertipe V |
| `Readonly<T>` | membuat semua field readonly |
| `NonNullable<T>` | membuang `null` dan `undefined` |

Saat `JobPosting` berubah, semua type yang dibangun darinya ikut berubah.

## ⚠️ Kesalahan umum

- `status: string`, bukan union berisi nilai-nilai yang sebenarnya.
- Field opsional untuk data yang selalu ada di keadaan tertentu.
- `default:` yang diam-diam mengembalikan sesuatu, bukan `assertNever`.
- Memakai `as` untuk memaksa sebuah bentuk, bukan mengecek labelnya.
- Menyalin field ke type kedua, bukan memakai `Pick` / `Omit`.

## 🏆 Praktik terbaik

- [ ] Pakai discriminated union agar keadaan yang mustahil tidak bisa ditulis.
- [ ] Akhiri switch dengan `assertNever`, agar kasus baru memicu error compile.
- [ ] Bangun type yang berkaitan dengan `Pick`, `Omit`, `Partial`, dan `Type["field"]`.
- [ ] Pakai `readonly` untuk data yang tidak boleh berubah (props, data API).
- [ ] Jaga type guard tetap kecil dan dites.
- [ ] Cek data dari luar di pintu masuknya, lalu ubah menjadi type-mu yang tepat.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke rekan tim apa arti "buat keadaan yang mustahil jadi tidak bisa ditulis", dengan contoh spinner loading dan pesan error yang tampil bersamaan.

## 📐 Rancang

Rancang type untuk **fitur pencocokan CV** CareerPilot. Sebuah request bisa dalam keadaan: idle, sedang meng-upload CV, sedang dianalisis, selesai (skor 0–100, skill yang cocok, skill yang kurang, saran), atau gagal (file terlalu besar, jenis file tidak didukung, atau AI tidak tersedia — retry hanya boleh untuk yang terakhir). Tulis union type-nya dan function yang mengembalikan pesan untuk setiap keadaan.

:::quiz
Tampilkan contoh desainnya

```ts
type MatchFailure =
  | { reason: "file_too_large"; maxMb: number }
  | { reason: "unsupported_type"; allowed: readonly string[] }
  | { reason: "ai_unavailable"; retryAfterSeconds: number };

interface MatchResult {
  score: number;                         // 0–100 (validated at the API boundary)
  matchedSkills: readonly string[];
  missingSkills: readonly string[];
  advice: string;
}

type CvMatchState =
  | { phase: "idle" }
  | { phase: "uploading"; fileName: string; progress: number }
  | { phase: "analyzing"; fileName: string }
  | { phase: "done"; fileName: string; result: MatchResult }
  | { phase: "failed"; fileName: string; failure: MatchFailure };

function canRetry(state: CvMatchState): boolean {
  return state.phase === "failed" && state.failure.reason === "ai_unavailable";
}

function statusMessage(state: CvMatchState): string {
  switch (state.phase) {
    case "idle": return "Upload your CV to see how well you match.";
    case "uploading": return `Uploading ${state.fileName}… ${state.progress}%`;
    case "analyzing": return "Analyzing your CV…";
    case "done": return `Match score: ${state.result.score}/100`;
    case "failed":
      switch (state.failure.reason) {
        case "file_too_large": return `File is larger than ${state.failure.maxMb} MB.`;
        case "unsupported_type": return `Please upload ${state.failure.allowed.join(", ")}.`;
        case "ai_unavailable": return `The AI is busy. Try again in ${state.failure.retryAfterSeconds}s.`;
        default: return assertNever(state.failure);
      }
    default: return assertNever(state);
  }
}
```

- `result` hanya ada di keadaan `done`, jadi halaman tidak bisa menampilkan skor saat masih upload.
- Alasan gagal juga berupa union, masing-masing dengan data tambahannya sendiri.
- Aturan retry ada di satu tempat: `canRetry`.
:::

### 📝 Checklist self-review

- [ ] Setiap keadaan hanya membawa datanya sendiri
- [ ] Alasan gagal juga berupa union
- [ ] Setiap switch mencakup semua kasus

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/web/m4/w2/02-interfaces-unions" ai="no-ai" title="Modelkan lamaran agar keadaan mustahil tidak bisa di-compile"}
Tulis interface, union untuk lokasi, union lamaran yang diberi label `status`, type `Status` yang dibangun darinya, type update `Partial<Pick<…>>`, sebuah type guard, dan function switch yang mencakup semua kasus. Tes type mengecek bahwa object yang salah (offer tanpa nominal, lowongan remote yang punya kota) gagal di-compile.
:::

:::hints
- Taruh field yang sama di interface dasar, lalu gabungkan (`&`) dengan setiap bentuk status.
- `type Status = Application["status"]` — dibangun otomatis.
- `function assertNever(value: never): never` di cabang `default`.
:::

## ✅ Cek cepat

:::quiz
Apa yang membuat sebuah union disebut "discriminated"?

Setiap bentuk punya field yang sama (seperti `status`) dengan nilai tetap yang berbeda, sehingga mengecek field itu memberi tahu TypeScript bentuk mana yang dimaksud.
:::

:::quiz
Kenapa memanggil `assertNever` di cabang `default`?

Kalau seseorang menambahkan kasus baru dan lupa menanganinya, nilainya bukan `never` lagi, jadi kode gagal di-compile tepat di situ.
:::

## 📚 Lanjut belajar

- [TypeScript Handbook: Object Types](https://www.typescriptlang.org/docs/handbook/2/objects.html)
- [TypeScript Handbook: Utility Types](https://www.typescriptlang.org/docs/handbook/utility-types.html)

---
title: "Array JavaScript & Transformasi Data"
summary: Olah data seperti profesional — map, filter, reduce, find, some/every, flatMap, sorting tanpa mutasi, pengelompokan, dan Set — perlengkapan sehari-hari untuk mengubah response API menjadi UI.
sourceHash: b9fb2dcfa2bc
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Dasar array dan method mana yang **memutasi**
- `map`, `filter`, `reduce`, `find`, `some`, `every`, `includes`
- `flatMap`, `Set`, `Object.groupBy`, `Object.entries/fromEntries`
- Sorting dengan comparator — dan `toSorted`, `toReversed`, `with` yang tidak memutasi
- Merangkai transformasi agar mudah dibaca, dan kapan loop biasa lebih baik
- Padanan Python untuk semuanya

## 🧠 Ide besarnya

Method array adalah **ban berjalan di pabrik**: data mentah dari API masuk, setiap stasiun mengerjakan satu tugas (ambil lowongan remote, ubah jadi data kartu, urutkan berdasarkan gaji), dan data siap-UI keluar di ujungnya — tanpa ada yang mengubah bahan aslinya.

## ❓ Kenapa ini ada?

Frontend terus-menerus membentuk ulang data: Flask API-mu mengembalikan daftar lamaran; dashboard butuh jumlah per status, papan butuh pengelompokan per kolom, grafik butuh rata-rata. Method array yang deklaratif menyatakan **apa** yang kamu mau, mudah dites, dan tidak memutasi data yang diandalkan React untuk mendeteksi perubahan (Minggu 3).

## 💥 Apa yang terjadi kalau TIDAK?

```js
function topJobs(jobs) {
  jobs.sort((a, b) => b.salary - a.salary);   // 🐛 mutates the caller's array (and React state!)
  return jobs.slice(0, 3);
}

const titles = [];
for (let i = 0; i <= jobs.length; i++) {       // 🐛 off-by-one → undefined
  if (jobs[i].remote == true) titles.push(jobs[i].title);
}
```

## 📖 Cara kerjanya, langkah demi langkah

### 1. Python ↔ JavaScript

| Python | JavaScript |
|---|---|
| `[j["title"] for j in jobs]` | `jobs.map((j) => j.title)` |
| `[j for j in jobs if j["remote"]]` | `jobs.filter((j) => j.remote)` |
| `functools.reduce` / `sum(...)` | `jobs.reduce((sum, j) => sum + j.salary, 0)` |
| `next((j for j in jobs if j["id"] == 2), None)` | `jobs.find((j) => j.id === 2)` → `undefined` kalau tidak ada |
| `any(...)` / `all(...)` | `some(...)` / `every(...)` |
| `sorted(jobs, key=...)` | `jobs.toSorted((a, b) => ...)` |
| `set(skills)` | `new Set(skills)` |
| `itertools.groupby` / defaultdict | `Object.groupBy(jobs, (j) => j.city)` |
| `enumerate(items)` | `items.map((item, index) => ...)` / `items.entries()` |

### 2. Memutasi vs tidak memutasi

| Memutasi ⚠️ | Mengembalikan array baru ✅ |
|---|---|
| `push`, `pop`, `shift`, `unshift`, `splice` | `concat`, `slice`, spread `[...a, x]` |
| `sort`, `reverse` | `toSorted`, `toReversed` |
| `arr[i] = x` | `arr.with(i, x)` |
| `fill`, `copyWithin` | `map`, `filter`, `flatMap` |

Di kode UI, utamakan kolom kanan — terutama untuk state.

### 3. Tiga serangkai

```js
const remote = jobs.filter((job) => job.remote);
const cards = remote.map((job) => ({ id: job.id, label: `${job.title} · ${job.company}` }));
const total = jobs.reduce((sum, job) => sum + (job.salaryMax ?? 0), 0);
```

`reduce(callback, initialValue)` — selalu berikan nilai awal.

```js
const countsByStatus = applications.reduce((counts, app) => {
  counts[app.status] = (counts[app.status] ?? 0) + 1;
  return counts;
}, {});
// { saved: 2, applied: 5, interview: 1 }
```

### 4. Mencari dan menguji

```js
jobs.find((job) => job.id === id)          // first match or undefined
jobs.findIndex((job) => job.id === id)     // index or -1
jobs.some((job) => job.city === "Bandung") // at least one
jobs.every((job) => job.salaryMax !== null)
skills.includes("python")                  // uses === (NaN-safe)
```

### 5. Sorting dengan benar

```js
[10, 9, 100].sort()                                // [10, 100, 9] 🐛 compares as strings
[10, 9, 100].toSorted((a, b) => a - b)             // [9, 10, 100]
jobs.toSorted((a, b) => (b.salaryMax ?? -1) - (a.salaryMax ?? -1) || a.id - b.id)   // salary desc, then id
jobs.toSorted((a, b) => a.title.localeCompare(b.title, "id"))                        // text, locale-aware
```

Comparator mengembalikan nilai negatif (a duluan), positif (b duluan), atau 0. `||` merangkai pemecah seri (tie-breaker).

### 6. Meratakan, keunikan, pengelompokan

```js
const allSkills = jobs.flatMap((job) => job.skills);            // [["py","sql"],["py"]] → ["py","sql","py"]
const unique = [...new Set(allSkills)].sort();                   // de-duplicate
const byCity = Object.groupBy(jobs, (job) => job.city);          // { Jakarta: [...], Bandung: [...] }
const titlesByCity = Object.fromEntries(
  Object.entries(byCity).map(([city, group]) => [city, group.map((j) => j.title)]),
);
```

`Object.groupBy` adalah ES2024 (semua browser modern dan Node 21+).

### 7. Rangkaian yang mudah dibaca

```js
const topRemoteSalaries = jobs
  .filter((job) => job.remote && job.salaryMax !== null)
  .toSorted((a, b) => b.salaryMax - a.salaryMax)
  .slice(0, 5)
  .map(({ title, salaryMax }) => ({ title, salary: formatRupiah(salaryMax) }));
```

Satu langkah per baris, function helper bernama untuk callback yang tidak sepele. Setiap langkah membuat array baru — tidak masalah untuk ratusan atau ribuan item; untuk data sangat besar atau loop yang sering dijalankan, satu `for...of` bisa lebih jelas dan lebih cepat.

## ⚖️ Trade-off

| Pilihan | ✅ | ❌ |
|---|---|---|
| Rangkaian method | deklaratif, bisa dites, immutable | array perantara; rangkaian panjang jadi sulit dipahami |
| Loop `for...of` | bisa `break` lebih awal, satu kali lewat, familier | lebih banyak variabel yang dimutasi |
| `reduce` untuk semuanya | satu kali lewat | sering lebih sulit dibaca daripada `filter`+`map` atau loop |
| `sort` di tempat | tanpa salinan | memutasi data bersama |
| `Object` sebagai map | ramah JSON | key menjadi string; key prototype — pakai `Map` untuk key sembarang |

## ✅ Kapan dipakai / 🚫 Kapan TIDAK dipakai

- ✅ Membentuk response API menjadi data UI; state turunan (jumlah, kelompok, total).
- ✅ `find`/`some` alih-alih loop pencarian manual.
- 🚫 `map` hanya untuk looping demi efek samping — pakai `forEach` atau `for...of`.
- 🚫 Akrobat `reduce` bersarang — tulis function bernama atau loop.

## 🏆 Praktik terbaik

- [ ] Jangan pernah memutasi input atau state: `toSorted`, spread, `map`/`filter`.
- [ ] Selalu beri `sort` sebuah comparator; pakai `localeCompare` untuk teks.
- [ ] Selalu beri `reduce` nilai awal.
- [ ] Tangani array kosong (rata-rata, `Math.max(...[])` bernilai `-Infinity`).
- [ ] Pakai `??` untuk angka yang tidak ada, bukan `||`.
- [ ] Beri nama callback yang kompleks (`const isAffordable = (job) => ...`).
- [ ] Pilih `Set`/`Map` untuk cek keanggotaan dan lookup alih-alih `includes` di dalam loop (O(n²)).

## 🏭 Cara dipakai di industri

- Setiap component React yang me-render list memakai `map`; UI filter dan sorting adalah `filter` + `toSorted`.
- Reducer Redux/Zustand dan function `select` di TanStack Query mentransformasi data secara immutable.
- Dashboard data menghitung agregat di sisi client dengan `reduce`/`groupBy` untuk dataset kecil (SQL di server untuk yang besar — Modul 2).

## ⚠️ Kesalahan umum

- `.sort()` pada angka tanpa comparator.
- Memutasi props/state dengan `push`/`sort`.
- Lupa `return` di dalam `map` yang memakai kurung kurawal: `map((j) => { j.title })` → isinya `undefined`.
- Memakai `includes` di dalam loop atas array besar.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke rekan tim kenapa `applications.sort(...)` di dalam component bisa memicu bug yang tidak terjadi dengan `toSorted`, meskipun hasilnya terlihat sama di layar.

## 📐 Rancang

Dashboard CareerPilot menerima `applications: [{ id, status, company: { name }, appliedOn, updatedAt, salaryMax }]`. Rancang function-function pure (signature + sketsa rangkaian method) untuk: (1) jumlah per status dengan semua status tetap ada, (2) kolom papan pipeline secara berurutan, masing-masing diurutkan berdasarkan `updatedAt` terbaru dulu, (3) 5 perusahaan teratas berdasarkan jumlah lamaran, (4) response rate = lamaran yang bergerak melewati `applied` ÷ lamaran yang mencapai `applied`.

:::quiz
Tampilkan contoh desainnya

```js
const STATUSES = ["saved", "applied", "screening", "interview", "offer", "accepted", "rejected", "withdrawn"];

export const countsByStatus = (apps) =>
  Object.fromEntries(STATUSES.map((s) => [s, apps.filter((a) => a.status === s).length]));
// one filter per status: O(8n) — fine; a single reduce also works

export const boardColumns = (apps) => {
  const groups = Object.groupBy(apps, (a) => a.status);
  return STATUSES.map((status) => ({
    status,
    items: (groups[status] ?? []).toSorted((a, b) => b.updatedAt.localeCompare(a.updatedAt)), // ISO strings sort lexically
  }));
};

export const topCompanies = (apps, n = 5) =>
  Object.entries(Object.groupBy(apps, (a) => a.company.name))
    .map(([name, group]) => ({ name, count: group.length }))
    .toSorted((a, b) => b.count - a.count || a.name.localeCompare(b.name))
    .slice(0, n);

const PAST_APPLIED = new Set(["screening", "interview", "offer", "accepted", "rejected"]);
export const responseRate = (apps) => {
  const reachedApplied = apps.filter((a) => a.appliedOn !== null);
  if (reachedApplied.length === 0) return 0;
  return reachedApplied.filter((a) => PAST_APPLIED.has(a.status)).length / reachedApplied.length;
};
```

Keputusan yang perlu dicatat: setiap status selalu ada (UI tidak pernah mengecek `undefined`), tie-break eksplisit, penjagaan pembagian dengan nol, timestamp ISO dibandingkan sebagai string. (Apakah "ditolak tanpa screening" dihitung sebagai respons adalah pertanyaan **produk** — tuliskan.)
:::

### 📝 Checklist self-review

- [ ] Function pure, tanpa mutasi
- [ ] Data kosong ditangani
- [ ] Urutan deterministik dengan tie-break

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/web/m4/w1/06-array-methods" ai="no-ai" title="Transformasi data lowongan dengan method array"}
Implementasikan sembilan function data kecil — filter, rata-rata, menghitung, sorting tanpa mutasi, pengelompokan, `every`/`some`, skill unik, dan lookup — atas data input yang dibekukan. Tes gagal kalau kamu memakai loop atau memutasi input.
:::

:::hints
- Data tes dibekukan dengan `Object.freeze`: `sort` padanya akan melempar error — pakai `toSorted`.
- Untuk `skillCounts`, `flatMap` dulu, lalu `reduce` menjadi sebuah object.
- `jobs.map((j) => j.salaryMax).filter((s) => s !== null)` sebelum menghitung rata-rata.
:::

## ✅ Cek cepat

:::quiz
Apa hasil `[3, 20, 100].sort()` dan kenapa?

`[100, 20, 3]` — tanpa comparator, elemen dibandingkan sebagai string ("100" < "20" < "3").
:::

:::quiz
`map` vs `forEach`?

`map` mengembalikan array baru berisi nilai hasil transformasi; `forEach` mengembalikan `undefined` dan hanya untuk efek samping.
:::

## 📖 Kamus (glosarium)

| Istilah | Bahasa Indonesia |
|---|---|
| Immutable | Tidak diubah (membuat salinan baru) |
| Callback | Fungsi yang diberikan ke fungsi lain |
| Comparator | Fungsi pembanding untuk pengurutan |
| Accumulator | Akumulator — nilai yang dibawa `reduce` |
| Derived data | Data turunan (dihitung dari data lain) |

## 📚 Lanjut belajar

- [MDN: Array](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array)
- [MDN: Object.groupBy()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/groupBy)

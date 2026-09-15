---
title: "Array JavaScript & Transformasi Data"
summary: Ubah data API menjadi apa yang dibutuhkan halaman — map, filter, reduce, find, some/every, flatMap, sorting tanpa mengubah data asli, pengelompokan, dan Set — dijelaskan dengan perbandingan Python.
sourceHash: c55d11af5ede
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Method array mana yang **mengubah** array asli, dan mana yang membuat array baru
- `map`, `filter`, `reduce`, `find`, `some`, `every`
- Mengurutkan angka dan teks dengan benar
- Menghapus duplikat dan mengelompokkan data
- Menulis rangkaian langkah yang mudah dibaca
- Versi Python dari setiap method

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **`map`** | Ubah setiap item dan dapatkan array baru dengan panjang yang sama |
| **`filter`** | Ambil hanya item yang lolos syarat |
| **`reduce`** | Gabungkan semua item menjadi satu nilai (total, jumlah, atau object) |
| **Mutate** | Mengubah data asli secara langsung |
| **Immutable** | Tidak mengubah data asli — buat salinan baru |
| **Comparator** | Function kecil yang memberi tahu `sort` mana dari dua item yang duluan |
| **`Set`** | Kumpulan nilai tanpa duplikat |

## 🧠 Ide besarnya

Method array bekerja seperti **laundry kiloan**: baju kotor masuk, satu meja memilah, meja berikutnya mencuci, meja berikutnya melipat, dan baju bersih yang terlipat keluar. Setiap meja punya satu tugas. Dan tumpukan aslinya tidak dihancurkan — setiap meja membuat tumpukan baru.

Dalam kode: lowongan mentah dari API → ambil lowongan remote (`filter`) → ubah masing-masing jadi data kartu (`map`) → urutkan berdasarkan gaji → tampilkan di halaman.

## ❓ Kenapa ini penting

Frontend terus-menerus membentuk ulang data: Flask API-mu mengembalikan daftar lamaran, dashboard butuh jumlah per status, papan butuh pengelompokan per kolom. Method array menyatakan **apa** yang kamu mau dalam beberapa baris yang jelas, mudah dites, dan tidak mengubah data yang diandalkan React (Minggu 3).

Cara lama gampang menimbulkan bug:

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

## 📖 Langkah demi langkah

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

### 2. Mengubah data asli vs membuat array baru

Sebagian method menulis langsung di kertas asli; sebagian lagi memfotokopi dulu.

| Mengubah data asli ⚠️ | Membuat array baru ✅ |
|---|---|
| `push`, `pop`, `shift`, `unshift`, `splice` | `concat`, `slice`, spread `[...a, x]` |
| `sort`, `reverse` | `toSorted`, `toReversed` |
| `arr[i] = x` | `arr.with(i, x)` |
| `fill`, `copyWithin` | `map`, `filter`, `flatMap` |

Di kode halaman — terutama state React — pakai kolom kanan.

### 3. Tiga serangkai: `map`, `filter`, `reduce`

```js
const remote = jobs.filter((job) => job.remote);
const cards = remote.map((job) => ({ id: job.id, label: `${job.title} · ${job.company}` }));
const total = jobs.reduce((sum, job) => sum + (job.salaryMax ?? 0), 0);
```

- `filter` = saringan: hanya yang lolos yang tersisa.
- `map` = stempel: setiap item diubah dengan cara yang sama.
- `reduce` = celengan: kamu memasukkan item satu per satu dan berakhir dengan satu total. Angka `0` di akhir adalah jumlah awal — selalu berikan.

`reduce` juga bisa membangun object, seperti menghitung suara:

```js
const countsByStatus = applications.reduce((counts, app) => {
  counts[app.status] = (counts[app.status] ?? 0) + 1;
  return counts;
}, {});
// { saved: 2, applied: 5, interview: 1 }
```

### 4. Mencari dan mengecek

```js
jobs.find((job) => job.id === id)          // first match or undefined
jobs.findIndex((job) => job.id === id)     // index or -1
jobs.some((job) => job.city === "Bandung") // at least one
jobs.every((job) => job.salaryMax !== null)
skills.includes("python")                  // uses === (NaN-safe)
```

- `some` = "apakah ada **minimal satu**?"
- `every` = "apakah **semuanya** lolos?"

### 5. Mengurutkan dengan benar

```js
[10, 9, 100].sort()                                // [10, 100, 9] 🐛 compares as strings
[10, 9, 100].toSorted((a, b) => a - b)             // [9, 10, 100]
jobs.toSorted((a, b) => (b.salaryMax ?? -1) - (a.salaryMax ?? -1) || a.id - b.id)   // salary desc, then id
jobs.toSorted((a, b) => a.title.localeCompare(b.title, "id"))                        // text, locale-aware
```

Tanpa comparator, JavaScript mengurutkan angka **seperti kata** ("100" datang sebelum "9", seperti di kamus). Comparator menjawab "siapa duluan?":
- angka negatif → `a` duluan,
- angka positif → `b` duluan,
- `0` → sama.

`||` menambahkan pemecah seri: kalau gajinya sama, urutkan berdasarkan id.

### 6. Meratakan, menghapus duplikat, mengelompokkan

```js
const allSkills = jobs.flatMap((job) => job.skills);            // [["py","sql"],["py"]] → ["py","sql","py"]
const unique = [...new Set(allSkills)].sort();                   // de-duplicate
const byCity = Object.groupBy(jobs, (job) => job.city);          // { Jakarta: [...], Bandung: [...] }
const titlesByCity = Object.fromEntries(
  Object.entries(byCity).map(([city, group]) => [city, group.map((j) => j.title)]),
);
```

- `flatMap` = `map`, lalu buka kantong-kantong kecil ke dalam satu kantong besar.
- `new Set(...)` = simpan setiap nilai sekali saja, seperti daftar tamu yang nama dobelnya dicoret.
- `Object.groupBy` = masukkan item ke kotak-kotak berdasarkan label (kota, status).

### 7. Rangkaian yang mudah dibaca

```js
const topRemoteSalaries = jobs
  .filter((job) => job.remote && job.salaryMax !== null)
  .toSorted((a, b) => b.salaryMax - a.salaryMax)
  .slice(0, 5)
  .map(({ title, salaryMax }) => ({ title, salary: formatRupiah(salaryMax) }));
```

Satu langkah per baris, seperti resep masakan. Kalau satu langkah rumit, beri nama (`const isRemote = (job) => ...`). Untuk data sangat besar (puluhan ribu item) atau kode yang sangat sering dijalankan, satu loop `for...of` sederhana bisa lebih jelas dan cepat.

## ⚠️ Kesalahan umum

- `.sort()` pada angka tanpa comparator.
- Mengubah props atau state dengan `push` atau `sort`.
- Lupa `return` di `map` yang memakai kurung kurawal: `map((j) => { j.title })` menghasilkan `undefined`.
- Memakai `map` hanya untuk looping (pakai `forEach` atau `for...of`).
- `reduce` bersarang yang terlalu "pintar" sampai tidak ada yang bisa membacanya.
- `includes` di dalam loop atas array besar (lambat) — pakai `Set`.

## 🏆 Praktik terbaik

- [ ] Jangan ubah input atau state: pakai `toSorted`, spread, `map`, `filter`.
- [ ] Selalu beri `sort` sebuah comparator; pakai `localeCompare` untuk teks.
- [ ] Selalu beri `reduce` nilai awal.
- [ ] Tangani array kosong (rata-rata dari nol item, `Math.max(...[])` bernilai `-Infinity`).
- [ ] Pakai `??` untuk angka yang tidak ada, bukan `||`.
- [ ] Beri nama callback yang rumit (`const isAffordable = (job) => ...`).
- [ ] Pakai `Set` atau `Map` untuk pengecekan "ada di sini tidak?" yang cepat.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke rekan tim kenapa `applications.sort(...)` di dalam component bisa memicu bug yang tidak terjadi dengan `toSorted`, meskipun layarnya terlihat sama. Pakai ide "menulis di kertas asli vs fotokopi".

## 📐 Rancang

Dashboard CareerPilot menerima `applications: [{ id, status, company: { name }, appliedOn, updatedAt, salaryMax }]`. Rencanakan function-function (nama + rangkaian langkah) untuk: (1) jumlah untuk setiap status, termasuk status yang nol, (2) kolom papan secara berurutan, update terbaru di atas, (3) 5 perusahaan teratas berdasarkan jumlah lamaran, (4) response rate = lamaran yang bergerak melewati `applied` ÷ lamaran yang mencapai `applied`.

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

- Setiap status selalu ada, jadi halaman tidak perlu mengecek `undefined`.
- Hasil seri dipecah berdasarkan nama, jadi urutannya tidak pernah loncat-loncat.
- Pembagian dengan nol sudah ditangani.
- Tanggal format ISO (`2026-09-01T…`) bisa dibandingkan sebagai teks.
- "Apakah penolakan tanpa panggilan screening dihitung sebagai respons?" adalah keputusan **produk** — tuliskan.
:::

### 📝 Checklist self-review

- [ ] Tidak ada function yang mengubah input-nya
- [ ] Data kosong ditangani
- [ ] Urutan selalu sama (pakai pemecah seri)

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/web/m4/w1/06-array-methods" ai="no-ai" title="Transformasi data lowongan dengan method array"}
Tulis sembilan function data kecil — filter, rata-rata, menghitung, mengurutkan tanpa mengubah input, mengelompokkan, `every`/`some`, skill unik, dan pencarian — dengan data input yang dibekukan. Tes gagal kalau kamu memakai loop atau mengubah input.
:::

:::hints
- Data tes dibekukan dengan `Object.freeze`: memanggil `sort` padanya akan error — pakai `toSorted`.
- Untuk `skillCounts`, pakai `flatMap` dulu, lalu `reduce` menjadi sebuah object.
- `jobs.map((j) => j.salaryMax).filter((s) => s !== null)` sebelum menghitung rata-rata.
:::

## ✅ Cek cepat

:::quiz
Apa hasil `[3, 20, 100].sort()`, dan kenapa?

`[100, 20, 3]` — tanpa comparator, angka dibandingkan sebagai teks ("100" < "20" < "3").
:::

:::quiz
`map` atau `forEach`?

`map` mengembalikan array baru berisi nilai yang sudah diubah. `forEach` tidak mengembalikan apa-apa — pakai hanya untuk melakukan sesuatu pada setiap item.
:::

## 📚 Lanjut belajar

- [MDN: Array](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Array)
- [MDN: Object.groupBy()](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Object/groupBy)

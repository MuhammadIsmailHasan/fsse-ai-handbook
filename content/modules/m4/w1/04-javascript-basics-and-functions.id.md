---
title: "Dasar JavaScript & Function"
summary: JavaScript untuk developer Python — nilai dan type, membandingkan nilai, const/let, string, function, arrow function, closure, dan module, plus perbedaan kecil yang memicu bug nyata.
sourceHash: 28c2fe9f55b9
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Perbandingan JavaScript dengan Python
- `const` dan `let`, type, object, dan array
- Membandingkan nilai dengan aman (`===`), dan nilai yang "dianggap kosong"
- String dan template literal
- Function, arrow function, dan closure
- Memecah kode ke beberapa file dengan `import` / `export`

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **`const` / `let`** | Cara membuat variabel: `const` tidak bisa diisi ulang, `let` bisa |
| **Truthy / falsy** | Nilai yang dianggap benar atau salah di dalam `if` |
| **`===`** | Perbandingan ketat: nilai **dan** type-nya sama |
| **`??`** | "Pakai nilai cadangan ini hanya kalau nilainya `null` atau `undefined`" |
| **Arrow function** | Cara singkat menulis function: `(a) => a * 2` |
| **Closure** | Function yang mengingat variabel dari tempat ia dibuat |
| **Module** | Satu file yang membagikan kode dengan `export` dan memakai kode dengan `import` |

## 🧠 Ide besarnya

Kamu sudah bisa memprogram. Belajar JavaScript setelah Python itu seperti **pindah dari Jakarta ke Bandung**: kebanyakan hal sama saja (jalan, toko, uang), tapi beberapa aturan lokal bikin kaget. Materi ini fokus ke kejutan-kejutan itu — `==`, nilai kosong, dan angka — karena di situlah bug muncul.

## ❓ Kenapa ini penting

JavaScript adalah satu-satunya bahasa yang dijalankan langsung oleh browser. Setiap halaman interaktif, React, dan Next.js — termasuk aplikasi CareerPilot-mu — adalah JavaScript (atau TypeScript yang diubah menjadi JavaScript).

Perbedaan kecil memicu bug nyata:

```js
if (salaryMax) { showSalary() }          // 🐛 salary 0 is hidden
const count = input.value + 1            // 🐛 "5" + 1 === "51"
if (status == 0) { ... }                 // 🐛 "" == 0 is true
0.1 + 0.2 === 0.3                        // false (same as Python!)
```

## 📖 Langkah demi langkah

### 1. Python ↔ JavaScript

| Python | JavaScript |
|---|---|
| `name = "Siti"` | `const name = "Siti"` (tidak bisa diisi ulang) / `let count = 0` |
| `None` | `null` (sengaja kosong) dan `undefined` (belum pernah diisi) |
| `True`, `False` | `true`, `false` |
| `f"Hi {name}"` | `` `Hi ${name}` `` |
| `len(items)` | `items.length` |
| `dict` | object `{ key: value }` atau `Map` |
| `list` | array `[1, 2, 3]` |
| `def add(a, b=1):` | `function add(a, b = 1) {}` atau `const add = (a, b = 1) => a + b` |
| `and / or / not` | `&& / \|\| / !` |
| `for x in items:` | `for (const x of items) {}` |
| `raise ValueError()` | `throw new Error()` |
| `try/except` | `try/catch` |
| `import x from y` | `import { x } from "./y.js"` |
| blok dengan indentasi | blok `{ }` (titik koma opsional tapi umum dipakai) |

Pakai `const` sebagai default dan `let` hanya kalau nilainya harus berubah. Jangan pernah pakai `var` (cara lama yang perilakunya aneh).

### 2. Type

Type sederhana: `string`, `number` (satu type untuk bilangan bulat dan desimal), `boolean`, `null`, `undefined` (dan `bigint`, `symbol` yang jarang dipakai). Selain itu semuanya **object** — array, function, date.

```js
typeof "hi"        // "string"
typeof 42          // "number"
typeof null        // "object"  ← historic bug; check null with === null
Array.isArray([])  // true
Number("12abc")    // NaN  (Not a Number — and NaN !== NaN; use Number.isNaN)
```

Tips uang: simpan rupiah sebagai **bilangan bulat** (seperti Flask API-mu). Menghitung uang dengan desimal menimbulkan kesalahan pembulatan.

### 3. Membandingkan nilai dan nilai "kosong"

`==` mencoba mengubah type sebelum membandingkan — seperti kasir yang menerima foto uang sebagai uang asli. `===` mengecek nilai **dan** type-nya. Selalu pakai `===`.

```js
0 == ""            // true   ← coercion
0 === ""           // false  ✅ always use === and !==
```

Nilai-nilai ini dianggap **salah** di dalam `if` (falsy): `false`, `0`, `""`, `null`, `undefined`, `NaN`. Selain itu dianggap benar — **termasuk `[]` dan `{}`**. (Di Python, list kosong dianggap salah. Di JavaScript dianggap benar!)

```js
const salary = job.salaryMax || "Not disclosed"   // 🐛 0 → "Not disclosed"
const salary = job.salaryMax ?? "Not disclosed"   // ✅ only null/undefined fall back
const city = job.company?.address?.city           // undefined instead of a crash
```

- `||` memakai nilai cadangan untuk **semua** nilai yang dianggap salah, termasuk `0`.
- `??` memakai nilai cadangan **hanya** untuk `null` atau `undefined`. Lebih tepat untuk angka.
- `?.` (optional chaining) berhenti dengan aman kalau ada yang tidak ada, bukan crash — seperti mengecek apakah pintunya ada sebelum membukanya.

### 4. String

```js
const title = "  Backend Engineer ";
title.trim().toLowerCase()                // "backend engineer"
title.includes("End")                     // false (case-sensitive)
`Rp ${min / 1_000_000}–${max / 1_000_000} juta`
"a-b-c".split("-")                        // ["a", "b", "c"]
"backend engineer".replace(/\s+/g, "-")    // regex with g flag = replace all
```

Template literal (dengan backtick `` ` ``) bekerja seperti f-string di Python: `${...}` menaruh nilai di dalam teks.

### 5. Function

```js
// declaration: hoisted, has its own `this`
function slugify(title) {
  return title.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
}

// arrow function: concise, inherits `this` from outside — the default in modern code
const double = (n) => n * 2;
const toCard = (job) => ({ id: job.id, label: job.title });   // returning an object: wrap in ()

// defaults, rest parameters, destructuring
function salaryLabel({ min = null, max = null } = {}) { ... }
const sum = (...numbers) => numbers.reduce((a, b) => a + b, 0);
```

- **Arrow function** adalah cara lebih singkat menulis function. Kebanyakan kode modern memakainya.
- `...numbers` mengumpulkan semua argumen ke dalam array (seperti `*args` di Python).
- Function adalah nilai: bisa dioper ke function lain, misalnya `button.addEventListener("click", onSave)`. Function yang dioper seperti ini disebut **callback** — "panggil aku lagi saat sesuatu terjadi".

### 6. Closure

Closure adalah function yang **mengingat** variabel dari tempat ia dibuat — seperti **tas ransel** yang selalu dibawa function itu.

```js
function createCounter(start = 0) {
  let count = start;                  // private
  return {
    increment: () => ++count,
    value: () => count,
  };
}
const saved = createCounter();
saved.increment();                    // 1 — nobody else can touch `count`
```

`count` tinggal di dalam ransel. Hanya `increment` dan `value` yang bisa menjangkaunya.

Contoh pemakaian yang umum adalah **debounce**: tunggu sampai pengguna berhenti mengetik, lalu cari sekali saja. Cara kerjanya seperti pintu lift yang menunggu sampai orang berhenti masuk sebelum menutup.

```js
function debounce(fn, waitMs) {
  let timer;                          // shared by every call of the returned function
  return (...args) => {
    clearTimeout(timer);
    timer = setTimeout(() => fn(...args), waitMs);
  };
}
const onSearch = debounce((text) => fetchJobs(text), 300);   // one request after typing stops
```

React hook (Minggu 3) juga dibangun di atas closure.

### 7. Object dan salinan

```js
const job = { id: 1, title: "Backend Engineer", salary: { min: 9e6, max: 14e6 } };
const { title, salary: { max } } = job;          // destructuring
const updated = { ...job, title: "Senior Backend Engineer" };   // copy + change (shallow!)
const [first, ...rest] = ["python", "sql", "docker"];
```

- **Destructuring** mengambil nilai dari object atau array ke dalam variabel.
- `{ ...job }` (spread) membuat salinan. Ini salinan **dangkal**: kotak luarnya baru, tapi kotak di dalamnya (seperti `salary`) masih dipakai bersama. Pakai `structuredClone(job)` untuk salinan penuh.
- `const copy = job` **tidak** menyalin — kedua nama menunjuk ke object yang sama (sama seperti Python).

### 8. Module

```js
// format.js
export function slugify(title) { ... }
export const CURRENCY = "IDR";

// app.js
import { slugify, CURRENCY } from "./format.js";
```

`export` membagikan kode dari sebuah file; `import` memakainya di file lain. Di browser: `<script type="module" src="app.js"></script>`. Setiap module punya variabelnya sendiri, jadi file-file tidak saling menimpa.

## ⚠️ Kesalahan umum

- `"5" + 1` dari input form menghasilkan `"51"` — ubah dulu dengan `Number()`.
- Mengecek list kosong dengan `if (list)` — `[]` dianggap benar. Pakai `list.length === 0`.
- `||` untuk nilai default angka (rusak saat `0`) — pakai `??`.
- Lupa `return` di arrow function yang memakai `{ }`.
- Mengubah object yang dioper masuk — mengejutkan pemanggilnya (dan nanti merusak React).

## 🏆 Praktik terbaik

- [ ] `const` sebagai default, `let` saat perlu, jangan pernah `var`.
- [ ] Selalu `===` dan `!==`; `??` untuk default; `?.` untuk data yang mungkin tidak ada.
- [ ] Function kecil dengan nama jelas; hindari variabel global.
- [ ] Template literal, bukan menyambung string dengan `+`.
- [ ] Satu tugas per module (file).
- [ ] Pakai Prettier (merapikan format) dan ESLint (menangkap `==`, variabel tak terpakai).
- [ ] Pelajari **Console** browser dan breakpoint — `debugger;` bekerja seperti `breakpoint()` di Python.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke developer Python kenapa `if (job.salaryMax)` adalah bug di JavaScript kalau gaji bisa bernilai `0`, dan operator mana yang memperbaiki nilai default-nya.

## 📐 Rancang

Kotak pencarian lowongan CareerPilot memanggil API selagi pengguna mengetik. Rencanakan function-function-nya (nama, input, output) yang: merapikan teks pencarian, menunggu sampai ketikan berhenti (debounce), mengabaikan jawaban lama yang datang terlambat, dan mengingat 20 pencarian terakhir.

:::quiz
Tampilkan contoh desainnya

```js
export const normalizeQuery = (text) => text.trim().replace(/\s+/g, " ").toLowerCase();

export function createSearch({ fetchJobs, render, waitMs = 300, cacheSize = 20 }) {
  const cache = new Map();          // query → results (Map keeps insertion order → simple LRU)
  let latestRequestId = 0;          // closure state

  async function run(rawText) {
    const query = normalizeQuery(rawText);
    if (query === "") return render([]);
    if (cache.has(query)) {
      const results = cache.get(query);
      cache.delete(query); cache.set(query, results);   // refresh recency
      return render(results);
    }
    const requestId = ++latestRequestId;
    const results = await fetchJobs(query);
    if (requestId !== latestRequestId) return;          // an older response arrived late → ignore
    cache.set(query, results);
    if (cache.size > cacheSize) cache.delete(cache.keys().next().value);   // evict oldest
    render(results);
  }

  return debounce(run, waitMs);
}
```

- `normalizeQuery` tidak punya efek samping, jadi mudah dites.
- Cache dan penghitung request tinggal di "ransel" closure — tidak ada yang lain bisa mengubahnya.
- Setiap request mendapat nomor. Kalau nomor lama menjawab paling akhir, hasilnya diabaikan — seperti pelayan yang mengabaikan pesanan yang sudah kamu ganti.
- `fetchJobs` dan `render` dioper masuk, jadi tes bisa memakai versi palsu.
:::

### 📝 Checklist self-review

- [ ] Jawaban lama yang datang terlambat diabaikan
- [ ] State privat disimpan di dalam closure
- [ ] Hal yang dibutuhkan function dioper masuk (mudah dites)

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/web/m4/w1/04-js-basics-functions" ai="no-ai" title="Slug, label gaji, closure, dan debounce"}
Tulis function-function kecil: ubah string menjadi slug URL, buat label gaji untuk beberapa kasus "nilai tidak ada", cek teks kosong tanpa mengandalkan truthiness, buat counter dengan closure, dan tulis function debounce (dites dengan timer palsu) — hanya dengan sintaks modern.
:::

:::hints
- `slugify`: dua kali replace dengan regex — karakter selain huruf/angka menjadi `-`, lalu hapus `-` di awal dan akhir.
- `salaryLabel`: bandingkan dengan `=== null || === undefined` (tesnya melarang `==`, jadi tulis lengkap).
- `Math.round(x * 10) / 10` membulatkan ke satu desimal; `String(9)` adalah `"9"` dan `String(9.5)` adalah `"9.5"`.
- `debounce`: simpan `timer` di luar function yang dikembalikan.
:::

## ✅ Cek cepat

:::quiz
Apa beda `null` dan `undefined`?

`undefined` berarti nilai belum pernah diisi (property atau argumen yang tidak ada). `null` berarti "sengaja kosong". Keduanya memicu `??`.
:::

:::quiz
Apa yang diingat oleh sebuah closure?

Variabel-variabel dari tempat function itu dibuat. Variabel itu tetap hidup selama function-nya masih ada.
:::

## 📚 Lanjut belajar

- [MDN: JavaScript Guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide)
- [javascript.info — The Modern JavaScript Tutorial](https://javascript.info/)
- [MDN: Closures](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Closures)

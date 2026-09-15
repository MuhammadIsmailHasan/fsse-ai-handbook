---
title: "Dasar JavaScript & Function"
summary: JavaScript untuk developer Python — nilai dan type, kesamaan dan truthiness, const/let, string dan template literal, function, arrow function, closure, module, serta keanehan yang memicu bug nyata.
sourceHash: ce2c7ef09159
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Di mana JavaScript berjalan (browser, Node.js) dan bedanya dengan Python
- `const` / `let`, type primitif, object dan array
- `===` vs `==`, **truthiness**, `??` vs `||`, optional chaining `?.`
- String, template literal, number (dan jebakannya)
- Function declaration, **arrow function**, parameter default dan rest
- **Closure** dan function sebagai nilai (callback, debounce)
- ES module: `import` / `export`

## 🧠 Ide besarnya

Kamu sudah bisa memprogram. JavaScript adalah **dialek baru, bukan cara berpikir baru**: variabel, function, loop, dan object bekerja mirip Python. Bahayanya ada di perbedaan kecil yang *terlihat* familier — `==`, truthiness, `this`, number — jadi materi ini fokus di sana.

## ❓ Kenapa ini ada?

JavaScript adalah satu-satunya bahasa yang dijalankan browser secara native, jadi setiap halaman web interaktif — termasuk React, Next.js, dan UI aplikasi CareerPilot-mu — adalah JavaScript (atau TypeScript yang di-compile menjadi JavaScript). Dengan Node.js, JavaScript juga menjalankan server, build tool, dan CLI.

## 💥 Apa yang terjadi kalau TIDAK mempelajari keanehannya?

```js
if (salaryMax) { showSalary() }          // 🐛 salary 0 is hidden
const count = input.value + 1            // 🐛 "5" + 1 === "51"
if (status == 0) { ... }                 // 🐛 "" == 0 is true
0.1 + 0.2 === 0.3                        // false (same as Python!)
```

## 📖 Cara kerjanya, langkah demi langkah

### 1. Contekan Python ↔ JavaScript

| Python | JavaScript |
|---|---|
| `name = "Siti"` | `const name = "Siti"` (tidak bisa di-assign ulang) / `let count = 0` |
| `None` | `null` (sengaja kosong) dan `undefined` (belum di-set) |
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

Jangan pernah pakai `var` (scope-nya function, di-hoist, membingungkan). `const` sebagai default; `let` saat kamu memang harus meng-assign ulang.

### 2. Type

Primitif: `string`, `number` (satu type untuk integer dan float), `bigint`, `boolean`, `null`, `undefined`, `symbol`. Selain itu semuanya **object** (array, function, date…).

```js
typeof "hi"        // "string"
typeof 42          // "number"
typeof null        // "object"  ← historic bug; check null with === null
Array.isArray([])  // true
Number("12abc")    // NaN  (Not a Number — and NaN !== NaN; use Number.isNaN)
```

Uang: number adalah float. Simpan rupiah sebagai **integer** (seperti Flask API-mu), jangan pernah menghitung mata uang dengan pecahan satuan.

### 3. Kesamaan dan truthiness

```js
0 == ""            // true   ← coercion
0 === ""           // false  ✅ always use === and !==
```

Nilai **falsy**: `false`, `0`, `-0`, `0n`, `""`, `null`, `undefined`, `NaN`. Selain itu semuanya truthy — termasuk `"0"`, `[]`, dan `{}` (berbeda dengan Python, di mana list kosong itu falsy!).

```js
const salary = job.salaryMax || "Not disclosed"   // 🐛 0 → "Not disclosed"
const salary = job.salaryMax ?? "Not disclosed"   // ✅ only null/undefined fall back
const city = job.company?.address?.city           // undefined instead of a crash
```

### 4. String

```js
const title = "  Backend Engineer ";
title.trim().toLowerCase()                // "backend engineer"
title.includes("End")                     // false (case-sensitive)
`Rp ${min / 1_000_000}–${max / 1_000_000} juta`
"a-b-c".split("-")                        // ["a", "b", "c"]
"backend engineer".replace(/\s+/g, "-")    // regex with g flag = replace all
```

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

Function adalah nilai: bisa dioper ke mana-mana (`button.addEventListener("click", onSave)`), dikembalikan, dan disimpan.

### 6. Closure

Sebuah function mengingat variabel dari scope tempat ia dibuat:

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

Closure menjadi mesin di balik event handler, React hook (Minggu 3), dan utility seperti **debounce**:

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

### 7. Object, spread, dan destructuring

```js
const job = { id: 1, title: "Backend Engineer", salary: { min: 9e6, max: 14e6 } };
const { title, salary: { max } } = job;          // destructuring
const updated = { ...job, title: "Senior Backend Engineer" };   // copy + change (shallow!)
const [first, ...rest] = ["python", "sql", "docker"];
```

Object dan array adalah **reference** (seperti Python): `const copy = job` tidak menyalin. Spread membuat salinan **dangkal** (shallow); `structuredClone(job)` membuat salinan dalam (deep).

### 8. Module

```js
// format.js
export function slugify(title) { ... }
export const CURRENCY = "IDR";

// app.js
import { slugify, CURRENCY } from "./format.js";
```

Di browser: `<script type="module" src="app.js"></script>`. Di Node: `"type": "module"` di `package.json`. Setiap module punya scope sendiri — tidak ada global yang tak disengaja.

## ⚖️ Trade-off

| Pilihan | ✅ | ❌ |
|---|---|---|
| Arrow function | ringkas, `this` yang bisa ditebak | tidak bisa jadi constructor; tanpa `arguments` |
| Function declaration | di-hoist, nama jelas di stack trace | `this` bergantung pada cara pemanggilannya |
| `==` | lebih pendek | bug coercion — hindari |
| `\|\|` untuk default | berfungsi untuk string | salah untuk `0`, `""`, `false` → pakai `??` |
| JS biasa | tanpa build step | tanpa type safety → TypeScript minggu depan |

## ✅ Kapan dipakai / 🚫 Kapan TIDAK dipakai

- ✅ `const` + arrow function + `===` + `??` + `?.` sebagai default.
- ✅ Closure untuk state privat dan callback.
- 🚫 `var`, `==`, mengubah prototype bawaan, variabel global.
- 🚫 Matematika number untuk uang dengan desimal.

## 🏆 Praktik terbaik

- [ ] `const` sebagai default, `let` hanya saat meng-assign ulang, jangan pernah `var`.
- [ ] Selalu `===`/`!==`; `??` untuk default; `?.` untuk data opsional.
- [ ] Function kecil yang pure dengan nama jelas; hindari state global tersembunyi.
- [ ] Template literal alih-alih menyambung string.
- [ ] Pakai ES module; satu tanggung jawab per module.
- [ ] Format dengan Prettier dan lint dengan ESLint (keduanya menangkap `==`, variabel tak terpakai, shadowing).
- [ ] Belajar memakai **Console** browser dan breakpoint **debugger** — `debugger;` bekerja seperti `breakpoint()` di Python.

## 🏭 Cara dipakai di industri

- Hampir semua frontend memakai JavaScript/TypeScript; banyak backend dan tool memakai Node.js, Deno, atau Bun.
- Code review rutin menandai `==`, default `||` untuk angka, dan mutasi object yang dipakai bersama.
- Debounce/throttle adalah standar untuk kotak pencarian dan handler scroll (TanStack, lodash, custom hook).

## ⚠️ Kesalahan umum

- Penyambungan string `"5" + 1` dari input form → konversi dengan `Number()`.
- Mengecek kosong dengan `if (list)` — `[]` itu truthy; pakai `list.length === 0`.
- Lupa `return` di arrow function multi-baris yang memakai `{ }`.
- Memutasi object yang dioper masuk (mengejutkan pemanggilnya — dan nanti merusak React).

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke developer Python kenapa `if (job.salaryMax)` adalah bug di JavaScript saat gaji bisa bernilai `0`, dan operator mana yang memperbaiki kasus "nilai default".

## 📐 Rancang

Kotak pencarian lowongan CareerPilot memanggil API selagi pengguna mengetik. Rancang function-function-nya (nama, input, output) yang: menormalkan query, men-debounce request, mengabaikan response yang datang tidak berurutan (response lama yang lambat tidak boleh menimpa hasil yang lebih baru), dan meng-cache 20 query terakhir.

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

- `normalizeQuery` yang pure sangat mudah dites.
- Closure menyimpan cache dan penghitung request secara privat.
- Dependency (`fetchJobs`, `render`) di-inject → bisa dites dengan fake.
- Nanti, `AbortController` bisa membatalkan request usang alih-alih mengabaikannya (materi 07), dan TanStack Query mengerjakan sebagian besar hal ini untukmu (Minggu 4).
:::

### 📝 Checklist self-review

- [ ] Response yang datang tidak berurutan sudah ditangani
- [ ] State disimpan privat di dalam closure
- [ ] Dependency di-inject

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/web/m4/w1/04-js-basics-functions" ai="no-ai" title="Slug, label gaji, closure, dan debounce"}
Implementasikan pembersihan string, label gaji dengan beberapa kasus nilai opsional, pengecekan kosong yang tidak mengandalkan truthiness, counter berbasis closure, dan function debounce yang dites dengan fake timer — hanya dengan sintaks modern.
:::

:::hints
- `slugify`: dua kali replace dengan regex — karakter non-alfanumerik menjadi `-`, lalu buang `-` di awal/akhir.
- `salaryLabel`: bandingkan dengan `=== null || === undefined` (atau `== null` — tapi tesnya melarang `==`, jadi tulis lengkap).
- `Math.round(x * 10) / 10` membulatkan ke satu desimal; `String(9)` adalah `"9"` dan `String(9.5)` adalah `"9.5"`.
- `debounce`: simpan `timer` di luar function yang dikembalikan.
:::

## ✅ Cek cepat

:::quiz
Apa beda `null` dan `undefined`?

`undefined` berarti nilai tidak pernah di-set (property atau argumen yang tidak ada); `null` adalah "tidak ada nilai" yang disengaja. Keduanya falsy dan keduanya memicu `??`.
:::

:::quiz
Apa yang ditangkap oleh sebuah closure?

Variabel-variabel dari scope tempat function itu dibuat, yang tetap hidup selama function itu masih ada.
:::

## 📖 Kamus (glosarium)

| Istilah | Bahasa Indonesia |
|---|---|
| Truthy / falsy | Nilai yang dianggap benar / salah dalam kondisi |
| Strict equality | Kesamaan ketat (`===`) |
| Arrow function | Fungsi panah |
| Closure | Penutupan — fungsi yang mengingat variabel di sekitarnya |
| Callback | Fungsi yang dipanggil kembali oleh fungsi lain |
| Debounce | Menunda eksekusi sampai input berhenti |

## 📚 Lanjut belajar

- [MDN: JavaScript Guide](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide)
- [javascript.info — The Modern JavaScript Tutorial](https://javascript.info/)
- [MDN: Closures](https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Closures)

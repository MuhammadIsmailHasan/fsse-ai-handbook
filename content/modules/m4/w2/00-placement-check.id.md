---
title: "Cek Penempatan Minggu 2"
summary: Type TypeScript, union dan generic, serta Tailwind CSS v4 — cari tahu apa yang bisa kamu lewati sebelum React.
sourceHash: 770535cf9a37
---

::::placement{id="modules/m4/w2"}
Jawab dari ingatan. Kalau ada istilah yang terasa baru, itu tanda untuk mempelajari materinya.

:::quiz
1 · Apa beda `unknown` dan `any`?

`any` mematikan pengecekan type — apa pun boleh, dan kesalahan tetap tersembunyi. `unknown` juga berarti "bisa apa saja", tapi TypeScript mengharuskanmu mengeceknya dulu (`typeof`, validasi) sebelum dipakai. Pakai `unknown` untuk data yang tidak kamu percaya.
:::

:::quiz
2 · Sebuah response API bisa berupa `{ ok: true, data: Job[] }` atau `{ ok: false, error: string }`. Bagaimana TypeScript tahu `data` ada?

Tulis sebagai satu type dengan dua pilihan: `type Response = { ok: true; data: Job[] } | { ok: false; error: string }`. Setelah `if (res.ok)`, TypeScript tahu itu pilihan pertama, jadi `res.data` bisa dipakai.
:::

:::quiz
3 · Apakah TypeScript mengecek JSON yang dikembalikan Flask API-mu saat aplikasi berjalan?

Tidak. Type dihapus saat kode di-build. `await res.json()` langsung dipercaya begitu saja. Kalau datanya mungkin tidak cocok, cek dengan library validasi (Zod, Minggu 5).
:::

:::quiz
4 · Tulis function `first` yang mengembalikan item pertama dari array apa pun (atau `undefined`) dengan type yang benar.

`function first<T>(items: readonly T[]): T | undefined { return items[0]; }` — `T` adalah type pengganti yang diisi TypeScript berdasarkan argumennya.
:::

:::quiz
5 · Di Tailwind, apa arti `md:grid-cols-2`? Apakah Tailwind mobile first?

Dua kolom mulai dari lebar layar `md` (48rem) **dan lebih besar**. Ya: class tanpa prefix berlaku untuk semua ukuran; prefix menambahkan rule untuk layar yang lebih besar.
:::

:::quiz
6 · Di mana kamu menambahkan warna dan breakpoint sendiri di Tailwind v4?

Di CSS, dengan `@theme { --color-brand-500: …; --breakpoint-3xl: 120rem; }`. Setiap nilai menjadi class Tailwind sekaligus variabel CSS. Tidak perlu `tailwind.config.js`.
:::
::::

:::tip[Menilai dirimu sendiri]
Lulus dengan **5 dari 6** → baca sekilas materinya dan kerjakan latihannya. Banyak developer salah menjawab pertanyaan 3 selama bertahun-tahun — pastikan kamu benar-benar paham.
:::

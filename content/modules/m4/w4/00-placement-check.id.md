---
title: "Cek Penempatan Minggu 4"
summary: Routing App Router, navigasi, environment variable, memanggil API, Server vs Client Component, caching, dan TanStack Query — cek apa yang bisa kamu lewati.
sourceHash: 77d17c7f4c1b
---

::::placement{id="modules/m4/w4"}
Jawab dari ingatan. Kalau ada istilah yang terasa baru, itu tanda untuk mempelajari materinya.

:::quiz
1 · File mana yang membuat URL `/jobs/42`, dan apa yang diterima halamannya?

`app/jobs/[id]/page.tsx`. Halaman menerima `params` sebagai **Promise** (`{ params: Promise<{ id: string }> }`) yang harus di-`await`. `id` berupa teks `"42"`, bukan angka.
:::

:::quiz
2 · Apa beda `API_TOKEN` dan `NEXT_PUBLIC_API_URL` di file `.env` Next.js?

Variabel tanpa prefix hanya ada di server. Variabel `NEXT_PUBLIC_` disalin ke JavaScript browser saat build — siapa pun bisa membacanya, jadi jangan pernah taruh rahasia di sana.
:::

:::quiz
3 · Kapan sebuah component sebaiknya menjadi Client Component?

Saat butuh state, effect, handler klik, custom hook, atau fitur browser. Memuat data yang memakai rahasia, format data yang berat, dan markup statis cocok di Server Component.
:::

:::quiz
4 · Di Next.js 16 dengan Cache Components, apakah `fetch` otomatis di-cache? Bagaimana cara meng-cache daftar lowongan publik selama satu jam dan menyegarkannya setelah admin mengedit lowongan?

Tidak — data selalu segar (dinamis) secara default. Taruh `"use cache"`, `cacheLife("hours")`, dan `cacheTag("jobs")` di function data, lalu panggil `updateTag("jobs")` (atau `revalidateTag`) di Server Action setelah edit berhasil.
:::

:::quiz
5 · Apa fungsi `error.tsx`, dan kenapa harus menjadi Client Component?

Menangkap error untuk bagian aplikasinya dan menampilkan layar pengganti beserta `error` dan function `retry()`. Menangkap error render butuh React di sisi browser, jadi file-nya butuh `"use client"`.
:::

:::quiz
6 · Kenapa memakai TanStack Query dan bukan `useEffect` + `useState` untuk memuat data di Client Component?

Ia menangani caching, mencegah request ganda, menyegarkan data di latar belakang, retry, pembatalan, state loading/error, dan pembaruan setelah perubahan — tanpa race condition dan kode yang berulang.
:::
::::

:::tip[Menilai dirimu sendiri]
Lulus dengan **5 dari 6**. Pertanyaan 4 berubah di Next.js 15 dan 16 — developer berpengalaman pun sebaiknya membaca materi 06.
:::

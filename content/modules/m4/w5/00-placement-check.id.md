---
title: "Cek Penempatan Minggu 5"
summary: Server Action dan state form, login berbasis sesi, role dan izin, Context, Route Handler, useEffect, React Hook Form + Zod, shadcn/ui, dan Zustand — cek apa yang bisa kamu lewati.
sourceHash: 55a92d423576
---

::::placement{id="modules/m4/w5"}
Jawab dari ingatan. Kalau ada istilah yang terasa baru, itu tanda untuk mempelajari materinya.

:::quiz
1 · Sebuah Server Action mengecek form dan mengembalikan error per field. Hook apa yang menampilkan error itu dan tombol "Menyimpan…"? Dan kenapa server tetap harus mengecek form padahal browser sudah mengeceknya?

`useActionState(action, initialState)` mengembalikan `[state, formAction, isPending]`; `useFormStatus()` di dalam form memberi `pending` untuk tombol submit. Server Action adalah endpoint POST publik — siapa pun bisa memanggilnya tanpa halamanmu — jadi pengecekan di server adalah satu-satunya yang bisa dipercaya.
:::

:::quiz
2 · Setelah login, di mana aplikasi Next.js sebaiknya menyimpan access token Flask, dan pengaturan cookie apa yang penting?

Di cookie sesi yang ditandatangani atau dienkripsi dan diatur oleh server: `httpOnly` (JavaScript tidak bisa membacanya), `secure` (hanya HTTPS), `sameSite: "lax"` (memblokir sebagian besar request dari situs lain), `path: "/"`, dan waktu kedaluwarsa. Bukan di `localStorage`.
:::

:::quiz
3 · Kamu mengecek login di `proxy.ts` dan menyembunyikan link admin dari yang bukan admin. Apakah Server Action admin sudah aman?

Belum. Pengecekan di proxy hanya pengecekan awal yang cepat, dan menyembunyikan link hanya soal tampilan. Server Action (dan Flask API) harus mengecek sesi dan izinnya sendiri.
:::

:::quiz
4 · Sebuah context menyediakan `{ filters, setFilters }` sebagai object baru yang dibuat di provider. Masalah performa apa yang muncul, dan satu cara memperbaikinya?

Object baru di setiap render membuat semua component yang memakai context itu digambar ulang, bahkan yang hanya memanggil `setFilters`. Perbaikan: bungkus value dengan `useMemo`, atau pecah menjadi context state dan context setter.
:::

:::quiz
5 · Sebutkan dua bug di `useEffect(() => { fetch(url).then(r => r.json()).then(setData) }, [url])`.

Tanpa pembatalan → response lama yang lambat bisa menimpa yang lebih baru (race condition), dan bisa mengubah state setelah component-nya hilang. Juga tanpa penanganan loading dan error. Tambahkan cleanup `AbortController` — atau pakai TanStack Query / Server Component.
:::

:::quiz
6 · Kapan memilih React Hook Form + Zod dibanding form Server Action sederhana, dan Zustand dibanding Context?

React Hook Form + Zod: form browser yang besar dengan pengecekan instan, kelompok field yang berulang, banyak field. Zustand: state UI browser yang dipakai component-component yang berjauhan dan sering berubah, di mana setiap component hanya berlangganan bagian yang ia pakai. Data server tetap di Server Component atau TanStack Query.
:::
::::

:::tip[Menilai dirimu sendiri]
Lulus dengan **5 dari 6**. Pertanyaan 2 dan 3 tentang keamanan — kalau salah satunya keliru, tetap kerjakan materi 02 dan 03.
:::

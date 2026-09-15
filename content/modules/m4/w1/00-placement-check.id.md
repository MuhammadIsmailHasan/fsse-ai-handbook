---
title: "Cek Penempatan Minggu 1"
summary: Semantik HTML, layout CSS, dasar JavaScript, DOM, kode async, dan aksesibilitas — lihat bagian mana dari web platform yang bisa kamu lewati.
sourceHash: 12aac51d46d6
---

::::placement{id="modules/m4/w1"}
Di Modul 2 kamu sudah membangun API. Minggu ini sisi sebaliknya: apa yang berjalan di browser. Jawab tanpa mencari apa pun.

:::quiz
1 · Kenapa memakai `<button>` dan bukan `<div onclick>` untuk sebuah aksi?

`<button>` bisa difokuskan, berfungsi dengan Enter/Space, diumumkan sebagai tombol oleh screen reader, dan bisa men-submit form. `<div>` butuh `tabindex`, key handler, dan role ARIA untuk mendekati itu — dan biasanya tetap ada yang terlewat.
:::

:::quiz
2 · Flexbox atau Grid untuk (a) navbar dengan logo di kiri dan link di kanan, (b) halaman dengan sidebar + konten + grid kartu?

(a) Flexbox — perataan satu dimensi dalam satu baris. (b) Grid — layout dua dimensi berupa baris dan kolom (kartu dengan `repeat(auto-fill, minmax(...))`). Keduanya sering dikombinasikan.
:::

:::quiz
3 · Apa yang dicetak kode ini, dan kenapa? `console.log(0 == "", [] == false, null ?? "x", 0 || "x")`

`true true "x" "x"` — `==` melakukan type coercion (pakai `===`); `??` hanya memakai nilai cadangan untuk `null`/`undefined`; `||` memakai nilai cadangan untuk nilai falsy apa pun, termasuk `0`.
:::

:::quiz
4 · Kenapa `element.innerHTML = job.title` berbahaya, dan apa yang sebaiknya dipakai?

Kalau `job.title` berisi HTML (misalnya `<img onerror=...>`), HTML itu di-parse dan bisa menjalankan script (XSS). Pakai `textContent` atau `createElement` untuk data.
:::

:::quiz
5 · `fetch("/api/jobs")` mendapat response 500. Apakah promise-nya reject?

Tidak. `fetch` hanya reject saat gagal jaringan (atau di-abort). Kamu harus mengecek `response.ok` / `response.status` dan melempar error sendiri.
:::

:::quiz
6 · Sebutkan tiga hal yang akan kamu cek agar sebuah form aksesibel.

Setiap input punya `<label for>` yang terlihat; error diumumkan dan dihubungkan dengan `aria-describedby` + `aria-invalid`; bisa dipakai hanya dengan keyboard; fokus pindah ke error pertama; kontras warna cukup; tidak hanya mengandalkan warna.
:::
::::

:::tip[Menilai dirimu sendiri]
Lulus dengan **5 dari 6** → baca sekilas materinya dan langsung ke latihan. Kalau kamu datang dari Python, materi 04 dan 07 (JavaScript dan async) adalah yang paling penting untuk tidak dilewati.
:::

---
title: "Cek Penempatan Minggu 3"
summary: Component React, props, state, menampilkan list, dan form terkontrol di proyek Next.js — cek apa yang sudah kamu kuasai.
sourceHash: 4fa5938ba652
---

::::placement{id="modules/m4/w3"}
Jawab dari ingatan. Kalau ada istilah yang terasa baru, itu tanda untuk mempelajari materinya.

:::quiz
1 · Apa beda props dan state?

Props adalah input yang diberikan parent ke sebuah component — child hanya membacanya. State adalah data milik component itu sendiri yang berubah seiring waktu lewat setter-nya; mengubahnya membuat component digambar ulang.
:::

:::quiz
2 · Kenapa `items.push(x); setItems(items)` sering tidak memperbarui layar?

Karena mengubah array yang sama, sehingga React melihat array "yang sama" dan bisa melewati penggambaran ulang. Buat array baru: `setItems([...items, x])` atau `setItems(prev => [...prev, x])`.
:::

:::quiz
3 · Kenapa item list butuh `key`, dan kenapa index array adalah key yang buruk saat item bisa dihapus atau diurutkan ulang?

Key memberi tahu React item mana yang mana di antara render. Dengan key berupa index, menghapus item pertama menggeser semua nomornya, sehingga React memberikan state tersimpan milik item yang salah (misalnya teks yang sudah diketik) ke item yang tersisa.
:::

:::quiz
4 · Apa fungsi `"use client"` di proyek Next.js App Router?

Menandai sebuah file (dan yang di-import-nya) sebagai Client Component, sehingga bisa memakai state, effect, handler klik, dan fitur browser. Tanpanya, component adalah Server Component secara default.
:::

:::quiz
5 · Apa itu controlled input?

Input yang `value`-nya berasal dari state React dan diperbarui lewat `onChange`. State React adalah satu-satunya sumber kebenaran.
:::

:::quiz
6 · Apa yang tampil di layar untuk `{count && <span>{count} new</span>}` saat `count` bernilai 0?

`0` — React menampilkan angka 0. Pakai `{count > 0 && …}` atau ternary (`? :`).
:::
::::

:::tip[Menilai dirimu sendiri]
Lulus dengan **5 dari 6** → baca sekilas materinya dan langsung ke latihan. Tetap kerjakan materi 06 (debugging) — sangat membantu di setiap minggu sesudahnya.
:::

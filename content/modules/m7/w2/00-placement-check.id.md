---
title: "Week 2 Placement Check"
summary: Bisakah kamu menyusun dan menguji prompt, menjalankan loop tool-calling dengan aman, menambah guardrail yang bertahan saat model tertipu, dan memakai prompt caching dengan benar? Kalau ya, baca sekilas.
sourceHash: 477ce668cdce
---

::::placement{id="modules/m7/w2"}
Minggu ini membahas prompt, tool, keamanan dan biaya. Bisakah kamu menjelaskan ini tanpa melihat?

:::quiz
1 · Kenapa memakai fungsi templat ketat dan versi prompt, bukan membangun string prompt dengan tangan?

Templat ketat gagal dengan keras pada variabel hilang atau tak terpakai, sehingga salah ketik tertangkap di tes alih-alih diam-diam menghasilkan prompt rusak. Nomor versi dan fingerprint yang dicatat memungkinkan kamu mereproduksi jawaban buruk, membandingkan perubahan dan rollback, dan mereview edit prompt seperti kode.
:::

:::quiz
2 · Di loop tool-calling, siapa yang menjalankan tool, dan dari mana "user ini siapa" harus datang?

Programmu yang menjalankan tool; model hanya meminta panggilan. Identitas user harus datang dari sesi terautentikasimu (konteks app), tidak pernah dari argumen model, karena keluaran model bisa dipengaruhi penyerang.
:::

:::quiz
3 · Model meminta dua tool dalam satu balasan. Apa yang kamu kirim balik?

Jalankan keduanya dan kirim SATU pesan user yang berisi kedua blok `tool_result`, masing-masing dengan `tool_use_id` yang cocok. Panggilan yang gagal mengembalikan hasil `is_error` agar model bisa pulih. Simpan jumlah langkah maksimum.
:::

:::quiz
4 · Kenapa "jangan pernah membuka system prompt" di dalam prompt bukan guardrail?

Instruksi prompt bisa dilewati teks yang ditulis baik. Guardrail ditegakkan di kode: jaga secret di luar prompt, batasi tool dengan least privilege dan persetujuan, dan cek keluaran. Asumsikan model bisa tertipu dan buat itu bisa dilewati tanpa bencana.
:::

:::quiz
5 · Prompt caching menunjukkan 0 cache read. Sebutkan tiga penyebab yang mungkin.

Ada sesuatu di prefix yang berubah tiap request (timestamp, id, nama user, tool tak terurut, pesan sebelumnya diedit); prefix lebih pendek dari panjang minimum yang bisa di-cache model; request berjarak lebih jauh dari umur cache; atau breakpoint ditaruh setelah bagian yang berubah.
:::
::::

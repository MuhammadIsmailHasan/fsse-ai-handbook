---
title: "Week 1 Placement Check"
summary: Bisakah kamu menjelaskan token dan context window, memilih model dengan bukti, memanggil chat API dengan streaming, mendapat JSON terstruktur yang bisa dipercaya, dan menjalankan model lokal? Kalau ya, baca sekilas.
sourceHash: b1a39b8d22b9
---

::::placement{id="modules/m7/w1"}
Minggu ini membahas cara kerja LLM dan cara memanggilnya. Bisakah kamu menjelaskan ini tanpa melihat?

:::quiz
1 · Apa itu token, dan kenapa token (bukan kata) menentukan biaya dan batasmu?

Token adalah potongan kecil teks: satu kata, bagian kata, atau simbol. Penyedia menagih per token untuk masukan dan keluaran, dan context window diukur dalam token. Masukan dan keluaran berbagi jendela yang sama, jadi prompt panjang menyisakan ruang lebih sedikit untuk jawaban, dan keluaran biasanya berharga lebih tinggi daripada masukan.
:::

:::quiz
2 · Jawaban berhenti di tengah kalimat. Apa yang kamu cek, dan apa dua perbaikannya?

Cek `stop_reason`: `"max_tokens"` berarti jawaban mencapai batas keluaran. Perbaikan: naikkan `max_tokens`, minta jawaban lebih pendek, pangkas prompt agar ada ruang, atau tampilkan opsi "lanjutkan".
:::

:::quiz
3 · Bagaimana kamu memilih antara model kecil dan besar untuk fitur baru?

Tulis kebutuhan (standar kualitas, waktu tunggu maksimum, volume, aturan data). Uji 2–3 model pada 20–50 contohmu sendiri dengan prompt yang sama, dan ukur kualitas, biaya per tugas selesai dan latency. Pilih model termurah yang memenuhi standar, dan simpan nama model di konfigurasi agar bisa berganti.
:::

:::quiz
4 · Kenapa chat API mengharuskanmu mengirim seluruh percakapan setiap kali, dan apa harganya?

API stateless: server tidak mengingat apa pun antar panggilan. Kamu yang memegang riwayat dan mengirim semuanya tiap giliran, jadi biaya dan latency tumbuh bersama percakapan. Kamu memangkas giliran lama, meringkas, atau mengambil hanya yang relevan.
:::

:::quiz
5 · Model mengembalikan JSON valid yang cocok dengan schema-mu, tapi id pesanan di dalamnya tidak ada. Apa yang salah, dan apa yang kamu tambahkan?

Schema mengecek bentuk, bukan kebenaran: model mengarang nilai. Tambahkan validasi bisnis di kodemu (cari id di database), izinkan `null` untuk fakta yang hilang, dan perlakukan nilai hasil ekstraksi sebagai masukan tak tepercaya.
:::

:::quiz
6 · Kapan model lokal (misalnya dengan Ollama) pilihan yang baik, dan apa yang tidak boleh dilakukan fallback?

Bagus untuk data privat, pemakaian offline, belajar dan pekerjaan massal murah. Fallback ke API cloud tidak boleh diam-diam mengirim data yang seharusnya tetap privat, dan tidak boleh menyembunyikan bug sungguhan dengan menangkap semua exception.
:::
::::

---
title: "Week 3 Placement Check"
summary: Bisakah kamu menguji app FastAPI dengan TestClient, menyusun proyek nyata, menjalankan pekerjaan setelah response, melakukan streaming response, dan memilih antara Flask dan FastAPI? Kalau ya, baca sekilas.
sourceHash: 6655b16ebc90
---

::::placement{id="modules/m3/w3"}
Minggu ini mengubah demo FastAPI menjadi app sungguhan. Bisakah kamu menjelaskan ini tanpa melihat?

:::quiz
1 · Bagaimana menguji endpoint FastAPI tanpa menjalankan server, dan bagaimana mengganti database asli dengan yang palsu?

Pakai `TestClient(app)` — ia memanggil app langsung, di proses yang sama, lalu kamu cek `status_code` dan `.json()`. Untuk mengganti dependency, isi `app.dependency_overrides[get_db] = fake_get_db` selama tes, lalu bersihkan setelahnya supaya tes berikutnya mulai bersih.
:::

:::quiz
2 · Kenapa app FastAPI sungguhan memecah kode jadi router, service, schema dan model, bukan satu `main.py`?

Tiap file punya satu tugas, jadi satu perubahan tetap di satu tempat dan tiap bagian bisa diuji sendiri. Router mengurus HTTP, service memegang aturan bisnis, schema menjelaskan bentuk request/response, model menjelaskan tabel database. Satu file besar mencampur semuanya dan jadi sulit diubah dan diuji.
:::

:::quiz
3 · Apa yang dilakukan `BackgroundTasks`, dan kapan ia alat yang salah?

Ia menjalankan fungsi **setelah** response dikirim, jadi klien tidak menunggu (misalnya mengirim email selamat datang). Ia salah untuk pekerjaan lambat atau penting yang harus selamat dari crash atau restart, karena tugasnya hidup di dalam proses web. Untuk itu, pakai antrean job sungguhan.
:::

:::quiz
4 · Apa itu streaming response, dan kenapa endpoint AI memakainya?

Streaming response mengirim isi dalam potongan kecil begitu siap, bukan menunggu seluruh jawaban. Endpoint AI men-stream token saat model menghasilkannya, jadi user melihat kata-kata muncul langsung, bukan menatap layar kosong.
:::

:::quiz
5 · Sebutkan satu alasan memilih FastAPI daripada Flask untuk layanan baru, dan satu alasan tetap memakai Flask.

FastAPI: validasi bawaan, dokumen OpenAPI otomatis dan `async` kelas satu, cocok untuk layanan API dan AI. Flask: ekosistem matang dan sederhana, serta codebase yang sudah dikenal timmu — menulis ulang app yang jalan punya biaya nyata.
:::
::::

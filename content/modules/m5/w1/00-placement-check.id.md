---
title: "Placement Check Minggu 1"
summary: Cara kerja container dan cara men-debug-nya, build target, tag image dan registry, image untuk jenis CPU berbeda, Compose untuk full stack, serta caching, rate limiting, dan antrean dengan Redis — cek bagian mana yang bisa kamu lewati.
sourceHash: fd4acd255aca
---

::::placement{id="modules/m5/w1"}
Jawab dari ingatan. Kalau ada istilah yang terasa baru, itu tanda untuk mempelajari materinya.

:::quiz
1 · Sebuah container menampilkan `Exited (137)`. Apa yang terjadi, dan bagaimana mencari tahu penyebabnya?

137 = 128 + 9 → prosesnya menerima **SIGKILL** (dihentikan paksa). Biasanya sistem mematikannya karena memakai memori terlalu banyak ("OOM killer"), atau `docker stop` berhenti menunggu karena aplikasi mengabaikan sinyal sopan SIGTERM. Cek `docker inspect --format '{{.State.OOMKilled}}' <name>`, `docker logs`, `docker stats`, dan apakah aplikasi menangani SIGTERM (CMD bentuk exec).
:::

:::quiz
2 · Kamu build image di Mac Apple Silicon lalu menjalankannya di server EC2 x86: `exec format error`. Kenapa, dan apa dua cara memperbaikinya?

Image-nya dibuat untuk chip ARM (`linux/arm64`), sedangkan server-nya memakai chip Intel/AMD — seperti colokan yang tidak cocok dengan stopkontak. Build untuk target tersebut (`docker buildx build --platform linux/amd64`) atau terbitkan satu image untuk keduanya (`--platform linux/amd64,linux/arm64`) — atau jalankan di server ARM (Graviton).
:::

:::quiz
3 · Kenapa memberi tag image dengan commit SHA Git, bukan hanya `latest`?

Setiap container yang berjalan jadi menunjuk ke source code yang persis; deployment bisa diulang; rollback = deploy tag sebelumnya lagi. `latest` bisa berubah kapan saja, jadi tidak memberi tahu apa yang sebenarnya berjalan.
:::

:::quiz
4 · Di Compose, bagaimana memastikan migrasi database berjalan **sekali** sebelum API dan worker menyala?

Tambahkan service `migrate` sekali jalan yang memakai image yang sama, lalu pasang `depends_on: migrate: condition: service_completed_successfully` di api dan worker (plus `db: condition: service_healthy`).
:::

:::quiz
5 · 10.000 cache key daftar produk kedaluwarsa di detik yang sama dan database tumbang. Sebutkan nama masalahnya dan dua perbaikannya.

**Cache stampede** (thundering herd) — seperti stok semua toko habis bersamaan dan semua pembeli menyerbu satu gudang. Tambahkan **jitter** acak ke waktu kedaluwarsa, pakai **lock** supaya hanya satu request yang membangun ulang sebuah key, sajikan nilai lama sambil memperbarui, atau isi duluan key yang populer.
:::

:::quiz
6 · Kenapa "`LPUSH` untuk menambah job dan `RPOP` untuk mengambilnya" bukan antrean yang andal, dan apa perbaikannya?

Kalau worker crash tepat setelah `RPOP`, job-nya hilang selamanya. Sebaiknya pindahkan job ke daftar "sedang diproses" dalam satu langkah (`BLMOVE`/`LMOVE`), hapus saat selesai, dan kembalikan job yang macet — atau pakai Redis Streams dengan consumer group, atau antrean sungguhan (SQS).
:::
::::

:::tip[Menilai dirimu sendiri]
Lulus dengan **5 dari 6**. Walaupun lulus, tetap kerjakan materi 05 — materi itu menerapkan minggu ini ke **RevoShop milikmu**.
:::

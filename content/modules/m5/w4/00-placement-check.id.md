---
title: "Cek Penempatan Minggu 4"
summary: Frontend di S3, CloudFront atau Amplify, deploy EC2 tanpa downtime, ECS Fargate di belakang load balancer, Lambda job dengan SQS, dan konfigurasi dari Parameter Store dan Secrets Manager — cek apa saja yang bisa kamu lewati.
sourceHash: 252ca092fac1
---

::::placement{id="modules/m5/w4"}
Jawab dari ingatan. Kalau ada kata yang baru untuk kamu, itu tanda untuk pelajari materi itu.

:::quiz
1 · Bisakah aplikasi Next.js App Router dengan Server Actions dan halaman per-pengguna di-host sebagai file di S3 + CloudFront? Apa pilihannya?

Tidak sepenuhnya. Static export hanya file di rak: tidak bisa jalankan Server Actions, baca cookie login, atau buat halaman per request. Pilihanmu: jalankan Node server (ECS/App Runner/EC2 dengan CloudFront di depan), pakai hosting terkelola yang dukung Next.js server rendering (AWS Amplify Hosting, Vercel), atau jaga aplikasi di batas apa yang bisa dilakukan static export.
:::

:::quiz
2 · Deploy EC2-mu membuat ulang container API dan ada error 5–10 detik tiap kali. Sebutkan dua cara untuk hapus downtime itu.

Entah blue/green di server yang sama — jalankan versi baru sebelah versi lama, cek kesehatannya, arahkan reverse proxy ke sana, lalu matikan yang lama — atau jalankan beberapa salinan di belakang load balancer dan ganti satu per satu (ECS rolling deployment, Auto Scaling group).
:::

:::quiz
3 · Di ECS, apa bedanya role **execution** dan role **task** pada task?

Role **execution** punya crew pengiriman: ECS sendiri memakainya untuk tarik image, baca secret untuk inject, dan tulis log. Role **task** adalah lencana yang dipakai **kode aplikasimu** saat panggil AWS API (S3, SQS…).
:::

:::quiz
4 · Bagaimana cara jalankan migrasi database untuk service ECS dengan aman?

Jalankan sekali sebagai task sendiri: `ecs run-task` dengan task definition yang sama tapi perintahnya diganti jadi `flask db upgrade`, tunggu sampai selesai sukses, baru update service. Jangan di startup setiap task, atau salinannya balapan satu sama lain.
:::

:::quiz
5 · Lambda yang konsumsi batch SQS 10 message gagal di message 7. Tanpa konfigurasi ekstra, apa yang terjadi, dan apa jalan keluarnya?

Batch seluruhnya kembali ke antrean, jadi ke-10 message diproses lagi — sembilan di antaranya dua kali. Hidupkan **ReportBatchItemFailures** dan kembalikan hanya ID message yang gagal, buat handler idempotent, dan tambah dead-letter queue untuk message yang terus gagal.
:::

:::quiz
6 · SSM Parameter Store atau Secrets Manager untuk JWT secret dan RDS master password RevoShop?

JWT secret: SecureString di Parameter Store sudah cukup — murah dan sederhana. RDS master password: Secrets Manager, karena RDS bisa buat dan rotate-nya untuk kamu. Entah cara mana, IAM role membaca mereka saat runtime; mereka tidak pernah duduk di image atau sebagai plain text di task definition.
:::
::::

:::tip[Nilai dirimu]
Lulus dengan **5 dari 6**. Semua orang harus kerjakan materi 06 — ia pindahkan **RevoShop-mu** ke ECS.
:::

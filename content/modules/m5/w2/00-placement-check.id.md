---
title: "Cek Penempatan Minggu 2"
summary: Desain pipeline dan metrik DORA, alur kerja build-once-deploy-many di GitHub Actions, environment dengan persetujuan, keamanan secret dan login OIDC ke AWS — periksa mana yang bisa kamu lewati.
sourceHash: ccb146d42e31
---

::::placement{id="modules/m5/w2"}
Jawab dari ingatanmu. Kalau ada kata yang baru buatmu, itu tanda kamu perlu belajar materinya.

:::quiz
1 · Apa bedanya continuous delivery dan continuous deployment?

Continuous **delivery**: setiap perubahan yang lulus pipeline *bisa* dirilis kapan saja, biasanya setelah orang memberi persetujuan. Continuous **deployment**: setiap perubahan yang lulus langsung dirilis ke production secara otomatis, tanpa langkah manual.
:::

:::quiz
2 · Sebutkan empat metrik DORA utama.

Frekuensi deployment, change lead time, change failure rate, dan berapa lama waktu pemulihan dari deployment yang gagal.
:::

:::quiz
3 · Kenapa "build once, deploy many" — dan apa persis yang bergerak dari staging ke production?

**Paket yang sama dan tidak berubah** bergerak maju (image yang dinamai dengan digestnya). Itu diuji di staging lalu di-deploy ke production. Membangun ulang untuk production bisa menghasilkan image yang berbeda — versi dependency baru, base image baru — daripada image yang benar-benar sudah kamu uji.
:::

:::quiz
4 · Bagaimana sebuah langkah workflow bisa diserang lewat teksnya sendiri, dan bagaimana mencegahnya?

`run: echo "${{ github.event.pull_request.title }}"` menempel teks yang ditulis orang asing ke perintah shell sebelum dijalankan, jadi judul PR yang dirancang jahat bisa menjalankan perintah. Lewatkan nilai yang tidak terpercaya melalui `env:` dan gunakan `"$TITLE"` di dalam script; juga berikan workflow `permissions` terkecil yang dibutuhkan.
:::

:::quiz
5 · Kenapa OIDC lebih baik daripada menyimpan `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY` sebagai GitHub secret, dan apa bagian paling penting dari IAM trust policy?

Tidak ada kunci jangka panjang yang bisa bocor atau perlu dirotasi — GitHub menukar token yang ditandatangani jangka pendek dengan kredensial sementara. Di trust policy, kondisi `sub` harus menyebutkan **repository mana dan branch atau environment mana** yang boleh memakai role (jangan `repo:owner/*` atau `*`).
:::

:::quiz
6 · Apa yang seharusnya diberikan GitHub **environment** bernama `production` kepadamu?

Peninjau yang wajib (persetujuan), aturan tentang branch atau tag mana yang boleh deploy, secret dan variable yang ada hanya untuk environment itu, dan catatan deployment — plus concurrency group sehingga dua deploy tidak pernah berjalan bersamaan.
:::
::::

:::tip[Nilai sendiri]
Lolos dengan **5 dari 6**. Semua orang harus mengerjakan materi 05 — ia menghubungkan **RevoShop-mu** ke pipeline asli.
:::

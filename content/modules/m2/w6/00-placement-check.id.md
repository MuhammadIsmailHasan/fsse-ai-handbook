---
title: "Cek Penempatan Minggu 6"
summary: Testing, load testing, secret, deployment, container, CI, dan logging — bisakah kamu ship dan operasikan API yang kamu bangun?
sourceHash: c8ba8700d451
---

::::placement{id="modules/m2/w6"}
Pertanyaan-pertanyaan ini memisahkan "jalan di laptopku" dari "jalan di production".

:::quiz
1 · Test integrasi-mu pakai SQLite, production memakai PostgreSQL. Sebutkan dua bug yang bisa lolos.

Perilaku khusus PostgreSQL tidak teruji: operator `ILIKE`, `JSONB`, handling timezone (`timestamptz`), constraint `CHECK`/panjang yang ditegakkan (yang diabaikan SQLite), perilaku concurrency/locking, case-sensitivity perbandingan, dan SQL `ON CONFLICT`/`FOR UPDATE`. Tes pakai engine database yang sama (misalnya PostgreSQL di Docker atau container service CI).
:::

:::quiz
2 · Apa yang membuat unit test bagus? Sebutkan tiga sifatnya.

Cepat, terisolasi/deterministik (tanpa network, waktu tetap, tanpa shared state), menguji satu perilaku dengan nama yang jelas, mengikuti Arrange–Act–Assert, dan gagal karena bug sungguhan (bukan refactor yang tidak membahayakan).
:::

:::quiz
3 · Di jalannya Locust, RPS stabil tapi p95 latency naik dari 120 ms menjadi 2 s saat user bertambah. Apa yang disarankan dan apa yang kamu cek?

Sistem sudah penuh (saturated): request mengantri. Cek CPU, koneksi DB/batas pool, query lambat (`pg_stat_statements`, `EXPLAIN`), worker/thread Gunicorn, dan panggilan eksternal; temukan bottleneck sebelum menambah server.
:::

:::quiz
4 · Di mana `JWT_SECRET_KEY` seharusnya berasal di production, dan apa yang harus dilakukan app jika hilang?

Dari environment variable / secret manager yang disuntikkan platform — jangan pernah di code atau git. App harus **menolak untuk mulai** (fail fast) daripada jatuh ke default.
:::

:::quiz
5 · Bagaimana caramu menjalankan Flask di production, dan kenapa bukan `flask run`?

Di balik WSGI server production seperti Gunicorn (worker, timeout, restart yang elegan), biasanya di balik reverse proxy/load balancer yang menangani TLS. `flask run` adalah server development single-process tanpa hardening production.
:::

:::quiz
6 · Apa yang harus dilakukan CI pipeline untuk API ini di setiap pull request?

Install dependency terkunci, cek lint/format, type check, jalankan test terhadap service PostgreSQL dengan migrasi sudah diterapkan, mungkin security scan (audit dependency, scanning secret) — dan blokir merge kalau ada yang gagal.
:::
::::

:::tip[Nilai dirimu sendiri]
Lulus dengan **5 dari 6**. Pertanyaan 1 terutama relevan untuk test RevoShop-mu.
:::

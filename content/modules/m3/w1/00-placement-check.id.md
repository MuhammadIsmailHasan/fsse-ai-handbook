---
title: "Week 1 Placement Check"
summary: Apakah kamu sudah tahu kenapa FastAPI ada, bagaimana Pydantic memvalidasi data, cara kerja param path/query/body, dan dari mana docs otomatis berasal? Kalau ya, baca sekilas saja.
sourceHash: ff3a9e0a445c
---

::::placement{id="modules/m3/w1"}
Kamu sudah membangun API RevoShop dengan Flask. FastAPI melakukan tugas yang sama dengan tipe dan docs otomatis. Bisakah kamu menjelaskan ini tanpa melihat?

:::quiz
1 · Apa yang FastAPI beri "gratis" yang Flask biasa tidak?

Validasi request otomatis dan docs API interaktif (Swagger UI / OpenAPI), keduanya dihasilkan dari **type hint** Python dan model Pydantic-mu — plus dukungan `async` kelas satu. Kamu mendeklarasikan bentuk datamu sekali, dan FastAPI memvalidasi input serta mendokumentasikan endpoint untukmu.
:::

:::quiz
2 · Apa itu model Pydantic, dan apa yang terjadi saat data tak cocok dengannya?

Sebuah kelas yang menggambarkan bentuk dan tipe data yang diharapkan (field, tipe, batasan). Saat JSON masuk tak cocok, Pydantic melempar error validasi dan FastAPI mengembalikan `422 Unprocessable Entity` dengan pesan jelas menyebutkan field mana yang salah — kamu tak menulis kode pengecekan itu sendiri.
:::

:::quiz
3 · Di `@app.get("/items/{item_id}")` dengan `def read(item_id: int, q: str | None = None)`, mana param path dan mana param query?

`item_id` adalah parameter **path** (muncul di jalur URL `/items/{item_id}`), dan `q` adalah parameter **query** (argumen fungsi yang tak ada di path, jadi datang dari query string seperti `?q=phone`). FastAPI memutuskan ini dengan mencocokkan nama argumen ke path.
:::

:::quiz
4 · Dari mana halaman `/docs` berasal, dan kenapa berguna?

FastAPI menghasilkan skema OpenAPI dari route dan model Pydantic-mu, dan menyajikan Swagger UI interaktif di `/docs` otomatis. Ia membuatmu (dan rekan frontend) bisa melihat tiap endpoint, input/output-nya, dan mencoba request di browser — tanpa dokumentasi terpisah untuk dipelihara.
:::

:::quiz
5 · Kamu sudah tahu Flask. Kapan memakai FastAPI sepadan, dan kapan Flask cukup?

FastAPI bersinar saat kamu ingin validasi dan docs otomatis, keamanan tipe, dan banyak I/O `async` (banyak panggilan eksternal bersamaan). Flask cukup baik untuk aplikasi lebih sederhana atau basis kode Flask yang sudah ada. Keduanya solid; FastAPI menukar sedikit pengetikan di awal untuk validasi dan docs yang tak perlu kamu tulis.
:::
::::

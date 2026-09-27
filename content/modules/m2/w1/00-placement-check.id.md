---
title: "Cek Penempatan Minggu 1"
summary: Periksa peralatan engineering sehari-hari kamu — terminal, Git, Markdown, virtual environment, dan Docker — dalam 20 menit.
sourceHash: 12fda7584bf2
---

::::placement{id="modules/m2/w1"}
Mungkin kamu sudah pakai alat-alat ini di RevoShop. Cek ini menanyakan apakah kamu bisa **menjelaskan** mereka — tidak hanya mengetik perintahnya.

:::quiz
1 · Apa bedanya `git add`, `git commit`, dan `git push`?

`add` memindahkan perubahan ke **staging area** (memilih apa yang masuk ke commit berikutnya). `commit` menyimpan snapshot dari perubahan yang sudah di-stage di **history lokal** kamu dengan pesan. `push` mengunggah commit lokal kamu ke **repository remote** (misalnya GitHub).
:::

:::quiz
2 · Pull request teman kamu punya merge conflict di `app/routes/products.py`. Apa maksudnya dan bagaimana kamu menyelesaikannya?

Kedua branch mengubah baris yang sama dengan cara berbeda, jadi Git tidak bisa memilih. Update branch kamu (`git pull`/`git merge main` atau rebase), buka file itu, pilih kombinasi yang benar di antara marker `<<<<<<<`, `=======`, `>>>>>>>`, hapus marker-nya, jalankan test, lalu `git add` dan commit (atau lanjutkan rebase).
:::

:::quiz
3 · Kenapa proyek Python pakai virtual environment, dan file apa yang mencatat dependency-nya?

Supaya setiap proyek punya versi package sendiri yang terisolasi dan tidak merusak proyek lain atau Python sistem. Dependency dicatat di `pyproject.toml` (plus lock file seperti `uv.lock`), atau `requirements.txt` di setup yang lebih lama.
:::

:::quiz
4 · Di terminal, bagaimana caranya mencari setiap file `.py` di bawah `app/` yang memuat teks `jwt_required`?

`grep -rn "jwt_required" app --include="*.py"` (atau `rg jwt_required app` dengan ripgrep).
:::

:::quiz
5 · Apa bedanya **image** Docker dan **container**?

Image adalah **template** yang read-only (aplikasi + lingkungannya, dibangun dari Dockerfile). Container adalah **instance yang sedang jalan** dari sebuah image. Satu image bisa jalan sebagai banyak container.
:::

:::quiz
6 · Sebutkan tiga hal yang tidak boleh pernah di-commit ke Git.

Secret (`.env`, API key, password, private key), folder yang di-generate/besar (`node_modules/`, `.venv/`, `__pycache__/`, build output), dan file personal/OS (`.DS_Store`, pengaturan editor) — plus data user yang asli.
:::
::::

:::tip[Nilai dirimu sendiri]
Lulus dengan **5 dari 6** dijawab dengan benar. Kalau kamu hanya tahu perintahnya tapi bukan *alasannya*, pelajari minggu ini — pendek dan sangat berguna setiap hari.
:::

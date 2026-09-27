---
title: "Cek Penempatan Minggu 5"
summary: Uji pemahaman desain API-mu — resource dan method, pagination, validasi dan status code, JWT auth, otorisasi, dokumentasi dan webhook.
sourceHash: 8adc640d254f
---

::::placement{id="modules/m2/w5"}
RevoShop punya JWT, role, dokumentasi Swagger dan webhook Midtrans. Bisakah kamu jelaskan *kenapa* masing-masing diperlukan?

:::quiz
1 · Rancang endpoint untuk menandai aplikasi nomor 42 sebagai ditarik kembali (withdrawn). Method dan path mana, dan apa terjadi kalau client mengirim ulang request yang sama setelah timeout?

Gunakan `PATCH /api/v1/applications/42` dengan `{"status": "withdrawn"}` atau endpoint aksi `POST /api/v1/applications/42/status`. Operasi harus **idempotent** — menarik kembali aplikasi yang sudah ditarik mengembalikan status akhir yang sama (200), bukan error atau baris history baru — atau client mengirim `Idempotency-Key`.
:::

:::quiz
2 · Offset pagination (`?page=500`) lambat dan menghasilkan duplikat saat baris baru tiba. Alternatif apa?

Keyset (cursor) pagination: `WHERE (created_at, id) < (:last_created_at, :last_id) ORDER BY created_at DESC, id DESC LIMIT 20`, mengembalikan `next_cursor` yang tidak terbaca manusia.
:::

:::quiz
3 · `400`, `401`, `403`, `404`, `409`, `422` — berikan satu contoh satu baris untuk masing-masing.

400 JSON tidak terbentuk dengan benar · 401 token hilang/kadaluarsa · 403 sudah login tapi tidak boleh (pembeli mengedit produk) · 404 resource tidak ada (atau milik orang lain) · 409 bertentangan dengan keadaan saat ini (duplikat, transisi tidak sah) · 422 terbentuk baik tapi field tidak sah.
:::

:::quiz
4 · Apa yang ada di dalam JWT, dan kenapa kamu tidak bisa menempatkan password user atau perubahan role yang perlu dicabut langsung di dalamnya?

Header, payload dengan claim (`sub`, `exp`, custom claim seperti `role`) dan signature — **signed, bukan encrypted**, jadi siapa pun bisa baca payload-nya. Server mempercayainya sampai kadaluarsa, jadi mencabut atau mengubah role tidak berlaku sampai kadaluarsa kecuali kamu menambah denylist/lifetime pendek + refresh token.
:::

:::quiz
5 · Authentication vs authorization — dan di mana kamu mengecek "pesanan ini milik user saat ini"?

Authentication = siapa kamu; authorization = apa yang boleh kamu lakukan. Kepemilikan adalah authorization dan harus di service/query (`WHERE user_id = :current_user`), bukan hanya di frontend.
:::

:::quiz
6 · Payment provider mengirim webhook. Sebutkan tiga hal yang endpoint-mu harus lakukan.

Verifikasi **signature** (tolak yang unsigned/lama), proses **idempotent** (event yang sama bisa tiba berkali-kali), jawab **dengan cepat** dengan 2xx dan kerjakan yang berat asinkron — plus log dan tangani event yang urut-urutan salah.
:::
::::

:::tip[Penilaian diri sendiri]
Lulus dengan **5 dari 6**. Kalau kamu sudah membuat fitur ini dengan bantuan AI, pelajari materi ini juga — penanya di wawancara selalu dalami auth dan webhook.
:::

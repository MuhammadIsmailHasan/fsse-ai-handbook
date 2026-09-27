---
title: "🎤 Pertahankan RevoShop-mu"
summary: Wawancara teknis simulasi tentang proyek backend-mu sendiri — jelaskan setiap keputusan, temukan titik lemahnya sebelum pewawancara, dan ubah menjadi daftar perbaikan serta presentasi proyek yang percaya diri.
sourceHash: 2b0431a3c6ca
---

## 🎯 Kenapa sesi ini ada

Dalam wawancara, pertanyaan backend yang paling sering bukan soal LeetCode. Pertanyaannya:

> *"Jelaskan proyek yang pernah kamu buat. Kenapa kamu mendesain seperti itu? Apa yang akan rusak duluan?"*

Banyak dari RevoShop dihasilkan dengan Kiro. Itu normal di 2026 — perusahaan **mengharapkan** kamu memakai alat AI. Tapi mereka juga **mengharapkan** kamu bisa menjelaskan, membela, dan memperbaiki setiap baris kode dengan nama kamu. Kalau tidak bisa, proyek malah merugikan kamu.

Sesi ini mengubah RevoShop dari "kode yang aku punya" menjadi "sistem yang aku pahami".

Pikirkan seperti tes berkendara: kamu sudah berkendara setiap hari, tapi sekarang seseorang bertanya *kenapa* kamu cek spion itu. Tahu jawabannya adalah apa yang mengubah sopir jadi sopir berlisensi.

:::warning[Aturan mainnya]
1. 🚫🤖 **Tidak boleh AI** saat menjawab. Buka kode, baca, jawab dengan kata-katamu sendiri.
2. **Jawab dengan bersuara** (atau buat voice memo), lalu tulis 3–5 poin. Berbicara mengungkap celah yang tidak terlihat saat baca diam-diam.
3. Setiap jawaban harus menunjuk ke **sebuah file dan baris** di RevoShop.
4. Kalau tidak tahu: tulis "Aku belum tahu", cari tahu, baru jawab. Itu poinnya.
5. Baru setelah satu bagian selesai, lihat panduan dan nilai dirimu.
:::

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Technical interview** | Percakapan di mana kamu menjelaskan dan membela cara sesuatu bekerja |
| **Project walkthrough** | Menceritakan kisah proyek-mu: masalah, desain, hasil |
| **Trade-off** | Apa yang kamu lepas untuk mendapat sesuatu yang lain |
| **Design decision** | Pilihan yang kamu buat dengan sengaja, punya alasan |
| **D-T-C** | Decision → Trade-off → Change: bentuk jawaban yang bagus |
| **Weak spot** | Bagian yang kamu tahu belum cukup baik |
| **Improvement backlog** | Daftar milikmu sendiri apa yang harus diperbaiki, berurutan |
| **Pitch** | Ringkasan singkat dan jelas tentang proyek untuk seseorang yang baru |

## 🧭 Cara menjawab: kerangka D-T-C

Untuk setiap pertanyaan "kenapa", jawab dalam tiga bagian:

| Bagian | Pertanyaan | Contoh |
|---|---|---|
| **D**ecision (Keputusan) | Apa yang kita buat? | "Total pesanan adalah kolom `Numeric(14, 2)`." |
| **T**rade-off | Kenapa ini dan bukan yang lain? | "Float tidak bisa tepat mewakili 0.1; uang harus tepat. Biayanya adalah konversi yang hati-hati di JSON." |
| **C**hange (Ubah) | Apa yang akan aku perbaiki sekarang, tahu lebih banyak? | "`to_dict()` konversi ke `float` — aku akan serialisasi sebagai string atau integer rupiah." |

Pewawancara senang bagian **C**: itu menunjukkan penilaian dan pertumbuhan. "Aku akan ubah X karena Y" lebih baik daripada pura-pura semuanya sempurna — tidak ada yang percaya proyek tanpa titik lemah, dan bilang satu titik lemah membuat jawaban-jawaban kamu yang lain lebih kredibel.

## 🗺️ Bagian 1 — Presentasi 2 menit

Tulis dan latihan presentasi memakai struktur ini. Waktu dirimu: **di bawah 2 menit**.

1. **Apa & siapa** — satu kalimat: apa yang RevoShop lakukan dan untuk siapa.
2. **Arsitektur** — lapisan-lapisannya (routes → services → repositories → models), PostgreSQL, JWT auth, Midtrans payment.
3. **Satu masalah sulit** yang kamu selesaikan (misalnya webhook payment, penanganan stok, izin peran).
4. **Kualitas** — test (berapa banyak, jenis apa), tes beban Locust, Docker, logging.
5. **Apa yang akan kamu lakukan selanjutnya** — satu perbaikan yang jujur.

Lalu gambar arsitektur **dari memori** di kertas: client, Gunicorn, Flask app layers, PostgreSQL, Midtrans (pengalihan checkout + webhook). Bandingkan dengan kode sesudahnya.

## 🔍 Bagian 2 — Pertahankan, topik demi topik

Untuk setiap pertanyaan: jawab dulu, baru buka panduan.

### A. Struktur proyek & arsitektur (W3–W4)

1. Lacak `POST /api/v1/orders` dari route ke database. Sebutkan setiap file yang dilewatinya.
2. Kenapa route memanggil service, dan service memanggil repository? Apa biaya route yang query DB langsung?
3. `create_app()` memilih config dari `FLASK_ENV`. Apa defaultnya, dan kenapa itu berisiko di server?

:::quiz
Panduan untuk A

1. `app/routes/orders.py` (parse & validasi dengan marshmallow schema, dapat identitas JWT) → `app/services/order_service.py` `OrderService.create` (resolusi alamat, pencarian produk, cek stok, snapshot harga) → `app/repositories/order_repository.py` `OrderRepository.create` (buat order + item, kurangi stok, commit) → model di `app/models/orders.py`. Jawaban yang kuat juga menyebut jalur error: service exception → handler di `app/errors.py` → JSON error.
2. Pemisahan tanggung jawab (pelajaran Week 4 lesson 06): detail HTTP tinggal di route, aturan bisnis di service (bisa ditest tanpa HTTP), persistensi di repository (bisa diganti, bisa di-mock). Biaya kalau dilewat: aturan diduplikasi di banyak endpoint, kode sulit ditest, SQL tersebar di mana-mana. Trade-off jujur: lebih banyak file/indirection untuk aplikasi kecil.
3. Default adalah `'development'` (DEBUG on, SQL echo). Deploy Procfile/PaaS tanpa `FLASK_ENV` menjalankan config development di production. Lebih baik: berhenti cepat kalau environment tidak diatur dengan jelas, dan jangan andalkan `FLASK_ENV` (Flask hapus makna bawaan di 2.3) — pakai `APP_ENV` punya kamu sendiri (pelajaran 04).
:::

### B. Database & integritas data (W2, W4)

4. Kenapa `price` adalah `Numeric(11, 2)` bukan `Float`? Lihat `to_dict()` — apakah respons API masih tepat?
5. Dua pembeli pesan **item terakhir** di saat yang sama. Jelajahi `OrderService.create` dan `OrderRepository.create`: apakah stok bisa negatif atau terjual lebih? Buktikan.
6. Kenapa `order_items` simpan `unit_price` daripada selalu baca `products.price`?
7. Kolom mana yang punya index? Pilih satu endpoint list dan jelaskan apakah query-nya pakai index (`EXPLAIN`).

:::quiz
Panduan untuk B

4. Aritmetika desimal yang tepat untuk uang; float kumpulkan kesalahan pembulatan biner. Tapi `to_dict()` kembalikan `float(self.price)`, jadi klien JSON dapat float — baik untuk tampilan, berisiko kalau klien lakukan aritmetika. Perbaikan: serialisasi sebagai string (`"150000.00"`) atau simpan integer rupiah.
5. **Race condition.** Service baca `product.stock` dan cek `stock < quantity` di Python; repository lalu buat `product.stock -= quantity`. Dua transaksi bisa baca stock = 1, kedua lolos cek, kedua tulis 0 → **oversold** (lost update). `products.stock` tidak punya constraint `CHECK (stock >= 0)`, jadi database tidak menghentikan juga (dan CHECK saja tidak cegah lost update). Perbaikan (Week 2 transaction): `SELECT … FOR UPDATE` di baris produk (urutan konsisten untuk hindari deadlock), atau UPDATE bersyarat atom `UPDATE products SET stock = stock - :q WHERE id = :id AND stock >= :q` dan cek jumlah baris terdampak. Buktikan dengan tes concurrency di PostgreSQL (pelajaran 02 design exercise) — bukan di SQLite.
6. **Price snapshot**: pesanan harus simpan harga yang pembeli sepakati, sekalipun penjual ubah harga nanti. Juga diperlukan untuk receipt yang akurat, refund, dan laporan.
7. Cek `index=True` di model, `Index(...)`, dan migrasi. Misalnya, listing pesanan pembeli filter `user_id` dan sort `id`/`created_at` — tanpa index di `(user_id, created_at)` jadi sequential scan saat pesanan bertambah. Jalankan `EXPLAIN ANALYZE` dengan data seeded dan tunjukkan rencana.
:::

### C. Desain API & validasi (W5)

8. Pilih tiga endpoint dan jelaskan status code untuk sukses dan dua error setiap.
9. Apa yang terjadi kalau klien kirim field tidak dikenal atau quantity negatif saat buat order? Tunjukkan schema yang putuskan.
10. Bagaimana pagination bekerja di `GET /products`? Apa yang terjadi di halaman 5.000?

:::quiz
Panduan untuk C

8. Cari 201 + resource dibuat di create, 200 di read/update, 204 atau 200 di delete, 400/422 untuk validasi, 401 token hilang/tidak sah, 403 peran/kepemilikan salah, 404 tidak ada, 409 konflik (email duplikat, transisi status tidak sah, stok tidak cukup). Siap membela 404-vs-403 untuk pesanan pengguna lain (sembunyikan keberadaan vs kejelas — Week 5 pelajaran 06).
9. Marshmallow 4 raise di field tidak dikenal secara default (`RAISE`); `validate.Range(min=1)` di quantity harus tolak ≤ 0. Buka schema di `app/schemas/` dan verifikasi — kalau aturan hilang, itu item untuk backlog-mu.
10. `page`/`limit` → `OFFSET (page-1)*limit`. Halaman dalam jadi lambat karena PostgreSQL masih jalan di baris yang dilewat, dan hasil bisa bergeser saat produk baru disisipi. Mitigasi: batas `limit`, keyset (cursor) pagination untuk infinite scroll (Week 5 pelajaran 01).
:::

### D. Autentikasi, otorisasi & pembayaran (W5)

11. Bagaimana password disimpan? Kenapa bcrypt dan bukan SHA-256?
12. Pengguna klik "logout". Apakah access token mereka masih bisa dipakai? Berapa lama? Apa yang akan kamu tambahkan?
13. Bagaimana kamu pastikan pembeli tidak bisa baca pesanan pembeli lain?
14. Midtrans panggil endpoint notifikasi-mu. Bagaimana kamu tahu request benar dari Midtrans? Apa kalau notifikasi yang sama datang dua kali?

:::quiz
Panduan untuk D

11. `bcrypt.hashpw` dengan per-password salt (`app/auth.py`). bcrypt **lambat sengaja** dengan work factor, jadi brute-force hash yang bocor mahal; SHA-256 cepat (miliaran tebakan per detik di GPU). Alternatif: Argon2id (rekomendasi pertama OWASP).
12. Tidak ada token blocklist/revocation di RevoShop, jadi access token tetap sah sampai expire (`ProductionConfig`: 15 menit; `BaseConfig`: 1 jam — perhatikan **sama** `JWT_ACCESS_TOKEN_EXPIRES` berarti *jam* di satu class dan *menit* di class lain, bug unit menunggu terjadi), dan refresh token berhari-hari. Perbaikan: access token berumur pendek + daftar revocation (Redis/DB dengan `jti`) dicek dengan `token_in_blocklist_loader`, revoke refresh token saat logout (Week 5 pelajaran 05).
13. Service dapat `user_id` dan `role` dan filter/cek kepemilikan (`OrderService.get_by_id(order_id, user_id, role)`). Sebut test yang buktikan (tes integrasi dengan dua pembeli), dan bahwa cek tinggal di service, tidak cuma di frontend.
14. `PaymentService.verify_signature` hitung ulang `SHA512(order_id + status_code + gross_amount + server_key)` dan bandingkan dengan `hmac.compare_digest` (constant time) ✅. Untuk duplikat: cek bagaimana `handle_notification` berperilaku saat status tidak berubah atau mundur — idempotency harus dari aturan transisi status saat ini atau simpan id notifikasi yang diproses. Juga: selalu verifikasi ulang jumlah, dan pertimbangkan panggil Midtrans status API untuk transisi kritis (Week 5 pelajaran 08).
:::

### E. Kualitas & operasi (W6)

15. Test-mu memakai SQLite di memory. Sebut satu perilaku RevoShop yang lolos di test dan gagal di PostgreSQL.
16. Test Locust-mu ukur apa, melawan server mana, dan berapa p95 endpoint terlambe-mu? Apa bottleneck-nya?
17. Apa yang terjadi kalau production menyala tanpa `JWT_SECRET_KEY`?
18. Jelaskan setup Docker-mu: image, user, bagaimana migrasi jalan, apa yang terjadi dengan 3 replika.
19. Pelanggan bilang "checkout aku gagal jam 14:02". Bagaimana kamu temukan apa yang terjadi?

:::quiz
Panduan untuk E

15. Race condition stok (SQLite serialisasi write berbeda; tidak ada `FOR UPDATE`), presisi `Numeric` dan constraint `CHECK`, case sensitivity dalam pencarian (`LIKE` vs `ILIKE`), penanganan timezone, batas panjang string. Perbaikan: jalankan test di PostgreSQL di Docker/CI (pelajaran 02 dan 07).
16. README arahkan Locust ke `127.0.0.1:5000` — **dev server**. Jawaban jujur: "angka-angka itu tidak representative production; aku jalankan ulang melawan Gunicorn dan dapat …". Lalu sebut bottleneck dengan bukti (query plan lambat, worker kepenuhan, latency panggil Midtrans). Kalau belum jalankan ulang, lakukan sekarang.
17. `BaseConfig` jatuh kembali ke `'super-secret-key-change-in-production'` — aplikasi akan menyala dengan secret publik, jadi siapa pun bisa forge token admin. `docker-compose.prod.yml` lindungi jalur itu dengan `${JWT_SECRET_KEY:?}`, tapi jalur Procfile tidak. Perbaikan: pengaturan berhenti-cepat (pelajaran 04).
18. Single-stage `python:3.12-slim`, dependensi install sebelum `COPY . .` ✅, non-root `appuser` ✅, exec-form CMD ✅; `entrypoint.sh` tunggu dengan netcat dan jalankan `flask db upgrade` di **setiap** container start — dengan 3 replika, tiga migrasi concurrent. `GUNICORN_WORKERS` di compose diabaikan karena CMD hardcode `--workers 3`. Perbaikan: migrasi sebagai release step, `gunicorn.conf.py` dari env, HEALTHCHECK, log ke stdout (pelajaran 05–06).
19. Hari ini: text log di `logs/app.log` tanpa request id — susah. Jawaban lebih baik: JSON log ke stdout dengan request id, error response tampilkan reference id, cari log dengan id itu dan `user_id` + time window, cek log notifikasi Midtrans untuk pesanan itu (pelajaran 08).
:::

### F. Pertanyaan tentang AI

20. *"Apa kamu yang tulis ini?"* Persiapkan jawaban jujur dan percaya diri.

:::quiz
Panduan untuk F

Jangan sembunyikan, dan jangan minta maaf. Jawaban yang kuat:

> "Aku membangunnya di bootcamp memakai Kiro untuk spec-driven development — aku tulis requirement dan steering rule, dan hasilkan banyak dari implementasi pertama. Sesudahnya aku review mendalam: misalnya aku temukan stock check punya race condition dan perbaiki dengan row lock plus test concurrency di PostgreSQL, dan aku pindahkan test dari SQLite ke Postgres. Aku bisa jalan-jalan kamu melalui bagian mana pun."

Itu tunjukkan: kamu pakai tool modern, kamu punya hasil itu, dan kamu bisa temukan dan perbaiki masalah nyata. Klaim itu kredibel hanya kalau kamu **bisa** jalan-jalan melalui bagian mana pun — itu sebabnya sesi ini ada.
:::

## 📋 Bagian 3 — Nilai dirimu sendiri

Untuk setiap 20 pertanyaan beri dirimu sendiri:

| Skor | Artinya |
|---|---|
| **2** | Jawab tanpa cari, tunjuk ke kode, sertakan trade-off |
| **1** | Perlu baca kode dulu, atau jawab kurang trade-off/perbaikan |
| **0** | Belum bisa jawab |

| Total | Di mana kamu |
|---|---|
| 34–40 | Siap wawancara proyek ini. Poles pitch dan README. |
| 22–33 | Solid. Pelajari ulang topik yang 0/1, baru ulangi pertanyaan itu dalam seminggu. |
| < 22 | Normal untuk proyek buatan AI. Kerjakan backlog di bawah — setiap perbaikan ajarkan konsep untuk nyata. |

Tambahkan setiap pertanyaan 0 atau 1 ke **antri review** (tandai pelajaran terkait selesai-tapi-review) jadi spaced repetition bawa mereka kembali.

## 🛠️ Bagian 4 — Daftar perbaikan RevoShop-mu

Setiap titik lemah yang kamu temukan sekarang adalah tugas, bukan kekhawatiran. Daftar yang tertulis juga adalah jawaban wawancara: ia tunjukkan kamu tahu posisi proyek.

Ubah titik lemah menjadi GitHub issue di repo RevoShop-mu. Backlog yang disarankan — pilih setidaknya **tiga** untuk kerjakan sendiri (No-AI untuk draft pertama):

- [ ] **Perbaiki race condition stok** dengan `FOR UPDATE` atau UPDATE bersyarat, plus test checkout concurrent *(M2 W2 L07, W6 L02)*
- [ ] **Jalankan test di PostgreSQL** (Docker lokal + layanan CI) *(W6 L02, L07)*
- [ ] **Pengaturan berhenti-cepat**: tanpa default JWT secret, environment eksplisit *(W6 L04)*
- [ ] **Revocation token saat logout** *(W5 L05)*
- [ ] **Serialisasi uang** sebagai string atau integer rupiah *(M2 W3 data types)*
- [ ] **GitHub Actions CI**: lint, audit, test di Postgres, Docker build *(W6 L07)*
- [ ] **Migrasi sebagai release step**, `gunicorn.conf.py`, `HEALTHCHECK` *(W6 L05, L06)*
- [ ] **JSON log ke stdout** dengan request id; stop log DB error param *(W6 L08)*
- [ ] **Jalankan Locust ulang melawan Gunicorn**, catat p95 per endpoint di README *(W6 L03)*
- [ ] **Bagian "Design decisions" README** memakai D-T-C untuk 5 keputusan kunci

Setiap item diperbaiki jadi kisah wawancara nyata: *"Aku temukan X, ukur, perbaiki dengan Y, dan buktikan dengan test Z."*

:::tip[Signal portofolio]
Pull request berjudul "fix: prevent overselling with row-level locks (+ concurrent checkout test)" lebih kesan kepada hiring manager daripada sepuluh endpoint baru.
:::

## ✅ Selesai jika

- [ ] Pitch direkam dalam di bawah 2 menit
- [ ] Arsitektur digambar dari memori
- [ ] Semua 20 pertanyaan dijawab dengan bersuara dengan referensi file dan dinilai
- [ ] Setidaknya 3 item backlog dibuka sebagai issue, dan 1 diperbaiki dan di-merge
- [ ] README punya bagian "Design decisions"

## 📣 Akhir Minggu 6 — bagikan progresmu

:::linkedin{type="weekly"}
🚢 Minggu 6: dari "jalan di laptop aku" ke siap production.

- Tulis test yang dinilai oleh *mutant* — salinan kode buatan cacat — untuk buktikan test-ku catch bug
- Tes beban API dengan Locust dan pelajari kenapa p95 penting daripada rata-rata
- Bangun pipeline CI dengan GitHub Actions: lint, type, test di PostgreSQL sungguhan, Docker build
- Deploy image Docker multi-stage, non-root dengan health check dan JSON log dengan request id

Lalu aku buat mock interview di backend e-commerce-ku sendiri dan temukan race condition yang bisa oversell item stok terakhir. Memperbaikinya ajarkan aku lebih banyak daripada bangun feature. [link ke PR-mu]

#Python #Flask #DevOps #Testing #LearningInPublic
:::

:::linkedin{type="reflection"}
🎓 Module 2 (Backend Development) selesai.

Apa yang aku bangun: [RevoShop — e-commerce API dengan X endpoint, JWT auth, Midtrans payment, Y test].
Bagian tersulit: [misalnya bikin webhook payment idempotent / memahami transaction].
Apa yang akan aku lakukan beda: [misalnya test di PostgreSQL sejak hari pertama].
Skill yang paling aku bangga: menjelaskan *kenapa* setiap keputusan desain dibuat — bukan cuma bahwa ia jalan.

Selanjutnya: frontend dengan React & TypeScript. 🚀

#BackendDevelopment #Python #PostgreSQL #LearningInPublic
:::

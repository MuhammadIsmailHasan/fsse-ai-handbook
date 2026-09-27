---
title: "Cek Penempatan Minggu 2"
summary: Bisakah kamu merancang tabel, menulis query dengan join dan agregat, serta menjelaskan index dan transaksi? Cek dalam 25 menit.
sourceHash: ce81130fbfe2
---

::::placement{id="modules/m2/w2"}
Tulis SQL di kertas atau di file scratch — jangan jalankan sampai kamu jawab semuanya.

:::quiz
1 · Rancang tabel untuk: pengguna bisa menyimpan banyak job listing, dan satu job listing bisa disimpan banyak pengguna, dengan catatan **kapan** disimpan.

Tiga tabel: `users(id PK, …)`, `jobs(id PK, …)`, dan tabel junction `saved_jobs(user_id FK → users, job_id FK → jobs, saved_at timestamptz NOT NULL DEFAULT now(), PRIMARY KEY (user_id, job_id))`. Primary key gabungan mencegah menyimpan job yang sama dua kali.
:::

:::quiz
2 · Tulis query: berapa banyak aplikasi per status untuk user 7, status paling sering dulu.

```sql
SELECT status, COUNT(*) AS total
FROM applications
WHERE user_id = 7
GROUP BY status
ORDER BY total DESC;
```
:::

:::quiz
3 · Daftar setiap perusahaan dengan jumlah aplikasinya — **termasuk perusahaan tanpa aplikasi**.

```sql
SELECT c.name, COUNT(a.id) AS applications
FROM companies c
LEFT JOIN applications a ON a.company_id = c.id
GROUP BY c.id, c.name
ORDER BY applications DESC;
```

`LEFT JOIN` tetap menyimpan perusahaan yang tidak ada pasangannya, dan `COUNT(a.id)` hanya menghitung baris sungguhan (0 kalau tidak ada). `COUNT(*)` akan salah memberi nilai 1.
:::

:::quiz
4 · Apa beda antara `WHERE` dan `HAVING`?

`WHERE` menyaring **baris sebelum** grouping; `HAVING` menyaring **grup setelah** agregasi (misalnya `HAVING COUNT(*) > 5`).
:::

:::quiz
5 · Query yang menyaring `applications` berdasarkan `user_id` lambat pada 10 juta baris. Hal pertama yang perlu dicek adalah apa, dan solusinya apa?

Jalankan `EXPLAIN ANALYZE` untuk melihat plannya. Kalau itu sequential scan, tambahkan index: `CREATE INDEX ON applications (user_id);` (kolom foreign key tidak diindeks secara otomatis di PostgreSQL).
:::

:::quiz
6 · Mengapa "buat order + kurangi stok + catat pembayaran" harus berjalan dalam transaksi?

Agar **atomic**: semua langkah berhasil (`COMMIT`) atau tidak satupun (`ROLLBACK`). Tanpanya, kegagalan di tengah jalan membuat data tidak konsisten, seperti stok berkurang untuk order yang tidak ada.
:::
::::

:::tip[Nilai dirimu]
Lulus dengan **5 dari 6**. Pertanyaan 3 adalah jebakan klasik — kalau kamu pakai `INNER JOIN` atau `COUNT(*)`, pelajari lagi materi 05.
:::

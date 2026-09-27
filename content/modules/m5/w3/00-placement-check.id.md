---
title: "Cek Penempatan Minggu 3"
summary: Keamanan akun AWS dan penagihan, evaluasi kebijakan IAM, desain region dan VPC, EC2, RDS, S3 dengan CloudFront, dan memetakan layanan AWS ke GCP dan Azure — cek yang bisa kamu lewati.
sourceHash: b6fda3cdc769
---

::::placement{id="modules/m5/w3"}
Jawab dari ingatan. Kalau ada kata yang baru bagimu, itu tanda kamu perlu pelajari materinya.

:::quiz
1 · Kamu baru saja membuat akun AWS. Apa empat hal pertama yang kamu lakukan, sebelum meluncurkan apa pun?

Nyalakan **MFA untuk root user** lalu hentikan pakai root; buat **identitas IAM admin dengan MFA** untuk pekerjaan sehari-hari (tanpa access key — pakai `aws login` untuk command line); atur **budget dan alert** dan cek paket gratis mana yang kamu dapat; dan isi **kontak alternatif** plus preferensi penagihan. Baru setelah itu pilih region, dengan sengaja.
:::

:::quiz
2 · Satu kebijakan izinkan `s3:*` di bucket; kebijakan lain di role yang sama tolak `s3:DeleteObject`. Bisakah role itu hapus object?

Tidak. **Deny** eksplisit selalu menang atas Allow apa pun — seperti tanda "jangan masuk" yang mengalahkan izin umum. Dan kalau tidak ada Allow yang cocok sama sekali, jawabannya tetap tidak.
:::

:::quiz
3 · Kenapa NAT gateway jadi "tagihan kejutan" bagi pelajar, dan apa dua cara menghindarinya untuk aplikasi kecil?

Kamu bayar per jam (puluhan dolar per bulan) ditambah per GB, bahkan saat tidak ada yang terjadi — seperti menyewa jembatan tol yang hampir tidak pernah dipakai. Untuk aplikasi kecil, taruh bagian yang perlu internet di **subnet publik** yang dilindungi security group (atau beri Fargate task IP publik), dan gunakan **VPC gateway endpoint** (gratis untuk S3 dan DynamoDB) untuk traffic ke AWS sendiri.
:::

:::quiz
4 · Security group vs network ACL: mana yang stateful, dan mana yang biasanya kamu pakai?

**Security group** itu stateful — kalau kamu izinkan request masuk, balasan diizinkan keluar otomatis — dan mereka tempel di setiap network interface. Kamu pakai untuk hampir semua hal. **NACL** itu filter stateless di seluruh subnet, cuma dipakai sesekali untuk aturan deny yang luas.
:::

:::quiz
5 · Instance RDS-mu harus terima koneksi hanya dari server API-mu. Bagaimana kamu katakan itu?

Taruh RDS di subnet privat dengan **Public access: No**, dan di security group-nya izinkan port 5432 masuk **dari security group API** — tunjuk ke group, bukan range IP, agar aturan tetap jalan saat server diganti. Juga wajibkan TLS (`sslmode=verify-full`).
:::

:::quiz
6 · Bagaimana browser dapatkan gambar produk dari bucket S3 privat, dan bagaimana penjual upload mereka?

Sajikan lewat **CloudFront dengan Origin Access Control**: bucket tetap privat dan cuma CDN yang boleh baca. Penjual upload **langsung ke S3 pakai presigned POST berumur pendek** yang batasi nama file, tipe, dan ukuran — jadi file tidak pernah lewat API-mu.
:::
::::

:::tip[Nilai dirimu sendiri]
Lulus dengan **5 dari 6**. Bahkan kalau lulus, baca materi 01 — aturan paket gratis (dan penutupan akun) penting sebelum kamu klik apa pun.
:::

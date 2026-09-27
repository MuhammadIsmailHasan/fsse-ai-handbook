---
title: "Membongkar dan Tinjau Biaya"
summary: Cloud menagihmu setiap detik untuk apa pun yang berjalan, jadi resource terlupakan itu seperti lampu menyala di ruangan kosong. Pelajari checklist pembongkaran yang tidak meninggalkan apa pun, dan tinjauan biaya yang menemukan pemborosan sebelum tagihan tiba.
sourceHash: 3750af59c789
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Perubahan pola pikir: kamu **menyewa** resource cloud setiap detik — berjalan = bayar
- **Checklist pembongkaran** yang tidak meninggalkan apa pun untuk menagihmu
- Penyebab umum di balik **tagihan mengejutkan** (terlupakan, terlalu besar, transfer data)
- Cara **tinjau biaya**: label, anggaran, dan temukan pengeluaran terbesar
- Kenapa `terraform destroy` plus pembersihan tambahan adalah jaringan pengamanmu

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Teardown** | Menghapus resource yang tidak lagi kamu butuhkan |
| **Orphan** | Resource yang masih berjalan tapi tidak ada yang menggunakannya |
| **Right-sizing** | Menyesuaikan ukuran resource dengan kebutuhan sesungguhnya |
| **Data transfer / egress** | Biaya memindahkan data keluar dari AWS |
| **Budget alarm** | Peringatan saat pengeluaran melampaui batas |
| **Tag** | Label pada resource agar kamu tahu untuk apa ia dipakai |

## 🧠 Ide besarnya

Memiliki komputer terasa gratis setelah membelinya — biarkan menyala, tidak ada biaya tambahan. Cloud kebalikannya: **apartemen sewaan dengan meter yang jalan setiap detik**. Setiap server, database, dan load balancer itu lampu, dan **kamu bayar untuk setiap yang menyala, baik ada orang di ruangan itu atau tidak.**

Jadi dua kebiasaan menjaga keselamatanmu. **Teardown** itu checklist saat kamu pergi: matikan setiap lampu, cabut semua alat, kembalikan kunci — tidak ada yang mengambil daya. **Cost review** adalah membaca tagihan listrik setiap bulan untuk menemukan pemanas di ruangan cadangan yang kamu lupa. Lakukan keduanya, cloud itu murah. Lewatkan, dan resource terlupakan akan menagihmu dalam diam selama berbulan-bulan.

## ❓ Kenapa ini penting

Horror story nomor satu untuk orang yang belajar AWS adalah **tagihan mengejutkan**: "Aku cuma bereksperimen, sebulan kemudian aku utang $200." Hampir tidak pernah dari hal yang kamu kerjakan — itu dari apa yang **kamu lupa**. Kamu menyalakan database untuk tes sesuatu, lalu pindah, dan terus jalan dengan tagihan beberapa dolar sehari selama enam minggu. Meter tidak pernah berhenti hanya karena perhatianmu berhenti.

Ini semakin penting dengan paket gratis berbasis kredit yang sudah diperingatkan modul: kredit habis, lalu resource terlupakan menagih uang sungguhan. Tiga penyebab umum sebaiknya kamu hafalkan:

- **Resource terlupakan** — ini yang besar. Instance, database, NAT gateway, dan load balancer yang kamu berhenti pakai tapi tidak pernah dihapus. Juga *orphan* yang tak terlihat: volume disk yang tidak terpasang, load balancer menganggur, snapshot database lama, IP Elastic yang tidak dipakai (AWS menagih untuk alamat yang disimpan tapi tidak dipakai).
- **Resource terlalu besar** — instance besar melakukan pekerjaan kecil. Kamu bayar untuk ukuran yang diminta, bukan kerja yang dipakai.
- **Data transfer (egress)** — memindahkan banyak data *keluar* dari AWS (ke pengguna atau region lain) menghabiskan uang dengan cara yang mengejutkan orang, karena itu bukan "hal" yang bisa dilihat berjalan.

Solusinya adalah disiplin, dan kamu sudah membangun sebagian besarnya. Jika semuanya ada di **Terraform**, `terraform destroy` menghapusnya semua dalam satu perintah yang ditampilkan — pertahanan terbaik, karena itu tidak bisa lupa seperti kamu. Lalu **pembersihan pendek** menangkap apa pun yang dibuat di luar Terraform, dan **cost review bulanan** (pakai **budget alarm** yang disiapkan di Minggu 3) menangkap apakah ada yang lolos *sebelum* menjadi tagihan nyata. Tidak ada di sini yang sulit; itu cuma kebiasaan — dan itu perbedaan antara cloud jadi taman bermain murah atau takutan mahal.

## 📖 Langkah demi langkah

### 1. Model mental: berjalan = bayar

Sebelum membuat apa pun, tanya "berapa biaya ini setiap jam, dan kapan aku akan matikannya?" `t3.micro` itu sen; instance besar, NAT gateway, atau RDS database yang dibiarkan satu bulan itu uang sungguhan. Kebiasaannya bukan kekikiran — itu tahu meter sedang jalan.

### 2. Checklist pembongkaran

Saat kamu selesai dengan satu pekerjaan atau eksperimen:

- [ ] **`terraform destroy`** stacknya (baca preview, konfirmasi). Ini menghapus semua yang dibuat Terraform — kasus terbaik.
- [ ] **Stop atau terminate** instance yang dibuat dengan tangan.
- [ ] Hapus **orphan**: volume EBS yang tidak terpasang, load balancer menganggur, IP Elastic yang tidak dipakai, snapshot/AMI lama.
- [ ] Kosongkan dan hapus **S3 bucket** yang tidak perlu (penyimpanan menagih setiap bulan).
- [ ] Cek **setiap region** yang pernah dipakai — resource bersembunyi di region yang kamu lupa disentuh.
- [ ] Konfirmasi di **billing console** bahwa tidak ada yang tak terduga masih terdaftar.

### 3. Temukan orphan

Orphan adalah resource yang tidak ada gunakan tapi tetap menagihmu. Cara murah menemukannya: cari yang **tidak terpasang pada apa pun** — volume tanpa instance, load balancer tanpa target sehat, IP Elastic tidak terkait dengan instance yang berjalan. Kalau resource tidak melakukan pekerjaan, itu lampu menyala. (Tools seperti AWS Trusted Advisor dan Cost Explorer menampilkan ini untuk kamu.)

### 4. Tinjau tagihan

Sekali sebulan (atau setelah eksperimen besar):

- Buka **Cost Explorer** dan lihat **pengeluaran terbesar** dulu — itulah di mana uangnya.
- Pakai **tag** (label `project` dan `environment` pada setiap resource) agar kamu bisa lihat *apa* setiap biaya berasal dari. Pengeluaran tanpa tag adalah pengeluaran yang tidak bisa dijelaskan.
- Cek **budget alarm** mu (Minggu 3) masih aktif — itu pemicu otomatis, ide yang sama seperti alarm di pelajaran terakhir, tapi untuk uang.
- **Right-size**: apakah ada yang jauh lebih besar dari yang diperlukan? Perkecil.

### 5. Tag membuat semua mungkin

Resource yang diberi tag `project=careerpilot, environment=dev` memberitahu kamu, berbulan-bulan kemudian, *kenapa itu ada dan apakah bisa dihapus.* Resource tanpa tag jadi misteri menakutkan yang tidak ada yang berani hapus. Tag semuanya dari awal (Terraform membuat ini mudah — atur tag di blok resource), dan both pembongkaran dan cost review jadi jauh lebih mudah.

### Pilih setupmu

- ✅ Semuanya di Terraform, diberi tag, dengan budget alarm → pembongkaran dan tinjau mudah dan aman.
- ✅ Checklist pembongkaran dijalankan di akhir setiap eksperimen atau proyek.
- 🚫 Jangan biarkan eksperimen berjalan "jaga-jaga" — buat ulang dari kode saat kamu butuh lagi.
- 🚫 Jangan percaya pada memorimu untuk lacak resource di region — pakai `destroy`, tag, dan billing console.

## ⚠️ Kesalahan umum

- Biarkan eksperimen **berjalan** dan lupakan — tagihan mengejutkan klasik.
- Lewatkan **orphan tak terlihat**: volume tidak terpasang, load balancer menganggur, IP Elastic tidak dipakai, snapshot lama.
- Resource bersembunyi di **region yang kamu lupa** dipakai.
- Resource **tanpa tag** yang tidak bisa diidentifikasi nanti, jadi tidak ada yang berani hapus.
- Anggap paket gratis berarti "gratis selamanya" — kredit habis, lalu resource terlupakan menagih uang nyata.

## 🏆 Praktik terbaik

- [ ] Kelola semuanya di **Terraform** agar `terraform destroy` jadi tombol off yang andal.
- [ ] **Tag** setiap resource (`project`, `environment`) dari awal.
- [ ] Jalankan **checklist pembongkaran** setelah setiap eksperimen; cek semua region.
- [ ] Simpan **budget alarm** aktif (Minggu 3) sebagai pemicu otomatis.
- [ ] Tinjau **pengeluaran terbesar** setiap bulan dan right-size yang terlalu besar.

:::revoshop
1. **Latihan pembongkaran.** Kamu habiskan akhir pekan untuk deploy RevoShop ke AWS untuk belajar. Tulis checklist pasti untuk pastikan biayanya hampir tidak ada saat Senin. Perintah mana yang mengerjakan sebagian besar pekerjaan?
2. **Buru orphan.** Daftar tiga resource "tak terlihat" yang bisa terus menagih setelah kamu pikir sudah bersih (hint: volume, alamat, snapshot). Bagaimana cara temukan masing-masing?
3. **Rencana tag.** Pilih tag yang akan kamu pasang di setiap resource RevoShop agar future-kamu bisa bilang mana yang aman dihapus. Kenapa resource tanpa tag jadi berbahaya?
4. **Baca tagihan.** Kalau tagihan AWS RevoShop berlipat ganda satu bulan, sebutkan tiga hal yang akan kamu cek lebih dulu (resource terlupakan? terlalu besar? transfer data?) dan di mana kamu lihat.
:::

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke teammate kenapa cloud itu "apartemen sewa dengan meter jalan", tiga penyebab umum tagihan mengejutkan, dan kenapa `terraform destroy` plus tag lebih baik dari coba ingat apa yang dibuat — pakai analogi lampu di ruangan kosong.

## 📐 Rancang

Rancang setup keselamatan biaya RevoShop: tag di setiap resource, ambang batas budget alarm, checklist pembongkaran yang dijalankan setelah eksperimen, dan langkah tinjau bulanan. Lalu jelaskan bagaimana semuanya di Terraform membuat semua ini andal.

:::quiz
Lihat contoh jawaban

**Tag:** `project=revoshop`, `environment=dev|prod`, `owner` di setiap resource (atur di blok Terraform). **Budget alarm:** anggaran bulanan (katakan $10 untuk belajar) yang email-mu di 50% dan 80% — pemicu Minggu 3. **Checklist pembongkaran:** `terraform destroy` stack (baca preview) → terminate instance yang dibuat tangan → hapus volume terlantar, load balancer menganggur, IP Elastic tidak dipakai, snapshot lama → kosongkan dan hapus S3 bucket yang tidak pakai → cek *setiap region* → konfirmasi billing console bersih. **Tinjau bulanan:** buka Cost Explorer, urut berdasarkan pengeluaran terbesar, pakai tag untuk lihat project/environment mana asalnya, right-size yang terlalu besar, konfirmasi budget alarm masih aktif. **Kenapa Terraform membuatnya andal:** semuanya dibuat lewat kode dihapus dengan satu `destroy` yang ditampilkan, jadi cleanup tidak tergantung pada mengingat apa yang diklik — tool tidak bisa lupa.
:::

### 📝 Checklist review mandiri

- [ ] Semuanya diberi tag dan di Terraform
- [ ] Ada budget alarm dan checklist pembongkaran
- [ ] Aku akan cek terlupakan/terlalu besar/egress saat tagihan loncat

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m5/w7/05-cost-review" ai="no-ai" title="Tinjau biaya dan temukan pemborosan"}
Tulis `monthly_cost(resources)` untuk total biaya cloud per bulan, dan `idle_resources(resources)` untuk daftar orphan yang menagihmu karena tidak ada gunanya — dua pertanyaan yang setiap cost review mulai dengan.
:::

:::hints
- Pakai **730 jam** sebagai satu bulan. Biaya bulanan resource adalah `hourly_cost * 730`.
- `monthly_cost` menjumlah *semua* resource (dipakai atau tidak); bulatkan total ke 2 desimal.
- `idle_resources` mengembalikan nama resource yang **diurutkan** di mana `in_use` adalah `False` — yang dibersihkan.
:::

## ✅ Cek cepat

:::quiz
Kenapa resource terlupakan adalah penyebab paling umum tagihan cloud mengejutkan?

Karena cloud menagihmu per detik untuk apa pun yang *berjalan*, dan berhenti perhatian tidak menghentikan meter. Kamu nyalakan database untuk tes, pindah, dan terus menagih beberapa dolar per hari selama minggu — sering kali orphan tak terlihat (volume tidak terpasang, load balancer menganggur) yang tidak kamu ingat buat. Biayanya bukan dari hal yang dikerjakan; dari hal yang dilupakan.
:::

:::quiz
Bagaimana semuanya di Terraform melindungi dari tagihan mengejutkan lebih baik daripada berhati-hati?

`terraform destroy` menghapus semuanya yang kode buat dalam satu perintah yang ditampilkan, jadi cleanup tidak tergantung kamu ingat apa yang diklik di region — tool tidak lupa seperti manusia. Berhati-hati membantu, tapi ingatan gagal; kode tidak. Tambah tag dan budget alarm, punya tombol off andal plus pemicu.
:::

## 📚 Lanjut belajar

- [AWS: Kontrol biayamu (free tier)](https://docs.aws.amazon.com/awsaccountbilling/latest/aboutv2/tracking-free-tier-usage.html)
- [AWS Cost Explorer](https://docs.aws.amazon.com/cost-management/latest/userguide/ce-what-is.html)
- [AWS: Praktik terbaik tag](https://docs.aws.amazon.com/whitepapers/latest/tagging-best-practices/tagging-best-practices.html)

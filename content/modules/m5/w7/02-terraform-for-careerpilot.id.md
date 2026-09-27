---
title: "Terraform untuk CareerPilot: Variabel, Output & Modul"
summary: Variabel membuat satu config bisa untuk dev dan prod. Output mengembalikan nilai seperti URL database. Modul menggabungkan resource yang bisa dipakai berulang. Bersama-sama, kamu membangun cloud CareerPilot berulang-ulang dari kode.
sourceHash: fe69d8dc8ca5
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- **Variabel** — satu set file Terraform yang bisa untuk dev *dan* prod
- **Output** — mendapat nilai balik (URL database, alamat load balancer)
- **Modul** — menggabungkan resource yang bisa dipakai berulang
- Bagaimana ketiga hal ini mengubah satu resource di Minggu 1 menjadi infrastruktur aplikasi sungguhan
- Loop yang sama: plan → apply → destroy, tapi untuk CareerPilot

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Variabel** | Nilai yang bisa diganti, diisi per lingkungan |
| **Output** | Nilai yang dikembalikan Terraform setelah membangun |
| **Modul** | Paket resource yang bisa dipakai berulang dengan inputnya sendiri |
| **Lingkungan** | dev / staging / prod, masing-masing punya pengaturan berbeda |
| **tfvars** | Berkas yang berisi nilai untuk variabel |

## 🧠 Ide besarnya

Materi terakhir menulis satu resource yang hard-coded (nilainya langsung dikode). Infrastruktur sungguhan butuh tiga langkah lagi, dan semuanya mirip hal yang sudah kamu tahu:

- **Variabel** adalah **kolom kosong di formulir** — ide mail-merge yang sama dari Helm. Satu config, diisi beda untuk dev (`t3.micro`, 1 salinan) dan prod (`t3.small`, 3 salinan).
- **Output** adalah **struk/bon** yang dihasilkan: "alamat database-mu di sini, URL situs-mu di sini" — nilai yang kamu (atau alat lain) butuh setelah resource ada.
- **Modul** adalah **paket IKEA**: satu bundel tertutup ("layanan web dengan load balancer dan security group") yang bisa kamu tempel sekali atau lima kali, tanpa menulis ulang bagiannya.

Semuanya bersama-sama membiarkan kamu menjelaskan seluruh cloud CareerPilot satu kali dan menciptakan salinan identik kapan saja.

## ❓ Kenapa ini penting

Tanpa variabel, kamu harus copy seluruh folder Terraform untuk setiap lingkungan dan edit nilai di dalamnya dengan tangan — persis masalah copy-paste drift yang sudah Helm selesaikan untuk Kubernetes. Satu set `.tf` ditambah satu berkas nilai kecil per lingkungan membuat dev dan prod tetap **bentuk yang sama**, hanya berbeda di tempat yang kamu inginkan.

Tanpa output, kamu membangun database lalu harus **berburu di console** untuk mendapat alamatnya untuk paste ke config aplikasi. Output memberikannya ke kamu (dan ke alat berikutnya) otomatis, jadi bagian-bagian terhubung tanpa copy manual — lebih sedikit kesalahan, dan bisa otomasi.

Tanpa modul, sistem besar jadi satu berkas raksasa yang tidak bisa dibaca, dengan pola yang sama di-copy berulang-ulang. Modul menamai pola sekali ("layanan di belakang load balancer") jadi kamu bisa pakai ulang dan baca dengan mudah — sama seperti "jangan ulangi diri sendiri" yang kamu pelajari di track Arsitektur, tapi untuk infrastruktur.

CareerPilot seukuran yang cukup untuk lihat semua tiga: punya backend API, database, storage tertentu, dan layak punya setidaknya lingkungan dev dan prod. Menjelaskan CareerPilot dalam Terraform yang bisa diatur parameter dan modular adalah cara tim sungguhan menjalankannya — dan ini **Fase 5 kamu**.

## 📖 Langkah demi langkah

### 1. Variabel: satu config, banyak lingkungan

Deklarasikan variabel, pakainya, dan berikan nilainya per lingkungan:

```hcl
variable "instance_type" {
  type    = string
  default = "t3.micro"
}

resource "aws_instance" "api" {
  instance_type = var.instance_type   # the blank, filled from the variable
  ami           = var.ami
}
```

```hcl
# prod.tfvars                # dev.tfvars
instance_type = "t3.small"   # instance_type = "t3.micro"
```

```bash
terraform apply -var-file=dev.tfvars    # builds the small dev version
terraform apply -var-file=prod.tfvars   # builds the bigger prod version
```

Berkas sama, isian berbeda — dev dan prod tidak bisa melenceng diam-diam.

### 2. Output: dapatkan nilai balik

Setelah membangun, kamu butuh nilai tertentu — endpoint database, URL situs. Deklarasikan sebagai **output**:

```hcl
output "database_url" {
  value = aws_db_instance.main.address
}

output "site_url" {
  value = aws_lb.web.dns_name
}
```

```bash
terraform output database_url    # prints the address; no console hunting
```

Sekarang config aplikasi-mu atau pipeline CI bisa baca ini otomatis, bukan seseorang copy-paste alamat dari halaman web.

### 3. Modul: pakai ulang satu bundel

**Modul** adalah folder berisi resource dengan input (variabel) dan output sendiri. Kamu pakainya seperti fungsi yang kamu panggil:

```hcl
module "api" {
  source        = "./modules/web-service"   # the reusable bundle
  instance_type = var.instance_type
  app_image     = var.app_image
}
```

Modul `web-service` bisa berisi instance, security group-nya, dan load balancer-nya — ditulis sekali. Butuh layanan identik kedua? Panggil modul lagi dengan input berbeda. Ini adalah "jangan ulangi diri sendiri" dari track Arsitektur, sekarang untuk infrastruktur.

### 4. Bentuk CareerPilot

CareerPilot butuh, kira-kira: **layanan backend** (API), **database** (RDS PostgreSQL), **storage** tertentu (S3 untuk berkas), dan **config/secret** (Parameter Store / Secrets Manager). Tata letak Terraform yang masuk akal:

```text
careerpilot-infra/
├── modules/
│   ├── web-service/     # API service + load balancer + security group
│   └── database/        # RDS instance + security group-nya
├── main.tf              # panggil modul, sambungkan
├── variables.tf         # instance_type, db_size, app_image, ...
├── outputs.tf           # database_url, site_url
├── dev.tfvars           # nilai kecil, murah
└── prod.tfvars          # nilai lebih besar
```

Maka `terraform apply -var-file=dev.tfvars` membangun lingkungan dev CareerPilot lengkap, dan `prod.tfvars` membangun prod dari *kode yang sama*.

### 5. Loop aman yang sama, selalu

Tidak ada yang berubah di loop: **plan** (baca selisihnya), **apply** (buat), **destroy** (hapus, diperlihatkan dulu). Variabel dan modul hanya membuat hal yang kamu rencanakan lebih besar dan bisa dipakai ulang. Selalu baca plan — modul bisa buat banyak resource sekaligus, jadi pratinjau penting lebih-lebih.

### Pilihan yang perlu dibuat

- ✅ Lebih dari satu lingkungan → variabel + file `.tfvars`, bukan folder yang dicopy.
- ✅ Pola yang kamu bangun lebih dari sekali (layanan, database) → modul.
- ✅ Nilai yang langkah berikutnya butuh (URL DB, URL situs) → output.
- 🚫 Jangan over-modularize setup kecil; modul untuk satu resource sekali jalan hanya menambah tidak perlu.

## ⚠️ Kesalahan umum

- Copy seluruh folder Terraform per lingkungan, bukan pakai **variabel** — mereka melenceng.
- Hard-code nilai yang berbeda per lingkungan (ukuran, tag image) langsung di resource.
- Berburu console untuk alamat database, bukan deklarasikan **output**.
- Letakkan **secret** di `.tfvars` yang di-commit ke git — simpan secret di Secrets Manager/Parameter Store dan acu.
- Modul sangat umum dan nested dalam-dalam, orang tidak bisa tahu apa yang dibangun — simpan mudah dibaca.

## 🏆 Praktik terbaik

- [ ] Sesuaikan per-lingkungan dengan **variabel** dan file `.tfvars`.
- [ ] Tampilkan nilai yang langkah lain butuh sebagai **output** (URL DB, URL situs).
- [ ] Kumpulkan pola berulang ke **modul**; simpan kecil dan mudah dibaca.
- [ ] Simpan **secret** jauh dari tfvars/git; acu secrets store.
- [ ] Bangun dev dan prod dari **kode sama**, nilai beda — tidak ada drift.

:::revoshop
1. **Temukan variabelnya.** Untuk CareerPilot (atau RevoShop), daftar nilai mana saja yang akan beda antara dev dan prod: ukuran instance, jumlah replika/instance, tag image, ukuran database. Itu jadi variabel di `.tfvars`.
2. **Daftar output-nya.** Setelah Terraform bangun CareerPilot, nilai mana yang aplikasi atau CI kamu butuh balik? (URL Database? URL situs? Nama bucket?) Setiap satu adalah satu `output`.
3. **Temukan modul.** Kelompok resource mana yang muncul lebih dari sekali, atau layak dinamai sebagai bundel ("layanan web": instance + load balancer + security group)? Itu calon modul.
4. **Persiapan Fase 5.** Gambar tata letak folder untuk Terraform CareerPilot-mu (modul, variabel, tfvars per lingkungan). Kamu akan bangun versi ini di Fase 5.
:::

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke rekan tim bagaimana variabel, output, dan modul mengubah "satu server hard-coded" jadi "seluruh cloud CareerPilot, bisa dibangun untuk dev dan prod dari kode sama". Hubungkan setiap satu dengan sesuatu yang mereka tahu: variabel ↔ blanko Helm, modul ↔ jangan-ulangi-diri-sendiri, output ↔ struk alamat.

## 📐 Rancang

Rancang tata letak Terraform CareerPilot-mu: namai modul, variabel yang berbeda antara dev dan prod, output yang aplikasi butuh, dan tulis dua perintah `apply`. Lalu jelaskan bagaimana kamu roboh lingkungan dev dengan bersih.

:::quiz
Lihat contoh jawaban

**Modul:** `web-service` (instance/layanan ECS API + load balancer + security group) dan `database` (RDS + security group-nya). **Variabel (beda per lingkungan):** `instance_type`, `instance_count`, `db_size`, `app_image` — set di `dev.tfvars` (kecil) dan `prod.tfvars` (lebih besar). **Output:** `database_url` (untuk config aplikasi), `site_url` (untuk kunjungi / untuk CI). **Perintah:** `terraform apply -var-file=dev.tfvars` dan `...prod.tfvars`. **Roboh:** `terraform destroy -var-file=dev.tfvars` — baca pratinjau (bisa hapus banyak resource dari modul), konfirmasi, dan semuanya yang dev bangun hilang, tagihan berhenti. Secret hidup di Secrets Manager dan diacu, jangan pernah di berkas tfvars.
:::

### 📝 Checklist review mandiri

- [ ] Perbedaan per-lingkungan adalah variabel, bukan berkas yang dicopy
- [ ] Pola yang bisa dipakai ulang adalah modul; nilai yang dibutuhkan adalah output
- [ ] Secret diacu, bukan di-commit di tfvars

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

### 🧠 Rancang (tidak ada kode)

Tidak ada Python di sini — praktek adalah merancang infrastruktur CareerPilot di atas kertas, siap untuk **Fase 5**:

1. Gambar tata letak folder (`modules/`, `main.tf`, `variables.tf`, `outputs.tf`, `dev.tfvars`, `prod.tfvars`).
2. Daftar setiap variabel dan nilainya dev vs prod di tabel kecil.
3. Daftar output dan siapa yang pakai setiap satu.
4. Untuk setiap modul, daftar resource di dalamnya.
5. Tulis perintah pasti `plan`, `apply`, dan `destroy` untuk lingkungan **dev**.

Simpan rancangan ini — Fase 5 meminta kamu bangun slice yang berfungsi.

## ✅ Cek cepat

:::quiz
Kenapa pakai variabel dengan `dev.tfvars`/`prod.tfvars` bukan copy folder Terraform untuk setiap lingkungan?

Jadi dev dan prod bagikan kode yang tepat (bentuk *sama*), dan hanya perbedaan yang dimaksud — ukuran, jumlah, tag image — hidup di berkas nilai kecil. Folder yang dicopy melenceng seiring perubahan dibuat di satu dan bukan di satunya, membuat ulang bug "staging tes sesuatu berbeda dari production". Satu config, banyak isian, membuat lingkungan jujur.
:::

:::quiz
Masalah apa yang Terraform output selesaikan?

Setelah Terraform bangun resource, sering kamu butuh nilai mereka — alamat database, URL load balancer. Tanpa output kamu akan berburu di console dan paste ke config dengan tangan. Output memberikan nilai balik otomatis, jadi config aplikasi atau pipeline CI bisa baca langsung — tidak ada copy manual, lebih sedikit kesalahan.
:::

## 📚 Lanjut belajar

- [Terraform: Input variables](https://developer.hashicorp.com/terraform/language/values/variables)
- [Terraform: Output values](https://developer.hashicorp.com/terraform/language/values/outputs)
- [Terraform: Modules](https://developer.hashicorp.com/terraform/language/modules)

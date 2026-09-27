---
title: "Terraform: Infrastruktur sebagai Kode"
summary: Alih-alih klik di konsol AWS, kamu menulis cloud-mu dalam berkas — server, database, network. Terraform tunjukkan rencana perubahan, lalu buat kenyataan cocok dengan rencana. Bisa diulang, bisa diperiksa di git, dan dihapus dengan satu perintah.
sourceHash: de455a788af0
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa itu **Infrastructure as Code (IaC)** dan kenapa klik di konsol tidak bisa berkembang
- Cara **Terraform** mengubah deskripsi cloud-mu jadi sumber daya nyata
- Putaran aman: **plan** (pratinjau perubahan) lalu **apply** (buat perubahan)
- Apa itu **state** Terraform (memorinya tentang apa yang sudah dibangun)
- Kenapa `terraform destroy` adalah obat tagihan AWS yang mengejutkan

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Infrastructure as Code (IaC)** | Mendeskripsikan server dan network-mu dalam berkas, bukan dengan klik |
| **Terraform** | Alat populer yang membangun sumber daya cloud dari berkas-berkas itu |
| **Resource** | Satu hal yang kamu buat: server, database, atau bucket |
| **Plan** | Pratinjau apa yang akan dibuat, diubah, atau dihapus |
| **Apply** | Benar-benar buat perubahan-perubahan itu |
| **State** | Catatan Terraform tentang apa yang sudah dibangun |
| **Drift** | Saat kenyataan tidak lagi cocok dengan kode |

## 🧠 Ide besarnya

Membangun cloud dengan **klik-klik di konsol AWS** itu seperti merakit furnitur dari ingatan: sekali jalan, tapi kamu tidak ingat persis apa yang sudah dilakukan, tidak bisa melakukannya dua kali dengan cara yang sama, dan orang lain tidak bisa meniru.

**Infrastructure as Code** adalah **lembar petunjuk IKEA**: seluruh bangunan tertulis, langkah demi langkah, dalam satu berkas. Siapa saja bisa ikuti petunjuk itu dan dapat hasil yang *sama*. Kalau kamu mau ruangan kedua yang identik (lingkungan staging), ikuti lembar yang sama. Kalau mau buang semuanya, ada catatan setiap benda yang mesti dibuang — tidak ada yang terlupakan di sudut, diam-diam biayai.

Terraform adalah alat yang membaca lembar petunjuk-mu, lihat apa yang sudah ada, dan jalankan langkah yang persis diperlukan agar kenyataan cocok — tidak kurang, tidak lebih.

## ❓ Kenapa ini penting

Di Minggu 3–4 kamu membuat sumber daya AWS sebagian dengan tangan. Itu bagus untuk belajar, tapi cara menjalankan sistem nyata, "click-ops" tidak tahan:

- **Tidak bisa diulang.** Kamu setup production dengan klik 40 layar. Sekarang bangun staging yang identik. Bisakah kamu klik 40 layar yang persis sama, persis cara yang sama? Tidak seorang pun bisa — jadi staging dan production diam-diam berbeda, dan kamu dapat bug Minggu 2: "di staging jalan."
- **Tidak bisa diperiksa.** Rekan kerja ubah security group di konsol. Tidak ada diff, tidak ada pull request, tidak ada catatan *siapa ubah apa dan kenapa*. Infrastruktur diam-diam berubah.
- **Tidak bisa dibuang.** Kamu buat sepuluh sumber daya untuk coba sesuatu, lalu lupa tiga di antaranya. Mereka terus biayai-mu selama berbulan-bulan. Ini cara #1 pelajar dapat tagihan AWS mengejutkan.
- **Drift.** Seseorang tweak pengaturan dengan tangan; sekarang setup "nyata" tidak cocok dokumen mana pun. Enam bulan kemudian tidak seorang pun tahu kenapa production berperilaku berbeda.

IaC perbaiki keempat masalah itu. Infrastruktur-mu adalah berkas di git: **bisa diulang** (apply lagi untuk lingkungan identik), **bisa diperiksa** (perubahan lewat pull request dengan diff terlihat), **bisa dibuang** (`terraform destroy` buang semua yang dibuatnya — cara teraman hindari sumber daya terlupakan), dan **terdeteksi drift-nya** (Terraform bandingkan kode dengan kenyataan dan bilang apa yang berbeda). Biayanya kurva belajar dan alat baru untuk dijalankan — tapi untuk apa pun lebih dari percobaan sekali-kali, deskripsikan infrastruktur dalam kode adalah cara yang dilakukan sekarang.

## 📖 Langkah demi langkah

### 1. Deskripsikan apa yang kamu mau

Berkas Terraform (`.tf`) deklarasikan **resource** — kamu bilang *apa* yang harus ada, bukan *bagaimana* membuatnya:

```hcl
# A single server, described in code.
resource "aws_instance" "web" {
  ami           = "ami-0abcd1234"
  instance_type = "t3.micro"
  tags = {
    Name = "revoshop-web"
  }
}
```

Ini deklaratif, cara berpikir yang sama seperti Kubernetes: kamu nyatakan hasil akhir yang diinginkan, dan alat mencari tahu panggilan API untuk sampai sana.

### 2. Plan: lihat sebelum lompat

**Jangan pernah** biarkan alat ubah cloud-mu tanpa tunjukkan dulu. `terraform plan` cetak **pratinjau** — diff apa yang akan dibuat, diubah, atau dihapus:

```bash
terraform plan
# + aws_instance.web will be created
#     instance_type = "t3.micro"
# Plan: 1 to add, 0 to change, 0 to destroy.
```

`+` berarti "buat". Nanti, ubah nilai mungkin tunjukkan `~` (ubah tempat) atau `-` (hapus). Pratinjau ini adalah sabuk pengaman-mu: kamu baca dan pastikan alat akan lakukan apa yang kamu maksud — *sebelum* apa pun nyata terjadi. Rencana yang bilang "3 hapus" saat kamu harap "1 tambah" baru saja selamatkan-mu.

### 3. Apply: buat nyata

```bash
terraform apply     # shows the plan again, then asks: do you want to proceed? yes
```

Terraform buat persis perubahan di rencana. Jalankan lagi tanpa ubah kode dan bilang "tidak ada perubahan" — kenyataan sudah cocok berkas. Idempotency itu intinya: apply kode yang sama selalu konvergen ke hasil yang sama.

### 4. State: memori Terraform

Untuk tahu apa yang mesti diubah, Terraform simpan berkas **state** yang catat apa yang sudah dibangun. Saat edit kode dan plan, bandingkan *kode* (apa yang mau) dengan *state* (apa yang dibuat) dengan *kenyataan* (apa yang sungguhan ada), dan tunjukkan perbedaannya.

> ⚠️ State bisa berisi nilai sensitif dan jangan hilang atau dibagikan sembarangan. Tim nyata simpan di backend bersama yang terkunci (seperti bucket S3 dengan locking), jangan pernah di-commit ke git. Untuk belajar, berkas state lokal itu bagus.

### 5. Destroy: tombol off

```bash
terraform destroy   # previews everything it will remove, then does it
```

Ini fitur yang buat-mu aman di AWS: semua yang kamu buat lewat Terraform dihapus dalam satu perintah, dengan pratinjau dulu. Tidak perlu berburu di konsol untuk database yang kamu lupa. Buat, eksperimen, `destroy` — disiplin lokal-pertama yang sudah kamu gunakan semua modul, sekarang untuk sumber daya cloud nyata.

### Memilih setup-mu

- ✅ Lingkungan nyata apa pun, apa pun yang akan dibangun lebih dari sekali, apa pun tim pakai → IaC dengan Terraform.
- ✅ Eksperimen yang yakin bisa sepenuhnya dibuang → Terraform, jadi `destroy` bersihkan.
- 🚫 Klik cepat sekali-kali untuk lihat sesuatu → konsol bagus; jangan jalankan sistem nyata dengan cara itu.
- 🚫 Edit sumber daya yang dikelola Terraform dengan tangan di konsol → sebab drift; ubah kode sebagai gantinya.

## ⚠️ Kesalahan umum

- Jalankan `apply` (atau `destroy`) **tanpa baca rencana** — rencana itu untuk tangkap kesalahan sebelum nyata.
- Bangun production dengan **klik**, jadi tidak pernah bisa ditiru atau diperiksa.
- Edit sumber daya yang dikelola Terraform **dengan tangan**, sebab drift yang kode tidak lagi deskripsikan.
- **Hilang atau commit** berkas state — hilang memisahkan sumber daya-mu; commit bisa bocor secret.
- Lupa `destroy` eksperimen, lalu bayar sumber daya terbengkalai berbulan-bulan.

## 🏆 Praktik terbaik

- [ ] Simpan semua infrastruktur nyata sebagai **kode di git**, diubah lewat pull request.
- [ ] Selalu **baca rencana** sebelum apply atau destroy.
- [ ] Simpan **state** di backend bersama yang terkunci (S3 + locking); jangan pernah commit.
- [ ] Ubah sumber daya dengan **edit kode**, jangan pernah tangan di konsol (hindari drift).
- [ ] `terraform destroy` eksperimen saat selesai — obat terpercaya untuk tagihan mengejutkan.

:::revoshop
1. **Kodekan Minggu 4.** Di Minggu 4 kamu deploy backend RevoShop di AWS. Daftar sumber daya yang setup itu butuh (instance atau ECS service, database, security group, load balancer). Masing-masing itu blok Terraform `resource`.
2. **Baca rencana.** Bayangkan `terraform plan` cetak "Plan: 1 to add, 0 to change, **2 to destroy**" saat yang dimaksud cuma tambah satu instance. Apa yang akan kamu lakukan, dan kenapa langkah plan yang selamatkan-mu?
3. **Janji teardown.** Dengan semua di Terraform, bagaimana pastikan eksperimen AWS akhir pekan biaya hampir tidak ada pada Senin? Perintah mana, dan kenapa itu lebih aman dari konsol?
4. **Dua lingkungan.** Bagaimana punya infra sebagai kode buat lingkungan staging identik jadi mudah — dan bagaimana itu bunuh bug "di staging jalan" dari Minggu 2?
:::

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan rekan kerja kenapa deskripsikan setup AWS RevoShop di Terraform alih-alih klik di konsol — pakai analogi lembar petunjuk IKEA — dan apa yang dilindungi langkah `plan`.

## 📐 Rancang

Di atas kertas, daftar resource Terraform untuk deploy AWS RevoShop dan deskripsikan putaran perubahan aman untuk tambah satu (misalnya, instance kedua): tulis resource, jalankan plan dan cek diff, apply, dan bagaimana sepenuhnya buang-nya nanti.

:::quiz
Lihat contoh jawaban

Resource: service ECS (atau instance EC2) untuk API, database PostgreSQL RDS, security group, load balancer, dan networking (VPC/subnet) dari Minggu 3. Putaran perubahan untuk tambah instance kedua: (1) tambah/ubah blok resource di `.tf` dan buka pull request agar diff-nya diperiksa; (2) `terraform plan` dan pastikan bilang "1 to add, 0 to destroy" — bukan sesuatu menakutkan; (3) `terraform apply` dan biarkan buat persis perubahan itu; (4) saat selesai eksperimen, `terraform destroy` (setelah baca pratinjau-nya) untuk buang semua dan stop tagihan. Karena semua kode, staging bisa apply identik berkas yang sama, jadi dua lingkungan tidak bisa diam-diam drift.
:::

### 📝 Checklist review mandiri

- [ ] Setiap resource dideskripsikan dalam kode, bukan diklik
- [ ] Putaran adalah plan → baca diff → apply
- [ ] Saya bisa sepenuhnya buang-nya dengan destroy

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m5/w7/01-terraform-plan" ai="no-ai" title="Hitung rencana Terraform"}
Tulis `plan(current, desired)`, diff jantung Terraform: bandingkan sumber daya yang ada sekarang dengan sumber daya yang kode-mu minta, dan laporkan apa yang mesti **dibuat**, **diubah**, atau **dihapus** — pratinjau yang dibaca sebelum apa pun sentuh cloud-mu.
:::

:::hints
- Keduanya `current` dan `desired` adalah dict dari `name -> attributes` (dict attributes per resource).
- **create**: di `desired` tapi tidak di `current`. **destroy**: di `current` tapi tidak di `desired`. **change**: di keduanya, tapi attribute berbeda.
- Kembalikan daftar terurut agar rencana stabil, contohnya `{"create": [...], "change": [...], "destroy": [...]}`.
:::

## ✅ Cek cepat

:::quiz
Kenapa `terraform plan` (pratinjau) kebiasaan penting sebelum `apply`?

Karena tunjukkan persis apa yang akan dibuat, diubah, atau dihapus *sebelum* apa pun nyata terjadi. Kalau rencana bilang "2 hapus" saat hanya maksud tambah satu resource, tangkap kesalahan gratis dan berhenti. Apply tanpa baca rencana itu biarkan alat bentuk ulang cloud-mu tanpa lihat — rencana adalah sabuk pengaman-mu.
:::

:::quiz
Sebutkan dua masalah Infrastructure as Code selesaikan yang klik konsol tidak bisa.

Dua dari: **repeatability** (apply berkas yang sama untuk lingkungan staging identik, alih-alih coba klik ulang 40 layar), **reviewability** (perubahan lewat pull request dengan diff terlihat dan catatan siapa/kenapa), **disposability** (`terraform destroy` buang semua yang dibuat, jadi tidak ada sumber daya terlupakan biayai), dan **drift detection** (Terraform bandingkan kode dengan kenyataan dan tandai perubahan yang dibuat tangan).
:::

## 📚 Lanjut belajar

- [Terraform: What is Terraform?](https://developer.hashicorp.com/terraform/intro)
- [Terraform: plan command](https://developer.hashicorp.com/terraform/cli/commands/plan)
- [Terraform: State](https://developer.hashicorp.com/terraform/language/state)

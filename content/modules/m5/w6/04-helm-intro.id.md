---
title: "Helm: Template & Paket untuk Kubernetes"
summary: Helm melakukan dua tugas — install aplikasi berpaket di Kubernetes dengan satu perintah (chart seperti apt/brew untuk cluster), dan template manifest-mu sendiri agar satu file dengan bagian kosong bisa diisi per environment daripada copy-paste YAML.
sourceHash: 92e7b5128d14
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Dua tugas yang dilakukan **Helm**: **install paket** dan **template manifest**
- Apa itu **chart** (paket untuk Kubernetes) dan file **values** (pengaturannya)
- Kenapa templating lebih baik daripada copy-paste YAML yang hampir sama untuk dev/staging/prod
- Ide "mail merge" di jantung Helm: **satu template, banyak salinan yang sudah diisi**
- Kapan Helm membantu dan kapan terlalu rumit

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Helm** | Alat yang membuat paket dan template manifest Kubernetes |
| **Chart** | Paket Helm: template + pengaturan bawaan untuk aplikasi |
| **Values** | Pengaturan yang kamu berikan ke chart (image, replika, dll) |
| **Template** | Manifest dengan bagian kosong yang akan diisi |
| **Render** | Isi bagian kosong dengan nilai jadi YAML sungguhan |
| **Release** | Satu instalasi chart di cluster |

## 🧠 Ide besarnya

Helm adalah **mail merge untuk Kubernetes**. Waktu kamu kirim surat yang sama ke 100 orang, kamu tidak retype 100 kali — kamu tulis **satu** template dengan bagian kosong ("Halo **[nama]**, pesananmu nomor **[nomor]**…") dan daftar nilai, lalu mail merge isi semuanya. Helm melakukan hal yang sama untuk YAML Kubernetes: kamu tulis **satu** template dengan bagian kosong seperti `{{ .Values.replicas }}`, dan file **values** yang kecil menyediakan `replicas: 3`. Helm render manifest sungguhan dengan mengisi bagian kosong.

Tugas keduanya adalah menjadi **app store untuk cluster**: **chart** adalah paket siap pakai (misalnya, "PostgreSQL" atau "Redis"), dan `helm install` meletakkannya di cluster-mu sama seperti `brew install` atau `apt install` meletakkan software di laptop-mu — satu perintah daripada menulis puluhan manifest dengan tangan.

## ❓ Kenapa ini penting

Begitu kamu menjalankan Kubernetes sungguhan, dua masalah muncul cepat.

**Pertama: banjir copy-paste.** Kamu butuh hampir manifest yang sama untuk dev, staging, dan production — app yang sama, tapi image tag berbeda, jumlah replika berbeda, dan ukuran sumber daya berbeda. Tanpa template kamu simpan tiga (atau sepuluh) file YAML yang hampir sama. Ubah satu hal dan kamu harus edit di setiap salinan, dan salinannya pelan-pelan jadi berbeda sampai "staging tes setup yang berlainan dari production" — bug yang persis sama seperti Minggu 2 ingatkan. Helm memperbaikinya: **satu** template, dan file values kecil per environment (`values-prod.yaml` atur `replicas: 6`, `values-dev.yaml` atur `replicas: 1`). Bentuk bersama tinggal di satu tempat; hanya perbedaannya saja yang ditulis.

**Kedua: install software orang lain.** Kamu mau Redis, atau alat metrics, atau ingress controller di cluster-mu. Menulis semua manifest itu dengan tangan dari dokumennya lambat dan mudah salah. Ada yang sudah bungkus setiap hal sebagai **chart**, jadi `helm install redis ...` setup di satu baris, dan `helm upgrade` / `helm uninstall` kelolanya dengan bersih. Ini leverage yang sama yang package manager berikan di laptop-mu — kamu tidak compile software dari awal, dan kamu jangan menulis manifest cluster dari awal juga.

Tradeoff-nya: Helm menambah layer templating, dan chart yang banyak template bisa jadi sulit dibaca (bagian kosong dalam bagian kosong). Untuk app kecil dengan satu environment, manifest polos lebih jelas. Helm penting ketika kamu punya **beberapa environment** atau kamu **install aplikasi berpaket** — bukan sebelumnya.

## 📖 Langkah demi langkah

### 1. Helm sebagai package manager

```bash
# Add a repository of charts, then install one — like apt/brew for your cluster.
helm install my-redis bitnami/redis
helm list                 # what's installed (releases)
helm upgrade my-redis bitnami/redis --set replica.replicaCount=2
helm uninstall my-redis   # clean removal of everything it created
```

Satu perintah install aplikasi yang sebaliknya puluhan manifest menulis dengan tangan. `helm uninstall` hapus persis apa yang ditambahkan — tidak ada sisa.

### 2. Helm sebagai templater (mail merge)

Manifest template punya bagian kosong yang baca dari values:

```yaml
# templates/deployment.yaml  (a template, not final YAML)
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {{ .Values.name }}
spec:
  replicas: {{ .Values.replicas }}      # a blank, filled from values
  template:
    spec:
      containers:
        - name: {{ .Values.name }}
          image: {{ .Values.image }}
```

Dan file values sediakan jawaban:

```yaml
# values.yaml
name: revoshop-api
replicas: 3
image: revoshop-api:v1.4
```

`helm template` (atau `helm install`) **render** mereka bersama jadi manifest sungguhan — `replicas: 3`, `image: revoshop-api:v1.4`. Ide yang sama seperti surat dan daftar nama.

### 3. Satu template, banyak environment

Intinya: simpan satu template, dan satu file values kecil per environment hanya untuk perbedaannya.

```yaml
# values-dev.yaml        # values-prod.yaml
replicas: 1              # replicas: 6
image: revoshop-api:dev  # image: revoshop-api:v1.4
```

```bash
helm template -f values-dev.yaml .    # renders the dev version
helm template -f values-prod.yaml .   # renders the prod version
```

Dev dan prod sekarang punya bentuk persis sama dan tidak bisa berbeda tidak sengaja — hanya perbedaan yang dimaksudkan (replika, image) ditulis, di file values. Ini "build sekali, atur per environment" (Minggu 2) diterapkan ke manifest-mu.

### 4. Apa yang ada di chart

**Chart** cuma folder: direktori `templates/` (manifest dengan bagian kosong), `values.yaml` (bawaan), dan `Chart.yaml` (nama dan versi). Install itu ciptakan **release** — satu instance bernama di cluster-mu yang Helm lacak jadi bisa upgrade atau hapus sebagai satu unit.

### Pilihan setup

- ✅ Install aplikasi berpaket (Redis, ingress, monitoring) → Helm, satu perintah.
- ✅ Satu app di beberapa environment yang beda cuma beberapa nilai → template Helm.
- 🚫 Satu app kecil dengan satu environment → manifest polos lebih sederhana dan jelas.
- 🚫 Template begitu banyak sampai hasil tidak bisa dibaca → kamu tukar satu masalah jadi masalah lebih buruk.

## ⚠️ Kesalahan umum

- Simpan banyak manifest **copy-paste** untuk environment daripada satu template + file values — salinannya jadi berbeda.
- Over-templating: bagian kosong dalam bagian kosong dalam kondisional, sampai chart tidak bisa dibaca.
- Install chart dari sumber **tidak dipercaya** tanpa baca apa yang mereka buat — kamu jalankan manifest orang di cluster-mu.
- Edit YAML yang sudah dirender di cluster dengan tangan, jadi `helm upgrade` berikutnya timpa perubahan-mu — edit values atau template sebagai gantinya.
- Ambil Helm untuk app kecil satu-environment di mana YAML polos lebih jelas.

## 🏆 Praktik terbaik

- [ ] Gunakan Helm untuk **install aplikasi berpaket** daripada menulis manifest mereka dengan tangan.
- [ ] Simpan **satu template** dan **file values kecil per environment** untuk perbedaannya.
- [ ] Jaga template bisa dibaca; jangan template apa yang tidak pernah berubah.
- [ ] Lacak versi: kunci versi chart dan simpan file values-mu di git.
- [ ] Install chart hanya dari sumber yang dipercaya, dan baca apa yang mereka buat.

:::revoshop
1. **Spotkan copy-paste.** Kalau RevoShop jalan di Kubernetes dengan dev/staging/prod, field mana yang berbeda antar environment (image tag, replika, ukuran sumber daya, config)? Perbedaan itu persis apa yang file values simpan.
2. **Tulis values.** Sketsa `values-dev.yaml` dan `values-prod.yaml` untuk RevoShop: replika dan image tag per masing-masing. Apa yang sama (dan jadi milik template, bukan values)?
3. **Install dependency.** RevoShop butuh Redis. Bandingkan menulis manifest Redis dengan tangan vs `helm install`. Apa yang chart hemat untuk kamu, dan apa yang tetap harus kamu tentukan (memory, persistence)?
4. **Apakah sudah sepadan?** RevoShop hari ini punya satu environment. Apakah layer templating Helm sepadan untuk ditambahkan sekarang, atau itu keputusan "nanti, kalau kita tambah environment" ? Jelaskan alasannya.
:::

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke rekan tim, memakai analogi mail merge, kenapa simpan satu template Helm plus file values per environment lebih aman daripada simpan tiga file YAML yang hampir sama — dan hubungkan ke bug "staging tes setup yang berlainan dari production" dari Minggu 2.

## 📐 Rancang

Rancang setup Helm RevoShop untuk dua environment. Putuskan apa yang ada di template bersama vs file values per-environment, tulis dua file values (dev dan prod berbeda di replika dan image), dan sebutkan satu chart yang kamu `helm install` daripada menulis dengan tangan.

:::quiz
Lihat jawaban kemungkinan

**Template (bersama):** bentuk Deployment dan Service — nama container, port, label, struktur — dengan bagian kosong untuk `name`, `replicas`, dan `image`. **Values:** `values-dev.yaml` → `replicas: 1`, `image: revoshop-api:dev`; `values-prod.yaml` → `replicas: 6`, `image: revoshop-api:v1.4`. Semua yang lain (port, label, probe) tetap di template supaya dev dan prod tidak bisa berbeda. **Chart yang diinstall, bukan tulis tangan:** Redis (misalnya Bitnami Redis chart) — satu `helm install` dengan override values untuk memory dan persistence, daripada tulis manifest Redis dari dokumennya.
:::

### 📝 Checklist review mandiri

- [ ] Bentuk bersama ada di template; hanya perbedaan ada di values
- [ ] File values dev dan prod berbeda hanya tempat yang perlu
- [ ] Saya gunakan chart untuk dependency daripada menulis dengan tangan

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m5/w6/04-helm-render" ai="no-ai" title="Render template Helm"}
Bangun mesin kecil di jantung Helm: tulis `render(template, values)` yang ganti setiap bagian kosong `{{ .Values.key }}` di string template dengan nilai yang cocok — langkah isi-bagian-kosong yang sama Helm jalankan sebelum kirim manifest ke Kubernetes.
:::

:::hints
- Bagian kosong terlihat seperti `{{ .Values.NAME }}`, di mana `NAME` adalah huruf, digit, atau underscore. Izinkan spasi opsional dalam kurung kurawal.
- Gunakan `re.sub` dengan pola seperti `\{\{\s*\.Values\.(\w+)\s*\}\}` dan fungsi replacer yang lihat nama yang ditangkap di `values`.
- Ubah nilai jadi teks dengan `str(...)`, jadi integer seperti `3` render jadi `3`. Jika key yang direferensikan tidak ada di `values`, lontarkan `KeyError(name)`.
:::

## ✅ Cek cepat

:::quiz
Kenapa satu template Helm plus file values per environment lebih aman daripada tiga file YAML yang hampir sama?

Bentuk bersama tinggal di persis satu tempat, jadi tidak bisa berbeda antar environment — hanya perbedaan yang dimaksudkan (replika, image) ditulis, di file values. Dengan tiga salinan, perubahan harus diulang di mana-mana dan salinan pelan-pelan berbeda tanpa sengaja, jadi staging tes setup yang berlainan dari production. Helm buat "bentuk sama, atur berbeda" jadi bawaan.
:::

:::quiz
Kamu mau Redis di cluster-mu. Kenapa ambil `helm install` daripada tulis manifest-mu sendiri?

Ada yang sudah bungkus Redis dengan benar sebagai chart, jadi satu perintah install-nya (dan `helm upgrade`/`uninstall` kelola bersih), sama seperti `brew install` lebih baik daripada compile dari kode sumber. Tulis semua manifest dari dokumen Redis dengan tangan lambat dan mudah salah; kamu tetap pilih atur seperti memory dan persistence, tapi lewat values chart.
:::

## 📚 Lanjut belajar

- [Helm: Apa itu Helm?](https://helm.sh/docs/)
- [Helm: Chart](https://helm.sh/docs/topics/charts/)
- [Helm: File values](https://helm.sh/docs/chart_template_guide/values_files/)

---
title: "Kubernetes Lokal dengan kind"
summary: kind menjalankan satu cluster Kubernetes lengkap di dalam Docker di laptopmu — gratis, bisa dibuang, cluster praktik tanpa akun cloud atau tagihan.
sourceHash: 6496c6e2e2a3
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa itu **kind** dan kenapa itu cara aman untuk belajar Kubernetes
- Perintah **kubectl** sehari-hari: apply, get, scale, delete
- Cara menulis **Deployment** dan **Service** kecil di YAML
- Cara *memantau* self-healing dan scaling terjadi di depan matamu
- Kenapa kamu harus selalu **menghapus cluster** setelah selesai

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **kind** | Kubernetes lokal di Docker di laptopmu |
| **Cluster** | Sekumpulan mesin yang dikelola Kubernetes (di sini, mesin palsu) |
| **kubectl** | Alat perintah untuk berbicara dengan Kubernetes |
| **Manifest** | Berkas YAML yang menggambarkan apa yang kamu inginkan (Deployment, Service) |
| **apply** | Kirim manifest ke cluster: "buat ini menjadi nyata" |
| **Replica** | Satu salinan yang sedang berjalan dari sebuah pod |

## 🧠 Ide besarnya

Belajar Kubernetes pada mesin cloud sungguhan itu seperti belajar mengemudi dengan menyewa mobil sungguhan di jalan tol sungguhan — mahal, lambat di setup, dan kesalahan biaya uang. **kind** (Kubernetes IN Docker) adalah **simulatornya**: ia menjalankan satu cluster Kubernetes kecil *di dalam container Docker di laptopmu*. Setir yang sama, pedal yang sama, perintah yang sama seperti yang asli — tapi gratis, muncul dalam hitungan menit, dan aman untuk dirusak. Setelah selesai, kamu hapus seluruh cluster dan tidak ada yang tertinggal.

Ini persis ide "jalankan di lokal dulu" yang sudah kamu pakai seluruh Module 5: praktik di tempat yang kesalahannya gratis, sebelum menyentuh apa pun yang berbayar.

## ❓ Kenapa ini penting

Kubernetes punya reputasi sulit, dan banyak ketakutan itu datang dari belajarnya di tempat yang salah — pada cluster cloud sungguhan di mana setiap eksperimen lambat, berbayar, dan terasa berisiko. Jadi orang tidak pernah *bermain*, dan mereka tidak pernah membangun ingatan otot.

kind menghilangkan semua itu. Cluster muncul dalam sekitar satu menit, tidak berbayar, dan bisa dibuang dan dibuat ulang secara instan. Itu berarti kamu bisa melakukan satu hal yang benar-benar mengajarkan Kubernetes: **rusakkan sengaja dan lihat ia menyembuhkan diri.** Hapus satu pod dan lihat yang baru muncul. Ubah "3 replicas" jadi "6" dan lihat tiga lagi mulai. Setelah kamu *lihat* control loop dari materi terakhir bekerja di depanmu, konsepnya berhenti abstrak. Dan karena ini `kubectl` sungguhan dengan manifest sungguhan, semua yang kamu pelajari di sini bekerja tanpa berubah pada cluster cloud sungguhan nanti — kamu tinggal arahkan perintah yang sama ke cluster yang lebih besar dan berbayar.

## 📖 Langkah demi langkah

### 1. Apa yang kamu butuhkan

- **Docker** sedang berjalan (kamu punya dari Week 1) — kind membangun cluster palsunya dari container Docker.
- **kind** dan **kubectl** terinstal. Di macOS dengan Homebrew: `brew install kind kubectl`. (Lihat halaman install resmi di bawah untuk sistem lain.)

### 2. Buat cluster yang bisa dibuang

```bash
kind create cluster --name practice
```

Dalam sekitar satu menit kamu punya cluster Kubernetes yang berfungsi. Cek ia masih hidup:

```bash
kubectl get nodes
# NAME                     STATUS   ROLES           AGE   VERSION
# practice-control-plane   Ready    control-plane   1m    v1.31.x
```

"Node" itu adalah container Docker yang berpura-pura jadi mesin. Cukup untuk belajar segalanya.

### 3. Jelaskan apa yang kamu inginkan (sebuah manifest)

Buat `app.yaml` — satu Deployment meminta **3 salinan** dari web server kecil, plus Service untuk memberi mereka satu alamat:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: web
spec:
  replicas: 3                 # I want 3 copies, always
  selector:
    matchLabels:
      app: web
  template:
    metadata:
      labels:
        app: web
    spec:
      containers:
        - name: web
          image: nginx:1.27-alpine
          ports:
            - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: web
spec:
  selector:
    app: web                  # send traffic to pods labelled app=web
  ports:
    - port: 80
      targetPort: 80
```

Ini adalah desired state dari materi terakhir, ditulis.

### 4. Buat nyata, dan lihat

```bash
kubectl apply -f app.yaml     # "make this true"
kubectl get pods              # watch 3 pods appear
# web-xxxx   Running
# web-yyyy   Running
# web-zzzz   Running
```

Kamu tidak pernah memberitahu Kubernetes *bagaimana* memulai tiga container — kamu menggambarkan end state dan ia melakukan langkahnya.

### 5. Pantau self-healing (bagian yang seru)

Hapus satu pod dan segera lihat lagi:

```bash
kubectl delete pod <one-pod-name>
kubectl get pods              # still 3! a new one is already starting
```

Kamu menghapus satu salinan; aktual turun ke 2; control loop menyadarinya dan memulai pengganti — tidak ada manusia terlibat. Itu seluruh materi terakhir, terjadi di depanmu.

### 6. Skala dengan mengubah angka yang diinginkan

```bash
kubectl scale deployment web --replicas=6
kubectl get pods              # now 6
```

Kamu mengubah *apa yang kamu inginkan* dari 3 jadi 6; loop memulai tiga lagi. Scaling turun bekerja dengan cara yang sama.

### 7. Selalu bersihkan

```bash
kind delete cluster --name practice
```

Seluruh cluster — setiap pod, node dan jaringan — hilang. Tidak ada yang sedang berjalan, tidak ada yang lupa. Ini kebiasaan lokal-dulu: buat, eksperimen, hapus.

### Memilih setup-mu

- ✅ Belajar Kubernetes, menguji manifest, menjalankan pengecekan CI → kind (gratis, instan, bisa dibuang).
- ✅ Demo cepat lokal dari aplikasi yang mengharapkan Kubernetes.
- 🚫 User sungguhan / production → cluster cloud terkelola (EKS), bukan kind di laptopmu.
- 🚫 Menyimpan data yang kamu pedulikan di dalam cluster kind — ia disposable by design.

## ⚠️ Kesalahan umum

- Lupa **menghapus cluster**, membiarkan container Docker makan memori di background.
- Edit pod yang sedang berjalan dengan tangan alih-alih mengubah **manifest** dan re-apply — perubahanmu hilang saat loop mengganti pod.
- Mengharapkan data yang disimpan di pod untuk survive — pod disposable; berkas lokal pod yang dihapus hilang.
- Menganggap kind sebagai production. Ia simulator: sempurna untuk belajar, salah untuk traffic sungguhan.
- Melewati langkah "hapus pod dan lihat ia menyembuhkan diri" — itulah latihan yang membuatnya klik.

## 🏆 Praktik terbaik

- [ ] Simpan desired state-mu di **manifest YAML** di version control; ubah berkas, re-apply.
- [ ] Gunakan kind untuk belajar, demo dan CI — gratis dan reproducible.
- [ ] **Hapus cluster** setelah selesai (buat → eksperimen → hapus).
- [ ] Buktikan manifest yang sama bekerja pada kind sebelum menjalankannya pada cluster berbayar.
- [ ] Jangan pernah simpan data yang kamu pedulikan di dalam cluster yang disposable.

:::revoshop
1. **Manifest untuk RevoShop.** Sketch satu Deployment untuk RevoShop API: berapa banyak replicas, image mana, port mana. Satu baris apa yang akan kamu ubah untuk menjalankan 5 salinan alih-alih 3?
2. **Coba itu (opsional, gratis).** Kalau kamu punya Docker gratis, nyalakan cluster kind dan deploy contoh `nginx` di atas. Hapus satu pod dan lihat ia kembali. Itu eksperimen lima menit mengajarkan lebih dari satu jam membaca.
3. **Masalah stateful.** RevoShop butuh PostgreSQL dan Redis. Kenapa menjalankan *mereka* di dalam pod yang disposable berisiko, dan di mana data mereka benar-benar milik (hint: Week 3's RDS, dan Redis terkelola)?
4. **Lokal vs sungguhan.** Perintah kind mana yang akan bekerja tanpa perubahan terhadap cluster EKS sungguhan, dan apa yang berubah (hint: bukan perintahnya — biaya dan siapa yang bisa mencapainya)?
:::

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke seorang teman kenapa kamu ingin belajar Kubernetes pada kind sebelum menyentuh cluster cloud sungguhan — memakai analogi driving-simulator — dan apa yang "hapus pod dan lihat ia kembali" demonstrasikan tentang control loop.

## 📐 Rancang

Tulis (di atas kertas atau di `app.yaml` sungguhan) desired state untuk aplikasi web kecil: satu Deployment dengan replica count pilihan dan image, dan satu Service di depan. Lalu daftarkan perintah `kubectl`/`kind` yang pasti kamu jalankan untuk membuat cluster, apply-nya, scale ke 6, dan runtuhkan semuanya.

:::quiz
Lihat jawaban yang mungkin

Manifest: satu Deployment `web` dengan `replicas: 3`, image `nginx:1.27-alpine`, port 80, plus Service yang memilih `app: web` di port 80. Perintah: `kind create cluster --name practice` → `kubectl apply -f app.yaml` → `kubectl get pods` (lihat 3) → `kubectl scale deployment web --replicas=6` (lihat 6) → `kind delete cluster --name practice` (semua hilang). Untuk membuktikan self-healing di antara: `kubectl delete pod <name>` lalu `kubectl get pods` — masih angka target, karena loop menggantikannya.
:::

### 📝 Checklist review mandiri

- [ ] Manifest menyatakan replica count dan image
- [ ] Aku tahu perintah create → apply → scale → delete
- [ ] Aku merencanakan untuk menghapus cluster di akhir

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

### 🧪 Hands-on: buat Kubernetes menyembuhkan diri di depanmu

Tidak ada Python di sini — latihannya adalah untuk *menggunakan* itu. Kalau kamu punya Docker berjalan (gratis):

1. `kind create cluster --name practice`
2. Simpan `app.yaml` dari langkah 3 di atas dan `kubectl apply -f app.yaml`.
3. `kubectl get pods` — konfirmasi 3 sedang Running.
4. `kubectl delete pod <one-name>` lalu segera `kubectl get pods` lagi. **Lihat pengganti muncul.** Tulis apa yang kamu lihat.
5. `kubectl scale deployment web --replicas=6`, konfirmasi 6, lalu kembali ke `--replicas=2`.
6. `kind delete cluster --name practice`. Konfirmasi dengan `kubectl get nodes` (akan error — cluster hilang).

Tidak ada Docker sekarang? Lakukan sebagai paper trace: untuk setiap perintah, tulis apa yang akan `kubectl get pods` tunjukkan setelahnya.

## ✅ Cek cepat

:::quiz
Kenapa kind tempat yang bagus untuk belajar Kubernetes, tapi tempat yang buruk untuk menjalankan traffic sungguhan?

kind menjalankan cluster lengkap di dalam Docker di laptopmu — gratis, instan, dan bisa dibuang — jadi kamu bisa eksperimen dan rusak hal dengan aman, dan perintahnya identik dengan cluster sungguhan. Tapi itu satu laptop yang berpura-pura jadi banyak mesin: tidak ada real availability, tidak bisa dijangkau user, dan disposable by design. Traffic sungguhan butuh cluster cloud terkelola (EKS).
:::

:::quiz
Kamu edit pod yang sedang berjalan dengan tangan untuk ubah pengaturan, dan sesaat kemudian perubahanmu hilang. Kenapa?

Pod disposable dan dikelola oleh control loop. Kalau pod itu diganti (ia crash, atau kamu hapus itu, atau rollout terjadi), pod baru dibuat dari **manifest**, bukan dari edit-mu dengan tangan. Untuk buat perubahan bertahan, edit YAML dan re-apply — itu mengubah desired state yang loop rebuild dari.
:::

## 📚 Lanjut belajar

- [kind: Quick start](https://kind.sigs.k8s.io/docs/user/quick-start/)
- [kubectl: Cheat sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Kubernetes: Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)

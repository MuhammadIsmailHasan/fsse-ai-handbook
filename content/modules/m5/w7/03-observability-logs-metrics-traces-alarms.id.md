---
title: "Observability: Log, Metrik, Trace & Alarm"
summary: Di production tidak ada yang menjaga, jadi sistem harus memperingatkanmu. Metrik adalah pengukur, log adalah buku harian, trace mengikuti satu permintaan, dan alarm adalah lampu peringatan yang membangunkan orang saat angka melampaui batas yang dirasakan pengguna.
sourceHash: a7462d03ead3
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Tiga sinyal: **metrik**, **log**, **trace** — apa yang masing-masing jawab
- Apa itu **alarm** dan kenapa itu yang memungkinkanmu berhenti menatap dashboard
- Cara membuat alarm yang **berguna**, bukan berisik (gejala yang pengguna rasakan)
- Ide kasar tentang **SLO** dan **error budget**
- Bagaimana sinyal bekerja bersama untuk pergi dari "ada yang salah" ke "ini alasannya"

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Metrik** | Angka yang dilacak dari waktu ke waktu (permintaan/detik, tingkat error) |
| **Log** | Catatan dengan waktu yang menjelaskan satu kejadian |
| **Trace** | Perjalanan satu permintaan melintasi layanan (Minggu 5) |
| **Alarm** | Aturan yang memicu ketika metrik melampaui batas |
| **Dashboard** | Layar berisi bagan metrik |
| **SLO** | Target yang kamu janjikan (misalnya 99,9% permintaan OK) |
| **Error budget** | Seberapa banyak kegagalan yang masih diizinkan SLO |

## 🧠 Ide besarnya

Observability itu seperti **dashboard dan lampu peringatan mobil**:

- **Metrik** adalah **pengukur** — kecepatan, bahan bakar, suhu mesin. Angka yang berubah dari waktu ke waktu. Satu pandangan memberi tahu kamu *bagaimana keadaan*.
- **Log** adalah **buku harian perjalanan** — catatan rinci untuk setiap kejadian ("14:02 belok kiri ke jalan tol"). Mereka memberi tahu kamu *persis apa yang terjadi*.
- **Trace** adalah **mengikuti satu perjalanan** melalui sistem mobil (kamu temui ini di Minggu 5).
- **Alarm** adalah **lampu peringatan** — kamu tidak menatap pengukur suhu selama enam jam; lampu merah hanya menyala *saat* melampaui batas berbahaya, jadi kamu bisa mengemudi (dan menjalani hidupmu) sampai itu terjadi.

Intinya ialah bahwa **mobil memberitahu kamu**, bukan kamu yang harus menjaga.

## ❓ Kenapa ini penting

Ini adalah kenyataan yang tidak nyaman tentang production: **tidak ada yang menjaganya.** Jam 3 pagi, kamu tidur, dan 500 pengguna baru saja kena error. Dashboard yang cantik tidak membantu *siapa pun* jika tidak ada manusia yang melihatnya. Jadi sistem harus menjangkau dan **memberitahu** kamu — itulah apa itu **alarm**, dan ini adalah bagian paling penting. Metrik, log, dan trace adalah cara kamu *menyelidiki*; alarm adalah cara kamu *mengetahui* sama sekali.

Tapi alarm memiliki dua sisi. Alarm yang terlalu mudah memicu — pada setiap blip kecil yang tidak dirasakan siapa pun — melatihmu untuk mengabaikannya. Setelah alarm palsu yang kesepuluh di jam 3 pagi, kamu senyapkan ponsel, lalu kamu melewatkan yang nyata. Ini **alert fatigue** (kelelahan alarm), dan inilah cara outage terlewatkan *meskipun* monitoring bagus. Jadi keahliannya bukan "tambahkan alarm"; itu menulis alarm yang **sedikit dan bermakna** yang memicu pada hal yang benar-benar dirasakan pengguna (checkout gagal, situs lambat) dan yang bisa ditindaklanjuti manusia — bukan pada noise internal seperti "CPU sempat mencapai 80%."

Kemudian, setelah alarm membangunkanmu, tiga sinyal bekerja sebagai corong: **metrik** mengatakan *sesuatu* salah ("tingkat error 8%"), **trace** mengatakan *di mana* ("span Pembayaran gagal"), dan **log** mengatakan *persis apa* ("Midtrans mengembalikan 503"). Metrik → trace → log membawamu dari "ada api" ke "penyedia pembayaran" dalam hitungan menit bukan jam. Tanpa ini, kamu menebak-nebak dalam gelap sementara pengguna pergi.

## 📖 Langkah demi langkah

### 1. Tiga sinyal, berdampingan

| Sinyal | Menjawab | Bentuk | Contoh |
|---|---|---|---|
| **Metrik** | *Apakah* ada yang salah, dan seberapa banyak? | angka dari waktu ke waktu | tingkat error = 8% |
| **Trace** | *Di mana* dalam permintaan? | satu permintaan melintasi layanan | span Pembayaran gagal |
| **Log** | *Persis apa* yang terjadi? | catatan kejadian dengan waktu | "Midtrans 503 pada 14:02" |

Kamu sudah tahu structured logging (Modul 2) dan mengenal tracing (Minggu 5). Metrik adalah bagian baru: hitungan dan pengukuran yang dikumpulkan dari waktu ke waktu — permintaan per detik, tingkat error, p95 latency, panjang antrean — biasanya dilihat sebagai bagan di **dashboard** dan, yang penting, dipantau oleh **alarm**.

### 2. Empat "golden signal" yang layak dipantau

Untuk hampir semua layanan, empat metrik menceritakan sebagian besar cerita:

- **Latency** — berapa lama permintaan berlangsung (pantau p95/p99, bukan rata-rata — rata-rata menyembunyikan ekor lambat).
- **Traffic** — berapa banyak permintaan (permintaan per detik).
- **Errors** — tingkat permintaan yang gagal (5xx, timeout).
- **Saturation** — seberapa penuh sistemnya (CPU, memori, panjang antrean).

Jika kamu hanya mengatur beberapa hal, atur ini.

### 3. Apa yang membuat alarm baik

Alarm hanyalah aturan: *ketika metrik melampaui batas selama beberapa waktu, beri tahu seseorang.* Alarm yang **baik** adalah:

- **Pada gejala yang pengguna rasakan** — "tingkat error > 2% selama 5 menit", "p95 latency > 1s" — bukan pada penyebab yang tidak diperhatikan siapa pun ("CPU di 80%"). CPU tinggi yang tidak merugikan siapa pun bukan keadaan darurat.
- **Dapat ditindaklanjuti** — saat memicu, ada sesuatu yang bisa dilakukan manusia. Alarm yang selalu kamu abaikan seharusnya menjadi bagan, bukan alarm.
- **Tidak terlalu sensitif** — menunggu beberapa menit ("selama 5 menit") jadi blip satu detik tidak membangunkanmu.
- **Jarang** — jika alarm menangis serigala setiap minggu, orang berhenti mempercayainya.

> Aturan praktis: **setiap alarm yang membangunkan manusia harus layak untuk dibangunkan.** Semua hal lain adalah dashboard.

### 4. SLO dan error budget (versi ramah)

Sebuah **SLO** (service level objective) adalah target yang kamu janjikan: "99,9% permintaan berhasil setiap bulan." Kesenjangan — 0,1% yang kamu boleh gagal — adalah **error budget** kamu. Ini mengubah keandalan dengan bijak: kamu tidak perlu *nol* error (tidak mungkin dan sangat mahal), kamu perlu tetap *dalam anggaran*. Jika kamu membakar anggaran dengan cepat, lambatkan dan perbaiki keandalan; jika ada banyak sisa, kamu bisa mengirimi fitur lebih cepat. Ini mengubah "apakah cukup andal?" menjadi angka bukan perdebatan.

### 5. Di AWS

**CloudWatch** mengumpulkan metrik dan log serta menjalankan **alarm** (misalnya "jika tingkat error 5xx > 2% selama 5 menit, kirim pemberitahuan"); alarm memberi tahu melalui **SNS** ke email, Slack, atau pager. Trace berasal dari **X-Ray** atau OpenTelemetry (Minggu 5). Untuk aplikasi LLM, **Langfuse** memberi kamu metrik, trace, dan biaya per panggilan. Ide yang sama di mana-mana — pengukur, buku harian, pandangan satu perjalanan, lampu peringatan.

### Memilih setup-mu

- ✅ Apa pun yang sungguhan: setidaknya empat golden signal, ditambah *beberapa* alarm pada gejala yang dihadapi pengguna.
- ✅ Satu SLO untuk alur paling penting (checkout), dengan error budget untuk memandu prioritas.
- 🚫 Jangan alarm pada setiap metrik — kebanyakan adalah dashboard, bukan panggilan.
- 🚫 Jangan bangunkan manusia untuk hal yang tidak bisa mereka tindaklanjuti, atau kamu akan melatih mereka mengabaikan alarm.

## ⚠️ Kesalahan umum

- **Tanpa alarm** — dashboard indah yang tidak diawasi siapa pun pada jam 3 pagi tidak memberi tahu apa pun.
- **Terlalu banyak alarm** — alert fatigue; yang nyata diabaikan di antara alarm palsu.
- Alarm pada **penyebab** (CPU, memori) bukan **gejala** yang pengguna rasakan (error, latency).
- Menonton **rata-rata** latency, yang menyembunyikan ekor lambat — pantau p95/p99.
- Log **rahasia atau data pribadi**, atau menghabiskan biaya pada log yang tidak pernah kamu baca.

## 🏆 Praktik terbaik

- [ ] Lacak empat golden signal: **latency, traffic, errors, saturation**.
- [ ] Alarm pada **gejala menghadap pengguna**, dan buat setiap alarm panggilan **dapat ditindaklanjuti**.
- [ ] Pertahankan alarm **sedikit dan terpercaya**; semua hal lain adalah dashboard.
- [ ] Atur **SLO + error budget** untuk alur paling penting kamu.
- [ ] Gunakan metrik → trace → log sebagai corong dari "apa yang salah" ke "kenapa".

:::revoshop
1. **Golden signal untuk RevoShop.** Sebut empat metrik yang kamu pantau untuk API RevoShop dan dari mana masing-masing berasal. Yang mana satu yang akan kamu alarm terlebih dahulu, dan pada batas berapa?
2. **Alarm baik vs alarm buruk.** Tulis satu alarm *baik* (gejala yang pengguna rasakan) dan satu alarm *buruk* (penyebab yang tidak diperhatikan siapa pun) untuk RevoShop. Kenapa alarm buruk akan melatihmu mengabaikan alarm?
3. **Corong.** Tingkat error checkout alarm di 8%. Jelajahi bagaimana kamu akan menggunakan trace, lalu log, untuk pergi dari alarm itu ke penyebab aktualnya (hint: span Pembayaran dari Minggu 5).
4. **Satu SLO.** Pilih alur paling penting RevoShop dan tulis SLO untuknya ("X% checkout berhasil per bulan"). Apa yang error budget biarkan kamu putuskan?
:::

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan kepada rekan kerja kenapa dashboard saja tidak cukup dan **alarm** adalah bagian kunci — menggunakan analogi lampu peringatan mobil — dan kenapa *terlalu banyak* alarm sama berbahayanya dengan tidak ada sama sekali.

## 📐 Rancang

Rancang monitoring RevoShop: empat metrik golden-signal, dua atau tiga alarm (batas, durasi, dan apa yang dilakukan manusia saat masing-masing memicu), satu SLO dengan error budget-nya, dan bagaimana kamu akan menggunakan metrik → trace → log untuk men-debug kegagalan checkout.

:::quiz
Tunjukkan kemungkinan jawaban

**Metrik:** p95 latency, permintaan/detik, tingkat error 5xx, CPU/memori (dan panjang antrean jika menggunakan antrean). **Alarm:** (1) "tingkat error 5xx > 2% selama 5 menit" → panggil on-call; tindakan: periksa error/trace, roll back jika deploy terakhir menyebabkannya; (2) "p95 latency > 1s selama 10 menit" → panggil; tindakan: temukan span lambat (trace), mungkin DB atau penyedia pembayaran; (3) "tingkat kesuksesan checkout < 98% selama 10 menit" → panggil; tindakan: selidiki Pembayaran. **SLO:** "99,5% checkout berhasil per bulan"; error budget 0,5% memutuskan apakah mengirim fitur (anggaran tersisa) atau fokus pada keandalan (anggaran terbakar). **Corong debug:** alarm tingkat error mengatakan *sesuatu* salah → trace checkout menunjukkan span Pembayaran yang gagal → log pada span itu mengatakan "Midtrans 503" → perbaiki atau failover. Semua alarm ada pada gejala yang dirasakan pelanggan, dan masing-masing punya tindakan jelas.
:::

### 📝 Checklist review mandiri

- [ ] Alarm ada pada gejala menghadap pengguna dan dapat ditindaklanjuti
- [ ] Alarm sedikit, bukan satu per metrik
- [ ] Saya bisa melacak alarm ke penyebab dengan metrik → trace → log

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m5/w7/03-evaluate-alarms" ai="no-ai" title="Tentukan alarm mana yang memicu"}
Alarm adalah aturan pada metrik. Tulis `evaluate_alarms(readings, rules)` yang memeriksa bacaan metrik saat ini terhadap sekumpulan aturan alarm dan mengembalikan persis alarm mana yang sedang aktif — logika yang CloudWatch jalankan setiap menit.
:::

:::hints
- Setiap aturan memiliki `name`, `metric`, `op` (salah satu dari `">"`, `"<"`, `">="`, `"<="`), dan `threshold`.
- Cari bacaan untuk metrik aturan; jika metrik itu tidak ada di `readings`, alarm tidak bisa memicu — lewati.
- Bandingkan dengan operator yang tepat; kumpulkan nama alarm yang aktif dan kembalikan mereka **diurutkan**.
:::

## ✅ Cek cepat

:::quiz
Kenapa alarm lebih penting daripada dashboard yang indah untuk production?

Karena di production tidak ada yang menjaga dashboard — jam 3 pagi dan semua orang tidur. Dashboard hanya membantu saat manusia melihat; alarm menjangkau dan *memberi tahu* manusia bahwa ada yang salah, jadi ini yang membuat kamu mengetahui sama sekali. Dashboard dan sinyal lain adalah untuk menyelidiki setelah alarm membangunkanmu.
:::

:::quiz
Kenapa alarm pada "tingkat error > 2%" bukan "CPU > 80%"?

Karena tingkat error adalah gejala yang benar-benar dirasakan pengguna — permintaan gagal — dan layak membangunkan manusia. CPU tinggi yang tidak menyebabkan error atau lambat tidak merugikan siapa pun, jadi alarm padanya melatih orang mengabaikan alarm (alert fatigue). Alarm pada gejala yang pengguna rasakan dan yang bisa ditindaklanjuti manusia; pertahankan penyebab seperti CPU sebagai dashboard.
:::

## 📚 Lanjut belajar

- [Google SRE Book: Monitoring & the Four Golden Signals](https://sre.google/sre-book/monitoring-distributed-systems/)
- [Google SRE Workbook: SLOs](https://sre.google/workbook/implementing-slos/)
- [Amazon CloudWatch: Alarms](https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/AlarmThatSendsEmail.html)

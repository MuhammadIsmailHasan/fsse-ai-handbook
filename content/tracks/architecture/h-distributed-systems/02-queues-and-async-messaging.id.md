---
title: "Queues & Async Messaging"
summary: Cara berhenti membuat user menunggu pekerjaan lambat — message queue membuat satu layanan menyerahkan tugas ke layanan lain dan membalas seketika, dengan at-least-once delivery, consumer idempotent, dan dead-letter queue untuk tugas yang gagal terus.
sourceHash: 6a4add1a40a2
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Kenapa pekerjaan lambat sebaiknya jalan **setelah** kamu membalas user
- Apa itu **message queue** dan pola **producer/consumer**
- Bagaimana queue **melepas ketergantungan** layanan dan menyerap lonjakan lalu lintas
- Delivery **at-least-once** dan kenapa consumer harus **idempotent**
- **Dead-letter queue** untuk tugas yang gagal terus
- Di mana ini cocok untuk RevoShop (Modul 5 menambah queue Redis)

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Queue** | Antrean pekerjaan yang menunggu dikerjakan |
| **Producer** | Kode yang menaruh pekerjaan ke queue |
| **Consumer / worker** | Kode yang mengambil pekerjaan dan mengerjakannya |
| **Async** | Kerjakan nanti, jangan buat pemanggil menunggu |
| **Decouple** | Membiarkan dua bagian bekerja tanpa saling menunggu |
| **At-least-once** | Sebuah tugas bisa terkirim lebih dari sekali |
| **Idempotent** | Melakukannya dua kali punya efek sama seperti sekali |
| **Dead-letter queue** | Tempat samping untuk tugas yang gagal terus |

## 🧠 Ide besarnya

Queue seperti **rel pesanan di warung ramai**. Kasir (**producer**) menjepit pesananmu ke rel dan langsung melayani pelanggan berikutnya — ia tak berdiri dan memasak. Para koki (**consumer**) menarik tiket dari rel dan memasak dengan kecepatan mereka sendiri. Rel membuat bagian depan dan dapur bekerja **tanpa saling menunggu**, dan menjaga antrean tetap stabil saat jam makan siang ramai.

## ❓ Kenapa ini penting

Sebagian pekerjaan lambat: mengirim email, memperkecil gambar, memanggil model AI, menagih kartu. Kalau request web-mu *melakukan* pekerjaan itu sebelum membalas, user menatap spinner selama beberapa detik, dan lonjakan order bisa menumbangkan server.

Queue memperbaiki keduanya: request web menjatuhkan tugas ke queue dan membalas **seketika** ("kami sedang memproses order-mu"); worker melakukan bagian lambat di latar belakang. Situs tetap cepat, dan lonjakan lalu lintas hanya membuat queue lebih panjang, bukan server tumbang.

## 📖 Langkah demi langkah

### 1. Producer dan consumer

Dua peran, dihubungkan oleh queue:

```
  web request (PRODUCER)  ──enqueue──▶  [ QUEUE ]  ──dequeue──▶  worker (CONSUMER)
      replies instantly                                          does the slow job
```

Producer menambah **message** (deskripsi tugas kecil, mis. `{"type": "send_receipt", "order_id": 42}`) lalu lanjut. Proses worker terpisah menarik message dan melakukan pekerjaannya.

### 2. Melepas ketergantungan dan menyerap lonjakan

Karena hanya terhubung lewat queue, producer dan consumer **decouple**:

- Layanan email bisa lambat atau sesaat mati — order tetap diterima; tugas struknya hanya menunggu.
- Serbuan 10.000 order tak menabrakkan apa pun; queue bertambah panjang dan worker menyusul. (Kamu juga bisa menambah worker.)

Ini alasan utama sistem besar bersandar pada queue.

### 3. Delivery at-least-once

Queue nyata (SQS, RabbitMQ, berbasis Redis) menjanjikan delivery **at-least-once**, bukan exactly-once. Kalau worker crash setelah melakukan pekerjaan tapi sebelum mengonfirmasi (**ack**), queue menganggapnya belum selesai dan **mengirim ulang** message-nya. Jadi tugas yang sama bisa jalan dua kali.

```
worker takes "send_receipt #42" → sends email → CRASHES before ack
queue redelivers "send_receipt #42" → a second worker sends it again → duplicate email
```

### 4. Jadi consumer harus idempotent

Perbaikannya (ide sama seperti API idempotent): buat worker aman dijalankan dua kali. Catat tugas mana yang sudah kamu tangani dan lewati duplikat.

```python
def handle(message, processed):
    if message["id"] in processed:      # already done this exact job
        return "skipped"
    do_the_work(message)
    processed.add(message["id"])        # mark done (in a shared store like Redis/DB)
    return "processed"
```

Kini message yang dikirim ulang terdeteksi dan dilewati, jadi "at-least-once" menjadi "efektif sekali".

### 5. Dead-letter queue

Sebagian tugas gagal tiap kali — data buruk, record yang hilang permanen. Mengulang selamanya menyumbat queue. Setelah beberapa percobaan gagal, pindahkan message ke **dead-letter queue** (tempat samping) supaya queue utama terus mengalir dan manusia bisa memeriksa kegagalannya nanti.

```
attempt 1 ❌ → retry
attempt 2 ❌ → retry
attempt 3 ❌ → move to DEAD-LETTER QUEUE (stop retrying; alert someone)
```

### Kapan memakai queue

| Situasi | Queue? |
|---|---|
| Pekerjaan samping lambat (email, resize gambar, panggilan AI, laporan) | ✅ ya — lakukan async |
| Meratakan lonjakan lalu lintas | ✅ ya — queue jadi penyangga |
| User harus melihat hasilnya pada request ini juga | 🚫 tidak — lakukan inline |
| Tulis CRUD sederhana dan cepat | 🚫 tidak — queue menambah kompleksitas tak perlu |

- ✅ Queue pekerjaan lambat, bisa diulang, "boleh selesai sesaat kemudian".
- ✅ Buat tiap consumer idempotent dan tambah dead-letter queue.
- 🚫 Jangan queue pekerjaan yang hasilnya dibutuhkan pemanggil *sekarang juga*.

## ⚠️ Kesalahan umum

- Consumer non-idempotent, sehingga delivery at-least-once menyebabkan email/tagihan ganda.
- Tak ada dead-letter queue, sehingga satu message beracun diulang selamanya dan memblokir yang lain.
- Menaruh pekerjaan yang user butuh segera ke queue, sehingga mereka tak pernah melihat hasilnya pada request itu.
- Kehilangan message dengan mengack *sebelum* pekerjaan berhasil (ack hanya setelah sukses).
- Menganggap urutan ketat; kebanyakan queue tak menjaminnya — rancang supaya urutan tak penting, atau pakai queue terurut.

:::revoshop
Modul 5 menambah queue berbasis Redis ke RevoShop. (1) Langkah checkout mana yang sebaiknya async — mengirim email struk, memberi tahu penjual, membuat PDF invoice — versus mana yang harus inline (memesan stok, mengambil pembayaran)? (2) Webhook Midtrans dan worker struk keduanya bisa jalan dua kali; apakah penanganan RevoShop idempotent (apakah duplikat mengubah saldo atau mengirim dua email)? (3) Kalau job invoice gagal karena record hilang, apa yang harus terjadi setelah beberapa retry?
:::

## 🏆 Praktik terbaik

- [ ] Pindahkan pekerjaan samping lambat yang bisa diulang dari jalur request ke queue; balas seketika.
- [ ] Buat tiap consumer idempotent (dedupe berdasarkan message id di penyimpanan bersama).
- [ ] Ack sebuah message hanya *setelah* pekerjaan berhasil.
- [ ] Tambah dead-letter queue dengan batas max-attempts dan alerting.
- [ ] Jaga message tetap kecil (id dan penunjuk, bukan payload raksasa).
- [ ] Jangan bergantung pada urutan kecuali queue menjaminnya; rancang untuk out-of-order.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan message queue dengan analogi rel-pesanan-warung. Lalu jelaskan, dalam dua kalimat, kenapa delivery at-least-once berarti worker-mu harus idempotent.

## 📐 Rancang

Tombol "lamar ke 20 pekerjaan" CareerPilot harus terasa instan, tapi tiap lamaran memicu pekerjaan lambat: menyesuaikan CV dengan panggilan AI, mengirim email konfirmasi, dan memperbarui hitungan dashboard. Rancang alur async: apa yang dilakukan request web versus apa yang dilakukan worker, bagaimana kamu menjaga langkah AI/email aman di bawah delivery at-least-once, dan apa yang terjadi saat panggilan AI untuk satu pekerjaan gagal berulang.

:::quiz
Tampilkan satu rancangan yang mungkin

**Request web (producer):** validasi 20 pekerjaan, tulis 20 baris `application` dengan status `queued`, enqueue 20 message seperti `{"id": "app_1001", "type": "process_application"}`, dan balas seketika ("memproses lamaranmu"). Tak ada pekerjaan lambat inline.

**Worker (consumer):** masing-masing menarik message dan melakukan langkah lambat — penyesuaian CV AI, kirim email, naikkan hitungan dashboard — lalu ack.

**Keamanan at-least-once:** tiap worker idempotent, berkunci pada id lamaran: kalau `app_1001` sudah `done`, lewati. Kirim email dan update hitungan juga dedupe pada id itu, jadi message yang dikirim ulang tak mengirim dua email atau menghitung ganda.

**Kegagalan berulang:** ulang langkah AI beberapa kali (dengan backoff — pelajaran berikutnya); setelah max attempts, pindahkan `app_1001` ke **dead-letter queue**, tandai barisnya `failed`, dan beri alert. 19 sisanya terus mengalir.

**Aturan yang ditunjukkan:** balas seketika, lakukan pekerjaan lambat di worker idempotent, dan dead-letter tugas yang tak akan sukses supaya satu tugas buruk tak memblokir sisanya.
:::

### 📝 Checklist review mandiri

- [ ] Hanya pekerjaan lambat/bisa-diulang yang di-queue; user mendapat balasan instan
- [ ] Consumer idempotent, berkunci pada id stabil
- [ ] Ack terjadi setelah sukses; kegagalan diulang lalu dead-letter
- [ ] Satu tugas gagal tak memblokir yang lain

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/architecture/h-distributed-systems/02-queue-consumer" ai="no-ai" title="Queue FIFO, consumer idempotent, dan dead-letter queue"}
Implementasikan queue FIFO kecil, consumer idempotent yang melewati message yang sudah diproses (supaya delivery at-least-once tak menagih ganda), dan runner retry-dengan-dead-letter yang mengulang handler gagal sampai batas sebelum men-dead-letter-nya. Tes memutar ulang message duplikat dan satu yang gagal permanen.
:::

:::hints
- `Queue`: list dengan `enqueue(msg)` menambah dan `dequeue()` mengambil dari depan (`pop(0)`), mengembalikan `None` saat kosong.
- `consume_idempotently(processed, handler, message)`: kalau `message["id"]` ada di `processed`, kembalikan `"duplicate"` tanpa memanggil handler; kalau tidak panggil handler, tambah id, kembalikan `"processed"`.
- `process_with_retries(handler, message, max_attempts)`: panggil handler dalam loop; handler yang raise berarti "gagal". Kembalikan `("done", attempts)` saat sukses atau `("dead-letter", attempts)` kalau semua attempt gagal.
:::

## ✅ Cek cepat

:::quiz
Kenapa menaruh pekerjaan lambat di queue menjaga situsmu tetap cepat saat lonjakan lalu lintas?

Request web hanya menjatuhkan message kecil dan membalas seketika, jadi user tak pernah menunggu pekerjaan lambat. Lonjakan hanya membuat queue lebih panjang; worker menguras dengan kecepatan mereka sendiri (dan kamu bisa menambah lebih banyak), alih-alih jalur request kelebihan beban dan crash.
:::

:::quiz
Queue mengirim at-least-once. Apa yang dipaksa itu untuk kamu bangun di tiap consumer, dan kenapa?

Idempotency: karena message yang sama bisa terkirim lebih dari sekali (mis. worker crash sebelum ack), consumer harus mendeteksi tugas yang sudah ditangani dan melewatinya — kalau tidak kamu dapat email, tagihan, atau hitungan ganda.
:::

## 📚 Lanjut belajar

- [AWS SQS: how queues work](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/welcome.html)
- [AWS: dead-letter queues](https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-dead-letter-queues.html)
- [Enterprise Integration Patterns: message queues](https://www.enterpriseintegrationpatterns.com/patterns/messaging/Message.html)

---
title: "Parameter Store & Secrets Manager"
summary: "Kelola konfigurasi runtime dan rahasia di AWS — Parameter Store dan KMS, IAM per-path, rotasi Secrets Manager, injeksi ke ECS dan EC2, cache di kode, rollout perubahan, dan audit."
sourceHash: 46e088ed2804
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- **SSM Parameter Store**: `String`, `StringList`, `SecureString`, standard vs advanced tier
- **KMS**: kunci AWS managed vs customer managed, dan apa yang `kms:Decrypt` benar-benar berikan
- **Path berjenjang** (`/revoshop/production/...`) dan **scoping IAM** per path
- **Secrets Manager**: rahasia JSON, **rotasi otomatis**, RDS managed password, cross-account sharing
- **Memasukkan nilai ke aplikasi**: ECS `secrets`, EC2 fetch script, Lambda extension, SDK dengan caching
- **Rollout perubahan**: kapan aplikasi yang sedang jalan melihat nilai baru
- **Audit** dengan CloudTrail dan perbandingan biaya

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Parameter Store** | Tempat AWS untuk menyimpan pengaturan, ada opsi untuk enkripsi |
| **SecureString** | Parameter yang disimpan terenkripsi, hanya bisa dibaca dengan kunci KMS |
| **KMS** | Layanan kunci AWS; `kms:Decrypt` adalah yang benar-benar membuka nilai |
| **Path** | Nama berjenjang (`/revoshop/production/jwt`) yang bisa kamu gunakan untuk beri akses |
| **Secrets Manager** | Layanan lebih mahal untuk rahasia yang bisa diganti otomatis sesuai jadwal |
| **Rotation** | Mengganti rahasia dengan yang baru sesuai jadwal |
| **Injection** | Platform memasukkan rahasia ke environment aplikasi saat startup |
| **Caching** | Menyimpan nilai yang sudah diambil di memori untuk beberapa waktu, jadi tidak perlu minta terus |
| **CloudTrail** | Catatan siapa yang memanggil API AWS apa, termasuk pembacaan rahasia |

## 🧠 Ide besarnya

Parameter Store itu seperti **lemari arsip dengan label**:

- laci per aplikasi dan environment (`/revoshop/production/`),
- beberapa folder dikunci dengan kunci (SecureString + KMS),
- dan penjaga (IAM) yang mengecek laci mana yang boleh kamu buka.

Secrets Manager itu seperti **layanan safe deposit bank**: lebih mahal per box, tapi bisa **mengubah kombinasi kunci sesuai jadwal** (rotasi) dan memberitahu siapa saja yang berhak dengan kunci yang baru.

## ❓ Kenapa ini penting

`JWT_SECRET_KEY` RevoShop, kredensial database, dan kunci server Midtrans harus sampai ke ECS task, EC2 host, dan Lambda function tanpa pernah tersimpan di Git, image, task definition, atau chat. Kamu juga perlu tahu **siapa yang membacanya**, dan bisa **mengubahnya** tanpa downtime.

Kalau asal-asalan:

- Rahasia ditulis sebagai nilai plain `environment` di task definition → siapa saja yang bisa jalankan `ecs:DescribeTaskDefinition` bisa lihatnya.
- Satu IAM policy dengan `ssm:GetParameter*` di `*` → staging task bisa baca production secret.
- Database password dirotasi, tapi running task masih pakai yang lama, jadi setiap koneksi baru gagal setelah password lama tidak berlaku.
- Parameter bernama `jwt`, `JWT`, `prod-jwt-new-final` — dan tidak ada yang tahu mana yang dipakai sekarang.

## 📖 Langkah demi langkah

### 1. Parameter Store

| Tipe | Dipakai untuk |
|---|---|
| `String` | non-secret config (`APP_ENV`, `WEB_CONCURRENCY`, `API_IMAGE` digest) |
| `StringList` | daftar terpisah koma |
| `SecureString` | rahasia, dienkripsi dengan KMS |

| Tier | Batas | Biaya |
|---|---|---|
| **Standard** | 10.000 parameter, nilai 4 KB | tidak ada biaya penyimpanan (API calls punya batas dan harga untuk throughput lebih tinggi) |
| **Advanced** | nilai lebih besar (8 KB), policy (kedaluwarsa, notifikasi) | dibayar per parameter per bulan |

```bash
aws ssm put-parameter --name /revoshop/production/JWT_SECRET_KEY --type SecureString --value "$(openssl rand -hex 32)" --overwrite
aws ssm get-parameters-by-path --path /revoshop/production/ --recursive --with-decryption
aws ssm get-parameter-history --name /revoshop/production/JWT_SECRET_KEY   # versions and who changed them
```

Konvensi nama: `/<app>/<environment>/<NAME>` dengan huruf besar gaya env-var → mapping ke environment variable jadi trivial (latihan 05).

### 2. KMS dalam satu paragraf

Nilai SecureString dienkripsi dengan kunci KMS: kunci **AWS managed** `alias/aws/ssm` (sederhana, tidak perlu urus key policy) atau **customer managed key** (kamu urus key policy, bisa grant cross-account, pengaturan rotasi; biaya per kunci per bulan ditambah request). Membaca SecureString perlu **keduanya** `ssm:GetParameter*` di parameter **dan** `kms:Decrypt` di kunci — scope `kms:Decrypt` dengan `kms:ViaService` atau ke ARN kunci spesifik.

### 3. IAM per path

Path mengubah satu lemari menjadi laci terpisah: badge staging membuka `/revoshop/staging/*` dan tidak ada yang lain. Tanpa path, setiap badge adalah master key.

```json
{
  "Effect": "Allow",
  "Action": ["ssm:GetParameters", "ssm:GetParameter"],
  "Resource": "arn:aws:ssm:ap-southeast-1:123456789012:parameter/revoshop/production/*"
}
```

- Role staging dapat `/revoshop/staging/*` saja.
- Manusia yang deploy tidak perlu *membaca* production secret — hanya CI/role yang menyuntik nilainya.
- Deny `ssm:PutParameter` di production path untuk semua kecuali grup admin kecil atau pipeline IaC.

### 4. Secrets Manager

| Fitur | Detail |
|---|---|
| Nilai secret | teks atau JSON (`{"username": …, "password": …}`) |
| Rotasi | Lambda-based rotation sesuai jadwal; **RDS/Aurora managed master password** rotate tanpa kamu menulis Lambda code |
| Versi | staging label `AWSCURRENT`, `AWSPREVIOUS`, `AWSPENDING` saat rotasi |
| Replication | multi-region secret |
| Biaya | per secret per bulan + per 10.000 API call |

Pedoman praktis: **Secrets Manager** untuk kredensial yang harus rotate (database password, kredensial pihak ketiga dengan API rotasi); **Parameter Store SecureString** untuk rahasia statis dan konfigurasi (kunci JWT signing, feature flag).

### 5. Memasukkan nilai ke kode yang sedang jalan

Dua cara masuk: platform memasukkan nilai ke environment aplikasi saat startup (sederhana, tapi perubahan perlu restart), atau aplikasi minta saat jalan dan ingat untuk beberapa menit (lebih fleksibel, tapi harus urus failure dan caching).

| Platform | Mekanisme | Ambil perubahan |
|---|---|---|
| **ECS** | task definition `secrets` → env var saat task start (JSON key didukung: `arn:…:secret:name-AbCdEf:password::`) | hanya **task baru** — force deployment baru |
| **EC2** | fetch saat deploy (Lab 3 `fetch-env.sh`) ke file `600` | deploy berikutnya |
| **Lambda** | AWS Parameters and Secrets Lambda Extension (cache lokal) atau SDK + cache in-memory | setelah cache TTL |
| **App code (any)** | SDK dengan TTL cache dan fallback stale (latihan 05) | setelah TTL |

### 6. Rotasi tanpa downtime

Mengubah kunci saat orang masih di dalam hanya bisa kalau kedua kunci membuka pintu untuk beberapa waktu. Itulah kenapa rotasi terjadi dalam dua langkah: tambah rahasia baru, biarkan semua ambilnya, lalu keluarkan yang lama.

**Rotasi password database (dua user)**: simpan dua database user (atau andalkan versioning managed rotation); rotate satu saat aplikasi pakai yang lain; roll task; rotate yang lain.

**Rotasi kunci JWT signing**: sign dengan kunci baru, verify dengan kedua-duanya lebih lama dari token lifetime terpanjang, baru keluarkan kunci lama.

**Kunci API pihak ketiga (Midtrans)**: buat kunci baru di dashboard provider → update parameter → force deployment ECS baru → verifikasi pembayaran → revoke kunci lama.

### 7. Audit dan kebersihan

- CloudTrail catat `GetParameter`, `GetSecretValue`, `PutParameter` dengan principal yang memanggil — berguna setelah incident (nilai tidak dicatat).
- Tag parameter/secret (`Project`, `Env`, `Owner`, `Rotation=90d`).
- Jangan pernah kirim rahasia di command line di environment bersama (terlihat di process list dan shell history) — baca dari file, stdin, atau SDK.

### Pilih setup-mu

Setiap opsi di sini adalah trade-off:

| Pilihan | ✅ | ❌ |
|---|---|---|
| Parameter Store Standard | sederhana, praktis gratis untuk aplikasi kecil | tidak ada rotasi bawaan; nilai 4 KB |
| Secrets Manager | rotasi, JSON secret, integrasi RDS | biaya per-secret per bulan |
| AWS managed KMS key | nol management | tidak ada key policy control atau cross-account sharing |
| Customer managed KMS key | kontrol, cross-account, audit per key | biaya dan tanggung jawab key policy |
| Inject at start (ECS) | tidak ada perubahan kode | perubahan perlu task baru |
| Load in code with cache | perubahan diambil tanpa redeploy | kode, caching, dan failure handling |

- ✅ Setiap nilai spesifik environment yang tidak dikompilasi ke image.
- ✅ Secrets Manager untuk rotating credential; Parameter Store untuk sisanya.
- 🚫 Jangan pakai keduanya sebagai database key-value umum atau untuk read berkecepatan tinggi tanpa caching.
- 🚫 Jangan simpan rahasia di parameter `String` "cuma untuk sekarang".

## ⚠️ Kesalahan umum

- Update parameter dan lupa task ECS yang sedang jalan masih punya nilai lama.
- Policy yang beri `ssm:GetParametersByPath` di `/` (setiap parameter di akun).
- Pakai parameter yang sama untuk staging dan production.
- Log dictionary konfigurasi saat startup (dengan rahasia di dalamnya).

:::revoshop
1. **Tree parameter-mu.** Tulis daftar lengkap untuk RevoShop: `/revoshop/production/{DATABASE_URL, JWT_SECRET_KEY, MIDTRANS_SERVER_KEY, MIDTRANS_CLIENT_KEY, MIDTRANS_IS_PRODUCTION, WEB_CONCURRENCY}` dan yang staging. Tandai setiap satu sebagai `String` atau `SecureString`, dan putuskan apakah `DATABASE_URL` tetap URL lengkap di SSM atau menjadi referensi Secrets Manager ke RDS-managed secret (latihan 05's `resolve_references`).
2. **Midtrans client key.** `MIDTRANS_CLIENT_KEY` dipakai frontend untuk buka popup Snap — apa itu rahasia? Apa yang terjadi kalau kamu simpan sebagai SecureString saja?
3. **Drill rotasi JWT.** Flask-JWT-Extended sign dengan `JWT_SECRET_KEY` di `config/base.py`. Rancang rotasi yang tidak logout semua user: setting mana yang pegang kunci lama, berapa lama kamu simpan (hint: `JWT_REFRESH_TOKEN_EXPIRES` adalah 7 hari di production), dan perubahan kode apa yang verify dengan dua kunci perlu (`@jwt.decode_key_loader`)?
4. **Lab 3 → Lab 4.** Di EC2 kamu tulis `.env.production` dari SSM saat deploy. Di ECS, task definition's `secrets` lakukan hal yang sama saat task start. Setelah ubah `/revoshop/production/MIDTRANS_SERVER_KEY`, perintah apa yang buat production ambilnya, dan gimana verifikasi tanpa print kunci?
5. **Audit.** Temukan `GetParametersByPath` call-mu sendiri dari Lab 3 di CloudTrail event history. Principal mana yang membuatnya (session name instance role mengandung instance ID)?
:::

## 🏆 Praktik terbaik

- [ ] Hirarki konsisten `/app/env/NAME`; environment strictly terpisah.
- [ ] SecureString (atau Secrets Manager) untuk setiap rahasia; `String` cuma untuk non-secret config.
- [ ] IAM scoped per path dan environment; `kms:Decrypt` scoped per key atau `kms:ViaService`.
- [ ] Rencana rotasi per rahasia; managed rotation untuk RDS master password.
- [ ] Inject via platform mechanism; force deployment baru setelah perubahan (atau pakai TTL caching di kode).
- [ ] Least orang/role bisa baca production secret; CI deploy tanpa manusia baca nilai.
- [ ] Tag dan CloudTrail monitoring; parameter history untuk track perubahan.
- [ ] Manage parameter *definitions* di IaC (nilai dari sumber aman, tidak di-commit).

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan analogi lemari arsip vs layanan safe deposit bank, dan kenapa "kita ubah parameter" tidak berarti "production pakai nilai yang baru".

## 📐 Rancang

Rancang sistem konfigurasi dan rahasia RevoShop untuk staging dan production di ECS: store dan tipe per nilai, kunci KMS, policy IAM untuk execution role, task role, GitHub OIDC deploy role dan admin manusia, prosedur rotasi untuk RDS password dan kunci JWT, dan gimana nilai yang berubah di-rollout dan diverifikasi.

:::quiz
Lihat contoh rancangan

| Nilai | Store | Catatan |
|---|---|---|
| RDS master password | Secrets Manager (RDS-managed, rotasi on) | dipakai cuma oleh migration task definition |
| `revoshop_app` DB password | Secrets Manager `revoshop/production/db-app` dengan Lambda rotasi **atau** SSM SecureString di-rotasi triwulanan dengan prosedur dua-user | di-inject sebagai `DB_PASSWORD`; aplikasi build `DATABASE_URL` dengan host dari parameter `String` |
| `JWT_SECRET_KEY` (+ `JWT_PREVIOUS_SECRET_KEY` saat rotasi) | SSM SecureString | rotasi tahunan dengan dual verification 7+ hari |
| `MIDTRANS_SERVER_KEY` | SSM SecureString | di-rotasi saat ganti staff |
| `MIDTRANS_CLIENT_KEY`, `APP_ENV`, `WEB_CONCURRENCY`, `DB_HOST` | SSM String | bukan rahasia |

- **KMS:** AWS managed `alias/aws/ssm` untuk kesederhanaan (single akun); customer managed key kalau staging dan production pernah split ke akun terpisah.
- **Execution role (per env):** `ssm:GetParameters` di `/revoshop/<env>/*`, `secretsmanager:GetSecretValue` di secret `revoshop/<env>/*`, `kms:Decrypt` via SSM/Secrets Manager.
- **Task role:** tidak ada akses SSM/Secrets (nilai di-inject).
- **GitHub deploy role:** tidak ada akses baca nilai rahasia; `iam:PassRole` untuk execution role; `ecs:RegisterTaskDefinition` referensikan ARN saja.
- **Admin manusia:** `PutParameter` di production path cuma via break-glass role dengan MFA; semua orang lain read-only nama saja (`ssm:DescribeParameters`), bukan nilai.
- **Rollout:** ubah nilai → `aws ecs update-service --force-new-deployment` → tunggu `services-stable` → verifikasi behavior (misal charge Midtrans sandbox) → cek CloudTrail bahwa task baca versi baru (`GetParameters` event setelah perubahan).
:::

### 📝 Checklist review mandiri

- [ ] Environment tidak bisa baca rahasia satu sama lain
- [ ] Deployer tidak perlu lihat nilai rahasia
- [ ] Setiap rotasi punya prosedur tanpa-downtime

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m5/w4/05-ssm-config-loader" ai="no-ai" title="Config dari Parameter Store dan Secrets Manager"}
Muat hirarki parameter secara rekursif dengan decryption dan pagination ke key yang aman seperti environment, resolve referensi `secretsmanager:` (ambil setiap secret sekali), dan cache konfigurasi dengan TTL dan fallback stale yang dibatasi — ditest dengan moto.
:::

:::hints
- `ssm.get_paginator("get_parameters_by_path")` urus `NextToken` untukmu.
- `rpartition("#")` pisah secret id dari JSON key walaupun ARN punya karakter lain.
- Simpan load time cuma saat load berhasil.
:::

## ✅ Cek cepat

:::quiz
Task definition ECS referensikan `/revoshop/production/JWT_SECRET_KEY` sebagai secret. Kamu update parameter. Kapan user lihat efeknya?

Cuma task yang dimulai **setelah** perubahan dapat nilai baru — force deployment baru jadi semua task ganti.
:::

:::quiz
Kenapa baca parameter SecureString butuh dua permission?

`ssm:GetParameter` izinkan baca parameter, dan `kms:Decrypt` di kunci KMS-nya izinkan decrypt nilai; tanpa yang kedua, kamu cuma dapat error akses untuk decryption.
:::

## 📚 Lanjut belajar

- [AWS docs: Parameter Store](https://docs.aws.amazon.com/systems-manager/latest/userguide/systems-manager-parameter-store.html) · [Restricting access by path](https://docs.aws.amazon.com/systems-manager/latest/userguide/sysman-paramstore-access.html)
- [AWS docs: Secrets Manager rotation](https://docs.aws.amazon.com/secretsmanager/latest/userguide/rotating-secrets.html)
- [AWS docs: Parameters and Secrets Lambda Extension](https://docs.aws.amazon.com/secretsmanager/latest/userguide/retrieving-secrets_lambda.html)

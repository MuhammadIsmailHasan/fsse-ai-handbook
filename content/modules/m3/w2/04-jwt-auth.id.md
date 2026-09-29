---
title: "JWT Authentication"
summary: Auth tanpa-state untuk layanan FastAPI — bagaimana JWT bertanda tangan membawa identitas user, kenapa server mempercayainya lewat pengecekan tanda tangan (tanpa lookup DB), cara kerja kedaluwarsa, dan bagaimana dependency get_current_user mengubah token jadi user.
sourceHash: b26114ef0df1
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Apa itu **JWT** dan tiga bagiannya
- Kenapa **tanda tangan** membuat server percaya token tanpa database
- Alur login → token → `Authorization: Bearer`
- **Kedaluwarsa** dan kenapa token berumur pendek penting
- Mengubah token jadi user dengan dependency `get_current_user`
- Trade-off jujur: JWT sulit dicabut

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **JWT** | Token bertanda tangan yang membawa claim (data) |
| **Claim** | Sepotong data di dalam token (mis. id user) |
| **Tanda tangan** | Bukti token tak dirusak |
| **Secret** | Kunci yang dipakai menandatangani/memverifikasi |
| **Stateless** | Server tak menyimpan penyimpanan sesi |
| **Bearer** | Skema header yang membawa token |
| **exp** | Claim waktu kedaluwarsa |

## 🧠 Ide besarnya

JWT seperti **gelang festival**. Di gerbang (login) kamu membuktikan siapa dirimu sekali dan mendapat gelang tahan-rusak yang dicap penyelenggara (**tanda tangan**). Di dalam, tiap kios cukup melirik gelang — mereka tak menelepon gerbang depan untuk mengecek, karena gelang palsu atau diubah jelas terlihat. Gelang itu sendiri membawa siapa dirimu dan kapan ia kedaluwarsa.

## ❓ Kenapa ini penting

API perlu tahu *siapa* yang memanggil pada tiap request, tapi mengecek ulang password tiap kali mustahil dan lambat. JWT menyelesaikan ini: setelah satu login, klien membawa token bertanda tangan yang membuktikan identitasnya. Server memverifikasi **tanda tangan** dengan **secret**-nya — tanpa lookup database — jadi auth berskala murah dan tanpa-state. Kamu memakai JWT + RBAC di RevoShop (Flask); konsepnya identik di FastAPI, disambungkan lewat dependency.

## 📖 Langkah demi langkah

### 1. Apa isi JWT

Tiga bagian dipisah titik: `header.payload.signature`.

- **Header**: algoritmanya (mis. `HS256`).
- **Payload**: **claim** — `sub` (subjek/id user), `exp` (kedaluwarsa), mungkin `role`.
- **Signature**: `HMAC(header.payload, secret)` — membuktikan dua bagian pertama tak diubah.

Payload hanya **di-base64, bukan dienkripsi** — siapa pun bisa membacanya. Jadi jangan pernah menaruh rahasia (password) di JWT; ia membuktikan identitas, ia tak menyembunyikan data.

### 2. Tanda tangan adalah kepercayaannya

Server menandatangani dengan **secret** yang hanya ia tahu. Untuk memverifikasi, ia menghitung ulang tanda tangan atas `header.payload` yang diterima dan membandingkan. Kalau seseorang mengubah payload (misalnya `role: admin`), tanda tangannya tak cocok dan token ditolak. Itulah kenapa server bisa **mempercayai claim tanpa lookup database** — tanda tangan menjamin integritas.

### 3. Alur login

```
1. POST /login {email, password}  → server checks credentials (once)
2. server signs a JWT: {"sub": user_id, "exp": now+15min}  → returns access_token
3. client stores the token, then on each request sends:
   Authorization: Bearer <token>
4. server verifies signature + exp, reads sub → knows the user
```

### 4. Kedaluwarsa (exp) dan refresh

Token membawa claim **`exp`** dan dicek pada tiap request; token kedaluwarsa ditolak. Jaga access token **berumur pendek** (menit) supaya token yang dicuri hanya berguna sebentar. Sesi lebih panjang memakai **refresh token** berumur panjang terpisah untuk mendapat access token baru (pola RevoShop).

### 5. Sambungkan dengan dependency

Persis `get_current_user` dari pelajaran DI, kini mendekode JWT:

```python
def get_current_user(authorization: str | None = Header(default=None)):
    token = _bearer(authorization)                 # 401 if missing/malformed
    payload = decode_and_verify(token, SECRET)     # 401 if bad signature or expired
    return load_user(payload["sub"])
```

Endpoint terproteksi menambah `user = Depends(get_current_user)` — satu tempat untuk semua auth.

### 6. Trade-off jujur: pencabutan

Karena server tak menyimpan penyimpanan sesi, ia tak bisa mudah **mencabut** token sebelum kedaluwarsa (logout di mana-mana, ban user seketika). Mitigasi: kedaluwarsa pendek, deny-list kecil berisi id token yang dicabut, atau mengecek "versi token" per user. Statelessness adalah manfaat *sekaligus* biayanya.

### Pilih setup auth-mu

| Kebutuhan | Lakukan ini |
|---|---|
| Identifikasi pemanggil murah per request | JWT diverifikasi lewat tanda tangan |
| Batasi kerusakan token dicuri | `exp` pendek (menit) |
| Sesi lebih panjang | alur refresh token |
| Logout/ban seketika | deny-list atau cek versi-token |
| Sembunyikan data | ❌ bukan JWT — ia terbaca; pakai HTTPS + jangan taruh rahasia di dalamnya |

- ✅ Tandatangani dengan secret kuat; verifikasi tanda tangan dan `exp` tiap request.
- ✅ Jaga access token berumur pendek; pusatkan auth di dependency.
- 🚫 Jangan pernah simpan password/rahasia di payload; jangan pernah percaya token yang belum diverifikasi.

## ⚠️ Kesalahan umum

- Menaruh data sensitif di payload (ia terbaca — hanya di-base64).
- Tak mengecek `exp`, sehingga token lama berlaku selamanya.
- Secret lemah atau bocor — siapa pun dengannya bisa memalsukan token.
- Mempercayai payload tanpa memverifikasi tanda tangan.
- Mengira kamu bisa mencabut JWT seketika (tak bisa, tanpa mesin tambahan).

:::revoshop
RevoShop memakai flask-jwt-extended (JWT + RBAC). (1) Temukan di mana ia menerbitkan token saat login dan di mana ia memproteksi route — di FastAPI ini menjadi endpoint `/login` dan `get_current_user`. (2) Claim apa yang RevoShop taruh di token (id user, role)? (3) Bagaimana RevoShop menangani kedaluwarsa/refresh, dan apa yang akan ia lakukan untuk memaksa logout meski JWT tanpa-state?
:::

## 🏆 Praktik terbaik

- [ ] Tandatangani token dengan kunci rahasia kuat di config/secrets, jangan pernah di kode.
- [ ] Verifikasi tanda tangan dan `exp` pada tiap request (lewat `get_current_user`).
- [ ] Jaga access token berumur pendek; pakai refresh token untuk sesi lebih panjang.
- [ ] Taruh hanya claim non-sensitif (id user, role) di payload.
- [ ] Punya strategi pencabutan (exp pendek + deny-list atau versi-token) kalau butuh logout seketika.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan JWT dengan analogi gelang-festival, termasuk kenapa kios tak menelepon gerbang (tanda tangan). Lalu katakan kenapa kamu tak boleh menaruh password di payload.

## 📐 Rancang

Rancang autentikasi untuk API CareerPilot: endpoint `/login`, apa yang masuk ke token, bagaimana endpoint terproteksi mengeceknya, pilihan kedaluwarsa, dan bagaimana kamu mendukung "logout dari semua perangkat" meski JWT tanpa-state.

:::quiz
Tampilkan satu rancangan yang mungkin

- **`POST /login`**: verifikasi email+password sekali; saat sukses tandatangani JWT `{"sub": user_id, "role": ..., "exp": now+15min}` dan kembalikan `access_token` (plus refresh token berumur lebih panjang).
- **Isi token**: `sub` (id user) dan `role` untuk RBAC — tanpa password atau data sensitif (payload terbaca).
- **Endpoint terproteksi**: `user = Depends(get_current_user)`, yang memverifikasi tanda tangan dan `exp` dan memuat user; cek peran lewat dependency `require_admin`.
- **Kedaluwarsa**: access token pendek (15 menit) membatasi jendela token yang dicuri; refresh token menerbitkan yang baru.
- **Logout di mana-mana**: karena JWT tanpa-state, simpan **versi token** per-user (atau timestamp `tokens_valid_after`) di DB; sertakan di token dan tolak token yang versinya basi. Menaikkan versi seketika membatalkan semua token yang ada.

**Aturan yang ditunjukkan:** JWT tanpa-state diverifikasi tanda tangan + kedaluwarsa pendek untuk auth murah, plus versi-token/deny-list saat kamu benar-benar butuh pencabutan seketika.
:::

### 📝 Checklist review mandiri

- [ ] Login menerbitkan token bertanda tangan berumur pendek dengan claim aman saja
- [ ] Tiap route terproteksi memverifikasi tanda tangan + kedaluwarsa lewat dependency
- [ ] Cek peran ditangani dependency
- [ ] Strategi pencabutan ada untuk logout seketika

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/m3/w2/04-jwt" ai="no-ai" title="Tandatangani dan verifikasi token dengan tangan"}
Bangun token ala JWT minimal dengan pustaka standar Python: `sign(payload, secret)` menghasilkan `base64(payload).base64(hmac)`, dan `verify(token, secret, now)` menghitung ulang tanda tangan (menolak perusakan) dan mengecek claim `exp` (menolak yang kedaluwarsa). Tes merusak token, memakai secret salah, dan mengedaluwarsakan token — semua harus ditolak.
:::

:::hints
- Pakai `json`, `hmac`, `hashlib`, `base64` (urlsafe, buang padding `=`), dan oper `now` untuk determinisme.
- `sign`: `body = b64(json(payload))`; `sig = b64(hmac_sha256(secret, body))`; kembalikan `f"{body}.{sig}"`.
- `verify`: split di `.`; hitung ulang sig dengan `hmac.compare_digest`; raise saat tak cocok; decode payload; kalau `payload["exp"] <= now` raise; kembalikan payload.
- Raise exception jelas (mis. `ValueError`) untuk token yang dirusak/kedaluwarsa/secret salah.
:::

## ✅ Cek cepat

:::quiz
Kenapa server bisa mempercayai claim JWT tanpa mencari token di database?

Karena token ditandatangani dengan secret yang hanya server tahu. Server menghitung ulang tanda tangan atas header+payload yang diterima; kalau cocok, token asli dan tak diubah, jadi ia mempercayai claim-nya (seperti id user) langsung — tanpa perjalanan bolak-balik ke database.
:::

:::quiz
Kenapa kamu tak boleh menaruh password atau rahasia di payload JWT?

Payload hanya di-base64, bukan dienkripsi — siapa pun yang memegang token bisa membacanya. JWT membuktikan identitas lewat tanda tangannya; ia tak menyembunyikan isinya. Taruh hanya claim non-sensitif (id user, role) di dalamnya.
:::

## 📚 Lanjut belajar

- [jwt.io — introduction to JSON Web Tokens](https://jwt.io/introduction)
- [FastAPI: OAuth2 with JWT](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)
- [OWASP: JWT security cheatsheet](https://cheatsheetseries.owasp.org/cheatsheets/JSON_Web_Token_for_Java_Cheat_Sheet.html)

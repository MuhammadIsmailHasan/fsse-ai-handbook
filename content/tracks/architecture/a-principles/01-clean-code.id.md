---
title: "Kode Bersih: Nama, Fungsi Kecil, Maksud Jelas"
summary: Tulis kode yang teman kerjamu (atau kamu di 3 bulan) mengerti dalam sekali baca — penamaan, ukuran fungsi, komentar yang berarti.
sourceHash: 8548d4a265fd
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Kenapa kode dibaca jauh lebih sering daripada ditulis
- Aturan penamaan yang menghilangkan kebutuhan akan sebagian besar komentar
- Membuat fungsi tetap kecil dan berada di **satu tingkat abstraksi**
- Komentar mana yang membantu dan mana yang merugikan
- Refactor dengan aman: test dulu, langkah-langkah kecil

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Kode bersih** | Kode yang orang berikutnya mengerti dalam sekali baca |
| **Intent** | Apa yang ingin dilakukan kode, bukan caranya |
| **Level of abstraction** | Seberapa detail kode dilihat: strategi vs detail kecil |
| **Guard clause** | Tangani kasus khusus dulu dan return cepat |
| **Magic number** | Angka tanpa penjelasan dalam kode (`* 0.11`) |
| **Refactor** | Merapikan kode tanpa mengubah perilakunya |
| **Code smell** | Tanda bahwa ada masalah di kode |

## 🧠 Ide besarnya

Kode punya dua penonton: **komputer** (yang menjalankan apapun yang valid) dan **manusia** (yang harus mengerti, mengubah, dan memperbaikinya). Kode bersih mengutamakan manusia.

Dapur yang bagus punya toples berlabel dan satu alat per laci. Kamu bisa masak di dapur yang berantakan juga — tapi setiap hidangan butuh waktu lebih lama, dan suatu hari orang ambil garam dari toples gula.

## ❓ Kenapa ini penting

- Tim menghabiskan sebagian besar waktu untuk **membaca** kode sebelum mengubahnya.
- Kode yang tidak jelas menyebabkan bug, karena orang salah pahami apa yang dilakukannya.
- Saat interview dan code review, keterbacaan dinilai seketat kesuksesan.

Ini argumen dapur yang sama: kamu *bisa* masak di dapur berantakan, tapi setiap hidangan butuh waktu lebih lama, dan suatu hari orang ambil garam dari toples gula.

## 📖 Langkah demi langkah

### 1. Nama yang menunjukkan maksud

Nama bagus menghemat komentar dan pertanyaan. `days_since_applied` tidak butuh penjelasan; `d` butuh paragraf.

```python
def total_discounted_revenue(orders: list[Order], minimum_amount: int) -> int:
    revenue = 0
    for order in orders:
        if order.is_paid and order.amount > minimum_amount:
            revenue += member_price(order) if order.is_member else order.amount
    return revenue
```

| Aturan | ❌ | ✅ |
|---|---|---|
| Bilang apa itu | `d`, `data`, `info` | `orders`, `job_listings` |
| Boolean dibaca ya/tidak | `flag`, `status` | `is_paid`, `has_access`, `can_edit` |
| Fungsi pakai kata kerja | `total()`, `user()` | `calculate_total()`, `find_user()` |
| Tanpa angka ajaib | `* 0.9` | `MEMBER_DISCOUNT = 0.10` |
| Istilah konsisten | `get_user`, `fetch_account`, `load_member` untuk ide yang sama | pilih satu: `get_…` |
| Panjang cocok lingkup | `the_list_of_all_active_users_in_system` | singkat di lingkup kecil (`i` di loop 3 baris), deskriptif di lingkup besar |

### 2. Fungsi kecil, satu pekerjaan

Fungsi harus melakukan **satu hal**, di **satu tingkat** detail:

```python
def import_jobs(path: str) -> ImportResult:
    rows = read_csv_rows(path)
    jobs = [parse_job(row) for row in rows]
    valid_jobs = [job for job in jobs if is_valid(job)]
    save_jobs(valid_jobs)
    return ImportResult(imported=len(valid_jobs), skipped=len(jobs) - len(valid_jobs))
```

Kamu bisa membaca `import_jobs` seperti daftar isi. Detail tersimpan di helper yang punya nama bagus. Mencampur tingkatan — "buka file", lalu "hitung rata-rata gaji", lalu "format tanggal string" di satu fungsi — memaksa pembaca melompat antara gambaran besar dan detail kecil.

Tanda fungsi melakukan terlalu banyak: lebih panjang dari satu layar, punya beberapa "bagian" terpisah garis kosong, namanya butuh *dan*, atau dia ambil lebih dari ~4 parameter.

### 3. Komentar: jelaskan **kenapa**, bukan **apa**

```python
# ❌ Noise: repeats the code
i += 1  # increment i

# ❌ Lie waiting to happen: code changes, comment doesn't
# Returns the top 3 skills
def top_skills(n): ...

# ✅ Why: context the code can't express
# The payment provider retries webhooks for 24h, so we must ignore duplicates by event id.
if event.id in processed_event_ids:
    return
```

Kalau kamu perlu komentar untuk menjelaskan **apa** yang dilakukan sebagian kode, coba ekstrak jadi fungsi yang **namanya** bilang apa itu.

### 4. Guard clause dan kode datar

(Kamu sudah ketemu ini di pelajaran Conditionals.) Tangani kasus invalid dulu, jaga jalur utama tidak terindent.

### 5. Refactor dengan aman

Test dulu, lalu langkah-langkah kecil. Refactor tanpa test adalah rearrange dapur dalam gelap — mungkin lebih rapi, dan kamu tidak tahu apa yang rusak.

:term[Refactoring]{bahasa="refactoring — mengubah struktur kode tanpa mengubah perilakunya"} = mengubah struktur **tanpa** mengubah perilaku.

1. Pastikan **test** menutup perilakunya (tulis kalau kurang).
2. Ubah **satu** hal (rename, ekstrak fungsi).
3. Jalankan test.
4. Commit. Ulangi.

### Memilih pendekatanmu

Setiap pilihan di sini adalah trade-off:

| Pilihan | ✅ | ❌ |
|---|---|---|
| Banyak fungsi kecil | Nama bisa dibaca, test mudah | Terlalu banyak lompatan kalau dipotong mekanis (fungsi 3 baris dipakai sekali di mana-mana) |
| Nama panjang deskriptif | Self-documenting | Bisa jadi aneh — rename konsepnya saja |
| Refactor sekarang | Perubahan masa depan lebih mudah | Waktu sekarang; risiko tanpa test |
| "Jalan, jangan sentuh" | Tidak ada risiko langsung | Setiap perubahan masa depan jadi lebih lambat dan berisiko |

- ✅ Rename dan ekstrak kapan saja kamu baru saja mengerti kode yang membingungkan — tinggalkan lebih jelas dari saat kamu datang.
- ✅ Refactor **sebelum** menambah fitur ke kode yang berantakan, dengan test.
- 🚫 Jangan refactor kode tanpa test yang menutupnya.
- 🚫 Jangan campur refactor besar dan perubahan perilaku dalam satu commit/PR — reviewer tidak bisa bedakan.

## ⚠️ Kesalahan umum

- Singkatan hanya kamu mengerti (`usr_mgr_svc`).
- Nama yang bohong (`get_user()` yang juga buat satu).
- Blok komentar jelaskan kode berantakan daripada membersihkannya.
- File "utils.py" raksasa di mana semuanya masuk.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke orang non-programmer kenapa "kode yang jalan" beda dari "kode yang bagus", pakai analogi dari kehidupan sehari-hari mereka (dapur bersama, spreadsheet berantakan, tulisan tangan…).

## 📐 Rancang

Tulis ulang fungsi `calc(d, t)` dari atas pelajaran ini dengan nama bagus, konstanta bernama, dan — kalau perlu — fungsi helper kecil. Anggap setiap `x` tuple `(order_id, amount, is_paid, is_member)`.

:::quiz
Lihat kemungkinan penulisan ulang

```python
MEMBER_DISCOUNT_RATE = 0.9

def revenue_above(orders: list[tuple[str, int, bool, bool]], minimum_amount: int) -> float:
    revenue = 0.0
    for _order_id, amount, is_paid, is_member in orders:
        if is_paid and amount > minimum_amount:
            revenue += charged_amount(amount, is_member)
    return revenue

def charged_amount(amount: int, is_member: bool) -> float:
    return amount * MEMBER_DISCOUNT_RATE if is_member else amount
```

Unpack tuple ke nama menghilangkan setiap tebakan `x[2]`.
:::

### 📝 Checklist review mandiri

- [ ] Tidak ada nama satu huruf di luar loop kecil
- [ ] Diskon dipegang konstanta bernama
- [ ] Orang bisa baca fungsi tanpa komentar apapun

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/architecture/a-principles/01-clean-code" ai="no-ai" title="Refactor laporan berantakan"}
`report.py` punya satu fungsi 40 baris dengan nama aneh yang bikin laporan status aplikasi untuk CareerPilot. Testnya sudah lulus — **jaga tetap lulus** saat kamu refactor:

- rename semuanya untuk tunjuk maksud
- ganti nilai ajaib dengan konstanta
- ekstrak minimal 3 fungsi helper bernama bagus
- tidak ada fungsi lebih panjang dari 15 baris, tidak ada nama satu huruf kecuali `_` (test cek)
:::

:::hints
- Jalankan test setelah **setiap** perubahan kecil.
- Mulai dengan rename (paling aman), lalu ekstrak fungsi.
- Lihat "bagian" terpisah garis kosong — masing-masing kandidat fungsi.
:::

## ✅ Cek cepat

:::quiz
Apa bedanya refactor dan rewrite?

Refactor ubah struktur langkah kecil yang jaga perilaku, didukung test. Rewrite ganti kode, sering ubah perilaku, risiko jauh lebih tinggi.
:::

:::quiz
Kapan komentar lebih baik dari nama yang lebih baik?

Kapan komentar jelaskan **kenapa** — alasan bisnis, batasan eksternal, keputusan tidak jelas — yang kode sendiri tidak bisa bilang.
:::

## 📚 Lanjut belajar

- [PEP 8 — Style Guide for Python Code](https://peps.python.org/pep-0008/)
- [Ruff — a fast Python linter & formatter](https://docs.astral.sh/ruff/)

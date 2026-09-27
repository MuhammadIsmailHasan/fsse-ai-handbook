---
title: "Cek Penempatan Minggu 0"
summary: Tahu dalam 20 menit apakah kamu bisa lompat ke minggu berikutnya — jawab dari ingatan, tanpa catatan, tanpa AI.
sourceHash: d7ddc220eaed
---

Kamu mungkin pernah ketemu topik-topik ini sebelumnya. Cek ini memberi tahu apakah kamu perlu **belajar** Minggu 0 atau **langsung lihat** latihan-latihannya dan lanjut ke minggu berikutnya.

::::placement{id="modules/m1/w0"}
Tulis jawaban-mu (di kertas atau kotak catatan di bawah) **sebelum** membuka tiap-tiap jawaban.

:::quiz
1 · Kamu ketik `https://shop.example.com/products?page=2` dan tekan Enter. Sebutkan langkah-langkah utama sampai halaman tampil.

(1) Browser bertanya ke DNS berapa IP address `shop.example.com`. (2) Browser terhubung ke server itu (dengan TLS, karena `https`). (3) Browser kirim HTTP **GET** request untuk `/products` dengan query `page=2`. (4) Server jalankan kode, mungkin baca database, lalu beri balik **response** dengan status code (misalnya 200) dan isi (HTML atau JSON). (5) Browser render-nya.
:::

:::quiz
2 · Apa output dari `print("5" + 5)`, dan kenapa?

Tidak ada output — dia lempar `TypeError`. Di Python tidak bisa tambah `str` sama `int`. Konversi dulu: `int("5") + 5` → `10`, atau `"5" + str(5)` → `"55"`.
:::

:::quiz
3 · Berapa nilai dari `17 // 5`, `17 % 5`, dan `True and not False`?

`3` (bagi bulat), `2` (sisa bagi), `True`.
:::

:::quiz
4 · Tulis (di kertas) fungsi `category(code)` yang beri balik `"success"` untuk HTTP code 200–299, `"client error"` untuk 400–499, `"server error"` untuk 500–599, dan `"other"` untuk yang lain.

```python
def category(code: int) -> str:
    if 200 <= code <= 299:
        return "success"
    elif 400 <= code <= 499:
        return "client error"
    elif 500 <= code <= 599:
        return "server error"
    return "other"
```

Cek sendiri: apakah kamu pakai `elif` (jadi hanya satu cabang yang jalan) dan tangani "yang lain"?
:::

:::quiz
5 · Tulis loop yang beri balik total dari daftar harga, dan jelaskan apa yang harusnya terjadi untuk daftar kosong.

```python
def total(prices: list[float]) -> float:
    result = 0
    for price in prices:
        result += price
    return result
```

Daftar kosong beri balik `0` — isi loop tidak pernah jalan. (Python punya fungsi bawaan `sum(prices)` yang sama.)
:::

:::quiz
6 · Pesan error habis dengan `IndexError: list index out of range`. Apa artinya, dan kamu cari tahu dari mana dulu?

Kode-mu minta posisi yang tidak ada (misalnya `items[3]` di list 3 item — posisi yang sah hanya 0, 1, 2). Baca traceback **dari bawah ke atas**: baris-baris paling akhir tunjuk file dan nomor baris yang gagal.
:::
::::

:::tip[Nilai sendiri]
Lulus kalau kamu dapat **minimal 5 dari 6** dengan benar *dan* bisa jelaskan *kenapa*, bukan hanya *apa*. Kalau jawaban benar tapi hanya menebak, tidak dihitung.
:::

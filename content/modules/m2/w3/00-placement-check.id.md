---
title: "Cek Penempatan Minggu 3"
summary: Module 1 mengajarkan dasar Python. Cek ini menguji lapisan profesional — idiom, decorator, class, type hint, exception, dan packaging.
sourceHash: 1ff0cafd70e7
---

::::placement{id="modules/m2/w3"}
Jawab dari ingatan. Ini adalah pertanyaan Python yang benar-benar ditanyakan dalam wawancara backend dan code review.

:::quiz
1 · Apa perbedaan antara `is` dan `==`, dan apa yang salah dengan `def add(item, items=[])`?

`==` membandingkan nilai; `is` membandingkan identitas (object yang sama) dan harus dipakai untuk `None`. List default dibuat sekali saja dan **dibagikan di semua pemanggilan**, jadi item menumpuk antar panggilan — gunakan `items=None` dan buat list di dalamnya.
:::

:::quiz
2 · Tulis decorator `timed` yang mencetak berapa lama fungsi berjalan, dan pertahankan nama asli fungsi.

```python
import functools, time

def timed(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            print(f"{func.__name__} took {time.perf_counter() - start:.3f}s")
    return wrapper
```
:::

:::quiz
3 · Kapan kamu pakai `set`, `dict`, `tuple`, dan `list`?

`list`: urutan yang bisa berubah. `tuple`: ukuran tetap, tidak bisa berubah (dan bisa jadi key di dict). `set`: item unik dengan pemeriksaan anggota cepat. `dict`: pencarian key → value.
:::

:::quiz
4 · Apa yang `@dataclass` hasilkan, dan kapan composition lebih baik daripada inheritance?

Ia menghasilkan `__init__`, `__repr__`, dan `__eq__` (dan opsional ordering/frozen behavior) dari field yang diberi tipe. Composition ("punya") lebih baik saat kamu ingin menggabung perilaku tanpa hierarki "adalah" yang kaku — contohnya layanan yang *punya* notifier daripada *adalah* subclass notifier.
:::

:::quiz
5 · Apa yang salah dengan ini, dan bagaimana kamu memperbaikinya?
```python
try:
    user = repo.get(user_id)
except:
    pass
```

`except` kosong menangkap segalanya (termasuk `KeyboardInterrupt`) dan menyembunyikan bug dengan diam; `user` bahkan mungkin tidak ada setelahnya. Tangkap exception **spesifik** yang kamu harapkan (misalnya `UserNotFound`), tangani dengan bermakna (return 404, log), dan biarkan error yang tidak terduga menyebar.
:::

:::quiz
6 · Apa yang `if __name__ == "__main__":` lakukan, dan kenapa circular import terjadi?

Blok itu hanya berjalan saat file dijalankan langsung, bukan saat di-import. Circular import terjadi saat module A mengimport B saat load sedangkan B mengimport A — biasanya tanda bahwa kode bersama harus pindah ke module ketiga (atau tanggung jawab saling terkait).
:::
::::

:::tip[Nilai dirimu sendiri]
Lulus dengan **5 dari 6**. Kalau decorator (Q2) terasa goyah, pelajari materi 04 saja — Flask dibangun di atasnya.
:::

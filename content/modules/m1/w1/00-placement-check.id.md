---
title: "Tes Penempatan Minggu 1"
summary: "Apakah kamu sudah bisa menghitung, mencari, mengurutkan, dan menggabung data di Python? Cek hasilnya dalam 20 menit."
sourceHash: aaa415ab720f
---

::::placement{id="modules/m1/w1"}
Jawab di kertas dulu. Kode tidak perlu sempurna di Python — logika yang jelas itu yang penting.

:::quiz
1 · Diberi `words = ["python", "react", "python", "sql", "python", "react"]`, tulis kode yang menemukan kata yang paling sering muncul dan berapa kali muncul.

```python
counts = {}
for word in words:
    counts[word] = counts.get(word, 0) + 1
top = max(counts, key=counts.get)
print(top, counts[top])   # python 3
```

(Cara lain: `collections.Counter(words).most_common(1)` juga berhasil — tapi bisa tanpanya?)
:::

:::quiz
2 · Kenapa binary search bisa menemukan item dari 1.000.000 angka terurut dalam sekitar 20 langkah, dan apa satu syaratnya?

Setiap langkah membagi dua rentang sisa: 1.000.000 → 500.000 → … → 1 butuh sekitar log₂(1.000.000) ≈ 20 langkah. Data **harus terurut**.
:::

:::quiz
3 · Urutkan list job ini berdasarkan gaji (tertinggi dulu), dan untuk gaji sama berdasarkan judul A→Z: `jobs = [("Dev", 10), ("Analyst", 12), ("Admin", 10)]`

```python
sorted(jobs, key=lambda job: (-job[1], job[0]))
# [("Analyst", 12), ("Admin", 10), ("Dev", 10)]
```
:::

:::quiz
4 · Pakai list comprehension, simpan hanya job yang remote dari `jobs = [{"title": "Dev", "remote": True}, {"title": "QA", "remote": False}]` dan kembalikan judulnya.

`[job["title"] for job in jobs if job["remote"]]` → `["Dev"]`
:::

:::quiz
5 · Kelompokkan penjualan ini berdasarkan kota dan jumlahkan: `[("Jakarta", 100), ("Bandung", 50), ("Jakarta", 30)]`

```python
totals = {}
for city, amount in sales:
    totals[city] = totals.get(city, 0) + amount
# {"Jakarta": 130, "Bandung": 50}
```
:::

:::quiz
6 · Sebelum coding masalah baru, langkah apa yang kamu ambil?

Pahami masalahnya (ulang dengan kata-katamu, jelaskan input/output) → tulis contoh termasuk kasus tepi → rencana di pseudocode → code → tes dengan contoh → review/perbaiki.
:::
::::

:::tip[Nilai sendiri]
Lulus dengan **5 dari 6** benar *dan* bisa dijelaskan. Soal 6 hanya dihitung kalau kamu benar-benar ikuti langkah-langkahnya — jujurlah!
:::

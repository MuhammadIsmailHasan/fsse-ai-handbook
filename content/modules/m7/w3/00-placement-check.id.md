---
title: "Week 3 Placement Check"
summary: Bisakah kamu menjelaskan embedding dan kemiripan, menyimpan dan mencari vektor di PostgreSQL, membangun dan mengukur semantic search, dan menggabungkan pencarian kata kunci dan vektor? Kalau ya, baca sekilas.
sourceHash: 53c0586b9fd7
---

::::placement{id="modules/m7/w3"}
Minggu ini membahas pencarian berbasis makna. Bisakah kamu menjelaskan ini tanpa melihat?

:::quiz
1 · Apa itu embedding, dan kenapa dokumen dan kueri harus memakai model embedding yang sama?

Embedding adalah daftar angka yang mewakili makna sebuah teks, sehingga makna yang mirip mendapat vektor yang berdekatan. Model berbeda membuat "peta" berbeda, jadi vektor dari dua model tidak bisa dibandingkan. Pakai satu model per indeks dan simpan namanya agar bisa embed ulang saat berganti.
:::

:::quiz
2 · Apa beda cosine similarity, dot product dan jarak Euclid?

Cosine hanya mengukur sudut antar vektor (mengabaikan panjang); dot product menggabungkan sudut dan panjang (sama dengan cosine untuk vektor ternormalisasi); Euclid adalah jarak garis lurus (lebih kecil berarti lebih dekat). Pencarian teks biasanya memakai cosine atau dot product ternormalisasi.
:::

:::quiz
3 · Di pgvector, kapan kamu menambah indeks HNSW atau IVFFlat, dan apa yang kamu korbankan?

Mulai dengan pencarian eksak, yang selalu benar dan cukup untuk puluhan ribu baris. Tambah indeks perkiraan saat latency terukur membutuhkannya. Kamu menukar sebagian recall (bisa melewatkan tetangga sebenarnya) dengan kecepatan, plus waktu build dan memori. Ukur recall terhadap hasil eksak dan setel `ef_search` atau `probes`.
:::

:::quiz
4 · Angka apa yang kamu pakai untuk menilai semantic search, dan bagaimana membangun tesnya?

Recall@k (apakah hasil benar ada di k teratas), precision@k (seberapa banyak k teratas berguna) dan MRR (seberapa tinggi hasil benar pertama). Bangun set uji 20–100 kueri nyata dengan id hasil yang benar, jalankan pencarian, dan baca kueri yang meleset.
:::

:::quiz
5 · Kenapa menggabungkan pencarian kata kunci dengan pencarian vektor, dan bagaimana reciprocal rank fusion bekerja?

Pencarian vektor menemukan makna tapi bisa melewatkan id, nama dan kata langka yang persis; pencarian kata kunci menemukan kata persis tapi melewatkan sinonim. Menggabungkan keduanya menutup kedua kelemahan. RRF memberi tiap dokumen 1/(60 + peringkat) dari setiap daftar dan menjumlahkannya, sehingga dokumen yang diberi peringkat tinggi oleh beberapa daftar naik, dan tak perlu penskalaan skor.
:::
::::

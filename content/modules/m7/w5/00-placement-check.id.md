---
title: "Week 5 Placement Check"
summary: Bisakah kamu membangun harness eval dengan gate, menyusun set uji yang bisa dipercaya, mengkalibrasi juri LLM, memakai metrik RAG dengan bijak, dan men-trace request AI? Kalau ya, baca sekilas.
sourceHash: "ed8be423b4fb"
---

::::placement{id="modules/m7/w5"}
Minggu ini tentang mengukur kualitas AI. Bisakah kamu menjelaskan ini tanpa melihat?

:::quiz
1 · Dua versi prompt sama-sama ber-pass-rate 0,80. Kenapa membandingkan lebih dari rata-rata, dan apa itu gate rilis?

Rata-rata yang sama bisa menyembunyikan bahwa versi baru merusak kasus penting sambil memperbaiki yang lain. Bandingkan kasus fixed dan broken terhadap baseline. Gate adalah aturan di CI yang memblokir rilis saat pass rate di bawah batas atau saat terlalu banyak (atau ada) kasus kritis yang mundur.
:::

:::quiz
2 · Sebut tiga ciri set uji yang baik, dan satu jebakan saat membaginya.

Kasus nyata (bukan hanya buatan sendiri), tag untuk cakupan termasuk kasus tak terjawab dan adversarial, id stabil dan harapan yang bisa dicek. Jebakan: kebocoran antara set dev dan test (pengacakan ulang, pertanyaan hampir-duplikat), jadi pakai pembagian hash stabil dan cek hampir-duplikat.
:::

:::quiz
3 · Juri LLM sepakat dengan manusia 90% waktu. Kenapa ia mungkin tetap tak berguna, dan apa yang kamu ukur sebagai gantinya?

Jika 90% jawaban baik, juri yang berkata "lulus" pada semuanya mendapat akurasi 90% karena keberuntungan. Kappa Cohen menghilangkan kesepakatan kebetulan, dan confusion matrix menunjukkan apakah juri meloloskan jawaban buruk. Uji juga bias posisi dan panjang.
:::

:::quiz
4 · Apa yang dikatakan faithfulness dan context recall masing-masing dalam sistem RAG?

Faithfulness memberi tahu apakah klaim jawaban didukung konteks yang terambil (generasi vs konteks). Context recall memberi tahu apakah konteks terambil memuat fakta yang dibutuhkan (retrieval). Recall rendah menunjuk retrieval; recall bagus dengan faithfulness rendah menunjuk prompt atau model.
:::

:::quiz
5 · Apa beda trace dan span, dan apa yang dicatat pada span panggilan model?

Trace adalah satu request utuh; span adalah langkah di dalamnya, bersarang. Pada panggilan model catat model dan parameter, versi prompt, token masukan dan keluaran, biaya, latency (dan time to first token), stop reason, dan error atau retry. Samarkan data pribadi dan secret.
:::
::::

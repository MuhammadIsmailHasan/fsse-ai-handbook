---
title: "Week 4 Placement Check"
summary: Bisakah kamu merancang alur RAG dengan jalur penolakan jujur, chunk menurut struktur, membersihkan dan me-re-rank kandidat, memvalidasi sitasi, dan mendiagnosis jawaban gagal? Kalau ya, baca sekilas.
sourceHash: 068aa8a4ac2f
---

::::placement{id="modules/m7/w4"}
Minggu ini membahas RAG secara mendalam. Bisakah kamu menjelaskan ini tanpa melihat?

:::quiz
1 · Kapan sistem RAG harus melewati panggilan model sepenuhnya?

Saat retrieval tidak mengembalikan apa pun yang bisa dipakai: tanpa chunk, semuanya di bawah batas skor, atau tak ada yang muat anggaran token. Memanggil model tanpa sumber mengundang jawaban karangan; kembalikan "tidak ditemukan" yang jujur dengan langkah berikutnya.
:::

:::quiz
2 · Kenapa chunk menurut heading dan paragraf, bukan tiap N karakter, dan apa yang ditambahkan jalur heading?

Chunk berbasis struktur menjaga satu ide tetap bersama dan tidak memotong kalimat, tabel atau langkah. Jalur heading ("Returns > Refunds") memberi tiap chunk konteks yang tak dimiliki kalimat polos, yang meningkatkan pencocokan dan pemahaman.
:::

:::quiz
3 · Retrieval mengembalikan 5 chunk hampir identik. Alat apa yang membantu, dan apa ide dua tahap?

Buang hampir-duplikat, pakai MMR untuk menambah variasi, dan re-rank dengan penilai yang lebih pintar. Ide dua tahap: ambil banyak kandidat dengan cepat (recall tinggi), lalu persempit ke beberapa terbaik (precision tinggi) dalam anggaran token.
:::

:::quiz
4 · Apa yang bisa diverifikasi kodemu tentang sitasi, dan apa yang tidak?

Ia bisa mengecek bahwa nomor yang dikutip ada, kalimat punya sitasi, dan teks yang dikutip muncul di sumber. Ia tidak bisa sepenuhnya memverifikasi bahwa sumber benar-benar mendukung klaim, lengkap atau terkini; itu butuh juri (sampel manusia atau model).
:::

:::quiz
5 · Jawaban RAG salah. Apa pertanyaan yang diajukan, berurutan?

Apakah jawaban ada di korpus? Apakah chunk yang tepat terambil? Apakah sampai ke prompt (setelah k, anggaran dan peringkat)? Apakah jawaban benar dan berpijak? "Tidak" pertama adalah akar masalah yang diperbaiki.
:::
::::

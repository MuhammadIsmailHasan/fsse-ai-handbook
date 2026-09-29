---
title: "Week 2 Placement Check"
summary: Bisakah kamu menjelaskan kapan async/await benar-benar membantu, apa yang dilakukan dependency injection FastAPI, cara kerja session SQLAlchemy 2.0 di FastAPI, dan alur auth JWT? Kalau ya, baca sekilas.
sourceHash: 4ef6a683ef6e
---

::::placement{id="modules/m3/w2"}
Minggu ini menyambungkan FastAPI ke database dengan auth. Bisakah kamu menjelaskan ini tanpa melihat?

:::quiz
1 · Kapan `async def` membuat endpoint FastAPI lebih cepat, dan kapan tak membantu?

Ia membantu saat handler kebanyakan **menunggu I/O** (database, API lain, model AI), karena server bisa melayani request lain selama menunggu. Ia **tidak** membantu kerja terikat-CPU (komputasi berat), yang menyibukkan event loop alih-alih menunggu.
:::

:::quiz
2 · Masalah apa yang diselesaikan `Depends(...)` (dependency injection) FastAPI?

Ia menyediakan setup bersama — session database, user terautentikasi saat ini, settings — ke endpoint mana pun yang mendeklarasikannya, alih-alih tiap handler membuatnya sendiri. FastAPI meresolusi dependency, menyuntikkan hasilnya, dan bisa membersihkannya setelahnya, yang juga membuat handler mudah diuji.
:::

:::quiz
3 · Di SQLAlchemy 2.0, bagaimana mengambil satu user lewat id dan menjalankan query?

`session.get(User, user_id)` mengambil lewat primary key; untuk query kamu membangun statement dan mengeksekusinya: `session.scalars(select(User).where(User.email == e)).all()`. `Session` adalah unit of work yang membundel perubahan dan meng-commit-nya dalam transaksi.
:::

:::quiz
4 · Telusuri login JWT: apa yang dikirim balik server, dan apa yang dilakukan klien berikutnya?

Saat login sukses server mengembalikan **token akses JWT** yang ditandatangani. Klien menyimpannya dan mengirimnya di request berikutnya di header `Authorization: Bearer <token>`. Server memverifikasi tanda tangan (tanpa lookup DB) dan membaca id user dari claim token.
:::

:::quiz
5 · Kenapa memverifikasi tanda tangan JWT pada tiap request alih-alih mencari token di database?

Karena tanda tangan membuktikan token diterbitkan server-mu dan tak dirusak, memakai kunci rahasia — jadi kamu mempercayai claim-nya tanpa perjalanan bolak-balik ke database. Statelessness itu manfaat utama JWT (trade-off-nya kamu tak bisa mudah mencabut token sebelum kedaluwarsa).
:::
::::

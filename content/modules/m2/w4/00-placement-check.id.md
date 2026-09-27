---
title: "Placement Check Minggu 4"
summary: Bisa kamu struktur aplikasi Flask dengan factory dan blueprint, model tabel dengan SQLAlchemy 2.0, tulis migrasi yang aman, dan hindari masalah query N+1?
sourceHash: 9d96e85ece00
---

::::placement{id="modules/m2/w4"}
Kamu sudah membangun RevoShop dengan alat-alat ini. Bisa kamu jelaskan semuanya tanpa melihat catatan?

:::quiz
1 · Kenapa pakai application factory (`create_app()`) daripada global `app = Flask(__name__)`?

Ia memungkinkan kamu buat aplikasi dengan config berbeda (dev, test, prod), hindari efek samping saat import dan circular import (extension diinisialisasi dengan `init_app`), dan beri setiap tes aplikasi yang segar.
:::

:::quiz
2 · Apa itu Flask blueprint, dan masalah apa yang ia selesaikan?

Sekumpulan route (plus error handler dan hook) yang bisa didaftarkan ke aplikasi, sering kali dengan URL prefix. Ia memecah aplikasi besar menjadi modul fitur (auth, products, orders) daripada satu file raksasa.
:::

:::quiz
3 · Di SQLAlchemy 2.0, bagaimana kamu muat semua application untuk user 7 berurutan dari yang terbaru, dan apa itu `Session`?

```python
stmt = select(Application).where(Application.user_id == 7).order_by(Application.created_at.desc())
applications = db.session.scalars(stmt).all()
```

Session itu unit of work: ia melacak objek yang dimuat/berubah dan mengirim perubahan ke database dalam satu transaction saat `commit()`.
:::

:::quiz
4 · Kamu tambah kolom `NOT NULL` ke tabel dengan 2 juta baris di production. Bagaimana cara migrasi yang aman?

Expand/contract: tambah kolom sebagai **nullable** (atau dengan default), deploy code yang menulisnya, **backfill** baris yang sudah ada (dalam batch), lalu tambah `NOT NULL` dalam migrasi berikutnya. Review migrasi yang autogenerate dan uji `upgrade` dan `downgrade`.
:::

:::quiz
5 · Apa itu masalah query N+1 dan bagaimana kamu perbaiki di SQLAlchemy?

Muat N parent dengan satu query, lalu trigger satu query tambahan per parent saat akses relationship (N query lagi). Perbaiki dengan eager loading: `select(User).options(selectinload(User.applications))` (atau `joinedload` untuk many-to-one).
:::

:::quiz
6 · Status application hanya boleh maju, tidak mundur. Aturan ini harus ada di mana: route, service, repository, atau model?

Di service/domain layer (mungkin method model), didukung database constraint — bukan di route (hanya HTTP) atau repository (hanya akses data saja).
:::
::::

:::tip[Hitung skormu]
Lulus dengan **5 dari 6**. Pertanyaan 4 dan 5 adalah yang sering jadi masalah di production — pelajari materi 04 dan 05 lagi kalau masih ragu.
:::

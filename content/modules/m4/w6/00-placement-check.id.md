---
title: "Placement Check Minggu 6"
summary: Setup Playwright dan tes end-to-end, page object dan login tersimpan, tes komponen, build yang lebih kecil, deploy Next.js dengan Docker, dan Core Web Vitals — cek bagian mana yang bisa kamu lewati.
sourceHash: 9d2656d331f7
---

::::placement{id="modules/m4/w6"}
Jawab dari ingatan. Kalau ada istilah yang terasa baru, itu tanda untuk mempelajari materinya.

:::quiz
1 · Tes Playwright-mu menulis `await page.click("#save"); await page.waitForTimeout(2000); expect(await page.textContent(".toast")).toBe("Saved")`. Sebutkan tiga masalahnya.

Menunggu dengan waktu tetap (sleep) itu lambat dan tetap bisa gagal secara acak ("flaky"). Selector CSS/ID rusak saat HTML berubah dan mengabaikan aksesibilitas. `expect(await …)` hanya mengecek sekali, tidak mencoba ulang. Lebih baik: `await page.getByRole("button", { name: "Save" }).click()` dan `await expect(page.getByRole("status")).toHaveText("Saved")`.
:::

:::quiz
2 · Bagaimana cara menghindari login lewat UI di setiap tes end-to-end, dan tes mana yang tidak boleh memakai login tersimpan itu?

Sebuah setup project login sekali dan menyimpan cookie ke file (`storageState`); tes lain memuat file itu. Tes yang logout (atau mengubah password atau keamanan pengguna) harus memakai login baru sendiri — kalau tidak, login bersama rusak untuk semua tes.
:::

:::quiz
3 · Unit, komponen, end-to-end: mana yang kamu pakai untuk menguji (a) format rentang gaji, (b) filter tabel dan status tombol hapus, (c) "pengguna login lalu membuat lamaran"?

(a) unit test, (b) tes komponen dengan Vitest + Testing Library, (c) tes end-to-end dengan Playwright. Sebagian besar tes sebaiknya jenis yang cepat dan murah; beberapa tes end-to-end menutup perjalanan pengguna yang paling penting.
:::

:::quiz
4 · Sebutkan tiga perubahan yang biasanya mengurangi JavaScript yang dikirim halaman Next.js saat pertama dimuat.

Pindahkan pekerjaan yang tidak interaktif (markdown, highlight kode) ke Server Components; muat widget berat khusus browser belakangan dengan `next/dynamic`; taruh `"use client"` hanya di komponen daun yang kecil; hindari library raksasa atau pakai `optimizePackageImports`.
:::

:::quiz
5 · Apa fungsi `output: "standalone"`, dan kenapa stage Docker terakhir harus berjalan sebagai user non-root?

Ia membuat `next build` menghasilkan `server.js` kecil dengan hanya `node_modules` yang benar-benar dibutuhkan, sehingga image tetap kecil. Berjalan sebagai non-root membatasi kerusakan kalau ada yang berhasil membobol aplikasi.
:::

:::quiz
6 · Apa itu LCP, INP, dan CLS, dan berapa batas "bagus"-nya?

Largest Contentful Paint ≤ 2,5 detik (seberapa cepat konten utama tampil), Interaction to Next Paint ≤ 200 ms (seberapa cepat halaman merespons klik atau tombol), Cumulative Layout Shift ≤ 0,1 (seberapa sedikit elemen melompat-lompat) — diukur pada persentil ke-75 dari kunjungan nyata.
:::
::::

:::tip[Menilai dirimu sendiri]
Lulus dengan **5 dari 6**. Walaupun lulus, tetap kerjakan latihan yang dinilai dengan mutant (02, 03, 06) — menulis tes yang menangkap bug nyata adalah skill yang dicek saat interview.
:::

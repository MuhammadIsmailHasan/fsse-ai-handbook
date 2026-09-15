---
title: "🔥 Dasar-Dasar Aksesibilitas"
summary: Bangun antarmuka yang bisa dipakai semua orang — prinsip WCAG, akses keyboard dan pengelolaan fokus, accessible name, pola ARIA yang benar, form dan error yang aksesibel, serta pengujian dengan tools dan screen reader.
sourceHash: 5e0e85d83694
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Untuk siapa aksesibilitas, dan empat prinsip **WCAG** (POUR)
- Akses keyboard: urutan fokus, fokus yang terlihat, **roving tabindex**, pengelolaan fokus
- Accessible name, role, dan state — accessibility tree
- Aturan pertama ARIA, dan mengimplementasikan pola ARIA sungguhan (tabs)
- Error form yang aksesibel dengan `aria-invalid` dan `aria-describedby`
- Pengujian: axe, Lighthouse, hanya keyboard, screen reader, role query dari Testing Library

## 🧠 Ide besarnya

Aksesibilitas adalah **ramp di samping tangga**: dibangun untuk pengguna kursi roda, tapi dipakai setiap hari oleh orang tua dengan stroller, pelancong dengan koper, dan kurir. Teks takarir membantu orang di kereta yang bising; shortcut keyboard membantu power user; pesan error yang jelas membantu semua orang. Mendesain untuk kasus pinggiran memperbaiki produk bagi semua.

## ❓ Kenapa ini ada?

- Orang memakai web dengan screen reader, keyboard, switch device, kontrol suara, zoom, dan mode kontras tinggi — secara permanen, sementara (tangan patah), atau situasional (sinar matahari terik).
- Hukum dan aturan pengadaan mewajibkannya (WCAG 2.2 AA adalah target yang umum).
- Markup yang aksesibel juga yang diandalkan oleh tes otomatis, mesin pencari, dan AI agent.

## 💥 Apa yang terjadi kalau TIDAK?

- Pencari kerja yang memakai VoiceOver tidak bisa menemukan tombol "Apply" karena itu sebuah `<div>`.
- Pengguna keyboard menekan Tab masuk ke modal… dan fokusnya malah pindah ke belakang modal.
- "Invalid input" muncul dengan warna merah di atas form, tapi screen reader tidak pernah mengumumkannya dan pesan itu tidak terhubung ke field-nya.
- Tabs custom terlihat bagus tapi tombol panah tidak berfungsi dan screen reader membacakan "clickable, clickable, clickable".

## 📖 Cara kerjanya, langkah demi langkah

### 1. Prinsip POUR dari WCAG

| Prinsip | Contoh |
|---|---|
| **Perceivable** (dapat dipersepsi) | alternatif teks, takarir, kontras ≥ 4.5:1, tidak hanya mengandalkan warna |
| **Operable** (dapat dioperasikan) | semua berfungsi dengan keyboard, fokus terlihat, tanpa jebakan keyboard, waktu yang cukup, ukuran target |
| **Understandable** (dapat dipahami) | label dan error yang jelas, navigasi yang bisa ditebak, bahasa di-set |
| **Robust** (tangguh) | markup semantik valid yang bisa ditafsirkan teknologi bantu |

### 2. Accessibility tree: role, name, state

Setiap elemen interaktif butuh:
- sebuah **role** (button, link, tab, checkbox),
- sebuah **accessible name** (teks yang terlihat, `<label>`, `aria-label`, `aria-labelledby`),
- **state** bila relevan (`aria-pressed`, `aria-expanded`, `aria-selected`, `aria-invalid`, `disabled`).

Elemen native memberikan semua ini secara gratis. Periksa di DevTools → Elements → panel **Accessibility**.

### 3. Akses keyboard

- `Tab` / `Shift+Tab` berpindah antar elemen interaktif sesuai **urutan DOM**.
- `Enter` mengaktifkan link dan button; `Space` mengaktifkan button dan checkbox.
- Widget komposit (tabs, menu, listbox) adalah **satu pemberhentian Tab**; tombol panah berpindah di dalamnya — teknik **roving tabindex**:

```js
buttons.forEach((button, i) => {
  button.tabIndex = i === selectedIndex ? 0 : -1;   // only the active tab is in the Tab order
});
```

- Jangan pernah memakai nilai `tabindex` positif (merusak urutan alami).
- **Kelola fokus** saat konteks berubah: buka dialog → fokus ke dalamnya; tutup → kembalikan fokus ke tombol yang membukanya; submit form yang tidak valid → fokus ke error pertama; navigasi di single-page app → fokus ke heading halaman baru.

### 4. Aturan pertama ARIA

> Kalau elemen atau atribut HTML native sudah memberikan semantik dan perilaku yang kamu butuhkan, **pakai itu, bukan ARIA**.

ARIA mengubah apa yang **diumumkan**, bukan bagaimana sesuatu **berperilaku** — `role="button"` pada `div` tidak membuatnya bisa difokuskan atau merespons Enter. Saat kamu memang butuh ARIA (tabs, combobox, live region), ikuti pola WAI-ARIA Authoring Practices dengan tepat.

### 5. Pola sungguhan: tabs

```html
<div role="tablist">
  <button role="tab" id="tab-saved" aria-controls="panel-saved" aria-selected="true" tabindex="0">Saved</button>
  <button role="tab" id="tab-applied" aria-controls="panel-applied" aria-selected="false" tabindex="-1">Applied</button>
</div>
<div role="tabpanel" id="panel-saved" aria-labelledby="tab-saved">…</div>
<div role="tabpanel" id="panel-applied" aria-labelledby="tab-applied" hidden>…</div>
```

Keyboard: `ArrowRight`/`ArrowLeft` berpindah (berputar), `Home`/`End` melompat. Seleksi mengikuti fokus.

### 6. Error form yang aksesibel

```html
<label for="email">Email</label>
<input id="email" type="email" aria-invalid="true" aria-describedby="email-error" />
<p id="email-error">Enter a valid email address</p>
```

- Error di samping field, berupa teks (bukan hanya border merah), dihubungkan dengan `aria-describedby`.
- `aria-invalid="true"` pada field yang tidak valid; hapus setelah diperbaiki.
- Pindahkan fokus ke field tidak valid yang pertama (atau ke ringkasan error yang menautkan ke field-field itu).
- Umumkan hasil async ("Lamaran tersimpan") dengan live region yang polite.

### 7. Aksesibilitas visual

- Kontras: 4.5:1 untuk teks normal, 3:1 untuk teks besar serta border/indikator fokus component UI.
- Jangan menyampaikan makna hanya dengan warna (badge status juga menampilkan teks atau ikon).
- Dukung zoom sampai 200% dan perubahan ukuran teks; hormati `prefers-reduced-motion`.
- Ukuran target: minimal 24×24 px CSS (WCAG 2.2), idealnya ~44×44 di layar sentuh.

### 8. Menguji aksesibilitas

| Metode | Menangkap |
|---|---|
| **Hanya keyboard** (cabut mouse-nya) | jebakan, style fokus yang hilang, kontrol yang tak terjangkau |
| **Screen reader** (VoiceOver `Cmd+F5`, NVDA di Windows, TalkBack di Android) | nama, pengumuman, urutan baca |
| **axe DevTools / Lighthouse** | ~30–50% masalah secara otomatis (kontras, label hilang, error ARIA) |
| **`getByRole` dari Testing Library** | tes gagal kalau elemen tidak punya role/nama — aksesibilitas tertanam di tes |
| **`jest-axe` / Playwright + axe** | pengecekan otomatis di CI (Minggu 6) |

Tool otomatis tidak bisa menilai apakah teks alt bermakna atau urutan fokus masuk akal — pengecekan manual tetap penting.

## ⚖️ Trade-off

| Pilihan | ✅ | ❌ |
|---|---|---|
| Elemen native | aksesibel secara default | styling beberapa elemen (select, date) terbatas |
| Widget custom + ARIA | kontrol desain penuh | harus mengimplementasikan keyboard, fokus, dan state dengan tepat |
| Library headless yang aksesibel (Radix, React Aria) | pola yang sudah benar, kamu yang men-styling | menambah dependency |
| Hanya pengecekan otomatis | murah, jalan di CI | melewatkan banyak masalah nyata |

## ✅ Kapan dipakai / 🚫 Kapan TIDAK dipakai

- ✅ Sejak baris HTML pertama — memperbaikinya belakangan itu mahal.
- ✅ Pakai component library aksesibel yang sudah teruji untuk widget kompleks (Minggu 5: shadcn/ui di atas Radix).
- 🚫 Jangan menambahkan ARIA untuk "memperbaiki" markup non-semantik kalau elemen native-nya ada.
- 🚫 Jangan menyembunyikan outline fokus atau mematikan zoom (`user-scalable=no`).

## 🏆 Praktik terbaik

- [ ] HTML semantik dulu; ARIA hanya untuk pola yang tidak ada di HTML, mengikuti ARIA Authoring Practices.
- [ ] Setiap kontrol bisa dijangkau dan dioperasikan dengan keyboard, dengan style `:focus-visible` yang terlihat.
- [ ] Kelola fokus pada dialog, perpindahan route, dan error validasi.
- [ ] Setiap input punya label; error berupa teks, dihubungkan lewat `aria-describedby`, dengan `aria-invalid`.
- [ ] Kontras dan ketidakbergantungan pada warna sudah dicek; hormati reduced motion.
- [ ] Pakai query berbasis role di tes (`getByRole`) dan jalankan axe di CI.
- [ ] Lakukan pengecekan 5 menit dengan keyboard + screen reader sebelum merge perubahan UI.

## 🏭 Cara dipakai di industri

- Banyak perusahaan memasukkan aksesibilitas ke Definition of Done dan menjalankan pengecekan axe di CI.
- Situs pemerintah dan pendidikan (serta vendornya) harus memenuhi WCAG 2.x AA; European Accessibility Act berlaku untuk banyak produk dan layanan digital yang dijual di Uni Eropa sejak Juni 2025.
- Filosofi Testing Library ("uji dengan cara pengguna memakai aplikasimu") menjadikan query berbasis role sebagai default di tim React.

## ⚠️ Kesalahan umum

- Placeholder sebagai label; tombol berisi ikon saja tanpa accessible name.
- `tabindex="0"` di semua elemen, atau nilai tabindex positif.
- Modal tanpa focus trap dan tanpa pengembalian fokus.
- `aria-label` yang bertentangan dengan teks yang terlihat (pengguna kontrol suara menyebutkan apa yang mereka lihat).

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke product manager kenapa "sudah lulus Lighthouse 100" tidak berarti alur melamar kerja sudah aksesibel, dan dua pengecekan manual apa yang akan kamu lakukan sebelum rilis.

## 📐 Rancang

Rancang kebutuhan aksesibilitas untuk **dialog "Pindahkan lamaran"** CareerPilot (dibuka dari sebuah kartu di papan): dialog ini menampilkan status saat ini, pilihan radio untuk status berikutnya, catatan opsional, dan Simpan/Batal. Cakup role, nama, perilaku keyboard, pengelolaan fokus, error, dan pengumuman.

:::quiz
Tampilkan contoh spesifikasinya

- **Pemicu**: `<button aria-haspopup="dialog">Move "Backend Engineer at Kopi Data"</button>` (accessible name yang spesifik, bukan hanya "Move").
- **Dialog**: `<dialog>` native yang dibuka dengan `showModal()` (focus trap + Escape gratis) atau role="dialog" dengan `aria-modal="true"`; `aria-labelledby` → `<h2>Move application</h2>` milik dialog; `aria-describedby` → "Currently: Applied".
- **Fokus**: saat dibuka, fokus ke radio pertama (atau ke heading kalau kontennya panjang); Tab berputar di dalam; Escape dan Batal menutup; saat ditutup, **kembalikan fokus ke pemicu**.
- **Pilihan**: `<fieldset><legend>Next status</legend>` dengan radio native (tombol panah berfungsi secara native); perpindahan yang tidak diizinkan tidak ditampilkan sama sekali (bukan sekadar diabu-abukan) — atau `disabled` beserta penjelasannya.
- **Catatan**: `<textarea>` berlabel; penghitung karakter diumumkan secara polite hanya saat mendekati batas.
- **Error**: kalau belum ada status yang dipilih, `aria-invalid` pada fieldset, pesan dihubungkan dengan `aria-describedby`, fokus pindah ke radio pertama. Error server (409 invalid_transition) ditampilkan di region alert di dalam dialog (`role="alert"`).
- **Berhasil**: tutup dialog, kembalikan fokus, dan umumkan "Dipindahkan ke Interview" di live region polite milik halaman; kolom baru kartu tercermin tanpa memindahkan fokus secara tak terduga.
- **Visual**: ring fokus terlihat, kontras dicek, status tidak pernah hanya lewat warna; berfungsi di zoom 200% dan di ponsel.
- **Tes**: `getByRole("dialog", { name: "Move application" })` dari Testing Library, alur keyboard dengan user-event, pengecekan axe di component test.
:::

### 📝 Checklist self-review

- [ ] Nama, role, dan state untuk setiap kontrol
- [ ] Fokus masuk, terkunci di dalam, lalu dikembalikan
- [ ] Error terhubung dan diumumkan
- [ ] Keberhasilan diumumkan tanpa merebut fokus

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/web/m4/w1/08-accessibility" ai="no-ai" title="Tabs dan error form yang aksesibel"}
Implementasikan pola ARIA tabs (role, id, roving tabindex, tombol panah/Home/End, panel tersembunyi) dan validasi form yang menandai field tidak valid, menghubungkan pesan error dengan `aria-describedby`, dan memfokuskan error pertama. Tes mencari elemen berdasarkan role dan accessible name — markup yang tidak aksesibel tidak akan lolos.
:::

:::hints
- Tulis `select(index, { focus })` yang memperbarui `aria-selected`, `tabIndex`, dan `hidden` untuk semua tab sekaligus.
- Dengarkan `keydown` di tablist; pakai `document.activeElement` untuk menemukan tab saat ini; panggil `event.preventDefault()` untuk tombol yang ditangani.
- `firstInvalid ??= input` hanya mengingat field tidak valid yang pertama.
:::

## ✅ Cek cepat

:::quiz
Apa aturan pertama ARIA?

Jangan pakai ARIA kalau elemen atau atribut HTML native sudah memberikan semantik dan perilaku yang kamu butuhkan.
:::

:::quiz
Apa yang dicapai roving tabindex?

Widget komposit (tabs, toolbar, menu) hanya memakan satu pemberhentian Tab; tombol panah memindahkan fokus di dalamnya, dengan menjaga `tabindex="0"` hanya pada item aktif dan `-1` pada sisanya.
:::

## 📖 Kamus (glosarium)

| Istilah | Bahasa Indonesia |
|---|---|
| Accessibility (a11y) | Aksesibilitas |
| WCAG | Pedoman aksesibilitas konten web |
| Accessible name | Nama yang diumumkan teknologi bantu |
| Focus management | Pengelolaan fokus keyboard |
| Assistive technology | Teknologi bantu (pembaca layar, kontrol suara) |
| Keyboard trap | Jebakan keyboard — fokus tidak bisa keluar |

## 📚 Lanjut belajar

- [W3C: WCAG 2.2 at a glance](https://www.w3.org/WAI/standards-guidelines/wcag/glance/)
- [ARIA Authoring Practices Guide — Tabs pattern](https://www.w3.org/WAI/ARIA/apg/patterns/tabs/)
- [Testing Library: Which query should I use?](https://testing-library.com/docs/queries/about/#priority)
- [axe DevTools browser extension](https://www.deque.com/axe/devtools/)

## 📣 Akhir Minggu 1 — bagikan progresmu

:::linkedin{type="weekly"}
🌐 Minggu pertama belajar frontend, berangkat dari latar belakang backend Python.

- Membangun ulang halaman "div soup" dengan HTML semantik — lalu mencobanya dengan screen reader. Membuka mata.
- Layout mobile-first dengan Grid dan Flexbox (satu baris: `repeat(auto-fill, minmax(16rem, 1fr))` 🤯)
- JavaScript untuk developer Python: `??` vs `||`, closure, dan kenapa `fetch` tidak melempar error untuk response 500
- Membuat tabs yang aksesibel dengan navigasi keyboard — dites dengan query berbasis role

Kejutan terbesar: [jawabanmu].

Berikutnya: TypeScript dan Tailwind. 🚀

#Frontend #JavaScript #Accessibility #LearningInPublic
:::

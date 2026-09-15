---
title: "🔥 Dasar-Dasar Aksesibilitas"
summary: Bangun halaman yang bisa dipakai semua orang — empat prinsip WCAG, keyboard dan fokus, nama dan role, ARIA yang benar, error form yang mudah ditemukan, serta cara menguji dengan tools dan screen reader.
sourceHash: a1fe56b0177c
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Siapa yang terbantu oleh aksesibilitas, dan empat prinsip WCAG
- Membuat semuanya bisa dipakai dengan keyboard, dan memindahkan fokus dengan benar
- Memberi setiap kontrol role, nama, dan state
- Kapan memakai ARIA — dan kapan tidak
- Error form yang bisa ditemukan pengguna screen reader
- Menguji dengan tools, keyboard, dan screen reader

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Accessibility (a11y)** | Membuat halaman bisa dipakai semua orang, termasuk penyandang disabilitas |
| **WCAG** | Buku aturan internasional untuk aksesibilitas web |
| **Focus** | Elemen yang saat ini menerima tombol keyboard |
| **Screen reader** | Software yang membacakan halaman (VoiceOver, NVDA, TalkBack) |
| **Accessible name** | Nama yang dibacakan screen reader untuk sebuah elemen ("Save, button") |
| **ARIA** | Atribut HTML tambahan yang memberi tahu screen reader sesuatu itu apa |
| **Live region** | Area yang perubahannya otomatis dibacakan |

## 🧠 Ide besarnya

Aksesibilitas itu seperti **ramp di samping tangga**. Dibangun untuk pengguna kursi roda, tapi orang tua dengan stroller, pelancong dengan koper, dan kurir juga memakainya setiap hari. Teks takarir membantu orang di kereta yang bising; pesan error yang jelas membantu semua orang. Membangun untuk orang-orang di pinggiran membuat produk lebih baik bagi semua.

## ❓ Kenapa ini penting

- Orang memakai web dengan screen reader, hanya keyboard, kontrol suara, atau zoom — sebagian secara permanen, sebagian sementara (tangan patah), sebagian sesaat (layar HP terkena sinar matahari).
- Banyak hukum dan perusahaan mewajibkannya (WCAG 2.2 level AA adalah target yang umum).
- Tes otomatis, Google, dan AI agent juga mengandalkan HTML yang aksesibel.

Apa yang salah kalau tidak ada:

- Pencari kerja yang memakai VoiceOver tidak bisa menemukan "Apply" karena itu sebuah `<div>`.
- Pengguna keyboard membuka popup, tapi fokusnya tetap **di belakang** popup.
- "Invalid input" muncul dengan warna merah, tapi screen reader tidak pernah membacakannya.
- Tabs custom terlihat bagus, tapi tombol panah tidak berfungsi.

## 📖 Langkah demi langkah

### 1. Empat prinsip WCAG (POUR)

| Prinsip | Artinya | Contoh |
|---|---|---|
| **Perceivable** | Orang bisa melihat atau mendengar kontennya | teks alt, takarir, kontras cukup, tidak hanya warna |
| **Operable** | Orang bisa memakainya | bisa dengan keyboard, fokus terlihat, tombol cukup besar |
| **Understandable** | Orang memahaminya | label dan error yang jelas, navigasi yang bisa ditebak |
| **Robust** | Alat bantu bisa membacanya | HTML yang benar sehingga dipahami alat bantu |

### 2. Role, nama, dan state

Screen reader menjelaskan setiap kontrol dengan tiga hal — seperti **name tag** di sebuah acara: *kamu siapa* (role), *namamu* (nama), *sedang apa sekarang* (state).

- **Role**: button, link, tab, checkbox.
- **Nama**: dari teks yang terlihat, `<label>`, `aria-label`, atau `aria-labelledby`.
- **State**: ditekan, terbuka, terpilih, tidak valid, nonaktif (`aria-pressed`, `aria-expanded`, `aria-selected`, `aria-invalid`, `disabled`).

Elemen HTML asli memberikan semua ini secara gratis. Cek di DevTools → Elements → **Accessibility**.

### 3. Keyboard dan fokus

- `Tab` / `Shift+Tab` berpindah antar kontrol sesuai urutan HTML.
- `Enter` menekan link dan button; `Space` menekan button dan checkbox.
- Kelompok seperti tabs atau menu adalah **satu pemberhentian Tab**. Di dalamnya, tombol panah yang berpindah. Ini disebut **roving tabindex** — seperti mikrofon yang diedarkan di meja rapat: hanya yang sedang memegangnya (`tabindex="0"`) yang bisa dijangkau dengan Tab.

```js
buttons.forEach((button, i) => {
  button.tabIndex = i === selectedIndex ? 0 : -1;   // only the active tab is in the Tab order
});
```

- Jangan pernah memakai `tabindex` lebih dari 0 — merusak urutan alami.
- **Pindahkan fokus** saat halaman berubah, seperti pemandu yang mengantarmu ke ruangan berikutnya:
  - buka dialog → fokus ke dalamnya;
  - tutup dialog → fokus kembali ke tombol yang membukanya;
  - form ada error → fokus ke error pertama;
  - pindah halaman di single-page app → fokus ke heading halaman baru.

### 4. Aturan pertama ARIA

> Kalau elemen HTML biasa sudah melakukan apa yang kamu butuhkan, **pakai itu, bukan ARIA**.

ARIA hanya mengubah apa yang **dibacakan**, bukan cara sesuatu **berperilaku**. Menaruh `role="button"` di `div` itu seperti menempel stiker "pintu" di tembok: orang diberi tahu itu pintu, tapi tetap tidak bisa dibuka. `div`-nya tetap tidak bisa difokuskan atau ditekan dengan Enter.

Pakai ARIA hanya untuk pola yang tidak ada di HTML (tabs, combobox, live region), dan ikuti pola resmi WAI-ARIA dengan tepat.

### 5. Contoh: tabs

```html
<div role="tablist">
  <button role="tab" id="tab-saved" aria-controls="panel-saved" aria-selected="true" tabindex="0">Saved</button>
  <button role="tab" id="tab-applied" aria-controls="panel-applied" aria-selected="false" tabindex="-1">Applied</button>
</div>
<div role="tabpanel" id="panel-saved" aria-labelledby="tab-saved">…</div>
<div role="tabpanel" id="panel-applied" aria-labelledby="tab-applied" hidden>…</div>
```

- `aria-selected` menunjukkan tab mana yang aktif; `aria-controls` menghubungkan tab ke panelnya.
- Keyboard: `ArrowRight`/`ArrowLeft` pindah ke tab berikutnya (dan berputar), `Home`/`End` lompat ke tab pertama/terakhir.

### 6. Error form yang bisa ditemukan

```html
<label for="email">Email</label>
<input id="email" type="email" aria-invalid="true" aria-describedby="email-error" />
<p id="email-error">Enter a valid email address</p>
```

- Taruh **teks** error di samping field-nya (bukan hanya border merah).
- `aria-describedby` menghubungkan pesan ke field, sehingga screen reader membacakannya — seperti sticky note yang ditempel di kotak yang benar.
- `aria-invalid="true"` menandai field yang salah; hapus setelah diperbaiki.
- Pindahkan fokus ke field salah yang pertama.
- Untuk pesan seperti "Lamaran tersimpan", pakai live region yang polite agar dibacakan.

### 7. Hal-hal yang dilihat orang

- Kontras: minimal 4.5:1 untuk teks normal; 3:1 untuk teks besar, ikon, dan cincin fokus.
- Jangan hanya memakai warna untuk menunjukkan makna (badge status juga menampilkan teks).
- Halaman harus tetap berfungsi di zoom 200%; hormati `prefers-reduced-motion`.
- Tombol minimal 24×24 px (sekitar 44×44 px lebih baik di layar sentuh).

### 8. Pengujian

| Cara | Menemukan |
|---|---|
| **Hanya keyboard** (singkirkan mouse) | kontrol yang tidak bisa dijangkau, cincin fokus yang hilang, fokus yang terjebak |
| **Screen reader** (VoiceOver `Cmd+F5` di Mac, NVDA di Windows, TalkBack di Android) | nama yang salah, pengumuman yang hilang, urutan baca yang aneh |
| **axe DevTools / Lighthouse** | sekitar 30–50% masalah secara otomatis (kontras, label yang hilang) |
| **`getByRole` dari Testing Library** | tes gagal kalau elemen tidak punya role atau nama |
| **Playwright + axe** | pengecekan otomatis di CI (Minggu 6) |

Tools tidak bisa menilai apakah teks alt berguna atau urutan fokus masuk akal. Kamu tetap butuh pengecekan manual singkat.

## ⚠️ Kesalahan umum

- Placeholder sebagai pengganti label; tombol berisi ikon saja tanpa nama.
- `tabindex="0"` di semua elemen, atau nilai di atas 0.
- Popup (modal) yang tidak menjaga fokus di dalam dan tidak mengembalikannya saat ditutup.
- `aria-label` yang berbeda dengan teks yang terlihat (pengguna kontrol suara menyebutkan apa yang mereka lihat).
- Menyembunyikan outline fokus atau mematikan zoom (`user-scalable=no`).
- Menambahkan ARIA untuk "memperbaiki" `div` padahal `<button>` asli ada.

## 🏆 Praktik terbaik

- [ ] Elemen HTML asli dulu; ARIA hanya untuk pola yang tidak ada di HTML.
- [ ] Semuanya berfungsi dengan keyboard, dengan style `:focus-visible` yang terlihat.
- [ ] Pindahkan fokus untuk dialog, perpindahan halaman, dan error form.
- [ ] Setiap input punya label; error berupa teks, dihubungkan dengan `aria-describedby`, dengan `aria-invalid`.
- [ ] Cek kontras; jangan pernah menunjukkan makna hanya dengan warna.
- [ ] Pakai `getByRole` di tes dan jalankan axe di CI.
- [ ] Sebelum merge perubahan UI, luangkan 5 menit hanya dengan keyboard dan screen reader.
- [ ] Untuk widget yang rumit, pakai library yang sudah teruji (Radix / shadcn/ui — Minggu 5).

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke product manager kenapa "Lighthouse memberi nilai 100" tidak membuktikan alur melamar kerja sudah aksesibel, dan dua pengecekan manual apa yang akan kamu lakukan sebelum rilis.

## 📐 Rancang

Rencanakan aksesibilitas **dialog "Pindahkan lamaran"** CareerPilot (dibuka dari kartu di papan). Isinya status saat ini, pilihan radio untuk status berikutnya, catatan opsional, dan Simpan/Batal. Cakup role, nama, keyboard, fokus, error, dan pengumuman.

:::quiz
Tampilkan contoh rencananya

- **Tombol pembuka**: `<button aria-haspopup="dialog">Move "Backend Engineer at Kopi Data"</button>` — nama yang spesifik, bukan hanya "Move".
- **Dialog**: `<dialog>` bawaan yang dibuka dengan `showModal()` (menjaga fokus di dalam dan bisa ditutup dengan Escape secara gratis). `aria-labelledby` menunjuk ke heading "Move application"; `aria-describedby` menunjuk ke "Currently: Applied".
- **Fokus**: saat dibuka, fokus ke radio pertama; Tab tetap di dalam; Escape dan Batal menutupnya; saat ditutup, **fokus kembali ke tombol pembukanya**.
- **Pilihan**: `<fieldset><legend>Next status</legend>` dengan radio button biasa (tombol panah otomatis berfungsi). Perpindahan yang tidak diizinkan tidak ditampilkan.
- **Catatan**: `<textarea>` dengan label.
- **Error**: belum memilih status → pesan dihubungkan dengan `aria-describedby`, dan fokus pindah ke radio pertama. Error dari server (409) ditampilkan di dalam dialog dengan `role="alert"`.
- **Berhasil**: tutup dialog, kembalikan fokus, dan umumkan "Dipindahkan ke Interview" di live region polite milik halaman.
- **Visual**: cincin fokus terlihat, kontras cukup, status tidak hanya lewat warna, berfungsi di zoom 200% dan di ponsel.
- **Tes**: `getByRole("dialog", { name: "Move application" })`, alur keyboard dengan user-event, dan pengecekan axe.
:::

### 📝 Checklist self-review

- [ ] Setiap kontrol punya role, nama, dan (kalau perlu) state
- [ ] Fokus masuk, tetap di dalam, lalu kembali
- [ ] Error terhubung ke field dan dibacakan
- [ ] Keberhasilan diumumkan tanpa membuat fokus melompat-lompat

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/web/m4/w1/08-accessibility" ai="no-ai" title="Tabs dan error form yang aksesibel"}
Bangun pola ARIA tabs (role, id, roving tabindex, tombol panah/Home/End, panel tersembunyi) dan validasi form yang menandai field yang salah, menghubungkan pesan error dengan `aria-describedby`, dan memfokuskan error pertama. Tes mencari elemen berdasarkan role dan nama — markup yang tidak aksesibel tidak akan lolos.
:::

:::hints
- Tulis `select(index, { focus })` yang memperbarui `aria-selected`, `tabIndex`, dan `hidden` untuk semua tab sekaligus.
- Dengarkan `keydown` di tablist; pakai `document.activeElement` untuk menemukan tab saat ini; panggil `event.preventDefault()` untuk tombol yang kamu tangani.
- `firstInvalid ??= input` hanya mengingat field salah yang pertama.
:::

## ✅ Cek cepat

:::quiz
Apa aturan pertama ARIA?

Jangan pakai ARIA kalau elemen atau atribut HTML biasa sudah memberikan makna dan perilaku yang kamu butuhkan.
:::

:::quiz
Apa yang dilakukan roving tabindex?

Kelompok seperti tabs hanya memakan satu pemberhentian Tab; tombol panah berpindah di dalamnya. Hanya item aktif yang punya `tabindex="0"`, sisanya `-1`.
:::

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

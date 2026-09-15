---
title: "🔥 Tes Komponen dengan Vitest + Testing Library"
summary: Menguji komponen React seperti cara pengguna memakainya — setup Vitest untuk Next.js, query Testing Library, user-event, state loading dan error, mock modul dan fetch, menguji hook, apa yang tidak perlu dites, dan mengecek kualitas tes dengan mutan.
sourceHash: d8c592439a9a
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Kenapa tes komponen memberi **nilai terbaik** untuk UI React
- Setup Vitest + jsdom + Testing Library di proyek Next.js
- Urutan prioritas query: `getByRole` → `getByLabelText` → `getByText` → `getByTestId`
- `getBy` vs `queryBy` vs `findBy`
- `userEvent` untuk klik dan ketikan yang realistis
- Menguji state async (pending, sukses, error) dengan Promise yang kamu kendalikan
- Mocking: modul (`vi.mock`), `fetch`, navigasi Next.js, timer
- Menguji custom hook dengan `renderHook`
- Apa yang **tidak** perlu dites, dan cara mutation testing mengukur kualitas tes

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Component test** | Merender satu komponen (beserta anak-anaknya) lalu memakainya seperti pengguna |
| **Vitest** | Test runner yang cepat (mirip Jest) dan cocok dengan Vite |
| **jsdom** | Halaman browser tiruan yang berjalan di dalam Node.js |
| **Testing Library** | Helper untuk mencari elemen seperti cara pengguna melihatnya (lewat role, label, teks) |
| **Query** | Fungsi untuk mencari elemen: `getByRole`, `findByText`… |
| **Mock** | Versi palsu dari sesuatu (jaringan, router, modul) |
| **Implementation detail** | Cara kode bekerja di dalam (nama state, class CSS) — pengguna tidak pernah melihatnya |
| **Coverage** | Baris kode mana saja yang dijalankan selama tes |

## 🧠 Ide besarnya

Aturan utama Testing Library: **semakin mirip tesmu dengan cara software dipakai, semakin bisa kamu percaya.** Pengguna tidak tahu komponenmu punya `useState` bernama `deletingId` — mereka melihat tombol bertuliskan "Deleting…" yang tidak bisa diklik dua kali. Uji **itu**.

Tes komponen itu seperti **simulator pesawat**: cukup realistis untuk berlatih setiap keadaan darurat (error, jaringan lambat, daftar kosong) dalam hitungan milidetik, tanpa biaya menerbangkan pesawat sungguhan (E2E).

## ❓ Kenapa ini penting

Tes E2E lambat dan butuh aplikasi, API, dan database yang sedang berjalan. Unit test untuk fungsi murni tidak menangkap bagaimana UI tersambung. Tes komponen merender pohon React sungguhan di jsdom, mengklik dan mengetik seperti pengguna, dan menjalankan ratusan kasus per detik — pas untuk tabel, form, dialog, rendering bersyarat, dan aksesibilitas.

Cara menguji yang salah terlihat seperti ini:

```tsx
// ❌ implementation-detail tests
expect(wrapper.state("deletingId")).toBe(13);                 // breaks on refactor to useReducer
expect(container.querySelector(".btn-danger")).toBeTruthy();  // breaks on a CSS change, misses a11y
expect(asFragment()).toMatchSnapshot();                       // 400-line snapshot nobody reads; "update snapshot" on every change
```

Tes seperti ini gagal saat kamu refactor dengan benar, dan lulus saat perilakunya rusak — kombinasi terburuk. Seperti ujian SIM yang mengecek warna mesin, bukan apakah kamu bisa mengerem.

## 📖 Langkah demi langkah

### 1. Setup di proyek Next.js

```bash
npm install -D vitest @vitejs/plugin-react jsdom @testing-library/react @testing-library/dom @testing-library/user-event @testing-library/jest-dom vite-tsconfig-paths
```

```ts
// vitest.config.mts
import react from "@vitejs/plugin-react";
import tsconfigPaths from "vite-tsconfig-paths";
import { defineConfig } from "vitest/config";

export default defineConfig({
  plugins: [tsconfigPaths(), react()],
  test: { environment: "jsdom", setupFiles: ["./vitest.setup.ts"], restoreMocks: true },
});
```

```ts
// vitest.setup.ts
import "@testing-library/jest-dom/vitest";   // toBeInTheDocument, toBeDisabled, toHaveAccessibleDescription…
```

Vitest belum bisa merender **Server Components** yang async. Uji fungsi datanya sebagai unit test, anak-anak client-nya sebagai komponen, dan halaman utuhnya dengan E2E.

### 2. Query

| Query | Tidak ketemu | Ketemu banyak | Async? | Dipakai untuk |
|---|---|---|---|---|
| `getBy…` | throw | throw | tidak | elemen yang harus ada |
| `queryBy…` | `null` | throw | tidak | mengecek sesuatu **tidak** ada |
| `findBy…` | reject setelah timeout | reject | **ya** | elemen yang muncul belakangan |
| `getAllBy…` / `queryAllBy…` / `findAllBy…` | — | array | — | daftar |

Cara mudah mengingat: `get` = "sekarang ada di sini", `query` = "mungkin tidak ada", `find` = "tunggu dulu".

Prioritas: `getByRole("button", { name: "Delete Backend Engineer" })` → `getByLabelText("Search")` → `getByText("No applications match your filters")` → `getByTestId` sebagai pilihan terakhir. Pakai `within(row)` untuk mencari di satu bagian UI, dan `screen.debug()` / `screen.logTestingPlaygroundURL()` saat buntu.

### 3. Interaksi dengan `userEvent`

```tsx
const user = userEvent.setup();
render(<ApplicationsTable applications={rows} onDelete={onDelete} />);

await user.type(screen.getByLabelText("Search"), "  FRONTEND ");
await user.selectOptions(screen.getByLabelText("Status"), "offer");
await user.click(screen.getByRole("button", { name: "Applied on" }));
await user.keyboard("{Escape}");
```

`userEvent` memicu seluruh rangkaian event seperti browser sungguhan (focus, keydown, input, keyup, click). `fireEvent` hanya memicu satu event — seperti jari yang tiba-tiba teleport ke tombol. Pakai `fireEvent` hanya kalau kamu butuh kontrol itu (misalnya dengan fake timer).

### 4. State async dengan Promise yang kamu kendalikan

```tsx
test("deletes by id with a pending state", async () => {
  let finish!: () => void;
  const onDelete = vi.fn(() => new Promise<void>((resolve) => (finish = resolve)));
  const user = userEvent.setup();
  render(<ApplicationsTable applications={rows} onDelete={onDelete} />);

  await user.click(screen.getByRole("button", { name: "Delete Frontend Developer" }));
  expect(onDelete).toHaveBeenCalledWith(13);
  const button = screen.getByRole("button", { name: "Delete Frontend Developer" });
  expect(button).toBeDisabled();
  expect(button).toHaveTextContent("Deleting…");

  finish();                                              // now let the request complete
  await vi.waitFor(() => expect(button).toBeEnabled());
});
```

Kamu memegang **remote jaringan**: request tetap "loading" sampai kamu menekan `finish()`. Dengan begitu kamu bisa mengecek state di tengah-tengah setiap kali — tanpa sleep, tanpa untung-untungan.

### 5. Mocking

```tsx
// Next.js navigation
const push = vi.fn();
vi.mock("next/navigation", () => ({ useRouter: () => ({ push, replace: vi.fn(), refresh: vi.fn() }), usePathname: () => "/jobs" }));

// A module your component imports
vi.mock("./lib/applications-client", () => ({ applicationsClient: { remove: vi.fn().mockResolvedValue(null) } }));

// fetch
vi.stubGlobal("fetch", vi.fn().mockResolvedValue(Response.json([{ id: 1 }])));

// timers
vi.useFakeTimers(); act(() => vi.advanceTimersByTime(4000));
```

Mock di **tepi** aplikasimu (jaringan, router, waktu, API browser) — seperti lokasi syuting film dengan latar kota yang dilukis, sementara aktornya (komponenmu) tetap asli.

- Jangan mock komponen anak buatanmu sendiri.
- Untuk komponen yang memanggil banyak API, **MSW (Mock Service Worker)** memalsukan request di level jaringan dan bisa dipakai bersama oleh tes, Storybook, dan development lokal.
- Bungkus komponen yang butuh provider (TanStack Query, context) dengan helper `renderWithProviders`; buat **QueryClient baru per tes** dengan `retry: false`.

### 6. Hook

```tsx
const { result, rerender } = renderHook(({ value }) => useDebouncedValue(value, 300), { initialProps: { value: "d" } });
```

Utamakan menguji hook lewat komponen yang memakainya; pakai `renderHook` untuk hook yang dipakai ulang dengan banyak kasus.

### 7. Yang tidak perlu dites

- State internal, fungsi privat, nama class CSS.
- Cara kerja library pihak ketiga (Radix sudah menguji focus trap-nya — uji **cara kamu memakainya**: judul, aksi konfirmasi, state pending).
- Snapshot besar. Snapshot inline kecil untuk output yang stabil dan bermakna tidak masalah.

### 8. Tesnya bagus tidak? Mutan lagi

Latihannya memberimu komponen yang sudah jadi dan 9 mutan (versi dengan satu bug masing-masing). Suite tes dengan coverage 100% tetap bisa membiarkan kebanyakan mutan lolos:

```tsx
test("renders", () => {
  render(<ApplicationsTable applications={rows} onDelete={vi.fn()} />);
  expect(screen.getByRole("table")).toBeInTheDocument();       // covers most lines, kills almost nothing
});
```

Coverage hanya bilang simulatornya **dinyalakan**; tidak bilang ada latihan darurat yang dilakukan. Di proyek sungguhan, **Stryker** menjalankan mutation testing untuk suite Vitest — pakai untuk kode kritis (izin akses, harga, validasi).

### Kapan memakai tes komponen

- ✅ Form, tabel, filter, dialog, rendering bersyarat, state loading/error/kosong, nama yang aksesibel.
- ✅ Tes untuk bug UI yang ditemukan di production.
- 🚫 Tata letak visual → visual regression atau screenshot E2E (jsdom tidak punya layout CSS sungguhan).
- 🚫 Server Components async dan routing lengkap → E2E.

## ⚠️ Kesalahan umum

- `getBy` untuk mengecek sesuatu tidak ada (ia throw) → pakai `queryBy` + `not.toBeInTheDocument()`.
- Lupa `await` pada `user.click` → pengecekan jalan sebelum UI ter-update.
- Mengharapkan update instan setelah pekerjaan async → pakai `findBy`.
- Mengabaikan peringatan "not wrapped in act(...)" — biasanya ada update yang terjadi setelah tes selesai; tunggu state akhirnya.
- Data tes yang tidak sengaja cocok dengan beberapa baris (mencari "data" cocok dengan role sekaligus nama perusahaan).

## 🏆 Praktik terbaik

- [ ] Query lewat role/label/teks; `within` untuk mempersempit; `getByTestId` paling akhir.
- [ ] `userEvent.setup()` per tes; `await` setiap interaksi.
- [ ] `findBy` / `vi.waitFor` untuk async; Promise yang kamu kendalikan untuk state pending; jangan pernah sleep dengan `setTimeout`.
- [ ] Uji semua state UI async: pending, sukses, error — plus kosong.
- [ ] Mock bagian tepi (jaringan, router, timer), bukan anak komponen; reset mock antar tes (`restoreMocks`).
- [ ] Provider/client baru per tes; tidak ada state yang dipakai bersama dan bisa berubah.
- [ ] Satu perilaku per tes, dinamai seperti kalimat dari spesifikasi.
- [ ] Jalankan tes di CI setiap PR; cek kualitas tes dengan mutasi untuk kode kritis.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan ke rekan tim dengan analogi simulator pesawat kenapa `expect(screen.getByRole("table")).toBeInTheDocument()` bisa memberi coverage 90% tapi hampir tidak memberi rasa percaya.

## 📐 Rancang

Daftarkan tes komponen untuk **ApplicationForm** CareerPilot dari W5 (React Hook Form + Zod, pilihan perusahaan yang dimuat dari API, baris skill dinamis, error server, state pending). Untuk setiap tes: siapkan, lakukan, cek — dan apa yang di-mock.

:::quiz
Lihat contoh daftar

| Tes | Siapkan / mock | Lakukan | Cek |
|---|---|---|---|
| memuat perusahaan | `fetch`/MSW mengembalikan 2 perusahaan | render | "Loading companies…" lalu opsi muncul (`findAllByRole("option")`) |
| gagal memuat perusahaan | MSW mengembalikan 500 | render | alert "Couldn't load companies" + tombol Retry mengambil ulang |
| field wajib | perusahaan sudah dimuat | klik Save | pesan untuk role/company, `aria-invalid`, `onSubmit` tidak dipanggil |
| baris skill | — | Add skill ×2, ketik, hapus yang pertama | baris yang tersisa tetap menyimpan isiannya; Add nonaktif saat maksimal |
| aturan gaji | — | min 20, max 10, blur | "Maximum must be at least the minimum" di field max |
| pending | `onSubmit` mengembalikan Promise yang kamu kendalikan | isi valid + Save | tombol nonaktif "Saving…"; resolve → aktif lagi |
| error field dari server | `onSubmit` resolve `{ fieldErrors: { role: "Already applied" } }` | submit | pesan di bawah Role, fokus pindah ke Role |
| sukses | `onSubmit` resolve `undefined` | submit | status "Application saved", form di-reset (tidak dirty) |

Mock: jaringan lewat MSW (atau stub `fetch`), router `next/navigation` kalau form melakukan redirect. Tidak di-mock: RHF, Zod, input anak.
:::

### 📝 Checklist review mandiri

- [ ] State pending, sukses, error, dan kosong sudah dites
- [ ] Hanya bagian tepi yang di-mock
- [ ] Setiap assertion adalah hal yang bisa dilihat pengguna

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/web/m4/w6/06-component-tests" ai="no-ai" title="Tes yang membunuh 9 mutan"}
Tulis tes Vitest + Testing Library untuk tabel lamaran yang sudah jadi (sorting, pencarian, filter status, state kosong, pending dan error saat menghapus). Grader menjalankan tesmu terhadap komponen asli dan 9 mutan.
:::

:::hints
- Baca setiap aturan di README dan tanyakan: "apa yang dilihat pengguna kalau ini rusak?"
- Pilih data tes di mana pencarian **hanya** cocok dengan role atau **hanya** dengan perusahaan.
- Pengecekan state pending butuh Promise yang kamu resolve sendiri.
:::

## ✅ Cek cepat

:::quiz
Kapan memakai `queryByText` alih-alih `getByText`?

Saat mengecek sesuatu **tidak** ada: `expect(screen.queryByText("Error")).not.toBeInTheDocument()`. `getBy` akan throw sebelum pengecekannya berjalan.
:::

:::quiz
Kenapa membuat `QueryClient` TanStack baru untuk setiap tes?

Kalau tidak, cache membocorkan data dari satu tes ke tes berikutnya, sehingga hasilnya bergantung pada urutan tes dijalankan.
:::

## 📚 Lanjut belajar

- Dokumentasi Next.js (tersedia di dalam proyek): Testing → Vitest
- [Testing Library: Guiding principles](https://testing-library.com/docs/guiding-principles) · [Which query should I use?](https://testing-library.com/docs/queries/about#priority)
- [Kent C. Dodds: Common mistakes with React Testing Library](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library)
- [Dokumentasi MSW](https://mswjs.io/docs)

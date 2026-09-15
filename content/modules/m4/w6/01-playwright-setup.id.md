---
title: "Setup Playwright"
summary: Memulai tes end-to-end dengan benar — kegunaannya, instal Playwright, config sungguhan (webServer, projects, retries, trace, reporter), locator, assertion yang menunggu, dan alat debugging.
sourceHash: eb2d5e396490
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Posisi tes **end-to-end (E2E)** di samping unit test dan tes komponen
- Instal Playwright dan apa saja yang dibuat `npm init playwright@latest`
- `playwright.config.ts` sungguhan: `webServer`, `baseURL`, `projects`, `retries`, `workers`, `forbidOnly`, trace, reporter
- **Locator** (`getByRole`, `getByLabel`) dan **web-first assertion** (`await expect(locator).toBeVisible()`)
- Auto-waiting, dan kenapa `waitForTimeout` adalah tanda buruk
- Debugging: UI mode, `--debug`, trace viewer, codegen

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **End-to-end (E2E) test** | Tes yang memakai seluruh aplikasi di browser sungguhan, seperti pengguna asli |
| **Playwright** | Alat yang mengendalikan browser sungguhan dari kode tes |
| **Locator** | Cara menemukan elemen di halaman ("tombol Save") |
| **Assertion** | Pengecekan: "teks ini harus terlihat" |
| **Auto-waiting** | Playwright menunggu sampai elemen siap sebelum beraksi |
| **Flaky test** | Tes yang kadang lulus kadang gagal tanpa ada perubahan kode |
| **Browser context** | Sesi browser baru yang terpisah, seperti jendela incognito baru |
| **Trace** | Rekaman langkah demi langkah dari tes, untuk debugging |

## 🧠 Ide besarnya

Unit test mengecek **batu bata**; tes komponen mengecek **satu ruangan**; tes E2E berjalan melewati **rumah yang sudah jadi** seperti tamu: buka pintu (muat halaman), nyalakan lampu (klik), cek air mengalir (lihat hasilnya).

Tes E2E menangkap masalah yang tidak terlihat di tes kecil — redirect rusak, cookie hilang, form yang mengirim ke URL salah. Tapi tesnya lambat, jadi kamu menulis **sedikit saja**, untuk perjalanan pengguna yang paling penting.

## ❓ Kenapa ini penting

Aplikasi Next.js-mu adalah rantai: browser → proxy → Server Component → Server Action → Flask → Postgres → redirect → render ulang. Setiap bagian bisa lulus tesnya sendiri, tapi rantainya tetap putus — seperti setiap gerbong kereta dalam kondisi baik tapi tidak tersambung.

Playwright mengendalikan **browser sungguhan** (Chromium, Firefox, WebKit) dan memberimu auto-waiting, browser baru untuk tiap tes, eksekusi paralel, dan alat debugging yang sangat bagus.

Tanpa ini:

- Rilis yang "jalan di laptopku": redirect login berputar terus di production karena satu pengaturan cookie.
- Mengklik aplikasi manual sebelum setiap deploy — dan dilewati saat buru-buru.
- Atau tes E2E yang ditulis buruk: `sleep(3000)`, selector CSS seperti `.btn-primary > span`, tes berbagi data → tes flaky yang akhirnya diabaikan semua orang.

## 📖 Langkah demi langkah

### 1. Piramida (atau trofi) testing

| Level | Alat | Kecepatan | Menangkap |
|---|---|---|---|
| Statis | TypeScript, ESLint | instan | typo, tipe salah |
| Unit | Vitest | ms | logika di fungsi murni |
| Komponen / integrasi | Vitest + Testing Library | ms–detik | perilaku UI, state, aksesibilitas |
| **E2E** | **Playwright** | detik | routing, auth, form, browser + server sungguhan yang bekerja bersama |

Banyak tim memakai "testing trophy": banyak tes komponen/integrasi, dan lapisan tipis tes E2E untuk **perjalanan kritis** (daftar, login, alur utama membuat data, checkout).

### 2. Instal

```bash
npm init playwright@latest          # asks: TypeScript, tests folder, GitHub Actions workflow, install browsers
# or in an existing project
npm install -D @playwright/test
npx playwright install --with-deps chromium    # browsers (and OS dependencies on Linux/CI)
```

Browser diunduh terpisah dari paket npm (ke folder cache). Kamu juga bisa memakai Google Chrome yang sudah terpasang dengan `channel: "chrome"`.

### 3. Config sungguhan

```ts
// playwright.config.ts
import { defineConfig, devices } from "@playwright/test";

const PORT = Number(process.env.PORT ?? 3091);
const CI = !!process.env.CI;

export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: CI,                       // a forgotten test.only fails the CI run
  retries: CI ? 2 : 0,                  // retry on CI only — and investigate anything flaky
  workers: CI ? 1 : undefined,          // CI machines are small; locally use your cores
  reporter: CI ? [["github"], ["html", { open: "never" }]] : [["list"], ["html", { open: "never" }]],
  use: {
    baseURL: `http://localhost:${PORT}`,  // page.goto("/login")
    trace: "on-first-retry",              // a full recording when a test is retried
    screenshot: "only-on-failure",
  },
  projects: [
    { name: "chromium", use: { ...devices["Desktop Chrome"] } },
    { name: "mobile", use: { ...devices["Pixel 7"] } },
    // { name: "webkit", use: { ...devices["Desktop Safari"] } },
  ],
  webServer: {
    command: CI ? "npm run build && npm run start" : "npm run dev",
    url: `http://localhost:${PORT}`,
    reuseExistingServer: !CI,             // locally reuse your running dev server
    timeout: 120_000,
  },
});
```

- **`webServer`** menyalakan aplikasimu sebelum tes dan mematikannya setelahnya.
- **`projects`** menjalankan tes yang sama di beberapa browser atau perangkat.
- **`forbidOnly`**: `test.only` yang tertinggal akan diam-diam melewati semua tes lain — di CI, lebih baik gagal.
- Di CI, uji **build production** (`next build && next start`). Mode dev lebih lambat dan perilakunya berbeda — seperti menguji mobil di bengkel, bukan di jalan.
- Pakai port non-default (seperti 3091) supaya tes tidak bentrok dengan aplikasi lokal lain.

### 4. Tes pertama

```ts
// e2e/smoke.spec.ts
import { expect, test } from "@playwright/test";

test("logged-out visitors see the login page", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Log in" })).toBeVisible();
  await expect(page).toHaveTitle("Log in · CareerPilot");
});
```

Setiap tes mendapat `page` sendiri di **browser context** yang baru (seperti jendela incognito baru): tidak ada cookie atau storage yang bocor dari satu tes ke tes berikutnya.

### 5. Locator — cari elemen seperti pengguna

| Utamakan | Contoh |
|---|---|
| `getByRole` | `page.getByRole("button", { name: "Save application" })` |
| `getByLabel` | `page.getByLabel("Email")` |
| `getByText` | `page.getByText("Application created")` |
| `getByPlaceholder`, `getByAltText`, `getByTitle` | kalau tidak ada pilihan yang lebih baik |
| `getByTestId` | cadangan stabil (`data-testid`) untuk elemen tanpa nama yang aksesibel |
| ❌ CSS/XPath | `page.locator(".card > div:nth-child(2) button")` — rusak saat refactor |

Pengguna tidak bilang "klik span di div ketiga"; mereka bilang "klik **Save**". Cari elemen dengan cara yang sama. Bonus: locator role juga menjadi **cek aksesibilitas** — kalau kamu tidak bisa menemukan tombol lewat role dan namanya, pengguna screen reader juga tidak bisa.

Locator baru mencari saat dipakai, dan bisa dipersempit bertahap: `page.getByRole("row").filter({ hasText: "Data Engineer" }).getByRole("button", { name: "Delete" })`.

### 6. Auto-waiting dan assertion yang mencoba ulang

```ts
await page.getByRole("button", { name: "Save" }).click();          // waits until visible, enabled, stable
await expect(page.getByRole("status")).toHaveText("Saved");          // retries until true or timeout (5 s default)
```

```ts
// ❌ checks once, immediately — flaky
expect(await page.getByRole("status").textContent()).toBe("Saved");
// ❌ slow AND still flaky
await page.waitForTimeout(3000);
```

Menunggu dengan waktu tetap itu seperti merebus mi instan tepat 3 menit sambil menutup mata — kadang masih keras, kadang terlalu lembek. `await expect(...)` itu seperti mencicipi mi setiap beberapa detik dan berhenti saat sudah pas.

### 7. Alat debugging

```bash
npx playwright test --ui                 # UI mode: watch, time-travel through each step
npx playwright test --debug              # step through with the inspector
npx playwright test -g "log in" --project=chromium
npx playwright show-report               # HTML report with traces and screenshots
npx playwright show-trace trace.zip      # trace from CI artifacts
npx playwright codegen localhost:3091    # record actions → generated locators (then clean them up)
```

**Trace** itu seperti rekaman CCTV dari tes: setiap langkah, tampilan halaman saat itu, request jaringan, dan log console. Saat tes gagal di CI, kamu tinggal menonton rekamannya, bukan menebak-nebak.

### Kapan memakai tes E2E

- ✅ Perjalanan pengguna yang kritis, login dan redirect, alur lintas beberapa halaman, cek "smoke" cepat setelah deploy.
- ✅ Tes untuk bug yang hanya terjadi dengan browser + server sungguhan.
- 🚫 Setiap pesan validasi atau kasus tepi dari fungsi format — pakai unit/tes komponen.
- 🚫 Situs pihak ketiga yang tidak kamu kendalikan — palsukan dengan `page.route`.

Di tempat kerja kamu mungkin juga bertemu **Cypress** (alternatif populer) dan **Selenium** (lebih lama, lebih banyak menunggu manual).

## ⚠️ Kesalahan umum

- Lupa `await` sebelum `expect(locator)...` → tes selesai sebelum sempat mengecek.
- Menulis langsung `http://localhost:3000` alih-alih memakai `baseURL`.
- Menjalankan E2E terhadap `next dev` di CI → lambat, halaman pertama sering flaky.
- Meng-commit `playwright/.auth/*.json`, `test-results/`, atau `playwright-report/`.
- Memakai hasil codegen apa adanya (selector rapuh, tanpa assertion).

## 🏆 Praktik terbaik

- [ ] Uji apa yang dilihat pengguna, dengan **locator role/label**; tambahkan `data-testid` hanya kalau perlu.
- [ ] Pakai **web-first assertion**; jangan pernah `waitForTimeout`.
- [ ] Buat tes **mandiri** (data sendiri, context sendiri); jalankan `fullyParallel`.
- [ ] `forbidOnly` di CI; retry hanya di CI, dan perbaiki tes flaky alih-alih menyembunyikannya.
- [ ] Trace `on-first-retry`, screenshot saat gagal, laporan HTML diunggah sebagai artifact CI.
- [ ] Jalankan E2E terhadap **build production** di CI.
- [ ] Atur port dan base URL lewat environment variable.
- [ ] Jaga suite E2E tetap kecil dan cepat; jalankan suite yang lambat setiap malam kalau perlu.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan analogi "batu bata, ruangan, rumah jadi" ke rekan tim yang ingin mengganti semua unit test dengan tes E2E "karena E2E menguji semuanya".

## 📐 Rancang

Rencanakan **strategi E2E** untuk aplikasi Next.js CareerPilot: 5–8 perjalanan pengguna mana yang layak dites E2E, browser/perangkat apa, bagaimana Flask API dan database dinyalakan di CI, dan apa yang dijalankan di setiap pull request vs setiap malam.

:::quiz
Lihat contoh rencana

**Perjalanan (suite pull request, ~3 menit):** login / logout; redirect route yang dilindungi dengan `next`; membuat lamaran (jalur sukses + satu error validasi dari server); memindahkan status di papan; menghapus dengan konfirmasi; pencarian + pagination di URL; menu navigasi mobile.

**Projects:** Chromium desktop di setiap pull request; `Pixel 7` untuk 2 tes navigasi; Firefox + WebKit setiap malam.

**Backend di CI:** `docker compose` menyalakan Postgres (port 5491) + Flask API (5091) dengan **database tes yang sudah diisi data awal**; `webServer` menjalankan `next build && next start` di 3091; setiap tes membuat user/data sendiri lewat helper API (atau satu user awal per worker) supaya tes tetap mandiri; layanan luar (AI, email) dipalsukan dengan `page.route` atau test double di API.

**Setiap malam:** eksekusi lintas browser penuh, snapshot visual halaman penting, Lighthouse CI / anggaran Web Vitals, E2E terhadap deployment staging.

**Artifact:** laporan HTML + trace diunggah saat gagal; tes flaky dicatat dan diperbaiki dalam satu sprint.
:::

### 📝 Checklist review mandiri

- [ ] E2E menutup perjalanan pengguna, bukan setiap kasus tepi
- [ ] Tes tidak bergantung pada data tes lain
- [ ] CI memakai build production

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/web/m4/w6/01-playwright-setup" ai="no-ai" title="Konfigurasi Playwright dan tulis smoke test"}
Tulis `playwright.config.ts` yang peka CI (webServer, projects untuk desktop dan mobile, retries, reporter, trace) dan dua smoke test untuk mini app CareerPilot. Grader memuat config-mu dengan environment variable yang berbeda-beda dan menjalankan tesmu di kedua project.
:::

:::hints
- `devices["Pixel 7"]` memberi ukuran layar mobile, sentuhan, dan user agent.
- Mini app dijalankan dengan `node ../_app/server.mjs`; URL health-nya `/health`.
- Kalau Playwright bilang browser tidak ada, jalankan `npx playwright install chromium` atau pakai cadangan `channel: "chrome"` dari README.
:::

## ✅ Cek cepat

:::quiz
Kenapa `retries: 2` di CI berbahaya kalau tidak ada yang melihat tes yang di-retry?

Retry menyembunyikan tes flaky: bug timing yang nyata (di tes atau di aplikasi) lulus di percobaan kedua dan tidak pernah diperbaiki. Pakai daftar "flaky" di laporan HTML dan trace-nya untuk memperbaikinya.
:::

:::quiz
Apa bedanya `page.getByRole("button", { name: "Save" })` dan `page.locator("button.save")`?

Locator role mencocokkan apa yang dilihat pengguna dan screen reader, dan tetap bertahan saat gaya diubah. Locator CSS bergantung pada cara HTML kebetulan ditulis dan tidak mengecek aksesibilitas.
:::

## 📚 Lanjut belajar

- [Dokumentasi Playwright: Installation](https://playwright.dev/docs/intro) · [Configuration](https://playwright.dev/docs/test-configuration) · [Best Practices](https://playwright.dev/docs/best-practices)
- Dokumentasi Next.js (tersedia di dalam proyek): Testing → Playwright
- [Playwright: Trace viewer](https://playwright.dev/docs/trace-viewer)

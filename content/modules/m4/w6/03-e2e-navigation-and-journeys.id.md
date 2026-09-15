---
title: "E2E: Navigasi & Perjalanan Pengguna"
summary: Menguji cara pengguna berpindah di aplikasi — login sekali dengan storageState, halaman yang dilindungi, link aktif, state di URL, tombol back, 404, judul dan breadcrumb, perjalanan lengkap dengan test.step, dan menjalankan E2E di CI.
sourceHash: d6275fdafbed
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Login **sekali** dengan setup project dan `storageState`
- Kapan tes butuh session sendiri (logout, perubahan role)
- Menguji **route guard** dan redirect `next`
- Navigasi aktif (`aria-current`), breadcrumb, dan judul halaman
- **State di URL**: search params, reload, back/forward
- Mengecek status HTTP yang asli (404 sungguhan)
- Perjalanan pengguna yang panjang dengan **`test.step`**
- Beberapa role, dan menjalankan E2E di GitHub Actions

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Session** | Server mengingat bahwa kamu sudah login (biasanya lewat cookie) |
| **`storageState`** | File berisi cookie dan localStorage browser yang disimpan |
| **Setup project** | Project Playwright yang jalan duluan untuk menyiapkan sesuatu (seperti login) |
| **Route guard** | Pengecekan yang mengusirmu dari halaman yang tidak boleh kamu lihat |
| **URL state** | State halaman yang disimpan di alamat, seperti `?q=data&page=2` |
| **Breadcrumb** | Jejak "Home › Applications › Data Engineer" |
| **User journey** | Perjalanan lengkap pengguna melewati beberapa halaman untuk menyelesaikan tugas |
| **Sharding** | Membagi tes ke beberapa mesin supaya lebih cepat selesai |

## 🧠 Ide besarnya

Tes navigasi mengecek **papan petunjuk dan pintu** sebuah gedung: bisakah kamu masuk tanpa kartu akses (guard)? Apakah peta menunjukkan "Anda di sini" (link aktif)? Kalau kamu membagikan nomor ruangan (URL) ke teman, apakah ia sampai di tempat yang sama (state di URL)? Apakah pintu "kembali" mengarah ke tempat asalmu?

Tes **journey** adalah seluruh perjalanan satu pengunjung, ditulis per bab (`test.step`), sehingga saat ada yang rusak kamu tahu bab mana yang gagal.

## ❓ Kenapa ini penting

Aplikasi Next.js punya banyak logika navigasi: redirect di `proxy.ts`, layout, `Link`, `useRouter().push/replace`, search params, `notFound()`, judul halaman. Bagian ini sering rusak setelah refactor ("filternya kami pindah ke state React dan sekarang link daftar yang sudah difilter tidak jalan saat dibagikan").

Tanpa tes ini:

- Hasil pencarian hanya ada di state React: membagikan URL atau menekan refresh menghilangkannya.
- Redirect berputar antara `/login` dan `/dashboard` saat cookie sudah kedaluwarsa.
- `/applications/9999` mengembalikan **200** dengan halaman kosong — mesin pencari menyimpan halaman sampah dan monitoring tidak pernah melihat error.
- Setiap tes login lewat UI: suite 40 tes menghabiskan 2 menit hanya untuk mengetik password.

## 📖 Langkah demi langkah

### 1. Login sekali: setup project + `storageState`

```ts
// playwright.config.ts
projects: [
  { name: "setup", testMatch: /.*\.setup\.ts/ },
  { name: "chromium", use: { ...devices["Desktop Chrome"], storageState: "playwright/.auth/user.json" }, dependencies: ["setup"] },
],
```

```ts
// e2e/auth.setup.ts
import { expect, test as setup } from "@playwright/test";

setup("authenticate", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("Email").fill(process.env.E2E_USER_EMAIL!);
  await page.getByLabel("Password").fill(process.env.E2E_USER_PASSWORD!);
  await page.getByRole("button", { name: "Log in" }).click();
  await expect(page.getByRole("heading", { name: "Applications" })).toBeVisible();   // wait until the cookie is set
  await page.context().storageState({ path: "playwright/.auth/user.json" });
});
```

Seperti hotel: kamu check-in di resepsionis **sekali** dan dapat kartu kunci. Setelah itu tinggal tempel kartunya, tidak perlu antre di resepsionis setiap kali.

- `storageState` menyimpan cookie dan localStorage. Setiap tes di `chromium` mulai dalam keadaan sudah login.
- Tambahkan `playwright/.auth` ke `.gitignore` — itu kartu kunci yang masih aktif.
- Untuk **beberapa role**, simpan beberapa file (`member.json`, `admin.json`) dan pakai `test.use({ storageState: "playwright/.auth/admin.json" })` di tes admin.

### 2. Tes yang butuh session baru

```ts
test.describe("without a session", () => {
  test.use({ storageState: { cookies: [], origins: [] } });

  test("protected pages redirect to login", async ({ page }) => {
    await page.goto("/applications");
    await expect(page).toHaveURL(/\/login\?next=%2Fapplications/);
  });
});
```

Logout **membatalkan session bersama di server** — seperti melaporkan kartu kunci bersama sebagai hilang: semua tamu yang memakai salinannya tiba-tiba terkunci di luar. Jadi tes logout harus login sendiri. Kalau tidak, tes lain yang sedang berjalan bersamaan tiba-tiba dilempar ke halaman login — bug klasik "hanya gagal di CI".

### 3. Link aktif, breadcrumb, judul

```ts
const nav = page.getByRole("navigation", { name: "Main" });
await expect(nav.getByRole("link", { name: "Jobs" })).toHaveAttribute("aria-current", "page");

await expect(page).toHaveTitle("Data Engineer · CareerPilot");       // generateMetadata works

await page.getByRole("navigation", { name: "Breadcrumb" }).getByRole("link", { name: "Applications" }).click();
await expect(page).toHaveURL(/\/applications$/);
```

Teks link yang sama bisa muncul di menu utama **dan** di breadcrumb. Mencari di dalam area yang punya nama (`navigation` dengan nama) memilih yang tepat — seperti bilang "papan Applications **di lantai 2**".

### 4. State di URL, reload, dan riwayat

```ts
await page.getByLabel("Search jobs").fill("data");
await page.getByRole("button", { name: "Search" }).click();
await expect(page).toHaveURL(/[?&]q=data/);
await page.reload();
await expect(page.getByTestId("result-count")).toHaveText("5 jobs found");

await page.getByRole("link", { name: "Next page" }).click();
await expect(page).toHaveURL(/page=2/);
await page.goBack();
await expect(page.getByRole("navigation", { name: "Pagination" })).toContainText("Page 1 of 3");
```

Di Next.js, filter yang harus bertahan setelah reload dan bisa dibagikan sebaiknya ada di `searchParams`. Pakai `router.push` kalau pengguna perlu bisa kembali ke langkah itu, dan `router.replace` untuk pencarian sambil mengetik (supaya tombol Back tidak mundur huruf demi huruf).

### 5. Status code yang asli

```ts
const response = await page.goto("/applications/9999");
expect(response?.status()).toBe(404);
await expect(page.getByRole("heading", { name: "Application not found" })).toBeVisible();
```

`notFound()` di Next.js mengembalikan 404 untuk request pertama. Mengklik link di dalam aplikasi tidak membuat response HTTP baru, jadi cek status dengan `page.goto`.

### 6. Journey dengan `test.step`

```ts
test("job seeker moves an application forward", async ({ page }) => {
  await test.step("open the application", async () => {
    await page.getByRole("navigation", { name: "Main" }).getByRole("link", { name: "Applications" }).click();
    await page.getByRole("link", { name: "Backend Engineer" }).click();
  });
  await test.step("move it to interview", async () => {
    await page.getByLabel("Move to").selectOption("interview");
    await page.getByRole("button", { name: "Update status" }).click();
    await expect(page.getByRole("status")).toHaveText("Status updated");
  });
  await test.step("see it in the list", async () => {
    await page.getByRole("navigation", { name: "Breadcrumb" }).getByRole("link", { name: "Applications" }).click();
    await expect(page.getByRole("row", { name: /Backend Engineer/ })).toContainText("interview");
  });
});
```

Step muncul di laporan HTML dan trace, jadi kegagalan terbaca "gagal di: move it to interview" — seperti pelacak paket yang menunjukkan di titik mana paketnya tertahan.

### 7. E2E di GitHub Actions

```yaml
e2e:
  needs: quality
  runs-on: ubuntu-latest
  timeout-minutes: 20
  services:
    postgres:
      image: postgres:18-alpine
      env: { POSTGRES_PASSWORD: postgres }
      ports: ["5491:5432"]
  steps:
    - uses: actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1 # v7.0.1
    - uses: actions/setup-node@820762786026740c76f36085b0efc47a31fe5020 # v7.0.0
      with: { node-version: 24, cache: npm }
    - run: npm ci
    - run: npx playwright install --with-deps chromium
    - run: npm run build
    - run: npx playwright test
      env:
        E2E_USER_EMAIL: ${{ secrets.E2E_USER_EMAIL }}
        E2E_USER_PASSWORD: ${{ secrets.E2E_USER_PASSWORD }}
    - uses: actions/upload-artifact@043fb46d1a93c77aae656e7c1c64a875d1fc6a0a # v7.0.1
      if: failure()
      with: { name: playwright-report, path: playwright-report, retention-days: 7 }
```

- Email dan password akun tes diambil dari **secret CI**, tidak pernah dari kode.
- Laporan diunggah hanya saat tes gagal, supaya kamu bisa membuka trace-nya.
- Untuk suite yang lebih besar, **shard** ke beberapa mesin: `npx playwright test --shard=1/4` dalam matrix, lalu gabungkan laporannya.

### Memilih cara login

| | ✅ | ❌ |
|---|---|---|
| `storageState` bersama | sangat cepat | session dan data dipakai bersama; tes logout/role perlu hati-hati |
| Login per tes lewat UI | benar-benar terpisah | lambat |
| Login per tes lewat API | terpisah dan cepat | butuh login lewat API; UI login tidak ikut dites (tes itu sekali secara terpisah) |

- ✅ Uji guard, redirect `next`, 404, state di URL, dan 1–3 journey teratas.
- 🚫 Jangan uji setiap link di setiap halaman — link checker atau tes komponen lebih murah untuk itu.

## ⚠️ Kesalahan umum

- Meng-commit `playwright/.auth/user.json` (itu session yang masih aktif!).
- Tes logout memakai session bersama → tes lain gagal secara acak.
- Mengecek status code setelah mengklik link di dalam aplikasi (tidak ada response baru).
- Memilih "Applications" dan cocok dengan breadcrumb sekaligus menu → error strict mode Playwright.
- `toHaveURL("/jobs?q=data")` sebagai string persis padahal urutan parameter bisa berubah — pakai regex atau parse `URL`.

## 🏆 Praktik terbaik

- [ ] Login sekali per role dengan setup project; jangan masukkan file `.auth` ke Git.
- [ ] Pakai `storageState: { cookies: [], origins: [] }` untuk tes tanpa login.
- [ ] Beri tes logout dan ganti password session sendiri.
- [ ] Cari di dalam area yang punya nama (`navigation` dengan nama, `main`, `dialog`).
- [ ] Cek `aria-current`, judul, dan breadcrumb — pengguna melihatnya.
- [ ] Taruh state yang bisa dibagikan di URL dan uji reload + back.
- [ ] Cek status HTTP asli untuk halaman error.
- [ ] Pecah journey dengan `test.step`; cukup beberapa saja.
- [ ] Simpan kredensial E2E di secret CI; pakai akun tes khusus, jangan pernah user asli.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan dengan analogi kartu kunci hotel kenapa tes logout yang memakai `storageState` bersama bisa membuat tes *lain* gagal secara acak, dan hanya kadang-kadang.

## 📐 Rancang

CareerPilot punya tiga role (member, mentor, admin). Rancang setup project Playwright (file setup, storage state, project mana bergantung pada project mana) dan daftar tes navigasi untuk izin akses: apa yang boleh dan tidak boleh dilihat serta dibuka oleh setiap role.

:::quiz
Lihat contoh rancangan

```ts
projects: [
  { name: "setup", testMatch: /auth\.setup\.ts/ },          // logs in 3 test accounts, saves member.json / mentor.json / admin.json
  { name: "member", testMatch: /member\/.*\.spec\.ts/, use: { storageState: ".auth/member.json" }, dependencies: ["setup"] },
  { name: "mentor", testMatch: /mentor\/.*\.spec\.ts/, use: { storageState: ".auth/mentor.json" }, dependencies: ["setup"] },
  { name: "admin",  testMatch: /admin\/.*\.spec\.ts/,  use: { storageState: ".auth/admin.json" },  dependencies: ["setup"] },
  { name: "anonymous", testMatch: /anonymous\/.*\.spec\.ts/, use: { storageState: { cookies: [], origins: [] } } },
]
```

| Role | Terlihat di menu | Cek URL langsung |
|---|---|---|
| anonymous | — | `/applications`, `/admin/companies` → login dengan `next` |
| member | Dashboard, My applications | `/mentees` dan `/admin/companies` → 404 (atau halaman 403); `/applications/:id` milik user lain → 404 |
| mentor | + Mentees | lamaran mentee terlihat hanya-baca (tanpa tombol Edit); milik non-mentee → 404; `/admin/*` → 404 |
| admin | + Companies, Users | bisa membuka semua; "Delete company" terlihat |

Tambahan: cek di level API (fixture `request` Playwright) bahwa member yang memanggil Server Action/route admin mendapat 403 — menyembunyikan di UI saja tidak cukup.
:::

### 📝 Checklist review mandiri

- [ ] Satu storage state per role
- [ ] Mengetik URL langsung ikut dites, bukan hanya link yang disembunyikan
- [ ] Project anonymous tidak punya session

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/web/m4/w6/03-e2e-navigation-journeys" ai="no-ai" title="Tes navigasi dengan session tersimpan"}
Tulis setup autentikasi yang menyimpan `storageState`, tes navigasi (guard, link aktif, pencarian lewat URL, pagination dan back, 404, judul dan breadcrumb), dan journey (logout dengan session sendiri, journey multi-langkah). Dinilai dengan 8 mutan.
:::

:::hints
- `page.goto()` mengembalikan response — pakai untuk status 404.
- Cari di dalam menu: `page.getByRole("navigation", { name: "Main" })`.
- Pikirkan tes mana yang mengubah session di server.
:::

## ✅ Cek cepat

:::quiz
Sebuah tes mengecek `await expect(page).toHaveURL("/login")` setelah membuka `/applications` tanpa login, tapi aplikasinya redirect ke `/login?next=%2Fapplications`. Apa yang terjadi, dan bagaimana menulisnya dengan lebih baik?

Tesnya gagal (string persis harus termasuk query-nya). Pakai regular expression, misalnya `/\/login\?next=%2Fapplications/`, yang sekaligus mengecek parameter `next`.
:::

:::quiz
Kenapa memakai `test.step` di journey yang panjang?

Laporan dan trace menunjukkan step mana yang gagal, jadi tes panjang tetap mudah di-debug tanpa harus dipecah menjadi banyak tes yang saling bergantung.
:::

## 📚 Lanjut belajar

- [Playwright: Authentication](https://playwright.dev/docs/auth) · [Projects & dependencies](https://playwright.dev/docs/test-projects) · [Sharding](https://playwright.dev/docs/test-sharding)
- [Playwright: Continuous Integration](https://playwright.dev/docs/ci)

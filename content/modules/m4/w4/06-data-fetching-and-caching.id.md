---
title: "🔥 Data Fetching & Caching di Next.js 16"
summary: Muat data di server tanpa mengantre, tampilkan bagian yang lambat belakangan dengan Suspense, dan cache dengan sengaja memakai Cache Components — use cache, cacheLife, cacheTag, updateTag, dan revalidateTag — tanpa membocorkan data pribadi.
sourceHash: 8810037ff8c5
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Memuat data secara bersamaan, bukan satu per satu
- Menampilkan bagian yang lambat belakangan dengan `<Suspense>` (streaming)
- **Cache Components**: selalu segar secara default, cache hanya yang kamu pilih
- `"use cache"`, `cacheLife`, dan `cacheTag`
- Menyegarkan cache setelah ada perubahan: `updateTag`, `revalidateTag`
- Kenapa data pribadi tidak boleh dibagikan dari cache
- Model caching lama yang akan kamu temui di tutorial

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Cache** | Salinan hasil yang disimpan, dipakai ulang agar tidak mengerjakan ulang |
| **Waterfall** | Request yang mengantre satu per satu, membuat halaman lambat |
| **Streaming** | Mengirim halaman sepotong-sepotong: bagian cepat dulu, yang lambat belakangan |
| **`<Suspense>`** | Menampilkan pengganti sementara sampai bagian yang lambat siap |
| **Stale** | Data lama tapi masih bisa dipakai |
| **Revalidate / invalidate** | Menandai salinan cache sebagai lama agar disegarkan |
| **Cache tag** | Label pada data cache, agar semua yang berlabel sama bisa disegarkan sekaligus |
| **Cache key** | Yang membedakan dua entri cache (misalnya id lowongan) |

## 🧠 Ide besarnya

Caching itu seperti **warung yang menyiapkan menu favorit sejak pagi**. Nasi goreng yang dipesan semua orang (daftar lowongan publik) bisa disiapkan duluan dan langsung disajikan, lalu diperbarui setiap jam. Tapi hidangan yang dibuat untuk **alergi satu pelanggan** (lamaran miliknya sendiri) harus dimasak baru khusus untuknya — memberikannya ke orang lain adalah bencana.

Keahliannya adalah memberi label yang benar pada setiap hidangan, dan membuang hidangan yang sudah disiapkan saat resepnya berubah (invalidation).

## ❓ Kenapa ini penting

Membangun setiap halaman dari nol dan memanggil Flask di setiap request itu lambat dan mahal saat banyak orang memakai aplikasimu. Tapi menampilkan data yang lama atau salah jauh lebih buruk. Next.js membiarkanmu memutuskan **per function atau component**: apa yang boleh dipakai ulang, berapa lama, dan bagaimana menyegarkannya setelah ada perubahan.

Yang salah kalau tanpa rencana:
- **Waterfall**: `await getUser()`, lalu `await getApplications()`, lalu `await getStats()` — tiga kali lebih lambat dari seharusnya.
- Endpoint AI yang lambat menahan seluruh dashboard.
- **Data pribadi di-cache**: pengguna A melihat lamaran pengguna B — insiden privasi.
- Lowongan yang sudah diedit tidak berubah karena tidak ada yang menyegarkan cache.

:::note[Model caching Next.js yang mana?]
Next.js 16 memperkenalkan **Cache Components**, diaktifkan dengan `cacheComponents: true` di `next.config.ts`. Materi ini mengajarkan model itu (yang dibahas pertama di dokumentasi Next.js). Proyek tanpa pengaturan itu memakai **model lama** (langkah 8). Cek `next.config.ts` sebelum mengikuti saran dari tutorial.
:::

## 📖 Langkah demi langkah

### 1. Bersamaan, bukan satu per satu

```tsx
// ❌ waterfall
const user = await getUser();
const applications = await getApplications();

// ✅ start together, await together
const [user, applications] = await Promise.all([getUser(), getApplications()]);
```

Seperti memesan makanan dan minuman sekaligus, bukan menunggu makanan datang dulu baru memesan minuman. Satu per satu hanya benar kalau sebuah request **butuh hasil** dari request sebelumnya.

### 2. Tampilkan bagian yang lambat belakangan

```tsx
export default function DashboardPage() {
  return (
    <>
      <h1>Dashboard</h1>                                   {/* sent immediately */}
      <Suspense fallback={<StatsSkeleton />}>
        <Stats />                                          {/* async; streams when ready */}
      </Suspense>
      <Suspense fallback={<MatchSkeleton />}>
        <AiMatchCard />                                    {/* slow AI call doesn't block Stats */}
      </Suspense>
    </>
  );
}
```

- Heading langsung tampil. Setiap `<Suspense>` menampilkan pengganti sementaranya sampai bagian itu siap.
- Kartu AI yang lambat tidak menahan statistik — seperti restoran yang menyajikan setiap hidangan saat sudah siap, bukan menunggu yang paling lama.
- `loading.tsx` membungkus seluruh halaman; `<Suspense>` membiarkanmu memilih bagian yang lebih kecil.

### 3. Nyalakan Cache Components

```ts
// next.config.ts
import type { NextConfig } from "next";
const nextConfig: NextConfig = { cacheComponents: true };
export default nextConfig;
```

Dengan pengaturan ini:
- Pemuatan data **selalu segar (dinamis) secara default**. Tidak ada yang di-cache kecuali kamu memintanya.
- Next.js membangun **kerangka** halaman yang sudah jadi dan mengalirkan bagian yang segar ke dalamnya.
- Kalau data yang tidak di-cache tidak berada di dalam `<Suspense>`, Next.js menampilkan error yang membantu, memintamu membungkusnya atau meng-cache-nya.

### 4. `"use cache"` + `cacheLife`

```ts
import { cacheLife, cacheTag } from "next/cache";

export async function getPublicJobs() {
  "use cache";
  cacheLife("hours");        // stale 5m, revalidate 1h, expire 1d
  cacheTag("jobs");
  const res = await fetch(`${process.env.API_URL}/api/v1/jobs`);
  return (await res.json()).data;
}

export async function getJob(id: number) {
  "use cache";
  cacheLife("hours");
  cacheTag("jobs", `job-${id}`);   // arguments are part of the cache key automatically
  …
}
```

- `"use cache"` = "simpan hasil function ini".
- `cacheLife("hours")` = berapa lama tetap segar — seperti label "baik digunakan sebelum" pada makanan.
- `cacheTag("jobs")` = sebuah label, agar nanti kamu bisa membuang semua salinan berlabel `jobs`.
- Argumen (seperti `id`) otomatis membuat entri terpisah: lowongan 1 dan lowongan 2 di-cache sendiri-sendiri.

| Profil | stale | revalidate | expire |
|---|---|---|---|
| `seconds` | 30 dtk | 1 dtk | 60 dtk |
| `minutes` | 5 mnt | 1 mnt | 1 jam |
| `hours` | 5 mnt | 1 jam | 1 hari |
| `days` | 5 mnt | 1 hari | 1 minggu |
| `weeks` | 5 mnt | 1 minggu | 30 hari |
| `max` | 5 mnt | 30 hari | 1 tahun |

`"use cache"` juga bisa ditaruh di bagian atas component atau halaman async, atau di bagian atas file. Selalu pasangkan dengan `cacheLife`.

### 5. Data pribadi: tidak pernah dibagikan

```tsx
async function MyApplicationsSummary() {
  const session = (await cookies()).get("session")?.value;   // runtime API → request-time
  if (!session) return <p>Log in to track applications</p>;
  const applications = await getMyApplications(session);     // NOT "use cache"
  return <p>You have {applications.length} applications</p>;
}

// page
<Suspense fallback={<p role="status">Loading your applications…</p>}>
  <MyApplicationsSummary />
</Suspense>
```

Aturan sederhana:
- Data yang sama untuk semua orang → cache, dengan tag.
- Data yang berbeda per pengguna → **jangan** taruh di cache bersama. Muat baru, di dalam `<Suspense>`.
- Jangan pernah memanggil `cookies()` atau `headers()` **di dalam** function `"use cache"`.

### 6. Segarkan cache setelah ada perubahan

```ts
"use server";
import { updateTag } from "next/cache";

export async function closeJob(jobId: number) {
  const session = (await cookies()).get("session")?.value;
  if (!session) return { ok: false, message: "Please log in" };
  const res = await fetch(`${process.env.API_URL}/api/v1/jobs/${jobId}/close`, { method: "POST", headers: { Authorization: `Bearer ${session}` } });
  if (!res.ok) return { ok: false, message: "Couldn't close the job" };
  updateTag("jobs");
  updateTag(`job-${jobId}`);
  return { ok: true };
}
```

| API | Di mana | Fungsinya |
|---|---|---|
| `updateTag(tag)` | Server Action | membuang salinan cache **saat itu juga** → pengguna langsung melihat perubahannya |
| `revalidateTag(tag, "max")` | Server Action, Route Handler (seperti webhook dari Flask) | menyajikan salinan lama sambil menyegarkan di latar belakang |
| `revalidatePath(path)` | Server Action, Route Handler | menyegarkan satu halaman utuh saat kamu tidak tahu tag-nya |

- Segarkan hanya **setelah** perubahannya berhasil.
- Saat **Flask** yang mengubah data (tool admin, pengguna lain), Flask bisa memanggil webhook Route Handler Next.js yang menjalankan `revalidateTag` — ide webhook bertanda tangan yang sama dari Modul 2 Minggu 5.

### 7. Browser punya cache sendiri

`router.refresh()` memuat ulang data server untuk halaman saat ini. TanStack Query meng-cache data di dalam browser (materi 07). Keduanya lapisan yang berbeda — saat melihat data lama, tanyakan dulu **lapisan mana** yang menyimpannya.

### 8. Model lama (tanpa `cacheComponents`)

- `fetch` **tidak** di-cache secara default (sejak Next.js 15). Nyalakan dengan `fetch(url, { cache: "force-cache", next: { revalidate: 3600, tags: ["jobs"] } })`.
- `unstable_cache(fn, keyParts, { tags, revalidate })` untuk data yang bukan `fetch`.
- Pengaturan halaman: `export const dynamic = "force-dynamic" | "force-static"`, `export const revalidate = 3600`.

Kamu akan melihat ini di proyek lama dan tutorial untuk Next.js 13–15.

## ⚠️ Kesalahan umum

- Mengikuti tutorial Next.js 14 ("fetch di-cache secara default") di proyek Next.js 16.
- Meng-cache function yang membaca sesi pengguna.
- Lupa menyegarkan setelah update, lalu "memperbaikinya" dengan mematikan caching di mana-mana.
- Mengetes caching hanya dengan `next dev` (perilakunya berbeda dengan production).
- Meng-cache semuanya "biar cepat" sebelum mengukur — data yang benar lebih penting.

## 🏆 Praktik terbaik

- [ ] Muat data yang tidak saling bergantung secara bersamaan.
- [ ] Bungkus bagian yang lambat dan yang per request dengan `<Suspense>` beserta pengganti sementara yang baik.
- [ ] Putuskan per function: publik → `"use cache"` + `cacheLife` + `cacheTag`; pribadi → tanpa cache.
- [ ] Pakai tag yang konsisten (`jobs`, `job-${id}`) dan segarkan di **setiap** tempat data berubah, termasuk webhook dari backend.
- [ ] `updateTag` setelah perubahan oleh pengguna di Server Action; `revalidateTag` untuk penyegaran di latar belakang.
- [ ] Jangan pernah memanggil `cookies()` / `headers()` di dalam function yang di-cache.
- [ ] Cek caching dengan `next build && next start`.
- [ ] Ketahui model mana yang dipakai proyekmu.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Dengan ide warung, jelaskan ke product manager kenapa daftar lowongan publik boleh sedikit lama (beberapa menit), tapi daftar lowongan tersimpan milik pengguna harus selalu segar dan tidak pernah dibagikan antar pengguna.

## 📐 Rancang

Rencanakan pemuatan dan caching untuk **halaman perusahaan publik** CareerPilot `/companies/[id]`: profil perusahaan (jarang diedit admin), lowongan yang dibuka (berubah setiap hari), statistik gaji (SQL berat, harian), "lamaranmu ke perusahaan ini" (hanya untuk pengguna yang login), dan "ringkasan budaya" dari AI (lambat, mahal, dibuat ulang setiap minggu).

:::quiz
Tampilkan contoh rencananya

| Bagian | Dimuat dengan | Cache | Penyegaran |
|---|---|---|---|
| Profil perusahaan | `getCompany(id)` | `"use cache"`, `cacheLife("days")`, `cacheTag("companies", "company-{id}")` | Server Action edit oleh admin → `updateTag("company-{id}")`; tool admin Flask → webhook → `revalidateTag("company-{id}", "max")` |
| Lowongan yang dibuka | `getCompanyJobs(id)` | `cacheLife("hours")`, `cacheTag("jobs", "company-{id}-jobs")` | lowongan dipublikasikan/ditutup → `updateTag` / `revalidateTag("company-{id}-jobs")` |
| Statistik gaji | `getSalaryStats(id)` | `cacheLife("days")`, `cacheTag("salary-stats")` | job malam hari → `revalidateTag("salary-stats", "max")` |
| Lamaranmu | `getMyApplicationsForCompany(session, id)` | **tanpa cache** (pribadi) | — ; di dalam `<Suspense>`; tampilkan "Login untuk melihat lamaranmu" kalau tidak ada sesi |
| Ringkasan budaya AI | `getCultureSummary(id)` | `cacheLife("weeks")`, `cacheTag("culture-{id}")` | job mingguan → `revalidateTag`; `<Suspense>` sendiri dengan skeleton |

- Profil, lowongan, dan statistik dimuat bersamaan dan membentuk bagian halaman yang cepat dan di-cache.
- Bagian pribadi dan bagian AI dialirkan terpisah, jadi tidak saling menahan.
- `generateMetadata` memakai ulang `getCompany` yang sudah di-cache.
- Cek dengan `next build && next start`, dan pastikan dua pengguna tes yang berbeda tidak pernah melihat bagian milik satu sama lain.
:::

### 📝 Checklist self-review

- [ ] Data publik dan pribadi dipisahkan
- [ ] Setiap function yang di-cache punya umur dan tag
- [ ] Setiap tempat yang mengubah data menyegarkan cache
- [ ] Bagian yang lambat dialirkan sendiri-sendiri

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/web/m4/w4/06-caching" ai="no-ai" title="Cache data publik, alirkan data pribadi, segarkan setelah perubahan"}
Nyalakan Cache Components, cache function lowongan publik dengan `"use cache"`, `cacheLife`, dan tag, biarkan lamaran pribadi tanpa cache di dalam `<Suspense>` (membaca cookie), dan tulis Server Action yang mengecek sesi dan memanggil `updateTag` hanya setelah perubahannya berhasil.
:::

:::hints
- `"use cache";` harus menjadi **baris pertama** di dalam function.
- `cacheTag("jobs", \`job-${id}\`)` menerima beberapa tag.
- Di halaman, render `<JobList />` langsung dan `<MyApplicationsSummary />` di dalam `<Suspense fallback={…}>`.
:::

## ✅ Cek cepat

:::quiz
Dengan `cacheComponents: true`, apa yang terjadi pada `fetch` di Server Component tanpa `"use cache"`?

Dijalankan baru di setiap request. Kalau tidak berada di dalam `<Suspense>`, Next.js memperingatkanmu agar meng-cache-nya atau mengalirkannya.
:::

:::quiz
`updateTag` vs `revalidateTag`?

`updateTag` (hanya di Server Action) langsung membuang salinan cache, jadi pengguna melihat perubahannya. `revalidateTag` menandainya lama dan menyegarkannya di latar belakang; juga bisa dipakai di Route Handler.
:::

## 📚 Lanjut belajar

- Dokumentasi Next.js (tersedia di dalam proyek): Fetching Data; Caching; Revalidating; referensi `use cache`, `cacheLife`, `cacheTag`, `updateTag`; Caching (Previous Model)
- [React docs: Suspense](https://react.dev/reference/react/Suspense)

---
title: "RBAC & Conditional Rendering"
summary: Tampilkan layar yang tepat untuk setiap role dan tegakkan aturannya di tempat yang penting — tabel izin alih-alih cek role, aturan kepemilikan, menu yang difilter, component Can, dan pengecekan di server.
sourceHash: c05ad7d3a8f3
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Role vs **permission**: tanyakan "bolehkah pengguna ini melakukan X?", bukan "apakah pengguna ini admin?"
- Satu **file aturan izin** yang dipakai tampilan dan server
- Aturan **kepemilikan**: data milikku, data milik mentee-ku
- Menampilkan atau menyembunyikan UI: menu yang difilter, component `<Can>`, sembunyikan vs nonaktifkan
- **Menegakkan** izin di Server Action, halaman, dan API
- Kapan menjawab 403 vs 404

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Role** | Kelompok pengguna: member, mentor, admin |
| **Permission** | Satu hal yang boleh dilakukan pengguna: "mengelola perusahaan" |
| **RBAC** | Role-Based Access Control: role memberikan izin |
| **Ownership** | "Lamaran ini milik pengguna 7" |
| **Policy** | Function yang memutuskan boleh/tidak untuk sebuah aksi |
| **Enforce** | Benar-benar memblokir aksinya di server |
| **Deny by default** | Kalau tidak ada aturan yang bilang boleh, jawabannya tidak |
| **403 / 404** | "Tidak diizinkan" / "Tidak ditemukan" |

## 🧠 Ide besarnya

Di gedung perkantoran, **kartu akses**-mu (role) membuka pintu-pintu tertentu (permission). Layar di lobi mungkin hanya menampilkan lantai yang boleh kamu datangi — itu memudahkan (conditional rendering). Tapi **kunci pintu** tetap mengecek kartumu. Kalau ada yang lewat tangga darurat, kunci itulah yang menghentikannya.

- Menyembunyikan UI = layar di lobi (kenyamanan).
- Otorisasi di server = kunci pintu (keamanan).

Kamu butuh keduanya, tapi hanya kunci pintu yang merupakan keamanan.

## ❓ Kenapa ini penting

CareerPilot punya **member** (pencari kerja), **mentor** yang me-review lamaran mentee-nya, dan **admin** yang mengelola perusahaan dan pengguna. Tanpa model yang jelas, pengecekan tersebar di mana-mana:

```tsx
{user.role === "admin" || user.role === "mentor" ? <MenteesLink /> : null}
```

Saat kamu menambahkan role "career coach", kamu harus mencari di 40 file.

Masalah yang lebih buruk:
- Member tidak bisa melihat tombol "Hapus perusahaan" — tapi Server Action-nya tanpa pengecekan, jadi memanggilnya dari DevTools benar-benar menghapus perusahaan.
- `/applications/15` menampilkan lamaran orang lain karena halamannya hanya mengecek "sudah login".
- Layar-layar tidak sepakat ("mentor boleh berkomentar" di satu tempat, tapi tidak di tempat lain).

## 📖 Langkah demi langkah

### 1. Role memberikan izin

```ts
// lib/permissions.ts — pure TypeScript, usable on server and client
export type Role = "member" | "mentor" | "admin";
export type Permission =
  | "applications:read:own" | "applications:write:own"
  | "applications:read:mentees" | "notes:comment"
  | "companies:manage" | "users:manage";

const MEMBER = ["applications:read:own", "applications:write:own"] as const;

export const ROLE_PERMISSIONS: Record<Role, readonly Permission[]> = {
  member: MEMBER,
  mentor: [...MEMBER, "applications:read:mentees", "notes:comment"],
  admin: [...MEMBER, "applications:read:mentees", "notes:comment", "companies:manage", "users:manage"],
};

export function can(user: { role: Role } | null, permission: Permission) {
  return !!user && Object.hasOwn(ROLE_PERMISSIONS, user.role) && ROLE_PERMISSIONS[user.role].includes(permission);
}
```

- Satu **tabel** menyatakan role mana punya izin apa — seperti daftar pintu yang bisa dibuka setiap kartu akses.
- Kode fitur bertanya tentang **izin** (`can(user, "companies:manage")`), bukan nama role.
- Menambah role = mengedit satu tabel.
- `can` menjawab **tidak** kalau tidak ada pengguna atau role-nya tidak dikenal (deny by default).

### 2. Kepemilikan dan hubungan

Izin saja tidak bisa menjawab "bolehkah Sari mengedit lamaran **yang ini**?".

```ts
export function canEditApplication(user: Actor, app: { ownerId: number }) {
  if (user.role === "admin") return true;
  return app.ownerId === user.id && can(user, "applications:write:own");
}

export function canViewApplication(user: Actor, app: { ownerId: number }) {
  if (user.role === "admin") return true;
  if (app.ownerId === user.id) return can(user, "applications:read:own");
  return can(user, "applications:read:mentees") && (user.menteeIds ?? []).includes(app.ownerId);
}
```

Seperti hotel: kartu kuncimu berfungsi di **lantai** yang diizinkan tipe kamarmu (izin), tapi hanya membuka **kamarmu sendiri** (kepemilikan). Kebanyakan aplikasi butuh persis ini: **RBAC + kepemilikan**. Saat aturan bergantung pada banyak detail (departemen, waktu, paket langganan), tim beralih ke policy engine.

### 3. Menampilkan dan menyembunyikan UI

```tsx
// Navigation derived from the same policy
export const navFor = (user: User | null) => NAV_ITEMS.filter((item) => !item.requires || can(user, item.requires));

// Declarative helper
export function Can({ user, permission, children, fallback = null }: CanProps) {
  return <>{can(user, permission) ? children : fallback}</>;
}

<Can user={user} permission="companies:manage" fallback={<p>Ask an admin to edit companies.</p>}>
  <DeleteCompanyButton companyId={company.id} />
</Can>
```

- Menu dibangun dari function `can` yang sama, jadi layar-layar tidak bisa tidak sepakat.
- `<Can>` hanya menampilkan children-nya kalau diizinkan, kalau tidak menampilkan `fallback`.

| Situasi | Sembunyikan atau nonaktifkan? |
|---|---|
| Pengguna **tidak akan pernah** punya akses (member → panel admin) | **sembunyikan** |
| Pengguna **bisa** mendapat akses (upgrade paket, verifikasi akun) | **nonaktifkan + jelaskan caranya** |
| Sementara tidak tersedia (form belum valid, sudah melamar) | **nonaktifkan + beri alasannya** |

### 4. Tegakkan di server — di setiap pintu

```ts
// Server Action
"use server";
export async function deleteCompanyAction(companyId: number) {
  const session = await verifySession();                       // authentication
  if (!can(session, "companies:manage")) {                     // authorization
    return { ok: false, message: "You don't have permission to do that" } as const;
  }
  await deleteCompany(companyId);
  return { ok: true } as const;
}
```

```tsx
// Page for a single resource
export default async function ApplicationPage({ params }: PageProps<"/applications/[id]">) {
  const user = await getCurrentUser();
  const app = await getApplication(Number((await params).id));
  if (!app || !canViewApplication(user, app)) notFound();       // 404: don't reveal it exists
  return <ApplicationDetail app={app} canEdit={canEditApplication(user, app)} />;
}
```

- Setiap Server Action: cek sesi dulu, lalu izinnya.
- Setiap halaman berisi data pribadi: cek sebelum menampilkan apa pun.
- **Flask API** mengecek lagi (Modul 2 Minggu 5). Pengecekan di Next.js memberi pengalaman yang baik; pengecekan di API melindungi data dari semua jenis client (aplikasi mobile, script).

### 5. 401, 403, atau 404?

| Kasus | Jawaban |
|---|---|
| Belum login | **401** / redirect ke login |
| Sudah login tapi tidak diizinkan, dan bukan rahasia bahwa halamannya ada (halaman admin) | **403** "Kamu tidak punya izin" |
| Datanya milik orang lain (lamaran #15) | **404** — jangan beri tahu bahwa datanya ada |

Seperti resepsionis hotel: kalau kamu bertanya tentang kamar tamu lain, mereka menjawab "tidak ada pesanan seperti itu", bukan "itu kamar orang lain".

:::note[forbidden() dan unauthorized()]
Next.js punya helper `forbidden()` dan `unauthorized()` dengan file `forbidden.tsx` / `unauthorized.tsx`, tapi di Next.js 16 keduanya masih **eksperimental** (`experimental.authInterrupts`). Mengembalikan hasil, atau memanggil `notFound()` / `redirect()`, sudah berfungsi sekarang.
:::

## ⚠️ Kesalahan umum

- `{count && <Badge />}` menampilkan `0` saat `count` bernilai 0 → pakai `count > 0 &&`.
- Mengecek izin di halaman tapi tidak di Server Action yang dipanggilnya.
- Memercayai role atau izin yang dikirim dari browser (`formData.get("role")`).
- Menyimpan izin di sesi selamanya — admin yang dicopot tetap punya akses sampai cookie-nya kedaluwarsa.
- `ROLE_PERMISSIONS[user.role]` dengan role yang tidak tepercaya seperti `"toString"` → mengembalikan function, bukan `undefined`. Pakai `Object.hasOwn`.
- Membangun policy engine besar hanya untuk dua role.

## 🏆 Praktik terbaik

- [ ] Kode fitur bertanya tentang **izin**, bukan nama role.
- [ ] **Deny by default**: role yang tidak dikenal dan pengguna yang tidak ada tidak mendapat apa-apa.
- [ ] Cek izin di setiap Server Action, Route Handler, dan halaman pribadi — dan di API.
- [ ] Sembunyikan yang tidak akan pernah bisa dipakai pengguna; nonaktifkan dengan penjelasan kalau suatu saat bisa.
- [ ] 404 untuk data milik pengguna lain; 403 kalau bukan rahasia bahwa halamannya ada.
- [ ] Tes aturan izin sebagai tabel (role × izin) — pure dan cepat.
- [ ] Baca role dari sesi yang sudah diverifikasi; cek ulang role penting dari API kalau bisa berubah.
- [ ] Catat percobaan yang ditolak pada aksi admin.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Dengan ide kartu akses, jelaskan ke product manager kenapa "kami sudah menyembunyikan tombolnya" belum cukup untuk mencegah member menghapus perusahaan.

## 📐 Rancang

CareerPilot menambahkan role **"recruiter"**. Recruiter bisa memasang lowongan untuk **perusahaannya sendiri**, melihat (tapi tidak mengubah) lamaran ke lowongan itu, dan menambahkan catatan yang hanya bisa dilihat recruiter lain dari perusahaan yang sama. Perbarui daftar izin, tulis function kepemilikan yang dibutuhkan, dan daftar setiap titik masuk server yang harus mengeceknya.

:::quiz
Tampilkan contoh desainnya

```ts
type Role = "member" | "mentor" | "recruiter" | "admin";
type Permission =
  | ... existing
  | "jobs:write:company"
  | "applications:read:company"
  | "notes:company";

ROLE_PERMISSIONS.recruiter = ["jobs:write:company", "applications:read:company", "notes:company"];

type Actor = { id: number; role: Role; companyId?: number; menteeIds?: number[] };

const canManageJob = (u: Actor, job: { companyId: number }) =>
  u.role === "admin" || (can(u, "jobs:write:company") && u.companyId === job.companyId);

const canViewCandidateApplication = (u: Actor, app: { job: { companyId: number } }) =>
  u.role === "admin" || (can(u, "applications:read:company") && u.companyId === app.job.companyId);

const canSeeNote = (u: Actor, note: { visibility: "private" | "company"; authorId: number; companyId?: number }) =>
  note.authorId === u.id || (note.visibility === "company" && can(u, "notes:company") && u.companyId === note.companyId);
```

**Titik masuk yang wajib mengecek:**
- `createJobAction`, `updateJobAction`, `closeJobAction`
- `app/(recruiter)/jobs/[id]/applicants/page.tsx` (404 untuk perusahaan lain)
- `addCompanyNoteAction`
- Route Handler `GET /api/jobs/[id]/applicants` (kalau papannya memakai TanStack Query)
- endpoint Flask untuk semua di atas (sumber kebenaran yang sesungguhnya)

`companyId` harus berasal dari database, jangan pernah dari form. Member tidak boleh pernah melihat catatan recruiter di lamarannya sendiri — tulis tes khusus untuk itu.
:::

### 📝 Checklist self-review

- [ ] Role baru ditambahkan di satu tabel
- [ ] Setiap perubahan dicek lagi di server
- [ ] Akses ke data perusahaan lain menghasilkan 404

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/web/m4/w5/03-rbac" ai="no-ai" title="Aturan izin, <Can>, dan action yang dilindungi"}
Bangun tabel role → izin, aturan kepemilikan untuk mentor dan admin, menu yang difilter, component `<Can>`, dan Server Action yang menolak member dan mentor sebelum memanggil API.
:::

:::hints
- `Object.hasOwn(ROLE_PERMISSIONS, role)` menghindari kejutan dari key bawaan object.
- Cek jalan pintas admin dulu, lalu kepemilikan, lalu hubungan.
- Di action, panggil `verifySession()` sebelum hal lainnya.
:::

## ✅ Cek cepat

:::quiz
Seorang mentor membuka `/applications/15`, milik orang yang bukan mentee-nya. Apa yang sebaiknya dilakukan halaman, dan kenapa status itu?

Panggil `notFound()` (404). Menjawab "403 Forbidden" akan memastikan bahwa lamaran #15 ada dan milik orang lain.
:::

:::quiz
Kenapa `lib/permissions.ts` sebaiknya bebas dari import Next.js dan database?

Agar aturan yang sama bisa berjalan di Server Component, Server Action, Client Component (untuk menampilkan atau menyembunyikan UI), dan unit test, tanpa pemalsuan.
:::

## 📚 Lanjut belajar

- Dokumentasi Next.js (tersedia di dalam proyek): panduan Authentication → Authorization; panduan Data Security
- [OWASP Top 10: Broken Access Control](https://owasp.org/Top10/A01_2021-Broken_Access_Control/)
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)

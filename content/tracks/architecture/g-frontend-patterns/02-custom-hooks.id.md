---
title: "Custom Hooks sebagai Perilaku yang Dapat Dipakai Ulang"
summary: Bagikan perilaku, bukan markup — merancang custom hook dengan masukan dan keluaran yang jelas, logika murni di luar React, callback stabil, pola controlled/uncontrolled, komponen headless, dan testing hook.
sourceHash: d553f7bf234f
---

::part[Pelajari Konsepnya]{n="1"}

## 🎯 Yang akan kamu pelajari

- Kapan logika pantas punya custom hook — dan kapan fungsi biasa lebih baik
- Merancang **API** hook-mu: masukan, keluaran, nama
- Menjaga **logika murni** (hitung halaman, validasi) di fungsi biasa yang dipanggil hook
- **Callback stabil** (`useCallback`, refs) dan kenapa konsumen peduli
- Pola **controlled vs uncontrolled** dengan `useControllableState`
- Komponen **headless**: perilaku di hook, markup dipilih pemanggil
- Testing hook dengan `renderHook`

## 🔤 Istilah penting

| Istilah | Artinya (sederhana) |
|---|---|
| **Custom hook** | Fungsi mulai dengan `use` yang memegang perilaku bisa dipakai ulang |
| **Pure function** | Masukan sama selalu menghasilkan keluaran sama, tanpa efek samping |
| **Hook API** | Apa yang hook menerima dan kembalikan |
| **Stable callback** | Fungsi yang identitasnya tetap antar render |
| **Controlled** | Induk punya nilai dan turunkan ke anak |
| **Uncontrolled** | Komponen simpan nilainya sendiri |
| **Headless component** | Perilaku tanpa tampilan; pemanggil tentukan penampilannya |
| **`renderHook`** | Alat test yang menjalankan hook sendiri |

## 🧠 Ide besarnya

Komponen itu **bata LEGO yang bisa kamu lihat**; hook adalah **motor dan gear di dalamnya**. Motor yang sama bisa menggerakkan mobil, crane, atau kincir angin — masing-masing punya badan beda. `usePagination` bisa menggerakkan pager bertombol angka, tombol "Muat lagi", atau gesekan di ponsel.

## ❓ Kenapa ini penting

Sebelum hook, berbagi perilaku dengan state berarti higher-order component atau render props — lapis pembungkus menumpuk. Hook biarkan kamu tarik "buka/tutup", "halaman", "nilai pilihan kontrol", "pencarian tunda" jadi fungsi, dan komponen mana saja bisa panggilnya, tiap panggilan simpan state **sendiri**.

Gambar motor itu intinya: motor sama menggerakkan mobil, crane atau kincir angin, dan tiap punya badan berbeda. `usePagination` bisa menggerakkan pager bertombol angka, tombol "Muat lagi", atau gesekan di ponsel.

Tapi bukan semua perlu satu: kalau logika tidak punya state dan tidak punya effect, fungsi biasa lebih jelas daripada hook.

## 📖 Langkah demi langkah

### 1. Logika murni dulu, hook belakangan

Kerjakan hitungan di fungsi biasa dulu, baru biarkan hook pegang state di sekitarnya. Logika murni jauh lebih mudah ditest — React tidak perlu.

```ts
// pagination.ts — pure, testable with a table of cases
export function getPageItems({ page, totalPages, siblings = 1 }: Options): (number | "…")[] { … }

// the hook adds React concerns only: memoization and callbacks
export function usePagination({ total, pageSize, page, onPageChange }: Args) {
  const totalPages = Math.max(0, Math.ceil(total / pageSize));
  const items = useMemo(() => getPageItems({ page, totalPages }), [page, totalPages]);
  const goTo = (target: number) => { const p = clamp(target, 1, totalPages); if (p !== page) onPageChange(p); };
  return { totalPages, items, hasPrevious: page > 1, hasNext: page < totalPages, previous: () => goTo(page - 1), next: () => goTo(page + 1), goTo };
}
```

Kalau fungsi tidak panggil hook apa saja, ia bukan hook — jangan kasih nama `useX`.

### 2. Rancang API-nya

| Pertanyaan | Jawaban bagus |
|---|---|
| Nama | apa yang disediakan: `useDisclosure`, `usePagination`, `useOnlineStatus` — bukan `useEffectOnce` |
| Masukan | satu object opsi (gampang diperluas) |
| Keluaran | object untuk banyak nilai; tuple `[value, setValue]` hanya untuk hook seperti `useState` |
| Efek samping | jelas dan dibersihkan |
| Tempat state | dalam (uncontrolled), luar (controlled), atau dua-duanya |

### 3. Callback stabil

```ts
export function useDisclosure(initial = false) {
  const [isOpen, setIsOpen] = useState(initial);
  const open = useCallback(() => setIsOpen(true), []);
  const close = useCallback(() => setIsOpen(false), []);
  const toggle = useCallback(() => setIsOpen((v) => !v), []);
  return { isOpen, open, close, toggle };
}
```

Fungsi stabil bisa diteruskan ke anak yang di-memo dan dipakai di dependency effect tanpa jalankan ulang effect. (React Compiler bisa memo otomatis — library hook sebaiknya tetap tegas.)

### 4. Controlled atau uncontrolled — dukung dua-duanya

Mendukung dua-duanya adalah yang buat komponen terasa profesional: jalan langsung dari box, dan keluar dari jalan saat induk mau kontrol.

```ts
export function useControllableState<T>({ value, defaultValue, onChange }: Options<T>) {
  const [internal, setInternal] = useState(defaultValue);
  const isControlled = value !== undefined;
  const current = isControlled ? value : internal;

  const latest = useRef({ current, isControlled, onChange });
  useEffect(() => { latest.current = { current, isControlled, onChange }; });

  const setValue = useCallback((next: T | ((prev: T) => T)) => {
    const { current: prev, isControlled: controlled, onChange: notify } = latest.current;
    const resolved = typeof next === "function" ? (next as (p: T) => T)(prev) : next;
    if (Object.is(resolved, prev)) return;
    if (!controlled) setInternal(resolved);
    notify?.(resolved);
  }, []);

  return [current, setValue] as const;
}
```

```tsx
<Tabs defaultValue="notes" />                          // uncontrolled: the component remembers
<Tabs value={tab} onValueChange={setTab} />            // controlled: the parent decides (URL, form, store)
```

Ini persis caranya Radix dan shadcn/ui terima `value` dan `defaultValue`.

### 5. Komponen headless

```tsx
function Pager({ total, page, onPageChange }: Props) {
  const { items, hasPrevious, hasNext, previous, next, goTo } = usePagination({ total, pageSize: 20, page, onPageChange });
  return (
    <nav aria-label="Pagination">
      <button onClick={previous} disabled={!hasPrevious}>Previous</button>
      {items.map((item, i) => item === "…" ? <span key={`gap-${i}`}>…</span> : (
        <button key={item} aria-current={item === page ? "page" : undefined} onClick={() => goTo(item)}>{item}</button>
      ))}
      <button onClick={next} disabled={!hasNext}>Next</button>
    </nav>
  );
}
```

Hook punya perilaku; tiap permukaan produk punya markup dan style sendiri.

### 6. Testing

```ts
test.each([[{ page: 5, totalPages: 10 }, [1, "…", 4, 5, 6, "…", 10]]])("%o", (input, expected) => {
  expect(getPageItems(input)).toEqual(expected);
});

const { result, rerender } = renderHook((page) => usePagination({ total: 95, pageSize: 20, page, onPageChange }), { initialProps: 1 });
act(() => result.current.next());
```

### Pilih setup-mu

Tiap opsi di sini ada trade-off:

| | ✅ | ❌ |
|---|---|---|
| Custom hook | pakai ulang perilaku di UI berbeda; bisa ditest | indirection; aturan hook (top level saja) |
| Fungsi biasa | paling sederhana, bebas framework | tidak ada state/effect |
| Perpustakaan headless component | perilaku akses-terjangkau gratis | pelajari API-nya; kontrol kurang |
| Copy-paste | cepat hari ini | perbedaan dan bug besok |

- ✅ Perilaku stateful yang sama di 2+ komponen, atau perilaku rumit layak ditest sendiri.
- ✅ Bungkus API browser dan subscription.
- 🚫 Kode tanpa hook dalam — buat jadi fungsi.
- 🚫 "Hook dewa" balik 20 nilai untuk satu halaman — potong atau tetap di komponen.

## ⚠️ Kesalahan umum

- Panggil hook secara kondisional atau di dalam loop.
- Balik fungsi baru tiap render dan rusak konsumen yang di-memo.
- Ganti komponen antara controlled dan uncontrolled habis mount (`value` dari `undefined` jadi string).
- Hook yang diam-diam bergantung pada context tanpa error membantu saat provider tidak ada.

## 🏆 Praktik terbaik

- [ ] Tarik logika murni jadi fungsi; hook hanya tambah hal React.
- [ ] Nama hook apa yang disediakan; satu object opsi dalam, object keluar.
- [ ] Balik callback stabil; dokumentasi nilai mana yang stabil.
- [ ] Dukung use controlled dan uncontrolled untuk state UI yang bisa dipakai ulang.
- [ ] Tetap hook fokus; komposisi hook kecil jadi lebih besar.
- [ ] Test fungsi murni dengan tabel kasus dan hook dengan `renderHook`.
- [ ] Jangan balik JSX dari hook — balik data dan handler.

::part[Jelaskan & Rancang]{n="2"}

## 🗣️ Jelaskan

Jelaskan analogi "motor dalam LEGO", terus jelaskan ke rekan kenapa `useControllableState` buat `Tabs` yang sama bisa digerakkan state dalam, URL atau perpustakaan form.

## 📐 Rancang

CareerPilot butuh **multi-select** bisa dipakai ulang untuk skill (di form), status (di filter URL), dan bandingkan job (di Zustand). Rancang `useMultiSelect`: masukan, keluaran, dukung controlled/uncontrolled, perilaku keyboard yang mau keluarkan, dan fungsi murni yang mau test terpisah.

:::quiz
Lihat rancangan yang mungkin

```ts
type UseMultiSelectOptions<T> = {
  options: T[];
  getKey: (option: T) => string;
  value?: string[];                    // controlled (URL, RHF, Zustand)
  defaultValue?: string[];             // uncontrolled
  onValueChange?: (keys: string[]) => void;
  max?: number;                        // e.g. 3 for compare
};

type UseMultiSelectResult<T> = {
  selectedKeys: string[];
  isSelected: (key: string) => boolean;
  toggle: (key: string) => "added" | "removed" | "full";
  clear: () => void;
  getOptionProps: (option: T) => { role: "option"; "aria-selected": boolean; onClick: () => void; id: string };
  getListboxProps: () => { role: "listbox"; "aria-multiselectable": true; onKeyDown: (e: KeyboardEvent) => void };
};
```

- Bangun di atas `useControllableState<string[]>`.
- Helper murni: `toggleKey(keys, key, max)` → `{ keys, result }`, `moveActive(index, key, length)` untuk Arrow/Home/End — ditest dengan tabel.
- Prop getter (`getOptionProps`) tetap kawat ARIA konsisten saat pemanggil pilih markup (chip, checkbox, kartu).
:::

### 📝 Checklist review mandiri

- [ ] Logika murni dipisah dari hook
- [ ] Controlled dan uncontrolled didukung
- [ ] Keluaran stabil, terdokumentasi

::ai-review{task="design"}

::part[Latihan Kecil]{n="3"}

:::exercise{path="exercises/web/architecture/g-frontend-patterns/02-custom-hooks" ai="no-ai" title="Halaman, buka/tutup dan state bisa kontrol"}
Tulis algoritma nomor halaman murni dengan hook `usePagination` di atasnya, hook `useDisclosure` dengan callback stabil, dan `useControllableState` yang dukung use controlled dan uncontrolled dengan fungsi updater.
:::

:::hints
- Kumpulkan halaman yang diingin di `Set`, urutkan, lalu sisip `"…"` hanya untuk celah lebih besar dari satu halaman.
- Simpan prop terbaru di ref jadi `setValue` tetap stabil.
- Test algoritma-mu di kertas dengan halaman 1, halaman terakhir, dan tengah.
:::

## ✅ Cek cepat

:::quiz
Dua komponen panggil `useDisclosure()`. Mereka bagikan `isOpen`?

Tidak. Hook bagikan logika, bukan state — tiap panggil punya state sendiri. Untuk bagikan state, angkat ke atas, pakai context atau store.
:::

:::quiz
Kenapa `setValue` dari `useControllableState` tidak boleh ganti identitas saat `onChange` ganti?

Konsumen taruh di dependency effect atau teruskan ke anak di-memo; fungsi baru tiap render akan jalankan ulang effect dan render ulang anak tanpa perlu.
:::


## 📚 Lanjut belajar

- [Dokumentasi React: Reusing Logic with Custom Hooks](https://react.dev/learn/reusing-logic-with-custom-hooks)
- [React Aria hooks](https://react-spectrum.adobe.com/react-aria/hooks.html)
- [Kent C. Dodds: Inversion of Control](https://kentcdodds.com/blog/inversion-of-control)

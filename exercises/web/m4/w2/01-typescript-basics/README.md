# M4 · W2 · 01 — From JavaScript to TypeScript

> 🚫🤖 **No-AI** · ⏱️ ~60 min · edit **`salary.ts`**

`salary.ts` is plain JavaScript renamed to `.ts`, with type errors and hidden bugs. Add types and fix it so that **`tsc` passes in strict mode** and the behavior matches:

| Export | Type | Behavior |
|---|---|---|
| `type Currency` | `"IDR" \| "USD"` | |
| `type SalaryRange` | `readonly [min: number \| null, max: number \| null]` | a labeled tuple |
| `parseSalary(input)` | `(input: string) => number \| null` | `"Rp 12.000.000"` → `12000000`; `"12000000"` → `12000000`; `"$1,500"` → `1500`; anything without digits → `null` |
| `parseRange(text)` | `(text: string) => SalaryRange` | `"Rp 9.000.000 - Rp 14.000.000"` → `[9000000, 14000000]`; one number → `[n, n]`; none → `[null, null]` |
| `formatAmount(amount, currency = "IDR")` | `(amount: number, currency?: Currency) => string` | IDR → `"Rp 12.000.000"` (dots every 3 digits), USD → `"$1,500"` (commas) — whole numbers only, round first |
| `midpoint(range)` | `(range: SalaryRange) => number \| null` | average of min and max, rounded down; `null` unless both exist |

`salary.types.ts` (don't edit) contains type-level checks, including lines marked `@ts-expect-error` that must **fail** to compile — so your types can't be too loose. Don't use `any`.

```bash
cd exercises/web
npx vitest run m4/w2/01-typescript-basics   # runs the behavior tests AND tsc
```

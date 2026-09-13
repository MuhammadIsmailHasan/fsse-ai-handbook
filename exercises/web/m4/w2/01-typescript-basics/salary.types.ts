// Type-level checks. Don't edit. Lines with @ts-expect-error MUST be type errors.
import { expectTypeOf } from "vitest";
import { formatAmount, midpoint, parseRange, parseSalary, type Currency, type SalaryRange } from "./salary";

expectTypeOf(parseSalary).toEqualTypeOf<(input: string) => number | null>();
expectTypeOf(parseRange).returns.toEqualTypeOf<SalaryRange>();
expectTypeOf<Currency>().toEqualTypeOf<"IDR" | "USD">();
expectTypeOf(formatAmount).parameter(1).toEqualTypeOf<Currency | undefined>();
expectTypeOf(midpoint).returns.toEqualTypeOf<number | null>();
expectTypeOf<SalaryRange>().toEqualTypeOf<readonly [min: number | null, max: number | null]>();

// @ts-expect-error — parseSalary only accepts strings
parseSalary(12);
// @ts-expect-error — unknown currency
formatAmount(10, "EUR");

const range: SalaryRange = [1, 2];
// @ts-expect-error — the tuple is readonly
range[0] = 5;

const maybe = parseSalary("x");
// @ts-expect-error — must handle null before doing math
maybe.toFixed();

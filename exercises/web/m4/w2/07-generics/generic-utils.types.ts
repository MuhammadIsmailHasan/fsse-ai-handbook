// Type-level checks. Don't edit.
import { expectTypeOf } from "vitest";
import { createStore, firstOrNull, groupBy, paginate, pick, tryCatch, type Paginated, type Result } from "./generic-utils";

interface Job {
  id: number;
  title: string;
  status: "saved" | "applied";
  salaryMax: number | null;
}
declare const jobs: Job[];
declare const job: Job;

expectTypeOf(groupBy(jobs, (j) => j.status)).toEqualTypeOf<Partial<Record<"saved" | "applied", Job[]>>>();
expectTypeOf(pick(job, ["title", "id"])).toEqualTypeOf<Pick<Job, "title" | "id">>();
// @ts-expect-error — not a key of Job
pick(job, ["company"]);

expectTypeOf(tryCatch(async () => 42)).resolves.toEqualTypeOf<Result<number>>();
async function useResult() {
  const result = await tryCatch(async () => "hi");
  if (result.ok) expectTypeOf(result.value).toEqualTypeOf<string>();
  else expectTypeOf(result.error).toEqualTypeOf<Error>();
  // @ts-expect-error — must check ok before reading value
  result.value;
}

expectTypeOf(paginate(jobs, 1, 20)).toEqualTypeOf<Paginated<Job>>();
expectTypeOf(firstOrNull(jobs)).toEqualTypeOf<Job | null>();

const store = createStore({ count: 0 });
expectTypeOf(store.get()).toEqualTypeOf<{ count: number }>();
store.set((previous) => ({ count: previous.count + 1 }));
// @ts-expect-error — wrong shape
store.set({ count: "one" });
expectTypeOf(store.subscribe(() => {})).toEqualTypeOf<() => void>();

export { useResult };

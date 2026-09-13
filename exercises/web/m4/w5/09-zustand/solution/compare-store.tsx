"use client";

import { createContext, useContext, useState, type ReactNode } from "react";
import { useStore } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";
import { createStore } from "zustand/vanilla";

export type CompareState = {
  jobIds: number[];
  isTrayOpen: boolean;
  toggleJob: (id: number) => "added" | "removed" | "full";
  clear: () => void;
  setTrayOpen: (open: boolean) => void;
};

const MAX_COMPARE = 3;

export function createCompareStore(initial?: Partial<Pick<CompareState, "jobIds" | "isTrayOpen">>) {
  return createStore<CompareState>()(
    persist(
      (set, get) => ({
        jobIds: [],
        isTrayOpen: false,
        ...initial,
        toggleJob: (id) => {
          const { jobIds } = get();
          if (jobIds.includes(id)) {
            set({ jobIds: jobIds.filter((jobId) => jobId !== id) });
            return "removed";
          }
          if (jobIds.length >= MAX_COMPARE) return "full";
          set({ jobIds: [...jobIds, id], isTrayOpen: true }); // always a new array: never mutate
          return "added";
        },
        clear: () => set({ jobIds: [], isTrayOpen: false }),
        setTrayOpen: (open) => set({ isTrayOpen: open }),
      }),
      {
        name: "careerpilot-compare",
        storage: createJSONStorage(() => localStorage),
        partialize: (state) => ({ jobIds: state.jobIds }), // UI flags like isTrayOpen aren't worth persisting
      },
    ),
  );
}

type CompareStore = ReturnType<typeof createCompareStore>;

const CompareStoreContext = createContext<CompareStore | null>(null);

export function CompareStoreProvider({ initial, children }: { initial?: Partial<Pick<CompareState, "jobIds" | "isTrayOpen">>; children: ReactNode }) {
  // One store per provider instance → no state shared between users on the server.
  const [store] = useState(() => createCompareStore(initial));
  return <CompareStoreContext.Provider value={store}>{children}</CompareStoreContext.Provider>;
}

export function useCompareStore<T>(selector: (state: CompareState) => T): T {
  const store = useContext(CompareStoreContext);
  if (!store) throw new Error("useCompareStore must be used inside <CompareStoreProvider>");
  return useStore(store, selector);
}

export const selectCount = (state: CompareState) => state.jobIds.length;
export const selectIsSelected = (id: number) => (state: CompareState) => state.jobIds.includes(id);

export function CompareButton({ jobId }: { jobId: number }) {
  // Selecting a boolean → this button re-renders only when *its* answer changes.
  const isSelected = useCompareStore(selectIsSelected(jobId));
  const toggleJob = useCompareStore((state) => state.toggleJob);
  const [isFull, setIsFull] = useState(false);

  return (
    <>
      <button type="button" aria-pressed={isSelected} onClick={() => setIsFull(toggleJob(jobId) === "full")}>
        Compare
      </button>
      {isFull && <span role="status">You can compare up to 3 jobs</span>}
    </>
  );
}

export function CompareTray() {
  const isOpen = useCompareStore((state) => state.isTrayOpen);
  const count = useCompareStore(selectCount);
  const clear = useCompareStore((state) => state.clear);
  if (!isOpen) return null;
  return (
    <aside aria-label="Compare jobs">
      <h2>{`Compare (${count}/${MAX_COMPARE})`}</h2>
      <button type="button" onClick={clear}>
        Clear
      </button>
    </aside>
  );
}

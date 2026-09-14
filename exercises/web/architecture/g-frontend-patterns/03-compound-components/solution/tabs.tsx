"use client";

import { createContext, useContext, useId, useRef, useState, type ComponentProps, type KeyboardEvent, type ReactNode } from "react";

type TabsContextValue = {
  baseId: string;
  selected: string | undefined;
  select: (value: string) => void;
  listRef: React.RefObject<HTMLDivElement | null>;
};

const TabsContext = createContext<TabsContextValue | null>(null);

function useTabsContext(part: string) {
  const context = useContext(TabsContext);
  if (!context) throw new Error(`Tabs.${part} must be used inside <Tabs>`);
  return context;
}

// Same idea as useControllableState (exercise 02), kept inline here.
type TabsProps = { value?: string; defaultValue?: string; onValueChange?: (value: string) => void; children: ReactNode };

function TabsRoot({ value, defaultValue, onValueChange, children }: TabsProps) {
  const [internal, setInternal] = useState(defaultValue);
  const selected = value !== undefined ? value : internal;
  const baseId = useId();
  const listRef = useRef<HTMLDivElement>(null);

  const select = (next: string) => {
    if (next === selected) return;
    if (value === undefined) setInternal(next);
    onValueChange?.(next);
  };

  return <TabsContext.Provider value={{ baseId, selected, select, listRef }}>{children}</TabsContext.Provider>;
}

const tabId = (baseId: string, value: string) => `${baseId}-tab-${value}`;
const panelId = (baseId: string, value: string) => `${baseId}-panel-${value}`;

function List({ children, ...props }: ComponentProps<"div">) {
  const { listRef } = useTabsContext("List");
  return (
    <div role="tablist" ref={listRef} {...props}>
      {children}
    </div>
  );
}

function Trigger({ value, disabled = false, children }: { value: string; disabled?: boolean; children: ReactNode }) {
  const { baseId, selected, select, listRef } = useTabsContext("Trigger");
  const isSelected = selected === value;

  function onKeyDown(event: KeyboardEvent<HTMLButtonElement>) {
    const tabs = [...(listRef.current?.querySelectorAll<HTMLButtonElement>('[role="tab"]:not([disabled])') ?? [])];
    const index = tabs.indexOf(event.currentTarget);
    const targets: Record<string, HTMLButtonElement | undefined> = {
      ArrowRight: tabs[(index + 1) % tabs.length],
      ArrowLeft: tabs[(index - 1 + tabs.length) % tabs.length],
      Home: tabs[0],
      End: tabs.at(-1),
    };
    const target = targets[event.key];
    if (!target) return;
    event.preventDefault();
    target.focus();
    target.click(); // automatic activation: focus follows selection
  }

  return (
    <button
      type="button"
      role="tab"
      id={tabId(baseId, value)}
      aria-selected={isSelected}
      aria-controls={panelId(baseId, value)}
      tabIndex={isSelected ? 0 : -1}
      disabled={disabled}
      data-value={value}
      onClick={() => select(value)}
      onKeyDown={onKeyDown}
    >
      {children}
    </button>
  );
}

function Panel({ value, children }: { value: string; children: ReactNode }) {
  const { baseId, selected } = useTabsContext("Panel");
  if (selected !== value) return null;
  return (
    <div role="tabpanel" id={panelId(baseId, value)} aria-labelledby={tabId(baseId, value)} tabIndex={0}>
      {children}
    </div>
  );
}

export const Tabs = Object.assign(TabsRoot, { List, Trigger, Panel });

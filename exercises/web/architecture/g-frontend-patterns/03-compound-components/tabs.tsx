"use client";
// Compound Tabs. See README.md.
import type { ComponentProps, ReactNode } from "react";

type TabsProps = { value?: string; defaultValue?: string; onValueChange?: (value: string) => void; children: ReactNode };

function TabsRoot(props: TabsProps) {
  return null;
}

function List(props: ComponentProps<"div">) {
  return null;
}

function Trigger(props: { value: string; disabled?: boolean; children: ReactNode }) {
  return null;
}

function Panel(props: { value: string; children: ReactNode }) {
  return null;
}

export const Tabs = Object.assign(TabsRoot, { List, Trigger, Panel });

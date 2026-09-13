"use client";
// Navigation components. See README.md.
import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";

export function NavLinks(props: { links: { href: string; label: string }[] }) {
  return null;
}

export function Breadcrumbs(props: { labels?: Record<string, string> }) {
  return null;
}

export function StatusFilter() {
  return null;
}

export function SaveAndOpen(props: { onSave: () => Promise<{ id: number }> }) {
  return null;
}

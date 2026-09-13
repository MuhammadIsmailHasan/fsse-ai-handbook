"use client";

import Link from "next/link";
import { usePathname, useRouter, useSearchParams } from "next/navigation";
import { useState } from "react";

export function isActive(pathname: string, href: string): boolean {
  if (href === "/") return pathname === "/";
  return pathname === href || pathname.startsWith(`${href}/`);
}

export function NavLinks({ links }: { links: { href: string; label: string }[] }) {
  const pathname = usePathname();
  return (
    <nav aria-label="Main">
      {links.map((link) => {
        const active = isActive(pathname, link.href);
        return (
          <Link key={link.href} href={link.href} aria-current={active ? "page" : undefined} className={active ? "font-semibold" : undefined}>
            {link.label}
          </Link>
        );
      })}
    </nav>
  );
}

const humanize = (segment: string) => segment.charAt(0).toUpperCase() + segment.slice(1).replaceAll("-", " ");

export function Breadcrumbs({ labels = {} }: { labels?: Record<string, string> }) {
  const pathname = usePathname();
  const segments = pathname.split("/").filter(Boolean);
  if (segments.length === 0) return null;

  const crumbs = segments.map((segment, index) => ({
    href: "/" + segments.slice(0, index + 1).join("/"),
    label: labels[segment] ?? humanize(segment),
  }));

  return (
    <nav aria-label="Breadcrumb">
      <ol>
        <li>
          <Link href="/">Home</Link>
        </li>
        {crumbs.map((crumb, index) => (
          <li key={crumb.href}>
            {index === crumbs.length - 1 ? <span aria-current="page">{crumb.label}</span> : <Link href={crumb.href}>{crumb.label}</Link>}
          </li>
        ))}
      </ol>
    </nav>
  );
}

const STATUS_OPTIONS = [
  ["", "All"],
  ["saved", "Saved"],
  ["applied", "Applied"],
  ["interview", "Interview"],
  ["offer", "Offer"],
  ["rejected", "Rejected"],
] as const;

export function StatusFilter() {
  const router = useRouter();
  const pathname = usePathname();
  const searchParams = useSearchParams();

  function handleChange(value: string) {
    const params = new URLSearchParams(searchParams.toString()); // copy: the hook's params are read-only
    if (value) params.set("status", value);
    else params.delete("status");
    params.delete("page"); // a new filter starts at page 1
    const query = params.toString();
    router.replace(query ? `${pathname}?${query}` : pathname, { scroll: false });
  }

  return (
    <>
      <label htmlFor="status-filter">Status</label>
      <select id="status-filter" value={searchParams.get("status") ?? ""} onChange={(event) => handleChange(event.target.value)}>
        {STATUS_OPTIONS.map(([value, label]) => (
          <option key={value} value={value}>
            {label}
          </option>
        ))}
      </select>
    </>
  );
}

export function SaveAndOpen({ onSave }: { onSave: () => Promise<{ id: number }> }) {
  const router = useRouter();
  const [saving, setSaving] = useState(false);
  const [failed, setFailed] = useState(false);

  async function handleClick() {
    setSaving(true);
    setFailed(false);
    try {
      const { id } = await onSave();
      router.push(`/applications/${id}`);
    } catch {
      setFailed(true);
      setSaving(false);
    }
  }

  return (
    <div>
      <button type="button" onClick={() => router.back()}>
        Back
      </button>
      <button type="button" disabled={saving} onClick={handleClick}>
        Save and open
      </button>
      {failed && <p role="alert">Couldn&apos;t save. Try again.</p>}
    </div>
  );
}

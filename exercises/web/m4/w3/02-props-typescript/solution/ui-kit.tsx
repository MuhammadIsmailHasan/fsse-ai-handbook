import { useId, type ComponentPropsWithoutRef, type ReactNode } from "react";

export type Status = "saved" | "applied" | "interview" | "offer" | "rejected";
export const STATUS_LABELS: Record<Status, string> = { saved: "Saved", applied: "Applied", interview: "Interview", offer: "Offer", rejected: "Rejected" };

export interface ButtonProps extends ComponentPropsWithoutRef<"button"> {
  variant?: "primary" | "secondary" | "danger";
  loading?: boolean;
}

export function Button({ variant = "primary", loading = false, type = "button", disabled, children, ...rest }: ButtonProps) {
  return (
    <button {...rest} type={type} data-variant={variant} disabled={disabled || loading} aria-busy={loading || undefined}>
      {loading ? "Loading…" : children}
    </button>
  );
}

export interface AvatarProps {
  name: string;
  src?: string;
  size?: number;
}

export function initials(name: string): string {
  return name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((word) => word[0]?.toUpperCase() ?? "")
    .join("");
}

export function Avatar({ name, src, size = 40 }: AvatarProps) {
  if (src) return <img src={src} alt={name} width={size} height={size} />;
  return (
    <span role="img" aria-label={name} style={{ width: size, height: size }}>
      {initials(name)}
    </span>
  );
}

export function StatusBadge({ status }: { status: Status }) {
  return <span data-status={status}>{STATUS_LABELS[status]}</span>;
}

export interface CardProps {
  title: string;
  actions?: ReactNode;
  children: ReactNode;
}

export function Card({ title, actions, children }: CardProps) {
  const titleId = useId();
  return (
    <section aria-labelledby={titleId}>
      <h2 id={titleId}>{title}</h2>
      {actions && <div>{actions}</div>}
      {children}
    </section>
  );
}

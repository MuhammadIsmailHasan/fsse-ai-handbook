import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

/** Join conditional classes (clsx) and let later Tailwind classes override earlier conflicting ones (tailwind-merge). */
export function cn(...inputs: ClassValue[]): string {
  return twMerge(clsx(inputs));
}

export type ButtonVariant = "primary" | "secondary" | "danger" | "ghost";
export type ButtonSize = "sm" | "md" | "lg";

const BASE =
  "inline-flex items-center justify-center rounded-lg font-semibold focus-visible:outline-2 focus-visible:outline-offset-2 disabled:pointer-events-none disabled:opacity-50";

export const BUTTON_VARIANTS = {
  primary: "bg-indigo-600 text-white hover:bg-indigo-500",
  secondary: "bg-white text-slate-900 ring-1 ring-slate-300 hover:bg-slate-50",
  danger: "bg-red-600 text-white hover:bg-red-500",
  ghost: "bg-transparent text-slate-700 hover:bg-slate-100",
} satisfies Record<ButtonVariant, string>;

export const BUTTON_SIZES = {
  sm: "px-2.5 py-1.5 text-sm",
  md: "px-4 py-2 text-sm",
  lg: "px-5 py-3 text-base",
} satisfies Record<ButtonSize, string>;

export interface ButtonClassOptions {
  variant?: ButtonVariant;
  size?: ButtonSize;
  fullWidth?: boolean;
  className?: string;
}

export function buttonClasses({ variant = "primary", size = "md", fullWidth = false, className }: ButtonClassOptions = {}): string {
  return cn(BASE, BUTTON_VARIANTS[variant], BUTTON_SIZES[size], fullWidth && "w-full", className);
}

export type Status = "saved" | "applied" | "interview" | "offer" | "rejected";

export const STATUS_BADGE = {
  saved: "bg-slate-100 text-slate-700",
  applied: "bg-blue-50 text-blue-700",
  interview: "bg-amber-50 text-amber-800",
  offer: "bg-green-50 text-green-700",
  rejected: "bg-red-50 text-red-700",
} satisfies Record<Status, string>;

export function badgeClasses(status: Status, className?: string): string {
  return cn("inline-flex items-center rounded-full px-2 py-0.5 text-xs font-medium", STATUS_BADGE[status], className);
}

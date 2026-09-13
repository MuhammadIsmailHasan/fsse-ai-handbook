import { cva, type VariantProps } from "class-variance-authority";
import type { ComponentProps } from "react";
import { cn } from "../../lib/utils";

export const badgeVariants = cva("inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium", {
  variants: {
    tone: {
      neutral: "bg-slate-100 text-slate-700",
      info: "bg-blue-100 text-blue-800",
      warning: "bg-amber-100 text-amber-800",
      success: "bg-green-100 text-green-800",
      danger: "bg-red-100 text-red-800",
    },
  },
  defaultVariants: { tone: "neutral" },
});

export function Badge({ tone, className, ...props }: ComponentProps<"span"> & VariantProps<typeof badgeVariants>) {
  return <span data-slot="badge" className={cn(badgeVariants({ tone }), className)} {...props} />;
}

type Status = "applied" | "interview" | "offer" | "rejected";

// Domain → design-system mapping lives in one place.
const STATUS_BADGE: Record<Status, { tone: NonNullable<VariantProps<typeof badgeVariants>["tone"]>; label: string }> = {
  applied: { tone: "info", label: "Applied" },
  interview: { tone: "warning", label: "Interview" },
  offer: { tone: "success", label: "Offer 🎉" },
  rejected: { tone: "danger", label: "Rejected" },
};

export function StatusBadge({ status }: { status: Status }) {
  const { tone, label } = STATUS_BADGE[status];
  return <Badge tone={tone}>{label}</Badge>;
}

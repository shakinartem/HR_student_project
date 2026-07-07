import { cn } from "@/lib/cn";

const toneClasses = {
  neutral: "border-white/10 bg-white/5 text-hub-text",
  accent: "border-hub-orange/40 bg-hub-orange/15 text-hub-orange",
  success: "border-emerald-500/30 bg-emerald-500/15 text-emerald-300",
  warning: "border-amber-500/30 bg-amber-500/15 text-amber-300",
  danger: "border-red-500/30 bg-red-500/15 text-red-300",
} as const;

export function StatusBadge({
  label,
  tone = "neutral",
}: {
  label: string;
  tone?: keyof typeof toneClasses;
}) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full border px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.16em]",
        toneClasses[tone],
      )}
    >
      {label}
    </span>
  );
}

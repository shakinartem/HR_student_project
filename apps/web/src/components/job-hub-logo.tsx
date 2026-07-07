import { cn } from "@/lib/cn";

export function JobHubLogo({ className, compact = false }: { className?: string; compact?: boolean }) {
  return (
    <div className={cn("inline-flex items-center font-bold uppercase tracking-[0.18em]", className)}>
      <span
        className={cn(
          "rounded-l-2xl bg-white px-3 py-2 text-hub-black",
          compact ? "text-[11px]" : "text-xs",
        )}
      >
        Джоб
      </span>
      <span
        className={cn(
          "rounded-r-2xl bg-hub-orange px-3 py-2 text-white",
          compact ? "text-[11px]" : "text-xs",
        )}
      >
        Хаб
      </span>
    </div>
  );
}

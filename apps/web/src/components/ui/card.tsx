import type { PropsWithChildren } from "react";

import { cn } from "@/lib/cn";

export function Card({ children, className }: PropsWithChildren<{ className?: string }>) {
  return (
    <div className={cn("rounded-[18px] border border-border bg-bg-card p-5 shadow-card", className)}>
      {children}
    </div>
  );
}

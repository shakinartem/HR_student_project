import type { PropsWithChildren } from "react";

import { cn } from "@/lib/cn";

export function Card({ children, className }: PropsWithChildren<{ className?: string }>) {
  return (
    <div className={cn("rounded-[28px] border border-white/70 bg-white/90 p-4 shadow-card backdrop-blur", className)}>
      {children}
    </div>
  );
}

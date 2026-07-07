import type { PropsWithChildren, ReactNode } from "react";

import { ChevronLeft } from "lucide-react";

import { JobHubLogo } from "@/components/job-hub-logo";
import { cn } from "@/lib/cn";

export function HrShell({
  title,
  subtitle,
  children,
  onBack,
  headerBadge,
  footer,
}: PropsWithChildren<{
  title: string;
  subtitle?: string;
  onBack?: (() => void) | null;
  headerBadge?: ReactNode;
  footer?: ReactNode;
}>) {
  return (
    <div className="mx-auto min-h-screen max-w-md px-4 pb-8 pt-4 text-hub-text">
      <header className="mb-5 rounded-[32px] border border-hub-border bg-hub-panel/95 p-4 shadow-card backdrop-blur">
        <div className="flex items-start justify-between gap-3">
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              {onBack ? (
                <button
                  className="inline-flex h-10 w-10 items-center justify-center rounded-2xl border border-hub-border bg-white/5 text-hub-text transition hover:bg-white/10"
                  onClick={onBack}
                  type="button"
                >
                  <ChevronLeft className="h-5 w-5" />
                </button>
              ) : null}
              <JobHubLogo compact />
            </div>
            <div>
              <h1 className="m-0 text-[28px] font-bold leading-tight">{title}</h1>
              {subtitle ? <p className="mt-2 text-sm text-hub-muted">{subtitle}</p> : null}
            </div>
          </div>
          {headerBadge}
        </div>
      </header>

      <main className="space-y-4">{children}</main>

      {footer ? <div className={cn("mt-6")}>{footer}</div> : null}
    </div>
  );
}

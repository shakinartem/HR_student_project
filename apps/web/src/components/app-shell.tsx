import type { PropsWithChildren, ReactNode } from "react";

import { BriefcaseBusiness } from "lucide-react";

export function AppShell({
  children,
  title,
  subtitle,
  headerRight,
}: PropsWithChildren<{
  title: string;
  subtitle?: string;
  headerRight?: ReactNode;
}>) {
  return (
    <div className="mx-auto min-h-screen max-w-md px-4 pb-8 pt-4 text-ink">
      <header className="mb-5 rounded-[28px] border border-white/70 bg-white/80 p-4 shadow-card backdrop-blur">
        <div className="flex items-start justify-between gap-3">
          <div className="space-y-2">
            <div className="inline-flex items-center gap-2 rounded-full bg-accentSoft px-3 py-1 text-xs font-semibold text-accent">
              <BriefcaseBusiness className="h-3.5 w-3.5" />
              Student Jobs
            </div>
            <div>
              <h1 className="m-0 text-2xl font-semibold">{title}</h1>
              {subtitle ? <p className="mt-1 text-sm text-slate-600">{subtitle}</p> : null}
            </div>
          </div>
          {headerRight}
        </div>
      </header>
      <main className="space-y-4">{children}</main>
    </div>
  );
}

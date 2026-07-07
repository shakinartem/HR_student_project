import { BriefcaseBusiness, CircleUserRound, CreditCard, Files } from "lucide-react";

import { cn } from "@/lib/cn";
import type { AppRoute } from "@/lib/routes";

const items: Array<{
  kind: AppRoute["kind"];
  label: string;
  icon: typeof BriefcaseBusiness;
}> = [
  { kind: "feed", label: "Лента", icon: BriefcaseBusiness },
  { kind: "applications", label: "Отклики", icon: Files },
  { kind: "balance", label: "Баланс", icon: CreditCard },
  { kind: "profile", label: "Профиль", icon: CircleUserRound },
];

export function BottomNav({
  currentRoute,
  onNavigate,
}: {
  currentRoute: AppRoute["kind"];
  onNavigate: (route: Extract<AppRoute, { kind: "feed" | "applications" | "balance" | "profile" }>) => void;
}) {
  return (
    <nav className="sticky bottom-4 z-10 mt-6 rounded-[28px] border border-white/70 bg-white/90 p-2 shadow-card backdrop-blur">
      <ul className="m-0 grid list-none grid-cols-4 gap-2 p-0">
        {items.map((item) => {
          const Icon = item.icon;
          const isActive = currentRoute === item.kind;
          return (
            <li key={item.kind}>
              <button
                className={cn(
                  "flex w-full flex-col items-center gap-1 rounded-2xl px-2 py-3 text-xs font-semibold transition-colors",
                  isActive ? "bg-accent text-white" : "text-slate-500 hover:bg-slate-50",
                )}
                onClick={() => onNavigate({ kind: item.kind })}
                type="button"
              >
                <Icon className="h-4 w-4" />
                <span>{item.label}</span>
              </button>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}

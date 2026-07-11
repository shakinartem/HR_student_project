import { BriefcaseBusiness, CircleUserRound, CreditCard, FileText } from "lucide-react";

import { cn } from "@/lib/cn";
import type { AppRoute } from "@/lib/routes";

const items: Array<{
  kind: AppRoute["kind"];
  label: string;
  icon: typeof BriefcaseBusiness;
}> = [
  { kind: "feed", label: "Jobs", icon: BriefcaseBusiness },
  { kind: "applications", label: "Responses", icon: FileText },
  { kind: "balance", label: "Wallet", icon: CreditCard },
  { kind: "profile", label: "Profile", icon: CircleUserRound },
];

export function BottomNav({
  currentRoute,
  onNavigate,
}: {
  currentRoute: AppRoute["kind"];
  onNavigate: (route: Extract<AppRoute, { kind: "feed" | "applications" | "balance" | "profile" }>) => void;
}) {
  return (
    <nav className="sticky bottom-6 z-10 mx-4 mt-6 rounded-xl border border-border bg-bg-secondary p-2 shadow-card">
      <ul className="m-0 grid list-none grid-cols-4 gap-2 p-0">
        {items.map((item) => {
          const Icon = item.icon;
          const isActive = currentRoute === item.kind;
          return (
            <li key={item.kind}>
              <button
                className={cn(
                  "flex w-full flex-col items-center gap-1 rounded-lg px-2 py-3 text-xs font-medium transition-all duration-200",
                  isActive ? "bg-accent text-white shadow-button" : "text-text-secondary hover:text-text-primary",
                )}
                onClick={() => onNavigate({ kind: item.kind })}
                type="button"
              >
                <Icon className="h-5 w-5" />
                <span>{item.label}</span>
              </button>
            </li>
          );
        })}
      </ul>
    </nav>
  );
}

import { BarChart3, Building2, CreditCard, MessageSquareWarning, ShieldCheck, Users, WalletCards } from "lucide-react";

import { Button } from "@/components/ui/button";
import { cn } from "@/lib/cn";
import type { AppRoute } from "@/lib/routes";

const items: Array<{
  kind:
    | "admin-dashboard"
    | "admin-users"
    | "admin-hr"
    | "admin-moderation"
    | "admin-complaints"
    | "admin-payments"
    | "admin-stats";
  label: string;
  icon: typeof ShieldCheck;
}> = [
  { kind: "admin-dashboard", label: "Dashboard", icon: ShieldCheck },
  { kind: "admin-users", label: "Users", icon: Users },
  { kind: "admin-hr", label: "HR access", icon: Building2 },
  { kind: "admin-moderation", label: "Moderation", icon: WalletCards },
  { kind: "admin-complaints", label: "Complaints", icon: MessageSquareWarning },
  { kind: "admin-payments", label: "Payments", icon: CreditCard },
  { kind: "admin-stats", label: "Stats", icon: BarChart3 },
];

export function AdminNav({
  currentRoute,
  onNavigate,
}: {
  currentRoute: AppRoute["kind"];
  onNavigate: (
    route: Extract<
      AppRoute,
      {
        kind:
          | "admin-dashboard"
          | "admin-users"
          | "admin-hr"
          | "admin-moderation"
          | "admin-complaints"
          | "admin-payments"
          | "admin-stats";
      }
    >,
  ) => void;
}) {
  return (
    <div className="overflow-x-auto pb-1">
      <div className="flex min-w-max gap-2">
        {items.map((item) => {
          const Icon = item.icon;
          const isActive = currentRoute === item.kind;
          return (
            <Button
              className={cn(
                "min-h-11 rounded-2xl px-4",
                isActive
                  ? "bg-hub-orange text-white hover:bg-hub-orange/90"
                  : "border border-hub-border bg-white/5 text-hub-text hover:bg-white/10",
              )}
              key={item.kind}
              onClick={() => onNavigate({ kind: item.kind })}
              type="button"
              variant="ghost"
            >
              <Icon className="mr-2 h-4 w-4" />
              {item.label}
            </Button>
          );
        })}
      </div>
    </div>
  );
}

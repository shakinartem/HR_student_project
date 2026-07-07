import { BarChart3, Building2, CreditCard, MessageSquareWarning, ShieldCheck, Users, WalletCards } from "lucide-react";

import { AdminNav } from "@/components/admin-nav";
import { HrShell } from "@/components/hr-shell";
import { StatusBadge } from "@/components/status-badge";
import { Card } from "@/components/ui/card";
import type { AppRoute } from "@/lib/routes";
import type { AdminStats, User } from "@/types/api";

const sections = [
  { kind: "admin-users", title: "Users", note: "Roles, block and mute controls.", icon: Users },
  { kind: "admin-hr", title: "HR access", note: "Approve and block HR profiles.", icon: Building2 },
  { kind: "admin-moderation", title: "Moderation", note: "Review manual queue vacancies.", icon: WalletCards },
  { kind: "admin-complaints", title: "Complaints", note: "Move complaints through MVP statuses.", icon: MessageSquareWarning },
  { kind: "admin-payments", title: "Payments", note: "Read-only payment ledger view.", icon: CreditCard },
  { kind: "admin-stats", title: "Stats", note: "Core marketplace counters.", icon: BarChart3 },
] as const;

function statItems(stats: AdminStats | null) {
  return [
    ["Total users", stats?.total_users ?? 0],
    ["Students", stats?.students ?? 0],
    ["HR users", stats?.hr_users ?? 0],
    ["Active vacancies", stats?.active_vacancies ?? 0],
    ["Payments", stats?.succeeded_payments ?? 0],
    ["Open complaints", stats?.open_complaints ?? 0],
  ] as const;
}

export function AdminDashboardScreen({
  currentUser,
  currentRoute,
  errorMessage,
  isLoading,
  onNavigate,
  stats,
}: {
  currentUser: User;
  currentRoute: AppRoute["kind"];
  errorMessage: string | null;
  isLoading: boolean;
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
  stats: AdminStats | null;
}) {
  return (
    <HrShell
      title="Admin dashboard"
      subtitle="Operational MVP tools for users, HR access, moderation, complaints, payments, and basic stats."
      headerBadge={<StatusBadge label={currentUser.role} tone="danger" />}
    >
      <AdminNav currentRoute={currentRoute} onNavigate={onNavigate} />

      {errorMessage ? (
        <Card className="border-red-500/30 bg-red-500/10 text-red-100">
          <p className="m-0 text-sm">{errorMessage}</p>
        </Card>
      ) : null}

      <div className="grid grid-cols-2 gap-3">
        {statItems(stats).map(([label, value]) => (
          <Card className="border-hub-border bg-hub-panel p-4 text-hub-text" key={label}>
            <p className="m-0 text-[11px] uppercase tracking-[0.16em] text-hub-muted">{label}</p>
            <p className="mb-0 mt-3 text-2xl font-bold">{isLoading ? "..." : value}</p>
          </Card>
        ))}
      </div>

      <section className="space-y-3">
        {sections.map((section) => {
          const Icon = section.icon;
          return (
            <button
              className="w-full rounded-[28px] border border-hub-border bg-hub-panel p-4 text-left text-hub-text transition hover:border-hub-orange/40"
              key={section.kind}
              onClick={() => onNavigate({ kind: section.kind })}
              type="button"
            >
              <div className="flex items-start gap-3">
                <div className="rounded-2xl bg-hub-orange/15 p-3 text-hub-orange">
                  <Icon className="h-5 w-5" />
                </div>
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <h2 className="m-0 text-base font-bold">{section.title}</h2>
                    <ShieldCheck className="h-4 w-4 text-hub-muted" />
                  </div>
                  <p className="m-0 text-sm text-hub-muted">{section.note}</p>
                </div>
              </div>
            </button>
          );
        })}
      </section>
    </HrShell>
  );
}

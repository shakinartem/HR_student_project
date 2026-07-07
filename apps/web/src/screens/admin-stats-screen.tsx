import { LoaderCircle } from "lucide-react";

import { AdminNav } from "@/components/admin-nav";
import { HrShell } from "@/components/hr-shell";
import { StatusBadge } from "@/components/status-badge";
import { Card } from "@/components/ui/card";
import type { AppRoute } from "@/lib/routes";
import type { AdminStats, User } from "@/types/api";

const statCards = [
  ["total_users", "Total users"],
  ["students", "Students"],
  ["hr_users", "HR users"],
  ["active_vacancies", "Active vacancies"],
  ["applications", "Applications"],
  ["succeeded_payments", "Succeeded payments"],
  ["open_complaints", "Open complaints"],
  ["manual_review_vacancies", "Manual review"],
] as const;

export function AdminStatsScreen({
  currentRoute,
  currentUser,
  errorMessage,
  isLoading,
  onNavigate,
  stats,
}: {
  currentRoute: AppRoute["kind"];
  currentUser: User;
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
    <HrShell title="Stats" subtitle="Simple MVP counters for operational visibility. No advanced analytics in this pass." headerBadge={<StatusBadge label={currentUser.role} tone="danger" />}>
      <AdminNav currentRoute={currentRoute} onNavigate={onNavigate} />

      {errorMessage ? (
        <Card className="border-red-500/30 bg-red-500/10 text-red-100">
          <p className="m-0 text-sm">{errorMessage}</p>
        </Card>
      ) : null}

      {isLoading ? (
        <Card className="flex items-center gap-3 border-hub-border bg-hub-panel text-hub-text">
          <LoaderCircle className="h-5 w-5 animate-spin text-hub-orange" />
          <p className="m-0 text-sm text-hub-muted">Loading stats...</p>
        </Card>
      ) : null}

      <div className="grid grid-cols-2 gap-3">
        {statCards.map(([key, label]) => (
          <Card className="border-hub-border bg-hub-panel p-4 text-hub-text" key={key}>
            <p className="m-0 text-[11px] uppercase tracking-[0.16em] text-hub-muted">{label}</p>
            <p className="mb-0 mt-3 text-2xl font-bold">{stats ? stats[key] : "0"}</p>
          </Card>
        ))}
      </div>
    </HrShell>
  );
}

import { CheckCircle2, LoaderCircle, OctagonX } from "lucide-react";

import { AdminNav } from "@/components/admin-nav";
import { HrShell } from "@/components/hr-shell";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { AppRoute } from "@/lib/routes";
import type { AdminModerationVacancy, User } from "@/types/api";

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "short",
  }).format(new Date(value));
}

export function AdminModerationScreen({
  currentRoute,
  currentUser,
  errorMessage,
  isLoading,
  isMutating,
  onApprove,
  onNavigate,
  onReject,
  vacancies,
}: {
  currentRoute: AppRoute["kind"];
  currentUser: User;
  errorMessage: string | null;
  isLoading: boolean;
  isMutating: boolean;
  onApprove: (vacancyId: string) => void;
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
  onReject: (vacancyId: string) => void;
  vacancies: AdminModerationVacancy[];
}) {
  return (
    <HrShell title="Moderation queue" subtitle="Process vacancies in manual review or moderation and keep decisions visible." headerBadge={<StatusBadge label={currentUser.role} tone="danger" />}>
      <AdminNav currentRoute={currentRoute} onNavigate={onNavigate} />

      {errorMessage ? (
        <Card className="border-red-500/30 bg-red-500/10 text-red-100">
          <p className="m-0 text-sm">{errorMessage}</p>
        </Card>
      ) : null}

      {isLoading ? (
        <Card className="flex items-center gap-3 border-hub-border bg-hub-panel text-hub-text">
          <LoaderCircle className="h-5 w-5 animate-spin text-hub-orange" />
          <p className="m-0 text-sm text-hub-muted">Loading moderation queue...</p>
        </Card>
      ) : null}

      {!isLoading && vacancies.length === 0 ? (
        <Card className="border-hub-border bg-hub-panel text-hub-text">
          <p className="m-0 text-sm text-hub-muted">No vacancies require manual moderation.</p>
        </Card>
      ) : null}

      {!isLoading ? (
        <section className="space-y-3">
          {vacancies.map((vacancy) => (
            <Card className="border-hub-border bg-hub-panel text-hub-text" key={vacancy.id}>
              <div className="flex items-start justify-between gap-3">
                <div className="space-y-2">
                  <h2 className="m-0 text-base font-bold">{vacancy.title}</h2>
                  <p className="m-0 text-sm text-hub-muted">
                    {vacancy.company_name ?? "No company"} | {vacancy.salary_text}
                  </p>
                  <p className="m-0 text-xs text-hub-muted">
                    {vacancy.category} | Added {formatDate(vacancy.created_at)}
                  </p>
                  {vacancy.moderation_reason ? (
                    <p className="m-0 text-xs text-amber-300">Last reason: {vacancy.moderation_reason}</p>
                  ) : null}
                </div>
                <StatusBadge label={vacancy.moderation_status} tone="warning" />
              </div>
              <div className="mt-4 grid grid-cols-2 gap-3">
                <Button disabled={isMutating} onClick={() => onApprove(vacancy.id)}>
                  <CheckCircle2 className="mr-2 h-4 w-4" />
                  Approve
                </Button>
                <Button disabled={isMutating} onClick={() => onReject(vacancy.id)} variant="secondary">
                  <OctagonX className="mr-2 h-4 w-4" />
                  Reject
                </Button>
              </div>
            </Card>
          ))}
        </section>
      ) : null}
    </HrShell>
  );
}

import { LoaderCircle, MessageSquareWarning } from "lucide-react";

import { AdminNav } from "@/components/admin-nav";
import { HrShell } from "@/components/hr-shell";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { AppRoute } from "@/lib/routes";
import type { AdminComplaint, User } from "@/types/api";

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function toneForStatus(status: string) {
  if (status === "resolved") {
    return "success" as const;
  }
  if (status === "rejected") {
    return "danger" as const;
  }
  if (status === "in_review") {
    return "warning" as const;
  }
  return "accent" as const;
}

export function AdminComplaintsScreen({
  complaints,
  currentRoute,
  currentUser,
  errorMessage,
  isLoading,
  isMutating,
  onNavigate,
  onUpdateStatus,
}: {
  complaints: AdminComplaint[];
  currentRoute: AppRoute["kind"];
  currentUser: User;
  errorMessage: string | null;
  isLoading: boolean;
  isMutating: boolean;
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
  onUpdateStatus: (complaintId: string, statusValue: string) => void;
}) {
  return (
    <HrShell title="Complaints" subtitle="Review complaint context, move it through status, and keep comments backend-driven." headerBadge={<StatusBadge label={currentUser.role} tone="danger" />}>
      <AdminNav currentRoute={currentRoute} onNavigate={onNavigate} />

      {errorMessage ? (
        <Card className="border-red-500/30 bg-red-500/10 text-red-100">
          <p className="m-0 text-sm">{errorMessage}</p>
        </Card>
      ) : null}

      {isLoading ? (
        <Card className="flex items-center gap-3 border-hub-border bg-hub-panel text-hub-text">
          <LoaderCircle className="h-5 w-5 animate-spin text-hub-orange" />
          <p className="m-0 text-sm text-hub-muted">Loading complaints...</p>
        </Card>
      ) : null}

      {!isLoading && complaints.length === 0 ? (
        <Card className="border-hub-border bg-hub-panel text-hub-text">
          <p className="m-0 text-sm text-hub-muted">No complaints found.</p>
        </Card>
      ) : null}

      {!isLoading ? (
        <section className="space-y-3">
          {complaints.map((complaint) => (
            <Card className="border-hub-border bg-hub-panel text-hub-text" key={complaint.id}>
              <div className="flex items-start justify-between gap-3">
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <MessageSquareWarning className="h-4 w-4 text-hub-orange" />
                    <h2 className="m-0 text-base font-bold">Complaint {complaint.id.slice(0, 8)}</h2>
                  </div>
                  <p className="m-0 text-sm text-hub-muted">{complaint.reason}</p>
                  <p className="m-0 text-xs text-hub-muted">
                    Reporter {complaint.reporter_user_id.slice(0, 8)} to target {complaint.target_user_id.slice(0, 8)}
                  </p>
                  <p className="m-0 text-xs text-hub-muted">
                    Vacancy {complaint.vacancy_id?.slice(0, 8) ?? "n/a"} | Application {complaint.application_id?.slice(0, 8) ?? "n/a"}
                  </p>
                  <p className="m-0 text-xs text-hub-muted">Updated {formatDate(complaint.updated_at)}</p>
                </div>
                <StatusBadge label={complaint.status} tone={toneForStatus(complaint.status)} />
              </div>
              <div className="mt-4 grid grid-cols-3 gap-2">
                <Button disabled={isMutating} onClick={() => onUpdateStatus(complaint.id, "in_review")} variant="secondary">
                  In review
                </Button>
                <Button disabled={isMutating} onClick={() => onUpdateStatus(complaint.id, "resolved")}>
                  Resolve
                </Button>
                <Button disabled={isMutating} onClick={() => onUpdateStatus(complaint.id, "rejected")} variant="secondary">
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

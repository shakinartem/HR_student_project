import { Building2, LoaderCircle, ShieldCheck } from "lucide-react";

import { AdminNav } from "@/components/admin-nav";
import { HrShell } from "@/components/hr-shell";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { AppRoute } from "@/lib/routes";
import type { AdminHRProfile, User } from "@/types/api";

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "short",
  }).format(new Date(value));
}

function toneForStatus(status: string) {
  if (status === "active") {
    return "success" as const;
  }
  if (status === "blocked") {
    return "danger" as const;
  }
  return "warning" as const;
}

export function AdminHrScreen({
  currentRoute,
  currentUser,
  errorMessage,
  isLoading,
  isMutating,
  onNavigate,
  onUpdateStatus,
  profiles,
}: {
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
  onUpdateStatus: (profileId: string, statusValue: string) => void;
  profiles: AdminHRProfile[];
}) {
  return (
    <HrShell title="HR access" subtitle="Approve pending HRs, block unsafe access, and keep company ownership visible." headerBadge={<StatusBadge label={currentUser.role} tone="danger" />}>
      <AdminNav currentRoute={currentRoute} onNavigate={onNavigate} />

      {errorMessage ? (
        <Card className="border-red-500/30 bg-red-500/10 text-red-100">
          <p className="m-0 text-sm">{errorMessage}</p>
        </Card>
      ) : null}

      {isLoading ? (
        <Card className="flex items-center gap-3 border-hub-border bg-hub-panel text-hub-text">
          <LoaderCircle className="h-5 w-5 animate-spin text-hub-orange" />
          <p className="m-0 text-sm text-hub-muted">Loading HR profiles...</p>
        </Card>
      ) : null}

      {!isLoading && profiles.length === 0 ? (
        <Card className="border-hub-border bg-hub-panel text-hub-text">
          <p className="m-0 text-sm text-hub-muted">No HR profiles in queue.</p>
        </Card>
      ) : null}

      {!isLoading ? (
        <section className="space-y-3">
          {profiles.map((profile) => (
            <Card className="border-hub-border bg-hub-panel text-hub-text" key={profile.id}>
              <div className="flex items-start justify-between gap-3">
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <Building2 className="h-4 w-4 text-hub-orange" />
                    <h2 className="m-0 text-base font-bold">{profile.company.name}</h2>
                  </div>
                  <p className="m-0 text-sm text-hub-muted">
                    {profile.user.first_name} {profile.user.last_name ?? ""} | @{profile.user.username ?? "no_username"}
                  </p>
                  <p className="m-0 text-xs text-hub-muted">
                    Position: {profile.position ?? "n/a"} | Added {formatDate(profile.created_at)}
                  </p>
                </div>
                <StatusBadge label={profile.verified_status} tone={toneForStatus(profile.verified_status)} />
              </div>
              <div className="mt-4 grid grid-cols-2 gap-3">
                {profile.verified_status !== "active" ? (
                  <Button disabled={isMutating} onClick={() => onUpdateStatus(profile.id, "active")}>
                    <ShieldCheck className="mr-2 h-4 w-4" />
                    Approve
                  </Button>
                ) : null}
                {profile.verified_status !== "blocked" ? (
                  <Button disabled={isMutating} onClick={() => onUpdateStatus(profile.id, "blocked")} variant="secondary">
                    Block
                  </Button>
                ) : null}
                {profile.verified_status === "blocked" ? (
                  <Button disabled={isMutating} onClick={() => onUpdateStatus(profile.id, "active")} variant="secondary">
                    Unblock
                  </Button>
                ) : null}
              </div>
            </Card>
          ))}
        </section>
      ) : null}
    </HrShell>
  );
}

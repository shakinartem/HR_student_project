import { CreditCard, LoaderCircle } from "lucide-react";

import { AdminNav } from "@/components/admin-nav";
import { HrShell } from "@/components/hr-shell";
import { StatusBadge } from "@/components/status-badge";
import { Card } from "@/components/ui/card";
import type { AppRoute } from "@/lib/routes";
import type { AdminPayment, User } from "@/types/api";

function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-GB", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function toneForPayment(status: string) {
  if (status === "succeeded") {
    return "success" as const;
  }
  if (status === "pending") {
    return "warning" as const;
  }
  return "neutral" as const;
}

export function AdminPaymentsScreen({
  currentRoute,
  currentUser,
  errorMessage,
  isLoading,
  onNavigate,
  payments,
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
  payments: AdminPayment[];
}) {
  return (
    <HrShell title="Payments" subtitle="Read-only payment timeline for MVP operations. No provider secrets or reconciliation tools here." headerBadge={<StatusBadge label={currentUser.role} tone="danger" />}>
      <AdminNav currentRoute={currentRoute} onNavigate={onNavigate} />

      {errorMessage ? (
        <Card className="border-red-500/30 bg-red-500/10 text-red-100">
          <p className="m-0 text-sm">{errorMessage}</p>
        </Card>
      ) : null}

      {isLoading ? (
        <Card className="flex items-center gap-3 border-hub-border bg-hub-panel text-hub-text">
          <LoaderCircle className="h-5 w-5 animate-spin text-hub-orange" />
          <p className="m-0 text-sm text-hub-muted">Loading payments...</p>
        </Card>
      ) : null}

      {!isLoading && payments.length === 0 ? (
        <Card className="border-hub-border bg-hub-panel text-hub-text">
          <p className="m-0 text-sm text-hub-muted">No payments found.</p>
        </Card>
      ) : null}

      {!isLoading ? (
        <section className="space-y-3">
          {payments.map((payment) => (
            <Card className="border-hub-border bg-hub-panel text-hub-text" key={payment.id}>
              <div className="flex items-start justify-between gap-3">
                <div className="space-y-2">
                  <div className="flex items-center gap-2">
                    <CreditCard className="h-4 w-4 text-hub-orange" />
                    <h2 className="m-0 text-base font-bold">
                      {payment.amount} {payment.currency}
                    </h2>
                  </div>
                  <p className="m-0 text-sm text-hub-muted">{payment.purpose}</p>
                  <p className="m-0 text-xs text-hub-muted">
                    User {payment.user.first_name} {payment.user.last_name ?? ""} | @{payment.user.username ?? "no_username"}
                  </p>
                  <p className="m-0 text-xs text-hub-muted">
                    Payment {payment.id.slice(0, 8)} | {formatDate(payment.created_at)}
                  </p>
                  <p className="m-0 text-xs text-hub-muted">
                    Entity {payment.entity_type ?? "n/a"}:{payment.entity_id ?? "n/a"}
                  </p>
                </div>
                <StatusBadge label={payment.status} tone={toneForPayment(payment.status)} />
              </div>
            </Card>
          ))}
        </section>
      ) : null}
    </HrShell>
  );
}

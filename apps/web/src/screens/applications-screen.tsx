import { CheckCircle2, Clock3, LoaderCircle, XCircle } from "lucide-react";

import { BottomNav } from "@/components/bottom-nav";
import { Card } from "@/components/ui/card";
import type { AppRoute } from "@/lib/routes";
import type { StudentApplication } from "@/types/api";

function formatCurrency(amount: string, currency = "RUB") {
  const value = Number(amount);
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(Number.isFinite(value) ? value : 0);
}

function formatDate(value: string | null) {
  if (!value) {
    return "—";
  }
  return new Intl.DateTimeFormat("en-US", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function statusBadge(status: string) {
  if (status === "accepted") {
    return { label: "Accepted", icon: CheckCircle2, color: "text-green-400" };
  }
  if (status === "rejected") {
    return { label: "Rejected", icon: XCircle, color: "text-red-400" };
  }
  return { label: "Pending", icon: Clock3, color: "text-amber-400" };
}

export function ApplicationsScreen({
  applications,
  isLoading,
  isError,
  errorMessage,
  onNavigate,
}: {
  applications: StudentApplication[];
  isLoading: boolean;
  isError: boolean;
  errorMessage: string | null;
  onNavigate: (route: Extract<AppRoute, { kind: "feed" | "applications" | "balance" | "profile" }>) => void;
}) {
  return (
    <div className="min-h-screen bg-bg-primary">
      <header className="sticky top-0 z-10 bg-bg-secondary/80 backdrop-blur-sm">
        <div className="flex items-center justify-between px-4 py-4">
          <div>
            <h1 className="text-2xl font-bold text-text-primary">Responses</h1>
            <p className="text-sm text-text-secondary mt-1">Track your job applications</p>
          </div>
        </div>
      </header>

      <main className="px-4 py-4 pb-24 space-y-4">
        {isLoading ? (
          <Card className="flex items-center gap-3">
            <LoaderCircle className="h-5 w-5 animate-spin text-accent" />
            <p className="m-0 text-sm text-text-secondary">Loading applications...</p>
          </Card>
        ) : null}

        {isError && errorMessage ? (
          <Card className="border-red-500/20 bg-red-500/10">
            <p className="m-0 text-sm text-red-400">{errorMessage}</p>
          </Card>
        ) : null}

        {!isLoading && !isError && applications.length === 0 ? (
          <Card className="flex flex-col items-center gap-4 py-12">
            <div className="w-16 h-16 rounded-full bg-bg-secondary flex items-center justify-center border border-border">
              <Clock3 className="h-8 w-8 text-text-secondary" />
            </div>
            <div className="text-center">
              <h2 className="mb-1 mt-0 text-lg font-semibold text-text-primary">No applications yet</h2>
              <p className="m-0 text-sm text-text-secondary max-w-xs">
                Apply to jobs from the feed. Your applications will appear here.
              </p>
            </div>
          </Card>
        ) : null}

        {!isLoading && !isError
          ? applications.map((application) => {
              const badge = statusBadge(application.status);
              const Icon = badge.icon;
              return (
                <Card key={application.id} className="space-y-2">
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h3 className="m-0 mb-1 text-base font-semibold text-text-primary">{application.vacancy_title}</h3>
                      <p className="m-0 text-sm text-text-secondary">{application.company_name ?? "Company pending"}</p>
                    </div>
                    <div className="flex items-center gap-1.5">
                      <Icon className={`h-4 w-4 ${badge.color}`} />
                      <span className={`text-xs font-medium ${badge.color}`}>{badge.label}</span>
                    </div>
                  </div>
                  <div className="border-t border-border pt-2 space-y-1">
                    <p className="m-0 text-xs text-text-secondary">
                      Applied: {formatDate(application.created_at)}
                    </p>
                    {application.student_comment ? (
                      <p className="m-0 text-xs text-text-secondary">"{application.student_comment}"</p>
                    ) : null}
                  </div>
                </Card>
              );
            })
          : null}

        <BottomNav currentRoute="applications" onNavigate={onNavigate} />
      </main>
    </div>
  );
}
import { LoaderCircle, RefreshCcw } from "lucide-react";

import { BottomNav } from "@/components/bottom-nav";
import { PreviewCounter } from "@/components/preview-counter";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { VacancyCard } from "@/components/vacancy-card";
import type { AppRoute } from "@/lib/routes";
import type { VacancyListItem } from "@/types/api";

export function FeedScreen({
  vacancies,
  isLoading,
  isError,
  onRetry,
  onOpenVacancy,
  previewCount,
  previewLimit,
  showPreviewCounter,
  actionError,
  authLabel,
  successMessage,
  successActionLabel,
  onSuccessAction,
  onNavigate,
}: {
  vacancies: VacancyListItem[];
  isLoading: boolean;
  isError: boolean;
  onRetry: () => void;
  onOpenVacancy: (vacancyId: string) => void;
  previewCount: number;
  previewLimit: number;
  showPreviewCounter: boolean;
  actionError: string | null;
  authLabel: string;
  successMessage?: string | null;
  successActionLabel?: string;
  onSuccessAction?: (() => void) | null;
  onNavigate: (route: Extract<AppRoute, { kind: "feed" | "applications" | "balance" | "profile" }>) => void;
}) {
  return (
    <div className="min-h-screen bg-bg-primary">
      <header className="sticky top-0 z-10 bg-bg-secondary/80 backdrop-blur-sm">
        <div className="flex items-center justify-between px-4 py-4">
          <div>
            <h1 className="text-2xl font-bold text-text-primary">Jobs</h1>
            <p className="text-sm text-text-secondary mt-1">Secure student jobs & internships</p>
          </div>
          <span className="rounded-full bg-bg-card px-4 py-2 text-xs font-medium text-accent border border-border">
            {authLabel}
          </span>
        </div>
      </header>

      <main className="px-4 py-4 pb-24 space-y-4">
        {showPreviewCounter ? (
          <Card className="border-accent/20 bg-accent/10">
            <PreviewCounter viewedCount={previewCount} maxCount={previewLimit} />
          </Card>
        ) : null}

        {successMessage ? (
          <Card className="border-accent/20 bg-accent/10">
            <p className="m-0 text-sm text-accent">{successMessage}</p>
            {onSuccessAction && successActionLabel ? (
              <Button className="mt-3 w-full" onClick={onSuccessAction} variant="secondary">
                {successActionLabel}
              </Button>
            ) : null}
          </Card>
        ) : null}

        {actionError ? (
          <Card>
            <p className="m-0 text-sm text-red-400">{actionError}</p>
          </Card>
        ) : null}

        {isLoading ? (
          <Card className="flex items-center gap-3">
            <LoaderCircle className="h-5 w-5 animate-spin text-accent" />
            <p className="m-0 text-sm text-text-secondary">Loading job opportunities...</p>
          </Card>
        ) : null}

        {!isLoading && isError ? (
          <Card className="space-y-3">
            <div>
              <h2 className="mb-1 mt-0 text-lg font-semibold text-text-primary">Unable to load feed</h2>
              <p className="m-0 text-sm text-text-secondary">Check connection and try again.</p>
            </div>
            <Button className="w-full" variant="secondary" onClick={onRetry}>
              <RefreshCcw className="mr-2 h-4 w-4" />
              Refresh
            </Button>
          </Card>
        ) : null}

        {!isLoading && !isError && vacancies.length === 0 ? (
          <Card>
            <h2 className="mb-1 mt-0 text-lg font-semibold text-text-primary">No vacancies yet</h2>
            <p className="m-0 text-sm text-text-secondary">
              No active jobs right now. Check back later for new opportunities.
            </p>
          </Card>
        ) : null}

        {!isLoading && !isError
          ? vacancies.map((vacancy) => (
              <VacancyCard key={vacancy.id} vacancy={vacancy} onOpen={() => onOpenVacancy(vacancy.id)} />
            ))
          : null}
      </main>

      <BottomNav currentRoute="feed" onNavigate={onNavigate} />
    </div>
  );
}

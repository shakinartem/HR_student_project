import { LoaderCircle, RefreshCcw } from "lucide-react";

import { AppShell } from "@/components/app-shell";
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
    <AppShell
      title="Лента вакансий"
      subtitle="Безопасные подработки и стажировки для студентов."
      headerRight={<span className="rounded-full bg-white px-3 py-2 text-xs font-medium text-slate-600">{authLabel}</span>}
    >
      {showPreviewCounter ? <PreviewCounter viewedCount={previewCount} maxCount={previewLimit} /> : null}

      {successMessage ? (
        <Card className="border-emerald-100 bg-emerald-50">
          <p className="m-0 text-sm text-emerald-700">{successMessage}</p>
          {onSuccessAction && successActionLabel ? (
            <Button className="mt-3 w-full" onClick={onSuccessAction} variant="secondary">
              {successActionLabel}
            </Button>
          ) : null}
        </Card>
      ) : null}

      {actionError ? (
        <Card className="border-red-100 bg-red-50">
          <p className="m-0 text-sm text-red-700">{actionError}</p>
        </Card>
      ) : null}

      {isLoading ? (
        <Card className="flex items-center gap-3">
          <LoaderCircle className="h-5 w-5 animate-spin text-accent" />
          <p className="m-0 text-sm text-slate-600">Загружаем актуальные вакансии…</p>
        </Card>
      ) : null}

      {!isLoading && isError ? (
        <Card className="space-y-3">
          <div>
            <h2 className="mb-1 mt-0 text-lg font-semibold">Не удалось загрузить ленту</h2>
            <p className="m-0 text-sm text-slate-600">Проверь соединение и попробуй ещё раз.</p>
          </div>
          <Button className="w-full" variant="secondary" onClick={onRetry}>
            <RefreshCcw className="mr-2 h-4 w-4" />
            Обновить
          </Button>
        </Card>
      ) : null}

      {!isLoading && !isError && vacancies.length === 0 ? (
        <Card>
          <h2 className="mb-1 mt-0 text-lg font-semibold">Пока пусто</h2>
          <p className="m-0 text-sm text-slate-600">
            Сейчас нет активных вакансий. Загляни позже, мы показываем только опубликованные предложения.
          </p>
        </Card>
      ) : null}

      {!isLoading && !isError
        ? vacancies.map((vacancy) => (
            <VacancyCard key={vacancy.id} vacancy={vacancy} onOpen={() => onOpenVacancy(vacancy.id)} />
          ))
        : null}

      <BottomNav currentRoute="feed" onNavigate={onNavigate} />
    </AppShell>
  );
}

import { ArrowLeft, BadgeRussianRuble, Building2, Clock3, MapPin } from "lucide-react";

import { AppShell } from "@/components/app-shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { VacancyDetail } from "@/types/api";

function VacancySection({ title, text }: { title: string; text: string | null | undefined }) {
  if (!text) {
    return null;
  }

  return (
    <Card>
      <h2 className="mb-2 mt-0 text-base font-semibold">{title}</h2>
      <p className="m-0 whitespace-pre-line text-sm text-slate-700">{text}</p>
    </Card>
  );
}

export function VacancyDetailScreen({
  vacancy,
  onBack,
  onApply,
  isLoading,
  errorMessage,
  applyError,
  isApplying,
}: {
  vacancy: VacancyDetail | null;
  onBack: () => void;
  onApply: () => void;
  isLoading: boolean;
  errorMessage: string | null;
  applyError: string | null;
  isApplying: boolean;
}) {
  return (
    <AppShell
      title={vacancy?.title ?? "Вакансия"}
      subtitle={vacancy?.company_name ?? "Подробности предложения"}
      headerRight={
        <button className="rounded-2xl border-0 bg-white px-3 py-2 text-slate-600" onClick={onBack} type="button">
          <ArrowLeft className="h-5 w-5" />
        </button>
      }
    >
      {isLoading ? (
        <Card>
          <p className="m-0 text-sm text-slate-600">Загружаем детали вакансии…</p>
        </Card>
      ) : null}

      {!isLoading && errorMessage ? (
        <Card className="space-y-3">
          <div>
            <h2 className="mb-1 mt-0 text-lg font-semibold">Не удалось открыть вакансию</h2>
            <p className="m-0 text-sm text-slate-600">{errorMessage}</p>
          </div>
          <Button className="w-full" variant="secondary" onClick={onBack}>
            Вернуться в ленту
          </Button>
        </Card>
      ) : null}

      {!isLoading && vacancy ? (
        <>
          <Card className="space-y-4">
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-sm text-slate-600">
                <Building2 className="h-4 w-4 text-accent" />
                <span>{vacancy.company_name ?? "Компания уточняется"}</span>
              </div>
              <div className="grid grid-cols-1 gap-2 text-sm text-slate-700">
                <div className="flex items-center gap-2 rounded-2xl bg-slate-50 px-3 py-2">
                  <BadgeRussianRuble className="h-4 w-4 text-accent" />
                  <span>{vacancy.salary_text}</span>
                </div>
                <div className="flex items-center gap-2 rounded-2xl bg-slate-50 px-3 py-2">
                  <Clock3 className="h-4 w-4 text-accent" />
                  <span>{vacancy.schedule}</span>
                </div>
                <div className="flex items-center gap-2 rounded-2xl bg-slate-50 px-3 py-2">
                  <MapPin className="h-4 w-4 text-accent" />
                  <span>{vacancy.district ?? "Район уточняется"}</span>
                </div>
              </div>
            </div>

            <Button className="w-full" disabled={isApplying} size="lg" onClick={onApply}>
              {isApplying ? "Отправляем…" : "Откликнуться"}
            </Button>
            {applyError ? <p className="m-0 text-sm text-red-600">{applyError}</p> : null}
            <p className="m-0 text-xs text-slate-500">Контакты работодателя скрыты и не отображаются в Mini App.</p>
          </Card>

          <Card className="border-blue-100 bg-blue-50">
            <p className="m-0 text-sm text-slate-700">
              После отклика HR увидит только учебный профиль и комментарий. Контакты студента откроются HR только после принятия отклика.
            </p>
          </Card>

          <VacancySection title="Описание" text={vacancy.description} />
          <VacancySection title="Требования" text={vacancy.requirements} />
          <VacancySection title="Условия" text={vacancy.conditions} />
        </>
      ) : null}
    </AppShell>
  );
}

import { ArrowLeft, BadgeRussianRuble, Building2, Clock3, MapPin } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { VacancyDetail } from "@/types/api";

function VacancySection({ title, text }: { title: string; text: string | null | undefined }) {
  if (!text) {
    return null;
  }

  return (
    <Card>
      <h2 className="mb-2 mt-0 text-base font-semibold text-text-primary">{title}</h2>
      <p className="m-0 whitespace-pre-line text-sm text-text-secondary">{text}</p>
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
    <div className="min-h-screen bg-bg-primary">
      <header className="sticky top-0 z-10 bg-bg-secondary/80 backdrop-blur-sm">
        <div className="flex items-center justify-between px-4 py-4">
          <div>
            <h1 className="text-2xl font-bold text-text-primary">{vacancy?.title ?? "Вакансия"}</h1>
            <p className="text-sm text-text-secondary mt-1">{vacancy?.company_name ?? "Детали"}</p>
          </div>
          <button className="rounded-full border-0 bg-bg-card p-3 text-text-secondary hover:text-text-primary" onClick={onBack} type="button">
            <ArrowLeft className="h-5 w-5" />
          </button>
        </div>
      </header>

      <main className="px-4 py-4 space-y-4">
        {isLoading ? (
          <Card>
            <p className="m-0 text-sm text-text-secondary">Загружаем вакансию...</p>
          </Card>
        ) : null}

        {!isLoading && errorMessage ? (
          <Card className="space-y-3">
            <div>
              <h2 className="mb-1 mt-0 text-lg font-semibold text-text-primary">Не удалось загрузить вакансию</h2>
              <p className="m-0 text-sm text-text-secondary">{errorMessage}</p>
            </div>
            <Button className="w-full" variant="secondary" onClick={onBack}>
              Назад к ленте
            </Button>
          </Card>
        ) : null}

        {!isLoading && vacancy ? (
          <>
            <Card className="space-y-4">
              <div className="space-y-3">
                <div className="flex items-center gap-2 text-sm text-text-secondary">
                  <Building2 className="h-4 w-4 text-accent" />
                  <span>{vacancy.company_name ?? "Компания уточняется"}</span>
                </div>
                <div className="grid grid-cols-1 gap-2 text-sm">
                  <div className="flex items-center gap-2 rounded-xl bg-bg-primary px-3 py-2">
                    <BadgeRussianRuble className="h-4 w-4 text-accent" />
                    <span className="text-text-primary">{vacancy.salary_text}</span>
                  </div>
                  <div className="flex items-center gap-2 rounded-xl bg-bg-primary px-3 py-2">
                    <Clock3 className="h-4 w-4 text-accent" />
                    <span className="text-text-secondary">{vacancy.schedule}</span>
                  </div>
                  <div className="flex items-center gap-2 rounded-xl bg-bg-primary px-3 py-2">
                    <MapPin className="h-4 w-4 text-accent" />
                    <span className="text-text-secondary">{vacancy.district ?? "Район уточняется"}</span>
                  </div>
                </div>
              </div>

              <Button className="w-full" disabled={isApplying} size="lg" onClick={onApply}>
                {isApplying ? "Отправляем..." : "Откликнуться"}
              </Button>
              {applyError ? <p className="m-0 text-sm text-red-400">{applyError}</p> : null}
              <p className="m-0 text-xs text-text-secondary text-center">
                Контакты работодателя скрыты
              </p>
            </Card>

            <Card className="border-accent/20 bg-accent/10">
              <p className="m-0 text-sm text-text-primary">
                После отклика HR увидит только ваш академический профиль. Контакты раскрываются только после принятия.
              </p>
            </Card>

            <VacancySection title="Описание" text={vacancy.description} />
            <VacancySection title="Обязанности" text={vacancy.responsibilities} />
            <VacancySection title="Требования" text={vacancy.requirements} />
            <VacancySection title="Условия" text={vacancy.conditions} />
          </>
        ) : null}
      </main>
    </div>
  );
}
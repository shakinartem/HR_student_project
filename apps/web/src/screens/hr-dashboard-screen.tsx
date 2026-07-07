import { BriefcaseBusiness, CircleAlert, FilePlus2, LoaderCircle, Sparkles, UserRoundSearch } from "lucide-react";

import { HrShell } from "@/components/hr-shell";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { HRApplication, HRVacancy, User } from "@/types/api";

function formatDate(value: string | null) {
  if (!value) {
    return "Без даты";
  }

  return new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    month: "short",
  }).format(new Date(value));
}

export function HrDashboardScreen({
  currentUser,
  vacancies,
  applications,
  isLoading,
  errorMessage,
  onCreateVacancy,
  onOpenVacancy,
  onOpenApplication,
}: {
  currentUser: User;
  vacancies: HRVacancy[];
  applications: HRApplication[];
  isLoading: boolean;
  errorMessage: string | null;
  onCreateVacancy: () => void;
  onOpenVacancy: (vacancyId: string) => void;
  onOpenApplication: (applicationId: string) => void;
}) {
  const activeVacancies = vacancies.filter((item) => item.status === "active").length;
  const paymentQueue = vacancies.filter((item) => item.payment_required).length;
  const freshApplications = applications.filter((item) => item.status === "pending").length;

  return (
    <HrShell
      title="HR dashboard"
      subtitle="Управляй публикацией вакансий и быстро принимай решения по откликам."
      headerBadge={<StatusBadge label={currentUser.role} tone="accent" />}
      footer={
        <Button className="w-full" onClick={onCreateVacancy} size="lg">
          <FilePlus2 className="mr-2 h-4 w-4" />
          Создать вакансию
        </Button>
      }
    >
      <div className="grid grid-cols-3 gap-3">
        <Card className="border-hub-border bg-hub-panel p-3 text-hub-text">
          <p className="m-0 text-[11px] uppercase tracking-[0.16em] text-hub-muted">Активные</p>
          <p className="mb-0 mt-3 text-2xl font-bold">{activeVacancies}</p>
        </Card>
        <Card className="border-hub-border bg-hub-panel p-3 text-hub-text">
          <p className="m-0 text-[11px] uppercase tracking-[0.16em] text-hub-muted">Оплата</p>
          <p className="mb-0 mt-3 text-2xl font-bold">{paymentQueue}</p>
        </Card>
        <Card className="border-hub-border bg-hub-panel p-3 text-hub-text">
          <p className="m-0 text-[11px] uppercase tracking-[0.16em] text-hub-muted">Новые</p>
          <p className="mb-0 mt-3 text-2xl font-bold">{freshApplications}</p>
        </Card>
      </div>

      {errorMessage ? (
        <Card className="border-red-500/20 bg-red-500/10 text-red-100">
          <p className="m-0 text-sm">{errorMessage}</p>
        </Card>
      ) : null}

      {isLoading ? (
        <Card className="flex items-center gap-3 border-hub-border bg-hub-panel text-hub-text">
          <LoaderCircle className="h-5 w-5 animate-spin text-hub-orange" />
          <p className="m-0 text-sm text-hub-muted">Собираем статусы вакансий и откликов…</p>
        </Card>
      ) : null}

      {!isLoading ? (
        <Card className="border-hub-border bg-hub-panel text-hub-text">
          <div className="flex items-start justify-between gap-3">
            <div>
              <p className="m-0 text-[11px] uppercase tracking-[0.16em] text-hub-muted">Фокус дня</p>
              <h2 className="mb-0 mt-2 text-lg font-bold">Не теряй кандидатов, которые уже готовы к созвону</h2>
            </div>
            <Sparkles className="h-5 w-5 text-hub-orange" />
          </div>
          <p className="mb-0 mt-3 text-sm text-hub-muted">
            Сначала доведи вакансии до публикации, затем обработай отклики без задержек. Контакты студентов откроются только
            после принятия отклика на backend.
          </p>
        </Card>
      ) : null}

      {!isLoading ? (
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="m-0 text-base font-bold text-hub-text">Мои вакансии</h2>
            <span className="text-xs text-hub-muted">{vacancies.length} шт.</span>
          </div>
          {vacancies.length === 0 ? (
            <Card className="border-hub-border bg-hub-panel text-hub-text">
              <p className="m-0 text-sm text-hub-muted">Пока нет вакансий. Начни с первой публикации в Джоб Хаб.</p>
            </Card>
          ) : (
            vacancies.map((vacancy) => (
              <button
                className="w-full rounded-[28px] border border-hub-border bg-hub-panel p-4 text-left text-hub-text transition hover:border-hub-orange/40"
                key={vacancy.id}
                onClick={() => onOpenVacancy(vacancy.id)}
                type="button"
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <h3 className="m-0 text-base font-bold">{vacancy.title}</h3>
                    <p className="mb-0 mt-2 text-sm text-hub-muted">
                      {vacancy.salary_text} • {vacancy.schedule}
                    </p>
                  </div>
                  <StatusBadge
                    label={vacancy.payment_required ? "нужна оплата" : vacancy.status}
                    tone={vacancy.payment_required ? "warning" : vacancy.status === "active" ? "success" : "neutral"}
                  />
                </div>
                <div className="mt-4 flex items-center justify-between text-xs text-hub-muted">
                  <span>{vacancy.category}</span>
                  <span>{formatDate(vacancy.published_at)}</span>
                </div>
              </button>
            ))
          )}
        </section>
      ) : null}

      {!isLoading ? (
        <section className="space-y-3">
          <div className="flex items-center justify-between">
            <h2 className="m-0 text-base font-bold text-hub-text">Отклики</h2>
            <span className="text-xs text-hub-muted">{applications.length} шт.</span>
          </div>
          {applications.length === 0 ? (
            <Card className="border-hub-border bg-hub-panel text-hub-text">
              <p className="m-0 text-sm text-hub-muted">Когда студенты откликнутся, здесь появятся карточки для быстрого разбора.</p>
            </Card>
          ) : (
            applications.map((application) => (
              <button
                className="w-full rounded-[28px] border border-hub-border bg-hub-panel p-4 text-left text-hub-text transition hover:border-hub-orange/40"
                key={application.id}
                onClick={() => onOpenApplication(application.id)}
                type="button"
              >
                <div className="flex items-start justify-between gap-3">
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <UserRoundSearch className="h-4 w-4 text-hub-orange" />
                      <span className="text-sm font-semibold">{application.student.first_name ?? "Кандидат"}</span>
                    </div>
                    <p className="m-0 text-sm text-hub-muted">{application.vacancy_title ?? "Без названия вакансии"}</p>
                  </div>
                  <StatusBadge
                    label={application.contacts ? "контакты открыты" : application.status}
                    tone={application.contacts ? "success" : application.status === "pending" ? "accent" : "neutral"}
                  />
                </div>
                <div className="mt-4 flex items-center justify-between text-xs text-hub-muted">
                  <span>{application.student.university ?? "Профиль без вуза"}</span>
                  <span>{formatDate(application.created_at)}</span>
                </div>
              </button>
            ))
          )}
        </section>
      ) : null}

      {!isLoading && (paymentQueue > 0 || freshApplications > 0) ? (
        <Card className="border-hub-border bg-hub-panel text-hub-text">
          <div className="flex items-start gap-3">
            <CircleAlert className="mt-0.5 h-5 w-5 text-hub-orange" />
            <div className="space-y-2">
              <h2 className="m-0 text-base font-bold">Нужны действия</h2>
              <ul className="m-0 space-y-1 pl-4 text-sm text-hub-muted">
                {paymentQueue > 0 ? <li>Оплати публикацию для {paymentQueue} вакансий.</li> : null}
                {freshApplications > 0 ? <li>Разбери {freshApplications} новых откликов, чтобы не потерять кандидатов.</li> : null}
              </ul>
            </div>
          </div>
        </Card>
      ) : null}
    </HrShell>
  );
}

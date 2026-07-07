import { BriefcaseBusiness, LoaderCircle } from "lucide-react";

import { AppShell } from "@/components/app-shell";
import { BottomNav } from "@/components/bottom-nav";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { AppRoute } from "@/lib/routes";
import type { StudentApplication, User } from "@/types/api";

function formatDate(value: string | null) {
  if (!value) {
    return "Дата не указана";
  }
  return new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

const statusLabels: Record<string, string> = {
  sent: "Отправлен",
  viewed: "Просмотрен",
  accepted: "HR заинтересован",
  rejected: "Отклонён",
};

export function ApplicationsScreen({
  currentUser,
  applications,
  isLoading,
  errorMessage,
  canAuthenticateInTelegram,
  onNavigate,
  onOpenFeed,
}: {
  currentUser: User | null;
  applications: StudentApplication[];
  isLoading: boolean;
  errorMessage: string | null;
  canAuthenticateInTelegram: boolean;
  onNavigate: (route: Extract<AppRoute, { kind: "feed" | "applications" | "balance" | "profile" }>) => void;
  onOpenFeed: () => void;
}) {
  const isGuest = !currentUser;

  return (
    <AppShell
      title="Мои отклики"
      subtitle="Следи за статусом откликов. Контакты HR здесь никогда не показываются."
      headerRight={
        <span className="rounded-full bg-white px-3 py-2 text-xs font-medium text-slate-600">
          {currentUser?.role === "student" ? "Студент" : "Гость"}
        </span>
      }
    >
      {isGuest ? (
        <>
          <Card className="space-y-3">
            <div>
              <h2 className="mb-1 mt-0 text-lg font-semibold">Сначала нужен вход</h2>
              <p className="m-0 text-sm text-slate-600">Список откликов доступен только авторизованному студенту.</p>
            </div>
            <p className="m-0 text-xs text-slate-500">
              {canAuthenticateInTelegram
                ? "Открой Mini App заново внутри Telegram, чтобы мы повторили авторизацию."
                : "Открой приложение внутри Telegram, чтобы получить доступ к откликам."}
            </p>
          </Card>
          <BottomNav currentRoute="applications" onNavigate={onNavigate} />
        </>
      ) : (
        <>
          {isLoading ? (
            <Card className="flex items-center gap-3">
              <LoaderCircle className="h-5 w-5 animate-spin text-accent" />
              <p className="m-0 text-sm text-slate-600">Загружаем отклики…</p>
            </Card>
          ) : null}

          {!isLoading && errorMessage ? (
            <Card className="border-red-100 bg-red-50">
              <p className="m-0 text-sm text-red-700">{errorMessage}</p>
            </Card>
          ) : null}

          {!isLoading && !errorMessage && applications.length === 0 ? (
            <Card className="space-y-3">
              <div className="rounded-2xl bg-accentSoft p-3 text-accent">
                <BriefcaseBusiness className="h-5 w-5" />
              </div>
              <div>
                <h2 className="mb-1 mt-0 text-lg font-semibold">Пока нет откликов</h2>
                <p className="m-0 text-sm text-slate-600">Когда откликнешься на вакансию, статус появится здесь.</p>
              </div>
              <Button className="w-full" onClick={onOpenFeed} variant="secondary">
                Перейти к вакансиям
              </Button>
            </Card>
          ) : null}

          {!isLoading && !errorMessage
            ? applications.map((application) => (
                <Card key={application.id}>
                  <div className="flex items-start justify-between gap-3">
                    <div>
                      <h2 className="mb-1 mt-0 text-lg font-semibold">{application.vacancy_title ?? "Вакансия"}</h2>
                      <p className="m-0 text-sm text-slate-600">{application.company_name ?? "Компания"}</p>
                    </div>
                    <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
                      {statusLabels[application.status] ?? application.status}
                    </span>
                  </div>
                  <p className="mb-0 mt-3 text-xs text-slate-500">Создан {formatDate(application.created_at)}</p>
                </Card>
              ))
            : null}

          <BottomNav currentRoute="applications" onNavigate={onNavigate} />
        </>
      )}
    </AppShell>
  );
}

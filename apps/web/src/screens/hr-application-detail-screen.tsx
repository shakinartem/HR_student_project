import { Check, LoaderCircle, X } from "lucide-react";

import { HrShell } from "@/components/hr-shell";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { HRApplication } from "@/types/api";

function infoRow(label: string, value: string | null | number | undefined) {
  if (value === null || value === undefined || value === "") {
    return null;
  }

  return (
    <div className="flex items-start justify-between gap-3 border-t border-white/10 py-3 first:border-t-0 first:pt-0">
      <span className="text-sm text-hub-muted">{label}</span>
      <span className="text-right text-sm font-medium text-hub-text">{String(value)}</span>
    </div>
  );
}

export function HrApplicationDetailScreen({
  application,
  isLoading,
  errorMessage,
  actionMessage,
  actionError,
  isAccepting,
  isRejecting,
  onBack,
  onAccept,
  onReject,
}: {
  application: HRApplication | null;
  isLoading: boolean;
  errorMessage: string | null;
  actionMessage: string | null;
  actionError: string | null;
  isAccepting: boolean;
  isRejecting: boolean;
  onBack: () => void;
  onAccept: () => void;
  onReject: () => void;
}) {
  const hasContacts = Boolean(
    application?.contacts && (application.contacts.phone || application.contacts.email || application.contacts.telegram_username),
  );

  return (
    <HrShell
      title={hasContacts ? "Контакты открыты" : "Отклик кандидата"}
      subtitle={
        hasContacts
          ? "Контакты отображаются только потому, что backend уже подтвердил принятие отклика."
          : "До принятия отклика показываем только безопасные данные профиля, без контактных полей."
      }
      onBack={onBack}
      footer={
        application && !hasContacts && application.status === "pending" ? (
          <div className="space-y-3">
            <Button className="w-full" disabled={isAccepting || isRejecting} onClick={onAccept} size="lg">
              {isAccepting ? <LoaderCircle className="mr-2 h-4 w-4 animate-spin" /> : <Check className="mr-2 h-4 w-4" />}
              Принять отклик
            </Button>
            <Button className="w-full" disabled={isAccepting || isRejecting} onClick={onReject} size="lg" variant="secondary">
              {isRejecting ? <LoaderCircle className="mr-2 h-4 w-4 animate-spin" /> : <X className="mr-2 h-4 w-4" />}
              Отклонить
            </Button>
          </div>
        ) : null
      }
    >
      {isLoading ? (
        <Card className="flex items-center gap-3 border-hub-border bg-hub-panel text-hub-text">
          <LoaderCircle className="h-5 w-5 animate-spin text-hub-orange" />
          <p className="m-0 text-sm text-hub-muted">Загружаем отклик…</p>
        </Card>
      ) : null}

      {errorMessage ? (
        <Card className="border-red-500/20 bg-red-500/10 text-red-100">
          <p className="m-0 text-sm">{errorMessage}</p>
        </Card>
      ) : null}

      {actionMessage ? (
        <Card className="border-emerald-500/20 bg-emerald-500/10 text-emerald-100">
          <p className="m-0 text-sm">{actionMessage}</p>
        </Card>
      ) : null}

      {actionError ? (
        <Card className="border-red-500/20 bg-red-500/10 text-red-100">
          <p className="m-0 text-sm">{actionError}</p>
        </Card>
      ) : null}

      {application ? (
        <>
          <Card className="space-y-4 border-hub-border bg-hub-panel text-hub-text">
            <div className="flex items-start justify-between gap-3">
              <div>
                <p className="m-0 text-sm text-hub-muted">Вакансия</p>
                <h2 className="mb-0 mt-2 text-lg font-bold">{application.vacancy_title ?? "Без названия"}</h2>
              </div>
              <StatusBadge label={hasContacts ? "принят" : application.status} tone={hasContacts ? "success" : "accent"} />
            </div>
            <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
              <p className="m-0 text-xs uppercase tracking-[0.16em] text-hub-muted">Правило доступа</p>
              <p className="mb-0 mt-2 text-sm text-hub-text">
                {hasContacts
                  ? "Контакты возвращены API после принятия отклика."
                  : "Контакты не запрашиваются и не рисуются, пока backend их не откроет."}
              </p>
            </div>
          </Card>

          <Card className="border-hub-border bg-hub-panel text-hub-text">
            <h2 className="mt-0 text-base font-bold">Профиль кандидата</h2>
            {infoRow("Имя", application.student.first_name)}
            {infoRow("Вуз", application.student.university)}
            {infoRow("Курс", application.student.course)}
            {infoRow("Специальность", application.student.speciality)}
            {infoRow("Предпочтительный график", application.student.preferred_schedule?.join(", "))}
            {infoRow("Опыт", application.student.experience_text)}
            {infoRow("Комментарий", application.student.student_comment)}
          </Card>

          {hasContacts ? (
            <Card className="border-hub-border bg-hub-panel text-hub-text">
              <h2 className="mt-0 text-base font-bold">Контакты студента</h2>
              {infoRow("Телефон", application.contacts?.phone)}
              {infoRow("Email", application.contacts?.email)}
              {infoRow("Telegram", application.contacts?.telegram_username)}
            </Card>
          ) : null}
        </>
      ) : null}
    </HrShell>
  );
}

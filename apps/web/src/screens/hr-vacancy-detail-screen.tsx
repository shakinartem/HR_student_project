import { CheckCircle2, CircleDollarSign, LoaderCircle, ShieldCheck } from "lucide-react";

import { HrShell } from "@/components/hr-shell";
import { StatusBadge } from "@/components/status-badge";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { HRVacancy } from "@/types/api";

function statusTone(status: string) {
  if (status === "active" || status === "approved") {
    return "success" as const;
  }
  if (status === "manual_review" || status === "pending") {
    return "warning" as const;
  }
  if (status === "rejected") {
    return "danger" as const;
  }
  return "neutral" as const;
}

function infoRow(label: string, value: string | null | undefined) {
  if (!value) {
    return null;
  }

  return (
    <div className="flex items-start justify-between gap-3 border-t border-white/10 py-3 first:border-t-0 first:pt-0">
      <span className="text-sm text-hub-muted">{label}</span>
      <span className="text-right text-sm font-medium text-hub-text">{value}</span>
    </div>
  );
}

export function HrVacancyDetailScreen({
  vacancy,
  isLoading,
  errorMessage,
  actionMessage,
  actionError,
  pendingPaymentId,
  canMockConfirm,
  isCreatingPayment,
  isConfirmingPayment,
  onBack,
  onCreatePayment,
  onConfirmPayment,
}: {
  vacancy: HRVacancy | null;
  isLoading: boolean;
  errorMessage: string | null;
  actionMessage: string | null;
  actionError: string | null;
  pendingPaymentId: string | null;
  canMockConfirm: boolean;
  isCreatingPayment: boolean;
  isConfirmingPayment: boolean;
  onBack: () => void;
  onCreatePayment: () => void;
  onConfirmPayment: () => void;
}) {
  const showContacts =
    vacancy &&
    (vacancy.hidden_contacts.contact_name ||
      vacancy.hidden_contacts.contact_phone ||
      vacancy.hidden_contacts.contact_email ||
      vacancy.hidden_contacts.contact_telegram);

  return (
    <HrShell
      title={vacancy?.title ?? "Вакансия"}
      subtitle="Публикация, оплата и модерация читаются отдельно, без скрытых предположений на фронтенде."
      onBack={onBack}
      footer={
        pendingPaymentId && canMockConfirm ? (
          <Button className="w-full" disabled={isConfirmingPayment} onClick={onConfirmPayment} size="lg">
            {isConfirmingPayment ? <LoaderCircle className="mr-2 h-4 w-4 animate-spin" /> : <CheckCircle2 className="mr-2 h-4 w-4" />}
            Подтвердить mock payment
          </Button>
        ) : vacancy?.payment_required ? (
          <Button className="w-full" disabled={isCreatingPayment || isLoading} onClick={onCreatePayment} size="lg">
            {isCreatingPayment ? <LoaderCircle className="mr-2 h-4 w-4 animate-spin" /> : <CircleDollarSign className="mr-2 h-4 w-4" />}
            Оплатить публикацию
          </Button>
        ) : null
      }
    >
      {isLoading ? (
        <Card className="flex items-center gap-3 border-hub-border bg-hub-panel text-hub-text">
          <LoaderCircle className="h-5 w-5 animate-spin text-hub-orange" />
          <p className="m-0 text-sm text-hub-muted">Загружаем состояние публикации…</p>
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

      {vacancy ? (
        <>
          <div className="grid grid-cols-1 gap-3">
            <Card className="space-y-4 border-hub-border bg-hub-panel text-hub-text">
              <div className="flex flex-wrap gap-2">
                <StatusBadge label={vacancy.status} tone={statusTone(vacancy.status)} />
                <StatusBadge label={vacancy.moderation_status} tone={statusTone(vacancy.moderation_status)} />
                <StatusBadge label={vacancy.payment_required ? "ожидает оплату" : "оплата подтверждена"} tone={vacancy.payment_required ? "warning" : "success"} />
              </div>
              <div>
                <p className="m-0 text-sm text-hub-muted">{vacancy.category}</p>
                <p className="mb-0 mt-2 text-lg font-bold">{vacancy.salary_text}</p>
              </div>
              <p className="m-0 text-sm text-hub-muted">
                {vacancy.schedule} {vacancy.district ? `• ${vacancy.district}` : ""} {vacancy.format ? `• ${vacancy.format}` : ""}
              </p>
            </Card>

            <Card className="space-y-4 border-hub-border bg-hub-panel text-hub-text">
              <div className="flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-hub-orange" />
                <h2 className="m-0 text-base font-bold">Статусы публикации</h2>
              </div>
              <div className="space-y-3">
                <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
                  <p className="m-0 text-xs uppercase tracking-[0.16em] text-hub-muted">Оплата</p>
                  <p className="mb-0 mt-2 text-sm font-medium text-hub-text">
                    {vacancy.payment_required ? "Вакансия еще не оплачена и не отправлена в публикацию." : "Оплата за публикацию подтверждена."}
                  </p>
                </div>
                <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
                  <p className="m-0 text-xs uppercase tracking-[0.16em] text-hub-muted">Модерация</p>
                  <p className="mb-0 mt-2 text-sm font-medium text-hub-text">
                    {vacancy.moderation_status === "approved"
                      ? "Вакансия одобрена и может быть показана студентам."
                      : vacancy.moderation_status === "manual_review"
                        ? "Нужна ручная проверка перед публикацией."
                        : vacancy.moderation_status === "rejected"
                          ? "Публикация отклонена правилами безопасности."
                          : "Статус модерации ожидает решения backend."}
                  </p>
                </div>
                <div className="rounded-3xl border border-white/10 bg-white/5 p-4">
                  <p className="m-0 text-xs uppercase tracking-[0.16em] text-hub-muted">Публикация</p>
                  <p className="mb-0 mt-2 text-sm font-medium text-hub-text">
                    {vacancy.status === "active"
                      ? "Вакансия уже доступна в ленте."
                      : vacancy.status === "rejected"
                        ? "Вакансия не показывается студентам."
                        : "Вакансия еще не опубликована."}
                  </p>
                </div>
              </div>
            </Card>
          </div>

          <Card className="border-hub-border bg-hub-panel text-hub-text">
            <h2 className="mt-0 text-base font-bold">Детали вакансии</h2>
            {infoRow("Адрес", vacancy.address)}
            {infoRow("Описание", vacancy.description)}
            {infoRow("Обязанности", vacancy.responsibilities)}
            {infoRow("Требования", vacancy.requirements)}
            {infoRow("Условия", vacancy.conditions)}
          </Card>

          {showContacts ? (
            <Card className="border-hub-border bg-hub-panel text-hub-text">
              <h2 className="mt-0 text-base font-bold">Контакты компании</h2>
              {infoRow("Контакт", vacancy.hidden_contacts.contact_name)}
              {infoRow("Телефон", vacancy.hidden_contacts.contact_phone)}
              {infoRow("Email", vacancy.hidden_contacts.contact_email)}
              {infoRow("Telegram", vacancy.hidden_contacts.contact_telegram)}
            </Card>
          ) : null}
        </>
      ) : null}
    </HrShell>
  );
}

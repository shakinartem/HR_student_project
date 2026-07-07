import { CheckCircle2, Clock3, LoaderCircle, Wallet } from "lucide-react";

import { AppShell } from "@/components/app-shell";
import { BottomNav } from "@/components/bottom-nav";
import { FormField, InfoRow } from "@/components/form-field";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import type { AppRoute } from "@/lib/routes";
import type { Payment, StudentBalanceResponse, StudentSubscription, User } from "@/types/api";

function formatCurrency(amount: string, currency = "RUB") {
  const value = Number(amount);
  return new Intl.NumberFormat("ru-RU", {
    style: "currency",
    currency,
    maximumFractionDigits: 2,
  }).format(Number.isFinite(value) ? value : 0);
}

function formatDate(value: string | null) {
  if (!value) {
    return "—";
  }
  return new Intl.DateTimeFormat("ru-RU", {
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
  }).format(new Date(value));
}

function subscriptionLabel(subscription: StudentSubscription | null) {
  if (!subscription || subscription.status !== "active") {
    return "Не активен";
  }
  return `Активен до ${formatDate(subscription.expires_at)}`;
}

export function BalanceScreen({
  currentUser,
  balance,
  subscription,
  payments,
  isLoading,
  errorMessage,
  topUpAmount,
  pendingPaymentId,
  paymentError,
  paymentSuccess,
  isCreatingPayment,
  isConfirmingPayment,
  canAuthenticateInTelegram,
  canMockConfirm,
  onTopUpAmountChange,
  onQuickAmountPick,
  onCreatePayment,
  onConfirmPayment,
  onNavigate,
}: {
  currentUser: User | null;
  balance: StudentBalanceResponse | null;
  subscription: StudentSubscription | null;
  payments: Payment[];
  isLoading: boolean;
  errorMessage: string | null;
  topUpAmount: string;
  pendingPaymentId: string | null;
  paymentError: string | null;
  paymentSuccess: string | null;
  isCreatingPayment: boolean;
  isConfirmingPayment: boolean;
  canAuthenticateInTelegram: boolean;
  canMockConfirm: boolean;
  onTopUpAmountChange: (value: string) => void;
  onQuickAmountPick: (value: number) => void;
  onCreatePayment: () => void;
  onConfirmPayment: () => void;
  onNavigate: (route: Extract<AppRoute, { kind: "feed" | "applications" | "balance" | "profile" }>) => void;
}) {
  const isGuest = !currentUser;

  return (
    <AppShell
      title="Баланс"
      subtitle="Пополняй внутренний баланс и активируй доступ к откликам."
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
              <h2 className="mb-1 mt-0 text-lg font-semibold">Баланс доступен после входа</h2>
              <p className="m-0 text-sm text-slate-600">
                В гостевом режиме можно смотреть вакансии, но пополнение и активация доступа недоступны.
              </p>
            </div>
            <p className="m-0 text-xs text-slate-500">
              {canAuthenticateInTelegram
                ? "Открой Mini App заново внутри Telegram, и мы попробуем авторизовать тебя автоматически."
                : "Открой приложение внутри Telegram, чтобы пополнить баланс и активировать доступ."}
            </p>
          </Card>
          <BottomNav currentRoute="balance" onNavigate={onNavigate} />
        </>
      ) : (
        <>
          {isLoading ? (
            <Card className="flex items-center gap-3">
              <LoaderCircle className="h-5 w-5 animate-spin text-accent" />
              <p className="m-0 text-sm text-slate-600">Загружаем баланс и подписку…</p>
            </Card>
          ) : null}

          {!isLoading && errorMessage ? (
            <Card className="border-red-100 bg-red-50">
              <p className="m-0 text-sm text-red-700">{errorMessage}</p>
            </Card>
          ) : null}

          {!isLoading && !errorMessage ? (
            <>
              <Card className="bg-gradient-to-br from-blue-600 to-cyan-500 text-white">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="m-0 text-sm text-blue-50">Текущий баланс</p>
                    <p className="mb-0 mt-2 text-3xl font-semibold">
                      {formatCurrency(balance?.balance ?? "0", balance?.currency ?? "RUB")}
                    </p>
                  </div>
                  <div className="rounded-2xl bg-white/20 p-3">
                    <Wallet className="h-6 w-6" />
                  </div>
                </div>
              </Card>

              <Card>
                <div className="mb-3 flex items-start justify-between gap-3">
                  <div>
                    <h2 className="mb-1 mt-0 text-lg font-semibold">Статус доступа</h2>
                    <p className="m-0 text-sm text-slate-600">Подписка активируется после подтвержденного платежа.</p>
                  </div>
                  {subscription?.status === "active" ? (
                    <CheckCircle2 className="h-5 w-5 text-emerald-600" />
                  ) : (
                    <Clock3 className="h-5 w-5 text-amber-600" />
                  )}
                </div>
                <InfoRow label="Статус" value={subscriptionLabel(subscription)} />
                <InfoRow label="Начало" value={formatDate(subscription?.starts_at ?? null)} />
                <InfoRow label="Окончание" value={formatDate(subscription?.expires_at ?? null)} />
              </Card>

              <Card className="space-y-4">
                <div>
                  <h2 className="mb-1 mt-0 text-lg font-semibold">Пополнить баланс</h2>
                  <p className="m-0 text-sm text-slate-600">
                    Первое пополнение должно покрывать месячный тариф. Если тариф недоступен из API, используем 350 ₽ по умолчанию.
                  </p>
                </div>

                <div className="flex flex-wrap gap-2">
                  {[350, 700, 1050].map((value) => (
                    <button
                      className="rounded-full bg-slate-100 px-3 py-2 text-xs font-semibold text-slate-700"
                      key={value}
                      onClick={() => onQuickAmountPick(value)}
                      type="button"
                    >
                      {value} ₽
                    </button>
                  ))}
                </div>

                <FormField label="Сумма пополнения">
                  <Input
                    inputMode="decimal"
                    onChange={(event) => onTopUpAmountChange(event.target.value)}
                    placeholder="350"
                    value={topUpAmount}
                  />
                </FormField>

                <Button className="w-full" onClick={onCreatePayment} size="lg">
                  {isCreatingPayment ? <LoaderCircle className="mr-2 h-4 w-4 animate-spin" /> : null}
                  Создать платёж
                </Button>
              </Card>

              {pendingPaymentId ? (
                <Card className="space-y-3">
                  <div>
                    <h2 className="mb-1 mt-0 text-lg font-semibold">Платёж создан</h2>
                    <p className="m-0 text-sm text-slate-600">
                      Платёж ожидает подтверждения на бэкенде. В локальном или тестовом режиме можно завершить его вручную.
                    </p>
                  </div>
                  <p className="m-0 text-xs text-slate-500">ID платежа: {pendingPaymentId}</p>
                  {canMockConfirm ? (
                    <Button className="w-full" onClick={onConfirmPayment} variant="secondary">
                      {isConfirmingPayment ? <LoaderCircle className="mr-2 h-4 w-4 animate-spin" /> : null}
                      Mock confirm
                    </Button>
                  ) : null}
                </Card>
              ) : null}

              {paymentError ? (
                <Card className="border-red-100 bg-red-50">
                  <p className="m-0 text-sm text-red-700">{paymentError}</p>
                </Card>
              ) : null}

              {paymentSuccess ? (
                <Card className="border-emerald-100 bg-emerald-50">
                  <p className="m-0 text-sm text-emerald-700">{paymentSuccess}</p>
                </Card>
              ) : null}

              <Card className="space-y-3">
                <div>
                  <h2 className="mb-1 mt-0 text-lg font-semibold">История баланса</h2>
                  <p className="m-0 text-sm text-slate-600">Все списания и пополнения берутся из бухгалтерского леджера.</p>
                </div>
                {balance?.transactions.length ? (
                  balance.transactions.map((transaction) => (
                    <div className="rounded-2xl bg-slate-50 px-4 py-3" key={transaction.id}>
                      <div className="flex items-center justify-between gap-3">
                        <span className="text-sm font-semibold text-slate-800">{transaction.reason}</span>
                        <span className={transaction.amount.startsWith("-") ? "text-sm font-semibold text-red-600" : "text-sm font-semibold text-emerald-600"}>
                          {formatCurrency(transaction.amount, balance.currency)}
                        </span>
                      </div>
                      <p className="mb-0 mt-1 text-xs text-slate-500">{formatDate(transaction.created_at)}</p>
                    </div>
                  ))
                ) : (
                  <p className="m-0 text-sm text-slate-500">Пока нет операций.</p>
                )}
              </Card>

              <Card className="space-y-3">
                <div>
                  <h2 className="mb-1 mt-0 text-lg font-semibold">История платежей</h2>
                  <p className="m-0 text-sm text-slate-600">Здесь видны созданные и подтвержденные платежи.</p>
                </div>
                {payments.length ? (
                  payments.map((payment) => (
                    <div className="rounded-2xl bg-slate-50 px-4 py-3" key={payment.id}>
                      <div className="flex items-center justify-between gap-3">
                        <span className="text-sm font-semibold text-slate-800">{formatCurrency(payment.amount, payment.currency)}</span>
                        <span className="text-xs font-semibold uppercase tracking-wide text-slate-500">{payment.status}</span>
                      </div>
                      <p className="mb-0 mt-1 text-xs text-slate-500">{formatDate(payment.created_at)}</p>
                    </div>
                  ))
                ) : (
                  <p className="m-0 text-sm text-slate-500">Платежей ещё не было.</p>
                )}
              </Card>
            </>
          ) : null}

          <BottomNav currentRoute="balance" onNavigate={onNavigate} />
        </>
      )}
    </AppShell>
  );
}

import { CheckCircle2, Clock3, LoaderCircle, Wallet } from "lucide-react";

import { BottomNav } from "@/components/bottom-nav";
import { FormField, InfoRow } from "@/components/form-field";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import type { AppRoute } from "@/lib/routes";
import type { Payment, StudentBalanceResponse, StudentSubscription, User } from "@/types/api";

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

function subscriptionLabel(subscription: StudentSubscription | null) {
  if (!subscription || subscription.status !== "active") {
    return "Not active";
  }
  return `Active until ${formatDate(subscription.expires_at)}`;
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
    <div className="min-h-screen bg-bg-primary">
      <header className="sticky top-0 z-10 bg-bg-secondary/80 backdrop-blur-sm">
        <div className="flex items-center justify-between px-4 py-4">
          <div>
            <h1 className="text-2xl font-bold text-text-primary">Wallet</h1>
            <p className="text-sm text-text-secondary mt-1">Top up balance and activate access to apply</p>
          </div>
          <span className="rounded-full bg-bg-card px-4 py-2 text-xs font-medium text-accent border border-border">
            {currentUser?.role === "student" ? "Student" : "Guest"}
          </span>
        </div>
      </header>

      <main className="px-4 py-4 pb-24 space-y-4">
        {isGuest ? (
          <Card className="flex flex-col items-center gap-4 py-8">
            <div className="w-16 h-16 rounded-full bg-bg-secondary flex items-center justify-center border border-border">
              <Wallet className="h-8 w-8 text-text-secondary" />
            </div>
            <div className="text-center">
              <h2 className="mb-1 mt-0 text-lg font-semibold text-text-primary">Login required</h2>
              <p className="m-0 text-sm text-text-secondary max-w-xs">
                {canAuthenticateInTelegram
                  ? "Restart Mini App in Telegram for automatic authentication"
                  : "Telegram authentication required to top up balance and activate access"}
              </p>
            </div>
          </Card>
        ) : (
          <>
            {isLoading ? (
              <Card className="flex items-center gap-3">
                <LoaderCircle className="h-5 w-5 animate-spin text-accent" />
                <p className="m-0 text-sm text-text-secondary">Loading balance...</p>
              </Card>
            ) : null}

            {!isLoading && errorMessage ? (
              <Card className="border-red-500/20 bg-red-500/10">
                <p className="m-0 text-sm text-red-400">{errorMessage}</p>
              </Card>
            ) : null}

            {!isLoading && !errorMessage ? (
              <>
                <Card className="bg-gradient-to-br from-accent/20 to-orange-500/10">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <p className="m-0 text-sm text-accent/80">Current Balance</p>
                      <p className="mb-0 mt-2 text-3xl font-bold text-text-primary">
                        {formatCurrency(balance?.balance ?? "0", balance?.currency ?? "RUB")}
                      </p>
                    </div>
                    <div className="rounded-full bg-accent/20 p-3">
                      <Wallet className="h-6 w-6 text-accent" />
                    </div>
                  </div>
                </Card>

                <Card>
                  <div className="mb-3 flex items-start justify-between gap-3">
                    <div>
                      <h2 className="mb-1 mt-0 text-lg font-semibold text-text-primary">Access Status</h2>
                      <p className="m-0 text-sm text-text-secondary">Subscription activates after confirmed payment</p>
                    </div>
                    {subscription?.status === "active" ? (
                      <CheckCircle2 className="h-5 w-5 text-green-400" />
                    ) : (
                      <Clock3 className="h-5 w-5 text-amber-400" />
                    )}
                  </div>
                  <InfoRow label="Status" value={subscriptionLabel(subscription)} />
                  <InfoRow label="Start" value={formatDate(subscription?.starts_at ?? null)} />
                  <InfoRow label="Expires" value={formatDate(subscription?.expires_at ?? null)} />
                </Card>

                <Card className="space-y-4">
                  <div>
                    <h2 className="mb-1 mt-0 text-lg font-semibold text-text-primary">Top Up Balance</h2>
                    <p className="m-0 text-sm text-text-secondary">
                      First top-up must cover monthly tariff (350 RUB by default)
                    </p>
                  </div>

                  <div className="flex flex-wrap gap-2">
                    {[350, 700, 1050].map((value) => (
                      <button
                        className="rounded-full bg-bg-primary px-3 py-2 text-xs font-medium text-text-secondary border border-border hover:text-text-primary"
                        key={value}
                        onClick={() => onQuickAmountPick(value)}
                        type="button"
                      >
                        {value} ₽
                      </button>
                    ))}
                  </div>

                  <FormField label="Amount">
                    <Input
                      inputMode="decimal"
                      onChange={(event) => onTopUpAmountChange(event.target.value)}
                      placeholder="350"
                      value={topUpAmount}
                      className="bg-bg-primary border-border"
                    />
                  </FormField>

                  <Button className="w-full" onClick={onCreatePayment} size="lg">
                    {isCreatingPayment ? <LoaderCircle className="mr-2 h-4 w-4 animate-spin" /> : null}
                    Create Payment
                  </Button>
                </Card>

                {pendingPaymentId ? (
                  <Card className="space-y-3">
                    <div>
                      <h2 className="mb-1 mt-0 text-lg font-semibold text-text-primary">Payment Created</h2>
                      <p className="m-0 text-sm text-text-secondary">
                        Payment awaiting confirmation. In local/test mode, confirm manually.
                      </p>
                    </div>
                    <p className="m-0 text-xs text-text-secondary">Payment ID: {pendingPaymentId}</p>
                    {canMockConfirm ? (
                      <Button className="w-full" onClick={onConfirmPayment} variant="secondary">
                        {isConfirmingPayment ? <LoaderCircle className="mr-2 h-4 w-4 animate-spin" /> : null}
                        Mock Confirm
                      </Button>
                    ) : null}
                  </Card>
                ) : null}

                {paymentError ? (
                  <Card className="border-red-500/20 bg-red-500/10">
                    <p className="m-0 text-sm text-red-400">{paymentError}</p>
                  </Card>
                ) : null}

                {paymentSuccess ? (
                  <Card className="border-accent/20 bg-accent/10">
                    <p className="m-0 text-sm text-accent">{paymentSuccess}</p>
                  </Card>
                ) : null}

                <Card className="space-y-3">
                  <div>
                    <h2 className="mb-1 mt-0 text-lg font-semibold text-text-primary">Balance History</h2>
                    <p className="m-0 text-sm text-text-secondary">All transactions from ledger</p>
                  </div>
                  {balance?.transactions.length ? (
                    balance.transactions.map((transaction) => (
                      <div className="rounded-xl bg-bg-primary px-4 py-3" key={transaction.id}>
                        <div className="flex items-center justify-between gap-3">
                          <span className="text-sm font-medium text-text-primary">{transaction.reason}</span>
                          <span className={transaction.amount.startsWith("-") ? "text-sm font-medium text-red-400" : "text-sm font-medium text-green-400"}>
                            {formatCurrency(transaction.amount, balance.currency)}
                          </span>
                        </div>
                        <p className="mb-0 mt-1 text-xs text-text-secondary">{formatDate(transaction.created_at)}</p>
                      </div>
                    ))
                  ) : (
                    <p className="m-0 text-sm text-text-secondary">No transactions yet.</p>
                  )}
                </Card>

                <Card className="space-y-3">
                  <div>
                    <h2 className="mb-1 mt-0 text-lg font-semibold text-text-primary">Payment History</h2>
                    <p className="m-0 text-sm text-text-secondary">Created and confirmed payments</p>
                  </div>
                  {payments.length ? (
                    payments.map((payment) => (
                      <div className="rounded-xl bg-bg-primary px-4 py-3" key={payment.id}>
                        <div className="flex items-center justify-between gap-3">
                          <span className="text-sm font-medium text-text-primary">{formatCurrency(payment.amount, payment.currency)}</span>
                          <span className="text-xs font-medium uppercase tracking-wide text-text-secondary">{payment.status}</span>
                        </div>
                        <p className="mb-0 mt-1 text-xs text-text-secondary">{formatDate(payment.created_at)}</p>
                      </div>
                    ))
                  ) : (
                    <p className="m-0 text-sm text-text-secondary">No payments yet.</p>
                  )}
                </Card>
              </>
            ) : null}
          </>
        )}

        <BottomNav currentRoute="balance" onNavigate={onNavigate} />
      </main>
    </div>
  );
}
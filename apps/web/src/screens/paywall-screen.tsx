import { ArrowLeft, LockKeyhole } from "lucide-react";

import { AppShell } from "@/components/app-shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

function getPaywallCopy(reason: "guest-limit" | "guest-apply" | "inactive-subscription" | undefined, isAuthenticated: boolean) {
  if (reason === "inactive-subscription" && isAuthenticated) {
    return {
      title: "Доступ к откликам не активен",
      subtitle: "Пополняй баланс и активируй месячный доступ, чтобы снова откликаться.",
      body: "Подписка управляется только бэкендом. После подтвержденного платежа доступ активируется автоматически.",
    };
  }

  if (reason === "guest-apply") {
    return {
      title: "Отклик доступен после активации",
      subtitle: "Чтобы откликнуться, нужно зарегистрироваться и активировать месячный доступ.",
      body: "Вакансии можно посмотреть заранее, но отклики и расширенный доступ открываются только студенту с активной подпиской.",
    };
  }

  return {
    title: "Лимит бесплатных просмотров достигнут",
    subtitle: "Три бесплатные вакансии уже использованы.",
    body: "Чтобы смотреть больше вакансий и откликаться, нужно зарегистрироваться и активировать доступ на месяц.",
  };
}

export function PaywallScreen({
  onBack,
  onPrimaryAction,
  primaryLabel,
  reason,
  isAuthenticated,
  canAuthenticateInTelegram,
}: {
  onBack: () => void;
  onPrimaryAction: () => void;
  primaryLabel: string;
  reason?: "guest-limit" | "guest-apply" | "inactive-subscription";
  isAuthenticated: boolean;
  canAuthenticateInTelegram: boolean;
}) {
  const copy = getPaywallCopy(reason, isAuthenticated);

  return (
    <AppShell
      title="Доступ к откликам"
      subtitle={copy.subtitle}
      headerRight={
        <button className="rounded-2xl border-0 bg-white px-3 py-2 text-slate-600" onClick={onBack} type="button">
          <ArrowLeft className="h-5 w-5" />
        </button>
      }
    >
      <Card className="bg-gradient-to-br from-blue-600 to-cyan-500 text-white">
        <div className="flex items-center gap-3">
          <div className="rounded-2xl bg-white/20 p-3">
            <LockKeyhole className="h-6 w-6" />
          </div>
          <div>
            <h2 className="mb-1 mt-0 text-xl font-semibold">{copy.title}</h2>
            <p className="m-0 text-sm text-blue-50">{copy.subtitle}</p>
          </div>
        </div>
      </Card>

      <Card className="space-y-4">
        <p className="m-0 text-base font-medium text-slate-800">{copy.body}</p>
        <Button className="w-full" size="lg" onClick={onPrimaryAction}>
          {primaryLabel}
        </Button>
        {!isAuthenticated && !canAuthenticateInTelegram ? (
          <p className="m-0 text-xs text-slate-500">Открой приложение внутри Telegram, чтобы активировать доступ.</p>
        ) : null}
      </Card>
    </AppShell>
  );
}

import { ArrowLeft, LockKeyhole } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";

function getPaywallCopy(reason: "guest-limit" | "guest-apply" | "inactive-subscription" | undefined, isAuthenticated: boolean) {
  if (reason === "inactive-subscription" && isAuthenticated) {
    return {
      title: "Доступ не активирован",
      subtitle: "Пополните баланс и активируйте месячный доступ",
      body: "Подписка контролируется на сервере. После подтверждения платежа доступ активируется автоматически.",
    };
  }

  if (reason === "guest-apply") {
    return {
      title: "Отклик после регистрации",
      subtitle: "Зарегистрируйтесь и активируйте месячный доступ",
      body: "Просматривайте вакансии заранее, но отклики требуют авторизации и активного статуса.",
    };
  }

  return {
    title: "Бесплатный лимит просмотров исчерпан",
    subtitle: "Три бесплатные вакансии уже просмотрены",
    body: "Чтобы увидеть больше вакансий и откликнуться, зарегистрируйтесь и активируйте доступ.",
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
    <div className="min-h-screen bg-bg-primary">
      <header className="sticky top-0 z-10 bg-bg-secondary/80 backdrop-blur-sm">
        <div className="flex items-center justify-between px-4 py-4">
          <div>
            <h1 className="text-2xl font-bold text-text-primary">Доступ к откликам</h1>
            <p className="text-sm text-text-secondary mt-1">{copy.subtitle}</p>
          </div>
          <button className="rounded-full border-0 bg-bg-card p-3 text-text-secondary hover:text-text-primary" onClick={onBack} type="button">
            <ArrowLeft className="h-5 w-5" />
          </button>
        </div>
      </header>

      <main className="px-4 py-8">
        <Card className="bg-gradient-to-br from-accent/20 to-orange-500/10 mb-6">
          <div className="flex items-center gap-4">
            <div className="rounded-full bg-accent/20 p-4">
              <LockKeyhole className="h-8 w-8 text-accent" />
            </div>
            <div>
              <h2 className="mb-1 mt-0 text-xl font-bold text-text-primary">{copy.title}</h2>
              <p className="m-0 text-sm text-text-secondary">{copy.subtitle}</p>
            </div>
          </div>
        </Card>

        <Card className="space-y-4">
          <p className="m-0 text-base font-medium text-text-primary">{copy.body}</p>
          <Button className="w-full" size="lg" onClick={onPrimaryAction}>
            {primaryLabel}
          </Button>
          {!isAuthenticated && !canAuthenticateInTelegram ? (
            <p className="m-0 text-xs text-text-secondary text-center">
              Откройте приложение в Telegram
            </p>
          ) : null}
        </Card>
      </main>
    </div>
  );
}
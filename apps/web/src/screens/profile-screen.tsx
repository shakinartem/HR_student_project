import { LoaderCircle, Save } from "lucide-react";
import { useEffect, useState } from "react";

import { AppShell } from "@/components/app-shell";
import { BottomNav } from "@/components/bottom-nav";
import { ChipGroup, FormField } from "@/components/form-field";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import type { AppRoute } from "@/lib/routes";
import type { StudentProfile, User } from "@/types/api";

const JOB_TYPE_OPTIONS = [
  { value: "part_time", label: "Частичная занятость" },
  { value: "shift", label: "Смены" },
  { value: "internship", label: "Стажировка" },
  { value: "project", label: "Проектная работа" },
];

const SCHEDULE_OPTIONS = [
  { value: "morning", label: "Утро" },
  { value: "day", label: "День" },
  { value: "evening", label: "Вечер" },
  { value: "weekend", label: "Выходные" },
];

const DISTRICT_OPTIONS = [
  { value: "center", label: "Центр" },
  { value: "zavodskoy", label: "Заводской" },
  { value: "leninsky", label: "Ленинский" },
  { value: "kirovsky", label: "Кировский" },
];

interface ProfileFormState {
  first_name: string;
  last_name: string;
  phone: string;
  email: string;
  university: string;
  course: string;
  speciality: string;
  preferred_job_types: string[];
  preferred_schedule: string[];
  preferred_districts: string[];
  experience_text: string;
}

function buildFormState(user: User | null, profile: StudentProfile | null): ProfileFormState {
  return {
    first_name: user?.first_name ?? "",
    last_name: user?.last_name ?? "",
    phone: user?.phone ?? "",
    email: user?.email ?? "",
    university: profile?.university ?? "",
    course: profile?.course ? String(profile.course) : "",
    speciality: profile?.speciality ?? "",
    preferred_job_types: profile?.preferred_job_types ?? [],
    preferred_schedule: profile?.preferred_schedule ?? [],
    preferred_districts: profile?.preferred_districts ?? [],
    experience_text: profile?.experience_text ?? "",
  };
}

function toggleValue(items: string[], value: string) {
  return items.includes(value) ? items.filter((item) => item !== value) : [...items, value];
}

export function ProfileScreen({
  currentUser,
  profile,
  isLoading,
  isSaving,
  errorMessage,
  saveError,
  saveSuccess,
  canAuthenticateInTelegram,
  onSave,
  onNavigate,
}: {
  currentUser: User | null;
  profile: StudentProfile | null;
  isLoading: boolean;
  isSaving: boolean;
  errorMessage: string | null;
  saveError: string | null;
  saveSuccess: string | null;
  canAuthenticateInTelegram: boolean;
  onSave: (payload: ProfileFormState) => void;
  onNavigate: (route: Extract<AppRoute, { kind: "feed" | "applications" | "balance" | "profile" }>) => void;
}) {
  const [form, setForm] = useState<ProfileFormState>(() => buildFormState(currentUser, profile));

  useEffect(() => {
    setForm(buildFormState(currentUser, profile));
  }, [currentUser, profile]);

  const isGuest = !currentUser;
  const isCompleted = profile?.profile_completed ?? false;

  return (
    <AppShell
      title={isCompleted ? "Профиль студента" : "Регистрация"}
      subtitle={
        isCompleted
          ? "Проверь контакты и предпочтения. Эти данные используются при отклике."
          : "Заполни профиль, чтобы откликаться после активации доступа."
      }
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
              <h2 className="mb-1 mt-0 text-lg font-semibold">Нужен вход через Telegram</h2>
              <p className="m-0 text-sm text-slate-600">
                Профиль и регистрация доступны только после авторизации Mini App через Telegram.
              </p>
            </div>
            <p className="m-0 text-xs text-slate-500">
              {canAuthenticateInTelegram
                ? "Открой Mini App заново внутри Telegram, и авторизация выполнится автоматически."
                : "Открой приложение внутри Telegram, чтобы активировать доступ и заполнить профиль."}
            </p>
          </Card>
          <BottomNav currentRoute="profile" onNavigate={onNavigate} />
        </>
      ) : (
        <>
          {isLoading ? (
            <Card className="flex items-center gap-3">
              <LoaderCircle className="h-5 w-5 animate-spin text-accent" />
              <p className="m-0 text-sm text-slate-600">Загружаем профиль…</p>
            </Card>
          ) : null}

          {!isLoading && errorMessage ? (
            <Card className="border-red-100 bg-red-50">
              <p className="m-0 text-sm text-red-700">{errorMessage}</p>
            </Card>
          ) : null}

          {!isLoading && !errorMessage ? (
            <>
              <Card className="space-y-4">
                <FormField label="Имя">
                  <Input
                    onChange={(event) => setForm((prev) => ({ ...prev, first_name: event.target.value }))}
                    value={form.first_name}
                  />
                </FormField>

                <FormField label="Фамилия">
                  <Input
                    onChange={(event) => setForm((prev) => ({ ...prev, last_name: event.target.value }))}
                    value={form.last_name}
                  />
                </FormField>

                <FormField label="Телефон">
                  <Input
                    inputMode="tel"
                    onChange={(event) => setForm((prev) => ({ ...prev, phone: event.target.value }))}
                    placeholder="+7 999 000 00 00"
                    value={form.phone}
                  />
                </FormField>

                <FormField label="Email">
                  <Input
                    inputMode="email"
                    onChange={(event) => setForm((prev) => ({ ...prev, email: event.target.value }))}
                    placeholder="student@example.com"
                    type="email"
                    value={form.email}
                  />
                </FormField>
              </Card>

              <Card className="space-y-4">
                <FormField label="Вуз">
                  <Input
                    onChange={(event) => setForm((prev) => ({ ...prev, university: event.target.value }))}
                    value={form.university}
                  />
                </FormField>

                <FormField label="Курс">
                  <Input
                    inputMode="numeric"
                    min={1}
                    onChange={(event) => setForm((prev) => ({ ...prev, course: event.target.value }))}
                    type="number"
                    value={form.course}
                  />
                </FormField>

                <FormField label="Специальность">
                  <Input
                    onChange={(event) => setForm((prev) => ({ ...prev, speciality: event.target.value }))}
                    value={form.speciality}
                  />
                </FormField>

                <ChipGroup
                  label="Предпочитаемый формат работы"
                  onToggle={(value) =>
                    setForm((prev) => ({
                      ...prev,
                      preferred_job_types: toggleValue(prev.preferred_job_types, value),
                    }))
                  }
                  options={JOB_TYPE_OPTIONS}
                  selected={form.preferred_job_types}
                />

                <ChipGroup
                  label="Удобный график"
                  onToggle={(value) =>
                    setForm((prev) => ({
                      ...prev,
                      preferred_schedule: toggleValue(prev.preferred_schedule, value),
                    }))
                  }
                  options={SCHEDULE_OPTIONS}
                  selected={form.preferred_schedule}
                />

                <ChipGroup
                  label="Подходящие районы"
                  onToggle={(value) =>
                    setForm((prev) => ({
                      ...prev,
                      preferred_districts: toggleValue(prev.preferred_districts, value),
                    }))
                  }
                  options={DISTRICT_OPTIONS}
                  selected={form.preferred_districts}
                />

                <FormField label="Опыт и комментарий о себе">
                  <Textarea
                    onChange={(event) => setForm((prev) => ({ ...prev, experience_text: event.target.value }))}
                    value={form.experience_text}
                  />
                </FormField>
              </Card>

              {saveError ? (
                <Card className="border-red-100 bg-red-50">
                  <p className="m-0 text-sm text-red-700">{saveError}</p>
                </Card>
              ) : null}

              {saveSuccess ? (
                <Card className="border-emerald-100 bg-emerald-50">
                  <p className="m-0 text-sm text-emerald-700">{saveSuccess}</p>
                </Card>
              ) : null}

              <Button className="w-full" onClick={() => onSave(form)} size="lg">
                {isSaving ? <LoaderCircle className="mr-2 h-4 w-4 animate-spin" /> : <Save className="mr-2 h-4 w-4" />}
                Сохранить профиль
              </Button>
            </>
          ) : null}

          <BottomNav currentRoute="profile" onNavigate={onNavigate} />
        </>
      )}
    </AppShell>
  );
}

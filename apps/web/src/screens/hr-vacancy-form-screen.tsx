import { type FormEvent, useState } from "react";

import { BriefcaseBusiness, LoaderCircle } from "lucide-react";

import { FormField } from "@/components/form-field";
import { HrShell } from "@/components/hr-shell";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import type { HRVacancyCreateRequest } from "@/types/api";

const initialForm: HRVacancyCreateRequest = {
  title: "",
  category: "",
  job_type: "",
  schedule: "",
  salary_text: "",
  salary_min: null,
  salary_max: null,
  district: "",
  address: "",
  format: "",
  description: "",
  responsibilities: "",
  requirements: "",
  conditions: "",
  experience_required: false,
  photo_url: "",
};

function parseNumber(value: string) {
  if (!value.trim()) {
    return null;
  }

  const parsed = Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

export function HrVacancyFormScreen({
  isSubmitting,
  submitError,
  onBack,
  onSubmit,
}: {
  isSubmitting: boolean;
  submitError: string | null;
  onBack: () => void;
  onSubmit: (payload: HRVacancyCreateRequest) => Promise<void>;
}) {
  const [form, setForm] = useState(initialForm);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    await onSubmit({
      ...form,
      title: form.title.trim(),
      category: form.category.trim(),
      job_type: form.job_type.trim(),
      schedule: form.schedule.trim(),
      salary_text: form.salary_text.trim(),
      district: form.district?.trim() || null,
      address: form.address?.trim() || null,
      format: form.format?.trim() || null,
      description: form.description?.trim() || null,
      responsibilities: form.responsibilities?.trim() || null,
      requirements: form.requirements?.trim() || null,
      conditions: form.conditions?.trim() || null,
      photo_url: form.photo_url?.trim() || null,
    });
  }

  return (
    <HrShell
      title="Новая вакансия"
      subtitle="Чистая, понятная форма без лишнего шума. Сохраняем draft, затем доводим до публикации."
      onBack={onBack}
      footer={
        <Button className="w-full" disabled={isSubmitting} size="lg" type="submit" form="hr-vacancy-form">
          {isSubmitting ? <LoaderCircle className="mr-2 h-4 w-4 animate-spin" /> : <BriefcaseBusiness className="mr-2 h-4 w-4" />}
          Сохранить вакансию
        </Button>
      }
    >
      {submitError ? (
        <Card className="border-red-500/20 bg-red-500/10 text-red-100">
          <p className="m-0 text-sm">{submitError}</p>
        </Card>
      ) : null}

      <form className="space-y-4" id="hr-vacancy-form" onSubmit={handleSubmit}>
        <Card className="space-y-4 border-hub-border bg-hub-panel text-hub-text">
          <FormField hint="Короткий заголовок без кликбейта." label="Название">
            <Input
              className="border-white/10 bg-white text-ink"
              onChange={(event) => setForm((current) => ({ ...current, title: event.target.value }))}
              placeholder="Например, Бариста на вечерние смены"
              required
              value={form.title}
            />
          </FormField>

          <div className="grid grid-cols-2 gap-3">
            <FormField label="Категория">
              <Input
                className="border-white/10 bg-white text-ink"
                onChange={(event) => setForm((current) => ({ ...current, category: event.target.value }))}
                placeholder="Ритейл"
                required
                value={form.category}
              />
            </FormField>
            <FormField label="Формат">
              <Input
                className="border-white/10 bg-white text-ink"
                onChange={(event) => setForm((current) => ({ ...current, format: event.target.value }))}
                placeholder="Офлайн"
                value={form.format ?? ""}
              />
            </FormField>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <FormField label="Тип занятости">
              <Input
                className="border-white/10 bg-white text-ink"
                onChange={(event) => setForm((current) => ({ ...current, job_type: event.target.value }))}
                placeholder="Смены"
                required
                value={form.job_type}
              />
            </FormField>
            <FormField label="График">
              <Input
                className="border-white/10 bg-white text-ink"
                onChange={(event) => setForm((current) => ({ ...current, schedule: event.target.value }))}
                placeholder="2/2, вечер"
                required
                value={form.schedule}
              />
            </FormField>
          </div>

          <FormField label="Зарплата">
            <Input
              className="border-white/10 bg-white text-ink"
              onChange={(event) => setForm((current) => ({ ...current, salary_text: event.target.value }))}
              placeholder="3500 ₽ за смену"
              required
              value={form.salary_text}
            />
          </FormField>

          <div className="grid grid-cols-2 gap-3">
            <FormField label="Минимум">
              <Input
                className="border-white/10 bg-white text-ink"
                inputMode="numeric"
                onChange={(event) => setForm((current) => ({ ...current, salary_min: parseNumber(event.target.value) }))}
                placeholder="3000"
                value={form.salary_min ?? ""}
              />
            </FormField>
            <FormField label="Максимум">
              <Input
                className="border-white/10 bg-white text-ink"
                inputMode="numeric"
                onChange={(event) => setForm((current) => ({ ...current, salary_max: parseNumber(event.target.value) }))}
                placeholder="4000"
                value={form.salary_max ?? ""}
              />
            </FormField>
          </div>
        </Card>

        <Card className="space-y-4 border-hub-border bg-hub-panel text-hub-text">
          <div className="grid grid-cols-2 gap-3">
            <FormField label="Район">
              <Input
                className="border-white/10 bg-white text-ink"
                onChange={(event) => setForm((current) => ({ ...current, district: event.target.value }))}
                placeholder="Центр"
                value={form.district ?? ""}
              />
            </FormField>
            <FormField label="Адрес">
              <Input
                className="border-white/10 bg-white text-ink"
                onChange={(event) => setForm((current) => ({ ...current, address: event.target.value }))}
                placeholder="ул. Ленина, 1"
                value={form.address ?? ""}
              />
            </FormField>
          </div>

          <FormField label="Описание">
            <Textarea
              className="border-white/10 bg-white text-ink"
              onChange={(event) => setForm((current) => ({ ...current, description: event.target.value }))}
              placeholder="Что это за работа и почему студенту будет комфортно."
              value={form.description ?? ""}
            />
          </FormField>

          <FormField label="Обязанности">
            <Textarea
              className="border-white/10 bg-white text-ink"
              onChange={(event) => setForm((current) => ({ ...current, responsibilities: event.target.value }))}
              placeholder="Конкретные задачи без воды."
              value={form.responsibilities ?? ""}
            />
          </FormField>

          <FormField label="Требования">
            <Textarea
              className="border-white/10 bg-white text-ink"
              onChange={(event) => setForm((current) => ({ ...current, requirements: event.target.value }))}
              placeholder="Что важно для кандидата."
              value={form.requirements ?? ""}
            />
          </FormField>

          <FormField label="Условия">
            <Textarea
              className="border-white/10 bg-white text-ink"
              onChange={(event) => setForm((current) => ({ ...current, conditions: event.target.value }))}
              placeholder="Ставка, питание, обучение, бонусы."
              value={form.conditions ?? ""}
            />
          </FormField>
        </Card>
      </form>
    </HrShell>
  );
}

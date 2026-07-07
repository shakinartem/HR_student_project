import { ArrowRight, BadgeRussianRuble, Clock3, MapPin, Sparkles } from "lucide-react";

import { Card } from "@/components/ui/card";
import type { VacancyListItem } from "@/types/api";

export function VacancyCard({
  vacancy,
  onOpen,
  disabled,
}: {
  vacancy: VacancyListItem;
  onOpen: () => void;
  disabled?: boolean;
}) {
  return (
    <button className="block w-full border-0 bg-transparent p-0 text-left" onClick={onOpen} disabled={disabled} type="button">
      <Card className="transition-transform active:scale-[0.99]">
        <div className="flex items-start justify-between gap-3">
          <div>
            {vacancy.is_promoted ? (
              <span className="inline-flex items-center gap-1 rounded-full bg-amber-100 px-2.5 py-1 text-xs font-semibold text-amber-700">
                <Sparkles className="h-3.5 w-3.5" />
                Продвигается
              </span>
            ) : null}
            <h2 className="mb-1 mt-3 text-lg font-semibold">{vacancy.title}</h2>
            <p className="m-0 text-sm text-slate-600">{vacancy.company_name ?? "Компания уточняется"}</p>
          </div>
          <ArrowRight className="mt-1 h-5 w-5 text-slate-400" />
        </div>

        <div className="mt-4 grid grid-cols-2 gap-2 text-sm text-slate-700">
          <div className="flex items-center gap-2 rounded-2xl bg-slate-50 px-3 py-2">
            <BadgeRussianRuble className="h-4 w-4 text-accent" />
            <span>{vacancy.salary_text}</span>
          </div>
          <div className="flex items-center gap-2 rounded-2xl bg-slate-50 px-3 py-2">
            <MapPin className="h-4 w-4 text-accent" />
            <span>{vacancy.district ?? "Район уточняется"}</span>
          </div>
          <div className="flex items-center gap-2 rounded-2xl bg-slate-50 px-3 py-2">
            <Clock3 className="h-4 w-4 text-accent" />
            <span>{vacancy.schedule}</span>
          </div>
          <div className="rounded-2xl bg-slate-50 px-3 py-2 text-slate-700">{vacancy.job_type}</div>
        </div>
      </Card>
    </button>
  );
}

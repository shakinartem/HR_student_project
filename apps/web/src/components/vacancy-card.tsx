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
              <span className="inline-flex items-center gap-1 rounded-full bg-accent/20 px-3 py-1.5 text-xs font-semibold text-accent">
                <Sparkles className="h-3.5 w-3.5" />
                Promoted
              </span>
            ) : null}
            <h2 className="mb-1 mt-3 text-lg font-bold text-text-primary">{vacancy.title}</h2>
            <p className="m-0 text-sm text-text-secondary">{vacancy.company_name ?? "Company pending"}</p>
          </div>
          <ArrowRight className="mt-1 h-5 w-5 text-text-secondary" />
        </div>

        <div className="mt-4 grid grid-cols-2 gap-2 text-sm">
          <div className="flex items-center gap-2 rounded-xl bg-bg-primary px-3 py-2">
            <BadgeRussianRuble className="h-4 w-4 text-accent" />
            <span className="text-text-primary">{vacancy.salary_text}</span>
          </div>
          <div className="flex items-center gap-2 rounded-xl bg-bg-primary px-3 py-2">
            <MapPin className="h-4 w-4 text-accent" />
            <span className="text-text-secondary">{vacancy.district ?? "District pending"}</span>
          </div>
          <div className="flex items-center gap-2 rounded-xl bg-bg-primary px-3 py-2">
            <Clock3 className="h-4 w-4 text-accent" />
            <span className="text-text-secondary">{vacancy.schedule}</span>
          </div>
          <div className="rounded-xl bg-bg-primary px-3 py-2 text-text-secondary">{vacancy.job_type}</div>
        </div>
      </Card>
    </button>
  );
}

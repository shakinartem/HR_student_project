import { Eye } from "lucide-react";

import { Card } from "@/components/ui/card";

export function PreviewCounter({ viewedCount, maxCount }: { viewedCount: number; maxCount: number }) {
  const safeCount = Math.min(viewedCount, maxCount);
  const left = Math.max(maxCount - safeCount, 0);

  return (
    <Card className="bg-gradient-to-br from-white to-blue-50">
      <div className="flex items-center justify-between gap-3">
        <div>
          <p className="m-0 text-sm font-medium text-slate-600">Бесплатные просмотры</p>
          <p className="m-0 mt-1 text-lg font-semibold">
            {safeCount} из {maxCount}
          </p>
        </div>
        <div className="rounded-2xl bg-accentSoft p-3 text-accent">
          <Eye className="h-5 w-5" />
        </div>
      </div>
      <p className="mb-0 mt-3 text-sm text-slate-600">
        {left > 0 ? `Осталось открыть ещё ${left} вакансии бесплатно.` : "Лимит бесплатных просмотров уже достигнут."}
      </p>
    </Card>
  );
}

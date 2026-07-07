import type { PropsWithChildren, ReactNode } from "react";

export function FormField({
  label,
  hint,
  error,
  children,
}: PropsWithChildren<{
  label: string;
  hint?: string;
  error?: string | null;
}>) {
  return (
    <label className="block space-y-2">
      <div className="space-y-1">
        <span className="block text-sm font-semibold text-slate-800">{label}</span>
        {hint ? <p className="m-0 text-xs text-slate-500">{hint}</p> : null}
      </div>
      {children}
      {error ? <p className="m-0 text-xs text-red-600">{error}</p> : null}
    </label>
  );
}

export function ChipGroup({
  label,
  options,
  selected,
  onToggle,
}: {
  label: string;
  options: Array<{ value: string; label: string }>;
  selected: string[];
  onToggle: (value: string) => void;
}) {
  return (
    <div className="space-y-2">
      <span className="block text-sm font-semibold text-slate-800">{label}</span>
      <div className="flex flex-wrap gap-2">
        {options.map((option) => {
          const isSelected = selected.includes(option.value);
          return (
            <button
              className={
                isSelected
                  ? "rounded-full bg-accent px-3 py-2 text-xs font-semibold text-white"
                  : "rounded-full bg-slate-100 px-3 py-2 text-xs font-semibold text-slate-600"
              }
              key={option.value}
              onClick={() => onToggle(option.value)}
              type="button"
            >
              {option.label}
            </button>
          );
        })}
      </div>
    </div>
  );
}

export function InfoRow({ label, value }: { label: string; value: ReactNode }) {
  return (
    <div className="flex items-center justify-between gap-3 py-2">
      <span className="text-sm text-slate-500">{label}</span>
      <span className="text-right text-sm font-semibold text-slate-800">{value}</span>
    </div>
  );
}

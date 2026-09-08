import { useEffect } from "react";
import { useForm } from "react-hook-form";

import {
  COMPLAINT_LABELS, REMUNERATION_LABELS, WORKFORCE_LABELS,
  type ChildFields, type ChildKind, type ChildRow,
} from "../api/humanRightsApi";

interface NumField { name: string; label: string; step?: string }

// Per-kind configuration: which categories exist and which counts are asked.
export const CHILD_CONFIG: Record<ChildKind, { title: string; labels: Record<string, string>; fields: NumField[] }> = {
  workforce: {
    title: "Workforce coverage (EI 1 training, EI 2 minimum wages)",
    labels: WORKFORCE_LABELS,
    fields: [
      { name: "total_count", label: "Total (A)" },
      { name: "hr_training_covered", label: "Covered by HR training (B)" },
      { name: "equal_min_wage_male", label: "Equal to min. wage -- male" },
      { name: "equal_min_wage_female", label: "Equal to min. wage -- female" },
      { name: "more_than_min_wage_male", label: "More than min. wage -- male" },
      { name: "more_than_min_wage_female", label: "More than min. wage -- female" },
    ],
  },
  remuneration: {
    title: "Median remuneration by gender (EI 3)",
    labels: REMUNERATION_LABELS,
    fields: [
      { name: "male_count", label: "Male -- number" },
      { name: "male_median_inr", label: "Male -- median (INR p.a.)", step: "0.01" },
      { name: "female_count", label: "Female -- number" },
      { name: "female_median_inr", label: "Female -- median (INR p.a.)", step: "0.01" },
    ],
  },
  complaint: {
    title: "Complaints on human rights issues (EI 6)",
    labels: COMPLAINT_LABELS,
    fields: [
      { name: "filed_count", label: "Filed during the year" },
      { name: "pending_count", label: "Pending at year end" },
    ],
  },
};

type FormValues = { category: string; remarks: string } & Record<string, unknown>;

interface Props {
  kind: ChildKind;
  initialData?: ChildRow;
  usedCategories?: string[]; // hidden on create: one row per category
  onSubmit: (data: ChildFields | Partial<ChildFields>) => void;
  onCancel?: () => void;
  loading?: boolean;
}

const inputCls = "w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none";

export default function ChildRowForm({ kind, initialData, usedCategories = [], onSubmit, onCancel, loading = false }: Props) {
  const cfg = CHILD_CONFIG[kind];
  const categories = Object.keys(cfg.labels);
  const isEdit = Boolean(initialData);
  const selectable = categories.filter((c) => !usedCategories.includes(c) || c === initialData?.category);

  const { register, handleSubmit, reset, formState: { errors } } = useForm<FormValues>();

  useEffect(() => {
    const base: Record<string, unknown> = {
      category: initialData?.category ?? selectable[0] ?? categories[0],
      remarks: initialData?.remarks ?? "",
    };
    for (const f of cfg.fields) {
      const v = initialData ? (initialData as unknown as Record<string, unknown>)[f.name] : undefined;
      base[f.name] = v ?? "";
    }
    reset(base as FormValues);
  }, [initialData, reset]); // eslint-disable-line react-hooks/exhaustive-deps

  // Create omits blanks; edit sends null (backend PUT is exclude_unset).
  const submit = (values: FormValues) => {
    const out: Record<string, unknown> = { category: values.category };
    for (const f of cfg.fields) {
      const raw = values[f.name];
      const v = raw === "" || raw === undefined || Number.isNaN(raw) ? null : Number(raw);
      if (v === null && !isEdit) continue;
      out[f.name] = v;
    }
    const remarks = values.remarks.trim() === "" ? null : values.remarks;
    if (remarks !== null || isEdit) out.remarks = remarks;
    onSubmit(out as ChildFields | Partial<ChildFields>);
  };

  return (
    <form onSubmit={handleSubmit(submit)} className="space-y-4 rounded-xl border border-gray-200 bg-gray-50 p-4">
      <h4 className="font-semibold text-gray-800">{isEdit ? "Edit row" : "Add row"} -- {cfg.title}</h4>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <div className="md:col-span-3">
          <label className="mb-1 block text-sm font-medium text-gray-700">Category *</label>
          <select {...register("category", { required: "Required" })} className={inputCls}>
            {selectable.map((c) => <option key={c} value={c}>{cfg.labels[c]}</option>)}
          </select>
          {errors.category && <p className="mt-1 text-sm text-red-600">{String(errors.category.message)}</p>}
        </div>
        {cfg.fields.map((f) => (
          <div key={f.name}>
            <label className="mb-1 block text-sm font-medium text-gray-700">{f.label}</label>
            <input type="number" step={f.step ?? "1"} min={0} placeholder="Not disclosed"
              {...register(f.name, { valueAsNumber: true })} className={inputCls} />
          </div>
        ))}
        <div className="md:col-span-3">
          <label className="mb-1 block text-sm font-medium text-gray-700">Remarks</label>
          <input type="text" {...register("remarks")} className={inputCls} />
        </div>
      </div>

      <div className="flex justify-end gap-3">
        {onCancel && (
          <button type="button" onClick={onCancel} disabled={loading}
            className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 disabled:opacity-50">
            Cancel
          </button>
        )}
        <button type="submit" disabled={loading || selectable.length === 0}
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
          {loading ? "Saving..." : isEdit ? "Update row" : "Add row"}
        </button>
      </div>
    </form>
  );
}

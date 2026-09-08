import { useEffect } from "react";
import { useForm } from "react-hook-form";

/**
 * Generic "one row per category" child form for BRSR tables: a category
 * select plus a configurable set of numeric fields and remarks. Create
 * omits blanks; edit sends blanks as null (backend PUT is exclude_unset).
 * Categories already present on the record are hidden on create.
 */
export interface NumField { name: string; label: string; step?: string }
export interface CategoryRowConfig {
  title: string;
  labels: Record<string, string>;
  fields: NumField[];
}

type FormValues = { category: string; remarks: string } & Record<string, unknown>;

interface Props {
  config: CategoryRowConfig;
  initialData?: Record<string, unknown> & { category: string };
  usedCategories?: string[];
  onSubmit: (data: Record<string, unknown>) => void;
  onCancel?: () => void;
  loading?: boolean;
}

const inputCls = "w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none";

export default function CategoryRowForm({ config, initialData, usedCategories = [], onSubmit, onCancel, loading = false }: Props) {
  const categories = Object.keys(config.labels);
  const isEdit = Boolean(initialData);
  const selectable = categories.filter((c) => !usedCategories.includes(c) || c === initialData?.category);
  const { register, handleSubmit, reset } = useForm<FormValues>();

  useEffect(() => {
    const base: Record<string, unknown> = {
      category: initialData?.category ?? selectable[0] ?? categories[0],
      remarks: (initialData?.remarks as string | null | undefined) ?? "",
    };
    for (const f of config.fields) base[f.name] = initialData?.[f.name] ?? "";
    reset(base as FormValues);
  }, [initialData, reset]); // eslint-disable-line react-hooks/exhaustive-deps

  const submit = (values: FormValues) => {
    const out: Record<string, unknown> = { category: values.category };
    for (const f of config.fields) {
      const raw = values[f.name];
      const v = raw === "" || raw === undefined || Number.isNaN(raw) ? null : Number(raw);
      if (v === null && !isEdit) continue;
      out[f.name] = v;
    }
    const remarks = values.remarks.trim() === "" ? null : values.remarks;
    if (remarks !== null || isEdit) out.remarks = remarks;
    onSubmit(out);
  };

  return (
    <form onSubmit={handleSubmit(submit)} className="space-y-4 rounded-xl border border-gray-200 bg-gray-50 p-4">
      <h4 className="font-semibold text-gray-800">{isEdit ? "Edit row" : "Add row"} -- {config.title}</h4>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <div className="md:col-span-3">
          <label className="mb-1 block text-sm font-medium text-gray-700">Category *</label>
          <select {...register("category", { required: true })} className={inputCls}>
            {selectable.map((c) => <option key={c} value={c}>{config.labels[c]}</option>)}
          </select>
        </div>
        {config.fields.map((f) => (
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
            className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 disabled:opacity-50">Cancel</button>
        )}
        <button type="submit" disabled={loading || selectable.length === 0}
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50">
          {loading ? "Saving..." : isEdit ? "Update row" : "Add row"}
        </button>
      </div>
    </form>
  );
}

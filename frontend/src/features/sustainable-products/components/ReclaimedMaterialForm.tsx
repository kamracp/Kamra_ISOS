import { useEffect } from "react";
import { useForm } from "react-hook-form";

import {
  RECLAIM_CATEGORY_LABELS,
  type ReclaimCategory,
  type ReclaimedMaterial,
  type ReclaimedMaterialCreate,
  type ReclaimedMaterialUpdate,
} from "../api/sustainableProductsApi";

interface FormValues {
  material_category: ReclaimCategory;
  reused_mt: number | "";
  recycled_mt: number | "";
  disposed_mt: number | "";
  remarks: string;
}

interface Props {
  initialData?: ReclaimedMaterial;
  usedCategories?: ReclaimCategory[]; // already present on this record -- hidden on create
  onSubmit: (data: ReclaimedMaterialCreate | ReclaimedMaterialUpdate) => void;
  onCancel?: () => void;
  loading?: boolean;
}

const CATEGORIES = Object.keys(RECLAIM_CATEGORY_LABELS) as ReclaimCategory[];
const QTY_FIELDS = ["reused_mt", "recycled_mt", "disposed_mt"] as const;
const QTY_LABELS: Record<(typeof QTY_FIELDS)[number], string> = {
  reused_mt: "Re-used (MT)",
  recycled_mt: "Recycled (MT)",
  disposed_mt: "Safely disposed (MT)",
};

const inputCls =
  "w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none";

export default function ReclaimedMaterialForm({
  initialData,
  usedCategories = [],
  onSubmit,
  onCancel,
  loading = false,
}: Props) {
  const isEdit = Boolean(initialData);
  const { register, handleSubmit, reset, formState: { errors } } = useForm<FormValues>();

  useEffect(() => {
    reset({
      material_category:
        initialData?.material_category ??
        CATEGORIES.find((c) => !usedCategories.includes(c)) ??
        "plastics",
      reused_mt: initialData?.reused_mt ?? "",
      recycled_mt: initialData?.recycled_mt ?? "",
      disposed_mt: initialData?.disposed_mt ?? "",
      remarks: initialData?.remarks ?? "",
    });
  }, [initialData, reset]); // eslint-disable-line react-hooks/exhaustive-deps

  // Same rule as the record form: create omits blanks, edit sends null so a
  // cleared quantity is actually cleared (backend PUT is exclude_unset).
  const submit = (values: FormValues) => {
    const out: Record<string, unknown> = { material_category: values.material_category };
    for (const f of QTY_FIELDS) {
      const raw = values[f];
      const v = raw === "" || raw === undefined || Number.isNaN(raw) ? null : Number(raw);
      if (v === null && !isEdit) continue;
      out[f] = v;
    }
    const remarks = values.remarks.trim() === "" ? null : values.remarks;
    if (remarks !== null || isEdit) out.remarks = remarks;
    onSubmit(out as ReclaimedMaterialCreate | ReclaimedMaterialUpdate);
  };

  // On create, categories already on the record are hidden; on edit the
  // current one must stay selectable even though it is "used".
  const selectable = CATEGORIES.filter(
    (c) => !usedCategories.includes(c) || c === initialData?.material_category,
  );

  return (
    <form
      onSubmit={handleSubmit(submit)}
      className="space-y-4 rounded-xl border border-gray-200 bg-gray-50 p-4"
    >
      <h4 className="font-semibold text-gray-800">
        {isEdit ? "Edit reclaimed material row" : "Add reclaimed material row"}
      </h4>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Material *</label>
          <select {...register("material_category", { required: "Required" })} className={inputCls}>
            {selectable.map((c) => (
              <option key={c} value={c}>{RECLAIM_CATEGORY_LABELS[c]}</option>
            ))}
          </select>
          {errors.material_category && (
            <p className="mt-1 text-sm text-red-600">{errors.material_category.message}</p>
          )}
        </div>
        {QTY_FIELDS.map((f) => (
          <div key={f}>
            <label className="mb-1 block text-sm font-medium text-gray-700">{QTY_LABELS[f]}</label>
            <input
              type="number"
              step="0.001"
              min={0}
              {...register(f, { valueAsNumber: true })}
              className={inputCls}
              placeholder="Not tracked"
            />
          </div>
        ))}
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">Remarks</label>
        <input type="text" {...register("remarks")} className={inputCls} />
      </div>

      <div className="flex justify-end gap-3">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={loading}
            className="rounded-lg border border-gray-300 px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 disabled:opacity-50"
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          disabled={loading || selectable.length === 0}
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Saving..." : isEdit ? "Update row" : "Add row"}
        </button>
      </div>
    </form>
  );
}

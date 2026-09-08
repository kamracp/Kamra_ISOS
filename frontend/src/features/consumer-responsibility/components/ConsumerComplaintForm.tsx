import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { COMPLAINT_LABELS, type ConsumerComplaint, type ConsumerComplaintCategory, type ConsumerComplaintFields } from "../api/consumerResponsibilityApi";

interface FormValues { category: ConsumerComplaintCategory; received_count: number | ""; pending_count: number | ""; remarks: string }
interface Props {
  initialData?: ConsumerComplaint;
  usedCategories?: ConsumerComplaintCategory[];
  onSubmit: (data: ConsumerComplaintFields | Partial<ConsumerComplaintFields>) => void;
  onCancel?: () => void;
  loading?: boolean;
}
const CATEGORIES = Object.keys(COMPLAINT_LABELS) as ConsumerComplaintCategory[];
const inputCls = "w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none";

export default function ConsumerComplaintForm({ initialData, usedCategories = [], onSubmit, onCancel, loading = false }: Props) {
  const isEdit = Boolean(initialData);
  const selectable = CATEGORIES.filter((c) => !usedCategories.includes(c) || c === initialData?.category);
  const { register, handleSubmit, reset } = useForm<FormValues>();

  useEffect(() => {
    reset({
      category: initialData?.category ?? selectable[0] ?? "other",
      received_count: initialData?.received_count ?? "",
      pending_count: initialData?.pending_count ?? "",
      remarks: initialData?.remarks ?? "",
    });
  }, [initialData, reset]); // eslint-disable-line react-hooks/exhaustive-deps

  const submit = (v: FormValues) => {
    const out: Record<string, unknown> = { category: v.category };
    for (const f of ["received_count", "pending_count"] as const) {
      const raw = v[f];
      const val = raw === "" || raw === undefined || Number.isNaN(raw) ? null : Number(raw);
      if (val === null && !isEdit) continue;
      out[f] = val;
    }
    const remarks = v.remarks.trim() === "" ? null : v.remarks;
    if (remarks !== null || isEdit) out.remarks = remarks;
    onSubmit(out as ConsumerComplaintFields | Partial<ConsumerComplaintFields>);
  };

  return (
    <form onSubmit={handleSubmit(submit)} className="space-y-4 rounded-xl border border-gray-200 bg-gray-50 p-4">
      <h4 className="font-semibold text-gray-800">{isEdit ? "Edit complaint row" : "Add complaint row"}</h4>
      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Category *</label>
          <select {...register("category", { required: true })} className={inputCls}>
            {selectable.map((c) => <option key={c} value={c}>{COMPLAINT_LABELS[c]}</option>)}
          </select>
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Received during the year</label>
          <input type="number" step="1" min={0} placeholder="Not disclosed" {...register("received_count", { valueAsNumber: true })} className={inputCls} />
        </div>
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Pending at year end</label>
          <input type="number" step="1" min={0} placeholder="Not disclosed" {...register("pending_count", { valueAsNumber: true })} className={inputCls} />
        </div>
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">Remarks</label>
        <input type="text" {...register("remarks")} className={inputCls} />
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

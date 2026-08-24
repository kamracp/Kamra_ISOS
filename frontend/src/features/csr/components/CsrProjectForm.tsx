import { useEffect } from "react";
import { useForm } from "react-hook-form";

import type { CsrProject, CsrProjectCreate } from "../api/csrApi";

interface CsrProjectFormProps {
  initialData?: CsrProject;
  onSubmit: (data: CsrProjectCreate) => void;
  onCancel?: () => void;
  loading?: boolean;
}

export default function CsrProjectForm({
  initialData,
  onSubmit,
  onCancel,
  loading = false,
}: CsrProjectFormProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<CsrProjectCreate>();

  useEffect(() => {
    if (initialData) {
      reset({
        project_name: initialData.project_name,
        activity_category: initialData.activity_category ?? "",
        location: initialData.location ?? "",
        is_local_area: initialData.is_local_area ?? "",
        amount_spent_inr: initialData.amount_spent_inr
          ? Number(initialData.amount_spent_inr)
          : undefined,
        direct_beneficiaries_count: initialData.direct_beneficiaries_count ?? undefined,
        remarks: initialData.remarks ?? "",
      });
    } else {
      reset({
        project_name: "",
        activity_category: "",
        location: "",
        is_local_area: "",
        amount_spent_inr: undefined,
        direct_beneficiaries_count: undefined,
        remarks: "",
      });
    }
  }, [initialData, reset]);

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="space-y-6 rounded-xl border border-gray-200 bg-white p-6 shadow-sm"
    >
      <div>
        <h2 className="text-xl font-semibold text-gray-800">
          {initialData ? "Edit CSR Project" : "Add CSR Project"}
        </h2>
        <p className="mt-1 text-sm text-gray-500">
          Schedule VII activity funded within this reporting year.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Project Name *
          </label>
          <input
            type="text"
            {...register("project_name", { required: "Required" })}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />
          {errors.project_name && (
            <p className="mt-1 text-sm text-red-600">{errors.project_name.message}</p>
          )}
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Activity Category
          </label>
          <input
            type="text"
            placeholder="e.g. Education, Health, Environment"
            {...register("activity_category")}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Location</label>
          <input
            type="text"
            {...register("location")}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Local Area?
          </label>
          <select
            {...register("is_local_area")}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          >
            <option value="">Select...</option>
            <option value="yes">Yes</option>
            <option value="no">No</option>
            <option value="partial">Partial</option>
          </select>
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Amount Spent (₹)
          </label>
          <input
            type="number"
            step="any"
            {...register("amount_spent_inr", { valueAsNumber: true, min: 0 })}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Direct Beneficiaries
          </label>
          <input
            type="number"
            {...register("direct_beneficiaries_count", { valueAsNumber: true, min: 0 })}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />
        </div>
      </div>

      <div>
        <label className="mb-1 block text-sm font-medium text-gray-700">Remarks</label>
        <textarea
          {...register("remarks")}
          rows={2}
          className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
        />
      </div>

      <div className="flex justify-end gap-3 border-t border-gray-200 pt-6">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={loading}
            className="rounded-lg border border-gray-300 px-5 py-2 font-medium text-gray-700 transition hover:bg-gray-100 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-blue-600 px-5 py-2 font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {loading ? "Saving..." : initialData ? "Update Project" : "Add Project"}
        </button>
      </div>
    </form>
  );
}

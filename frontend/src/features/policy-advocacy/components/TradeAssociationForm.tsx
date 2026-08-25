import { useEffect } from "react";
import { useForm } from "react-hook-form";

import type { TradeAssociation, TradeAssociationCreate } from "../api/policyAdvocacyApi";

interface TradeAssociationFormProps {
  initialData?: TradeAssociation;
  onSubmit: (data: TradeAssociationCreate) => void;
  onCancel?: () => void;
  loading?: boolean;
}

export default function TradeAssociationForm({
  initialData,
  onSubmit,
  onCancel,
  loading = false,
}: TradeAssociationFormProps) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<TradeAssociationCreate>();

  useEffect(() => {
    if (initialData) {
      reset({
        association_name: initialData.association_name,
        reach: initialData.reach ?? "",
        remarks: initialData.remarks ?? "",
      });
    } else {
      reset({
        association_name: "",
        reach: "",
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
          {initialData ? "Edit Trade Association" : "Add Trade Association"}
        </h2>
        <p className="mt-1 text-sm text-gray-500">
          Trade/industry chamber membership within this reporting year.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Association Name *
          </label>
          <input
            type="text"
            placeholder="e.g. Confederation of Indian Industry (CII)"
            {...register("association_name", { required: "Required" })}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />
          {errors.association_name && (
            <p className="mt-1 text-sm text-red-600">{errors.association_name.message}</p>
          )}
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Reach</label>
          <select
            {...register("reach")}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          >
            <option value="">Select...</option>
            <option value="National">National</option>
            <option value="State">State</option>
            <option value="District">District</option>
          </select>
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
          {loading ? "Saving..." : initialData ? "Update Association" : "Add Association"}
        </button>
      </div>
    </form>
  );
}

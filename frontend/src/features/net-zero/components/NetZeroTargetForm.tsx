import { useForm } from "react-hook-form";
import type { NetZeroTargetCreate } from "../api/netZeroApi";

interface NetZeroTargetFormProps {
  onSubmit: (data: NetZeroTargetCreate) => void;
  onCancel?: () => void;
  loading?: boolean;
}

export default function NetZeroTargetForm({
  onSubmit,
  onCancel,
  loading = false,
}: NetZeroTargetFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<NetZeroTargetCreate>({
    defaultValues: {
      target_type: "near_term",
      scope_coverage: "scope_1_2",
    },
  });

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="space-y-6 rounded-xl border border-gray-200 bg-white p-6 shadow-sm"
    >
      <div>
        <h2 className="text-xl font-semibold text-gray-800">Add Net Zero Target</h2>
        <p className="mt-1 text-sm text-gray-500">
          SBTi-style commitment: reduce emissions X% from a baseline year, by a target year.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Target Name *</label>
          <input
            type="text"
            {...register("target_name", { required: "Required" })}
            placeholder="e.g. Near-Term SBTi Target"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />
          {errors.target_name && (
            <p className="mt-1 text-sm text-red-600">{errors.target_name.message}</p>
          )}
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Target Type</label>
          <select
            {...register("target_type")}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          >
            <option value="near_term">Near-Term (5-10 yr)</option>
            <option value="long_term">Long-Term (Net Zero)</option>
          </select>
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Baseline Year *</label>
          <input
            type="number"
            {...register("baseline_year", { required: "Required", valueAsNumber: true })}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />
          {errors.baseline_year && (
            <p className="mt-1 text-sm text-red-600">{errors.baseline_year.message}</p>
          )}
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Baseline Emissions (tCO2e) *
          </label>
          <input
            type="number"
            step="any"
            {...register("baseline_co2e_tonnes", { required: "Required", valueAsNumber: true })}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />
          {errors.baseline_co2e_tonnes && (
            <p className="mt-1 text-sm text-red-600">{errors.baseline_co2e_tonnes.message}</p>
          )}
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Target Year *</label>
          <input
            type="number"
            {...register("target_year", { required: "Required", valueAsNumber: true })}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />
          {errors.target_year && (
            <p className="mt-1 text-sm text-red-600">{errors.target_year.message}</p>
          )}
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Reduction Target (%) *
          </label>
          <input
            type="number"
            step="any"
            {...register("reduction_percentage", { required: "Required", valueAsNumber: true })}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />
          {errors.reduction_percentage && (
            <p className="mt-1 text-sm text-red-600">{errors.reduction_percentage.message}</p>
          )}
        </div>
      </div>

      <div className="flex justify-end gap-3 border-t border-gray-200 pt-6">
        {onCancel && (
          <button
            type="button"
            onClick={onCancel}
            disabled={loading}
            className="rounded-lg border border-gray-300 px-5 py-2 font-medium text-gray-700 hover:bg-gray-100 disabled:opacity-50"
          >
            Cancel
          </button>
        )}
        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-blue-600 px-5 py-2 font-medium text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {loading ? "Saving..." : "Add Target"}
        </button>
      </div>
    </form>
  );
}

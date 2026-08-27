import { useEffect } from "react";
import { useForm } from "react-hook-form";

import type {
  ManufacturingElectricityRecord,
  ManufacturingElectricityRecordCreate,
} from "../api/manufacturingElectricityApi";

interface ManufacturingElectricityRecordFormProps {
  units: { id: number; unit_name: string; unit_code: string }[];
  initialData?: ManufacturingElectricityRecord;
  defaultUnitId?: number;
  onSubmit: (data: ManufacturingElectricityRecordCreate) => void;
  onCancel?: () => void;
  loading?: boolean;
}

export default function ManufacturingElectricityRecordForm({
  units,
  initialData,
  defaultUnitId,
  onSubmit,
  onCancel,
  loading = false,
}: ManufacturingElectricityRecordFormProps) {
  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm<ManufacturingElectricityRecordCreate>();

  const consumed = watch("electricity_consumed_kwh");
  const renewable = watch("renewable_kwh");

  useEffect(() => {
    if (initialData) {
      reset({
        manufacturing_unit_id: initialData.manufacturing_unit_id,
        period_start: initialData.period_start,
        period_end: initialData.period_end,
        electricity_consumed_kwh: initialData.electricity_consumed_kwh,
        renewable_kwh: initialData.renewable_kwh,
        source: initialData.source ?? "",
        remarks: initialData.remarks ?? "",
      });
    } else {
      reset({
        manufacturing_unit_id: defaultUnitId,
        period_start: "",
        period_end: "",
        electricity_consumed_kwh: undefined,
        renewable_kwh: 0,
        source: "",
        remarks: "",
      });
    }
  }, [initialData, defaultUnitId, reset]);

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="space-y-6 rounded-xl border border-gray-200 bg-white p-6 shadow-sm"
    >
      <div>
        <h2 className="text-xl font-semibold text-gray-800">
          {initialData ? "Edit Electricity Record" : "Add Electricity Record"}
        </h2>
        <p className="mt-1 text-sm text-gray-500">
          Scope 2 purchased electricity -- CO2e is derived automatically using the
          unit's country grid factor.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Manufacturing Unit *
          </label>
          <select
            {...register("manufacturing_unit_id", {
              required: "Required",
              valueAsNumber: true,
            })}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          >
            <option value="">Select...</option>
            {units.map((u) => (
              <option key={u.id} value={u.id}>
                {u.unit_code} -- {u.unit_name}
              </option>
            ))}
          </select>
          {errors.manufacturing_unit_id && (
            <p className="mt-1 text-sm text-red-600">{errors.manufacturing_unit_id.message}</p>
          )}
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Source</label>
          <input
            type="text"
            placeholder="e.g. Utility bill #4521"
            {...register("source")}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Period Start *
          </label>
          <input
            type="date"
            {...register("period_start", { required: "Required" })}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />
          {errors.period_start && (
            <p className="mt-1 text-sm text-red-600">{errors.period_start.message}</p>
          )}
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Period End *
          </label>
          <input
            type="date"
            {...register("period_end", { required: "Required" })}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />
          {errors.period_end && (
            <p className="mt-1 text-sm text-red-600">{errors.period_end.message}</p>
          )}
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Electricity Consumed (kWh) *
          </label>
          <input
            type="number"
            step="any"
            {...register("electricity_consumed_kwh", {
              required: "Required",
              valueAsNumber: true,
              min: { value: 0, message: "Must be 0 or more" },
            })}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />
          {errors.electricity_consumed_kwh && (
            <p className="mt-1 text-sm text-red-600">{errors.electricity_consumed_kwh.message}</p>
          )}
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Renewable Portion (kWh)
          </label>
          <input
            type="number"
            step="any"
            {...register("renewable_kwh", { valueAsNumber: true, min: 0 })}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />
        </div>
      </div>

      {consumed !== undefined && consumed !== null && (
        <div className="rounded-lg bg-blue-50 px-4 py-3 text-sm text-blue-800">
          Billed against grid factor:{" "}
          <span className="font-semibold">
            {Math.max((consumed || 0) - (renewable || 0), 0).toLocaleString()} kWh
          </span>{" "}
          (renewable portion excluded)
        </div>
      )}

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
          {loading ? "Saving..." : initialData ? "Update Record" : "Add Record"}
        </button>
      </div>
    </form>
  );
}

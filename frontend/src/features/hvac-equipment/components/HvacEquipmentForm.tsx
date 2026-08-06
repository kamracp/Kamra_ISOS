import { useEffect } from "react";
import { useForm } from "react-hook-form";

import type { HvacEquipment, HvacEquipmentCreate } from "../api/hvacEquipmentApi";

interface HvacEquipmentFormProps {
  buildings: { id: number; building_name: string }[];
  initialData?: HvacEquipment;
  defaultBuildingId?: number;
  onSubmit: (data: HvacEquipmentCreate) => void;
  onCancel?: () => void;
  loading?: boolean;
}

export default function HvacEquipmentForm({
  buildings,
  initialData,
  defaultBuildingId,
  onSubmit,
  onCancel,
  loading = false,
}: HvacEquipmentFormProps) {
  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm<HvacEquipmentCreate>();

  const capacity = watch("capacity_kw");
  const cop = watch("cop");
  const hours = watch("operating_hours_per_day");
  const days = watch("operating_days_per_month");

  const livePreview =
    capacity && cop && hours && days
      ? ((Number(capacity) / Number(cop)) * Number(hours) * Number(days)).toFixed(2)
      : null;

  useEffect(() => {
    if (initialData) {
      reset({
        building_id: initialData.building_id,
        equipment_code: initialData.equipment_code,
        equipment_name: initialData.equipment_name,
        equipment_type: initialData.equipment_type,
        capacity_kw: initialData.capacity_kw,
        cop: initialData.cop,
        operating_hours_per_day: initialData.operating_hours_per_day,
        operating_days_per_month: initialData.operating_days_per_month,
        manufacturer: initialData.manufacturer ?? "",
        installation_year: initialData.installation_year ?? undefined,
        is_active: initialData.is_active,
      });
    } else {
      reset({
        building_id: defaultBuildingId ?? undefined,
        equipment_code: "",
        equipment_name: "",
        equipment_type: "",
        // Typical starting values for a standard split-AC/package unit —
        // the user should override these with actual nameplate data where known.
        capacity_kw: 5.5,
        cop: 3.2,
        operating_hours_per_day: 8,
        operating_days_per_month: 26,
        manufacturer: "",
        installation_year: undefined,
        is_active: true,
      });
    }
  }, [initialData, defaultBuildingId, reset]);

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="space-y-8 rounded-xl border border-gray-200 bg-white p-6 shadow-sm"
    >
      <div>
        <h2 className="text-xl font-semibold text-gray-800">
          {initialData ? "Edit HVAC Equipment" : "Add HVAC Equipment"}
        </h2>

        <p className="mt-1 text-sm text-gray-500">
          Enter equipment specifications for engineering-based energy estimation.
        </p>
      </div>

      {/* Identity */}
      <section className="space-y-4">
        <h3 className="border-b pb-2 text-lg font-semibold text-gray-700">
          Identity
        </h3>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Building *
            </label>

            <select
              {...register("building_id", {
                required: "Building is required",
                valueAsNumber: true,
              })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            >
              <option value="">Select building...</option>
              {buildings.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.building_name}
                </option>
              ))}
            </select>

            {errors.building_id && (
              <p className="mt-1 text-sm text-red-600">
                {errors.building_id.message}
              </p>
            )}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Equipment Code *
            </label>

            <input
              type="text"
              {...register("equipment_code", {
                required: "Equipment code is required",
              })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />

            {errors.equipment_code && (
              <p className="mt-1 text-sm text-red-600">
                {errors.equipment_code.message}
              </p>
            )}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Equipment Name *
            </label>

            <input
              type="text"
              {...register("equipment_name", {
                required: "Equipment name is required",
              })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />

            {errors.equipment_name && (
              <p className="mt-1 text-sm text-red-600">
                {errors.equipment_name.message}
              </p>
            )}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Equipment Type *
            </label>

            <select
              {...register("equipment_type", {
                required: "Equipment type is required",
              })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            >
              <option value="">Select type...</option>
              <option value="Chiller">Chiller</option>
              <option value="Split-AC">Split AC</option>
              <option value="VRF">VRF</option>
              <option value="Package-Unit">Package Unit</option>
              <option value="Cassette-AC">Cassette AC</option>
              <option value="Other">Other</option>
            </select>

            {errors.equipment_type && (
              <p className="mt-1 text-sm text-red-600">
                {errors.equipment_type.message}
              </p>
            )}
          </div>
        </div>
      </section>

      {/* Performance specs */}
      <section className="space-y-4">
        <h3 className="border-b pb-2 text-lg font-semibold text-gray-700">
          Performance Specifications
        </h3>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Capacity (kW) *
            </label>

            <input
              type="number"
              step="any"
              {...register("capacity_kw", {
                required: "Capacity is required",
                valueAsNumber: true,
                min: { value: 0.01, message: "Must be greater than 0" },
              })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />

            {errors.capacity_kw && (
              <p className="mt-1 text-sm text-red-600">
                {errors.capacity_kw.message}
              </p>
            )}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              COP *
            </label>

            <input
              type="number"
              step="any"
              {...register("cop", {
                required: "COP is required",
                valueAsNumber: true,
                min: { value: 0.01, message: "Must be greater than 0" },
              })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />

            {errors.cop && (
              <p className="mt-1 text-sm text-red-600">{errors.cop.message}</p>
            )}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Hours/Day *
            </label>

            <input
              type="number"
              step="any"
              {...register("operating_hours_per_day", {
                required: "Operating hours is required",
                valueAsNumber: true,
              })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />

            {errors.operating_hours_per_day && (
              <p className="mt-1 text-sm text-red-600">
                {errors.operating_hours_per_day.message}
              </p>
            )}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Days/Month
            </label>

            <input
              type="number"
              {...register("operating_days_per_month", { valueAsNumber: true })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
          </div>
        </div>

        {livePreview && (
          <div className="rounded-lg bg-blue-50 px-4 py-3 text-sm text-blue-800">
            Estimated energy consumption:{" "}
            <span className="font-semibold">{livePreview} kWh/month</span>
          </div>
        )}
      </section>

      {/* Additional info */}
      <section className="space-y-4">
        <h3 className="border-b pb-2 text-lg font-semibold text-gray-700">
          Additional Information
        </h3>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Manufacturer
            </label>

            <input
              type="text"
              {...register("manufacturer")}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Installation Year
            </label>

            <input
              type="number"
              {...register("installation_year", { valueAsNumber: true })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
          </div>

          <div className="flex items-end">
            <label className="inline-flex items-center gap-3">
              <input
                type="checkbox"
                {...register("is_active")}
                className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
              />

              <span className="text-sm font-medium text-gray-700">
                Active Equipment
              </span>
            </label>
          </div>
        </div>
      </section>

      {/* Action Buttons */}
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
          {loading
            ? "Saving..."
            : initialData
              ? "Update Equipment"
              : "Add Equipment"}
        </button>
      </div>
    </form>
  );
}

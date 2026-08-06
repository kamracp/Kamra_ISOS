import { useEffect } from "react";
import { useForm } from "react-hook-form";

import type { Building, BuildingCreate } from "../api/buildingApi";
import { useSegment } from "../../../context/SegmentContext";
import { useFacilityCategories } from "../../facility-categories/hooks/useFacilityCategories";

interface BuildingFormProps {
  initialData?: Building;
  onSubmit: (data: BuildingCreate) => void;
  onCancel?: () => void;
  loading?: boolean;
}

export default function BuildingForm({
  initialData,
  onSubmit,
  onCancel,
  loading = false,
}: BuildingFormProps) {
  const { segment } = useSegment();
  const { data: categories = [] } = useFacilityCategories(segment);

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<BuildingCreate>();

  useEffect(() => {
    if (initialData) {
      reset({
        building_code: initialData.building_code,
        building_name: initialData.building_name,
        description: initialData.description ?? "",
        address_line_1: initialData.address_line_1 ?? "",
        address_line_2: initialData.address_line_2 ?? "",
        city: initialData.city ?? "",
        state: initialData.state ?? "",
        country: initialData.country ?? "",
        pincode: initialData.pincode ?? "",
        building_type: initialData.building_type ?? "",
        category_id: initialData.category_id ?? undefined,
        total_floor_area: initialData.total_floor_area ?? undefined,
        number_of_floors: initialData.number_of_floors ?? undefined,
        year_constructed: initialData.year_constructed ?? undefined,
        is_active: initialData.is_active,
      });
    } else {
      reset({
        building_code: "",
        building_name: "",
        description: "",
        address_line_1: "",
        address_line_2: "",
        city: "",
        state: "",
        country: "India",
        pincode: "",
        building_type: "",
        category_id: undefined,
        total_floor_area: undefined,
        number_of_floors: undefined,
        year_constructed: undefined,
        is_active: true,
      });
    }
  }, [initialData, reset]);

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="space-y-8 rounded-xl border border-gray-200 bg-white p-6 shadow-sm"
    >
      <div>
        <h2 className="text-xl font-semibold text-gray-800">
          {initialData ? "Edit Building" : "Create Building"}
        </h2>

        <p className="mt-1 text-sm text-gray-500">
          Enter building master information.
        </p>
      </div>

      {/* Identity Information */}
      <section className="space-y-4">
        <h3 className="border-b pb-2 text-lg font-semibold text-gray-700">
          Identity
        </h3>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Building Code *
            </label>

            <input
              type="text"
              {...register("building_code", {
                required: "Building code is required",
              })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />

            {errors.building_code && (
              <p className="mt-1 text-sm text-red-600">
                {errors.building_code.message}
              </p>
            )}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Building Name *
            </label>

            <input
              type="text"
              {...register("building_name", {
                required: "Building name is required",
              })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />

            {errors.building_name && (
              <p className="mt-1 text-sm text-red-600">
                {errors.building_name.message}
              </p>
            )}
          </div>

          <div className="md:col-span-2">
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Description
            </label>

            <textarea
              {...register("description")}
              rows={3}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
          </div>
        </div>
      </section>

      {/* Building Details */}
      <section className="space-y-4">
        <h3 className="border-b pb-2 text-lg font-semibold text-gray-700">
          Building Details
        </h3>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Building Type
            </label>

            <input
              type="text"
              placeholder="e.g. Factory, Office"
              {...register("building_type")}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Category
            </label>

            <select
              {...register("category_id", { valueAsNumber: true })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            >
              <option value="">No category</option>
              {categories.map((c) => (
                <option key={c.id} value={c.id}>
                  {c.name}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Total Floor Area (sq.m)
            </label>

            <input
              type="number"
              step="any"
              {...register("total_floor_area", { valueAsNumber: true })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Number of Floors
            </label>

            <input
              type="number"
              {...register("number_of_floors", { valueAsNumber: true })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Year Constructed
            </label>

            <input
              type="number"
              {...register("year_constructed", { valueAsNumber: true })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
          </div>
        </div>
      </section>

      {/* Address Information */}
      <section className="space-y-4">
        <h3 className="border-b pb-2 text-lg font-semibold text-gray-700">
          Address Information
        </h3>

        <div className="grid grid-cols-1 gap-4">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Address Line 1
            </label>

            <input
              type="text"
              {...register("address_line_1")}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Address Line 2
            </label>

            <input
              type="text"
              {...register("address_line_2")}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                City
              </label>

              <input
                type="text"
                {...register("city")}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                State
              </label>

              <input
                type="text"
                {...register("state")}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Country
              </label>

              <input
                type="text"
                {...register("country")}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                PIN Code
              </label>

              <input
                type="text"
                {...register("pincode")}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
              />
            </div>
          </div>
        </div>
      </section>

      {/* Status */}
      <section className="space-y-4">
        <h3 className="border-b pb-2 text-lg font-semibold text-gray-700">
          Status
        </h3>

        <label className="inline-flex items-center gap-3">
          <input
            type="checkbox"
            {...register("is_active")}
            className="h-4 w-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500"
          />

          <span className="text-sm font-medium text-gray-700">
            Active Building
          </span>
        </label>
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
              ? "Update Building"
              : "Create Building"}
        </button>
      </div>
    </form>
  );
}

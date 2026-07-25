import { useEffect } from "react";
import { useForm } from "react-hook-form";

import CountrySelector from "../../countries/components/CountrySelector";
import { useCountries } from "../../countries/hooks/useCountries";

import type {
  ManufacturingUnit,
  ManufacturingUnitCreate,
  PatSector,
} from "../api/manufacturingUnitApi";

interface ManufacturingUnitFormProps {
  buildings: { id: number; building_name: string }[];
  initialData?: ManufacturingUnit;
  defaultSector?: PatSector;
  onSubmit: (data: ManufacturingUnitCreate) => void;
  onCancel?: () => void;
  loading?: boolean;
}

const SECTORS: { value: PatSector; label: string }[] = [
  { value: "aluminium", label: "Aluminium" },
  { value: "cement", label: "Cement" },
  { value: "chlor_alkali", label: "Chlor-Alkali" },
  { value: "fertilizer", label: "Fertilizer" },
  { value: "iron_steel", label: "Iron & Steel" },
  { value: "pulp_paper", label: "Pulp & Paper" },
  { value: "textile", label: "Textile" },
  { value: "thermal_power", label: "Thermal Power" },
  { value: "refineries", label: "Refineries" },
  { value: "railways", label: "Railways" },
  { value: "discoms", label: "DISCOMs" },
  { value: "petrochemicals", label: "Petrochemicals" },
  { value: "other", label: "Other" },
];

export default function ManufacturingUnitForm({
  buildings,
  initialData,
  defaultSector,
  onSubmit,
  onCancel,
  loading = false,
}: ManufacturingUnitFormProps) {
  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm<ManufacturingUnitCreate>();

  const { data: countries } = useCountries();
  const selectedCountry = watch("country_code") ?? "IN";
  const countryInfo = countries?.find((c) => c.code === selectedCountry);

  useEffect(() => {
    if (initialData) {
      reset({
        building_id: initialData.building_id,
        unit_code: initialData.unit_code,
        unit_name: initialData.unit_name,
        sector: initialData.sector,
        baseline_year: initialData.baseline_year,
        standards_applicable: initialData.standards_applicable ?? "",
        country_code: initialData.country_code ?? "IN",
        remarks: initialData.remarks ?? "",
      });
    } else {
      reset({
        building_id: undefined,
        unit_code: "",
        unit_name: "",
        sector: defaultSector,
        baseline_year: new Date().getFullYear(),
        standards_applicable: "BEE PAT + ISO 50001",
        country_code: "IN",
        remarks: "",
      });
    }
  }, [initialData, defaultSector, reset]);

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="space-y-8 rounded-xl border border-gray-200 bg-white p-6 shadow-sm"
    >
      <div>
        <h2 className="text-xl font-semibold text-gray-800">
          {initialData ? "Edit Manufacturing Unit" : "Add Manufacturing Unit"}
        </h2>

        <p className="mt-1 text-sm text-gray-500">
          Tracked per BEE PAT Scheme / ISO 50001 -- sector and baseline year
          for SEC/EnPI benchmarking.
        </p>
      </div>

      <section className="space-y-4">
        <h3 className="border-b pb-2 text-lg font-semibold text-gray-700">
          Identity
        </h3>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Unit Code *
            </label>

            <input
              type="text"
              {...register("unit_code", { required: "Unit code is required" })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />

            {errors.unit_code && (
              <p className="mt-1 text-sm text-red-600">
                {errors.unit_code.message}
              </p>
            )}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Unit Name *
            </label>

            <input
              type="text"
              {...register("unit_name", { required: "Unit name is required" })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />

            {errors.unit_name && (
              <p className="mt-1 text-sm text-red-600">
                {errors.unit_name.message}
              </p>
            )}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Sector *
            </label>

            <select
              {...register("sector", { required: "Sector is required" })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            >
              <option value="">Select sector...</option>
              {SECTORS.map((s) => (
                <option key={s.value} value={s.value}>
                  {s.label}
                </option>
              ))}
            </select>

            {errors.sector && (
              <p className="mt-1 text-sm text-red-600">{errors.sector.message}</p>
            )}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Plant / Building
            </label>

            <select
              {...register("building_id", { valueAsNumber: true })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            >
              <option value="">None</option>
              {buildings.map((b) => (
                <option key={b.id} value={b.id}>
                  {b.building_name}
                </option>
              ))}
            </select>
          </div>
        </div>
      </section>

      <section className="space-y-4">
        <h3 className="border-b pb-2 text-lg font-semibold text-gray-700">
          PAT / Compliance
        </h3>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Baseline Year *
            </label>

            <input
              type="number"
              {...register("baseline_year", {
                required: "Baseline year is required",
                valueAsNumber: true,
              })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />

            {errors.baseline_year && (
              <p className="mt-1 text-sm text-red-600">
                {errors.baseline_year.message}
              </p>
            )}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Standards Applicable
            </label>

            <input
              type="text"
              {...register("standards_applicable")}
              placeholder="BEE PAT + ISO 50001"
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Country *
            </label>

            <CountrySelector
              value={selectedCountry}
              onChange={(code) => setValue("country_code", code)}
            />

            {countryInfo && (
              <p className="mt-1 text-xs text-gray-500">
                Grid factor:{" "}
                {countryInfo.grid_factor_kgco2e_per_kwh !== null
                  ? countryInfo.grid_factor_kgco2e_per_kwh + " kgCO2e/kWh"
                  : "pending verification"}
                {" \u00b7 "}
                {countryInfo.applicable_standards}
              </p>
            )}
          </div>
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Remarks
          </label>

          <textarea
            {...register("remarks")}
            rows={2}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />
        </div>
      </section>

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
          {loading ? "Saving..." : initialData ? "Update Unit" : "Add Unit"}
        </button>
      </div>
    </form>
  );
}

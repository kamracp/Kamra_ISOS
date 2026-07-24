import { useForm } from "react-hook-form";
import type { DecarbonizationProjectCreate, ProjectCategory } from "../api/netZeroApi";

interface DecarbonizationProjectFormProps {
  onSubmit: (data: DecarbonizationProjectCreate) => void;
  onCancel?: () => void;
  loading?: boolean;
}

const CATEGORIES: { value: ProjectCategory; label: string }[] = [
  { value: "energy_efficiency", label: "Energy Efficiency" },
  { value: "renewable_generation", label: "Renewable Generation (Solar/Wind)" },
  { value: "fuel_switching", label: "Fuel Switching" },
  { value: "waste_heat_recovery", label: "Waste Heat Recovery" },
  { value: "electrification", label: "Electrification" },
  { value: "ccus", label: "CCUS" },
  { value: "other", label: "Other" },
];

export default function DecarbonizationProjectForm({
  onSubmit,
  onCancel,
  loading = false,
}: DecarbonizationProjectFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<DecarbonizationProjectCreate>({
    defaultValues: { status: "proposed", annual_opex_delta: 0 },
  });

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="space-y-6 rounded-xl border border-gray-200 bg-white p-6 shadow-sm"
    >
      <div>
        <h2 className="text-xl font-semibold text-gray-800">Add Decarbonization Project</h2>
        <p className="mt-1 text-sm text-gray-500">
          Feeds the MACC engine: cost per tonne of CO2e abated, cheapest first.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Project Name *</label>
          <input
            type="text"
            {...register("project_name", { required: "Required" })}
            placeholder="e.g. Rooftop Solar 500kW"
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />
          {errors.project_name && (
            <p className="mt-1 text-sm text-red-600">{errors.project_name.message}</p>
          )}
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Category *</label>
          <select
            {...register("category", { required: "Required" })}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          >
            <option value="">Select...</option>
            {CATEGORIES.map((c) => (
              <option key={c.value} value={c.value}>
                {c.label}
              </option>
            ))}
          </select>
          {errors.category && (
            <p className="mt-1 text-sm text-red-600">{errors.category.message}</p>
          )}
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">CAPEX (₹) *</label>
          <input
            type="number"
            step="any"
            {...register("capex", { required: "Required", valueAsNumber: true, min: 0 })}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />
          {errors.capex && <p className="mt-1 text-sm text-red-600">{errors.capex.message}</p>}
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Annual OPEX Delta (₹)
          </label>
          <input
            type="number"
            step="any"
            {...register("annual_opex_delta", { valueAsNumber: true })}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />
          <p className="mt-1 text-xs text-gray-400">Negative = saves running cost annually</p>
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">Lifespan (Years) *</label>
          <input
            type="number"
            {...register("lifespan_years", { required: "Required", valueAsNumber: true, min: 1 })}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />
          {errors.lifespan_years && (
            <p className="mt-1 text-sm text-red-600">{errors.lifespan_years.message}</p>
          )}
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Annual CO2e Abated (tonnes) *
          </label>
          <input
            type="number"
            step="any"
            {...register("annual_co2e_abated_tonnes", {
              required: "Required",
              valueAsNumber: true,
              min: 0,
            })}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />
          {errors.annual_co2e_abated_tonnes && (
            <p className="mt-1 text-sm text-red-600">
              {errors.annual_co2e_abated_tonnes.message}
            </p>
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
          {loading ? "Saving..." : "Add Project"}
        </button>
      </div>
    </form>
  );
}

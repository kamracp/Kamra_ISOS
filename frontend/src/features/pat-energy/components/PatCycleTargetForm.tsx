import { useEffect } from "react";
import { useForm } from "react-hook-form";

import type { PatCycleTarget, PatCycleTargetCreate } from "../api/patEnergyApi";

interface PatCycleTargetFormProps {
  initialData?: PatCycleTarget;
  onSubmit: (data: PatCycleTargetCreate) => void;
  onCancel?: () => void;
  loading?: boolean;
}

export default function PatCycleTargetForm({
  initialData,
  onSubmit,
  onCancel,
  loading = false,
}: PatCycleTargetFormProps) {
  const {
    register,
    handleSubmit,
    reset,
    watch,
    formState: { errors },
  } = useForm<PatCycleTargetCreate>();

  const baselineProd = watch("baseline_production_qty");
  const baselineEnergy = watch("baseline_energy_gj");
  const reductionPct = watch("mandated_reduction_percent");

  const baselineSec =
    baselineProd && baselineEnergy
      ? Number(baselineEnergy) / Number(baselineProd)
      : null;
  const targetSec =
    baselineSec !== null && reductionPct !== undefined
      ? baselineSec * (1 - Number(reductionPct) / 100)
      : null;

  useEffect(() => {
    if (initialData) {
      reset({
        cycle_number: initialData.cycle_number,
        cycle_start_year: initialData.cycle_start_year,
        cycle_end_year: initialData.cycle_end_year,
        baseline_production_qty: initialData.baseline_production_qty,
        production_unit: initialData.production_unit,
        baseline_energy_gj: initialData.baseline_energy_gj,
        mandated_reduction_percent: initialData.mandated_reduction_percent,
      });
    } else {
      reset({
        cycle_number: undefined,
        cycle_start_year: undefined,
        cycle_end_year: undefined,
        baseline_production_qty: undefined,
        production_unit: "",
        baseline_energy_gj: undefined,
        mandated_reduction_percent: undefined,
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
          {initialData ? "Edit PAT Cycle Target" : "Add PAT Cycle Target"}
        </h2>
        <p className="mt-1 text-sm text-gray-500">
          BEE PAT-notified baseline and mandated reduction for this cycle. Target
          SEC is calculated automatically, never entered directly.
        </p>
      </div>

      <section className="space-y-4">
        <h3 className="border-b pb-2 text-lg font-semibold text-gray-700">
          Cycle
        </h3>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Cycle Number *
            </label>
            <input
              type="number"
              {...register("cycle_number", {
                required: "Cycle number is required",
                valueAsNumber: true,
                min: { value: 1, message: "Must be at least 1" },
              })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
            {errors.cycle_number && (
              <p className="mt-1 text-sm text-red-600">{errors.cycle_number.message}</p>
            )}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Cycle Start Year *
            </label>
            <input
              type="number"
              {...register("cycle_start_year", {
                required: "Start year is required",
                valueAsNumber: true,
              })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
            {errors.cycle_start_year && (
              <p className="mt-1 text-sm text-red-600">{errors.cycle_start_year.message}</p>
            )}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Cycle End Year *
            </label>
            <input
              type="number"
              {...register("cycle_end_year", {
                required: "End year is required",
                valueAsNumber: true,
              })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
            {errors.cycle_end_year && (
              <p className="mt-1 text-sm text-red-600">{errors.cycle_end_year.message}</p>
            )}
          </div>
        </div>
      </section>

      <section className="space-y-4">
        <h3 className="border-b pb-2 text-lg font-semibold text-gray-700">
          Baseline (Measured)
        </h3>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Baseline Production Qty *
            </label>
            <input
              type="number"
              step="any"
              {...register("baseline_production_qty", {
                required: "Baseline production is required",
                valueAsNumber: true,
                min: { value: 0.0001, message: "Must be greater than 0" },
              })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
            {errors.baseline_production_qty && (
              <p className="mt-1 text-sm text-red-600">
                {errors.baseline_production_qty.message}
              </p>
            )}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Production Unit *
            </label>
            <input
              type="text"
              placeholder="e.g. tonnes clinker"
              {...register("production_unit", {
                required: "Production unit is required",
              })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
            {errors.production_unit && (
              <p className="mt-1 text-sm text-red-600">{errors.production_unit.message}</p>
            )}
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Baseline Energy (GJ) *
            </label>
            <input
              type="number"
              step="any"
              {...register("baseline_energy_gj", {
                required: "Baseline energy is required",
                valueAsNumber: true,
                min: { value: 0.0001, message: "Must be greater than 0" },
              })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
            {errors.baseline_energy_gj && (
              <p className="mt-1 text-sm text-red-600">{errors.baseline_energy_gj.message}</p>
            )}
          </div>
        </div>
      </section>

      <section className="space-y-4">
        <h3 className="border-b pb-2 text-lg font-semibold text-gray-700">
          BEE Mandated Target
        </h3>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div>
            <label className="mb-1 block text-sm font-medium text-gray-700">
              Mandated Reduction (%) *
            </label>
            <input
              type="number"
              step="any"
              {...register("mandated_reduction_percent", {
                required: "Mandated reduction is required",
                valueAsNumber: true,
                min: { value: 0, message: "Cannot be negative" },
                max: { value: 100, message: "Cannot exceed 100" },
              })}
              className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
            />
            {errors.mandated_reduction_percent && (
              <p className="mt-1 text-sm text-red-600">
                {errors.mandated_reduction_percent.message}
              </p>
            )}
          </div>
        </div>

        {baselineSec !== null && targetSec !== null && (
          <div className="rounded-lg bg-blue-50 px-4 py-3 text-sm text-blue-800">
            Baseline SEC:{" "}
            <span className="font-semibold">{baselineSec.toFixed(4)} GJ/unit</span>
            {" · "}
            Target SEC:{" "}
            <span className="font-semibold">{targetSec.toFixed(4)} GJ/unit</span>
          </div>
        )}
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
          {loading ? "Saving..." : initialData ? "Update Target" : "Add Target"}
        </button>
      </div>
    </form>
  );
}

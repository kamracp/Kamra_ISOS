import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import toast from "react-hot-toast";

import { useManufacturingUnits } from "../../manufacturing-units/hooks/useManufacturingUnits";
import {
  usePatCycleTargets,
  useCreatePatCycleTarget,
  useUpdatePatCycleTarget,
  useDeletePatCycleTarget,
  usePatSummary,
} from "../hooks/usePatEnergy";
import PatCycleTargetForm from "../components/PatCycleTargetForm";
import type { PatCycleTarget, PatCycleTargetCreate } from "../api/patEnergyApi";
import ConfirmDialog from "../../../components/ui/ConfirmDialog";

export default function PatEnergyPage() {
  const { data: units = [] } = useManufacturingUnits();
  const [selectedUnitId, setSelectedUnitId] = useState<number | "">("");
  const [year, setYear] = useState<number>(new Date().getFullYear());

  const { data: targets = [], isLoading: targetsLoading } = usePatCycleTargets(
    selectedUnitId ? Number(selectedUnitId) : undefined
  );
  const { data: summary, isLoading: summaryLoading } = usePatSummary(
    selectedUnitId ? Number(selectedUnitId) : undefined,
    year
  );

  const createMutation = useCreatePatCycleTarget();
  const updateMutation = useUpdatePatCycleTarget();
  const deleteMutation = useDeletePatCycleTarget();

  const [showForm, setShowForm] = useState(false);
  const [selectedTarget, setSelectedTarget] = useState<PatCycleTarget | null>(null);
  const [deleteId, setDeleteId] = useState<number | null>(null);

  const selectedUnit = useMemo(
    () => units.find((u) => u.id === Number(selectedUnitId)),
    [units, selectedUnitId]
  );

  async function saveTarget(formData: PatCycleTargetCreate) {
    if (!selectedUnitId) return;
    try {
      if (selectedTarget) {
        await updateMutation.mutateAsync({ targetId: selectedTarget.id, data: formData });
      } else {
        await createMutation.mutateAsync({ unitId: Number(selectedUnitId), data: formData });
      }
      setShowForm(false);
      setSelectedTarget(null);
    } catch (error) {
      console.error(error);
      toast.error("Unable to save PAT cycle target.");
    }
  }

  async function deleteTarget() {
    if (deleteId === null) return;
    try {
      await deleteMutation.mutateAsync(deleteId);
      setDeleteId(null);
    } catch (error) {
      console.error(error);
      toast.error("Unable to delete PAT cycle target.");
    }
  }

  return (
    <div className="space-y-6 p-8">
      <div>
        <h1 className="text-3xl font-bold">PAT Energy (SEC Tracking)</h1>
        <p className="text-gray-500">
          BEE PAT-notified baseline &amp; mandated reduction targets, compared
          against actual SEC derived automatically from production records and
          utility bills.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 rounded-xl border bg-white p-5 shadow-sm md:grid-cols-2">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Manufacturing Unit
          </label>
          <select
            value={selectedUnitId}
            onChange={(e) =>
              setSelectedUnitId(e.target.value ? Number(e.target.value) : "")
            }
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          >
            <option value="">Select unit...</option>
            {units.map((u) => (
              <option key={u.id} value={u.id}>
                {u.unit_name} ({u.unit_code})
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Year
          </label>
          <input
            type="number"
            value={year}
            onChange={(e) => setYear(Number(e.target.value))}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          />
        </div>
      </div>

      {!selectedUnitId && (
        <div className="rounded-lg border border-gray-200 bg-gray-50 p-6 text-center text-gray-500">
          Select a manufacturing unit to view PAT targets and SEC status.
        </div>
      )}

      {selectedUnitId && (
        <>
          <div className="rounded-xl border bg-white p-5 shadow-sm">
            <div className="flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-800">
                {year} SEC Status
              </h2>
              <Link
                to="/production-records"
                className="text-sm font-medium text-blue-600 hover:underline"
              >
                Manage production records →
              </Link>
            </div>

            {summaryLoading ? (
              <p className="mt-3 text-gray-500">Loading...</p>
            ) : !summary || summary.actual_sec_gj_per_unit === null ? (
              <p className="mt-3 text-gray-500">
                {summary?.message ?? "No data available for this year."}
              </p>
            ) : (
              <div className="mt-3 grid grid-cols-1 gap-4 md:grid-cols-4">
                <div>
                  <p className="text-sm text-gray-500">Actual Energy</p>
                  <p className="text-xl font-bold text-gray-800">
                    {summary.actual_energy_gj?.toFixed(2)} GJ
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Actual Production</p>
                  <p className="text-xl font-bold text-gray-800">
                    {summary.actual_production_qty?.toFixed(2)}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Actual SEC</p>
                  <p className="text-xl font-bold text-blue-700">
                    {summary.actual_sec_gj_per_unit?.toFixed(4)} GJ/unit
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-500">Status</p>
                  {summary.on_track === null ? (
                    <p className="text-xl font-bold text-gray-400">No target</p>
                  ) : summary.on_track ? (
                    <p className="text-xl font-bold text-green-700">On Track</p>
                  ) : (
                    <p className="text-xl font-bold text-red-700">Behind Target</p>
                  )}
                </div>
              </div>
            )}
          </div>

          <div className="flex items-center justify-between">
            <h2 className="text-xl font-bold text-gray-800">
              PAT Cycle Targets — {selectedUnit?.unit_name}
            </h2>
            <button
              onClick={() => {
                setSelectedTarget(null);
                setShowForm(true);
              }}
              className="rounded-lg bg-blue-600 px-5 py-2 font-medium text-white transition hover:bg-blue-700"
            >
              + Add Target
            </button>
          </div>

          <div className="overflow-hidden rounded-xl border bg-white shadow">
            <table className="min-w-full">
              <thead className="bg-gray-100">
                <tr>
                  <th className="border-b px-4 py-3 text-left">Cycle</th>
                  <th className="border-b px-4 py-3 text-left">Years</th>
                  <th className="border-b px-4 py-3 text-left">Baseline SEC</th>
                  <th className="border-b px-4 py-3 text-left">Reduction %</th>
                  <th className="border-b px-4 py-3 text-left">Target SEC</th>
                  <th className="border-b px-4 py-3 text-center">Actions</th>
                </tr>
              </thead>
              <tbody>
                {targetsLoading ? (
                  <tr>
                    <td colSpan={6} className="py-10 text-center text-gray-500">
                      Loading...
                    </td>
                  </tr>
                ) : targets.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-10 text-center text-gray-500">
                      No PAT cycle targets for this unit.
                    </td>
                  </tr>
                ) : (
                  targets.map((t) => (
                    <tr key={t.id} className="hover:bg-gray-50">
                      <td className="border-b px-4 py-3">Cycle {t.cycle_number}</td>
                      <td className="border-b px-4 py-3">
                        {t.cycle_start_year}–{t.cycle_end_year}
                      </td>
                      <td className="border-b px-4 py-3">
                        {t.baseline_sec_gj_per_unit.toFixed(4)} GJ/{t.production_unit}
                      </td>
                      <td className="border-b px-4 py-3">{t.mandated_reduction_percent}%</td>
                      <td className="border-b px-4 py-3 font-semibold">
                        {t.target_sec_gj_per_unit.toFixed(4)} GJ/{t.production_unit}
                      </td>
                      <td className="border-b px-4 py-3 text-center">
                        <button
                          onClick={() => {
                            setSelectedTarget(t);
                            setShowForm(true);
                          }}
                          className="mr-2 rounded bg-amber-500 px-3 py-1 text-white hover:bg-amber-600"
                        >
                          Edit
                        </button>
                        <button
                          onClick={() => setDeleteId(t.id)}
                          className="rounded bg-red-600 px-3 py-1 text-white hover:bg-red-700"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </>
      )}

      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-6">
          <div className="max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-xl bg-white shadow-2xl">
            <div className="flex items-center justify-between border-b px-6 py-4">
              <h2 className="text-2xl font-bold">
                {selectedTarget ? "Edit PAT Cycle Target" : "Add PAT Cycle Target"}
              </h2>
              <button
                onClick={() => {
                  setShowForm(false);
                  setSelectedTarget(null);
                }}
                className="text-3xl leading-none text-gray-500 hover:text-black"
              >
                ×
              </button>
            </div>
            <div className="p-6">
              <PatCycleTargetForm
                initialData={selectedTarget ?? undefined}
                onSubmit={saveTarget}
                loading={createMutation.isPending || updateMutation.isPending}
                onCancel={() => {
                  setShowForm(false);
                  setSelectedTarget(null);
                }}
              />
            </div>
          </div>
        </div>
      )}

      <ConfirmDialog
        open={deleteId !== null}
        title="Delete PAT Cycle Target"
        message="Are you sure you want to delete this target? This action cannot be undone."
        loading={deleteMutation.isPending}
        onCancel={() => setDeleteId(null)}
        onConfirm={deleteTarget}
      />
    </div>
  );
}

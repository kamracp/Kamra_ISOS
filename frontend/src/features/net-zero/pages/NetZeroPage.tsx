import { useState } from "react";
import toast from "react-hot-toast";

import {
  useNetZeroTargets,
  useCreateNetZeroTarget,
  useDeleteNetZeroTarget,
  useNetZeroSummary,
  useDecarbonizationProjects,
  useCreateDecarbonizationProject,
  useDeleteDecarbonizationProject,
} from "../hooks/useNetZero";

import NetZeroTargetForm from "../components/NetZeroTargetForm";
import DecarbonizationProjectForm from "../components/DecarbonizationProjectForm";
import { useManufacturingUnits } from "../../manufacturing-units/hooks/useManufacturingUnits";

import type {
  NetZeroTarget,
  NetZeroTargetCreate,
  DecarbonizationProjectCreate,
} from "../api/netZeroApi";

export default function NetZeroPage() {
  const { data: units = [] } = useManufacturingUnits();
  const unitNameById = new Map(units.map((u) => [u.id, `${u.unit_name} (${u.unit_code})`]));

  const { data: targets = [] } = useNetZeroTargets();
  const createTarget = useCreateNetZeroTarget();
  const deleteTarget = useDeleteNetZeroTarget();

  const { data: projects = [] } = useDecarbonizationProjects();
  const createProject = useCreateDecarbonizationProject();
  const deleteProject = useDeleteDecarbonizationProject();

  const [selectedTargetId, setSelectedTargetId] = useState<number | null>(null);
  const { data: summary } = useNetZeroSummary(selectedTargetId ?? undefined);

  const [showTargetForm, setShowTargetForm] = useState(false);
  const [showProjectForm, setShowProjectForm] = useState(false);

  async function saveTarget(data: NetZeroTargetCreate) {
    try {
      const created = await createTarget.mutateAsync(data);
      setShowTargetForm(false);
      setSelectedTargetId(created.id);
    } catch (error) {
      console.error(error);
    }
  }

  async function saveProject(data: DecarbonizationProjectCreate) {
    try {
      await createProject.mutateAsync(data);
      setShowProjectForm(false);
    } catch (error) {
      console.error(error);
    }
  }

  return (
    <div className="space-y-6 p-8">
      <div>
        <h1 className="text-3xl font-bold">Net Zero Action Plan</h1>
        <p className="text-gray-500">
          Targets, decarbonization projects, and the cheapest path to get there (MACC)
        </p>
      </div>

      {/* Targets */}
      <div className="rounded-xl border bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">Net Zero Targets</h2>
          <button
            onClick={() => setShowTargetForm(true)}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            + Add Target
          </button>
        </div>

        {targets.length === 0 ? (
          <p className="mt-4 text-sm text-gray-400">No targets set yet.</p>
        ) : (
          <div className="mt-4 flex flex-wrap gap-3">
            {targets.map((t: NetZeroTarget) => (
              <button
                key={t.id}
                onClick={() => setSelectedTargetId(t.id)}
                className={`rounded-lg border px-4 py-2 text-sm ${
                  selectedTargetId === t.id
                    ? "border-blue-600 bg-blue-50 font-semibold text-blue-700"
                    : "border-gray-300 text-gray-700 hover:bg-gray-50"
                }`}
              >
                {t.target_name} ({t.baseline_year}→{t.target_year}, -{t.reduction_percentage}%)
                {t.manufacturing_unit_id && (
                  <span className="ml-2 rounded bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800">
                    {unitNameById.get(t.manufacturing_unit_id) ?? "Unit-scoped"}
                  </span>
                )}
                <span
                  onClick={(e) => {
                    e.stopPropagation();
                    deleteTarget.mutate(t.id);
                    if (selectedTargetId === t.id) setSelectedTargetId(null);
                  }}
                  className="ml-3 text-red-500 hover:underline"
                >
                  ×
                </span>
              </button>
            ))}
          </div>
        )}

        {showTargetForm && (
          <div className="mt-4">
            <NetZeroTargetForm
              onSubmit={saveTarget}
              onCancel={() => setShowTargetForm(false)}
              loading={createTarget.isPending}
            />
          </div>
        )}
      </div>

      {/* Summary / trajectory */}
      {summary && summary.status === "ok" && (
        <div className="rounded-xl border bg-white p-6 shadow-sm">
          <h2 className="text-xl font-semibold">
            {summary.target_name} — BAU vs Target
          </h2>

          <div className="mt-4 grid grid-cols-2 gap-4 md:grid-cols-4">
            <div className="rounded-lg bg-gray-50 p-4">
              <p className="text-xs text-gray-500">Baseline ({summary.baseline_year})</p>
              <p className="text-2xl font-bold">{summary.baseline_co2e_tonnes} t</p>
            </div>
            <div className="rounded-lg bg-gray-50 p-4">
              <p className="text-xs text-gray-500">Target ({summary.target_year})</p>
              <p className="text-2xl font-bold">{summary.target_co2e_tonnes} t</p>
            </div>
            <div className="rounded-lg bg-gray-50 p-4">
              <p className="text-xs text-gray-500">Expected Today ({summary.current_year})</p>
              <p className="text-2xl font-bold">{summary.expected_co2e_tonnes_on_trajectory} t</p>
            </div>
            <div
              className={`rounded-lg p-4 ${
                summary.on_track ? "bg-green-50" : "bg-red-50"
              }`}
            >
              <p className="text-xs text-gray-500">Actual Today</p>
              <p className="text-2xl font-bold">{summary.current_actual_co2e_tonnes} t</p>
              <p
                className={`text-sm font-medium ${
                  summary.on_track ? "text-green-700" : "text-red-700"
                }`}
              >
                {summary.on_track ? "On track" : `${summary.gap_tonnes} t over trajectory`}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Projects + MACC */}
      <div className="rounded-xl border bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-semibold">
            Decarbonization Projects (MACC — cheapest first)
          </h2>
          <button
            onClick={() => setShowProjectForm(true)}
            className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
          >
            + Add Project
          </button>
        </div>

        {showProjectForm && (
          <div className="mt-4">
            <DecarbonizationProjectForm
              onSubmit={saveProject}
              onCancel={() => setShowProjectForm(false)}
              loading={createProject.isPending}
            />
          </div>
        )}

        {(summary?.macc && summary.macc.length > 0) || projects.length > 0 ? (
          <table className="mt-4 w-full text-sm">
            <thead>
              <tr className="border-b text-left text-gray-500">
                <th className="py-2">Project</th>
                <th className="py-2">Category</th>
                <th className="py-2">CAPEX</th>
                <th className="py-2">tCO2e/yr Abated</th>
                <th className="py-2">MAC (₹/tCO2e)</th>
                <th className="py-2 text-center">Actions</th>
              </tr>
            </thead>
            <tbody>
              {(summary?.macc ?? projects.map((p) => ({ ...p, marginal_abatement_cost: null }))).map(
                (p: any) => (
                  <tr key={p.id} className="border-b">
                    <td className="py-2 font-medium">{p.project_name}</td>
                    <td className="py-2 capitalize">{p.category.replace(/_/g, " ")}</td>
                    <td className="py-2">₹{p.capex.toLocaleString("en-IN")}</td>
                    <td className="py-2">{p.annual_co2e_abated_tonnes}</td>
                    <td className="py-2 font-semibold">
                      {p.marginal_abatement_cost != null
                        ? `₹${p.marginal_abatement_cost.toLocaleString("en-IN")}`
                        : "-"}
                    </td>
                    <td className="py-2 text-center">
                      <button
                        onClick={() => deleteProject.mutate(p.id)}
                        className="text-sm text-red-600 hover:underline"
                      >
                        Remove
                      </button>
                    </td>
                  </tr>
                )
              )}
            </tbody>
          </table>
        ) : (
          <p className="mt-4 text-sm text-gray-400">No projects added yet.</p>
        )}
      </div>
    </div>
  );
}

import { useState } from "react";
import toast from "react-hot-toast";

import {
  useClimateRisks,
  useClimateRiskSummary,
  useCreateClimateRisk,
  useDeleteClimateRisk,
} from "../hooks/useClimateRisk";
import {
  CATEGORY_LABELS,
  type RiskCategory,
  type RiskTimeHorizon,
  type RiskLikelihood,
  type ClimateRiskCreate,
} from "../api/climateRiskApi";

const CATEGORY_OPTIONS: RiskCategory[] = [
  "physical_acute",
  "physical_chronic",
  "transition_policy_legal",
  "transition_technology",
  "transition_market",
  "transition_reputation",
];

const TIME_HORIZON_OPTIONS: { value: RiskTimeHorizon; label: string }[] = [
  { value: "short_term", label: "Short-term (0-3 yrs)" },
  { value: "medium_term", label: "Medium-term (3-10 yrs)" },
  { value: "long_term", label: "Long-term (10+ yrs)" },
];

const LIKELIHOOD_OPTIONS: RiskLikelihood[] = [
  "unlikely",
  "possible",
  "likely",
  "almost_certain",
];

function formatInr(value: number): string {
  return `Rs ${value.toLocaleString("en-IN", { maximumFractionDigits: 0 })}`;
}

const emptyForm: ClimateRiskCreate = {
  risk_name: "",
  category: "physical_acute",
  time_horizon: "medium_term",
  likelihood: "possible",
  estimated_financial_impact_inr: 0,
  mitigation_cost_inr: 0,
  mitigation_benefit_inr: 0,
  description: "",
  mitigation_action: "",
};

export default function ClimateRiskPage() {
  const { data: risks, isLoading } = useClimateRisks();
  const { data: summary } = useClimateRiskSummary();
  const createMutation = useCreateClimateRisk();
  const deleteMutation = useDeleteClimateRisk();

  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState<ClimateRiskCreate>(emptyForm);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!form.risk_name.trim()) {
      toast.error("Risk name is required.");
      return;
    }
    createMutation.mutate(form, {
      onSuccess: () => {
        setForm(emptyForm);
        setShowForm(false);
      },
    });
  };

  const handleDelete = (id: number, name: string) => {
    if (window.confirm(`Delete climate risk "${name}"?`)) {
      deleteMutation.mutate(id);
    }
  };

  return (
    <div className="mx-auto max-w-6xl space-y-6 p-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-800">
          Climate Risk (TCFD)
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          Physical and transition climate risks with financial
          quantification, aligned to the TCFD (Task Force on
          Climate-related Financial Disclosures) recommendations.
        </p>
      </div>

      {summary && (
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
            <div className="text-xs text-gray-500">Total Risks Tracked</div>
            <div className="mt-1 text-xl font-bold text-gray-800">
              {summary.total_risks}
            </div>
          </div>
          <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
            <div className="text-xs text-gray-500">Total Financial Impact</div>
            <div className="mt-1 text-xl font-bold text-red-600">
              {formatInr(summary.total_estimated_financial_impact_inr)}
            </div>
          </div>
          <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
            <div className="text-xs text-gray-500">Mitigation Benefit</div>
            <div className="mt-1 text-xl font-bold text-green-600">
              {formatInr(summary.total_mitigation_benefit_inr)}
            </div>
          </div>
          <div className="rounded-xl border border-blue-200 bg-blue-50 p-4 shadow-sm">
            <div className="text-xs text-blue-700">Net Risk Exposure</div>
            <div className="mt-1 text-xl font-bold text-blue-800">
              {formatInr(summary.total_net_risk_exposure_inr)}
            </div>
          </div>
        </div>
      )}

      <div className="flex justify-end">
        <button
          onClick={() => setShowForm((s) => !s)}
          className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700"
        >
          {showForm ? "Cancel" : "+ Add Climate Risk"}
        </button>
      </div>

      {showForm && (
        <form
          onSubmit={handleSubmit}
          className="space-y-4 rounded-xl border border-gray-200 bg-white p-5 shadow-sm"
        >
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Risk Name *
              </label>
              <input
                type="text"
                value={form.risk_name}
                onChange={(e) => setForm({ ...form, risk_name: e.target.value })}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Category
              </label>
              <select
                value={form.category}
                onChange={(e) =>
                  setForm({ ...form, category: e.target.value as RiskCategory })
                }
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
              >
                {CATEGORY_OPTIONS.map((c) => (
                  <option key={c} value={c}>
                    {CATEGORY_LABELS[c]}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Time Horizon
              </label>
              <select
                value={form.time_horizon}
                onChange={(e) =>
                  setForm({
                    ...form,
                    time_horizon: e.target.value as RiskTimeHorizon,
                  })
                }
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
              >
                {TIME_HORIZON_OPTIONS.map((t) => (
                  <option key={t.value} value={t.value}>
                    {t.label}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Likelihood
              </label>
              <select
                value={form.likelihood}
                onChange={(e) =>
                  setForm({
                    ...form,
                    likelihood: e.target.value as RiskLikelihood,
                  })
                }
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
              >
                {LIKELIHOOD_OPTIONS.map((l) => (
                  <option key={l} value={l}>
                    {l.replace("_", " ")}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Estimated Financial Impact (Rs) *
              </label>
              <input
                type="number"
                min="0"
                value={form.estimated_financial_impact_inr}
                onChange={(e) =>
                  setForm({
                    ...form,
                    estimated_financial_impact_inr: Number(e.target.value),
                  })
                }
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Mitigation Cost (Rs)
              </label>
              <input
                type="number"
                min="0"
                value={form.mitigation_cost_inr}
                onChange={(e) =>
                  setForm({
                    ...form,
                    mitigation_cost_inr: Number(e.target.value),
                  })
                }
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Mitigation Benefit (Rs)
              </label>
              <input
                type="number"
                min="0"
                value={form.mitigation_benefit_inr}
                onChange={(e) =>
                  setForm({
                    ...form,
                    mitigation_benefit_inr: Number(e.target.value),
                  })
                }
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
              />
            </div>

            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Description
              </label>
              <textarea
                value={form.description}
                onChange={(e) => setForm({ ...form, description: e.target.value })}
                rows={2}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
              />
            </div>

            <div className="sm:col-span-2">
              <label className="mb-1 block text-sm font-medium text-gray-700">
                Mitigation Action
              </label>
              <textarea
                value={form.mitigation_action}
                onChange={(e) =>
                  setForm({ ...form, mitigation_action: e.target.value })
                }
                rows={2}
                className="w-full rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
              />
            </div>
          </div>

          <button
            type="submit"
            disabled={createMutation.isPending}
            className="rounded-lg bg-blue-600 px-5 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
          >
            {createMutation.isPending ? "Saving..." : "Save Risk"}
          </button>
        </form>
      )}

      {isLoading && <p className="text-gray-500">Loading climate risks...</p>}

      {risks && risks.length > 0 && (
        <div className="overflow-x-auto rounded-xl border border-gray-200 bg-white shadow-sm">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-gray-50 text-left text-xs uppercase text-gray-500">
                <th className="px-4 py-3">Risk</th>
                <th className="px-4 py-3">Category</th>
                <th className="px-4 py-3">Horizon</th>
                <th className="px-4 py-3">Likelihood</th>
                <th className="px-4 py-3">Financial Impact</th>
                <th className="px-4 py-3">Mitigation Benefit</th>
                <th className="px-4 py-3">Net Exposure</th>
                <th className="px-4 py-3"></th>
              </tr>
            </thead>
            <tbody>
              {risks.map((r) => (
                <tr key={r.id} className="border-b last:border-0">
                  <td className="px-4 py-3">
                    <div className="font-medium text-gray-800">{r.risk_name}</div>
                    {r.description && (
                      <div className="mt-0.5 text-xs text-gray-400">
                        {r.description}
                      </div>
                    )}
                  </td>
                  <td className="px-4 py-3 text-xs text-gray-600">
                    {CATEGORY_LABELS[r.category]}
                  </td>
                  <td className="px-4 py-3 text-xs text-gray-600">
                    {r.time_horizon.replace("_", " ")}
                  </td>
                  <td className="px-4 py-3 text-xs text-gray-600">
                    {r.likelihood.replace("_", " ")}
                  </td>
                  <td className="px-4 py-3 font-medium text-red-600">
                    {formatInr(r.estimated_financial_impact_inr)}
                  </td>
                  <td className="px-4 py-3 font-medium text-green-600">
                    {formatInr(r.mitigation_benefit_inr)}
                  </td>
                  <td className="px-4 py-3 font-semibold text-blue-700">
                    {formatInr(r.net_risk_exposure_inr)}
                  </td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => handleDelete(r.id, r.risk_name)}
                      className="text-xs text-red-500 hover:underline"
                    >
                      Delete
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {risks && risks.length === 0 && !isLoading && (
        <p className="text-sm text-gray-500">
          No climate risks recorded yet. Add one to begin TCFD-style risk
          tracking.
        </p>
      )}
    </div>
  );
}

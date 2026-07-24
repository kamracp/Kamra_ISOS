import { useState } from "react";
import { useCarbonSummary } from "../features/carbon/hooks/useCarbonSummary";
import { useSegment } from "../context/SegmentContext";
import {
  useFacilityCategories,
  useCreateFacilityCategory,
  useDeleteFacilityCategory,
} from "../features/facility-categories/hooks/useFacilityCategories";

export default function Dashboard() {
  const { data: carbon } = useCarbonSummary();
  const { segment } = useSegment();

  const { data: categories = [] } = useFacilityCategories(segment);
  const createCategory = useCreateFacilityCategory(segment);
  const deleteCategory = useDeleteFacilityCategory(segment);

  const [newCategoryName, setNewCategoryName] = useState("");

  const totalTonnes = carbon?.total_co2e_tonnes ?? 0;
  const electricityKwh = (carbon?.line_items ?? [])
    .filter((item) => item.meter_type === "electricity")
    .reduce((sum, item) => sum + item.consumption, 0);

  const portfolioTitle =
    segment === "manufacturing" ? "Facility Portfolio" : "Building Portfolio";

  async function handleAddCategory() {
    const name = newCategoryName.trim();
    if (!name) return;

    try {
      await createCategory.mutateAsync({
        segment,
        name,
        display_order: categories.length,
      });
      setNewCategoryName("");
    } catch (error) {
      console.error(error);
    }
  }

  const kpis = [
    {
      title: "Organizations",
      value: "0",
      color: "bg-blue-50 border-blue-200",
    },
    {
      title: segment === "manufacturing" ? "Facilities" : "Buildings",
      value: "0",
      color: "bg-green-50 border-green-200",
    },
    {
      title: "Electricity",
      value: `${electricityKwh.toLocaleString("en-IN")} kWh`,
      color: "bg-yellow-50 border-yellow-200",
    },
    {
      title: "Carbon",
      value: `${totalTonnes} tCO₂e`,
      color: "bg-red-50 border-red-200",
    },
  ];

  return (
    <div className="space-y-6">

      <div>
        <h1 className="text-3xl font-bold text-slate-800">
          Enterprise Energy Dashboard
        </h1>

        <p className="text-slate-500">
          {segment === "manufacturing"
            ? "Operational overview of your facility portfolio"
            : "Operational overview of your building portfolio"}
        </p>
      </div>

      {/* KPI */}

      <div className="grid gap-6 lg:grid-cols-4">

        {kpis.map((item) => (
          <div
            key={item.title}
            className={`rounded-xl border p-6 shadow-sm ${item.color}`}
          >
            <p className="text-sm text-slate-500">
              {item.title}
            </p>

            <h2 className="mt-3 text-4xl font-bold">
              {item.value}
            </h2>
          </div>
        ))}

      </div>

      {/* Second Row */}

      <div className="grid gap-6 xl:grid-cols-2">

        <div className="rounded-xl border bg-white p-6 shadow-sm">

          <h2 className="text-xl font-semibold">
            {portfolioTitle}
          </h2>

          <div className="mt-4 flex gap-2">
            <input
              value={newCategoryName}
              onChange={(e) => setNewCategoryName(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleAddCategory()}
              placeholder="e.g. Engineering Wing, Workshop, Utility..."
              className="flex-1 rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
            />

            <button
              onClick={handleAddCategory}
              disabled={createCategory.isPending || !newCategoryName.trim()}
              className="rounded-lg bg-blue-600 px-4 py-2 text-sm font-medium text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >
              + Add
            </button>
          </div>

          <table className="mt-4 w-full">

            <tbody>

              {categories.length === 0 ? (
                <tr>
                  <td colSpan={2} className="py-6 text-center text-sm text-gray-400">
                    No categories added yet.
                  </td>
                </tr>
              ) : (
                categories.map((category, idx) => (
                  <tr
                    key={category.id}
                    className={idx < categories.length - 1 ? "border-b" : ""}
                  >
                    <td className="py-3">{category.name}</td>
                    <td className="py-3 text-right">
                      <span className="mr-4 font-semibold">0</span>
                      <button
                        onClick={() => deleteCategory.mutate(category.id)}
                        className="text-sm text-red-600 hover:underline"
                      >
                        Remove
                      </button>
                    </td>
                  </tr>
                ))
              )}

            </tbody>

          </table>

        </div>

        <div className="rounded-xl border bg-white p-6 shadow-sm">

          <h2 className="text-xl font-semibold">
            Utility Summary
          </h2>

          <table className="mt-5 w-full">

            <tbody>

              <tr className="border-b">
                <td className="py-3">Electricity</td>
                <td className="text-right">0 kWh</td>
              </tr>

              <tr className="border-b">
                <td className="py-3">Water</td>
                <td className="text-right">0 m³</td>
              </tr>

              <tr className="border-b">
                <td className="py-3">Natural Gas</td>
                <td className="text-right">0 Nm³</td>
              </tr>

              <tr className="border-b">
                <td className="py-3">Diesel</td>
                <td className="text-right">0 Litres</td>
              </tr>

              <tr>
                <td className="py-3">Steam</td>
                <td className="text-right">0 Tonnes</td>
              </tr>

            </tbody>

          </table>

        </div>

      </div>

      {/* Third Row */}

      <div className="grid gap-6 xl:grid-cols-3">

        <div className="rounded-xl border bg-white p-6 shadow-sm">

          <h2 className="text-xl font-semibold">
            Carbon Status
          </h2>

          <div className="mt-5 space-y-4">

            <div>
              Scope 1 : {((carbon?.by_scope_kg.scope_1 ?? 0) / 1000).toFixed(3)} tCO₂e
            </div>

            <div>
              Scope 2 : {((carbon?.by_scope_kg.scope_2 ?? 0) / 1000).toFixed(3)} tCO₂e
            </div>

            <div>
              Scope 3 : {((carbon?.by_scope_kg.scope_3 ?? 0) / 1000).toFixed(3)} tCO₂e
            </div>

          </div>

        </div>

        <div className="rounded-xl border bg-white p-6 shadow-sm">

          <h2 className="text-xl font-semibold">
            Active Alerts
          </h2>

          <p className="mt-5 text-green-600">
            No active alerts
          </p>

        </div>

        <div className="rounded-xl border bg-white p-6 shadow-sm">

          <h2 className="text-xl font-semibold">
            AI Recommendations
          </h2>

          <p className="mt-5 text-slate-500">
            AI insights will appear after energy data is available.
          </p>

        </div>

      </div>

    </div>
  );
}

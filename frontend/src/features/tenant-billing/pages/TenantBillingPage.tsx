import { useState } from "react";

import { useBuildings } from "../../buildings/hooks/useBuildings";
import { useFloors } from "../../floors/hooks/useFloors";
import { useTenantBilling } from "../hooks/useTenantBilling";

export default function TenantBillingPage() {
  const { data: buildings = [] } = useBuildings();
  const [selectedBuildingId, setSelectedBuildingId] = useState<number | "">("");
  const [selectedFloorId, setSelectedFloorId] = useState<number | "">("");

  const { data: floors = [] } = useFloors(
    selectedBuildingId ? Number(selectedBuildingId) : undefined
  );

  const {
    data: billingResults = [],
    isLoading,
    isError,
  } = useTenantBilling(
    selectedFloorId ? Number(selectedFloorId) : undefined
  );

  const totalComponentA = billingResults.reduce(
    (sum, r) => sum + r.component_a_kwh,
    0
  );
  const totalComponentB = billingResults.reduce(
    (sum, r) => sum + r.component_b_kwh,
    0
  );
  const totalKwh = billingResults.reduce((sum, r) => sum + r.total_kwh, 0);

  return (
    <div className="space-y-6 p-8">
      <div>
        <h1 className="text-3xl font-bold">Tenant Billing Allocation</h1>
        <p className="text-gray-500">
          Engineering-based per-occupant energy allocation — dedicated area +
          common area share
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 rounded-xl border bg-white p-5 shadow-sm md:grid-cols-2">
        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Building
          </label>
          <select
            value={selectedBuildingId}
            onChange={(e) => {
              setSelectedBuildingId(e.target.value ? Number(e.target.value) : "");
              setSelectedFloorId("");
            }}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none"
          >
            <option value="">Select building...</option>
            {buildings.map((b) => (
              <option key={b.id} value={b.id}>
                {b.building_name}
              </option>
            ))}
          </select>
        </div>

        <div>
          <label className="mb-1 block text-sm font-medium text-gray-700">
            Floor
          </label>
          <select
            value={selectedFloorId}
            onChange={(e) =>
              setSelectedFloorId(e.target.value ? Number(e.target.value) : "")
            }
            disabled={!selectedBuildingId}
            className="w-full rounded-lg border border-gray-300 px-3 py-2 focus:border-blue-500 focus:outline-none disabled:bg-gray-100"
          >
            <option value="">Select floor...</option>
            {floors.map((f) => (
              <option key={f.id} value={f.id}>
                {f.floor_name}
              </option>
            ))}
          </select>
        </div>
      </div>

      {!selectedFloorId && (
        <div className="rounded-lg border border-gray-200 bg-gray-50 p-6 text-center text-gray-500">
          Select a building and floor to view tenant billing allocation.
        </div>
      )}

      {selectedFloorId && isLoading && (
        <div className="p-6 text-center text-gray-500">
          Calculating allocation...
        </div>
      )}

      {selectedFloorId && isError && (
        <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-red-600">
          Unable to load tenant billing data.
        </div>
      )}

      {selectedFloorId && !isLoading && !isError && (
        <>
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            <div className="rounded-xl border bg-white p-5 shadow-sm">
              <p className="text-sm text-gray-500">
                Total Component A (Dedicated)
              </p>
              <p className="mt-1 text-2xl font-bold text-blue-700">
                {totalComponentA.toFixed(2)} kWh
              </p>
            </div>
            <div className="rounded-xl border bg-white p-5 shadow-sm">
              <p className="text-sm text-gray-500">
                Total Component B (Common Area)
              </p>
              <p className="mt-1 text-2xl font-bold text-purple-700">
                {totalComponentB.toFixed(2)} kWh
              </p>
            </div>
            <div className="rounded-xl border bg-white p-5 shadow-sm">
              <p className="text-sm text-gray-500">Total Floor Consumption</p>
              <p className="mt-1 text-2xl font-bold text-green-700">
                {totalKwh.toFixed(2)} kWh
              </p>
            </div>
          </div>

          <div className="overflow-hidden rounded-xl border bg-white shadow">
            <table className="min-w-full">
              <thead className="bg-gray-100">
                <tr>
                  <th className="border-b px-4 py-3 text-left">Occupant</th>
                  <th className="border-b px-4 py-3 text-left">Area (sq ft)</th>
                  <th className="border-b px-4 py-3 text-left">
                    Component A (kWh)
                  </th>
                  <th className="border-b px-4 py-3 text-left">
                    Component B (kWh)
                  </th>
                  <th className="border-b px-4 py-3 text-left">Total (kWh)</th>
                  <th className="border-b px-4 py-3 text-left">
                    Billing Month
                  </th>
                </tr>
              </thead>
              <tbody>
                {billingResults.length === 0 ? (
                  <tr>
                    <td colSpan={6} className="py-10 text-center text-gray-500">
                      <p className="font-medium">No billable occupants found for this floor.</p>
                      <p className="mt-2 text-sm">
                        Tenant Billing splits a floor's total energy consumption between its
                        Occupants, in proportion to each occupant's office area. This floor
                        has no Occupants set up yet — Occupant management isn't available in
                        the product yet, so this page will stay empty until that's built.
                      </p>
                    </td>
                  </tr>
                ) : (
                  billingResults.map((r) => (
                    <tr key={r.occupant_id} className="hover:bg-gray-50">
                      <td className="border-b px-4 py-3 font-medium">
                        {r.occupant_name}
                      </td>
                      <td className="border-b px-4 py-3">
                        {r.office_area_sqft.toLocaleString()}
                      </td>
                      <td className="border-b px-4 py-3">
                        {r.component_a_kwh.toFixed(2)}
                      </td>
                      <td className="border-b px-4 py-3">
                        {r.component_b_kwh.toFixed(2)}
                      </td>
                      <td className="border-b px-4 py-3 font-semibold">
                        {r.total_kwh.toFixed(2)}
                      </td>
                      <td className="border-b px-4 py-3">
                        {r.billing_month}
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </>
      )}
    </div>
  );
}
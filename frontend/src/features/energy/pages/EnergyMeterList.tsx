import { useState } from "react";
import { Plus, Zap } from "lucide-react";
import EnergyMeterForm from "../components/EnergyMeterForm";
import {
  useEnergyMeters,
  useCreateEnergyMeter,
  useUpdateEnergyMeter,
  useDeleteEnergyMeter,
} from "../hooks/useEnergyMeters";
import { useQuery } from "@tanstack/react-query";
import client from "../../../services/api/client";

// ── Building fetch (for the form dropdown) ────────────────────────────────────

function useBuildings() {
  return useQuery({
    queryKey: ["buildings"],
    queryFn: async () => {
      const { data } = await client.get("/buildings/");
      return data;
    },
  });
}

// ── Scope badge ───────────────────────────────────────────────────────────────

function ScopeBadge({ scope }: { scope: string }) {
  const styles: Record<string, string> = {
    scope_1: "bg-orange-100 text-orange-700",
    scope_2: "bg-blue-100 text-blue-700",
    renewable: "bg-green-100 text-green-700",
    other: "bg-gray-100 text-gray-600",
  };
  const labels: Record<string, string> = {
    scope_1: "Scope 1",
    scope_2: "Scope 2",
    renewable: "Renewable",
    other: "Other",
  };
  return (
    <span
      className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${
        styles[scope] ?? styles.other
      }`}
    >
      {labels[scope] ?? scope}
    </span>
  );
}

// ── Main Page ─────────────────────────────────────────────────────────────────

export default function EnergyMeterList() {
  const [showForm, setShowForm] = useState(false);
  const [editingMeter, setEditingMeter] = useState<any | null>(null);

  const { data: meters = [], isLoading, isError } = useEnergyMeters();
  const { data: buildings = [] } = useBuildings();
  const createMeter = useCreateEnergyMeter();
  const updateMeter = useUpdateEnergyMeter();
  const deleteMeter = useDeleteEnergyMeter();

  function closeForm() {
    setShowForm(false);
    setEditingMeter(null);
  }

  if (isLoading) {
    return (
      <div className="p-6">
        <h1 className="mb-4 text-2xl font-bold">Energy Meters</h1>
        <p>Loading meters...</p>
      </div>
    );
  }

  if (isError) {
    return (
      <div className="p-6">
        <h1 className="mb-4 text-2xl font-bold">Energy Meters</h1>
        <p className="text-red-600">Unable to load energy meters.</p>
      </div>
    );
  }

  return (
    <div className="space-y-6 p-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="flex items-center gap-2 text-3xl font-bold">
            <Zap size={28} className="text-yellow-500" />
            Energy Meters
          </h1>
          <p className="text-gray-500">
            Manage energy and utility meters across your buildings.
          </p>
        </div>
        <button
          onClick={() => setShowForm(true)}
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        >
          <Plus size={18} />
          Add Meter
        </button>
      </div>

      {/* Table */}
      <div className="overflow-hidden rounded-lg border bg-white shadow">
        <table className="min-w-full">
          <thead className="bg-slate-100">
            <tr>
              <th className="px-4 py-3 text-left text-sm font-semibold">Code</th>
              <th className="px-4 py-3 text-left text-sm font-semibold">Meter Name</th>
              <th className="px-4 py-3 text-left text-sm font-semibold">Type</th>
              <th className="px-4 py-3 text-left text-sm font-semibold">Unit</th>
              <th className="px-4 py-3 text-left text-sm font-semibold">GHG Scope</th>
              <th className="px-4 py-3 text-left text-sm font-semibold">Provider</th>
              <th className="px-4 py-3 text-left text-sm font-semibold">Status</th>
              <th className="px-4 py-3 text-left text-sm font-semibold">Actions</th>
            </tr>
          </thead>
          <tbody>
            {meters.length === 0 ? (
              <tr>
                <td
                  colSpan={8}
                  className="py-8 text-center text-gray-500"
                >
                  No meters found. Add your first meter.
                </td>
              </tr>
            ) : (
              meters.map((meter: any) => (
                <tr key={meter.id} className="border-t hover:bg-slate-50">
                  <td className="px-4 py-3 font-mono text-sm">
                    {meter.meter_code}
                  </td>
                  <td className="px-4 py-3 font-medium">{meter.meter_name}</td>
                  <td className="px-4 py-3 text-sm capitalize">
                    {meter.meter_type.replace("_", " ")}
                  </td>
                  <td className="px-4 py-3 text-sm">{meter.unit}</td>
                  <td className="px-4 py-3">
                    <ScopeBadge scope={meter.scope} />
                  </td>
                  <td className="px-4 py-3 text-sm">
                    {meter.utility_provider ?? "—"}
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                        meter.is_active
                          ? "bg-green-100 text-green-700"
                          : "bg-gray-100 text-gray-500"
                      }`}
                    >
                      {meter.is_active ? "Active" : "Inactive"}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <div className="flex gap-3">
                      <button
                        onClick={() => {
                          setEditingMeter(meter);
                          setShowForm(true);
                        }}
                        className="text-sm text-blue-600 hover:underline"
                      >
                        Edit
                      </button>
                      <button
                        onClick={() => {
                          if (
                            confirm(
                              `Delete meter "${meter.meter_name}"? This will also delete all its utility bills.`
                            )
                          ) {
                            deleteMeter.mutate(meter.id);
                          }
                        }}
                        className="text-sm text-red-600 hover:underline"
                      >
                        Delete
                      </button>
                    </div>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Add / Edit Meter Form Modal */}
      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4">
          <div className="w-full max-w-2xl max-h-[90vh] overflow-y-auto rounded-xl">
            <EnergyMeterForm
              buildings={buildings}
              initialData={editingMeter ?? undefined}
              onSubmit={(data) => {
                if (editingMeter) {
                  updateMeter.mutate(
                    { id: editingMeter.id, data },
                    { onSuccess: closeForm }
                  );
                } else {
                  createMeter.mutate(data, { onSuccess: closeForm });
                }
              }}
              onCancel={closeForm}
              loading={createMeter.isPending || updateMeter.isPending}
            />
          </div>
        </div>
      )}
    </div>
  );
}
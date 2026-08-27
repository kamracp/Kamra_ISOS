import { useState } from "react";
import toast from "react-hot-toast";

import {
  useManufacturingElectricityRecords,
  useCreateManufacturingElectricityRecord,
  useUpdateManufacturingElectricityRecord,
  useDeleteManufacturingElectricityRecord,
} from "../hooks/useManufacturingElectricity";
import { useManufacturingUnits } from "../../manufacturing-units/hooks/useManufacturingUnits";
import ManufacturingElectricityRecordForm from "../components/ManufacturingElectricityRecordForm";
import type {
  ManufacturingElectricityRecord,
  ManufacturingElectricityRecordCreate,
} from "../api/manufacturingElectricityApi";
import ConfirmDialog from "../../../components/ui/ConfirmDialog";

export default function ManufacturingElectricityPage() {
  const { data: records = [], isLoading, isError } = useManufacturingElectricityRecords();
  const { data: units = [] } = useManufacturingUnits();

  const createRecord = useCreateManufacturingElectricityRecord();
  const updateRecord = useUpdateManufacturingElectricityRecord();
  const deleteRecord = useDeleteManufacturingElectricityRecord();

  const [showForm, setShowForm] = useState(false);
  const [selectedRecord, setSelectedRecord] = useState<ManufacturingElectricityRecord | null>(null);
  const [deleteId, setDeleteId] = useState<number | null>(null);

  async function saveRecord(data: ManufacturingElectricityRecordCreate) {
    try {
      if (selectedRecord) {
        await updateRecord.mutateAsync({ id: selectedRecord.id, data });
      } else {
        await createRecord.mutateAsync(data);
      }
      setShowForm(false);
      setSelectedRecord(null);
    } catch (error) {
      console.error(error);
      toast.error("Unable to save electricity record.");
    }
  }

  function unitLabel(unitId: number) {
    const unit = units.find((u) => u.id === unitId);
    return unit ? `${unit.unit_code} -- ${unit.unit_name}` : `Unit #${unitId}`;
  }

  if (isLoading) {
    return <div className="p-10 text-center">Loading electricity records...</div>;
  }

  if (isError) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-red-600">
        Unable to load electricity records.
      </div>
    );
  }

  return (
    <div className="space-y-6 p-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Electricity (Scope 2)</h1>
          <p className="text-gray-500">
            Purchased grid electricity per manufacturing unit -- CO2e derived
            automatically using each unit's country grid factor.
          </p>
        </div>
        <button
          onClick={() => {
            setSelectedRecord(null);
            setShowForm(true);
          }}
          className="rounded-lg bg-blue-600 px-5 py-2 font-medium text-white transition hover:bg-blue-700"
        >
          + Add Record
        </button>
      </div>

      {records.length === 0 ? (
        <div className="rounded-lg border border-gray-200 bg-gray-50 p-6 text-center text-gray-500">
          No electricity records yet.
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border bg-white shadow-sm">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b bg-gray-50 text-left text-gray-500">
                <th className="px-4 py-3">Unit</th>
                <th className="px-4 py-3">Period</th>
                <th className="px-4 py-3">Consumed (kWh)</th>
                <th className="px-4 py-3">Renewable (kWh)</th>
                <th className="px-4 py-3">Grid Factor</th>
                <th className="px-4 py-3">Scope 2 CO2e</th>
                <th className="px-4 py-3 text-center">Actions</th>
              </tr>
            </thead>
            <tbody>
              {records.map((r) => (
                <tr key={r.id} className="border-b">
                  <td className="px-4 py-3 font-medium">{unitLabel(r.manufacturing_unit_id)}</td>
                  <td className="px-4 py-3">
                    {r.period_start} to {r.period_end}
                  </td>
                  <td className="px-4 py-3">{r.electricity_consumed_kwh.toLocaleString()}</td>
                  <td className="px-4 py-3">{r.renewable_kwh.toLocaleString()}</td>
                  <td className="px-4 py-3">
                    {r.grid_factor_kgco2e_per_kwh !== null && r.grid_factor_kgco2e_per_kwh !== undefined
                      ? `${r.grid_factor_kgco2e_per_kwh} kg/kWh`
                      : "Not tracked"}
                  </td>
                  <td className="px-4 py-3">
                    {r.scope2_co2e_kg !== null && r.scope2_co2e_kg !== undefined
                      ? `${r.scope2_co2e_kg.toLocaleString()} kg`
                      : (
                        <span className="text-amber-600" title="This unit's country has no verified grid factor yet">
                          Not tracked
                        </span>
                      )}
                  </td>
                  <td className="px-4 py-3 text-center">
                    <button
                      onClick={() => {
                        setSelectedRecord(r);
                        setShowForm(true);
                      }}
                      className="mr-2 text-amber-600 hover:underline"
                    >
                      Edit
                    </button>
                    <button
                      onClick={() => setDeleteId(r.id)}
                      className="text-red-600 hover:underline"
                    >
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-6">
          <div className="max-h-[90vh] w-full max-w-2xl overflow-y-auto rounded-xl bg-white shadow-2xl">
            <div className="p-6">
              <ManufacturingElectricityRecordForm
                units={units}
                initialData={selectedRecord ?? undefined}
                onSubmit={saveRecord}
                loading={createRecord.isPending || updateRecord.isPending}
                onCancel={() => {
                  setShowForm(false);
                  setSelectedRecord(null);
                }}
              />
            </div>
          </div>
        </div>
      )}

      <ConfirmDialog
        open={deleteId !== null}
        title="Delete Electricity Record"
        message="Are you sure you want to delete this record?"
        loading={deleteRecord.isPending}
        onCancel={() => setDeleteId(null)}
        onConfirm={async () => {
          if (deleteId === null) return;
          await deleteRecord.mutateAsync(deleteId);
          setDeleteId(null);
        }}
      />
    </div>
  );
}

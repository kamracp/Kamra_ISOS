import { useState } from "react";
import { useManufacturingFuelRecords, useCreateManufacturingFuelRecord, useUpdateManufacturingFuelRecord, useDeleteManufacturingFuelRecord, useFuelLibrary } from "../hooks/useManufacturingFuels";
import { useManufacturingUnits } from "../../manufacturing-units/hooks/useManufacturingUnits";
import ManufacturingFuelRecordForm from "../components/ManufacturingFuelRecordForm";
import { PURPOSE_LABELS, type ManufacturingFuelRecord, type ManufacturingFuelRecordCreate } from "../api/manufacturingFuelsApi";
import ConfirmDialog from "../../../components/ui/ConfirmDialog";

const n = (v: number | null | undefined, d = 0) => (v === null || v === undefined ? "--" : v.toLocaleString("en-IN", { maximumFractionDigits: d }));

export default function ManufacturingFuelsPage() {
  const [year, setYear] = useState<number | undefined>(undefined);
  const { data: records = [], isLoading, isError } = useManufacturingFuelRecords(year);
  const { data: units = [] } = useManufacturingUnits();
  const { data: library = [] } = useFuelLibrary();
  const createRecord = useCreateManufacturingFuelRecord();
  const updateRecord = useUpdateManufacturingFuelRecord();
  const deleteRecord = useDeleteManufacturingFuelRecord();

  const [showForm, setShowForm] = useState(false);
  const [selected, setSelected] = useState<ManufacturingFuelRecord | null>(null);
  const [deleteId, setDeleteId] = useState<number | null>(null);

  const unitName = (id: number) => units.find((u) => u.id === id)?.unit_name ?? `Unit ${id}`;
  const totals = records.reduce((a, r) => ({ gj: a.gj + (r.energy_gj ?? 0), toe: a.toe + (r.energy_toe ?? 0), co2e: a.co2e + (r.scope1_co2e_kg ?? 0), bio: a.bio + (r.biogenic_co2_kg ?? 0) }), { gj: 0, toe: 0, co2e: 0, bio: 0 });

  async function save(data: ManufacturingFuelRecordCreate) {
    try {
      if (selected) { const { manufacturing_unit_id: _u, ...rest } = data; await updateRecord.mutateAsync({ id: selected.id, data: rest }); }
      else await createRecord.mutateAsync(data);
      setShowForm(false); setSelected(null);
    } catch (e) { console.error(e); }
  }

  if (isLoading) return <div className="p-10 text-center">Loading fuel records...</div>;
  if (isError) return <div className="rounded-lg border border-red-200 bg-red-50 p-6 text-red-600">Unable to load fuel records.</div>;

  return (
    <div className="space-y-6 p-8">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Fuels & Combustion</h1>
          <p className="text-gray-500">Fuel burned per unit and period. One entry feeds PAT SEC (thermal), Scope 1 and BRSR P6 energy -- IPCC 2006 factors, AR5 GWP.</p>
        </div>
        <div className="flex items-center gap-3">
          <input type="number" placeholder="Year" className="w-28 rounded-lg border border-gray-300 px-3 py-2" value={year ?? ""} onChange={(e) => setYear(e.target.value ? Number(e.target.value) : undefined)} />
          <button onClick={() => { setSelected(null); setShowForm(true); }} className="rounded-lg bg-blue-600 px-5 py-2 font-medium text-white hover:bg-blue-700">+ Add Fuel Record</button>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4 md:grid-cols-4">
        {[["Energy", `${n(totals.gj)} GJ`], ["Energy (toe)", n(totals.toe, 1)], ["Scope 1 combustion", `${n(totals.co2e / 1000, 1)} tCO₂e`], ["Biogenic CO₂", `${n(totals.bio / 1000, 1)} t`]].map(([k, v]) => (
          <div key={k} className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm"><p className="text-xs uppercase tracking-wide text-gray-400">{k}</p><p className="mt-1 text-xl font-semibold text-gray-800">{v}</p></div>
        ))}
      </div>

      {records.length === 0 ? (
        <div className="rounded-lg border border-gray-200 bg-gray-50 p-6 text-center text-gray-500">No fuel records yet.</div>
      ) : (
        <div className="overflow-x-auto rounded-xl border bg-white shadow-sm">
          <table className="w-full text-sm">
            <thead><tr className="border-b bg-gray-50 text-left text-gray-500">
              <th className="px-4 py-3">Unit</th><th className="px-4 py-3">Period</th><th className="px-4 py-3">Fuel</th><th className="px-4 py-3">Purpose</th>
              <th className="px-4 py-3 text-right">Tonnes</th><th className="px-4 py-3 text-right">Energy (GJ)</th><th className="px-4 py-3 text-right">toe</th>
              <th className="px-4 py-3 text-right">Scope 1 (tCO₂e)</th><th className="px-4 py-3 text-right">Biogenic CO₂ (t)</th><th className="px-4 py-3 text-center">Actions</th>
            </tr></thead>
            <tbody>
              {records.map((r) => (
                <tr key={r.id} className="border-b">
                  <td className="px-4 py-3 font-medium">{unitName(r.manufacturing_unit_id)}</td>
                  <td className="px-4 py-3">{r.period_start} → {r.period_end}</td>
                  <td className="px-4 py-3">{r.fuel_name ?? r.fuel_key}{r.is_biogenic && <span className="ml-1 rounded bg-green-100 px-1.5 py-0.5 text-xs text-green-700">biogenic</span>}</td>
                  <td className="px-4 py-3 text-gray-500">{PURPOSE_LABELS[r.purpose]}</td>
                  <td className="px-4 py-3 text-right">{n(r.quantity_tonnes, 3)}</td>
                  <td className="px-4 py-3 text-right">{n(r.energy_gj)}</td>
                  <td className="px-4 py-3 text-right">{n(r.energy_toe, 2)}</td>
                  <td className="px-4 py-3 text-right">{n((r.scope1_co2e_kg ?? 0) / 1000, 2)}</td>
                  <td className="px-4 py-3 text-right">{n((r.biogenic_co2_kg ?? 0) / 1000, 2)}</td>
                  <td className="px-4 py-3 text-center">
                    <button onClick={() => { setSelected(r); setShowForm(true); }} className="mr-2 text-amber-600 hover:underline">Edit</button>
                    <button onClick={() => setDeleteId(r.id)} className="text-red-600 hover:underline">Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showForm && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-6">
          <div className="max-h-[90vh] w-full max-w-3xl overflow-y-auto rounded-xl bg-white shadow-2xl"><div className="p-6">
            <ManufacturingFuelRecordForm units={units} library={library} initialData={selected ?? undefined} onSubmit={save}
              loading={createRecord.isPending || updateRecord.isPending} onCancel={() => { setShowForm(false); setSelected(null); }} />
          </div></div>
        </div>
      )}
      <ConfirmDialog open={deleteId !== null} title="Delete Fuel Record" message="Are you sure? PAT SEC and Scope 1 for this period will change."
        loading={deleteRecord.isPending} onCancel={() => setDeleteId(null)}
        onConfirm={async () => { if (deleteId === null) return; await deleteRecord.mutateAsync(deleteId); setDeleteId(null); }} />
    </div>
  );
}
